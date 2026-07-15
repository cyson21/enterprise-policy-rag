# Enterprise Policy RAG

사용자·부서·workspace 권한으로 정책 문서 검색 후보를 제한하고, 근거가 있을 때만 답변과 citation을 생성하는 FastAPI 프로젝트입니다. [웹 사례](https://cyson21.github.io/projects/enterprise-policy-rag/) · [공개 데모](https://enterprise-policy-rag.vercel.app/)

## 포트폴리오 링크

- [웹 사례](https://cyson21.github.io/projects/enterprise-policy-rag/) · [공개 데모](https://enterprise-policy-rag.vercel.app/) · [전체 포트폴리오 PDF](https://github.com/cyson21/portfolio-hub/releases/download/latest/portfolio-complete.pdf) · [최신 이력서](https://github.com/cyson21/portfolio-hub/releases/download/latest/resume.pdf)

## 문제

검색 후 애플리케이션에서 권한 없는 문서를 제거하면 이미 민감한 후보가 검색 계층을 통과합니다. 또한 근거가 없는 질문도 LLM에 전달하면 그럴듯한 답변이 생성됩니다. 권한 범위를 retrieval 전에 적용하고 evidence 부족을 명시적으로 거절해야 합니다.

## 설계

```text
Auth context -> FastAPI
             -> memory repository or PostgreSQL/pgvector
                -> workspace/owner/public/department SQL prefilter
                -> vector ranking
             -> no evidence: reject without provider call
             -> evidence: fake or OpenAI provider -> answer + citations
             -> query log + latency + estimated token/cost + eval history
Static demo  -> bundled fixtures only; backend/database/provider와 분리
```

- 기본 실행은 메모리 저장소와 결정론적 embedding·LLM을 사용해 네트워크 없이 회귀를 재현합니다.
- PostgreSQL 경로는 vector 정렬 전에 접근 범위를 SQL `WHERE` 절로 제한합니다.
- 인증 강제 모드는 요청 본문의 권한 값 대신 검증된 session scope를 사용합니다.

## 실패 조건

| 조건 | 보호 규칙 |
|---|---|
| 다른 workspace 요청 | session 범위와 다르면 `403`으로 거절해야 함 |
| 비공개·타 부서 문서 | retrieval 후보와 citation에 포함되지 않아야 함 |
| 검색 근거 없음 | LLM을 호출하지 않고 `insufficient_evidence`를 반환해야 함 |
| 외부 provider 미설정 | fake provider 경로로 재현 가능해야 함 |
| 정적 공개 데모 | FastAPI·PostgreSQL·OpenAI 호출 없이 fixture만 렌더링해야 함 |

## 검증 결과

| 검증 | 확인 결과 |
|---|---|
| 인증 gate | session workspace 우선, 본문 권한 값 무시, workspace 불일치 거절을 확인 |
| 메모리 권한 검색 | 다른 workspace·부서·비공개 문서를 retrieval 결과에서 제외 |
| 근거 부족 | citation 후보가 없으면 provider를 호출하지 않고 거절 사유 반환 |
| provider 선택 | 기본 fake provider와 명시적 OpenAI Responses 구성을 분리 |
| 조회·평가 | 지연, 검색 수, 추정 token·cost와 3개 고정 질문의 적중·citation 결과를 기록 |
| 정적 웹 | fixture build가 `/api` 의존 없이 렌더링되는지 browser smoke로 확인 |

PostgreSQL 권한 선필터 통합 테스트는 실제 PostgreSQL 환경에서 별도로 실행하며, 위 결과에는 메모리 저장소에서 재현한 권한 격리만 포함합니다.

### 재현 가능한 검증 리포트

GitHub Actions는 `pgvector/pgvector:pg16` 서비스에 프로젝트 스키마를 적용하고 `RUN_POSTGRES_TESTS=1`로 전체 pytest를 실행합니다. pytest JUnit XML과 이를 Python 표준 라이브러리만으로 변환한 `portfolio-evidence.json`을 함께 artifact로 보관하며, JSON에는 schema version, 프로젝트, 정확한 Git commit, UTC 생성 시각, 검증 범위, 전체·suite별 테스트 집계가 기록됩니다. OpenAI live smoke는 기존 `RUN_OPENAI_LIVE_SMOKE=1` opt-in 조건을 유지하므로 실제 키가 없는 CI에서는 외부 요청을 만들지 않습니다.

로컬 비DB 결과도 같은 형식으로 생성할 수 있습니다.

```bash
mkdir -p artifacts
RUN_POSTGRES_TESTS=0 RUN_OPENAI_LIVE_SMOKE=0 pytest -q --junitxml=artifacts/pytest.xml
python scripts/portfolio_evidence.py artifacts/pytest.xml \
  --output artifacts/portfolio-evidence.json \
  --scope "local pytest; PostgreSQL integration excluded; OpenAI live smoke opt-in"
```

## 대표 코드와 테스트

- 코드: [repository.py](app/repository.py) - workspace, owner, public 범위, 부서 교집합을 SQL 선필터에 적용합니다.
- 테스트: [test_retrieval_permissions.py](tests/test_retrieval_permissions.py) - 메모리 경로에서 workspace·부서·비공개 문서 격리를 검증합니다.

## 실행

Python 3.11 이상에서 기본 회귀를 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
python -m compileall -q app
```

웹은 동적 build와 정적 fixture build를 각각 검증합니다.

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm web:smoke
pnpm web:build
pnpm web:build:static
pnpm web:smoke:static
```

PostgreSQL과 인증 모드는 [로컬 실행](docs/runbooks/local-demo.md)의 선택 절차를 따릅니다.

## 제한 사항

- `demo` 인증은 요청 권한을 신뢰하며 `trusted_headers`는 외부 proxy가 헤더를 안전하게 관리한다는 전제가 필요합니다.
- 공개 데모는 정적 fixture이며 FastAPI, PostgreSQL, pgvector, OpenAI의 실행 증거가 아닙니다.
- token은 4글자당 1개로 근사하고 정적 단가를 적용하므로 실제 provider usage나 청구액이 아닙니다.
- 3개 고정 질문 평가는 권한·검색·citation 회귀용이며 일반적인 RAG 품질 benchmark가 아닙니다.
- 대규모 문서 ingest, production IdP 연동, 운영 부하, 자동 확장과 multi-region은 검증하지 않았습니다.
