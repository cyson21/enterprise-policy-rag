# Agent Plan

## Architecture

- Extend document models with `indexing_status`.
- Add admin document update and delete request/response models.
- Extend `PolicyRepository` with document replacement, deletion, and admin audit log methods.
- Add `PATCH /admin/documents/{document_id}`, `DELETE /admin/documents/{document_id}`, and `GET /admin/audit-logs`.
- Reuse `AuthContextProvider` and reject non-admin sessions with 403.
- Keep indexing synchronous for this slice: replacement chunks are embedded immediately and the final stored status is `ready`.

## Steps

1. Write failing API tests for admin update, delete, audit log listing, and non-admin rejection.
2. Add models and repository methods for update/delete/audit.
3. Wire service methods and FastAPI/Starlette routes.
4. Update PostgreSQL schema idempotently.
5. Update docs/TODO/project tracking.
6. Run targeted tests, full pytest, frontend smoke/build/static smoke, and git checks.
7. Commit, push, and verify Vercel Git deployment.

