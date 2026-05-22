# Decisions

- Use a deterministic `golden-demo` dataset with three permission-aware cases.
- Run eval through `PolicyRagServices.answer()` so retrieval permission filtering and answer citations are tested together.
- Keep eval history non-persistent until PostgreSQL is running.
- Use fake-provider metrics only; no external LLM judge.
- Show eval results in Operations to make quality checks visible in the portfolio UI.
