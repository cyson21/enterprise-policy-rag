# Changed Files

| File | Purpose |
|---|---|
| `app/models.py` | Add retrieval `score_threshold` and UI metadata fields |
| `app/retrieval.py` | Add rank, access reason, and score threshold filtering |
| `app/providers.py` | Expand fake embedding tokenizer for Korean demo queries |
| `app/demo_data.py` | Seed no-key demo documents |
| `app/main.py` | Add `seed_demo` app factory option |
| `tests/test_retrieval_metadata_api.py` | Cover metadata, threshold, and persona-specific demo retrieval |
| `tests/test_api_retrieval.py` | Keep existing API tests isolated from demo seed data |
| `tests/test_personas_api.py` | Keep persona API tests isolated from demo seed data |
| `web/vite.config.ts` | Add `/api` proxy to backend |
| `web/src/api/client.ts` | Add typed live retrieval client and fallback results |
| `web/src/fixtures/personas.ts` | Add API persona normalization |
| `web/src/app/App.tsx` | Pass workspace id into app shell |
| `web/src/components/layout/AppShell.tsx` | Pass active persona/workspace to page routes |
| `web/src/routes/search/SearchPage.tsx` | Wire live retrieval, persona refresh, result selection, and evidence panel |
| `web/src/styles/tokens.css` | Add retrieval metadata, empty state, and evidence panel styles |
| `web/scripts/smoke.mjs` | Check live retrieval wiring markers |
| `README.md` | Update current implementation and next step |
| `TODO.md` | Mark Search Console and demo data complete |
| `docs/project-tracking.md` | Add Phase 1B verification snapshot |
| `docs/next-agent-bootstrap.md` | Update next-agent continuation scope |
