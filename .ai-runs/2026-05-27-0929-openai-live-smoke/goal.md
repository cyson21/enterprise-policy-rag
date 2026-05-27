# Goal

Add a controlled live OpenAI smoke path that is opt-in, safe by default, and documented separately from normal fake-provider verification.

## Scope

- Store the user-provided API key in ignored `.env.local`.
- Add `.env.local` to `.gitignore`.
- Add a live smoke script that only runs when `RUN_OPENAI_LIVE_SMOKE=1`.
- Keep all default tests and local checks on fake providers with no API key requirement.
- Record verification without exposing the API key.

