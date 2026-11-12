# WeChat Article Reader — launch copy and distribution checklist

Status: **ready for editorial review / not posted**. Only mark a platform as published when a public post URL has been verified. Plugin directory approval is pending.

## X — launch post (English, concise)

A recurring problem: paste a WeChat article URL into an AI assistant, get “I can’t access it,” then manually copy the text.

I built WeChat Article Reader, an open-source MCP tool that *tries* to turn public WeChat links into attributable Markdown.

✅ Titles, publisher, text & image URLs
✅ Up to 5 links per call
✅ Explicit errors when blocked
❌ No private/login-protected content or bypass

Tested with a public article in ChatGPT today. Not yet listed in the plugin directory; individual links may fail.

https://github.com/7l7/wechat-article-reader

## X — optional follow-up thread

1/ Why build yet another reader? WeChat articles can be hard for generic web browsing tools to fetch. The fallback is tedious copying and pasting, especially when researching multiple sources.

2/ The goal isn't to scrape everything. It's a small, read-only MCP interface for **accessible public** links: source title, account, Markdown and image URLs.

3/ Crucial: if the source denies access or changes, the tool returns a failure. It doesn't invent an article. In one connected ChatGPT test (2026-11-12), it successfully read a public 刘润 article.

4/ Independent open source, no WeChat login, no private-content access, no claims of affiliation or universal success. Code, setup and known limits: https://github.com/7l7/wechat-article-reader

## 中文社媒（即刻 / V2EX / 开发者社区）：完整版

### 标题：为什么 AI 总读不到公众号文章？我开源了一个 MCP 阅读工具

平时做内容研究，最烦的一件事：找到一篇微信公众号文章，把链接发给 AI，让它提炼观点、对比资料，结果只得到一句“无法访问”。

接下来只能手工复制正文，丢失图片位置和来源信息；有时一口气要看好几篇，这个动作会重复很多次。

我因此做了 **WeChat Article Reader**，一个开源、只读的 MCP 工具。目标很简单：**让支持自定义 MCP 的 AI 客户端，尽量直接读取可公开访问的公众号文章，而不是要求用户每次手动搬运文本。**

它现在能做：
- 输入公开文章链接，返回标题、公众号名称、Markdown 正文及图片地址
- 一次处理最多 5 篇公开文章，适合研究和交叉阅读
- 支持 MCP 接入，AI 可以在原有对话里调用
- 遇到无法访问的页面，明确报错而不是编造文章内容

**实测情况：** 2026-11-12，在已连接的 ChatGPT 中成功解析刘润公众号的公开文章《为了让同事少加班，我手搓了一个自动工作台》。这证明该链接当时可读，不代表所有微信文章都能读。

**边界：** 不能读取私密或登录保护文章，不绕过微信权限，也不代替公众号后台。项目不是微信官方产品，ChatGPT 插件目录尚未正式上架。

源码和接入说明：https://github.com/7l7/wechat-article-reader

如果有可公开分享却无法读取的公众号链接，欢迎附失败信息提 Issue。不要提交 Cookie、私人文章或账号凭证。

## Reddit / Hacker News — transparent technical launch

Title: Show HN: An MCP reader for public WeChat articles

Body:

I regularly found that pasting a public WeChat Official Account URL into a generic AI browsing workflow failed, forcing manual copy/paste of the article and losing useful source information.

So I built WeChat Article Reader, a read-only, open-source Streamable HTTP MCP service in Python/FastAPI. For supported public URLs it extracts the title, account, Markdown and image URLs; it accepts up to five links per call. When WeChat blocks a page, it returns an error instead of fabricated content.

I verified a public article through a connected ChatGPT client on Nov 12, 2026, but compatibility varies by URL and the directory listing is not yet approved. No private content, no login bypass, and no affiliation with Tencent/WeChat.

Repo, setup, limitations: https://github.com/7l7/wechat-article-reader

Use each community's submission rules. Do not bulk cross-post or falsely claim a directory launch.

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
