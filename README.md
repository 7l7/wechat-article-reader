# WeChat Article Reader — Read Public WeChat Articles in ChatGPT via MCP

**Open-source WeChat Official Account article reader (微信公众号文章读取工具)** for AI assistants. Turn supported public `mp.weixin.qq.com/s/...` links into attributable Markdown, with the article title, publisher and image URLs. Useful for ChatGPT research, summarization and citation workflows; inaccessible pages return explicit errors rather than fabricated content. **Not an official WeChat/Tencent tool.**

[Setup guide, examples and FAQ](docs/WECHAT_READER_GUIDE.md) · [AI-readable product facts](llms.txt) · [Report a public URL issue](https://github.com/7l7/wechat-article-reader/issues)

A read-only MCP service that extracts metadata and Markdown from **publicly accessible** WeChat Official Account articles. Designed to let a ChatGPT plugin read and summarize articles from their original public URLs.

## What it does

- Fetch up to five publicly accessible `https://mp.weixin.qq.com/s/...` URLs per call.
- Extract the article title, account name, date when present, Markdown text, and image URLs.
- Convert HTML/Markdown that the user explicitly supplies.
- Clearly report inaccessible or restricted articles rather than fabricating content.

The service cannot access private WeChat chats, login-protected articles, subscriptions, or account settings. It does not automate posting or payments.

## Quick start

In a ChatGPT client or MCP application that permits custom MCP servers, connect the endpoint below, then ask:

> Use WeChat Article Reader to read https://mp.weixin.qq.com/s/Y-avtk21U7fDhJb0J-vbmg and summarize it with source attribution.

This example article was successfully read by a connected ChatGPT tool on 2026-11-12. That does not guarantee access to every WeChat article.

## MCP connection

**Endpoint:** `https://wechat-article-reader-mcp.onrender.com/mcp`  
**Health:** https://wechat-article-reader-mcp.onrender.com/health  
**Transport:** Streamable HTTP / JSON-RPC  
**Tools:** `read_wechat_articles`, `import_wechat_article`

A public test article at `https://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ` returned 3,141 Markdown characters, with an attributed title and publisher, during a Render service-side MCP tools/call test on 2026-11-12. Live availability can change; one successful read is not a guarantee of universal access or ChatGPT-client end-to-end compatibility.

## Privacy and terms

- [Privacy Policy](PRIVACY.md)
- [Terms of Service](TERMS.md)

The application does not intentionally persist article content or submitted URLs in a database; the hosting platform may retain standard operational logs. Article URLs are sent to WeChat to retrieve public pages. For details, see the policy.

## Support

Open an issue at [GitHub Issues](https://github.com/7l7/wechat-article-reader/issues). Include the failure code and a public example URL if you have permission to share it. Do **not** post confidential data, account cookies, passwords or private articles.

## Developer notes

- Python / FastAPI / httpx / BeautifulSoup / markdownify
- Code: `app.py`, `article_extractor.py`
- Tests: `python -m pytest tests -q`
- Deployment: Render Python web service, `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Abuse control: in-memory request limiter and bounded HTTP payload; review scaling limits before exposing to large public traffic.

## Public listing

Plugin-directory submission is being prepared. Public approval and publication have **not** occurred. See [submission readiness](SUBMISSION_READINESS.md).
