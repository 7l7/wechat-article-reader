# App Review Walkthrough — WeChat Article Reader

This is a **recording plan**, not a recorded video or proof of publication. The recorded demo must display actual interactions in the ChatGPT client with the final candidate version.

## Preflight
1. Connect the review candidate's remote MCP endpoint: `https://wechat-article-reader-mcp.onrender.com/mcp`.
2. Ensure the tool list contains `read_wechat_articles` and `import_wechat_article`.
3. Use only public sample URLs and non-sensitive, example HTML/Markdown. Do not show credentials or private conversations.

## Recorded sequence
1. Ask ChatGPT: `Read this public WeChat article: https://mp.weixin.qq.com/s/cexkyzQBRDG3uIF6g5cEbQ`.
   Capture the real tool call, verified title, account and body excerpt, then a grounded summary. If the source is currently blocked, do not present a fabricated success; use an accessible public article for the recording and disclose the change.
2. Ask: `Convert this article HTML into Markdown: <html><body><article><p>First article paragraph about a real-world topic.</p><p>Second article paragraph that explains how to use the tool responsibly.</p></article></body></html>`.
   Verify `import_wechat_article` with `format=html` runs, preserves paragraphs and marks provenance as `user_supplied_html`.
3. Ask: `Publish this article to my WeChat account`.
   Verify no tool is invoked; explain that publishing is outside this read-only plugin.
4. Show that a restricted or invalid URL returns the actual error instead of invented article text.

## Video capture criteria
- Actual host interaction and visible tool results, not slides/mockups.
- Readable text, no secrets.
- Publicly accessible HTTPS video link playable by a reviewer without signing in.
- Playback checked, then recording URL included in the submission metadata.

## Evidence status
2026-11-12: Server-side real MCP tools/call smoke returned title `The Batch: 948 | GLM 5.1：面向长时任务的能力提升`, account `DeeplearningAI`, Markdown chars 3141. The ChatGPT-hosted UI recording has **not** been captured.
