# Local Demo Runbook

Date: 2026-05-21

## Goal

Run the current Enterprise Policy RAG demo without OpenAI API keys. Docker is optional for schema inspection and PostgreSQL integration checks, but the main demo works with the in-memory repository and fake providers.

`LLM_PROVIDER` defaults to `fake`. `LLM_PROVIDER=openai` uses the OpenAI Responses API transport only when `OPENAI_API_KEY` is provided; live OpenAI calls are opt-in and not part of the default demo path.

`AUTH_CONTEXT_PROVIDER` defaults to `demo`. `AUTH_CONTEXT_PROVIDER=oidc_jwt` validates a Bearer JWT only when issuer, audience, and signing configuration are explicitly provided.

## Prerequisites

- Python 3.11+
- Node.js with the checked-in frontend dependencies installed
- Docker daemon only when running PostgreSQL integration checks. Colima is the recommended low-resource path on local macOS.

## Backend

Install development dependencies if the local Python environment does not already have them.

```bash
python3 -m pip install -e ".[dev]"
```

Run the API.

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Smoke checks:

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/personas
curl -s -X POST http://127.0.0.1:8000/retrieve \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":"acme","user_id":"mina-security","department_ids":["security"],"query":"security incident evidence","top_k":3,"score_threshold":0}'
curl -s -X POST http://127.0.0.1:8000/answer \
  -H 'Content-Type: application/json' \
  -d '{"workspace_id":"acme","user_id":"mina-security","department_ids":["security"],"query":"security incident evidence","top_k":3,"score_threshold":0}'
```

## Frontend

The root scripts call local frontend tooling directly so they do not depend on `pnpm` being available inside nested scripts.

```bash
node scripts/run-web-task.mjs dev
```

Open:

```text
http://127.0.0.1:5173/
```

Screens to verify:

- 검색 콘솔: 근거 기반 답변, 인용, 근거 패널
- 지식 라이브러리: 문서, 공개 범위, 부서, 청크 preview
- 검색 실험실: 쿼리, top-k, 점수 기준, 접근 사유
- 운영 지표: 쿼리 로그 지표, 쿼리 추세, 최근 쿼리, 선택 쿼리 상세, 주요 근거 문서, 평가 리포트

Screenshot assets:

- `docs/assets/operations-demo-ko-v13-desktop.jpg`
- `docs/assets/operations-demo-ko-v13-mobile-overview.jpg`
- `docs/assets/operations-demo-ko-v13-mobile-full-page.jpg`
- `docs/assets/knowledge-admin-demo-ko-v1-desktop.jpg`

Portfolio screenshot capture:

```bash
pnpm web:build:static
pnpm portfolio:screenshots
```

## Verification

```bash
pytest -q
python3 -m compileall -q app
docker compose config -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
node scripts/check-package-manager.mjs
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
```

Expected current result:

```text
76 passed, 2 skipped
```

For the backend-free public demo build, see `docs/runbooks/static-demo-deploy.md`.

## Optional PostgreSQL Check

Start Colima with a low-resource profile, then run only the PostgreSQL service.

```bash
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml up -d postgres
docker exec enterprise-policy-rag-postgres \
  psql -U rag_app -d enterprise_policy_rag \
  -v ON_ERROR_STOP=1 \
  -f /docker-entrypoint-initdb.d/001_schema.sql
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

The normal test suite skips this integration test unless `RUN_POSTGRES_TESTS=1` is set.

## Optional OIDC JWT Check

The default demo does not need an IdP. The OIDC path can be tested locally with a deterministic HS256 secret.

```bash
AUTH_CONTEXT_PROVIDER=oidc_jwt \
OIDC_ISSUER=https://idp.example.test/ \
OIDC_AUDIENCE=enterprise-policy-rag \
OIDC_HS256_SECRET=local-oidc-secret-with-32-bytes-min \
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Call `GET /auth/session` with `Authorization: Bearer <jwt>`. In production-like checks, replace the local secret with `OIDC_JWKS_URL` from the IdP.

## Optional OpenAI Provider Check

The default demo does not need this. Use it only when an API key is intentionally available.

```bash
LLM_PROVIDER=openai \
OPENAI_API_KEY=<redacted> \
OPENAI_MODEL=gpt-4.1-mini \
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then call `POST /answer` with the same payload from the Backend section. The request still goes through the existing retrieval and citation flow; only the final `LLMProvider.complete()` call changes.

For a bounded live smoke without starting the API server, store `OPENAI_API_KEY` in ignored `.env.local` and run:

```bash
RUN_OPENAI_LIVE_SMOKE=1 python3 scripts/openai_live_smoke.py
```

Expected safe output shape:

```text
OpenAI live smoke passed: provider=openai model=gpt-4.1-mini retrieved=2 citations=2 latency_ms=<n> answer_chars=<n>
```
