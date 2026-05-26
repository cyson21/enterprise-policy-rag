# Enterprise Policy RAG Project Status

작성일: 2026-05-20
역할: 현재 상태, 문서 소유권, phase별 산출물, 주요 결정을 추적한다.

## 현재 스냅샷

| 항목 | 상태 |
|---|---|
| 도메인 | 엔터프라이즈 사내 정책/업무 문서 RAG |
| 목적 | AI Native Back-end Engineer 포지션 대응용 사이드 프로젝트 |
| 핵심 아키텍처 | React UI + FastAPI + PostgreSQL/pgvector + provider abstraction + eval/ops |
| 현재 Phase | Phase 4F Vercel Git integration connected |
| 실제 LLM API | 후순위. fake provider first |
| 온프레미스 | 1차 범위 제외 |

## 문서 소유권

| 문서 | 역할 |
|---|---|
| `README.md` | 외부 공개용 프로젝트 소개와 핵심 링크 |
| `TODO.md` | 현재 작업 상태 추적 |
| `docs/project-tracking.md` | 현재 상태와 주요 결정 |
| `docs/internal/design/*.md` | 전체 제품/화면/아키텍처 설계 |
| `docs/internal/plans/*.md` | 내부 실행 계획 |
| `docs/next-agent-bootstrap.md` | 다음 에이전트 시작 지침 |
| `.ai-runs/**` | 작업 단위별 목표, 변경, 결정, 검증 기록 |

## 현재까지 결정

- 프로젝트 컨셉은 `Enterprise Policy RAG Backend`로 한다.
- 공고 벤치마킹 기준은 RAG, LLM API, 권한, latency, 비용, eval, 운영 관측이다.
- StockRush의 Dev RAG는 개발 운영용 도구였고, 이 프로젝트는 제품 백엔드 RAG를 구현한다.
- 온프레미스 배포는 1차 범위에서 제외한다.
- 실제 OpenAI API 연결은 후순위로 두고, 초기 개발과 CI는 fake provider로 검증한다.
- embedding과 LLM 호출은 provider 인터페이스로 분리한다.
- 1차 MVP는 retrieval-only API까지 먼저 완성한다.
- 첫 구현 slice는 in-memory repository와 fake embedding으로 API key 없는 검증을 고정하고, PostgreSQL/pgvector는 compose와 schema로 먼저 준비한다.
- 권한 필터 기준은 same workspace, public visibility, owner access, department intersection이다.
- 포트폴리오 시연을 위해 화면은 필수 범위에 포함한다.
- 화면은 Search Console, Knowledge Library, Retrieval Lab, Operations 4개로 제한한다.
- UI는 Dify Knowledge/Retrieval Test와 Glean Search/Admin/Insights의 제품 패턴을 참고하되 그대로 복제하지 않는다.
- frontend package manager는 pnpm workspace를 사용한다.
- pnpm은 `packageManager: pnpm@11.1.3`으로 root `package.json`에 고정한다.
- Docker Desktop 대신 Colima를 저자원 Docker daemon으로 사용할 수 있게 한다.
- PostgreSQL 통합 검증은 기본 compose에 `docker-compose.low-resource.yml`을 겹쳐 1 CPU / 512MB 컨테이너 제한으로 실행한다.
- `/retrieve`와 `/answer` 호출은 query log repository에 기록하고, Operations API는 저장된 log에서 지표를 계산한다.
- Query log는 in-memory default와 `PostgresQueryLogRepository` 구현을 함께 둔다.
- `DATABASE_URL`이 설정되면 document/query log repository 모두 PostgreSQL runtime으로 전환한다.
- 기존 Docker volume은 init SQL이 자동 재실행되지 않으므로 schema 변경 후 `001_schema.sql`을 idempotent하게 재적용한다.
- retrieval result, answer, citation snapshot을 query log 하위로 저장하고 `/evidence/top`에서 top evidence document를 계산한다.
- eval run과 eval case result를 runtime repository에 저장하고 `GET /eval-runs`에서 history로 조회한다.
- Operations trend는 query log를 기준으로 `GET /metrics/trend`에서 retrieval/answer/zero-result/latency daily trend를 제공한다.
- Query drilldown은 `GET /queries/{query_id}`에서 query log, retrieval result, answer, citation snapshot을 함께 제공한다.
- OpenAI adapter는 `LLM_PROVIDER=openai`로 명시 선택하고 `OPENAI_API_KEY`가 있을 때만 live Responses API transport를 사용한다. 기본 테스트와 로컬 실행은 fake provider를 유지한다.
- Portfolio screenshot은 Operations 화면을 기준으로 desktop/mobile 상태를 캡처한다.
- Public portfolio demo는 static read-only fake-provider build로 배포한다. 현재 production URL은 `https://enterprise-policy-rag.vercel.app`이다.
- GitHub public repository는 `https://github.com/cyson21/enterprise-policy-rag`이다.
- Vercel Git integration은 GitHub App repo access 승인 후 `cyson21/enterprise-policy-rag`에 연결했다.

