# Agent Plan

## Context

- Compose and schema already exist for PostgreSQL + pgvector.
- Runtime dependencies are declared in `pyproject.toml`, but the current local Python environment does not have `psycopg` installed.
- The safest next step is a repository implementation that is import-safe without `psycopg` and unit-tested through fake connections.

## Steps

- [x] Add failing repository tests for PostgreSQL insert SQL and row mapping.
- [x] Introduce a `PolicyRepository` protocol used by services and retrieval.
- [x] Implement `PostgresPolicyRepository` with optional `psycopg` import and explicit runtime error if the dependency is missing.
- [x] Keep `InMemoryPolicyRepository` as the default app path.
- [x] Run targeted repository tests, full pytest, compile smoke, compose config, and frontend smoke/build.
- [x] Update README, TODO, project tracking, next-agent bootstrap, changed-files, decisions, and verification.

## Risks

- Local environment cannot currently import `psycopg`; do not make module import fail.
- Do not require Docker or DB startup for ordinary pytest.
- Do not expose raw embeddings through API responses.
