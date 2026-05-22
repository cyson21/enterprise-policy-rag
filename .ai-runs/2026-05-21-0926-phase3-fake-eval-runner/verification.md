# Verification

## Red Checks

```bash
pytest tests/test_eval_api.py -q
node scripts/run-web-task.mjs smoke
```

- API tests initially failed with `404` for `/eval-runs`.
- Frontend smoke initially failed because `loadEvalRuns`, `citation_coverage`, and `Eval Report` were not wired.

## Commands

```bash
pytest tests/test_eval_api.py -q
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
curl -s --max-time 5 -X POST 'http://127.0.0.1:8000/eval-runs' -H 'Content-Type: application/json' -d '{"workspace_id":"acme","dataset_id":"golden-demo"}'
curl -s --max-time 5 'http://127.0.0.1:5173/api/eval-runs?workspace_id=acme'
pytest -q
python3 -m compileall -q app
docker compose config -q
node scripts/check-package-manager.mjs
Browser smoke for Operations eval report table and console errors
```

## Result

- `pytest tests/test_eval_api.py -q`: 2 passed.
- `node scripts/run-web-task.mjs smoke`: passed.
- `node scripts/run-web-task.mjs build`: passed.
- `POST /eval-runs`: returned `golden-demo` with 3 cases, retrieval hit `1.0`, citation coverage `1.0`.
- `GET /api/eval-runs`: returned the latest fake eval run.
- `pytest -q`: 28 passed, 1 skipped.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `node scripts/check-package-manager.mjs`: passed.
- Browser smoke confirmed Operations eval report table and zero console errors.
