# Goal

Add a production auth/SSO boundary without changing the fake-provider-first default path.

## Scope

- Document the intended production auth/SSO architecture.
- Add a minimal, testable backend auth context provider boundary.
- Keep local and CI verification API-key-free.
- Keep the public demo static and safe.
- Do not add a real IdP, JWT verifier, paid auth service, or production secrets.

