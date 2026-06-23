# Enterprise Policy RAG

Enterprise Policy RAG는 기업 내부 정책, 업무 매뉴얼, 보안 지침 문서를 권한 기반으로 검색하고, 근거가 있는 답변과 운영 지표를 제공하는 RAG 백엔드 프로젝트입니다. 기본 경로는 fake provider와 in-memory 저장소로 동작하며, PostgreSQL/pgvector와 OpenAI 연동은 명시적으로 켜는 선택형 경로입니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 문제 | 사내 문서 RAG에서 권한 필터, citation, 평가, 지연/비용 관측이 답변 품질만큼 중요함 |
| 핵심 역량 | FastAPI, PostgreSQL/pgvector, provider boundary, permission-aware retrieval, eval/observability, React demo |
| 백엔드 초점 | 권한 기반 retrieval, citation/refusal, provider opt-in, query observability |
| 대표 증거 | `pytest`, frontend smoke/build, static public demo, PostgreSQL 선택 통합 테스트, controlled OpenAI live smoke |
| 실행 기준 | API key 없이 fake provider + in-memory repository로 로컬 검증 가능 |
| 범위 경계 | 공개 데모는 static fixture 중심이며, 운영형 인증/실시간 OpenAI/production SaaS 전환은 별도 opt-in 또는 hardening 범위 |

## 핵심 성과

| 성과 | 상태 | 근거 |
|---|---|---|
| 권한 기반 검색 | workspace/user/department/visibility 필터로 private 문서 혼입 방지 | retrieval/API tests |
| 근거 기반 답변 | citation 후보와 근거 부족 refusal을 API와 UI에서 확인 | answer tests, Search Console |
| 외부 비용 없는 기본 검증 | fake embedding/LLM과 in-memory repository로 전체 핵심 경로 검증 | `pytest`, frontend smoke/build |
| 선택형 live provider | OpenAI/PostgreSQL은 환경 변수로만 활성화 | live smoke guard, PostgreSQL integration tests |

## 왜 만들었나

RAG를 단순 챗봇 기능으로 만들면 백엔드 역량이 잘 드러나지 않습니다. 이 프로젝트는 “누가 어떤 문서를 볼 수 있는가”, “답변 근거가 무엇인가”, “검색 품질과 비용을 어떻게 관측하는가”를 중심으로 제품형 RAG 백엔드의 핵심 경계를 보여줍니다.

## 백엔드 설계 포인트

| 포인트 | 선택 이유 | 구현/검증 |
|---|---|---|
| 권한 선필터 retrieval | 생성 모델 이전에 접근 가능한 chunk만 후보로 만들어야 함 | permission filter tests |
| fake-first provider boundary | API key, 비용, 네트워크 없이 회귀 검증을 안정화하기 위함 | fake embedding/LLM default, `pytest` |
| citation/refusal | 근거 없는 답변을 줄이고 답변 판단 근거를 남기기 위함 | answer API tests, Search Console |
| observability | latency, token, cost estimate, retrieval quality를 운영 지표로 남기기 위함 | metrics/trend/detail APIs |

## 아키텍처

```text
문서 등록
-> deterministic chunking
-> embedding 저장(in-memory 또는 PostgreSQL/pgvector)
-> workspace/user/department/visibility 권한 필터
-> retrieval 결과와 citation 후보 생성
-> fake 또는 OpenAI LLM provider
-> 답변, refusal, citation, query log, eval/metric 저장
-> React demo console / static public demo
```

`EmbeddingProvider`, `LLMProvider`, repository 구현을 분리해 기본 검증은 API key와 Docker 없이 통과하고, PostgreSQL/pgvector 또는 OpenAI는 환경 변수로만 켭니다.

## 구현 범위

| 영역 | 구현 내용 | 증거 |
|---|---|---|
| Document API | 문서 등록, 조회, 수정, 삭제, chunk preview | FastAPI tests |
| Retrieval | workspace/user/department/visibility 기반 권한 필터, score/top-k 제어 | retrieval tests, Search Console |
| Answer | fake LLM 답변, 근거 부족 refusal, citation 반환 | answer API tests |
| Provider Boundary | fake embedding/LLM 기본값, OpenAI Responses/Embeddings opt-in adapter | controlled live smoke guard |
| Persistence | in-memory 기본, PostgreSQL/pgvector 선택 repository | PostgreSQL integration smoke |
| Auth Boundary | demo context, trusted headers, OIDC JWT adapter, session-bound retrieve/answer | auth/OIDC tests |
| Observability | query log, latency, token, cost estimate, evidence top, trend/detail | Operations API/UI |
| Demo UI | Search Console, Knowledge Library, Retrieval Lab, Operations | frontend smoke/static build |
| Public Demo | `VITE_DEMO_MODE=static` read-only fake-provider build | Vercel production URL |

## 대표 시나리오

| 시나리오 | 검증한 문제 | 결과/증거 |
|---|---|---|
| 권한 기반 검색 | 다른 workspace/department/private 문서가 섞이지 않는지 | permission filter tests |
| Citation 답변 | 답변이 retrieval 근거와 함께 반환되는지 | answer API, Search Console |
| 근거 부족 refusal | 검색 근거가 부족할 때 답변을 꾸미지 않는지 | fake answer tests |
| Query observability | latency, token, cost estimate, retrieved chunks가 남는지 | metrics/trend/detail APIs |
| Eval runner | golden set 기준 retrieval hit와 citation coverage를 계산하는지 | eval API/tests |
| Static public demo | 공개 데모가 `/api` 없이 렌더링되는지 | `pnpm web:smoke:static`, Vercel URL |
| OpenAI opt-in smoke | 실제 OpenAI 경로가 provider boundary 뒤에서만 켜지는지 | `RUN_OPENAI_LIVE_SMOKE=1` 수동 smoke |

