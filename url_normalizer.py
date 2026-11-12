"""Normalize ordinary public WeChat article URLs and reject unsafe destinations."""
import html
import re
from urllib.parse import urlsplit, parse_qs, urlunsplit

# Accept URL pasted alone or embedded in an ordinary message.
_CANDIDATE = re.compile(r"https://mp\.weixin\.qq\.com/s(?:/|\?)[^\s<>\"'\u3000]*", re.I)
_SHORT = re.compile(r"^/s/[A-Za-z0-9_-]{6,256}$")
_LONG_FIELDS = ("__biz","mid","idx","sn")

def normalize_article_url(value: str) -> str | None:
    if not isinstance(value,str) or len(value)>5000: return None
    value=html.unescape(value).strip()
    match=_CANDIDATE.search(value)
    if not match: return None
    candidate=match.group(0).rstrip(".,;!)]}。；，！）】")
    try:
        parts=urlsplit(candidate)
        if (parts.scheme!="https" or parts.hostname!="mp.weixin.qq.com"
            or parts.username is not None or parts.password is not None
            or parts.port not in (None,443) or parts.fragment):
            return None
        if _SHORT.fullmatch(parts.path):
            return urlunsplit(("https","mp.weixin.qq.com",parts.path,parts.query,""))
        if parts.path=="/s":
            params=parse_qs(parts.query,keep_blank_values=False)
            if all(params.get(k) and len(params[k])==1 for k in _LONG_FIELDS):
                return urlunsplit(("https","mp.weixin.qq.com",parts.path,parts.query,""))
    except ValueError:
        return None
    return None
