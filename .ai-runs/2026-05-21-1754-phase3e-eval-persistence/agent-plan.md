# Agent Plan

1. Add RED tests proving `POST /eval-runs` persists a run and `GET /eval-runs` returns stored history.
2. Add eval run repository models and in-memory implementation.
3. Wire `run_eval` and `list_eval_runs` through the service repository.
4. Add PostgreSQL eval repository and schema.
5. Extend runtime storage selection for PostgreSQL eval repositories.
6. Run targeted and full regression tests.
7. Run low-resource PostgreSQL smoke if the schema changes.
8. Update docs and verification records.
