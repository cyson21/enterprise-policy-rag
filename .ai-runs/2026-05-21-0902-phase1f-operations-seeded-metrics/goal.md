# Goal

Turn Operations from static preview cards into a seeded metrics and recent-query screen without adding eval execution, answer generation, or OpenAI calls.

## Scope

- Add API key-free seeded metrics endpoints.
- Display usage, latency, cost estimate, retrieval hit, and zero-result rate.
- Display recent retrieval-only query rows.
- Keep data deterministic for portfolio/demo use.

## Out of Scope

- Query log persistence.
- Eval runner.
- Answer/citation generation.
- Production admin dashboard.
