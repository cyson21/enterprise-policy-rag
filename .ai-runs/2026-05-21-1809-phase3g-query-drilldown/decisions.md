# Decisions

- Use `GET /queries/{query_id}` with a required `workspace_id` query parameter.
- Return `404` when the query id is missing or belongs to another workspace.
- Store enough in-memory retrieval and citation snapshot fields to match the PostgreSQL-backed response shape.
- Keep the UI as a compact Operations detail panel instead of adding a new route.
