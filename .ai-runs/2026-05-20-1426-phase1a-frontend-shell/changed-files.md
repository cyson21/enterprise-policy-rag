# Changed Files

| File | Purpose |
|---|---|
| `app/personas.py` | Demo workspace and persona fixtures for no-key UI scenarios |
| `app/main.py` | Add `/workspaces/current` and `/personas` endpoints in FastAPI and fallback ASGI app |
| `tests/test_personas_api.py` | API tests for demo workspace and permission personas |
| `web/package.json` | Declare React/Vite frontend package and smoke/build scripts |
| `web/index.html` | Vite HTML entry |
| `web/vite.config.ts` | Vite React server config |
| `web/tsconfig.json` | TypeScript config for frontend source |
| `web/scripts/smoke.mjs` | No-install frontend shell static smoke |
| `web/src/app/App.tsx` | React app root and route/persona state |
| `web/src/app/routes.tsx` | Four required product routes |
| `web/src/api/client.ts` | Fixture-backed API client placeholder |
| `web/src/components/layout/AppShell.tsx` | Sidebar/top bar/page shell |
| `web/src/components/persona/PersonaSelector.tsx` | Persona selector |
| `web/src/fixtures/personas.ts` | Frontend workspace and persona demo data |
| `web/src/routes/search/SearchPage.tsx` | Search Console preview route |
| `web/src/routes/knowledge/KnowledgePage.tsx` | Knowledge Library preview route |
| `web/src/routes/retrieval-lab/RetrievalLabPage.tsx` | Retrieval Lab preview route |
| `web/src/routes/operations/OperationsPage.tsx` | Operations preview route |
| `web/src/styles/tokens.css` | Product shell styles and responsive layout |
| `README.md` | Current implementation and verification updates |
| `TODO.md` | Phase 1A status updates |
| `docs/project-tracking.md` | Current phase and verification snapshot updates |
