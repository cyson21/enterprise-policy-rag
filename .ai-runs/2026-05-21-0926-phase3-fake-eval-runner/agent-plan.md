# Agent Plan

## Context

- Retrieval and fake answer APIs work without Docker.
- Operations already shows seeded metrics and recent query rows.
- TODO still has golden question set, retrieval hit, citation coverage, eval report, and eval result display.

## Steps

- [x] Add failing backend tests for eval run API and eval run list API.
- [x] Add failing frontend smoke markers for eval table wiring.
- [x] Implement golden question set and eval runner using `PolicyRagServices`.
- [x] Add FastAPI and Starlette fallback routes for `/eval-runs`.
- [x] Implement typed frontend eval client and Operations eval table.
- [x] Run targeted tests, full pytest, frontend smoke/build, compile smoke, compose config, and browser/API smoke.
- [x] Update README, TODO, project tracking, next-agent bootstrap, changed-files, decisions, and verification.

## Risks

- Eval must stay deterministic and fake-provider based.
- Do not imply production persistence.
- Do not require Docker or OpenAI.
