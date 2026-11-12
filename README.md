# Article Lens — Public Article Reader

**Article Lens** is an independent, read-only article extraction service for publicly accessible article links from supported sources. Currently it supports public WeChat Official Account article URLs and user-provided HTML or Markdown.

> Independent third-party tool. Not affiliated with, sponsored by, or endorsed by Tencent or WeChat.

## Supported workflows
- Read up to five public article URLs per request.
- Extract original title, account, publication date if present, Markdown text, and image links.
- Import user-supplied HTML and Markdown without requesting a remote article.
- Return explicit errors for inaccessible, invalid, deleted, or restricted pages. The tool does not bypass source restrictions.

The service does not log into messaging accounts, access private chats, publish content, purchase anything, or guarantee that every article remains retrievable. Respect source copyright and terms.

## Connection

MCP endpoint: `https://wechat-article-reader-mcp.onrender.com/mcp`

Health: `https://wechat-article-reader-mcp.onrender.com/health`

Transport: HTTPS streamable HTTP JSON-RPC. Tools: `read_wechat_articles` and `import_wechat_article`.

The internal MCP tool and server identifiers retain their historical names to preserve backward compatibility. The public-facing name is **Article Lens**.

## Privacy, terms and support

- [Privacy policy](PRIVACY.md)
- [Terms of service](TERMS.md)
- [Support and bug reports](https://github.com/7l7/wechat-article-reader/issues)

## Evidence

- [Live integration evidence](E2E_EVIDENCE.md): six independently published public articles successfully parsed; remote HTTPS MCP initialization, discovery, and real article retrieval passed from an external test client.
- Testing does not guarantee universal access, nor does a server test substitute for ChatGPT-hosted submission review.

## Developer operations

Python / FastAPI / httpx / BeautifulSoup / markdownify.

Run tests using `pip install -r requirements-dev.txt && python -m pytest -q`.

Deployment: Render Python web service using `uvicorn app:app --host 0.0.0.0 --port $PORT`. The production server includes bounded download sizes, request caps, and a single-process rate limiter.

## Publication

Public Plugin Directory submission is being prepared and has **not** been approved. See [readiness tracker](SUBMISSION_READINESS.md) and [demo instructions](REVIEW_DEMO_PLAN.md).
