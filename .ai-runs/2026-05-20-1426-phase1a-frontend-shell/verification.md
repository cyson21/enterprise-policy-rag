# Verification

## Commands

```bash
pytest tests/test_personas_api.py -q
node web/scripts/smoke.mjs
npm run smoke --prefix web
pytest -q
python3 -m compileall -q app
docker compose config -q
npm run build --prefix web
```

## Result

- `pytest tests/test_personas_api.py -q`: 2 passed.
- `node web/scripts/smoke.mjs`: passed.
- `npm run smoke --prefix web`: passed.
- `pytest -q`: 11 passed.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `npm run build --prefix web`: failed because frontend dependencies were not installed; `tsc` is not available in the current environment. Network install was not run.
