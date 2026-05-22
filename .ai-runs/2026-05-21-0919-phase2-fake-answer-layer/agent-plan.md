# Agent Plan

## Context

- Retrieval core, Search Console, Knowledge Library, Retrieval Lab, and Operations are working without Docker.
- `LLMProvider` exists as an interface placeholder, but no answer layer exists.
- This slice must remain API key-free and provider-isolated.

## Steps

- [x] Add failing backend tests for `/answer`, citations, permission filtering, and refusal when evidence is missing.
- [x] Add failing frontend smoke markers for answer/citation Search Console wiring.
- [x] Implement answer request/response models and `FakeLLMProvider`.
- [x] Implement `AnswerService` using retrieval results as evidence.
- [x] Add FastAPI and Starlette fallback routes for `/answer`.
- [x] Wire Search Console to `loadAnswer` and display answer, citations, refusal, token/cost metadata.
- [x] Run API tests, full pytest, frontend smoke/build, compile smoke, compose config, and browser/API smoke.
- [x] Update README, TODO, project tracking, next-agent bootstrap, changed-files, decisions, and verification.

## Risks

- Do not bypass retrieval permission filtering.
- Do not call external AI services.
- Do not make answer text look like a real OpenAI response.
- Keep refusal behavior explicit when citations are empty.
