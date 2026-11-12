# Read WeChat Official Account Articles in ChatGPT — WeChat Article Reader

**WeChat Article Reader** is a read-only MCP server for publicly accessible WeChat Official Account articles (微信公众号文章). It extracts the article title, publisher, Markdown body and image URLs from supported public `mp.weixin.qq.com/s/...` links. The publication date is returned when detectable.

- Source code: https://github.com/7l7/wechat-article-reader
- MCP endpoint: https://wechat-article-reader-mcp.onrender.com/mcp
- Service health: https://wechat-article-reader-mcp.onrender.com/health
- Support: https://github.com/7l7/wechat-article-reader/issues

**Availability:** The source code and MCP endpoint are public. ChatGPT plugin-directory approval and listing are **not yet complete**. Users may connect the MCP server in a client that supports custom MCP connections where permitted by their plan and client.

## Problem

WeChat articles are sometimes inaccessible to conventional AI browsing. Copying long posts by hand loses formatting and image references. WeChat Article Reader offers an explicit tool that attempts to retrieve a public article and returns structured, attributable content. Not every article is accessible.

## How to use

1. In a compatible MCP client, add the server endpoint above according to that client's custom connector instructions.
2. Ask: "Use WeChat Article Reader to read https://mp.weixin.qq.com/s/Y-avtk21U7fDhJb0J-vbmg and summarize the key points."
3. Inspect the returned title, publisher, Markdown and image URLs. The tool returns an explicit error when the source cannot be accessed.
4. You can submit up to five public article URLs in a single `read_wechat_articles` call.

The server exposes `read_wechat_articles` and `import_wechat_article`. The latter only converts content supplied by the user; it does **not** circumvent restricted links.

## Example: verified public article

In a ChatGPT-connected test on November 12, 2026, the article **“为了让同事少加班，我手搓了一个自动工作台”** from **刘润** was successfully read via its public URL https://mp.weixin.qq.com/s/Y-avtk21U7fDhJb0J-vbmg. This confirms the tested URL, not universal link compatibility. The date field was unavailable in that result.

## Limitations

- Publicly accessible links only; no private conversations, login-protected articles or subscription access.
- Publisher sites can rate-limit, block or change markup.
- Metadata such as publish date can be unavailable.
- No publishing to WeChat; no bypass of account authentication.
- Respect publishers' copyright and terms; use excerpts and citations rather than republishing full articles.

## FAQ

### Can ChatGPT read a WeChat Official Account article from its URL?
With a compatible connected MCP client and a reachable public article, WeChat Article Reader can extract Markdown content and metadata. Success is not guaranteed for every link.

### Is WeChat Article Reader an official WeChat product?
No. It is an independent open-source utility and is not affiliated with Tencent or WeChat.

### Does it require a WeChat login?
Not for supported public links. It cannot access articles requiring a login.

### Can it read multiple articles at once?
Yes, up to five public URLs per call.

### Does it return images?
It returns discovered image URLs; rendering or downloading those images depends on the client and source access.

### Is it already listed in the ChatGPT plugin directory?
No. Public directory approval and listing have not been completed.

### What if an article is blocked?
The service reports an error. You may use `import_wechat_article` with HTML or Markdown that you have permission to provide.

### Can it automate my WeChat account?
No. The MCP tools are read-only and do not post, administer accounts or retrieve private content.

## Privacy

Read the [privacy policy](../PRIVACY.md) and [terms](../TERMS.md). The service does not intentionally store submitted article text in a database, but infrastructure logs may exist.

Updated: 2026-11-12.
