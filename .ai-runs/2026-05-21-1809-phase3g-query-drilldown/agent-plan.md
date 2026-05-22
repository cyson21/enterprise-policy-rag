# Agent Plan

1. Add RED API tests for query drilldown on retrieval and answer query rows.
2. Add response models for query detail, retrieval snapshots, answer metadata, and citations.
3. Extend `QueryLogRepository` with query detail lookup.
4. Implement in-memory and PostgreSQL lookup paths.
5. Add FastAPI and Starlette fallback route `GET /queries/{query_id}`.
6. Connect Operations UI to select a recent query and render its detail panel.
7. Add frontend smoke coverage.
8. Run Python, frontend, compose, and low-resource PostgreSQL verification.
9. Update README, TODO, project tracking, API/data-model, runbook, one-pager, bootstrap, and this run ledger.
