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

## 2026-11-12 public listing hardening

- Package draft v0.5.0 created; icon 512×512, root portable MCP schema, 5 positive and 3 negative review cases.
- Added public Privacy Policy and Terms draft, improved README/support, and review demo plan.
- Added per-process rate limiting, 200 KB bounded JSON request streaming, 8 MB decompressed HTML streaming limit, concurrency cap 3, both tool annotations, and code regression fixtures.
- **Latest actual real article test after stream/gzip fix passed** at 2026-11-12 07:25:41Z: `RELEASE_CANARY_PASS`, title `The Batch: 948 | GLM 5.1：面向长时任务的能力提升`, publisher `DeeplearningAI`, 3141 Markdown chars through MCP tool call. This is server-side evidence, not a ChatGPT host recording.
- Temporary public test removed from startup; final source version v0.5.0 in commit `f27bf3e7`.

Remaining for public listing: verified publisher identity, policy approval, country targeting and commerce confirmation, unauthenticated access check of all 4 published listing URLs, real ChatGPT demo recording and URL, full 5+3 case execution in the exact saved Portal version, Portal validation/scans/attestations, submission and approval. No public approval claimed.

## Article Lens public candidate — 2026-11-12

- Private package is already renamed to **Article Lens v0.6.1**; original plugin ID and MCP endpoint retained.
- Public-review candidate refreshed to **Article Lens v0.6.1**. The ZIP has passed local structure checks: 512 × 512 icon, portable plugin.json, mcp.json, original server URL, five positive review cases and three negative review cases.
- First review case tests real article; second tests two **different** articles in a single batch rather than a duplicated sample; the others test HTML import, Markdown import and URL pasted in prose. Negative cases test publish, private messages and purchases.
- README, privacy policy, terms and demo plan have been rebranded to Article Lens and identify the plugin as independent of Tencent/WeChat.
- Existing integration evidence: six public articles passed live MCP reads and remote HTTPS MCP initialize/list/call succeeded. These are not substitutes for the public Directory portal's saved-version case runs.
- Four listing URLs are present in package metadata and corresponding repository files exist. External unauthenticated URL inspection via web fetch failed (cache misses); **access/content verification is not yet passed**.
- Publisher legal identity, policy approval, selected countries, commerce confirmation, **real** ChatGPT demo recording, reviewer-facing hosted recording URL, portal submission and attestations remain unresolved. Do not treat candidate ZIP as submission-ready.

## Public release validation on 2026-11-12

- Rebuilt separate portable submission candidate as Article Lens v0.6.1 (public manifest internal slug `article-lens`; remote MCP key `article-lens`; onboarding skill `read-public-articles`). This is intentionally separate from the already-installed private `wechat-article-reader` plugin and does not replace its connection.
- Verified ZIP inventory: `plugin.json`, `mcp.json`, `README.md`, `assets/icon.png` (512x512 PNG), and `skills/read-public-articles/SKILL.md`. JSON parse, ZIP CRC, semantic version, absent `.app.json`/apps bindings, and five positive plus three negative cases passed local package checks.
- The current release has **no commerce feature**; `review.commerce=false` reflects observed behavior, not any claim about future features.
- Live ChatGPT-connected MCP calls on 2026-11-12: five distinct article URLs in one call all status=ok, titles/accounts present, Markdown lengths 3149 / 5864 / 14350 / 2998 / 5793. User-provided HTML and Markdown import both status=ok and marked their provenance.
- No available subagent/delegate executor was exposed to this conversation; package checks and live connector calls were executed directly. Do not claim delegated review.
- Unfinished external release gates: verified publisher identity and consent, eligible project/organization, real video walkthrough URL demonstrating the exact plugin in ChatGPT, live portal import/connection and DNS domain verification, applicable portal scans, review case execution in the saved draft, published four-URL access checks, target country confirmation, and required owner legal attestations. None may be fabricated or auto-attested.
- Authoritative submission guide: https://developers.openai.com/plugins/deploy/submission and errors: https://developers.openai.com/plugins/deploy/submission-errors .
- No public Plugin Directory upload, review submission, approval, or publication has occurred.
