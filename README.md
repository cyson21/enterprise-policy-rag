# Enterprise Policy RAG

Enterprise Policy RAG는 기업 내부 정책, 업무 매뉴얼, 보안 지침 문서를 권한에 맞게 검색하고, 답변 근거와 운영 지표를 제공하는 RAG 백엔드 프로젝트입니다. 기본 실행은 테스트용 provider와 메모리 저장소를 사용하며, PostgreSQL/pgvector와 OpenAI 연동은 필요할 때만 켭니다.

## 프로젝트 요약

| 항목 | 내용 |
|---|---|
| 해결하려는 문제 | 사내 문서 RAG에서는 답변 품질뿐 아니라 권한 필터, 출처 표시, 평가, 지연 시간과 비용 기록이 필요함 |
| 주요 기술 | FastAPI, PostgreSQL/pgvector, provider 분리, 권한 기반 검색, 평가·운영 지표, React 데모 |
| 주요 기능 | 권한 기반 검색, 출처 표시와 답변 거절, 선택형 provider, 검색 기록 |
| 확인 방법 | `pytest`, 프런트엔드 스모크 테스트와 빌드, 정적 공개 데모, PostgreSQL 통합 테스트, 선택형 OpenAI 스모크 테스트 |
| 빠른 실행 | API key 없이 테스트용 provider와 메모리 저장소로 로컬 실행 가능 |
| 제한 사항 | 공개 데모는 정적 예제 데이터를 사용하며, 운영형 인증·실시간 OpenAI·SaaS 운영은 별도 보완이 필요함 |

## 주요 내용

| 주제 | 관련 문서와 코드 | 설명 |
|---|---|---|
| 권한 기반 검색 | [retrieval 구현](app/retrieval.py), [권한 테스트](tests/test_retrieval_permissions.py) | 접근할 수 없는 문서가 검색 후보에 섞이지 않는지 확인 |
| 출처 표시와 답변 거절 | [answer 구현](app/answer.py), [Answer API 테스트](tests/test_answer_api.py) | 검색 근거가 있을 때만 답변하고 근거가 부족하면 거절하는 흐름 |
| 공개 데모 | [정적 데모 테스트](scripts/smoke-static-demo.mjs), [배포 문서](docs/runbooks/static-demo-deploy.md) | 공개 화면이 실시간 API나 API key 없이 동작하는지 확인 |

## 주요 코드와 테스트

| 구분 | 코드 또는 기능 | 테스트 또는 실행 방법 |
|---|---|---|
| 권한 기반 검색 | [retrieval.py](app/retrieval.py) | [test_retrieval_permissions.py](tests/test_retrieval_permissions.py), [test_retrieval_metadata_api.py](tests/test_retrieval_metadata_api.py) |
| 출처 표시와 답변 거절 | [answer.py](app/answer.py) | [test_answer_api.py](tests/test_answer_api.py) |
| 테스트용 provider와 실제 provider 분리 | [ADR-0001](docs/adr/0001-fake-provider-first-retrieval-rag.md) | `pytest -q`, 선택형 `RUN_OPENAI_LIVE_SMOKE=1 python3 scripts/openai_live_smoke.py` |

## 실행 환경

| 구분 | 준비 사항 | 확인할 내용 |
|---|---|---|
| 기본 로컬 | Python, pnpm | 테스트용 embedding·LLM과 메모리 저장소로 API·UI 테스트 |
| PostgreSQL 연동 | Docker PostgreSQL/pgvector | 실제 DB 저장소와 API 통합 테스트 |
| OpenAI 연동 | API key와 환경 변수 | OpenAI adapter 스모크 테스트이며 공개 데모나 기본 CI에는 포함하지 않음 |

## 구현 결과

| 구현 내용 | 결과 | 확인 방법 |
|---|---|---|
| 권한 기반 검색 | workspace/user/department/visibility 필터로 private 문서 혼입 방지 | retrieval/API tests |
| 근거 기반 답변 | citation 후보와 근거 부족 refusal을 API와 UI에서 확인 | answer tests, Search Console |
| 외부 비용 없는 기본 테스트 | 테스트용 embedding·LLM과 메모리 저장소로 핵심 흐름 확인 | `pytest`, 프런트엔드 스모크 테스트와 빌드 |
| 선택형 외부 연동 | OpenAI와 PostgreSQL은 환경 변수로만 활성화 | OpenAI 스모크 테스트, PostgreSQL 통합 테스트 |

