# Goal

## Objective

Implement Phase 1A: frontend shell and demo persona foundation for Enterprise Policy RAG.

## Scope

In scope:

- React/Vite frontend source scaffold under `web/`.
- App shell with sidebar, top bar, workspace badge, provider badge, and persona selector.
- Route placeholders for Search Console, Knowledge Library, Retrieval Lab, and Operations.
- Demo persona fixtures shared by UI and backend API.
- Backend `GET /workspaces/current` and `GET /personas` endpoints.
- No-key, no-network-install smoke validation.

Out of scope:

- PostgreSQL repository implementation.
- Search Console live retrieval wiring.
- Answer generation.
- Eval engine.
- OpenAI adapter.

## Exit Criteria

- Frontend shell files exist and pass static smoke checks.
- Backend persona/workspace endpoints pass API tests.
- Existing backend retrieval tests still pass.
- README/TODO/project-tracking reflect Phase 1A progress.
