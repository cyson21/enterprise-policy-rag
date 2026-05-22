# Verification

## Red Checks

```bash
node scripts/run-web-task.mjs smoke
```

- Initially failed because `runLabRetrieval`, `Lab query`, and `thresholdControl` markers were missing.

## Commands

```bash
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
pytest -q
python3 -m compileall -q app
docker compose config -q
node scripts/check-package-manager.mjs
curl -s --max-time 5 -X POST 'http://127.0.0.1:8000/retrieve' -H 'Content-Type: application/json' -d '{"workspace_id":"acme","user_id":"mina-security","department_ids":["security"],"query":"security incident evidence","top_k":1,"score_threshold":0}'
curl -s --max-time 5 -X POST 'http://127.0.0.1:5173/api/retrieve' -H 'Content-Type: application/json' -d '{"workspace_id":"acme","user_id":"mina-security","department_ids":["security"],"query":"security incident evidence","top_k":1,"score_threshold":0.95}'
Browser smoke for Retrieval Lab screen, debug panel, top-k clamp, and console errors
```

## Result

- `node scripts/run-web-task.mjs smoke`: passed.
- `node scripts/run-web-task.mjs build`: passed.
- `pytest -q`: 21 passed, 1 skipped.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `node scripts/check-package-manager.mjs`: passed.
- Backend retrieval with `top_k=1` returned one `Security Incident Manual` result.
- Vite proxy retrieval with `score_threshold=0.95` returned an empty result list.
- Browser smoke confirmed Retrieval Lab live result rendering, debug panel, top-k clamp from out-of-range input to `10`, and zero console errors.
