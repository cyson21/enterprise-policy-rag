# Enterprise Policy RAG

Enterprise Policy RAG는 기업 내부 정책, 업무 매뉴얼, 보안 지침 문서를 권한 기반으로 검색하고, 근거가 있는 답변과 운영 지표를 제공하는 RAG 백엔드 프로젝트입니다.

## Project Goal

RAG를 단순 챗봇 기능으로 구현하는 것이 아니라, 실제 엔터프라이즈 백엔드에서 문제가 되는 권한, 근거, latency, token cost, 평가 가능성을 함께 다룹니다.

1차 범위에서는 온프레미스 설치형 배포를 제외하고, 로컬 Docker Compose로 재현 가능한 SaaS형 백엔드와 포트폴리오 시연용 운영 화면을 함께 만듭니다.

## MVP Scope

| 영역 | 구현 목표 |
|---|---|
| Document Ingestion | Markdown/TXT 문서 등록, chunking, metadata 저장 |
| Embedding Store | PostgreSQL + pgvector 기반 chunk vector 저장 |
| Retrieval | workspace, user, department, visibility 기반 권한 필터 검색 |
| Answer Generation | fake LLM provider 우선, 이후 OpenAI adapter 추가 |
| Citation | 답변에 사용된 chunk와 source document 반환 |
| Observability | request latency, token usage, estimated cost, retrieved chunks 기록 |
| Eval | golden question set 기반 retrieval hit와 citation coverage 측정 |

## Non-Goals

- 온프레미스 설치형 배포
- 처음부터 복잡한 multi-agent workflow
- 대규모 문서 파서 제품화
- 실제 결제/과금 시스템
- Kubernetes 운영 자동화

## Planned Stack

| 영역 | 후보 |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript, Vite |
| Package Manager | pnpm workspace |
| DB | PostgreSQL, pgvector |
| Worker | FastAPI background task 또는 RQ/Celery 후순위 검토 |
| Cache/Queue | Redis |
| LLM | fake provider first, OpenAI adapter later |
| Runtime | Docker Compose |
| Test | pytest, API integration tests, eval fixtures |

## First Milestone

```text
문서 등록
→ chunk 저장
→ fake embedding 기반 검색
→ 권한 필터 적용
→ retrieval-only API 응답
→ 테스트와 project tracking 기록
```

실제 LLM API 연결은 후순위입니다. 초기 구조는 `LLMProvider`와 `EmbeddingProvider`를 분리해 API key 없이도 테스트와 CI가 통과하도록 설계합니다.

## Current Implementation

현재 구현된 단위는 backend retrieval core prototype, Phase 1A frontend shell, Phase 1B live Search Console, Phase 1C Knowledge Library API/UI, Phase 2 fake answer layer, Phase 3 fake eval runner, query log 기반 Operations API, top evidence persistence, eval persistence, Operations query trend/detail, opt-in OpenAI Responses API transport, production auth/SSO boundary, admin document workflow API, Knowledge Library admin UI controls, 한국어 데모 UI와 최신 screenshot assets입니다.

- FastAPI application skeleton: `GET /health`, `POST /documents`, `GET /documents`, `GET /documents/{document_id}`, `PATCH /admin/documents/{document_id}`, `DELETE /admin/documents/{document_id}`, `GET /admin/audit-logs`, `POST /retrieve`, `POST /answer`, `GET /auth/session`, `POST /auth/retrieve`, `POST /auth/answer`, `POST /eval-runs`, `GET /eval-runs`, `GET /metrics/summary`, `GET /metrics/trend`, `GET /queries/recent`, `GET /queries/{query_id}`, `GET /evidence/top`
- Demo foundation API: `GET /workspaces/current`, `GET /personas`
- Auth/SSO boundary: default demo auth context, opt-in trusted header provider, session-bound retrieval/answer endpoints
- UI-ready retrieval response: rank, score, visibility, department ids, access reason
- Knowledge Library response: document metadata, chunk count, chunk preview, embedding dimensions
- Demo documents: Remote Access, Security Incident, Finance Reimbursement, Executive Access
- PostgreSQL + pgvector compose: `docker-compose.yml`
- Low-resource PostgreSQL compose override: `docker-compose.low-resource.yml`
- Schema: workspace, document, document chunk, query log, retrieval result, answer, citation, eval run, eval case result, admin audit log, pgvector embedding column
- Repository implementations: in-memory default, optional `PostgresPolicyRepository`, optional `PostgresQueryLogRepository`
- Runtime storage selection: no `DATABASE_URL` uses in-memory repositories; `DATABASE_URL` uses PostgreSQL repositories for documents, query logs, and eval runs
- Provider boundary: `EmbeddingProvider`, `LLMProvider`, deterministic `FakeEmbeddingProvider`, deterministic `FakeLLMProvider`, env-gated `OpenAILLMProvider`
- LLM provider selection: default `LLM_PROVIDER=fake`; `LLM_PROVIDER=openai` requires `OPENAI_API_KEY` and uses a standard-library OpenAI Responses API transport outside default tests
- Local retrieval path: in-memory repository + fake embeddings
- Local answer path: retrieval evidence + fake LLM provider + citations + refusal on insufficient evidence
- Permission filter: same workspace, public visibility, owner access, department intersection
- Frontend shell: React/Vite source scaffold under `web/`
- UI routes: 검색 콘솔, 지식 라이브러리, 검색 실험실, 운영 지표
- UI localization: backend seed 데이터가 영어여도 사용자명, 부서, 문서명, provider, 상태 라벨을 한국어로 표시
- Search Console: live `/api/retrieve` and `/api/answer` calls with persona-based refresh, cited answer, citation list, and evidence panel
- Knowledge Library: live `/api/documents` and `/api/documents/{document_id}` data with document detail and chunk previews
- Admin workflow: admin-role document replacement/deletion, synchronous indexing status, append-only audit log API
- Admin UI controls: Knowledge Library에서 admin persona로 document update/delete와 audit log 조회를 조작하고, non-admin persona는 읽기 전용 상태를 표시
- Retrieval Lab: live `/api/retrieve` debugging with query, top-k, score threshold, persona, score, and access reason
- Operations: query log 기반 `/api/metrics/summary`, `/api/metrics/trend`, `/api/queries/recent`, `/api/queries/{query_id}`, `/api/evidence/top`, persisted `/api/eval-runs` with usage, latency, cost estimate, retrieval hit, zero-result rate, daily retrieval/answer trend, recent query rows, selected query detail, top evidence documents, and eval history
- Eval: `golden-demo` question set, fake-provider retrieval hit and citation coverage report
- Demo personas: 김민아, 박준, 이하나, 최서진
- Portfolio screenshots: `docs/assets/operations-demo-ko-v7-desktop.jpg` 1440x1650, `docs/assets/operations-demo-ko-v12-mobile-overview.jpg` 500x1500, `docs/assets/operations-demo-ko-v12-mobile-full-page.jpg` 500x3600
- Static portfolio demo mode: `VITE_DEMO_MODE=static` build avoids `/api` calls and serves read-only fake-provider data from `web/dist`
- Public demo: `https://enterprise-policy-rag.vercel.app`
- GitHub repository: `https://github.com/cyson21/enterprise-policy-rag`
- Vercel Git integration: connected to `cyson21/enterprise-policy-rag` for push-based deployments
- Auth UI status: top bar shows the current auth session mode while keeping persona selection for demo scenarios
- Tests: chunking, fake embedding, fake answer, permission filter, retrieval-only API flow, persona API, document API, answer API, eval API, retrieval metadata API, query log metrics/trend/detail, evidence persistence, eval persistence, PostgreSQL repository integration, frontend shell/static smoke

