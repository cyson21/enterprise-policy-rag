# Agent Plan

## Context

- Phase 1B made Search Console call live retrieval data.
- Knowledge Library is still a static table preview.
- Demo documents already exist, but the API only supports ingest and retrieve.
- PostgreSQL/pgvector compose and schema exist; default app behavior remains fake-provider, API key-free local verification.

## Steps

- [x] Add failing backend tests for `GET /documents` and `GET /documents/{document_id}`.
- [x] Add failing frontend smoke checks for live Knowledge Library wiring markers.
- [x] Implement repository/service models for document summaries and document detail with chunks.
- [x] Add FastAPI and Starlette fallback routes for document list/detail.
- [x] Implement typed frontend document client and Knowledge Library live data state.
- [x] Run targeted tests, full backend tests, frontend smoke/build, compile smoke, compose config, and browser/API smoke.
- [x] Update README, TODO, project tracking, next-agent bootstrap, changed-files, decisions, and verification.

## Files Expected to Change

- `.ai-runs/2026-05-20-1542-phase1c-knowledge-library-api/*`
- `app/main.py`
- `app/models.py`
- `app/repository.py`
- `app/services.py`
- `tests/test_documents_api.py`
- `web/src/api/client.ts`
- `web/src/routes/knowledge/KnowledgePage.tsx`
- `web/scripts/smoke.mjs`
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`

## Risks

- Document detail must not expose documents from another workspace.
- Knowledge Library should remain a management/readiness surface, not answer generation.
- UI fallback data should preserve local display when the backend is not running.
