# Goal

Add the first admin workflow slice: document update/delete, indexing status, and audit logs.

## Scope

- Keep the implementation behind the existing auth context boundary.
- Require admin role for admin endpoints.
- Support synchronous re-indexing for document replacement.
- Persist audit logs in the default in-memory path and PostgreSQL repository path.
- Keep local and CI verification API-key-free.

## Excluded

- Full admin dashboard UX.
- Async indexing workers.
- Background job queues.
- Real IdP/OIDC adapter.