## Phase 0 완료 기준

- README, TODO, project tracking, foundation plan, next-agent bootstrap을 준비한다.
- 새 에이전트가 바로 실제 레포 기준으로 phase plan을 이어갈 수 있게 한다.
- 구현 전 ADR, 데이터 모델, API 경계를 먼저 정한다.

## Phase 0.5 아키텍처 재정리 산출물

- 전체 제품 아키텍처 설계: `docs/internal/design/2026-05-20-enterprise-policy-rag-product-architecture.md`
- 전체 상세 구현 계획: `docs/internal/plans/2026-05-20-enterprise-policy-rag-master-plan.md`
- 화면 포함 구현 계획: `docs/internal/plans/2026-05-20-architecture-first-ui-implementation-plan.md`
- 필수 화면 범위: Search Console, Knowledge Library, Retrieval Lab, Operations
- 구현 방향: frontend/backend/data model을 함께 계획한 뒤 다음 코드 작업 진행

## Phase 1 Prototype 구현 산출물

- FastAPI backend skeleton
- PostgreSQL + pgvector Docker Compose
- document/chunk schema
- fake embedding provider
- retrieval-only API
- 권한 필터 테스트

## Phase 1 검증 스냅샷

| 항목 | 결과 |
|---|---|
| Unit/API tests | `pytest -q` 기준 9 passed |
| Python compile smoke | `python3 -m compileall -q app` 통과 |
| Compose syntax | `docker compose config -q` 통과 |
| API key 의존성 | 없음. fake embedding provider 사용 |
| 제외 범위 | OpenAI adapter, 답변 생성, eval, admin dashboard |

## Phase 1A 예정 산출물

- React/Vite frontend skeleton
- Search Console
- Knowledge Library
- PostgreSQL repository integration
- Seeded demo data
- UI smoke test

## Phase 1A 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Frontend shell | `web/` React/Vite source scaffold 추가 |
| Package manager | pnpm 11.1.3 workspace 전환, `pnpm-lock.yaml` 생성 |
| Routes | Search Console, Knowledge Library, Retrieval Lab, Operations |
| Demo context | `GET /workspaces/current`, `GET /personas`, frontend persona fixtures |
| UI smoke | `pnpm web:smoke` 통과 |
| Frontend build | `pnpm web:build` 통과 |
| Backend regression | `pytest -q` 기준 11 passed |
| Dev server | `http://127.0.0.1:5173/` 응답 확인 |

## Phase 1B 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Retrieval response | rank, visibility, department ids, access reason, score threshold 추가 |
| Demo documents | Remote Access, Security Incident, Finance Reimbursement, Executive Access |
| Search Console | live `/api/retrieve` 호출과 evidence panel 연결 |
| Persona refresh | `security` persona는 Security Incident를 보고, `finance` persona는 제외됨 |
| API regression | `pytest -q` 기준 14 passed |
| Frontend verification | `pnpm web:smoke`, `pnpm web:build` 통과 |
| Browser smoke | `Search Console`, `Security Incident Manual`, `access_reason`, persona refresh 확인 |