다음 구현은 real IdP/OIDC adapter 또는 controlled live OpenAI smoke 중 하나로 나눌 수 있습니다. 기본 로컬/CI 경로는 계속 API key 없이 fake provider로 동작합니다.

## Product Screen Plan

필수 화면은 4개로 제한합니다.

| 화면 | 목적 |
|---|---|
| 검색 콘솔 | 직원이 질문하고 권한 내 검색 결과, 답변, 근거를 확인 |
| 지식 라이브러리 | 문서 등록, chunk 상태, visibility/department/owner 관리 |
| 검색 실험실 | top-k, score threshold, persona별 retrieval 품질 디버깅 |
| 운영 지표 | query, latency, cost estimate, eval 품질 지표 확인 |

## Local Verification

```bash
pytest -q
python3 -m compileall -q app
docker compose config -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
pnpm web:smoke
```

표준 실행 환경에서는 개발 의존성을 설치한 뒤 앱을 실행합니다.

```bash
python3 -m pip install -e ".[dev]"
uvicorn app.main:app --reload
corepack enable pnpm
pnpm install
pnpm web:dev
```

API key 없이도 테스트와 retrieval-only 로컬 검증이 가능해야 합니다.

Frontend 명령은 저장소 루트에서 실행합니다.

```bash
pnpm check:package-manager
pnpm web:smoke
pnpm web:build
pnpm web:build:static
pnpm web:smoke:static
```

PostgreSQL repository 통합 테스트는 Docker Postgres가 떠 있고 Python 환경에 `psycopg`가 설치된 경우에만 실행합니다. Docker Desktop 대신 Colima를 쓰면 낮은 CPU/RAM으로 검증할 수 있습니다.

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew install colima
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
python3 -m pip install 'psycopg[binary]>=3.2,<4.0'
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml up -d postgres
```

기존 volume에 schema가 이미 만들어진 뒤 새 테이블이 추가된 경우에는 init SQL을 idempotent하게 다시 적용합니다.

```bash
docker exec enterprise-policy-rag-postgres \
  psql -U rag_app -d enterprise_policy_rag \
  -v ON_ERROR_STOP=1 \
  -f /docker-entrypoint-initdb.d/001_schema.sql
```

```bash
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
```

검증 후에는 자원 점유를 줄이기 위해 Postgres와 Colima를 내립니다.

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

## Key Docs

| 문서 | 내용 |
|---|---|
| [ADR 0001](docs/adr/0001-fake-provider-first-retrieval-rag.md) | fake provider first와 Docker 선택 검증 결정 |
| [API and Data Model](docs/api-data-model.md) | 현재 API surface와 데이터 모델 초안 |
| [Local Demo Runbook](docs/runbooks/local-demo.md) | API key 없는 로컬 실행과 검증 |
| [Static Demo Deploy Runbook](docs/runbooks/static-demo-deploy.md) | 백엔드 없는 public read-only 데모 배포 절차 |
| [Portfolio One-Pager](docs/portfolio-one-pager.md) | 포트폴리오 요약 |
| [Architecture SVG](docs/assets/architecture.svg) | 아키텍처 다이어그램 |

## Working Rule

