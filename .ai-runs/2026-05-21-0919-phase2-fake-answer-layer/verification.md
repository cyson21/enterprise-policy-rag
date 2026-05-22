# Verification

## Red Checks

```bash
pytest tests/test_answer_api.py -q
node scripts/run-web-task.mjs smoke
```

- API tests initially failed with `404` for `/answer`.
- Frontend smoke initially failed because `loadAnswer`, `Cited Answer`, and `refusal_reason` were not wired.

## Commands

```bash
pytest tests/test_answer_api.py -q
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
curl -s --max-time 5 -X POST 'http://127.0.0.1:8000/answer' -H 'Content-Type: application/json' -d '{"workspace_id":"acme","user_id":"mina-security","department_ids":["security"],"query":"security incident evidence","top_k":3,"score_threshold":0}'
curl -s --max-time 5 -X POST 'http://127.0.0.1:5173/api/answer' -H 'Content-Type: application/json' -d '{"workspace_id":"acme","user_id":"hana-people","department_ids":["people"],"query":"nonexistent policy phrase","top_k":5,"score_threshold":0.95}'
pytest -q
python3 -m compileall -q app
docker compose config -q
node scripts/check-package-manager.mjs
Browser smoke for Search Console cited answer panel and console errors
```

## Result

- `pytest tests/test_answer_api.py -q`: 3 passed.
- `node scripts/run-web-task.mjs smoke`: passed.
- `node scripts/run-web-task.mjs build`: passed.
- `/answer` security persona returned fake answer with `Security Incident Manual` citation.
- `/api/answer` no-evidence case returned `refusal_reason=insufficient_evidence`.
- `pytest -q`: 26 passed, 1 skipped.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `node scripts/check-package-manager.mjs`: passed.
- Browser smoke confirmed Search Console cited answer panel and zero console errors.
