# Enterprise Policy RAG TODO

마지막 갱신: 2026-05-26
상태 표기: `[ ]` 미시작, `[~]` 진행 중, `[x]` 완료, `[!]` 차단

## 운영 원칙

- 이 파일은 현재 작업 상태를 추적하는 단일 TODO 목록으로 사용한다.
- 큰 방향과 의사결정 근거는 `docs/project-tracking.md`에 기록한다.
- 구현 전 phase plan을 먼저 작성하고, 완료 기준을 만족해야 `[x]`로 변경한다.
- 실제 LLM API 호출은 fake provider 기반 테스트와 인터페이스가 안정된 뒤 연결한다.

## Phase 0. 프로젝트 기준 정리

- [x] Project 02 컨셉 확정
  - 결과: `Enterprise Policy RAG Backend`
- [x] StockRush와의 차이 정리
  - 결과: StockRush는 개발 운영용 Dev RAG, Project 02는 제품 백엔드 RAG를 다룬다.
- [x] 온프레미스 제외 결정
  - 결과: 1차 범위는 로컬 Docker Compose 기반 SaaS형 백엔드로 제한한다.
- [x] 실제 LLM API 연결 후순위 결정
  - 결과: fake provider를 먼저 두고 OpenAI adapter는 후속 phase로 분리한다.
- [x] ADR 디렉터리와 첫 ADR 작성
  - 결과: `docs/adr/0001-fake-provider-first-retrieval-rag.md`
- [x] API/데이터 모델 초안 작성
  - 결과: `docs/api-data-model.md`

## Phase 0.5. 전체 제품 아키텍처 재정리

- [x] 화면 포함 전체 제품 설계 작성
  - 결과: `docs/internal/design/2026-05-20-enterprise-policy-rag-product-architecture.md`
- [x] 필수 화면 범위 확정
  - 결과: Search Console, Knowledge Library, Retrieval Lab, Operations 4개 화면으로 제한한다.
- [x] 레퍼런스 기반 UX 방향 확정
  - 결과: Dify Knowledge/Retrieval Test, Glean Search/Admin/Insights 패턴을 참고하되 그대로 복제하지 않는다.
- [x] 화면/API/data model 상세 구현 계획 작성
  - 결과: `docs/internal/plans/2026-05-20-architecture-first-ui-implementation-plan.md`
- [x] 전체 master implementation plan 작성
  - 결과: `docs/internal/plans/2026-05-20-enterprise-policy-rag-master-plan.md`

## Phase 1. Retrieval Core Prototype

- [x] FastAPI 프로젝트 스캐폴딩
  - 결과: `app/main.py`에 health, document ingestion, retrieval-only endpoint를 구성했다.
- [x] PostgreSQL + pgvector 로컬 compose 구성
  - 결과: `docker-compose.yml`과 `infra/postgres/init/001_schema.sql`을 추가했다.
- [x] document/chunk metadata schema 작성
  - 결과: workspace, document, document chunk, vector column, permission filter용 index를 정의했다.
- [x] Markdown/TXT ingestion API 구현
  - 결과: `POST /documents`가 metadata와 content를 받아 chunk를 저장한다.
- [x] chunking strategy 구현
  - 결과: paragraph 기반 deterministic chunking을 추가했다.
- [x] fake embedding provider 구현
  - 결과: API key 없이 동작하는 deterministic hash-vector provider를 추가했다.
- [x] 권한 필터가 적용된 retrieval API 구현
  - 결과: workspace, owner, department, visibility 기준으로 결과를 제한한다.
- [x] retrieval-only API 테스트 작성
  - 결과: pytest 9개로 chunking, fake embedding, permission filter, API 흐름을 검증한다.

## Phase 1A. Retrieval Core + Search UI

