# Decisions

- Admin APIs are session-bound and require `role=admin`.
- Document update is a synchronous replacement flow that regenerates chunks and embeddings.
- `indexing_status` is stored on documents and is `ready` after synchronous update completion.
- Audit log entries are append-only and record actor, action, document id, and detail metadata.
- Existing public/demo persona flows remain unchanged.

