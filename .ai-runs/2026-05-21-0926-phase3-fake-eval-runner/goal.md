# Goal

Add a fake-provider eval runner and Operations eval table that work without Docker, OpenAI, or external services.

## Scope

- Add deterministic golden question set.
- Evaluate retrieval hit and citation coverage using existing retrieval/answer services.
- Add `POST /eval-runs` and `GET /eval-runs`.
- Show latest eval run in Operations.

## Out of Scope

- Persisted eval history.
- PostgreSQL-backed eval tables.
- OpenAI or real LLM evaluation.
- Production admin dashboard.