## Phase 1C 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Document list API | `GET /documents?workspace_id=acme`가 문서 metadata와 chunk count를 반환 |
| Document detail API | `GET /documents/{document_id}?workspace_id=acme`가 chunk preview와 embedding dimensions를 반환 |
| Workspace guard | 다른 workspace로 document detail을 조회하면 `404` 반환 |
| Knowledge Library | live `/api/documents`와 detail API로 문서 목록, 권한 메타데이터, chunk preview 표시 |
| API regression | `tests/test_documents_api.py` 추가 |
| Frontend verification | `pnpm web:smoke`, `pnpm web:build` 대상에 Knowledge Library live wiring 포함 |

## Phase 1D 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Repository interface | `PolicyRepository` protocol을 추가하고 service/retrieval이 구현체 대신 인터페이스를 사용 |
| PostgreSQL repository | `PostgresPolicyRepository`가 workspace/document/chunk insert와 joined chunk 조회를 구현 |
| Import safety | `psycopg` 미설치 환경에서도 module import는 유지하고, 실제 DB repository 생성 시 명확한 RuntimeError 반환 |
| Unit verification | fake connection으로 insert SQL, vector literal, joined row mapping, document mapping 검증 |
| Integration path | `RUN_POSTGRES_TESTS=1` 전용 PostgreSQL round-trip retrieval test 추가 |
| Low-resource daemon | Colima 1 CPU / 약 1GB VM profile에서 Docker context `colima` 사용 |
| PostgreSQL limit | `docker-compose.low-resource.yml`로 1 CPU, 512MB memory, 64MB shm, reduced buffers 적용 |
| Integration result | 실제 PostgreSQL/pgvector 컨테이너 round-trip retrieval 통합 테스트 통과 |

## Phase 1D Docker 검증 스냅샷

| 항목 | 결과 |
|---|---|
| Docker daemon | Colima `--cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker` |
| Compose override | `docker-compose.low-resource.yml` 추가 |
| Container limits | `NanoCpus=1000000000`, `Memory=536870912`, `ShmSize=67108864` |
| PostgreSQL tuning | `shared_buffers=64MB`, `work_mem=4MB`, `maintenance_work_mem=32MB`, `max_connections=20`, `effective_cache_size=256MB` |
| Runtime sample | `docker stats --no-stream` 기준 `CPU=5.78%`, `MEM=36.55MiB / 512MiB` |
| Integration test | `tests/test_postgres_repository_integration.py` 기준 1 passed |
| Cleanup | Postgres container stop 후 `colima stop` 완료 |

## Phase 1E 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Retrieval Lab | 정적 preview에서 live `/api/retrieve` 호출 화면으로 전환 |
| Controls | query, top-k, score threshold를 조정해 retrieved chunk를 비교 |
| Persona context | app shell의 active persona와 workspace를 그대로 사용 |
| Debug metadata | rank, score, visibility, department ids, access reason, source 표시 |
| Guardrail | top-k와 score threshold를 UI에서 범위 제한 |
| Browser smoke | Retrieval Lab 화면, top-k clamp, debug panel, console error 0건 확인 |

## Phase 1F 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Metrics API | `GET /metrics/summary?workspace_id=acme` seeded 운영 지표 반환 |
| Recent queries API | `GET /queries/recent?workspace_id=acme` retrieval-only query rows 반환 |
| Operations screen | seeded API 기반 KPI, p95 latency, estimated cost, retrieval hit, zero-result rate 표시 |
| Query rows | query, user, latency, hit count, top score 표시 |
| Guardrail | eval runner, answer generation, OpenAI provider는 추가하지 않음 |
| Browser smoke | Operations screen, seeded metrics, recent query rows, console error 0건 확인 |

