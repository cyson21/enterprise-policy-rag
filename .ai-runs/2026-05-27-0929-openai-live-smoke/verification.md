# Verification

## Secret Handling

- Added `.env.local` to `.gitignore`.
- Stored `OPENAI_API_KEY` in `.env.local` with mode `0600`.
- Verified `.env.local` is ignored:
  - `git check-ignore -v .env.local`
  - Result: `.gitignore:7:.env.local .env.local`.

## RED

- `pytest tests/test_openai_live_smoke.py -q`
  - Result: failed as expected before implementation.
  - Output: import error because `scripts/openai_live_smoke.py` did not exist.

## GREEN

- `pytest tests/test_openai_live_smoke.py -q`
  - Result: passed.
  - Output: `3 passed in 0.17s`.
- `python3 scripts/openai_live_smoke.py`
  - Result: passed skip mode.
  - Output: `skipped: set RUN_OPENAI_LIVE_SMOKE=1 to run the controlled OpenAI live smoke`.
- `RUN_OPENAI_LIVE_SMOKE=1 python3 scripts/openai_live_smoke.py`
  - Result: passed live OpenAI smoke.
  - Output: `OpenAI live smoke passed: provider=openai model=gpt-4.1-mini retrieved=2 citations=2 latency_ms=3563 answer_chars=151`.

## Final Checks

- `pytest -q`
  - Result: passed.
  - Output: `76 passed, 2 skipped in 1.43s`.
- `python3 -m compileall -q app scripts/openai_live_smoke.py`
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
  - Output: static Vite build completed.
- `pnpm web:smoke:static`
  - Result: passed.
  - Output: `static demo smoke passed`.
- `git diff --check`
  - Result: passed.
- `git diff -- . ':(exclude).env.local' | rg -n 'sk-proj-8ep|OPENAI_API_KEY=.*sk-' || true`
  - Result: passed, no secret value in tracked diff.

## Pending After Commit

- Push and Vercel deployment check.
