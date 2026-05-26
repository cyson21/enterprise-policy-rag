# Changed Files

## Backend

- `app/auth.py`
  - Added `AuthContextProvider` boundary with demo and trusted-header providers.
  - Added `AuthSession` and `SessionSearchQuery` models.
- `app/main.py`
  - Added `GET /auth/session`.
  - Added `POST /auth/retrieve` and `POST /auth/answer`.
  - Wired session-bound endpoints so permission fields come from auth context.
- `tests/test_auth_context.py`
  - Added TDD coverage for demo session, trusted header normalization, session-bound retrieval/answer, and missing identity headers.

## Frontend

- `web/src/api/client.ts`
  - Added `getAuthSession` and static fallback auth session.
- `web/src/app/App.tsx`
  - Loads auth session context and passes auth mode to the shell.
- `web/src/components/layout/AppShell.tsx`
  - Shows current auth session mode in the top bar.
- `web/src/utils/display.ts`
  - Added auth mode display formatting.
- `web/src/styles/tokens.css`
  - Added auth status pill styling.
- `web/scripts/smoke.mjs`
  - Added auth session labels to frontend smoke.
- `scripts/smoke-static-demo.mjs`
  - Added auth session text to static rendered smoke.

## Docs

- `docs/internal/design/2026-05-26-production-auth-sso-design.md`
  - Added production auth/SSO boundary design and excluded scope.
- `docs/api-data-model.md`
  - Documented auth endpoints, auth provider selection, `AuthSession`, and `SessionSearchQuery`.
- `README.md`
  - Updated current implementation and next slice.
- `TODO.md`
  - Marked production auth/SSO boundary complete and moved real IdP/OIDC adapter to future work.
- `docs/project-tracking.md`
  - Added Phase 5A snapshot.
- `docs/next-agent-bootstrap.md`
  - Updated continuation guidance.
- `docs/portfolio-one-pager.md`
  - Updated next valuable slice.
- `docs/portfolio-interview-guide.md`
  - Updated tradeoff and next steps.

## Side-Projects Hub

- `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md`
  - Updated auth/deploy status summary.