## Phase 2A 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Fake LLM provider | `FakeLLMProvider`가 `LLMProvider` 인터페이스 뒤에서 deterministic 답변 생성 |
| Answer API | `POST /answer`가 retrieval 결과 기반 answer, citations, refusal reason, provider metadata 반환 |
| Permission guard | Answer citation도 기존 retrieval permission filter를 그대로 사용 |
| Refusal | 근거가 없거나 threshold를 넘는 citation이 없으면 `insufficient_evidence` 반환 |
| Cost/latency | fake provider 기준 `estimated_cost_usd=0.0`, token/latency estimate 반환 |
| Search Console | cited answer, citation list, evidence panel을 함께 표시 |
| 제외 범위 | OpenAI adapter, 외부 LLM 호출, eval runner, production admin dashboard |

## Phase 3A 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Golden dataset | `golden-demo` 3개 케이스: security incident, finance reimbursement, executive access |
| Eval API | `POST /eval-runs`, `GET /eval-runs` 추가 |
| Retrieval hit | expected document가 retrieved/cited document에 포함되는지 계산 |
| Citation coverage | answer citations가 expected document를 포함하는지 계산 |
| Operations eval table | retrieval hit, citation coverage, case count, provider와 케이스별 hit/coverage 표시 |
| 제외 범위 | eval persistence, PostgreSQL eval tables, 외부 LLM judge |

## Phase 3B 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Query log model | `QueryLogCreate`, `StoredQueryLog` 추가 |
| Repository boundary | `QueryLogRepository` protocol, `InMemoryQueryLogRepository`, `PostgresQueryLogRepository` 추가 |
| Retrieval logging | `/retrieve` 호출이 mode=`retrieval`, latency, retrieved count, top score를 저장 |
| Answer logging | `/answer` 호출이 mode=`answer`, token count, estimated cost, refusal reason을 저장 |
| Metrics API | `/metrics/summary`가 저장된 query log에서 searches, p95 latency, retrieval hit, zero-result rate 계산 |
| Recent query API | `/queries/recent`가 retrieval/answer row를 최신순으로 반환 |
| PostgreSQL schema | `query_logs` table과 workspace/date, workspace/mode index 추가 |
| Demo behavior | `seed_demo=True`일 때 demo query logs를 seed하고, 이후 실제 호출이 상단에 추가됨 |
| 제외 범위 | runtime env 기반 PostgreSQL repository selection, eval persistence, OpenAI adapter |

## Phase 3C 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Runtime builder | `app/runtime.py` 추가 |
| Default mode | `DATABASE_URL`이 없으면 in-memory document/query log repository 사용 |
| PostgreSQL mode | `DATABASE_URL`이 있으면 `PostgresPolicyRepository`, `PostgresQueryLogRepository` 사용 |
| App factory | `create_app()`이 runtime builder를 통해 shared service instance 구성 |
| Runtime smoke | Colima low-resource Postgres에서 document ingest, retrieval, query log, metrics flow 통과 |
| Schema backfill | 기존 volume에 `query_logs`가 없어 `001_schema.sql`을 재적용해 idempotent DDL 확인 |
| 제외 범위 | ranked retrieval result table, answer/citation table, eval persistence, OpenAI adapter |

## Phase 3D 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Retrieval result persistence | `/retrieve` 호출 결과 chunk rank, score, access reason, document snapshot 저장 |
| Answer persistence | `/answer` 호출 answer text, refusal reason, provider, token/cost/latency 저장 |
| Citation persistence | answer citation chunk, quote, score, source snapshot 저장 |
| Top evidence API | `GET /evidence/top` 추가 |
| Operations screen | Top Evidence table 추가 |
| PostgreSQL schema | `retrieval_results`, `answers`, `citations` tables and indexes 추가 |
| Runtime smoke | Colima low-resource Postgres에서 새 schema 적용 후 runtime integration 통과 |
| 제외 범위 | eval run persistence, trend chart, OpenAI adapter |

