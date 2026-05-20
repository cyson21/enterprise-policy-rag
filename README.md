# Enterprise Policy RAG

Enterprise Policy RAG는 기업 내부 정책, 업무 매뉴얼, 보안 지침 문서를 권한 기반으로 검색하고, 근거가 있는 답변과 운영 지표를 제공하는 RAG 백엔드 프로젝트입니다.

## Project Goal

RAG를 단순 챗봇 기능으로 구현하는 것이 아니라, 실제 엔터프라이즈 백엔드에서 문제가 되는 권한, 근거, latency, token cost, 평가 가능성을 함께 다룹니다.

1차 범위에서는 온프레미스 설치형 배포를 제외하고, 로컬 Docker Compose로 재현 가능한 SaaS형 백엔드 구조를 만듭니다.

## MVP Scope

| 영역 | 구현 목표 |
|---|---|
| Document Ingestion | Markdown/TXT/PDF 문서 등록, chunking, metadata 저장 |
| Embedding Store | PostgreSQL + pgvector 기반 chunk vector 저장 |
| Retrieval | workspace, user, department, visibility 기반 권한 필터 검색 |
| Answer Generation | fake LLM provider 우선, 이후 OpenAI adapter 추가 |
| Citation | 답변에 사용된 chunk와 source document 반환 |
| Observability | request latency, token usage, estimated cost, retrieved chunks 기록 |
| Eval | golden question set 기반 retrieval hit와 citation coverage 측정 |

## Non-Goals

- 온프레미스 설치형 배포
- 처음부터 복잡한 multi-agent workflow
- 대규모 문서 파서 제품화
- 실제 결제/과금 시스템
- Kubernetes 운영 자동화

## Planned Stack

| 영역 | 후보 |
|---|---|
| Backend | Python, FastAPI |
| DB | PostgreSQL, pgvector |
| Worker | FastAPI background task 또는 RQ/Celery 후순위 검토 |
| Cache/Queue | Redis |
| LLM | fake provider first, OpenAI adapter later |
| Runtime | Docker Compose |
| Test | pytest, API integration tests, eval fixtures |

## First Milestone

```text
문서 등록
→ chunk 저장
→ fake embedding 기반 검색
→ 권한 필터 적용
→ retrieval-only API 응답
→ 테스트와 project tracking 기록
```

실제 LLM API 연결은 후순위입니다. 초기 구조는 `LLMProvider`와 `EmbeddingProvider`를 분리해 API key 없이도 테스트와 CI가 통과하도록 설계합니다.

## Key Docs

| 문서 | 내용 |
|---|---|

## Working Rule

