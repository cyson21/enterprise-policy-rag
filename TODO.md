# Enterprise Policy RAG TODO

마지막 갱신: 2026-05-20
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
- [ ] ADR 디렉터리와 첫 ADR 작성
  - 완료 기준: RAG 중심 프로젝트 선택 이유와 온프레미스 제외 이유를 기록한다.
- [ ] API/데이터 모델 초안 작성
  - 완료 기준: workspace, document, chunk, permission, query log, eval run 핵심 테이블이 정의된다.

## Phase 1. Retrieval Core

- [ ] FastAPI 프로젝트 스캐폴딩
- [ ] PostgreSQL + pgvector 로컬 compose 구성
- [ ] document/chunk metadata schema 작성
- [ ] Markdown/TXT ingestion API 구현
- [ ] chunking strategy 구현
- [ ] fake embedding provider 구현
- [ ] 권한 필터가 적용된 retrieval API 구현
- [ ] retrieval-only API 테스트 작성

## Phase 2. LLM Answer Layer

- [ ] `LLMProvider` 인터페이스 정의
- [ ] fake LLM provider 구현
- [ ] OpenAI adapter 추가
- [ ] citation 포함 답변 API 구현
- [ ] 근거 부족 시 답변 거부 규칙 구현
- [ ] token/latency/cost 기록 구현

## Phase 3. Eval and Operations

- [ ] golden question set fixture 작성
- [ ] retrieval hit 평가 구현
- [ ] citation coverage 평가 구현
- [ ] eval report 생성
- [ ] query log 조회 API 구현
- [ ] 운영 지표 README 반영

## Phase 4. Portfolio Package

- [ ] README 공개용 정리
- [ ] 아키텍처 이미지 작성
- [ ] 포트폴리오 one-pager 작성
- [ ] 데모 실행 runbook 작성
- [ ] 최종 검증 기록 정리
