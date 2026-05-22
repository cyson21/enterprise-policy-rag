# Decisions

- Use the existing retrieval-only `/api/retrieve` endpoint instead of adding a debug endpoint in this slice.
- Reuse `loadRetrieval` so Search Console and Retrieval Lab share request/response typing.
- Keep active workspace/persona controlled by the app shell.
- Show rank, score, visibility, departments, source, and access reason in the debug panel.
- Clamp top-k to `1..10` and score threshold to `0..1` before sending the request.
- Do not add generated answers, LLM provider code, eval runner, or Operations metrics in this slice.
