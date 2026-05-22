# Goal

## Objective

Implement Phase 1B: Search Console live retrieval vertical slice.

## Scope

In scope:

- Enrich retrieval API response with rank, visibility, department ids, and access reason.
- Add score threshold support.
- Add deterministic no-key demo documents for UI retrieval.
- Wire Search Console to live retrieval with persona-based refresh.
- Add frontend and backend smoke tests.

Out of scope:

- PostgreSQL persistence.
- Answer generation.
- Citation answer layer.
- Eval engine.
- OpenAI adapter.

## Exit Criteria

- `POST /retrieve` returns UI-ready retrieval result metadata.
- Security and finance personas return different results for the same query.
- Search Console calls live API and displays retrieved chunks/evidence.
- pnpm build/smoke and backend pytest pass.