## Phase 3E 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Eval repository | `EvalRunRepository`, `InMemoryEvalRunRepository`, `PostgresEvalRunRepository` 추가 |
| Eval run persistence | `POST /eval-runs`가 run summary와 case results 저장 |
| Eval history | `GET /eval-runs`가 저장된 최근 run history 반환 |
| Demo behavior | 저장된 eval run이 없으면 fake `golden-demo` run을 lazy 생성해 Operations가 비지 않음 |
| Runtime selection | `DATABASE_URL`이 있으면 eval repository도 PostgreSQL 사용 |
| PostgreSQL schema | `eval_runs`, `eval_case_results` tables and indexes 추가 |
| Runtime smoke | Colima low-resource Postgres에서 eval persistence flow 통과 |
| 제외 범위 | external LLM judge, trend chart, OpenAI adapter |

## Phase 3F 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Trend API | `GET /metrics/trend`가 query log를 날짜별로 묶어 retrieval count, answer count, zero-result count, average latency를 반환 |
| Repository support | `InMemoryQueryLogRepository`, `PostgresQueryLogRepository` 모두 trend aggregation 구현 |
| Operations screen | Query Trend table 추가 |
| PostgreSQL runtime | Colima low-resource Postgres에서 `/metrics/trend` runtime smoke 통과 |
| Verification | `pytest -q` 기준 46 passed, 2 skipped |
| 제외 범위 | query drilldown, OpenAI adapter, external LLM judge |

## Phase 3G 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Query detail API | `GET /queries/{query_id}`가 query log metadata, retrieval snapshots, answer metadata, citation snapshots 반환 |
| Repository support | `InMemoryQueryLogRepository`, `PostgresQueryLogRepository` 모두 query detail lookup 구현 |
| Operations screen | Recent Queries row 선택과 Query Detail panel 추가 |
| PostgreSQL runtime | Colima low-resource Postgres에서 `/queries/{query_id}` runtime smoke 통과 |
| Verification | `pytest -q` 기준 50 passed, 2 skipped |
| 제외 범위 | OpenAI adapter, external LLM calls, production admin dashboard |

## Phase 3H 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Provider selection | `build_llm_provider_from_env` 추가, 기본값은 `fake` |
| OpenAI adapter boundary | `OpenAILLMProvider`가 request payload를 구성하고 provider 선택 경계를 고정 |
| API key guard | `LLM_PROVIDER=openai` 선택 시 `OPENAI_API_KEY` 필수 |
| Runtime wiring | `build_services_from_env`가 LLM provider를 명시 주입 |
| Verification | `pytest -q` 기준 56 passed, 2 skipped |
| 제외 범위 | live OpenAI HTTP transport, external LLM calls in tests |

## Phase 4A 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Operations polish | Trend, Recent Queries, Query Detail을 2-column operations console로 재배치 |
| Responsive guard | Mobile에서 table은 내부 가로 스크롤로 제한하고 body overflow 제거 |
| Screenshot assets | `docs/assets/operations-demo-ko-v7-desktop.jpg`, `docs/assets/operations-demo-ko-v12-mobile-overview.jpg`, `docs/assets/operations-demo-ko-v12-mobile-full-page.jpg` |
| Korean UI | 화면 라벨, persona, department, document title, provider 표시를 한국어로 전환 |
| Screenshot refresh | 합성 보드 대신 개별 산출물 기준으로 desktop 1440x1650, mobile webview 500x1500, mobile full page 500x3600 재촬영 |
| Browser QA | Desktop/mobile render, console error/warn 0건, framework overlay 없음 |
| Verification | `pnpm` 대체 runner 기준 frontend smoke/build 통과 |
| 제외 범위 | live OpenAI HTTP transport, deployed public demo |

## Phase 4B 진행 스냅샷

| 항목 | 결과 |
|---|---|
| OpenAI live transport | `OpenAIHTTPTransport`가 `/v1/responses` payload를 전송하고 `output_text` 또는 message content text를 파싱한다 |
| Provider guard | 기본값은 계속 `FakeLLMProvider`; `LLM_PROVIDER=openai`는 `OPENAI_API_KEY`가 있을 때만 활성화된다 |
| Dependency policy | optional OpenAI path 때문에 새 runtime dependency를 추가하지 않고 Python standard library HTTP transport를 사용한다 |
| Test strategy | 외부 OpenAI 호출 없이 fake HTTP opener로 request/header/body/response/error parsing을 검증한다 |
| Portfolio closeout | `docs/portfolio-interview-guide.md`에 demo script, architecture story, tradeoff를 정리했다 |
| 제외 범위 | 실제 OpenAI API key smoke, public hosted deployment, production auth/SSO |

