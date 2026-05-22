# Decisions

- `LLM_PROVIDER` defaults to `fake`.
- `LLM_PROVIDER=openai` requires `OPENAI_API_KEY`, but no default test uses it.
- The adapter skeleton exposes payload construction for deterministic tests.
- Live external calls remain outside this slice.
