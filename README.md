# Enterprise Policy RAG

[![CI](https://github.com/cyson21/enterprise-policy-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/cyson21/enterprise-policy-rag/actions/workflows/ci.yml)

사내 규정 문서를 검색해서 질문에 답하는 FastAPI RAG입니다. 볼 권한이 있는 문서만 검색하고, 근거 문서가 있을 때만 답변과 출처를 돌려줍니다. 백엔드 API부터 React 관리 화면까지 혼자 진행한 개인 프로젝트입니다.

[포트폴리오](https://cyson21.github.io/projects/enterprise-policy-rag/) · [데모](https://enterprise-policy-rag.vercel.app/) · [이력서](https://cyson21.github.io/downloads/resume.pdf)

## 기술 구성

기본 실행과 테스트는 Python, FastAPI, 메모리 저장소, 가짜 임베딩과 가짜 모델로 돌아갑니다. 외부 서비스 없이 항상 같은 결과가 나옵니다.

PostgreSQL, pgvector, OpenAI는 설정을 켜면 동작하도록 따로 분리해 두었습니다. 운영 환경에서 쓴 것은 아닙니다.

## 풀려던 문제

검색한 다음에 권한 없는 문서를 빼면, 민감한 문서가 이미 검색 결과까지는 올라온 뒤입니다. 근거가 없는 질문을 그대로 LLM에 넘기면 그럴듯한 답이 나오기도 합니다. 그래서 검색 후보를 만들기 전에 권한부터 적용하고, 근거가 부족하면 답하지 않고 거절하게 했습니다.

## 구조

```text
인증 정보 -> FastAPI
          -> 메모리 저장소 또는 PostgreSQL/pgvector
             -> 작업 공간·소유자·공개 범위·부서 SQL 선필터
             -> 벡터 유사도 정렬
          -> 근거 없음: 모델을 호출하지 않고 거절
          -> 근거 있음: 테스트 모델 또는 OpenAI -> 답변과 출처
          -> 질의 기록·지연시간·추정 토큰·비용·평가 이력
정적 데모 -> 포함된 고정 데이터만 사용하며 백엔드·DB·외부 모델과 분리
```

- 기본 실행은 메모리 저장소와 고정된 임베딩, 답변 모델을 써서 네트워크 없이도 같은 결과가 나옵니다.
- PostgreSQL에서는 벡터 유사도로 정렬하기 전에 SQL `WHERE` 절에서 권한 조건부터 겁니다.
- 인증 모드에서는 요청 본문에 적힌 권한 값을 믿지 않고, 로그인할 때 확인한 범위를 씁니다.

## 실패 상황별 결과

| 상황 | 결과 |
|---|---|
| 다른 작업 공간을 요청 | 로그인한 범위와 다르면 `403`으로 거절합니다 |
| 비공개 문서, 다른 부서 문서 | 검색 결과와 출처에 나오지 않습니다 |
| 관련 문서가 없음 | LLM을 부르지 않고 `insufficient_evidence`를 돌려줍니다 |
| 외부 모델 설정이 없음 | 테스트용 모델로 전체 흐름을 돌릴 수 있습니다 |
| 공개 데모 | FastAPI, PostgreSQL, OpenAI를 부르지 않고 고정 데이터만 보여 줍니다 |

## 확인한 방법

| 검증 | 확인한 내용 |
|---|---|
| 인증 | 로그인한 작업 공간을 우선하고, 본문의 권한 값은 무시하며, 범위가 다르면 거절 |
| 메모리 권한 검색 | 다른 작업 공간, 다른 부서, 비공개 문서가 결과에서 빠짐 |
| 근거 부족 | 출처 후보가 없으면 모델을 부르지 않고 거절 이유를 반환 |
| 모델 선택 | 기본 테스트 모델과 OpenAI Responses 설정을 분리 |
| 조회, 평가 | 검색 건수와 지연 시간을 기록하고, 고정 질문으로 권한과 출처가 그대로인지 확인 |
| PostgreSQL 권한 검색 | 실제 DB 통합 테스트에서 작업 공간, 작성자, 공개 범위, 부서 조건과 `ready` 상태가 SQL 후보 단계에서 걸리는지 확인 |
| 정적 화면 | 고정 데이터 빌드가 `/api` 없이 렌더링되는지 브라우저 테스트로 확인 |

## 대표 코드와 테스트

- 코드: [repository.py](app/repository.py) - 작업 공간, 작성자, 공개 범위, 부서 조건을 SQL에서 먼저 겁니다.
- 테스트: [test_retrieval_permissions.py](tests/test_retrieval_permissions.py) - 메모리 저장소에서 다른 작업 공간, 부서, 비공개 문서가 빠지는지 확인합니다.
- 실제 DB 테스트: [test_postgres_repository_integration.py](tests/test_postgres_repository_integration.py) - 볼 수 있는 문서, 없는 문서, 다른 작업 공간 문서, 색인 전 문서를 한 번에 넣고 결과를 확인합니다.

## 실행

Python 3.11 이상에서 기본 회귀를 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
python -m compileall -q app
```

웹은 API에 붙는 화면과 고정 데이터 화면을 따로 빌드합니다.

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm web:smoke
pnpm web:build
pnpm web:build:static
pnpm web:smoke:static
```

PostgreSQL과 인증 모드는 [로컬 실행](docs/runbooks/local-demo.md)의 선택 절차를 따릅니다.

```bash
RUN_OPENAI_LIVE_SMOKE=1 python3 scripts/openai_live_smoke.py
```

PostgreSQL repository 통합 테스트는 Docker Postgres가 떠 있고, 위 기본 회귀 절의 `python -m pip install -e ".[dev]"`로 base 패키지(FastAPI 포함)가 이미 설치된 Python 환경에 `psycopg`를 추가한 경우에만 실행합니다. `psycopg`만 설치하고 base를 건너뛰면 FastAPI가 없어 `create_app`이 Starlette fallback으로 빠지고, 테스트에서 `AttributeError: 'State' object has no attribute 'services'`가 납니다. Docker Desktop 대신 Colima를 쓰면 낮은 CPU/RAM으로 검증할 수 있습니다.

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew install colima
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
# 선행: 위 실행 절의 venv 활성화와 `python -m pip install -e ".[dev]"`
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
TEST_DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
```

다 쓰고 나면 Postgres와 Colima를 내립니다.

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

## 문서

| 문서 | 내용 |
|---|---|
| [ADR 0001](docs/adr/0001-fake-provider-first-retrieval-rag.md) | fake provider first와 Docker 선택 검증 결정 |
| [API and Data Model](docs/api-data-model.md) | 현재 API surface와 데이터 모델 초안 |
| [Local Demo Runbook](docs/runbooks/local-demo.md) | API key 없는 로컬 실행과 검증 |
| [Static Demo Deploy Runbook](docs/runbooks/static-demo-deploy.md) | 백엔드 없는 public read-only 데모 배포 절차 |
| [Production Hardening Checklist](docs/runbooks/production-hardening-checklist.md) | 실제 production SaaS 전환 전 필수 보강 항목 |
| [Portfolio One-Pager](docs/portfolio-one-pager.md) | 포트폴리오 요약 |
| [Architecture SVG](docs/assets/architecture.svg) | 아키텍처 다이어그램 |

## 해 보지 않은 것

- `demo` 인증은 요청에 적힌 권한을 그대로 믿습니다. `trusted_headers`는 앞단 서버가 헤더를 제대로 관리한다는 전제가 필요합니다.
- 공개 데모는 고정 데이터만 보여 줍니다. FastAPI, PostgreSQL, pgvector, OpenAI를 실제로 돌린 결과가 아닙니다.
- 권한은 애플리케이션 SQL로 거릅니다. PostgreSQL RLS는 쓰지 않았습니다.
- 적은 데이터로 pgvector 정렬이 되는지만 봤습니다. IVFFlat 인덱스를 타는지, 문서가 많을 때 얼마나 빠른지는 확인하지 않았습니다.
- 토큰 수는 글자 4개를 1토큰으로 어림잡고 고정 단가를 곱한 값이라 실제 청구액과 다릅니다.
- 고정 질문 평가는 권한, 검색, 출처가 그대로인지 보는 용도이지 RAG 품질 평가가 아닙니다.
- 대량 문서 수집, 사내 IdP 연동, 대규모 부하, 자동 확장, 다중 리전은 해 보지 않았습니다.

## 관련 프로젝트와 공개 자료

이 저장소의 코드·실행·테스트는 이 저장소에서 관리합니다. [웹 포트폴리오의 프로젝트 설명](https://cyson21.github.io/projects/enterprise-policy-rag/)과 [공개 자료 안내](https://github.com/cyson21/portfolio-hub)는 외부에서 구현 근거를 찾는 진입점입니다.

- 관련 주제: [ai-gateway](https://github.com/cyson21/ai-gateway) — LLM 호출 인증·비용·캐시·폴백 정책 비교.
- 최신 제출 파일: [이력서 PDF](https://cyson21.github.io/downloads/resume.pdf) · [경력기술서 PDF](https://cyson21.github.io/downloads/career-description.pdf).

위 관련 저장소는 별도로 실행하는 개인 프로젝트입니다. 서로의 서비스를 순서대로 띄우거나 실제 API·메시지로 연결한 E2E 체인이 구현됐다는 의미는 아닙니다. 구현·검증 범위가 바뀌면 이 README와 웹 프로젝트 문안을 함께 확인합니다.
