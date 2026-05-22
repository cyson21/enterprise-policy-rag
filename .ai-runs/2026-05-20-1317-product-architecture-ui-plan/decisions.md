# Decisions

| Decision | Reason | Alternatives |
|---|---|---|
| Include frontend in the core portfolio scope | A portfolio project needs visible product workflows, not only API proof | Keep backend-only and rely on Swagger |
| Limit essential screens to four | Shows product value without turning the project into a large admin suite | Build many small admin pages |
| Use Search Console as the first screen | It demonstrates permission-aware RAG immediately | Start with a dashboard or landing page |
| Use persona selector before real auth | It proves permission behavior without blocking on SSO/OIDC | Implement full auth first |
| Implement vertical slices by screen | Keeps backend work tied to visible product value | Continue backend-only phases |
| Use references as patterns only | Avoid copying proprietary UI while borrowing proven enterprise SaaS structure | Clone a reference layout directly |
