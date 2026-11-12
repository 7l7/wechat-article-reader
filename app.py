import asyncio
import json
import re
from urllib.parse import urlsplit, urljoin

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import logging
import time
from collections import defaultdict, deque
from article_extractor import extract as extract_wechat_html
from url_normalizer import normalize_article_url

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
# Single-instance ephemeral abuse guard. Multi-instance deployment requires shared limits.
_REQUESTS = defaultdict(deque)
RATE_WINDOW_SECONDS = 60
RATE_LIMIT = 20
MAX_REQUEST_BYTES = 200_000
MAX_HTML_BYTES = 8_000_000

class ResponseTooLarge(Exception):
    pass

async def get_bounded(client: httpx.AsyncClient, url: str) -> httpx.Response:
    async with client.stream("GET",url) as incoming:
        buf=bytearray()
        async for data in incoming.aiter_bytes():
            buf.extend(data)
            if len(buf)>MAX_HTML_BYTES:
                raise ResponseTooLarge("HTML response too large")
        # aiter_bytes() already decodes Content-Encoding; remove stale encoding
        # headers before constructing a new Response to avoid double-decompression.
        headers=dict(incoming.headers)
        headers.pop("content-encoding",None)
        headers.pop("content-length",None)
        return httpx.Response(incoming.status_code,headers=headers,
                              content=bytes(buf),request=incoming.request)

_FETCH_SEMAPHORE = asyncio.Semaphore(3)

def allow_request(client_ip: str) -> bool:
    now = time.monotonic()
    if len(_REQUESTS) > 10000:
        _REQUESTS.clear()
    queue = _REQUESTS[client_ip]
    while queue and queue[0] < now - RATE_WINDOW_SECONDS:
        queue.popleft()
    if len(queue) >= RATE_LIMIT:
        return False
    queue.append(now)
    return True

