# Agent Plan

## Context

- Master plan sets the next immediate work as `Phase 1A: Frontend Shell + Demo Personas`.
- Network package installation is not explicitly approved, so dependencies will be declared but not installed.
- Verification must still run without API keys or external AI calls.

## Steps

- [x] Create `.ai-runs/2026-05-20-1426-phase1a-frontend-shell/` records.
- [x] Add failing backend API tests for workspace/personas.
- [x] Add failing frontend static smoke script for required shell files and route labels.
- [x] Implement backend workspace/persona fixtures and endpoints.
- [x] Implement frontend React/Vite source scaffold and visual shell.
- [x] Run backend and frontend smoke checks.
- [x] Update README, TODO, project tracking, changed files, decisions, verification.

## Files Expected to Change

- `.ai-runs/2026-05-20-1426-phase1a-frontend-shell/*`
- `app/main.py`
- `app/personas.py`
- `tests/test_personas_api.py`
- `web/**`
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`

## Risks

- Frontend dependencies are not installed in the current environment.
- Static smoke checks prove structure and content, not a full browser render.
- The first UI must remain a compact product shell, not a landing page.