- [x] pnpm workspace 전환
  - 결과: root `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `pnpm web:*` scripts를 추가했다.
- [x] React/Vite frontend skeleton 구성
  - 결과: `web/` 아래 sidebar, top bar, workspace/persona selector, route shell source를 구성했다.
- [x] Search Console 구현
  - 결과: persona별 live retrieval 결과와 source/chunk/score/access reason 패널을 실제 API로 보여준다.
- [x] Knowledge Library 구현
  - 결과: `GET /documents`, `GET /documents/{document_id}` API와 live document/detail/chunk preview 화면을 연결했다.
- [x] PostgreSQL repository 연결
  - 결과: `PostgresPolicyRepository`와 fake connection 기반 repository 테스트를 추가했고, Colima low-resource Docker daemon에서 PostgreSQL/pgvector round-trip 통합 테스트를 통과했다.
  - 검증: `RUN_POSTGRES_TESTS=1 DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag pytest tests/test_postgres_repository_integration.py -q`
- [x] seeded demo data 작성
  - 결과: workspace/persona fixture, `/personas` API, demo documents를 추가했다.
- [x] 화면 smoke test 작성
  - 결과: `pnpm web:smoke`가 핵심 shell/route/persona 라벨을 검증한다.

## Phase 2. LLM Answer Layer

- [x] `LLMProvider` 인터페이스 정의
  - 결과: `app/providers.py`에 LLM provider boundary를 유지한다.
- [x] fake LLM provider 구현
  - 결과: API key 없이 deterministic 답변을 만드는 `FakeLLMProvider`를 추가했다.
- [x] OpenAI adapter boundary 추가
  - 결과: `LLM_PROVIDER=openai` 선택 시 `OpenAILLMProvider`를 만들고, 기본 검증은 계속 fake provider로 유지한다.
- [x] Live OpenAI completion transport 연결
  - 결과: `OpenAIHTTPTransport`가 Responses API payload를 전송하고 output text를 파싱한다. 기본 테스트는 mock opener만 사용하고 외부 호출은 하지 않는다.
- [x] citation 포함 답변 API 구현
  - 결과: `POST /answer`가 retrieval 결과를 citation으로 반환한다.
- [x] 근거 부족 시 답변 거부 규칙 구현
  - 결과: citation이 없으면 `refusal_reason=insufficient_evidence`를 반환한다.
- [x] token/latency/cost 기록 구현
  - 결과: `/retrieve`, `/answer` 호출이 query log repository에 mode, latency, retrieved count, top score, provider, token/cost metadata를 저장한다.

## Phase 3. Eval and Operations

- [x] Retrieval Lab 화면 구현
  - 결과: query, top-k, score threshold, persona 기준으로 live retrieval 결과와 debug metadata를 비교한다.
- [x] Operations 화면 구현
  - 결과: query log 기반 metrics/recent query API로 KPI, latency, cost estimate, retrieval hit, query rows를 표시한다.
- [x] golden question set fixture 작성
  - 결과: `golden-demo` 3개 케이스를 추가했다.
- [x] retrieval hit 평가 구현
  - 결과: `POST /eval-runs`가 retrieval hit rate를 계산한다.
- [x] citation coverage 평가 구현
  - 결과: answer citation 문서 기준 coverage를 계산한다.
- [x] eval report 생성
  - 결과: Operations에 Eval Report table을 표시한다.
- [x] query log 조회 API 구현
  - 결과: `/queries/recent`가 runtime query log repository에서 최신 retrieval/answer row를 반환한다.
  - 결과: `/metrics/summary`가 저장된 query log에서 searches, p95 latency, estimated cost, retrieval hit rate, zero-result rate를 계산한다.
- [x] runtime PostgreSQL repository selection 구현
  - 결과: `DATABASE_URL`이 없으면 in-memory document/query log repository를 쓰고, 있으면 `PostgresPolicyRepository`와 `PostgresQueryLogRepository`를 사용한다.
  - 검증: Colima low-resource Postgres에서 document ingestion, retrieval, query log, metrics runtime smoke를 통과했다.
- [x] retrieval result / answer / citation persistence 구현
  - 결과: retrieval result, answer, citation detail row를 query log 하위로 저장한다.
  - 결과: `/evidence/top`이 retrieval/citation count와 평균 score 기준 top evidence document를 반환한다.
  - 결과: Operations 화면에 Top Evidence table을 추가했다.
- [x] eval run persistence 구현
  - 결과: `POST /eval-runs`가 eval run summary와 case result를 저장하고, `GET /eval-runs`가 저장된 history를 반환한다.
  - 결과: PostgreSQL runtime에서도 `eval_runs`, `eval_case_results` 저장/조회 smoke를 통과했다.
- [x] Operations trend 구현
  - 결과: `/metrics/trend`가 retrieval/answer/zero-result/latency daily trend를 반환하고 Operations 화면에 Query Trend table을 표시한다.
- [x] Operations query drilldown 구현
  - 결과: `/queries/{query_id}`가 query log, retrieval result, answer, citation snapshot을 반환하고 Operations에서 selected query detail을 표시한다.
- [x] 운영 지표 README 반영
  - 결과: README Current Implementation에 Operations/Eval 범위를 반영했다.

## Phase 4. Portfolio Package

- [x] README 공개용 정리
  - 결과: 현재 구현 범위와 핵심 문서 링크를 갱신했다.
- [x] 아키텍처 이미지 작성
  - 결과: `docs/assets/architecture.svg`
- [x] 포트폴리오 one-pager 작성
  - 결과: `docs/portfolio-one-pager.md`
- [x] Operations demo polish와 screenshot 작성
  - 결과: Operations를 2-column console로 정리하고 desktop/mobile screenshot assets를 추가했다.
- [x] 데모 UI 한국어 전환과 screenshot 재촬영
  - 결과: 사용자명, 부서, 문서명, provider, Operations 라벨을 한국어로 표시하고 desktop/mobile/detail screenshot을 다시 저장했다.
- [x] 데모 실행 runbook 작성
  - 결과: `docs/runbooks/local-demo.md`
- [x] 최종 검증 기록 정리
  - 결과: 각 `.ai-runs/*/verification.md`에 작업 단위별 검증을 남겼다.
- [x] 포트폴리오 면접/시연 가이드 작성
  - 결과: `docs/portfolio-interview-guide.md`
- [x] Static read-only demo build 준비
  - 결과: `VITE_DEMO_MODE=static`, `web:build:static`, `web:smoke:static`, `vercel.json`, `docs/runbooks/static-demo-deploy.md`
- [x] 공개 배포 URL 발급
  - 결과: `https://enterprise-policy-rag.vercel.app`
- [x] GitHub remote 생성과 push
  - 결과: `https://github.com/cyson21/enterprise-policy-rag`
- [x] Vercel Git integration 연결
  - 결과: GitHub App 접근 승인 후 `cyson21/enterprise-policy-rag`가 Vercel project에 연결되었고, deploy hook 조회가 정상 동작한다.

## Phase 5. 남은 확장 후보

- [x] Production auth/SSO boundary 설계와 최소 구현
  - 결과: `GET /auth/session`, `POST /auth/retrieve`, `POST /auth/answer`, demo/trusted header auth provider, UI auth status를 추가했다.
- [x] Admin workflow 확장
  - 결과: admin-role document update/delete, synchronous `indexing_status`, append-only audit log API를 추가했다.
- [x] Admin UI controls
  - 결과: Knowledge Library에 admin persona 전용 document update/delete controls와 audit log view를 추가했고, non-admin persona는 읽기 전용 안내를 표시한다.
- [x] Real IdP/OIDC adapter
  - 결과: `AUTH_CONTEXT_PROVIDER=oidc_jwt` provider가 Bearer JWT의 issuer/audience/signature/expiry를 검증하고 session claim을 매핑한다.
- [ ] Controlled live OpenAI smoke
  - 목표: 기본 fake-provider 경로를 유지하면서 API key가 있을 때만 제한된 live OpenAI smoke를 실행한다.
