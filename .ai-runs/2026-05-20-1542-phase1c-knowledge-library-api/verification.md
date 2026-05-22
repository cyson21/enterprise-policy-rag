# Verification

## Red Checks

```bash
pytest tests/test_documents_api.py -q
pnpm web:smoke
```

- Backend test initially failed with `405` for `GET /documents` and `404` for document detail before the routes existed.
- Frontend smoke initially failed because `loadDocuments`, `loadDocumentDetail`, `Document detail`, and `embedding_dimensions` were not wired.

## Commands

```bash
pytest tests/test_documents_api.py -q
pnpm web:smoke
pnpm web:build
pytest -q
python3 -m compileall -q app
docker compose config -q
curl -s --max-time 5 'http://127.0.0.1:8000/documents?workspace_id=acme'
curl -s --max-time 5 'http://127.0.0.1:8000/documents/doc_2?workspace_id=acme'
curl -s --max-time 5 'http://127.0.0.1:8000/documents/doc_2?workspace_id=other' -w '\n%{http_code}\n'
curl -s --max-time 5 'http://127.0.0.1:5173/api/documents?workspace_id=acme'
curl -s --max-time 5 'http://127.0.0.1:5173/api/documents/doc_2?workspace_id=acme'
Browser smoke for Knowledge Library list, document detail, chunk preview, row selection, and console errors
```

## Result

- `pytest tests/test_documents_api.py -q`: 3 passed.
- `pytest -q`: 17 passed.
- `python3 -m compileall -q app`: passed.
- `docker compose config -q`: passed.
- `pnpm web:smoke`: passed.
- `pnpm web:build`: passed.
- Backend document list returned 4 ACME demo documents.
- Backend document detail for `doc_2` returned `Security Incident Manual` with `embedding_dimensions: 64`.
- Backend document detail with the wrong workspace returned `404`.
- Vite proxy returned the same document list/detail payloads through `/api/documents`.
- Browser smoke confirmed Knowledge Library list, detail panel, `embedding_dimensions 64`, row selection to Security Incident Manual, and zero console errors.
