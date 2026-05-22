# Agent Plan

## Context

- Phase 1A added the React/Vite shell and persona fixtures.
- Phase 1B must make Search Console use actual retrieval data instead of static preview.
- The app still uses in-memory repository and fake embeddings; PostgreSQL persistence is Phase 1C.

## Steps

- [x] Add failing backend tests for retrieval metadata, score threshold, and persona-specific demo results.
- [x] Add failing frontend smoke checks for live retrieval wiring markers.
- [x] Implement backend access reason, rank, visibility, department ids, and score threshold.
- [x] Seed deterministic demo documents into the app factory for UI runs.
- [x] Implement typed frontend retrieval client and Search Console live state.
- [x] Run backend tests, pnpm smoke/build, and browser DOM smoke.
- [x] Update README/TODO/project tracking and this run's changed-files/decisions/verification.

## Files Expected to Change

- `.ai-runs/2026-05-20-1532-phase1b-search-live-retrieval/*`
- `app/main.py`
- `app/models.py`
- `app/retrieval.py`
- `app/services.py`
- `app/demo_data.py`
- `tests/test_retrieval_metadata_api.py`
- `web/src/api/client.ts`
- `web/src/routes/search/SearchPage.tsx`
- `web/src/components/layout/AppShell.tsx`
- `web/src/app/App.tsx`
- `web/scripts/smoke.mjs`
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`

## Risks

- Browser frontend needs a backend URL; use relative API paths with Vite proxy.
- Existing API tests should remain isolated from demo seed data.
- Search UI should remain retrieval-only, not imply generated answers.