## Phase 4C 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Static demo mode | `VITE_DEMO_MODE=static`일 때 frontend가 `/api` 호출 없이 fake-provider fixture를 사용한다 |
| Build scripts | `web:build:static`, `web:preview:static`, `web:smoke:static` 추가 |
| Deploy config | `vercel.json`이 static build command와 `web/dist` output을 지정한다 |
| Browser smoke | `scripts/smoke-static-demo.mjs`가 headless Chrome으로 Operations route를 열고 `/api` 요청이 없는지 확인한다 |
| Runbook | `docs/runbooks/static-demo-deploy.md`에 local build, smoke, preview, Vercel 배포 절차를 기록했다 |
| 배포 상태 | Phase 4D에서 production alias 발급 완료 |

## Phase 4D 진행 스냅샷

| 항목 | 결과 |
|---|---|
| Vercel auth | Device auth로 `cyson21s-projects` team에 로그인 |
| Project link | `cyson21s-projects/enterprise-policy-rag` |
| Production URL | `https://enterprise-policy-rag.vercel.app` |
| Deployment ID | `dpl_8rEfeFSZUHqSZaBzJdgJ45vUxtrw` |
| Deployment state | Vercel API 기준 `READY` |
| Browser verification | Headless Chrome으로 `/?route=operations` 렌더링, `공개 데모`, `운영 지표`, `쿼리 상세`, `평가 리포트` 확인 |
| 남은 범위 | production auth/SSO, admin workflow |

## Phase 4E 진행 스냅샷

| 항목 | 결과 |
|---|---|
| GitHub repo | `https://github.com/cyson21/enterprise-policy-rag` public repository 생성 |
| Remote | local `origin`을 `https://github.com/cyson21/enterprise-policy-rag.git`로 설정 |
| Push | `main` branch push 완료 |
| Secret scan | dummy `sk-test`와 `<redacted>` 문서 예시 외 실제 token/key 패턴 없음 |
| Vercel Git connect | 초기 시도는 GitHub App repo access 미승인으로 실패 |
| Deploy hook fallback | Vercel deploy hook도 Git 연결 프로젝트에서만 생성 가능해 실패 |
| 후속 처리 | Phase 4F에서 GitHub App 접근 승인 후 연결 완료 |

## Phase 4F 진행 스냅샷

| 항목 | 결과 |
|---|---|
| GitHub App access | 사용자가 Vercel GitHub App에 `cyson21/enterprise-policy-rag` 접근 권한 승인 |
| Vercel Git connect | `vercel git connect https://github.com/cyson21/enterprise-policy-rag.git --yes`가 already connected 상태 반환 |
| Deploy hook check | `vercel deploy-hooks list --project enterprise-policy-rag --scope cyson21s-projects`가 project id와 empty hooks list를 정상 반환 |
| Browser policy | 회사 작업 화면 노출을 피하기 위해 승인 이후 검증은 Chrome 없이 CLI로 진행 |

## Phase 2 완료 산출물

- LLM provider interface
- fake LLM provider
- OpenAI adapter
- citation answer API
- query log, token, latency, cost tracking

## Phase 3/4 완료 산출물

- Retrieval Lab
- Operations dashboard
- golden question set
- eval runner
- retrieval hit report
- citation coverage report
- 운영 지표 조회 API
- PostgreSQL runtime repository selection
- eval run persistence

## 남은 확장 후보

- Production auth/SSO
- Admin workflow 확장

## 참고 벤치마크

| 레퍼런스 | 참고 관점 |
|---|---|
| R2R | RAG API 서버 기능 범위 |
| Haystack | pipeline 분리와 component 경계 |
| RAGFlow | 문서 처리와 citation UX |
| Open RAG Eval | 평가 리포트와 품질 기준 |
| AnythingLLM | workspace와 문서 채팅 UX |
