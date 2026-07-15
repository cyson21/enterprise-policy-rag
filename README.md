# Enterprise Policy RAG

Enterprise Policy RAG는 사내 정책 문서를 사용자·부서·공개 범위에 따라 검색하고, 검색 근거를 포함한 답변과 조회 기록을 제공하는 FastAPI 백엔드 프로젝트입니다. 기본 경로는 고정 결과를 반환하는 테스트용 임베딩·LLM과 메모리 저장소로 동작하며, PostgreSQL/pgvector와 OpenAI 연동은 명시적으로 선택한 경우에만 사용합니다. 기본 데모 모드는 인증을 강제하지 않으므로 운영 인증이 아니라 권한 검색 흐름을 재현하기 위한 환경입니다.

## 포트폴리오 링크

- [웹 사례](https://cyson21.github.io/projects/enterprise-policy-rag/) · [공개 데모](https://enterprise-policy-rag.vercel.app/) · [전체 포트폴리오 PDF](https://github.com/cyson21/portfolio-hub/releases/download/latest/portfolio-complete.pdf) · [최신 이력서](https://github.com/cyson21/portfolio-hub/releases/download/latest/resume.pdf)

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 문제 | RAG 검색 후보에 접근 불가능한 문서가 포함되거나, 근거 없이 답변이 생성되는 상황을 제어 |
| 핵심 구현 | 권한 범위 검색, PostgreSQL SQL 선필터, 근거 부족 시 답변 거절, 인용 정보, 조회 기록, 고정 평가 데이터 |
| 기본 실행 | Python 3.11 이상, 메모리 저장소, 테스트용 임베딩·LLM, API key 불필요 |
| 선택 실행 | PostgreSQL 16 + pgvector, OpenAI Responses·Embeddings API, OIDC JWT 또는 신뢰 헤더 인증 |
| 검증 방식 | `pytest`, PostgreSQL 통합 테스트, 프런트엔드 빌드·스모크 검사, 선택형 OpenAI 스모크 검사 |
| 공개 데모 경계 | 정적 예제 데이터만 렌더링하며 FastAPI, PostgreSQL, OpenAI를 호출하지 않음 |

## 아키텍처

```text
클라이언트
  -> 인증 컨텍스트
     - demo: 고정 페르소나 / 비강제 인증
     - trusted_headers: 외부 인증 계층이 전달한 헤더
     - oidc_jwt: issuer, audience, 서명 검증
  -> FastAPI API
  -> 문서 청킹과 임베딩
  -> 저장소
     - 기본: 메모리
     - 선택: PostgreSQL/pgvector, SQL 권한 선필터
  -> 검색 결과와 인용 후보
  -> 근거 없음: 제공자 호출 없이 답변 거절
  -> 근거 있음: 테스트용 또는 OpenAI LLM 제공자
  -> 답변, 인용, 조회 기록, 지연·토큰·비용 추정치, 평가 이력

정적 웹 데모
  -> 빌드에 포함된 fixture만 사용
  -> FastAPI / PostgreSQL / OpenAI와 분리
```

저장소와 외부 제공자 인터페이스를 분리해 기본 회귀 테스트는 네트워크와 Docker 없이 실행합니다. PostgreSQL 경로에서는 벡터 유사도 정렬 전에 workspace, 소유자, 공개 범위, 부서 교집합을 SQL `WHERE` 절로 제한합니다.

## 핵심 설계 판단

### 1. 검색 후보 단계에서 권한 범위 제한

애플리케이션에서 검색 결과를 받은 뒤 제거하는 대신, PostgreSQL 조회 단계에서 접근 가능한 문서만 벡터 정렬 대상으로 만듭니다. 인증 강제 모드에서는 요청 본문의 workspace·사용자·부서 값을 사용하지 않고 검증된 세션 값으로 치환합니다.

- 구현: [PostgreSQL 저장소](app/repository.py), [인증 범위 적용](app/main.py), [인증 컨텍스트](app/auth.py)
- 검증: [PostgreSQL 저장소 통합 테스트](tests/test_postgres_repository_integration.py), [권한 검색 테스트](tests/test_retrieval_permissions.py), [인증 게이트 테스트](tests/test_auth_gate.py). PostgreSQL 통합 테스트는 접근 가능한 문서 조회를 확인하며, 여러 권한 범위의 문서를 한 번에 저장한 뒤 SQL 결과에서 제외하는 부정 사례는 아직 직접 검증하지 않습니다.

### 2. 근거가 없으면 생성 제공자를 호출하지 않음

검색 결과에서 인용 후보를 만들 수 없으면 `insufficient_evidence`를 반환하고 답변 생성을 중단합니다. 근거가 있으면 문서 제목, 원문 위치, 인용문, 검색 점수를 답변과 함께 반환합니다.

- 구현: [답변 서비스](app/answer.py), [검색 서비스](app/retrieval.py)
- 검증: [답변 API 테스트](tests/test_answer_api.py), [검색 API 테스트](tests/test_api_retrieval.py)

### 3. 외부 연동을 선택형 경로로 분리

기본 실행은 테스트용 임베딩·LLM과 메모리 저장소를 사용합니다. `DATABASE_URL`, `EMBEDDING_PROVIDER=openai`, `LLM_PROVIDER=openai`가 지정된 경우에만 PostgreSQL 또는 OpenAI 어댑터를 선택합니다.

- 구현: [런타임 구성](app/runtime.py), [제공자 어댑터](app/providers.py)
- 검증: [저장소 선택 테스트](tests/test_runtime_storage.py), [제공자 선택 테스트](tests/test_provider_selection.py), [OpenAI 스모크 도구 테스트](tests/test_openai_live_smoke.py)

### 4. 운영 수치는 측정값과 추정값을 구분

지연 시간과 검색 건수는 실행 중 관찰한 값입니다. 토큰 수는 입력·출력 문자열 길이를 합산해 **4글자당 1토큰**으로 근사하고, 예상 비용은 이 추정 토큰 수에 코드에 정의한 모델별 정적 단가를 적용합니다. OpenAI 응답의 실제 usage나 청구 금액을 나타내지 않습니다.

- 구현: [토큰·비용 추정](app/answer.py), [모델별 정적 단가](app/providers.py), [조회 기록](app/query_logs.py)
- 검증: [운영 API 테스트](tests/test_operations_api.py), [조회 기록 테스트](tests/test_query_logs.py)

### 5. 평가는 고정된 소규모 데이터로 재현

평가 기능은 저장소에 포함된 3개 질문과 기대 문서 ID를 사용해 검색 적중 여부와 인용 포함 여부를 계산합니다. 일반적인 RAG 품질 벤치마크가 아니라 권한·검색·인용 경로의 회귀 검사용입니다.

- 구현: [고정 평가 데이터와 실행기](app/evaluation.py), [평가 이력 저장](app/eval_runs.py)
- 검증: [평가 API 테스트](tests/test_eval_api.py), [평가 이력 테스트](tests/test_eval_runs.py)

## 검증 시나리오

| 시나리오 | 관찰 기준 | 코드·테스트 근거 |
|---|---|---|
| 인증 우회 방지 | 인증 강제 모드에서 요청 본문의 권한 값보다 JWT 세션 범위를 우선 | [main.py](app/main.py), [test_auth_gate.py](tests/test_auth_gate.py) |
| workspace 격리 | 세션과 다른 workspace 조회를 `403`으로 거절 | [auth.py](app/auth.py), [test_auth_gate.py](tests/test_auth_gate.py) |
| 권한 범위 제한 | 메모리 경로에서 다른 workspace·부서·비공개 문서를 제외하고, PostgreSQL 경로에서 SQL 선필터 조회를 실행 | [repository.py](app/repository.py), [test_retrieval_permissions.py](tests/test_retrieval_permissions.py), [test_postgres_repository_integration.py](tests/test_postgres_repository_integration.py) |
| 근거 부족 답변 거절 | 인용 후보가 없으면 LLM 제공자 호출 없이 거절 사유 반환 | [answer.py](app/answer.py), [test_answer_api.py](tests/test_answer_api.py) |
| 제공자 선택 | 기본 테스트용 제공자와 명시적 OpenAI 제공자 구성을 분리 | [providers.py](app/providers.py), [test_provider_selection.py](tests/test_provider_selection.py) |
| 조회 이력 | 지연 시간, 검색 결과, 추정 토큰·비용을 조회 상세와 집계 API에 기록 | [operations.py](app/operations.py), [test_operations_api.py](tests/test_operations_api.py) |
| 고정 평가 | 3개 고정 질문으로 검색 적중과 인용 포함 여부를 반복 계산 | [evaluation.py](app/evaluation.py), [test_eval_api.py](tests/test_eval_api.py) |
| 정적 공개 화면 | 정적 빌드가 fixture를 사용하며 `/api` 의존 없이 렌더링 | [데모 모드 설정](web/src/config/demoMode.ts), [정적 데모 검사](scripts/smoke-static-demo.mjs) |

## 재현 방법

### 기본 백엔드: Python 3.11 이상

API key와 Docker가 필요하지 않습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
python -m compileall -q app
```

로컬 API 실행:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

기본 데모 모드는 인증을 강제하지 않고 요청의 권한 컨텍스트를 신뢰합니다. 인증 범위까지 확인하려면 [로컬 실행 문서](docs/runbooks/local-demo.md)의 OIDC 또는 신뢰 헤더 설정을 사용합니다.

### 웹 콘솔: Node.js 20.19 이상, pnpm 11.1.3

동적 API 빌드와 정적 fixture 빌드는 같은 `web/dist`를 사용하므로 아래 두 경로를 순서대로 각각 검증합니다. 정적 스모크 검사에는 Chrome 또는 Chromium이 필요하며 자동 탐지가 실패하면 `CHROME_PATH`를 지정합니다.

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check:package-manager
pnpm web:smoke
pnpm web:build
```

```bash
pnpm web:build:static
pnpm web:smoke:static
```

### PostgreSQL/pgvector 선택 검증

```bash
(
  set -e
  trap 'docker compose down' EXIT
  docker compose config -q
  docker compose up -d --wait postgres
  export DATABASE_URL='postgresql://rag_app:rag_app_password@localhost:5432/enterprise_policy_rag'
  RUN_POSTGRES_TESTS=1 pytest \
    tests/test_postgres_repository_integration.py \
    tests/test_postgres_runtime_integration.py -q
)
```

이 경로는 호스트 포트 `5432`가 비어 있어야 하며, [PostgreSQL 초기 스키마](infra/postgres/init/001_schema.sql)를 적용한 실제 저장소 동작을 확인합니다.

### OpenAI 선택 스모크 검사

실제 네트워크 요청과 비용이 발생할 수 있으므로 기본 검증에는 포함하지 않습니다.

```bash
RUN_OPENAI_LIVE_SMOKE=1 \
OPENAI_API_KEY='<redacted>' \
OPENAI_MODEL='gpt-4.1-mini' \
python3 scripts/openai_live_smoke.py
```

이 스모크 검사는 테스트용 임베딩으로 검색한 근거를 OpenAI Responses 제공자에 전달하는 답변 경로만 확인합니다. OpenAI Embeddings API는 호출하지 않습니다.

## 담당 범위

개인 프로젝트로 다음 영역을 직접 설계·구현·테스트했습니다.

- FastAPI 문서·검색·답변·운영 지표 API
- 메모리 및 PostgreSQL/pgvector 저장소 분리
- 권한 검색과 인증 세션 범위 적용
- 테스트용 및 OpenAI 제공자 어댑터 분리
- 답변 거절, 인용 정보, 조회 기록, 고정 평가 기능
- React/Vite 웹 콘솔과 정적 fixture 데모 검증

## 제한 사항

- `demo` 모드는 요청 권한 정보를 신뢰하고, `trusted_headers` 모드는 외부 인증 프록시가 헤더를 안전하게 생성·정리한다는 전제가 필요합니다.
- 정적 화면, PostgreSQL, OpenAI Responses는 서로 분리된 선택 검증이며 기본 회귀 테스트가 이 외부 경로를 항상 실행하지는 않습니다.
- 토큰·비용 추정과 3개 고정 평가 사례는 회귀 비교용입니다. 실제 청구액이나 일반적인 RAG 품질을 대표하지 않습니다.
- PostgreSQL 경로에는 여러 권한 범위의 문서를 함께 저장한 뒤 SQL 결과에서 제외되는지 확인하는 부정 통합 사례가 아직 없습니다.
- 대규모 문서 파싱, 멀티 리전, 자동 확장, 운영 모니터링은 구현·검증 범위에 포함하지 않습니다.

## 관련 문서

| 문서 | 내용 |
|---|---|
| [ADR-0001: 테스트용 제공자 우선](docs/adr/0001-fake-provider-first-retrieval-rag.md) | 외부 비용 없이 검색·답변 흐름을 먼저 검증한 이유 |
| [API와 데이터 모델](docs/api-data-model.md) | 엔드포인트와 주요 데이터 구조 |
| [로컬 실행](docs/runbooks/local-demo.md) | 기본 데모와 인증 모드 실행 절차 |
| [정적 데모 배포](docs/runbooks/static-demo-deploy.md) | fixture 기반 읽기 전용 빌드와 배포 경계 |
