# Decisions

- Implement only fake-provider answer generation; do not add OpenAI adapter or external AI calls.
- Build answer citations from `RetrievalService` results so workspace/user/department/visibility filtering is reused exactly.
- Return `refusal_reason=insufficient_evidence` when retrieval returns no citation candidates.
- Include token, latency, provider, and estimated cost metadata in the response, but leave persistence for the later query log slice.
- Keep Search Console answer UI next to the evidence panel so portfolio viewers can see both answer and supporting chunks.
