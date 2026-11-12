import asyncio
from app import rpc, parse, valid

def test_validation():
    assert valid("https://mp.weixin.qq.com/s/example")
    assert not valid("https://mp.weixin.qq.com.evil.test/s/example")
    assert not valid("http://mp.weixin.qq.com/s/example")
    assert not valid("https://mp.weixin.qq.com:444/s/example")

def test_rpc():
    async def run():
        a=await rpc({"jsonrpc":"2.0","id":1,"method":"initialize"})
        assert a["result"]["serverInfo"]["name"]=="wechat-article-reader"
        b=await rpc({"jsonrpc":"2.0","id":2,"method":"tools/list"})
        assert b["result"]["tools"][0]["name"]=="read_wechat_articles"
        c=await rpc({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"read_wechat_articles","arguments":{"urls":["https://evil.example/s/a"]}}})
        assert "INVALID_URL" in c["result"]["content"][0]["text"]
    asyncio.run(run())

def test_parse():
    html='<div id="activity-name">Sample</div><div id="js_name">Example</div><div id="js_content"><p>'+('Article content is verified and structured. '*4)+'</p></div>'
    result=parse(html,"https://mp.weixin.qq.com/s/test")
    assert result["status"]=="ok" and result["title"]=="Sample"