## 기술적 의사결정과 트러블슈팅

| 주제 | 문제/선택지 | 적용 | 검증/남은 리스크 |
|---|---|---|---|
| fake-first 기본값 | live provider를 기본값으로 두면 비용/네트워크/secret에 검증이 묶임 | fake provider + in-memory repository 기본값 | API key 없는 full local check |
| PostgreSQL/pgvector opt-in | 로컬 기본 경로와 DB 통합 경로를 섞으면 실패 원인 분리가 어려움 | repository boundary 뒤 선택 integration으로 분리 | `RUN_POSTGRES_TESTS=1` 경로 |
| 공개 데모 | public demo가 live API 호출에 의존하면 배포/비용 리스크가 커짐 | static fixture build | `pnpm web:smoke:static`, Vercel URL |

## 빠른 실행

기본 로컬 검증은 API key와 Docker가 필요 없습니다.

```bash
pytest -q
python3 -m compileall -q app
pnpm check:package-manager
pnpm web:smoke
pnpm web:build
pnpm web:build:static
pnpm web:smoke:static
```

개발 서버:

```bash
python3 -m pip install -e ".[dev]"
uvicorn app.main:app --reload
corepack enable pnpm
pnpm install
pnpm web:dev
```

OIDC JWT provider는 명시적으로 켤 때만 사용합니다.

```bash
AUTH_CONTEXT_PROVIDER=oidc_jwt \
OIDC_ISSUER=https://idp.example.test/ \
OIDC_AUDIENCE=enterprise-policy-rag \
OIDC_HS256_SECRET=local-oidc-secret-with-32-bytes-min \
uvicorn app.main:app --reload
```

OpenAI retrieval/answer 경로는 provider를 명시적으로 선택할 때만 활성화됩니다.

```bash
EMBEDDING_PROVIDER=openai \
LLM_PROVIDER=openai \
OPENAI_API_KEY=<redacted> \
OPENAI_EMBEDDING_MODEL=text-embedding-3-small \
OPENAI_MODEL=gpt-4.1-mini \
OPENAI_TIMEOUT_SECONDS=20 \
uvicorn app.main:app --reload
```

## 검증

| 구분 | 명령/증거 | 비고 |
|---|---|---|
| 기본 backend | `pytest -q`, `python3 -m compileall -q app` | API key/Docker 불필요 |
| Frontend | `pnpm web:smoke`, `pnpm web:build` | live route smoke/build |
| Static demo | `pnpm web:build:static`, `pnpm web:smoke:static` | `/api` 호출 없는 public demo 기준 |
| Compose syntax | `docker compose config -q`, `docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q` | PostgreSQL 선택 경로 구성 확인 |
| PostgreSQL integration | `RUN_POSTGRES_TESTS=1 ... pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q` | Docker Postgres와 `psycopg` 필요 |
| OpenAI live smoke | `RUN_OPENAI_LIVE_SMOKE=1 python3 scripts/openai_live_smoke.py` | ignored `.env.local`, safe metadata만 출력 |
| Public demo | https://enterprise-policy-rag.vercel.app | static read-only fixture demo |

## 운영/배포

| 항목 | 내용 | 근거 |
|---|---|---|
| 기본 로컬 | fake provider + in-memory repository | API key/Docker 없는 검증 명령 |
| 선택 DB | PostgreSQL/pgvector compose와 integration tests | `docker-compose*.yml`, PostgreSQL tests |
| 선택 live provider | OpenAI Responses/Embeddings adapter | controlled live smoke |
| 공개 데모 | static read-only Vercel build | static smoke, Vercel production URL |

## 담당 범위

개인 포트폴리오 프로젝트로, 아래 역량을 증명하는 데 초점을 둡니다.

| 영역 | 증명하려는 역량 | 결과 |
|---|---|---|
| Retrieval backend | 권한 필터와 citation 후보 생성 | permission-aware retrieval 구현 |
| Provider boundary | fake/live provider 분리와 opt-in live smoke | 비용 없는 회귀와 controlled live path 공존 |
| 운영 관측 | query log, latency, token, cost estimate, eval | Operations API/UI 구현 |

## 프로젝트 구조

```text
app/                 FastAPI backend, provider/repository boundaries
tests/               backend unit/API/integration tests
web/                 React/Vite demo console
scripts/             package-manager, static smoke, OpenAI smoke helpers
docs/                design, runbooks, portfolio docs
docker-compose*.yml  PostgreSQL/pgvector optional runtime
```

## 문서 읽는 순서

| 순서 | 문서 | 목적 |
|---|---|---|
| 1 | [Portfolio One-Pager](docs/portfolio-one-pager.md) | 포트폴리오 요약과 경계 |
| 3 | [API and Data Model](docs/api-data-model.md) | API surface와 데이터 모델 |
| 5 | [Local Demo Runbook](docs/runbooks/local-demo.md) | API key 없는 실행 |
| 6 | [Static Demo Deploy Runbook](docs/runbooks/static-demo-deploy.md) | public read-only demo 배포 |
| 7 | [Production Hardening Checklist](docs/runbooks/production-hardening-checklist.md) | 운영 전환 전 남은 항목 |

## 범위 밖

- 온프레미스 설치형 배포
- 복잡한 multi-agent orchestration
- 대규모 문서 파서 제품화
- 처음부터 Kubernetes 운영
- 실제 과금/결제 기능
- OAuth redirect/session-cookie 운영 흐름
- 공개 데모/fixture 중심 정합성을 운영형 실시간 연동 완료로 주장하는 것
