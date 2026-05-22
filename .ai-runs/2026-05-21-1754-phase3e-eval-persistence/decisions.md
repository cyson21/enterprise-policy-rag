# Decisions

- Keep eval persistence separate from query log persistence because eval runs are quality-control records, not user query activity.
- Preserve demo UX by making `GET /eval-runs` lazily create a fake `golden-demo` run when no run exists yet.
- Store per-case expected, retrieved, and cited document ids as arrays in PostgreSQL.
- Keep the first eval persistence slice limited to fake-provider results.
