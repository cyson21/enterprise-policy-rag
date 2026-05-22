# Goal

Add Operations query drilldown so a recent query row can show the stored retrieval, answer, and citation snapshots behind it.

## Scope

- Add `GET /queries/{query_id}`.
- Return query log metadata, retrieval result snapshots, answer metadata, and citation snapshots.
- Keep fake providers and API-key-free local verification.
- Add Operations UI selection for recent query rows.
- Keep OpenAI adapter and external LLM calls out of this slice.
