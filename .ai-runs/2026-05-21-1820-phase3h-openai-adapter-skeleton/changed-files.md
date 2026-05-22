# Changed Files

## Backend

- `app/providers.py`
  - Added `OpenAITransport` protocol.
  - Added `OpenAILLMProvider` skeleton.
  - Added `build_llm_provider_from_env`.
- `app/runtime.py`
  - Injects fake or OpenAI LLM provider based on `LLM_PROVIDER`.

## Tests

- `tests/test_provider_selection.py`
  - Added provider selection tests.
  - Added OpenAI payload/transport tests without network calls.
  - Added runtime selection tests.

## Docs

- `README.md`
- `TODO.md`
- `docs/project-tracking.md`
- `docs/next-agent-bootstrap.md`
- `docs/api-data-model.md`
- `docs/runbooks/local-demo.md`
- `docs/portfolio-one-pager.md`
