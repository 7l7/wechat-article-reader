"""Regression fixtures representing common public WeChat HTML templates.
These are synthetic fixtures, not proof of access to a live WeChat article.
"""
from article_extractor import extract

def test_public_rich_text():
    html = """
    <html><head><meta property="og:title" content="测试文章"/></head>
    <body><h1 id="activity-name">测试文章</h1><span id="js_name">测试公众号</span>
      <script>var ct = "1711111111"; var item_show_type = "0";</script>
      <div id="js_content"><p>这是一段内容丰富的微信公众号文章正文，需要足够长才能正常完成有效性验证。</p>
      <p>第二段提供新的信息，包含正文中的结构性数据和描述。</p>
      <img data-src="https://mmbiz.qpic.cn/test/abc" src="data:image/gif;base64,AAAA"></div>
    </body></html>"""
    result = extract(html,"https://mp.weixin.qq.com/s/example")
    assert result["status"]=="ok"
    assert result["title"]=="测试文章"
    assert result["account"]=="测试公众号"
    assert "第二段" in result["markdown"]
    assert "https://mmbiz.qpic.cn/test/abc" in result["markdown"]
    assert result["display_type"]=="article"

def test_image_gallery():
    html = """<script>var item_show_type = 8;</script><h1 id="activity-name">图片合集</h1>
    <div id="js_content"><img data-src="https://mmbiz.qpic.cn/a"/><img data-src="https://mmbiz.qpic.cn/b"/></div>"""
    result=extract(html,"https://mp.weixin.qq.com/s/images")
    assert result["status"]=="ok" and result["display_type"]=="image"
    assert len(result["images"])==2

def test_verification_rejected():
    assert extract("<title>请输入验证码</title>","https://mp.weixin.qq.com/s/test")["error_code"]=="ACCESS_RESTRICTED"

def test_no_body_rejected():
    assert extract("<div>Hello</div>","https://mp.weixin.qq.com/s/test")["error_code"]=="CONTENT_NOT_FOUND"
