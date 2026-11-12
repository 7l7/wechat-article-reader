import asyncio
import json
import re
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import logging
from article_extractor import extract as extract_wechat_html

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
TOOL = {"name":"read_wechat_articles","description":"Read up to five publicly accessible WeChat Official Account articles. Return verified title, account, Markdown, image URLs, and explicit errors if inaccessible.","inputSchema":{"type":"object","properties":{"urls":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":5}},"required":["urls"],"additionalProperties":False},"annotations":{"readOnlyHint":True,"openWorldHint":True,"destructiveHint":False}}


IMPORT_TOOL = {
 "name":"import_wechat_article",
 "description":"Convert article HTML or Markdown explicitly supplied by the user. Never use this tool to fetch blocked web pages.",
 "inputSchema":{"type":"object","properties":{"content":{"type":"string","minLength":1,"maxLength":150000},"format":{"type":"string","enum":["html","markdown"]},"source_url":{"type":"string"},"title":{"type":"string"}},"required":["content","format"],"additionalProperties":False},
 "annotations":{"readOnlyHint":True,"openWorldHint":False}
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
    if not isinstance(url, str) or len(url)>2048:
        return False
    try:
        p=urlsplit(url)
        return p.scheme=="https" and p.hostname=="mp.weixin.qq.com" and p.username is None and p.password is None and p.port in (None,443) and (p.path=="/s" or p.path.startswith("/s/"))
    except ValueError:
        return False

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
    if not valid(url):return {"status":"error","source_url":str(url)[:200],"error_code":"INVALID_URL","message":"Only https://mp.weixin.qq.com/s/... links are accepted"}
    try:
        async with httpx.AsyncClient(timeout=15,follow_redirects=False,headers={"User-Agent":"Mozilla/5.0 (compatible; WeChatArticleReader/1.0)","Accept":"text/html","Accept-Language":"zh-CN,zh;q=0.9"}) as client:
            r=await client.get(url)
        if r.status_code in (301,302,303,307,308,403,429):
            redirect=r.headers.get("location","") if r.status_code in (301,302,303,307,308) else ""
            path=urlsplit(redirect).path if redirect else ""
            host=urlsplit(redirect).hostname if redirect else ""
            logging.getLogger("uvicorn.error").warning("WECHAT_REDIRECT_DIAGNOSTIC http=%s host=%r path=%r",r.status_code,host,path[:100])
            return {"status":"error","source_url":url,"error_code":"ACCESS_RESTRICTED","message":"HTTP "+str(r.status_code),"redirect_path":path[:140]}
        if r.status_code!=200:
            return {"status":"error","source_url":url,"error_code":"HTTP_ERROR","message":"HTTP "+str(r.status_code)}
        if len(r.content)>3000000 or "text/html" not in r.headers.get("content-type",""):
            return {"status":"error","source_url":url,"error_code":"INVALID_RESPONSE","message":"Unexpected response"}
        if any(s in r.text for s in ("访问过于频繁","请输入验证码","环境异常","操作过于频繁")):
            return {"status":"error","source_url":url,"error_code":"ACCESS_RESTRICTED","message":"WeChat verification required"}
        return parse(r.text,url)
    except (httpx.RequestError,TimeoutError):
        return {"status":"error","source_url":url,"error_code":"NETWORK_ERROR","message":"Network request failed"}

async def rpc(payload):
    if not isinstance(payload,dict) or payload.get("jsonrpc")!="2.0":
        return {"jsonrpc":"2.0","id":None,"error":{"code":-32600,"message":"Invalid request"}}
    if "id" not in payload:return None
    rid=payload["id"]; method=payload.get("method")
    if method=="initialize":
        result={"protocolVersion":"2025-06-18","capabilities":{"tools":{"listChanged":False}},"serverInfo":{"name":"wechat-article-reader","version":"0.4.0"}}
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
async def health():return {"status":"ok","service":"wechat-article-reader","version":"0.4.0"}
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
    body=await request.body()
    if not 0<len(body)<=20000:return JSONResponse({"error":"Invalid request size"},status_code=413)
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
    assert discovery.json()["result"]["tools"][0]["name"]=="read_wechat_articles"
    assert "INVALID_URL" in call.json()["result"]["content"][0]["text"]
    assert parsed["status"]=="ok" and parsed["title"]=="Fixture title" and "Verified article body" in parsed["markdown"]
    logging.getLogger("uvicorn.error").info("RUNTIME_SELFTEST_PASS health=200 tool_discovery=ok tool_call=ok parser=ok origin=ok protocol_headers=ok")

# One-shot external smoke test on a separately published public sample article.
# Does not use authentication, a browser, proxies, cookies, or restricted tabs.
@app.on_event("startup")
async def smoke_public_sample():
    sample="https://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ"
    article=await read(sample)
    logger=logging.getLogger("uvicorn.error")
    if article.get("status")=="ok":
        logger.info("PUBLIC_ARTICLE_SMOKE_PASS title=%r body_length=%d account_present=%s",
                    article.get("title","")[:100],len(article.get("markdown","")),
                    bool(article.get("account")))
    else:
        logger.warning("PUBLIC_ARTICLE_SMOKE_FAIL code=%s message=%s",
                       article.get("error_code","unknown"),article.get("message","")[:120])
        logger.warning("PUBLIC_ARTICLE_REDIRECT_PATH path=%r",article.get("redirect_path",""))
