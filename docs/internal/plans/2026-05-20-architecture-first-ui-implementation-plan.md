# Architecture-First UI Implementation Plan

작성일: 2026-05-20

## Goal

전체 제품 그림을 먼저 고정한 뒤, 화면에서 시연 가능한 vertical slice 단위로 구현한다.

## 원칙

- 화면은 필수 범위다.
- 첫 화면은 Search Console이다.
- 백엔드 API는 화면이 실제로 쓰는 순서대로 확장한다.
- API key 없이 demo/test가 가능해야 한다.
- OpenAI adapter, 실제 답변 생성, eval engine은 화면/검색 흐름이 안정된 뒤 진행한다.
- 레퍼런스 화면을 그대로 복제하지 않고, 제품 패턴만 가져온다.

## 구현 순서

### Slice 0: Architecture Baseline

목표:

- 전체 아키텍처 문서와 TODO/project tracking을 현재 방향으로 맞춘다.

산출물:

- `docs/internal/design/2026-05-20-enterprise-policy-rag-product-architecture.md`
- `docs/project-tracking.md`
- `TODO.md`
- `docs/next-agent-bootstrap.md`

완료 기준:

- 필수 화면 4개가 명시되어 있다.
- 다음 구현 범위가 `Search Console + Knowledge Library + PostgreSQL persistence`로 정리되어 있다.

### Slice 1: Frontend Shell + Demo Personas

목표:

- 포트폴리오 시연이 가능한 기본 화면 골격을 만든다.

예정 파일:

- `web/package.json`
- `web/src/app/App.tsx`
- `web/src/app/routes.tsx`
- `web/src/components/layout/AppShell.tsx`
- `web/src/components/persona/PersonaSelector.tsx`
- `web/src/api/client.ts`
- `web/src/fixtures/personas.ts`
- `web/src/styles/tokens.css`

완료 기준:

- 좌측 sidebar와 상단 workspace/persona/provider badge가 보인다.
- Search, Knowledge, Retrieval Lab, Operations route가 존재한다.
- persona selector가 전역 상태로 동작한다.
- 아직 backend가 없어도 fixture로 화면이 깨지지 않는다.

검증:

- frontend unit/smoke test
- desktop/mobile screenshot smoke

### Slice 2: Search Console Vertical Slice

목표:

- 사용자가 질문하고 권한 내 retrieved chunks를 확인한다.

Backend:

- `POST /retrieve` response에 `access_reason`, `visibility`, `department_ids`를 포함한다.
- `GET /personas` fixture API를 추가한다.

Frontend:

- `web/src/routes/search/SearchPage.tsx`
- query input
- retrieval result list
- source/chunk detail panel
- empty state
- persona 변경 시 결과 재요청

완료 기준:

- 같은 query에서 security/finance persona 결과가 다르게 보인다.
- 화면에 generated answer가 아니라 retrieval-only 결과임이 명확하다.
- 권한 밖 문서가 결과에 나오지 않는다.

검증:

- API permission tests
- UI smoke test: persona 변경 후 결과 차이 확인

### Slice 3: Knowledge Library + PostgreSQL Persistence

목표:

- 문서 등록, 목록, 상세, chunk preview를 실제 DB path와 연결한다.

Backend:

- PostgreSQL repository 추가
- `GET /documents`
- `GET /documents/{id}`
- `POST /documents`
- seed script 또는 demo fixture loader

Frontend:

- `web/src/routes/knowledge/KnowledgePage.tsx`
- document table
- create document drawer
- document detail side panel
- chunk list
- visibility/department filters

완료 기준:

- Docker Compose DB에 문서를 저장하고 재조회한다.
- 등록한 문서가 Search Console에서 검색된다.
- 문서별 visibility/department/owner가 UI에서 보인다.

검증:

- repository integration test
- document API test
- UI smoke test: 문서 등록 후 검색

### Slice 4: Retrieval Lab

목표:

- RAG 품질과 권한 필터를 개발자/운영자 시점에서 디버깅한다.

Backend:

- `POST /retrieve/debug` 또는 `POST /retrieve` debug 옵션
- top-k, score threshold 적용
- access reason 노출

Frontend:

- `web/src/routes/retrieval-lab/RetrievalLabPage.tsx`
- top-k control
- score threshold control
- query input
- ranked chunk table
- access reason column

완료 기준:

- retrieval setting 변경이 결과에 반영된다.
- 각 결과가 왜 보였는지 설명된다.
- Search Console보다 디버깅 정보가 더 많다.

검증:

- score threshold API test
- UI smoke test: top-k 변경

### Slice 5: Answer + Citation

목표:

- fake LLM으로 답변 생성과 citation UX를 만든다.

Backend:

- `LLMProvider`
- `FakeLLMProvider`
- `POST /answer`
- refusal policy
- citation model

Frontend:

- Search Console answer panel
- citation cards
- unsupported answer state

완료 기준:

- API key 없이 fake answer/citation이 동작한다.
- 근거가 없으면 답변을 거부한다.
- OpenAI adapter는 아직 선택 기능으로만 둔다.

검증:

- answer/refusal tests
- citation mapping tests
- UI smoke test

### Slice 6: Operations + Eval

목표:

- 운영 가능한 AI 백엔드라는 신호를 화면과 지표로 보여준다.

Backend:

- query log
- latency/provider/cost estimate
- eval dataset
- eval run/result

Frontend:

- `web/src/routes/operations/OperationsPage.tsx`
- KPI cards
- query log table
- top document table
- eval run table

완료 기준:

- seeded demo data 또는 실제 query log 기반으로 Operations 화면이 동작한다.
- retrieval hit와 citation coverage가 표시된다.

검증:

- metrics API test
- eval runner test
- UI smoke test

### Slice 7: Portfolio Package

목표:

- 구현 결과를 평가자가 빠르게 이해할 수 있게 정리한다.

산출물:

- README demo flow
- architecture SVG
- screenshots
- runbook
- portfolio one-pager

완료 기준:

- 로컬에서 demo를 재현할 수 있다.
- 화면 캡처가 최신 UI와 일치한다.
- README에 문제, 아키텍처, 검증 결과가 연결된다.

## 다음 즉시 작업

1. `Slice 1: Frontend Shell + Demo Personas`를 구현한다.
2. 구현 전에 `.ai-runs/<run-id>/`에 goal/plan/decisions/verification 파일을 만든다.
3. frontend route shell과 persona selector가 완료되면 screenshot smoke를 남긴다.
