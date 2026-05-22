# Goal

Close the post-screenshot implementation gaps that can be completed without requiring a user decision.

## Scope

- Keep the default app and CI path API-key-free.
- Convert the existing OpenAI provider skeleton into an explicit opt-in live transport path.
- Add deterministic tests around the live transport without making external API calls.
- Tighten portfolio/demo documentation so the current state, remaining boundaries, and next step are clear.
- Record verification results in this run ledger.

## Out of Scope

- Running a real OpenAI request without an API key from the user.
- Deploying a public hosted demo.
- Adding production auth/SSO, billing, Kubernetes, or on-premise deployment.