TOOL = {"name":"read_wechat_articles","description":"Read up to five publicly accessible WeChat Official Account articles. Return verified title, account, Markdown, image URLs, and explicit errors if inaccessible.","inputSchema":{"type":"object","properties":{"urls":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":5}},"required":["urls"],"additionalProperties":False},"annotations":{"readOnlyHint":True,"openWorldHint":True,"destructiveHint":False}}


IMPORT_TOOL = {
 "name":"import_wechat_article",
 "description":"Convert article HTML or Markdown explicitly supplied by the user. Never use this tool to fetch blocked web pages.",
 "inputSchema":{"type":"object","properties":{"content":{"type":"string","minLength":1,"maxLength":150000},"format":{"type":"string","enum":["html","markdown"]},"source_url":{"type":"string"},"title":{"type":"string"}},"required":["content","format"],"additionalProperties":False},
 "annotations":{"readOnlyHint":True,"openWorldHint":False,"destructiveHint":False}
}
def import_article(args):
    content=args.get("content","")
    kind=args.get("format")
    if not isinstance(content,str) or not 1<=len(content)<=150000 or kind not in ("html","markdown"):
        return {"status":"error","error_code":"INVALID_INPUT","message":"Expected user-supplied HTML or Markdown"}
    source=args.get("source_url","")
    if not isinstance(source,str):source=""
    if kind=="html":
        parsed=parse(content,source)
        if parsed["status"]=="ok":
            parsed["source_method"]="user_supplied_html"
            return parsed
        soup=BeautifulSoup(content,"html.parser")
        for tag in soup(["script","style","noscript","iframe","svg"]):tag.decompose()
        candidate=soup.select_one("article") or soup.select_one("main") or soup.body
        if not candidate or len(candidate.get_text(" ",strip=True))<40:
            return {"status":"error","error_code":"CONTENT_NOT_FOUND","message":"No substantial article in supplied HTML"}
        md=markdown(candidate)
        title=args.get("title","") or (soup.title.get_text(" ",strip=True) if soup.title else "")
    else:
        md=content
        title=args.get("title","")
    if len(md.strip())<40:
        return {"status":"error","error_code":"CONTENT_TOO_SHORT","message":"Supplied content too short"}
    return {"status":"ok","source_url":source,"title":title,"markdown":md[:75000],"truncated":len(md)>75000,"source_method":"user_supplied_"+kind}

def valid(url):
    return normalize_article_url(url) is not None

def markdown(root):
    parts=[]
    def walk(n):
        if isinstance(n,NavigableString):
            parts.append(str(n))
            return
        if not isinstance(n,Tag) or n.name in ("script","style","noscript","iframe","svg"):
            return
        if n.name=="img":
            src=n.get("data-src") or n.get("src") or ""
            if src.startswith(("https://","http://")):
                parts.append("\n![]("+src+")\n")
            return
        if n.name=="br": parts.append("\n"); return
        if n.name in ("h1","h2","h3","h4","h5","h6"):
            parts.append("\n"+"#"*int(n.name[1])+" "+n.get_text(" ",strip=True)+"\n")
            return
        if n.name=="li":parts.append("\n- ")
        if n.name in ("p","div","section","blockquote"):parts.append("\n")
        if n.name=="a":
            href=n.get("href","")
            if href.startswith(("https://","http://")):
                parts.append("["+n.get_text(" ",strip=True)+"]("+href+")")
                return
        for c in n.children:walk(c)
        if n.name in ("p","div","section","li","blockquote"):parts.append("\n")
    walk(root)
    return re.sub(r"\n{3,}","\n\n","".join(parts)).strip()

def parse(html,url):
    return extract_wechat_html(html,url)

async def read(url):
    canonical=normalize_article_url(url)
    if canonical is None:
        return {"status":"error","source_url":str(url)[:200],"error_code":"INVALID_URL","message":"Only public HTTPS mp.weixin.qq.com article links are accepted"}
    async with _FETCH_SEMAPHORE:
        return await _read_network(canonical)

async def _read_network(url):
    try:
        async with httpx.AsyncClient(timeout=15,follow_redirects=False,headers={"User-Agent":"Mozilla/5.0 (compatible; WeChatArticleReader/1.0)","Accept":"text/html","Accept-Language":"zh-CN,zh;q=0.9"}) as client:
            r=await get_bounded(client,url)
            if r.status_code in (301,302,303,307,308):
                location=r.headers.get("location","")
                next_url=urljoin(url,location) if location else ""
                old=urlsplit(url); target=urlsplit(next_url) if next_url else None
                safe=(target is not None and target.scheme=="https" and
                      target.hostname=="mp.weixin.qq.com" and target.port in (None,443)
                      and target.path==old.path and next_url!=url)
                if safe:
                    logging.getLogger("uvicorn.error").info("WECHAT_CANONICAL_REDIRECT follow_once=true")
                    r=await get_bounded(client,next_url)
        if r.status_code in (301,302,303,307,308,403,429):
            redirect=r.headers.get("location","") if r.status_code in (301,302,303,307,308) else ""
            path=urlsplit(redirect).path if redirect else ""
            host=urlsplit(redirect).hostname if redirect else ""
            logging.getLogger("uvicorn.error").warning("WECHAT_REDIRECT_DIAGNOSTIC http=%s host=%r path=%r",r.status_code,host,path[:100])
            return {"status":"error","source_url":url,"error_code":"ACCESS_RESTRICTED","message":"HTTP "+str(r.status_code),"redirect_path":path[:140]}
        if r.status_code!=200:
            return {"status":"error","source_url":url,"error_code":"HTTP_ERROR","message":"HTTP "+str(r.status_code)}
        if len(r.content)>8000000 or "text/html" not in r.headers.get("content-type",""):
            logging.getLogger("uvicorn.error").warning("WECHAT_RESPONSE_DIAGNOSTIC status=%s content_type=%r bytes=%d",r.status_code,r.headers.get("content-type","")[:100],len(r.content))
            return {"status":"error","source_url":url,"error_code":"INVALID_RESPONSE","message":"Unexpected response"}
        if any(s in r.text for s in ("访问过于频繁","请输入验证码","环境异常","操作过于频繁")):
            return {"status":"error","source_url":url,"error_code":"ACCESS_RESTRICTED","message":"WeChat verification required"}
        return parse(r.text,url)
    except ResponseTooLarge:
        return {"status":"error","source_url":url,"error_code":"RESPONSE_TOO_LARGE","message":"Article HTML exceeds the 8 MB limit"}
    except (httpx.RequestError,TimeoutError):
        return {"status":"error","source_url":url,"error_code":"NETWORK_ERROR","message":"Network request failed"}

async def rpc(payload):
    if not isinstance(payload,dict) or payload.get("jsonrpc")!="2.0":
        return {"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Invalid request"}}
    if "id" not in payload:return None
    rid=payload["id"]; method=payload.get("method")
    if method=="initialize":
        result={"protocolVersion":"2025-06-18","capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"wechat-article-reader","version":"0.5.0"}}
    elif method=="ping":result={}
    elif method=="tools/list":result={"tools":[TOOL,IMPORT_TOOL]}
    elif method=="tools/call":
        p=payload.get("params") or {}; a=p.get("arguments") or {}
        if p.get("name")==IMPORT_TOOL["name"]:
            item=import_article(a)
            result={"content":[{"type":"text","text":json.dumps(item,ensure_ascii=False)}],"isError":item["status"]!="ok"}
            return {"jsonrpc":"2.0","id":rid,"result":result}
        urls=a.get("urls")
        if p.get("name")!=TOOL["name"] or not isinstance(urls,list) or not 1<=len(urls)<=5 or not all(isinstance(u,str) for u in urls):
            return {"jsonrpc":"2.0","id":rid,"error":{"code":-32602,"message":"Invalid arguments"}}
        logging.getLogger("uvicorn.error").info("MCP_TOOL_CALL_START count=%d",len(urls))
        articles=await asyncio.gather(*(read(u) for u in urls))
        logging.getLogger("uvicorn.error").info("MCP_TOOL_CALL_END outcomes=%s",",".join(x.get("error_code","ok") for x in articles))
        result={"content":[{"type":"text","text":json.dumps({"articles":articles},ensure_ascii=False)}],"isError":all(a["status"]=="error" for a in articles)}
    else:return {"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":"Method not found"}}
    return {"jsonrpc":"2.0","id":rid,"result":result}

@app.get("/health")
async def health():return {"status":"ok","service":"wechat-article-reader","version":"0.5.0"}
@app.post("/mcp")
async def mcp(request:Request):
    # Public MCP endpoint: disallow cross-origin browser invocations from
    # arbitrary sites; server-to-server MCP calls normally omit Origin.
    origin=request.headers.get("origin")
    if origin and origin not in ("https://chatgpt.com","https://chat.openai.com"):
        return JSONResponse({"error":"Origin not allowed"},status_code=403)
    version=request.headers.get("mcp-protocol-version")
    if version and version not in ("2025-03-26","2025-06-18","2025-11-25"):
        return JSONResponse({"error":"Unsupported MCP protocol version"},status_code=400)
    if "application/json" not in request.headers.get("content-type",""):return JSONResponse({"error":"JSON required"},status_code=415)
    peer=request.client.host if request.client else "unknown"
    if not allow_request(peer):
        return JSONResponse({"error":"Rate limit exceeded"},status_code=429,headers={"Retry-After":"60"})
    length_header=request.headers.get("content-length")
    if length_header and length_header.isdigit() and int(length_header)>MAX_REQUEST_BYTES:
        return JSONResponse({"error":"Request too large"},status_code=413)
    chunks=[]; size=0
    async for chunk in request.stream():
        size+=len(chunk)
        if size>MAX_REQUEST_BYTES:
            return JSONResponse({"error":"Request too large"},status_code=413)
        chunks.append(chunk)
    body=b"".join(chunks)
    if not body:return JSONResponse({"error":"Empty request"},status_code=400)
    try:data=json.loads(body)
    except ValueError:return JSONResponse({"error":"Invalid JSON"},status_code=400)
    resp=await rpc(data)
    if resp is None:return Response(status_code=202)
    return JSONResponse(resp,headers={"Cache-Control":"no-store"})

# Runtime verification: exercises the deployed ASGI application, MCP discovery,
# error-path tool execution, and parser without requesting external articles.
@app.on_event("startup")
async def verify_runtime():
    import logging
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://internal") as client:
        health = await client.get("/health")
        discovery = await client.post("/mcp",json={"jsonrpc":"2.0","id":1,"method":"tools/list"})
        call = await client.post("/mcp",json={"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"read_wechat_articles","arguments":{"urls":["https://invalid.example/s/a"]}}})
    fixture = '<h1 id="activity-name">Fixture title</h1><span id="js_name">Fixture account</span><div id="js_content"><p>' + ('Verified article body for deterministic parsing. '*4) + '</p></div>'
    parsed = parse(fixture,"https://mp.weixin.qq.com/s/fixture")
    imported=await rpc({"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"import_wechat_article","arguments":{"format":"html","content":"<html><title>Example</title><body><article><p>"+("A genuine article supplied by its user. "*5)+"</p></article></body></html>"}}})
    assert "user_supplied_html" in imported["result"]["content"][0]["text"]
    assert health.status_code==200
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://internal") as client:
        bad_origin=await client.post("/mcp",headers={"Origin":"https://attacker.example"},json={"jsonrpc":"2.0","id":1,"method":"tools/list"})
        good_origin=await client.post("/mcp",headers={"Origin":"https://chatgpt.com","MCP-Protocol-Version":"2025-06-18","Accept":"application/json, text/event-stream"},json={"jsonrpc":"2.0","id":1,"method":"tools/list"})
        invalid_version=await client.post("/mcp",headers={"MCP-Protocol-Version":"invalid"},json={"jsonrpc":"2.0","id":1,"method":"ping"})
    assert bad_origin.status_code==403 and good_origin.status_code==200 and invalid_version.status_code==400
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://internal") as client:
        # Use a payload larger than the previous 20 KB cap, but not real user data.
        large_import=await client.post("/mcp",json={"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"import_wechat_article","arguments":{"format":"markdown","content":"A"*30000}}})
        oversized=await client.post("/mcp",data=b"x"*(MAX_REQUEST_BYTES+1),headers={"Content-Type":"application/json"})
    assert large_import.status_code==200 and "user_supplied_markdown" in large_import.text
    assert oversized.status_code==413
    assert normalize_article_url("这篇 https://mp.weixin.qq.com/s/j8q018Lck1TWHO3NxQDiJQ 讲了什么")=="https://mp.weixin.qq.com/s/j8q018Lck1TWHO3NxQDiJQ"
    assert normalize_article_url("https://mp.weixin.qq.com/s?__biz=abc&amp;mid=123&amp;idx=1&amp;sn=def")=="https://mp.weixin.qq.com/s?__biz=abc&mid=123&idx=1&sn=def"
    assert TOOL["annotations"]["destructiveHint"] is False
    assert IMPORT_TOOL["annotations"]["destructiveHint"] is False
    assert discovery.json()["result"]["tools"][0]["name"]=="read_wechat_articles"
    assert "INVALID_URL" in call.json()["result"]["content"][0]["text"]
    assert parsed["status"]=="ok" and parsed["title"]=="Fixture title" and "Verified article body" in parsed["markdown"]
    logging.getLogger("uvicorn.error").info("RUNTIME_SELFTEST_PASS health=200 tool_discovery=ok tool_call=ok parser=ok origin=ok protocol_headers=ok large_import=ok max_body=ok annotations=ok")






