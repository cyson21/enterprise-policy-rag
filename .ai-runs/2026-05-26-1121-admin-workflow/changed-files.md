# Changed Files

## Backend

- `app/models.py`
  - Added `IndexingStatus`, `DocumentUpdate`, admin response, and audit log models.
- `app/repository.py`
  - Added document update/delete and admin audit log methods to repository boundary.
  - Implemented in-memory and PostgreSQL paths.
- `app/services.py`
  - Added admin document replacement, deletion, and audit log listing service methods.
- `app/main.py`
  - Added `PATCH /admin/documents/{document_id}`.
  - Added `DELETE /admin/documents/{document_id}`.
  - Added `GET /admin/audit-logs`.
  - Enforced admin role through the existing auth context boundary.
- `infra/postgres/init/001_schema.sql`
  - Added `documents.indexing_status`.
  - Added `admin_audit_logs` table and indexes.

## Tests

- `tests/test_admin_workflow.py`
  - Added admin update/delete/audit/non-admin rejection API coverage.
- `tests/test_postgres_repository.py`
  - Added PostgreSQL repository coverage for update/delete/audit methods.
- `tests/test_documents_api.py`
  - Updated document summary expectation for `indexing_status`.

## Frontend

- `web/src/api/client.ts`
  - Added `indexing_status` to document summaries and static fixtures.
- `web/src/routes/knowledge/KnowledgePage.tsx`
  - Added indexing status to Knowledge Library table and detail panel.
- `web/src/utils/display.ts`
  - Added indexing status label formatting.
- `web/src/styles/tokens.css`
  - Adjusted Knowledge Library table columns.
- `web/scripts/smoke.mjs`
  - Added indexing status smoke label.

## Docs

- `README.md`
- `TODO.md`
- `docs/api-data-model.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`
- `docs/portfolio-one-pager.md`
- `docs/portfolio-interview-guide.md`

## Side-Projects Hub

- `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag/README.md`
  - Updated admin workflow status.
