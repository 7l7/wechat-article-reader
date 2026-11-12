# Public Plugin Directory readiness tracker

Last updated: 2026-11-12

## Proven working
- Public remote MCP endpoint: https://wechat-article-reader-mcp.onrender.com/mcp
- Read-only `read_wechat_articles` tool; max 5 article URLs
- User-provided HTML/Markdown import tool
- Actual public URL smoke result from 2026-11-12: `The Batch: 948 | GLM 5.1：面向长时任务的能力提升` (DeeplearningAI), 3141 Markdown characters. This was observed at the service's `tools/call` path using its JSON-RPC method; it is **not** a claim that the ChatGPT client installed and invoked this plugin.
- Access-restriction and parse-failure errors are explicit.

## Preparation not yet verified
- Publisher's verified identity / chosen developer name
- Jurisdiction/country targeting selection
- Whether monetization or purchases are planned (none is implemented in the current code; publisher must confirm)
- Logo and composer icon assets included in upload
- Four public listing URLs checked for working access and purpose
- Real reviewer-visible demo recording, hosted at an accessible URL
- Five positive and three negative review cases run against the final saved submission version
- Portal connection, security scans and owner legal attestations

## Required boundaries
- Do not claim that all public articles or original specified URLs work.
- Do not claim launch/review approval from private plugin creation.
- Respect restricted page access and user content permissions.
