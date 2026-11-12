"""Extract publicly available WeChat article HTML; does not fetch or bypass access controls."""
import html
import json
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

SCRIPT_VALUE = re.compile(r"""(?:^|[;\s])(?:var\s+)?([A-Za-z_]\w*)\s*=\s*(["'])(.*?)\2""", re.S)
TYPE_RE = re.compile(r"""(?:var\s+)?item_show_type\s*=\s*["']?(\d+)""")
TS_RE = re.compile(r"""(?:var\s+)?(?:ct|publish_time)\s*=\s*["']?(\d{10})""")
BLOCKED = ("访问过于频繁", "请输入验证码", "操作过于频繁", "环境异常", "请在微信客户端打开")

def extract(html_text: str, url: str) -> dict:
    """Parse known WeChat article layouts from already-retrieved HTML."""
    soup = BeautifulSoup(html_text, "html.parser")
    raw = html_text[:3000000]
    if any(marker in raw for marker in BLOCKED) and not soup.select_one("#js_content"):
        return {"status":"error", "source_url":url, "error_code":"ACCESS_RESTRICTED",
                "message":"WeChat returned a restricted-access page"}
    def meta(*names):
        for name in names:
            el = soup.select_one(f'meta[property="{name}"]') or soup.select_one(f'meta[name="{name}"]')
            if el and el.get("content", "").strip():
                return html.unescape(el["content"]).strip()
        return ""
    def node(*selectors):
        for selector in selectors:
            el = soup.select_one(selector)
            if el and el.get_text(" ", strip=True):
                return el.get_text(" ", strip=True)
        return ""
    def script_value(key):
        for match in SCRIPT_VALUE.finditer(raw):
            if match.group(1) == key:
                return html.unescape(match.group(3))
        return ""
    title = node("#activity-name", ".rich_media_title") or meta("og:title", "twitter:title") or script_value("msg_title")
    account = node("#js_name", ".profile_nickname") or script_value("nickname") or meta("author")
    intro = meta("og:description", "description")
    publish = node("#publish_time") or script_value("publish_time")
    if not publish:
        ts = TS_RE.search(raw)
        if ts:
            publish = datetime.fromtimestamp(int(ts.group(1)), timezone.utc).isoformat()
    display = TYPE_RE.search(raw)
    type_id = display.group(1) if display else "0"
    body = soup.select_one("#js_content") or soup.select_one(".rich_media_content")
    if body is None:
        return {"status":"error","source_url":url,"error_code":"CONTENT_NOT_FOUND",
                "message":"No known public article body","title":title,"account":account}
    for element in body.select("script,style,noscript,iframe"):
        element.decompose()
    images = list(dict.fromkeys(src for im in body.select("img")
        if (src := im.get("data-src") or im.get("data-original") or im.get("src") or "").startswith(("https://","http://"))))
    text = body.get_text(" ",strip=True)
    # Video/image-only posts genuinely may have no long textual body.
    display_type = {"5":"video","7":"audio","8":"image","10":"text"}.get(type_id,"article")
    if len(text) < 40 and not (images and display_type=="image"):
        return {"status":"error","source_url":url,"error_code":"CONTENT_TOO_SHORT",
                "message":"No substantial visible article text; media-only posts require dedicated handling",
                "title":title,"account":account,"display_type":display_type}
    from markdownify import markdownify as convert
    for image in body.select("img"):
        source = image.get("data-src") or image.get("data-original") or image.get("src")
        if source:
            image["src"] = source
    md = convert(str(body), heading_style="ATX", strip=["script","style"]).strip()
    if not md and images:
        md = "\n".join(f"![]({u})" for u in images)
    return {
      "status":"ok","source_url":url,"title":title,"account":account,
      "published_at":publish,"description":intro,"display_type":display_type,
      "markdown":md[:75000],"truncated":len(md)>75000,
      "images":images[:100],"text_length":len(text),
      "source_method":"public_html"
    }
