# Changed Files

## Backend

- `app/models.py`
  - Added query trend response models.
- `app/query_logs.py`
  - Added `list_query_trend` to the query log repository boundary.
  - Implemented in-memory daily trend aggregation.
  - Implemented PostgreSQL daily trend aggregation from the latest N days.
- `app/services.py`
  - Added `get_query_trend`.
- `app/main.py`
  - Added `GET /metrics/trend` for FastAPI and Starlette fallback paths.

## Frontend

- `web/src/api/client.ts`
  - Added query trend types, API client, and offline fallback data.
- `web/src/routes/operations/OperationsPage.tsx`
  - Added Query Trend table to Operations.
- `web/scripts/smoke.mjs`
  - Added smoke coverage for the Query Trend section.

## Tests

- `tests/test_operations_api.py`
  - Added API behavior coverage for retrieval/answer trend grouping.
- `tests/test_query_logs.py`
  - Added repository mapping coverage for PostgreSQL trend rows.
- `tests/test_postgres_runtime_integration.py`
  - Added runtime smoke assertion for `/metrics/trend`.

## Docs

- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`
- `docs/api-data-model.md`
- `docs/runbooks/local-demo.md`
- `docs/portfolio-one-pager.md`
