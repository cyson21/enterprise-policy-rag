# Goal

Add runtime repository selection so the app can use PostgreSQL-backed document and query log repositories when `DATABASE_URL` is set, while preserving the current in-memory fake-provider default when no database URL is configured.

Boundaries:

- Keep fake embedding and fake LLM providers as the default.
- Do not add OpenAI API calls.
- Do not add production auth/SSO or an admin dashboard.
- Keep Docker optional for normal tests.
