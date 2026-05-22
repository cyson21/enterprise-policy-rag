# ADR 0001: Fake Provider First Enterprise Policy RAG

Date: 2026-05-21

## Status

Accepted

## Context

Enterprise Policy RAG는 사내 정책, 업무 매뉴얼, 보안 지침을 권한 기반으로 검색하고, 근거가 있는 답변과 운영 지표를 제공하는 제품형 RAG 백엔드다.

초기 구현에서 가장 중요한 리스크는 외부 AI 품질보다 다음 세 가지다.

- 문서와 chunk metadata가 권한 기준을 보존하는가
- retrieval 결과가 workspace, owner, department, visibility 기준을 지키는가
- API key 없이도 테스트, UI, 운영 지표, eval 흐름을 재현할 수 있는가

OpenAI API와 온프레미스 배포는 모두 후순위다. 1차 범위에서는 로컬 Docker Compose 기반 SaaS형 백엔드를 목표로 하되, Docker가 없어도 fake provider 기반 기능 검증은 가능해야 한다.

## Decision

- `EmbeddingProvider`와 `LLMProvider` 인터페이스를 먼저 둔다.
- 기본 구현은 `FakeEmbeddingProvider`와 `FakeLLMProvider`로 한다.
- 외부 AI 호출은 provider 뒤에만 추가한다.
- 기본 app path는 in-memory repository를 사용한다.
- PostgreSQL/pgvector는 compose, schema, repository implementation, optional integration test로 준비한다.
- 실제 PostgreSQL round-trip은 Docker daemon과 `psycopg` 환경이 있을 때만 실행한다.

## Consequences

Positive:

- API key 없이 `pytest`, frontend smoke, build, browser smoke가 가능하다.
- 권한 필터, citation, refusal, eval 흐름을 deterministic하게 검증할 수 있다.
- OpenAI adapter를 나중에 붙여도 API/UI/use case 경계를 유지할 수 있다.

Tradeoffs:

- fake embedding/LLM 품질은 실제 semantic retrieval 품질을 대표하지 않는다.
- PostgreSQL persistence 완료 전에는 기본 실행 경로가 in-memory다.
- 운영 지표와 eval history는 현재 seeded 또는 in-process 계산이며 영속 저장되지 않는다.

## Follow-Up

- Docker daemon 실행 후 `RUN_POSTGRES_TESTS=1` PostgreSQL repository round-trip을 검증한다.
- query log, eval run, retrieval result persistence를 PostgreSQL에 연결한다.
- OpenAI adapter는 fake provider tests가 안정된 뒤 선택적으로 추가한다.
