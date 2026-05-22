# Goal

Implement Phase 1C Knowledge Library API and live UI wiring without adding answer generation, OpenAI calls, eval, or dashboard expansion.

## Scope

- Add retrieval-core document list/detail API for demo and local testing.
- Expose chunk previews and permission metadata needed by the Knowledge Library screen.
- Keep fake embedding and in-memory repository as the default local path.
- Keep API key-free pytest and frontend verification working.

## Out of Scope

- OpenAI API integration
- Generated answers
- Eval engine
- Production admin dashboard
- Full PostgreSQL persistence switch
