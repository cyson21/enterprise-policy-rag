# Enterprise Policy RAG Project Status

작성일: 2026-05-20
역할: 현재 상태, 문서 소유권, phase별 산출물, 주요 결정을 추적한다.

## 현재 스냅샷

| 항목 | 상태 |
|---|---|
| 도메인 | 엔터프라이즈 사내 정책/업무 문서 RAG |
| 목적 | AI Native Back-end Engineer 포지션 대응용 사이드 프로젝트 |
| 핵심 아키텍처 | FastAPI + PostgreSQL/pgvector + provider abstraction + eval |
| 현재 Phase | Phase 0 foundation |
| 실제 LLM API | 후순위. fake provider first |
| 온프레미스 | 1차 범위 제외 |

## 문서 소유권

| 문서 | 역할 |
|---|---|
| `README.md` | 외부 공개용 프로젝트 소개와 핵심 링크 |
| `TODO.md` | 현재 작업 상태 추적 |
| `docs/project-tracking.md` | 현재 상태와 주요 결정 |
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

## Phase 0 목표

- README, TODO, project tracking, foundation plan, next-agent bootstrap을 준비한다.
- 새 에이전트가 바로 실제 레포 기준으로 phase plan을 이어갈 수 있게 한다.
- 구현 전 ADR, 데이터 모델, API 경계를 먼저 정한다.

## Phase 1 예정 산출물

- FastAPI backend skeleton
- PostgreSQL + pgvector Docker Compose
- document/chunk schema
- fake embedding provider
- retrieval-only API
- 권한 필터 테스트

## Phase 2 예정 산출물

- LLM provider interface
- fake LLM provider
- OpenAI adapter
- citation answer API
- query log, token, latency, cost tracking

## Phase 3 예정 산출물

- golden question set
- eval runner
- retrieval hit report
- citation coverage report
- 운영 지표 조회 API

## 참고 벤치마크

| 레퍼런스 | 참고 관점 |
|---|---|
| R2R | RAG API 서버 기능 범위 |
| Haystack | pipeline 분리와 component 경계 |
| RAGFlow | 문서 처리와 citation UX |
| Open RAG Eval | 평가 리포트와 품질 기준 |
| AnythingLLM | workspace와 문서 채팅 UX |