## 프로젝트 배경

RAG를 단순 챗봇 기능으로 만들면 검색 권한, 답변 근거, 운영 지표 같은 백엔드 문제가 드러나지 않습니다. 이 프로젝트는 “누가 어떤 문서를 볼 수 있는가”, “답변 근거가 무엇인가”, “검색 품질과 비용을 어떻게 기록하는가”에 집중했습니다.

## 주요 설계

| 설계 | 선택 이유 | 구현과 테스트 |
|---|---|---|
| 검색 전 권한 필터 | 생성 모델을 호출하기 전에 접근 가능한 chunk만 후보로 만들어야 함 | 권한 필터 테스트 |
| 테스트용 provider 기본값 | API key, 비용, 네트워크 없이 반복 테스트하기 위함 | 테스트용 embedding·LLM, `pytest` |
| 출처 표시와 답변 거절 | 근거 없는 답변을 줄이고 판단 근거를 남기기 위함 | Answer API 테스트, Search Console |
| 운영 지표 | 지연 시간, token, 예상 비용, 검색 품질을 기록하기 위함 | metrics·trend·detail API |

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

| 영역 | 구현 내용 | 확인 방법 |
|---|---|---|
| Document API | 문서 등록, 조회, 수정, 삭제, chunk preview | FastAPI tests |
| Retrieval | workspace/user/department/visibility 기반 권한 필터, score/top-k 제어 | retrieval tests, Search Console |
| Answer | fake LLM 답변, 근거 부족 refusal, citation 반환 | answer API tests |
| Provider 분리 | 테스트용 embedding·LLM 기본값, 선택형 OpenAI Responses·Embeddings adapter | 선택형 OpenAI 스모크 테스트 |
| Persistence | in-memory 기본, PostgreSQL/pgvector 선택 repository | PostgreSQL integration smoke |
| 인증 | 데모 사용자 정보, trusted header, OIDC JWT adapter, 세션 기반 검색·답변 | 인증·OIDC 테스트 |
| 운영 지표 | 검색 기록, 지연 시간, token, 예상 비용, 검색 근거, 추이·상세 정보 | Operations API·UI |
| 데모 UI | Search Console, Knowledge Library, Retrieval Lab, Operations | 프런트엔드 스모크 테스트·정적 빌드 |
| 공개 데모 | `VITE_DEMO_MODE=static` 읽기 전용 테스트용 provider 빌드 | Vercel 배포 주소 |

## 대표 시나리오

| 시나리오 | 확인 내용 | 결과 |
|---|---|---|
| 권한 기반 검색 | 다른 workspace/department/private 문서가 섞이지 않는지 | permission filter tests |
| Citation 답변 | 답변이 retrieval 근거와 함께 반환되는지 | answer API, Search Console |
| 근거 부족 refusal | 검색 근거가 부족할 때 답변을 꾸미지 않는지 | fake answer tests |
| 검색 기록 | 지연 시간, token, 예상 비용, 검색된 chunk가 남는지 | metrics·trend·detail API |
| 평가 도구 | 기준 질문으로 검색 적중과 출처 포함 비율을 계산하는지 | 평가 API와 테스트 |
| 공개 정적 데모 | 공개 데모가 `/api` 없이 렌더링되는지 | `pnpm web:smoke:static`, Vercel 주소 |
| OpenAI 선택 테스트 | 실제 OpenAI 경로가 명시적으로 선택했을 때만 켜지는지 | `RUN_OPENAI_LIVE_SMOKE=1` 수동 테스트 |

## 기술 선택과 문제 해결

| 주제 | 고민한 점 | 적용 내용 | 확인 방법과 남은 과제 |
|---|---|---|---|
| 테스트용 provider 기본값 | 실제 provider를 기본값으로 두면 테스트가 비용·네트워크·시크릿에 의존함 | 테스트용 provider와 메모리 저장소를 기본값으로 사용 | API key 없는 로컬 테스트 |
| PostgreSQL/pgvector 선택 실행 | 로컬 기본 경로와 DB 통합 경로를 섞으면 실패 원인 파악이 어려움 | 저장소 구현을 분리하고 DB 통합 테스트는 별도로 실행 | `RUN_POSTGRES_TESTS=1` |
| 공개 데모 | 공개 화면이 실시간 API에 의존하면 배포와 비용 부담이 커짐 | 정적 예제 데이터로 읽기 전용 빌드 | `pnpm web:smoke:static`, Vercel 주소 |

