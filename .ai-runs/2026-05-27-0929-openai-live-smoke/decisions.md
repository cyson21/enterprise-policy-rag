# Decisions

- Live OpenAI verification is explicitly opt-in through `RUN_OPENAI_LIVE_SMOKE=1`.
- `.env.local` is ignored and used only for local secret loading.
- The smoke path uses in-memory repositories and seeded demo data to avoid Docker/PostgreSQL cost.
- The smoke output reports only safe metadata, not the API key or full model response.
- Normal pytest/frontend/build verification continues to require no API key.

