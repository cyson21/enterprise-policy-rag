# Agent Plan

1. Inspect the current provider boundary, runtime wiring, and documentation state.
2. Implement a small standard-library OpenAI Responses API transport behind `OpenAITransport`.
3. Preserve fake provider as the default and keep `LLM_PROVIDER=openai` behind `OPENAI_API_KEY`.
4. Add unit tests with mocked HTTP openers for payload, header, response parsing, and error handling.
5. Add portfolio/interview closeout documentation and update README/TODO/project tracking/bootstrap/runbook.
6. Run backend, frontend, compose, and package-manager verification.
7. Record changed files, decisions, and verification output.
