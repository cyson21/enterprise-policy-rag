# Decisions

| Decision | Reason | Alternatives |
|---|---|---|
| Use Vite `/api` proxy for browser dev | Avoid CORS setup while keeping frontend fetch paths stable | Add backend CORS immediately |
| Keep demo seed in `create_app(seed_demo=True)` and disable it in tests | Browser/demo needs data, API tests need isolation | Hard-code UI-only fixtures |
| Add access reason as `owner`, `public`, `department_match` | Matches the first permission model and UI badges | Return only booleans |
| Extend fake embedding tokenizer for Korean | Demo queries are Korean-first and must retrieve matching Korean chunks | Keep English-only demo content |
| Keep Search Console retrieval-only | Phase 1B excludes answer generation | Add fake answer panel now |
