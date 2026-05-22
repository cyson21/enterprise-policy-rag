# Goal

Persist query evidence details for retrieval and answer flows, then expose top evidence usage in Operations.

Scope:

- Store retrieval result rows under each retrieval query log.
- Store answer rows and citation rows under each answer query log.
- Expose `GET /evidence/top` so Operations can show the most-used evidence documents.
- Add PostgreSQL schema and repository behavior while keeping Docker optional for normal tests.

Out of scope:

- OpenAI API calls.
- Production admin dashboard.
- Full eval result persistence.
