# Changed Files

- `app/auth.py`: added `OIDCJWTAuthContextProvider`, Bearer token extraction, JWT validation, claim mapping, and env-based provider selection.
- `tests/test_auth_context.py`: added OIDC JWT happy-path, session-bound retrieval, missing token, and invalid signature tests.
- `pyproject.toml`: added `PyJWT[crypto]` runtime dependency for JWT/JWKS verification.
- `docs/internal/design/2026-05-26-production-auth-sso-design.md`: updated auth design with `oidc_jwt` provider and env settings.
- `docs/api-data-model.md`: documented OIDC provider selection, env vars, and `auth_mode`.
- `README.md`: updated current implementation, tests, and local OIDC run example.
- `TODO.md`: marked Real IdP/OIDC adapter complete.
- `docs/project-tracking.md`: recorded Phase 5D OIDC JWT adapter snapshot.
- `docs/next-agent-bootstrap.md`: added this run and moved next priority to controlled live OpenAI smoke.
- `docs/runbooks/local-demo.md`: added optional OIDC JWT check and updated expected test count.
- `docs/portfolio-one-pager.md`: updated auth capability and next-slice text.
- `docs/portfolio-interview-guide.md`: updated architecture/tradeoff notes and next steps.
- `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md`: updated side-project hub summary outside this git repo.