## 빠른 실행

기본 로컬 테스트에는 API key와 Docker가 필요하지 않습니다.

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

## 테스트

| 구분 | 명령 또는 결과 | 설명 |
|---|---|---|
| 기본 백엔드 | `pytest -q`, `python3 -m compileall -q app` | API key와 Docker 불필요 |
| 프런트엔드 | `pnpm web:smoke`, `pnpm web:build` | API 연결 경로 스모크 테스트와 빌드 |
| 정적 데모 | `pnpm web:build:static`, `pnpm web:smoke:static` | `/api` 호출이 없는 공개 데모 |
| Compose 설정 | `docker compose config -q`, `docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q` | PostgreSQL 선택 경로의 설정 확인 |
| PostgreSQL 통합 | `RUN_POSTGRES_TESTS=1 ... pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q` | Docker PostgreSQL과 `psycopg` 필요 |
| OpenAI 스모크 테스트 | `RUN_OPENAI_LIVE_SMOKE=1 python3 scripts/openai_live_smoke.py` | Git에서 제외된 `.env.local`을 사용하고 민감하지 않은 정보만 출력 |
| 공개 데모 | https://enterprise-policy-rag.vercel.app | 정적 예제 데이터를 사용하는 읽기 전용 데모 |

## 운영/배포

| 항목 | 내용 | 확인 방법 |
|---|---|---|
| 기본 로컬 | 테스트용 provider와 메모리 저장소 | API key와 Docker가 필요 없는 테스트 명령 |
| PostgreSQL 연동 | PostgreSQL/pgvector Compose와 통합 테스트 | `docker-compose*.yml`, PostgreSQL 테스트 |
| OpenAI 연동 | OpenAI Responses·Embeddings adapter | 선택형 OpenAI 스모크 테스트 |
| 공개 데모 | 읽기 전용 Vercel 빌드 | 정적 데모 테스트, Vercel 배포 주소 |

## 담당 범위

개인 프로젝트이며, 직접 구현하고 테스트한 범위는 다음과 같습니다.

| 분야 | 구현 내용 | 확인 방법 |
|---|---|---|
| 검색 백엔드 | 권한 필터와 출처 후보 생성 | 권한 기반 검색 테스트 |
| Provider 분리 | 테스트용 provider와 실제 provider를 분리 | 기본 테스트와 선택형 OpenAI 테스트 |
| 운영 지표 | 검색 기록, 지연 시간, token, 예상 비용, 평가 | Operations API·UI |

## 프로젝트 구조

```text
app/                 FastAPI 백엔드, provider와 저장소 구현 분리
tests/               backend unit/API/integration tests
web/                 React/Vite demo console
scripts/             package manager 점검, 정적 데모·OpenAI 테스트 도구
docs/                design, runbooks, portfolio docs
docker-compose*.yml  선택형 PostgreSQL/pgvector 실행 환경
```

## 참고 문서

| 순서 | 문서 | 내용 |
|---|---|---|
| 1 | [Portfolio One-Pager](docs/portfolio-one-pager.md) | 프로젝트 요약과 제한 사항 |
| 2 | [API and Data Model](docs/api-data-model.md) | API 목록과 데이터 모델 |
| 3 | [Local Demo Runbook](docs/runbooks/local-demo.md) | API key 없는 실행 |
| 4 | [Static Demo Deploy Runbook](docs/runbooks/static-demo-deploy.md) | 읽기 전용 공개 데모 배포 |
| 5 | [운영 보완 체크리스트](docs/runbooks/production-hardening-checklist.md) | 운영 전환 전에 보완할 항목 |

## 제한 사항

- 온프레미스 설치형 배포
- 복잡한 멀티 에이전트 구성
- 대규모 문서 파서 제품화
- 처음부터 Kubernetes 운영
- 실제 과금/결제 기능
- OAuth redirect/session-cookie 운영 흐름
- 정적 예제 데이터로 만든 공개 데모를 운영형 실시간 연동으로 설명하지 않음
