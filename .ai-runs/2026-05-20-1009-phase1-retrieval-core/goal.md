# Goal

## Objective

Implement the first Phase 1 retrieval core slice for Enterprise Policy RAG.

## Scope

In scope:

- FastAPI application skeleton with a health endpoint.
- PostgreSQL + pgvector Docker Compose and SQL schema for documents/chunks.
- Deterministic fake embedding provider behind an `EmbeddingProvider` interface.
- Markdown/TXT document registration with chunk creation.
- Retrieval-only API that returns accessible chunks, not generated answers.
- Permission filter tests for workspace, owner, department, and public visibility.
- Run-local validation without OpenAI API keys.

Out of scope:

- OpenAI API adapter.
- LLM answer generation.
- Citation answer layer.
- Eval runner or golden question set.
- Admin dashboard.
- On-premise deployment.

## Exit Criteria

- `.ai-runs/2026-05-20-1009-phase1-retrieval-core/agent-plan.md` records the implementation plan before code changes.
- Tests prove deterministic fake embeddings and permission-aware retrieval.
- API-level tests cover document ingestion and retrieval-only behavior without API keys.
- README, TODO, and project tracking reflect the implemented Phase 1 slice.
