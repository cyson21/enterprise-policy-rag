# Goal

Turn Retrieval Lab from a static preview into a live retrieval debugging screen using the existing retrieval-only API.

## Scope

- Use current workspace and active persona from the app shell.
- Let the user adjust query, top-k, and score threshold.
- Display retrieved chunks with rank, score, visibility, departments, and access reason.
- Keep this retrieval-only: no answer generation, OpenAI call, or eval runner.

## Out of Scope

- New backend answer API.
- LLM provider implementation.
- Eval scoring engine.
- Production admin dashboard.
