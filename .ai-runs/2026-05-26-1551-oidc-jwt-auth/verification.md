# Verification

## RED

- `pytest tests/test_auth_context.py -q`
  - Result: failed as expected before implementation.
  - Output: 4 OIDC tests failed because `AUTH_CONTEXT_PROVIDER=oidc_jwt` was unsupported.

## GREEN

- `pytest tests/test_auth_context.py -q`
  - Result: passed.
  - Output: `9 passed in 0.28s`.
- `pytest -q`
  - Result: passed.
  - Output: `73 passed, 2 skipped in 0.46s`.
- `python3 -m compileall -q app`
  - Result: passed.
- `docker compose config -q`
  - Result: passed.
- `docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q`
  - Result: passed.
- `pnpm web:smoke`
  - Result: passed.
  - Output: `frontend shell smoke passed`.
- `pnpm web:build`
  - Result: passed.
  - Output: Vite production build completed.
- `pnpm web:build:static`
  - Result: passed.
  - Output: static Vite build completed with `VITE_DEMO_MODE=static`.
- `pnpm web:smoke:static`
  - Result: passed.
  - Output: `static demo smoke passed`.

## Final Checks

- `git diff --check`
  - Result: passed.

## Pending After Commit

- Push and Vercel deployment check.
