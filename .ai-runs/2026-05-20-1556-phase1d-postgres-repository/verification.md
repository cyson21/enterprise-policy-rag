# Verification

## Red Checks

```bash
pytest tests/test_postgres_repository.py -q
```

- Initially failed because `PostgresPolicyRepository` did not exist.

## Commands

```bash
pytest tests/test_postgres_repository.py -q
pytest -q
python3 -m compileall -q app
docker compose config -q
node scripts/check-package-manager.mjs
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
/opt/homebrew/Cellar/node/24.10.0/bin/corepack pnpm web:smoke
/opt/homebrew/Cellar/node/24.10.0/bin/corepack pnpm web:build
docker info --format '{{.ServerVersion}}'
```

## Result

- `pytest tests/test_postgres_repository.py -q`: 4 passed.
- `pytest -q`: 21 passed, 1 skipped.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `node scripts/check-package-manager.mjs`: passed.
- `node scripts/run-web-task.mjs smoke`: passed.
- `node scripts/run-web-task.mjs build`: passed.
- `corepack pnpm web:smoke`: passed after root scripts stopped calling nested `pnpm`.
- `corepack pnpm web:build`: passed after root scripts stopped calling nested `pnpm`.
- `docker info`: Docker daemon is not running in the current local environment, so `RUN_POSTGRES_TESTS=1` PostgreSQL round-trip was not executed.
