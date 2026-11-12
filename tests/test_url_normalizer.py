import pytest
from url_normalizer import normalize_article_url
from app import valid

@pytest.mark.parametrize("input_url,expected",[
 ("https://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ","https://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ"),
 ("这篇文章：https://mp.weixin.qq.com/s/j8q018Lck1TWHO3NxQDiJQ 请阅读","https://mp.weixin.qq.com/s/j8q018Lck1TWHO3NxQDiJQ"),
 ("https://mp.weixin.qq.com/s?__biz=abc&amp;mid=123&amp;idx=1&amp;sn=def","https://mp.weixin.qq.com/s?__biz=abc&mid=123&idx=1&sn=def"),
 ("https://mp.weixin.qq.com/s?__biz=abc&mid=123&idx=1&sn=def","https://mp.weixin.qq.com/s?__biz=abc&mid=123&idx=1&sn=def"),
])
def test_valid(input_url,expected):
    assert normalize_article_url(input_url)==expected
    assert valid(input_url)

@pytest.mark.parametrize("bad",[
 "http://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ",
 "https://mp.weixin.qq.com.evil.org/s/cexkyzQBRDG3uIF6g5cEbQ",
 "https://attacker@mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ",
 "https://mp.weixin.qq.com:444/s/cexkyzQBRDG3uIF6g5cEbQ",
 "https://mp.weixin.qq.com/s?__biz=abc&mid=123&idx=1",
 "https://mp.weixin.qq.com/s/invalid",
 "https://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ#fragment",
])
def test_rejected(bad):
    assert normalize_article_url(bad) is None
