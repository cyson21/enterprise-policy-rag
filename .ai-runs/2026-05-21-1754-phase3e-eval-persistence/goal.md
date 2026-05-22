# Goal

Persist fake-provider eval runs and case results so Operations can list eval history instead of recomputing a synthetic run on every read.

Scope:

- Store eval run summary and per-case results.
- Keep fake provider and golden-demo dataset.
- Add in-memory and PostgreSQL repository implementations.
- Keep default local tests Docker-free.

Out of scope:

- External LLM judge.
- OpenAI adapter.
- Advanced trend charts.
