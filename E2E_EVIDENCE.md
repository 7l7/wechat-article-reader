# Real-World Integration Evidence (2026-11-12)

## Public article retrieval — six independently published samples

Each sample was requested by the Render service using the actual `read_wechat_articles` or `read` path, not a mocked HTTP transport. The first two were requested together through the MCP JSON-RPC `tools/call` method. The next four were requested as independent, sequential public-URL reads. The tests used no cookies, credentials, proxies, CAPTCHA bypass, or browser automation.

| Article ID | Publisher returned by parser | Title returned by parser | Markdown characters | Result |
| --- | --- | --- | ---: | --- |
| `cexkyzQBRDG3uIF6g5cEbQ` | DeeplearningAI | The Batch: 948 | GLM 5.1：面向长时任务的能力提升 | 3,141 | PASS |
| `j8q018Lck1TWHO3NxQDiJQ` | 智源研究院 | 黄铁军：大模型时代，AI生态何以“根深叶茂” | 5,864 | PASS |
| `ZHLdNnASp-QMQ3MHmyUrKA` | 市值风云 | 强烈质疑大康农业涉嫌财务舞弊：一笔2.93亿元的离奇应收款 | 财务舞弊 | 14,350 | PASS |
| `izVZNkk4kEjZGf_Tqmz8FQ` | gsngzt | 好运哥2008：突发大利好！抓紧上车！ | 2,998 | PASS |
| `e6eY6v6TuMBL9WHzRhdGeg` | 财经早餐 | 【财经早餐】2022.06.05星期日 | 5,793 | PASS |
| `nEJhdxGea-KLZA_IGw9R5A` | 心智工具箱 | 成为自己，不完美，但美好 | 4,223 | PASS |

Render logs:
- 2026-11-12 08:10:13Z `MCP_TOOL_CALL_END outcomes=ok,ok`
- 2026-11-12 08:14:04–08:14:20Z four `MATRIX_PROBE_RESULT ... code=ok` entries.

## Independently exercised HTTPS MCP endpoint

At 2026-11-12 08:19:28Z, an independent HTTP client initiated HTTPS requests to the **public Render URL**, not `ASGITransport`, with ChatGPT-compatible `Accept`, `Origin`, and `MCP-Protocol-Version` headers.

- `initialize`: 200 `application/json`
- `tools/list`: 200 `application/json`
- `tools/call` (`read_wechat_articles`): 200 `application/json`
- Article title: The Batch: 948 | GLM 5.1：面向长时任务的能力提升
- Article body: 3,141 Markdown characters
- Result: `REMOTE_HTTPS_MCP_RESULT passed=True status=(200,200,200)`

## Important remaining limits

These tests **do not** prove that *every* arbitrary public WeChat URL works, that deleted/restricted links are readable, or that the ChatGPT client has installed or invoked the private plugin. Remote HTTPS invocation is proven from a separate client, **not from ChatGPT**.

The user-provided WeChat tab blocked by Browser Use was not accessed or bypassed during these tests.

All temporary startup probes have been removed from the production code following validation. The ongoing public service keeps explicit error responses for inaccessible articles.
