# Agent Plan

1. Add RED API tests for top evidence after retrieval/answer calls.
2. Add RED repository tests for in-memory and PostgreSQL evidence persistence.
3. Implement Pydantic models for evidence detail and top evidence response.
4. Extend query log repositories with retrieval result, answer, citation storage.
5. Wire `PolicyRagServices.retrieve` and `.answer` to persist detail rows.
6. Add `GET /evidence/top` to FastAPI and Starlette fallback paths.
7. Add Operations UI/API client display for top evidence documents.
8. Add PostgreSQL schema tables and indexes.
9. Run targeted tests, full regression, frontend smoke/build, and optional low-resource PostgreSQL smoke if needed.
10. Update README/TODO/project tracking/bootstrap/API/runbook and record verification.
