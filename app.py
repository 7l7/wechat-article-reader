import asyncio
import json
import re
from urllib.parse import urlsplit

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
TOOL = {"name":"read_wechat_articles","description":"Read up to five publicly accessible WeChat Official Account articles. Return verified title, account, Markdown, image URLs, and explicit errors if inaccessible.","inputSchema":{"type":"object","properties":{"urls":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":5}},"required":["urls"],"additionalProperties":False},"annotations":{"readOnlyHint":True,"openWorldHint":True,"destructiveHint":False}}

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
    soup=BeautifulSoup(html,"html.parser")
    content=soup.select_one("#js_content")
    if content is None or len(content.get_text(" ",strip=True))<60:
        return {"status":"error","source_url":url,"error_code":"CONTENT_NOT_FOUND","message":"No verified article body"}
    title=soup.select_one("#activity-name")
    meta=soup.select_one('meta[property="og:title"]')
    name=soup.select_one("#js_name")
    date=soup.select_one("#publish_time")
    md=markdown(content)
    imgs=list(dict.fromkeys((x.get("data-src") or x.get("src") or "") for x in content.select("img")))
    return {"status":"ok","source_url":url,"title":title.get_text(" ",strip=True) if title else (meta.get("content","") if meta else ""),"account":name.get_text(" ",strip=True) if name else "","published_at":date.get_text(" ",strip=True) if date else "","markdown":md[:75000],"images":[i for i in imgs if i.startswith(("https://","http://"))][:100],"truncated":len(md)>75000}

async def read(url):
    if not valid(url):return {"status":"error","source_url":str(url)[:200],"error_code":"INVALID_URL","message":"Only https://mp.weixin.qq.com/s/... links are accepted"}
    try:
        async with httpx.AsyncClient(timeout=15,follow_redirects=False,headers={"User-Agent":"Mozilla/5.0 (compatible; WeChatArticleReader/1.0)","Accept":"text/html","Accept-Language":"zh-CN,zh;q=0.9"}) as client:
            r=await client.get(url)
        if r.status_code in (301,302,303,307,308,403,429):
            return {"status":"error","source_url":url,"error_code":"ACCESS_RESTRICTED","message":"HTTP "+str(r.status_code)}
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
    elif method=="tools/list":result={"tools":[TOOL]}
    elif method=="tools/call":
        p=payload.get("params") or {}; a=p.get("arguments") or {}
        urls=a.get("urls")
        if p.get("name")!=TOOL["name"] or not isinstance(urls,list) or not 1<=len(urls)<=5 or not all(isinstance(u,str) for u in urls):
            return {"jsonrpc":"2.0","id":rid,"error":{"code":-32602,"message":"Invalid arguments"}}
        articles=await asyncio.gather(*(read(u) for u in urls))
        result={"content":[{"type":"text","text":json.dumps({"articles":articles},ensure_ascii=False)}],"isError":all(a["status"]=="error" for a in articles)}
    else:return {"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":"Method not found"}}
    return {"jsonrpc":"2.0","id":rid,"result":result}

@app.get("/health")
async def health():return {"status":"ok","service":"wechat-article-reader","version":"0.4.0"}
@app.post("/mcp")
async def mcp(request:Request):
    if "application/json" not in request.headers.get("content-type",""):return JSONResponse({"error":"JSON required"},status_code=415)
    body=await request.body()
    if not 0<len(body)<=20000:return JSONResponse({"error":"Invalid request size"},status_code=413)
    try:data=json.loads(body)
    except ValueError:return JSONResponse({"error":"Invalid JSON"},status_code=400)
    resp=await rpc(data)
    if resp is None:return Response(status_code=202)
    return JSONResponse(resp,headers={"Cache-Control":"no-store"})
