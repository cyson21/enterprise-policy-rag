# Production Hardening Checklist

Date: 2026-05-28

## Goal

This checklist closes the portfolio scope for Project 02 and records what must be added before turning Enterprise Policy RAG into a real production SaaS service.

The current public deployment is a static read-only demo. It intentionally does not run the FastAPI backend, PostgreSQL, OpenAI live calls, or production user sessions.

## Current Closure Status

| Area | Status | Evidence |
|---|---|---|
| Portfolio demo | Complete | `https://enterprise-policy-rag.vercel.app` static read-only build |
| Default local verification | Complete | fake providers, in-memory repositories, no API key required |
| Retrieval permissions | Complete | workspace, owner, department, visibility tests |
| Citation and refusal behavior | Complete | fake LLM answer API and tests |
| Operations observability | Complete | query log metrics, trend, detail, evidence, eval history |
| Admin workflow boundary | Complete | admin role update/delete/audit log API and UI controls |
| OIDC JWT boundary | Complete | opt-in issuer/audience/signature/expiry validation |
| OpenAI live path | Complete as opt-in smoke | `RUN_OPENAI_LIVE_SMOKE=1`, ignored `.env.local`, safe metadata output |
| Public production SaaS readiness | Not claimed | use the checklist below before a real customer-facing backend rollout |

## Required Before Real Production

| Control | Required Action | Current Project State |
|---|---|---|
| Secret rotation | Rotate any OpenAI key that was pasted into chat or shell history; keep only platform-managed secrets in deployment environments. | `.env.local` is ignored and tests do not require a key. |
| Environment matrix | Define `development`, `preview`, `production` env variables for auth, DB, provider, CORS, rate limits, and logging. | Vercel static demo uses no backend env. |
| Request size limit | Add body-size limits for document ingestion and admin update endpoints. | Not implemented; document payloads are prototype-sized. |
| Rate limiting | Add per-user/workspace and admin endpoint rate limits, preferably backed by Redis or gateway middleware. | Not implemented in app process. |
| CORS and trusted origins | Lock API CORS to known frontend origins and internal tooling domains. | Public demo is static; API CORS policy is not production-tuned. |
| Security headers | Add API/web headers for content type, frame, referrer, and permissions policies at the hosting edge or app middleware. | Static hosting headers are not customized. |
| Auth session model | Replace demo persona selector with real session cookies/OIDC redirect flow and role mapping. | OIDC JWT provider boundary exists; redirect/cookie flow is excluded. |
| Admin audit retention | Define audit log retention, export, and tamper-evidence policy. | Append-only audit rows exist for prototype flows. |
| Data retention | Define document/chunk/query/citation retention and deletion behavior by workspace. | Repository supports delete, but no lifecycle policy exists. |
| Migration workflow | Add Alembic or equivalent migration lifecycle for schema changes. | Schema is tracked as idempotent init SQL. |
| Backups and restore | Add PostgreSQL backup, restore rehearsal, and pgvector index recovery steps. | Docker compose is local only. |
| Observability | Add structured JSON logs, request ids, metrics export, alerting, and error reporting. | Query metrics exist; platform observability is not wired. |
| Cost controls | Add model allowlist, token caps, daily workspace budgets, and fail-closed behavior. | OpenAI live smoke is manually gated. |
| Evaluation gate | Run golden set eval on provider/config changes before promotion. | Fake-provider eval runner exists. |
| Abuse and prompt safety | Add content policy checks, system prompt review, and injection-resistant citation handling. | Retrieval/citation flow is deterministic prototype logic. |
| Deployment rollback | Document Vercel promotion/rollback and database rollback steps. | Static demo deployment is verified through Vercel Git integration. |
| Load testing | Add representative ingestion/search/answer load tests and latency budgets. | Unit/API tests cover correctness, not load. |
| Compliance review | Review PII, access logs, retention, and enterprise policy document handling. | Not part of portfolio scope. |

## Portfolio Closeout Criteria

- Public demo is available and does not require secrets.
- README, one-pager, interview guide, screenshots, architecture diagram, and runbooks are current.
- Default tests pass without Docker or external AI calls.
- OpenAI live path is opt-in only and never part of default CI.
- Production hardening gaps are explicit and not implied as already solved.

## Verification Commands

Use these for final project closeout:

```bash
pnpm check:package-manager
pnpm web:build:static
pnpm web:smoke:static
pnpm web:smoke
python3 -m compileall -q app scripts/openai_live_smoke.py
pytest -q
git diff --check
```

Use these for public demo deployment checks:

```bash
pnpm dlx vercel ls enterprise-policy-rag --scope cyson21s-projects
curl -I -L https://enterprise-policy-rag.vercel.app
```

## Decision

Project 02 is complete as a portfolio-grade backend/RAG demo. A real production SaaS rollout should start as a separate project phase from this checklist rather than being treated as remaining portfolio work.
