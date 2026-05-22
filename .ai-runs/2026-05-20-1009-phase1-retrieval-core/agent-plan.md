# Phase 1 Retrieval Core Implementation Plan

## Context

- Project 02 is `Enterprise Policy RAG`.
- First implementation slice is limited to retrieval core.
- API key, OpenAI adapter, answer generation, eval, admin dashboard, and on-premise deployment are excluded.
- Runtime dependencies should be declared, but local tests must not require an API key or external AI call.

## Steps

- [x] Add project scaffolding: Python package, dependency metadata, ignore file, and Docker Compose.
- [x] Add PostgreSQL/pgvector SQL schema for workspaces, documents, chunks, and indexes.
- [x] Write failing pytest coverage for chunking, fake embeddings, retrieval permission filtering, and API retrieval flow.
- [x] Implement deterministic chunking and provider interfaces.
- [x] Implement in-memory repository and retrieval service for local/API tests.
- [x] Implement FastAPI app skeleton with document registration and retrieval-only endpoints.
- [x] Run pytest and record the verification result.
- [x] Update README, TODO, project tracking, changed-files, decisions, and verification records.

## Files Expected to Change

- `.ai-runs/2026-05-20-1009-phase1-retrieval-core/*`
- `.gitignore`
- `pyproject.toml`
- `docker-compose.yml`
- `infra/postgres/init/001_schema.sql`
- `app/**`
- `tests/**`
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`

## Risks

- FastAPI is not installed in the current global Python environment, so project dependency metadata must be explicit.
- Local verification should avoid network installation and external AI services.
- The first slice must not drift into answer generation or OpenAI wiring.
