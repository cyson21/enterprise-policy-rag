# Agent Plan

## Architecture

- Add an `AuthContextProvider` boundary with two modes:
  - `demo`: default local/static-friendly auth context using the existing demo persona.
  - `trusted_headers`: future production gateway/SSO handoff mode, disabled unless explicitly configured.
- Add `GET /auth/session` so clients can inspect the current workspace/user/department/role context.
- Add session-bound `POST /auth/retrieve` and `POST /auth/answer` endpoints that derive permission inputs from auth context instead of trusting request body persona fields.
- Keep existing `/retrieve` and `/answer` endpoints unchanged for demo/persona testing.
- Add a small UI status pill for the current auth mode; keep the persona selector for portfolio demos.

## Steps

1. Write failing backend tests for demo auth session, trusted header normalization, and session-bound retrieval permission filtering.
2. Implement the minimal auth provider models and route wiring.
3. Add frontend auth session fallback, API client call, top-bar status pill, and smoke labels.
4. Write the auth/SSO design document and update API/data-model and project tracking docs.
5. Run targeted tests, full pytest, frontend smoke/build/static smoke, and git checks.
6. Commit and push the completed slice.

