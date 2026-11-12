"""Submission hardening regression tests (no remote HTTP dependencies)."""
import asyncio
import json
import time
import httpx

from app import app, rpc, allow_request, _REQUESTS, MAX_REQUEST_BYTES

def run(coro):
    return asyncio.run(coro)

def test_tool_annotations_and_discovery():
    response=run(rpc({"jsonrpc":"2.0","id":1,"method":"tools/list"}))
    tools=response["result"]["tools"]
    assert {t["name"] for t in tools}=={"read_wechat_articles","import_wechat_article"}
    for tool in tools:
        annotations=tool["annotations"]
        assert annotations["readOnlyHint"] is True
        assert annotations["destructiveHint"] is False
        assert isinstance(annotations["openWorldHint"],bool)

def test_html_import_large_enough_to_exceed_old_limit():
    content="<article><p>"+("Responsible article summary. "*1200)+"</p></article>"
    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://unit") as client:
            response=await client.post("/mcp",json={"jsonrpc":"2.0","id":17,"method":"tools/call","params":{"name":"import_wechat_article","arguments":{"format":"html","content":content}}})
        return response
    _REQUESTS.clear()
    resp=run(scenario())
    assert resp.status_code==200
    body=json.loads(resp.json()["result"]["content"][0]["text"])
    assert body["status"]=="ok"
    assert body["source_method"]=="user_supplied_html"

def test_request_above_limit_rejected_without_consuming_full_body():
    _REQUESTS.clear()
    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://unit") as client:
            return await client.post("/mcp",content=b"x"*(MAX_REQUEST_BYTES+1),headers={"Content-Type":"application/json"})
    result=run(scenario())
    assert result.status_code==413

def test_rate_guard():
    _REQUESTS.clear()
    for i in range(20):
        assert allow_request("test-peer") is True
    assert allow_request("test-peer") is False
    assert allow_request("second-peer") is True

def test_public_sample_status_is_not_faked():
    result=run(rpc({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"read_wechat_articles","arguments":{"urls":["https://example.com/article"]}}}))
    assert "INVALID_URL" in result["result"]["content"][0]["text"]
    assert result["result"]["isError"] is True
