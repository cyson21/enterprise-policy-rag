# Decisions

- Keep `demo` as the default auth mode so local development, CI, and the static demo still require no credentials.
- Add OIDC/JWT as an explicit opt-in provider via `AUTH_CONTEXT_PROVIDER=oidc_jwt`.
- Use HS256 secret support for deterministic local/CI tests and env-driven JWT validation.
- Do not add OAuth authorization code flow, browser redirects, session cookies, or user provisioning in this slice.

