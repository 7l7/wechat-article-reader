# WeChat Article Reader — launch copy and distribution checklist

Status: **ready for editorial review / not posted**. Only mark a platform as published when a public post URL has been verified. Plugin directory approval is pending.

## X — launch post (English)

WeChat articles can be hard to read with AI browsing, so I built an open-source MCP reader for public WeChat Official Account links.

It extracts titles, publisher names, Markdown and image URLs, and returns explicit errors when a page is blocked.

✅ Read up to 5 public links per call
✅ ChatGPT/custom MCP compatible
❌ No private articles or login bypass
❌ Not yet listed in the ChatGPT plugin directory

Code + setup: https://github.com/7l7/wechat-article-reader

## X — follow-up technical post (English)

Under the hood: FastAPI + httpx + BeautifulSoup + markdownify, exposed via Streamable HTTP MCP.

Tools: `read_wechat_articles` and `import_wechat_article`.

A real public article was successfully read through the connected tool on Nov 12, 2026. Coverage varies with source access; inaccessible pages return an error rather than invented content.

Repo: https://github.com/7l7/wechat-article-reader

## 中文社媒（即刻 / V2EX / 开发者社区）

**开源一个能让 ChatGPT 读取微信公众号文章的 MCP 工具**

很多时候把微信公众号链接发给 AI，得到的不是文章内容，而是“无法访问”。我做了一个开源、只读的 WeChat Article Reader：

- 输入公开公众号文章链接，尝试提取标题、公众号名称、Markdown 正文和图片地址
- 一次最多处理 5 篇
- 提供标准 MCP 接口，可接入支持自定义 MCP 的客户端
- 文章无法访问时明确报错，不伪造正文
- 不读取私密文章，不绕过登录，不管理公众号账号

今天已经通过已连接的 ChatGPT 工具实测读取一篇公开文章；不是所有公众号链接都保证成功。当前尚未正式上架 ChatGPT 插件目录。

源码、接入说明和限制：https://github.com/7l7/wechat-article-reader

欢迎用**可公开分享**的文章链接反馈兼容性问题（不要提交 Cookie 或私密内容）。

## Reddit / Hacker News — avoid spam

Title: Show HN: Open-source MCP reader for public WeChat Official Account articles

Body: I built a small read-only MCP service for public WeChat article URLs. It extracts Markdown and metadata, supports batches of up to five, and fails explicitly when pages are inaccessible. The backend uses Python/FastAPI and does not require a WeChat account for public links. This is independent and not affiliated with WeChat. Source and limitations: https://github.com/7l7/wechat-article-reader . Feedback about accessible public examples welcome.

Use the appropriate community's posting rules. Do not cross-post identical content aggressively.

## Distribution and verification

| Channel | Action | Status | Evidence |
|---|---|---|---|
| GitHub | SEO README + accessible docs + llms.txt | PR pending review | Link to PR |
| X | Publish announcement | Not posted | Post URL needed |
| X | Publish technical follow-up after launch | Not posted | Post URL needed |
| 即刻/V2EX | Post Chinese developer announcement | Not posted | Post URL needed |
| Hacker News | Submit if community guidelines permit | Not posted | Post URL needed |
| Plugin directory | Complete submission and approval | Not listed | Official listing URL needed |

## Tracking (manual first)

Record posted_at, channel, canonical URL, impressions, profile visits, GitHub referral visits, stars, MCP connection attempts, successful public reads, and error categories. Avoid treating claimed AI mentions as measurable GEO traffic without source data.

## SEO / GEO quality gates

- Stable product naming: WeChat Article Reader / 微信公众号文章读取 MCP 工具
- Canonical link: repository until a dedicated docs domain exists.
- Claims cite actual tests, scope and restrictions. Do not claim universal access.
- Text accessible without JS, clear FAQ, original technical details, privacy and terms.
- Do not create mass-generated keyword pages or misleading “official WeChat” branding.
- `llms.txt` is supplementary machine-readable documentation, **not** a search ranking or AI recommendation guarantee.
