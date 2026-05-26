# Goal

Add a real OIDC/JWT auth adapter behind `AuthContextProvider` while preserving the API-key-free demo and CI path.

## Scope

- Add `AUTH_CONTEXT_PROVIDER=oidc_jwt`.
- Validate Bearer JWT issuer, audience, signature, expiry, and required session claims.
- Support local/CI verification with an env-provided HS256 secret.
- Keep `demo` as the default provider.
- Keep `trusted_headers` available for protected gateway handoff.

