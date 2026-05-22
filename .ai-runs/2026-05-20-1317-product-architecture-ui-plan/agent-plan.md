# Agent Plan

## Context

- The first retrieval core slice was already implemented.
- The user clarified that a portfolio project needs visible frontend screens.
- The next step is to establish a stronger full-picture plan before adding more implementation.

## Steps

- [x] Review product references for enterprise search, RAG knowledge management, retrieval testing, and insights.
- [x] Define the minimum screen set that can demonstrate the product without overbuilding.
- [x] Define backend/frontend/data/provider architecture and boundaries.
- [x] Define implementation phases that include UI from the start.
- [x] Update project docs so future work follows the architecture-first direction.

## Files Expected to Change

- `.ai-runs/2026-05-20-1317-product-architecture-ui-plan/*`
- `docs/internal/design/2026-05-20-enterprise-policy-rag-product-architecture.md`
- `README.md`
- `TODO.md`
- `docs/project-tracking.md`

## Risks

- UI scope can grow too quickly. Keep the first frontend to 4 primary screens.
- Reference-inspired design must not copy proprietary product screens verbatim.
- Backend implementation already exists; future work should align it to this architecture rather than expanding ad hoc.
