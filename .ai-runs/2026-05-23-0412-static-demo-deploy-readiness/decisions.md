# Decisions

- Use a static read-only demo as the first public demo path because it avoids API keys, Docker, database hosting, and secret management.
- Keep the live local app path unchanged; the static demo mode is selected only by `VITE_DEMO_MODE=static`.
- Do not trigger real OpenAI calls or public backend hosting in this slice.
- Prefer build-time environment selection over URL-only flags so deployed assets are deterministic and do not generate `/api` network noise.
