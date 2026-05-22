# Decisions

- Keep `InMemoryPolicyRepository` as the default app repository so local UI and CI remain API key-free and DB-free.
- Add a `PolicyRepository` protocol so retrieval/service code can accept either in-memory or PostgreSQL implementations.
- Make `PostgresPolicyRepository` import-safe when `psycopg` is not installed, but fail clearly at repository construction without an injected connection.
- Rank retrieval in application code for now; PostgreSQL repository returns joined chunks with embeddings and metadata.
- Store pgvector embeddings as vector literals like `[0.5,0.25]` through the DB adapter and never expose raw vectors through document detail API.
- Add `RUN_POSTGRES_TESTS=1` integration test entrypoint, but keep it skipped by default because ordinary pytest should not require Docker or psycopg.
- Replace root web scripts with `scripts/run-web-task.mjs` so scripts do not depend on nested `pnpm` being available in PATH.
