# Goal

Add a fake-provider answer layer with citations and refusal behavior, without using OpenAI or any external AI API.

## Scope

- Keep retrieval permission filtering as the source of evidence.
- Add `LLMProvider` fake implementation behind the existing provider interface.
- Add answer API that returns answer text, citations, provider metadata, token estimate, cost estimate, latency estimate, and refusal reason.
- Connect Search Console to the answer API for portfolio-visible cited answers.

## Out of Scope

- OpenAI adapter.
- Real LLM calls.
- Eval runner.
- Docker/PostgreSQL round-trip.
- Production admin dashboard.
