# Goal

Add an OpenAI adapter skeleton behind provider interfaces without changing the default fake-provider verification path.

## Scope

- Add provider selection helpers for `LLM_PROVIDER`.
- Keep default runtime on `FakeLLMProvider`.
- Add OpenAI adapter request payload construction that can be unit-tested without network access.
- Require explicit API key only when `LLM_PROVIDER=openai` is selected.
- Do not add live OpenAI API calls to CI or local default tests.
