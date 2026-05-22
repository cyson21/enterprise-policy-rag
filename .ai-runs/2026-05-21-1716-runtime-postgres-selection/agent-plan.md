# Agent Plan

1. Add RED tests for runtime repository selection:
   - no `DATABASE_URL` uses in-memory document/query log repositories
   - `DATABASE_URL` uses PostgreSQL document/query log repositories with the same DSN
2. Implement a small runtime storage builder module.
3. Wire `create_app()` through the builder.
4. Keep normal test runs API-key-free and Docker-free.
5. If Docker remains off, validate PostgreSQL path with unit tests and compose checks only.
6. If a low-resource Docker check is needed and available, run only the PostgreSQL app smoke.
7. Update README/TODO/project tracking/bootstrap/API docs and record verification.
