# Enterprise Policy RAG

[![CI](https://github.com/cyson21/enterprise-policy-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/cyson21/enterprise-policy-rag/actions/workflows/ci.yml)

사용자가 열람할 수 있는 정책 문서만 검색하고, 근거가 있을 때만 답변과 출처를 제공하는 FastAPI 프로젝트입니다.

개인 프로젝트로 권한 기반 검색·답변 API, PostgreSQL/pgvector 저장 경로, 외부 모델 연동 경계와 운영 화면을 직접 설계·구현했습니다.

[웹 사례](https://cyson21.github.io/projects/enterprise-policy-rag/) · [공개 데모](https://enterprise-policy-rag.vercel.app/) · [전체 포트폴리오 PDF](https://github.com/cyson21/portfolio-hub/releases/download/latest/portfolio-complete.pdf) · [최신 이력서](https://github.com/cyson21/portfolio-hub/releases/download/latest/resume.pdf)

## 문제

검색 후 애플리케이션에서 권한 없는 문서를 제거하면 이미 민감한 후보가 검색 계층을 통과합니다. 또한 근거가 없는 질문도 LLM에 전달하면 그럴듯한 답변이 생성됩니다. 검색 후보를 만들기 전에 권한 범위를 적용하고 근거가 부족하면 답변을 명시적으로 거절해야 합니다.

## 설계

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

- 기본 실행은 메모리 저장소와 고정된 임베딩·답변 모델을 사용해 네트워크 없이 같은 결과를 재현합니다.
- PostgreSQL 경로는 벡터 유사도 정렬 전에 접근 범위를 SQL `WHERE` 절로 제한합니다.
- 인증 강제 모드는 요청 본문의 권한 값 대신 로그인 과정에서 확인한 접근 범위를 사용합니다.

## 실패 조건

| 조건 | 보호 규칙 |
|---|---|
| 다른 작업 공간 요청 | 로그인 범위와 다르면 `403`으로 거절해야 함 |
| 비공개·타 부서 문서 | 검색 후보와 출처에 포함되지 않아야 함 |
| 검색 근거 없음 | LLM을 호출하지 않고 `insufficient_evidence`를 반환해야 함 |
| 외부 모델 미설정 | 테스트용 모델로 핵심 흐름을 확인할 수 있어야 함 |
| 정적 공개 데모 | FastAPI·PostgreSQL·OpenAI 호출 없이 고정 데이터만 표시해야 함 |

## 검증 결과

| 검증 | 확인 결과 |
|---|---|
| 인증 경계 | 로그인한 작업 공간을 우선하고 본문의 권한 값은 무시하며 범위 불일치를 거절 |
| 메모리 권한 검색 | 다른 작업 공간·부서·비공개 문서를 검색 결과에서 제외 |
| 근거 부족 | 출처 후보가 없으면 모델을 호출하지 않고 거절 사유 반환 |
| 모델 연동 선택 | 기본 테스트용 모델과 명시적 OpenAI Responses 구성을 분리 |
| 조회·평가 | 검색 건수와 지연시간을 기록하고 고정 질문으로 권한·출처 회귀를 확인 |
| PostgreSQL 권한 검색 | 실제 DB 통합 테스트에서 작업 공간·소유자·공개 범위·부서 조건과 `ready` 상태를 SQL 후보 단계에서 확인 |
| 정적 화면 | 고정 입력 빌드가 `/api` 의존 없이 렌더링되는지 브라우저 테스트로 확인 |

## 대표 코드와 테스트

- 코드: [repository.py](app/repository.py) - 작업 공간, 소유자, 공개 범위와 부서 조건을 SQL 선필터에 적용합니다.
- 테스트: [test_retrieval_permissions.py](tests/test_retrieval_permissions.py) - 메모리 경로에서 작업 공간·부서·비공개 문서 격리를 확인합니다.
- 실 DB 테스트: [test_postgres_repository_integration.py](tests/test_postgres_repository_integration.py) - 허용·거절·다른 작업 공간·미색인 문서를 같은 질의 후보에서 확인합니다.

## 실행

Python 3.11 이상에서 기본 회귀를 실행합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
python -m compileall -q app
```

웹은 동적 화면과 고정 데이터 화면을 각각 빌드·검증합니다.

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

- `demo` 인증은 요청 권한을 신뢰하며 `trusted_headers`는 앞단 서버가 헤더를 안전하게 관리한다는 전제가 필요합니다.
- 공개 데모는 포함된 고정 데이터만 사용하며 FastAPI, PostgreSQL, pgvector, OpenAI의 실제 실행 결과가 아닙니다.
- 권한 격리는 애플리케이션 SQL 선필터로 검증하며 PostgreSQL RLS를 구현했다는 주장은 하지 않습니다.
- 소규모 통합 데이터의 pgvector 정렬은 기능 확인 범위이며, IVFFlat 인덱스 사용 여부나 운영 규모 검색 성능을 증명하지 않습니다.
- 토큰은 4글자당 1개로 근사하고 고정 단가를 적용하므로 실제 모델 사용량이나 청구액이 아닙니다.
- 고정 질문 평가는 권한·검색·출처 회귀용이며 일반적인 RAG 품질 평가가 아닙니다.
- 대규모 문서 수집, 운영 IdP 연동, 운영 부하, 자동 확장과 다중 리전은 검증하지 않았습니다.
