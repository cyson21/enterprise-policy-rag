# Agent Plan

## Context

- Operations route currently renders static cards.
- Product plan calls for operating metrics, but eval and answer layers are out of this slice.
- Seeded metrics are enough to make the screen portfolio-visible while preserving the retrieval-core boundary.

## Steps

- [x] Add failing backend tests for metrics summary and recent query APIs.
- [x] Add failing frontend smoke markers for live Operations wiring.
- [x] Implement seeded operations models and FastAPI/Starlette routes.
- [x] Implement typed frontend operations client and live Operations screen.
- [x] Run API tests, full pytest, frontend smoke/build, compile smoke, compose config, and browser smoke.
- [x] Update README, TODO, project tracking, next-agent bootstrap, changed-files, decisions, and verification.

## Risks

- Do not imply production observability or real eval execution.
- Keep values clearly seeded/demo while looking like credible operating data.
- Do not add an LLM answer layer through the metrics work.
