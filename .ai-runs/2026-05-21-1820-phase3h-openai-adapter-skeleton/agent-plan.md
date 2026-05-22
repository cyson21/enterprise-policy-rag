# Agent Plan

1. Add RED tests for default fake LLM provider selection and explicit OpenAI provider selection.
2. Add RED tests for OpenAI adapter payload construction without making network calls.
3. Implement `OpenAILLMProvider` skeleton and `build_llm_provider_from_env`.
4. Wire runtime service creation to use the provider helper.
5. Verify answer API still works without API keys.
6. Run Python/frontend/compose checks.
7. Update README, TODO, project tracking, API/data-model, runbook, one-pager, bootstrap, and this run ledger.
