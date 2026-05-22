# Decisions

- Add seeded metrics APIs instead of real query-log persistence in this slice.
- Keep Operations retrieval-only: no answer text, citation generation, eval execution, or OpenAI provider.
- Use deterministic timestamps and values so portfolio screenshots stay stable.
- Expose `retrieval_hit_rate` and `zero_result_rate` as seeded metrics while leaving real eval runner for a later phase.
- Wire Operations through the same `/api` Vite proxy and fallback fixture pattern used by other screens.
