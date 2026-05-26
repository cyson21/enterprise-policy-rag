# Decisions

- `AUTH_CONTEXT_PROVIDER=demo` remains the default so tests, local runs, and public demos work without credentials.
- `trusted_headers` mode is an adapter boundary for a future identity-aware proxy or SSO gateway. It is not a standalone security mechanism.
- Existing persona-driven endpoints stay available for the demo and eval tooling.
- Session-bound endpoints ignore any malicious `user_id` or `department_ids` fields in the request body.
- No new runtime dependencies are added.

