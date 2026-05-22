# Verification

## Commands

```bash
pytest tests/test_retrieval_metadata_api.py -q
pnpm web:smoke
pnpm web:build
pytest -q
python3 -m compileall -q app
docker compose config -q
curl -s --max-time 5 http://127.0.0.1:8000/health
curl -s --max-time 5 -X POST http://127.0.0.1:8000/retrieve -H 'Content-Type: application/json' -d '{"workspace_id":"acme","user_id":"mina-security","department_ids":["security"],"query":"보안 사고 발생 시 누구에게 알려야 해?","top_k":5,"score_threshold":0}'
curl -s --max-time 5 -X POST http://127.0.0.1:5173/api/retrieve -H 'Content-Type: application/json' -d '{"workspace_id":"acme","user_id":"joon-finance","department_ids":["finance"],"query":"보안 사고 발생 시 누구에게 알려야 해?","top_k":5,"score_threshold":0}'
Browser DOM smoke for `Security Incident Manual`, `access_reason`, and finance persona refresh
```

## Result

- `pytest tests/test_retrieval_metadata_api.py -q`: 3 passed.
- `pnpm web:smoke`: passed.
- `pnpm web:build`: passed.
- `pytest -q`: 14 passed.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- Backend `/health`: `{"status":"ok"}`.
- Backend security retrieval returned `Security Incident Manual`.
- Vite `/api/retrieve` finance persona excluded `Security Incident Manual` and returned only public remote access content for that query.
- Browser DOM smoke found `Search Console`, `Security Incident Manual`, `access_reason`, `score_threshold 0`; after switching to `joon-finance`, `Security Incident Manual` count became 0.
