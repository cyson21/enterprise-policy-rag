# Verification

## Red Checks

```bash
pytest tests/test_operations_api.py -q
node scripts/run-web-task.mjs smoke
```

- API tests initially failed with `404` for `/metrics/summary` and `/queries/recent`.
- Frontend smoke initially failed because `loadOperationsSummary`, `retrieval_hit_rate`, and `Recent Queries` were not wired.

## Commands

```bash
pytest tests/test_operations_api.py -q
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
curl -s --max-time 5 'http://127.0.0.1:8000/metrics/summary?workspace_id=acme'
curl -s --max-time 5 'http://127.0.0.1:5173/api/queries/recent?workspace_id=acme'
pytest -q
python3 -m compileall -q app
docker compose config -q
node scripts/check-package-manager.mjs
Browser smoke for Operations metrics, recent query rows, and console errors
```

## Result

- `pytest tests/test_operations_api.py -q`: 2 passed.
- `node scripts/run-web-task.mjs smoke`: passed.
- `node scripts/run-web-task.mjs build`: passed.
- `/metrics/summary?workspace_id=acme`: returned seeded searches `128`, p95 latency `184`, retrieval hit `0.92`.
- `/api/queries/recent?workspace_id=acme`: returned three retrieval-only rows.
- `pytest -q`: 23 passed, 1 skipped.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `node scripts/check-package-manager.mjs`: passed.
- Browser smoke confirmed Operations metrics, recent query rows, and zero console errors.
