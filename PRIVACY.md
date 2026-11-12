# Article Lens — Privacy Policy

**Last updated:** 12 November 2026

Article Lens is an independent third-party tool; it is not affiliated with Tencent or WeChat.

## Service
Article Lens is a read-only article extraction tool. It receives URLs of publicly accessible WeChat Official Account articles and returns article metadata and text, or an explicit error. It also supports HTML or Markdown provided directly by the user.

## Information processed
- For URL reads, the service processes the submitted article URL and the page content retrieved from WeChat.
- For imports, the service processes HTML or Markdown supplied by the user.
- Standard request metadata (such as timestamp, source network address and request outcome) may be processed by our hosting provider for hosting, availability and abuse prevention.
- The service does not ask for your WeChat password, authentication cookies or account credentials.

## Sharing and external services
The article URL is sent to `mp.weixin.qq.com` to retrieve the page. Requests are handled by the infrastructure provider Render. Content returned to ChatGPT is processed under the terms of the ChatGPT service and any connected account configuration. We do not sell submitted content or use it to train our own model.

## Storage and logging
The application does not intentionally store submitted article URLs, article bodies or imported HTML/Markdown in a database. It logs operational outcomes, such as success and error categories, without logging article bodies. Infrastructure providers may retain server and request logs under their own operational policies. We have not specified a guaranteed log-retention period.

## User choices
Do not submit confidential, sensitive or unauthorized content. Do not submit third-party private material without permission. The tool can be disconnected from your ChatGPT account. For support or concerns, use the project's GitHub issue tracker.

## Security
URL retrieval is restricted to the HTTPS `mp.weixin.qq.com` article endpoint. It does not use your logged-in WeChat session or attempt to bypass access checks. Access restrictions may prevent retrieval.

## Changes
This policy may be revised as the service evolves. Material changes will be reflected on this page.

**Support:** https://github.com/7l7/wechat-article-reader/issues
