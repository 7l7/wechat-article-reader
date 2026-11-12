"""Regression tests for bounded WeChat HTML streaming."""
import asyncio
import gzip
import httpx
import pytest
from app import get_bounded, ResponseTooLarge, MAX_HTML_BYTES

def test_compressed_html_works():
    html=("<html><body><h1>微信正文</h1>"+"一段文章内容。"*100+"</body></html>").encode()
    compressed=gzip.compress(html)
    def handler(req):
        return httpx.Response(200,headers={"content-encoding":"gzip","content-type":"text/html; charset=UTF-8","content-length":str(len(compressed))},content=compressed)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await get_bounded(client,"https://mp.weixin.qq.com/s/test")
    res=asyncio.run(run())
    assert res.status_code==200
    assert "微信正文" in res.text

def test_html_limit_applies_to_decompressed_size():
    html=b"A"*(MAX_HTML_BYTES+100)
    compressed=gzip.compress(html)
    def handler(req):
        return httpx.Response(200,headers={"content-encoding":"gzip","content-type":"text/html"},content=compressed)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await get_bounded(client,"https://mp.weixin.qq.com/s/test")
    with pytest.raises(ResponseTooLarge):
        asyncio.run(run())
