# Decisions

- Use daily buckets for the first trend slice; hourly charts are unnecessary for demo data.
- Keep the endpoint under metrics as `GET /metrics/trend`.
- Aggregate directly from query logs so it works for both in-memory and PostgreSQL runtime modes.
- Display as a compact table in Operations to avoid adding a charting dependency.
