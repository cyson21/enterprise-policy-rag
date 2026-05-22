# Changed Files

- `app/runtime.py`
  - Adds `build_services_from_env()` for `DATABASE_URL` based repository selection.
- `app/main.py`
  - Uses the runtime builder when constructing the shared service instance.
- `tests/test_runtime_storage.py`
  - Covers in-memory default and PostgreSQL selection behavior.
- `tests/test_postgres_runtime_integration.py`
  - Covers document ingestion, retrieval, query log, and metrics flow through the app factory with PostgreSQL runtime repositories.
- `README.md`, `TODO.md`, `docs/project-tracking.md`, `docs/next-agent-bootstrap.md`, `docs/api-data-model.md`, `docs/runbooks/local-demo.md`, `docs/portfolio-one-pager.md`
  - Update current status, runtime storage behavior, PostgreSQL verification commands, and next-step guidance.
- `.ai-runs/2026-05-21-1716-runtime-postgres-selection/*`
  - Records this run's goal, plan, decisions, changed files, and verification.
