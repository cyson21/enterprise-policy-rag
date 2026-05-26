# Enterprise Policy RAG Interview Guide

## 30-Second Pitch

Enterprise Policy RAG는 사내 정책/업무 매뉴얼/보안 지침을 권한 기반으로 검색하고, 근거가 있는 답변과 운영 지표를 제공하는 RAG 백엔드입니다. 단순 챗봇이 아니라 권한 필터, citation, provider abstraction, query logging, eval, latency/cost visibility까지 제품 운영 관점으로 구성했습니다.

## Demo Path

Public URL: `https://enterprise-policy-rag.vercel.app`

Repository: `https://github.com/cyson21/enterprise-policy-rag`

1. 검색 콘솔에서 `김민아 / 보안` persona로 보안 사고 질문을 실행한다.
2. 답변, citation, chunk score, 접근 사유가 함께 표시되는지 보여준다.
3. `박준 / 재무` persona로 바꿔 같은 질문의 검색 결과가 권한에 따라 달라지는지 보여준다.
4. 지식 라이브러리에서 문서 visibility, department, owner, chunk preview를 확인한다.
5. 검색 실험실에서 top-k와 score threshold를 조정해 retrieval 결과 변화를 보여준다.
6. 운영 지표에서 query trend, recent queries, selected query detail, top evidence, eval history를 보여준다.

## Architecture Story

- API는 FastAPI app factory로 구성되어 있고, 서비스 계층이 document ingestion, retrieval, answer, eval, operations를 조율한다.
- 저장소는 `PolicyRepository`, `QueryLogRepository`, `EvalRunRepository` 인터페이스 뒤에 있다.
- 기본 로컬 경로는 in-memory repository와 fake provider를 사용해 API key와 Docker 없이 통과한다.
- `DATABASE_URL`이 있으면 PostgreSQL + pgvector repository로 전환한다.
- 모든 외부 AI 호출은 `EmbeddingProvider`, `LLMProvider` 뒤에 있고, `LLM_PROVIDER=openai`는 명시 opt-in일 때만 OpenAI Responses API transport를 사용한다.

## What To Emphasize

- 권한 필터는 retrieval 결과에만 UI 표시를 덧붙인 것이 아니라 service-level ranking 전에 적용된다.
- citation과 query detail은 호출 시점의 snapshot으로 저장되어 나중에 운영 화면에서 재현 가능하다.
- eval은 fake provider 기반 golden set으로 retrieval hit와 citation coverage를 반복 측정한다.
- 운영 화면은 seeded metric이 아니라 query log repository에서 계산되는 API와 연결되어 있다.
- 기본 검증은 `pytest`, compile smoke, compose config, frontend smoke/build로 API key 없이 재현된다.
- public demo용 static build는 `/api` 호출 없이 같은 화면을 read-only fake-provider fixture로 렌더링한다.

## Tradeoffs

- 실제 IdP/OIDC 연결 대신 demo auth context와 persona selector를 사용한다. 포트폴리오에서는 권한 시나리오를 빠르게 보여주고, production 전환 경계는 `AuthContextProvider`와 session-bound endpoint로 분리했다.
- 대규모 문서 파서나 PDF ingestion은 제외했다. 첫 범위는 Markdown/TXT chunking, permission retrieval, citation, operations에 집중한다.
- OpenAI live transport는 구현되어 있지만 기본 테스트에서는 호출하지 않는다. 비용과 secret 의존성을 CI에 넣지 않기 위해 mock HTTP opener로 검증한다.
- 온프레미스 배포와 Kubernetes 운영 자동화는 1차 범위에서 제외했다.

## Evidence

- Architecture: `docs/assets/architecture.svg`
- API/data model: `docs/api-data-model.md`
- Demo runbook: `docs/runbooks/local-demo.md`
- Static deploy runbook: `docs/runbooks/static-demo-deploy.md`
- Screenshots: `docs/assets/operations-demo-ko-v7-desktop.jpg`, `docs/assets/operations-demo-ko-v12-mobile-overview.jpg`, `docs/assets/operations-demo-ko-v12-mobile-full-page.jpg`
- Verification records: `.ai-runs/*/verification.md`

## Next Steps

- admin UI controls for document update/delete, indexing state, audit log
- real IdP/OIDC adapter behind `AuthContextProvider`
- optional live OpenAI smoke with a controlled API key
