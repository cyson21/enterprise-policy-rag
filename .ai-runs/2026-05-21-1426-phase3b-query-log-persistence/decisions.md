# Decisions

- Treat query logging as an application service boundary, not a UI-only fixture.
- Store both retrieval and answer calls with a `mode` field so Operations can distinguish Search Console answer calls from Retrieval Lab retrieval-only calls.
- Compute summary metrics from stored logs:
  - `searches`: total query log rows for the workspace
  - `p95_latency_ms`: nearest-rank p95 from recorded latency values
  - `retrieval_hit_rate`: share of rows with at least one retrieved/cited result
  - `zero_result_rate`: share of rows with no result
  - `estimated_cost_usd`: sum of recorded cost estimates
- Keep demo rows as seed data for portfolio presentation, but make API tests use `seed_demo=False` to prove runtime logging works without fixtures.
- Add PostgreSQL schema support now, while leaving low-resource Docker integration optional for this slice.
