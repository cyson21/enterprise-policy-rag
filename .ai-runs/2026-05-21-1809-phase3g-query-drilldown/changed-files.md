# Changed Files

## Backend

- `app/models.py`
  - Added query detail response models for query metadata, retrieval snapshots, answer metadata, and citation snapshots.
- `app/query_logs.py`
  - Added `get_query_detail` to the query log repository boundary.
  - Implemented in-memory query detail lookup.
  - Implemented PostgreSQL query detail lookup across `query_logs`, `retrieval_results`, `answers`, and `citations`.
- `app/services.py`
  - Added query detail service method.
- `app/main.py`
  - Added `GET /queries/{query_id}` to FastAPI and Starlette fallback paths.

## Frontend

- `web/src/api/client.ts`
  - Added query detail types, API client, and fallback detail.
- `web/src/routes/operations/OperationsPage.tsx`
  - Added selectable recent query rows and Query Detail panel.
- `web/src/styles/tokens.css`
  - Added selected query row and detail panel styles.
- `web/scripts/smoke.mjs`
  - Added smoke labels for query drilldown.

## Tests

- `tests/test_operations_api.py`
  - Added API coverage for retrieval query detail and answer/citation query detail.
- `tests/test_query_logs.py`
  - Added in-memory and fake PostgreSQL query detail mapping coverage.
- `tests/test_postgres_runtime_integration.py`
  - Added actual PostgreSQL runtime smoke for `/queries/{query_id}`.

## Docs

- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`
- `docs/api-data-model.md`
- `docs/runbooks/local-demo.md`
- `docs/portfolio-one-pager.md`
