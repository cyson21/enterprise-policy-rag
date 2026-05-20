# Next Agent Bootstrap

이 문서는 새 에이전트가 `/Users/chanyang.son/Documents/side-projects/repos/enterprise-policy-rag`에서 실제 구현을 시작할 때 읽는 기준이다.

## 먼저 읽을 파일

1. `/Users/chanyang.son/Documents/side-projects/SIDE_PROJECT_GUIDE.md`
2. `README.md`
3. `TODO.md`
4. `docs/project-tracking.md`
5. `docs/internal/plans/2026-05-20-project-02-foundation-plan.md`

## 현재 합의된 방향

- 프로젝트명: `Enterprise Policy RAG`
- 실제 구현 레포: `/Users/chanyang.son/Documents/side-projects/repos/enterprise-policy-rag`
- 상위 소개 폴더: `/Users/chanyang.son/Documents/side-projects/projects/02-enterprise-policy-rag`
- 1차 목표: 권한 기반 retrieval core
- 실제 OpenAI API 연결: 후순위
- 온프레미스 배포: 1차 범위 제외

## 첫 구현 단위 추천

첫 구현 에이전트는 아래 범위만 잡는 것이 좋다.

```text
FastAPI skeleton
PostgreSQL + pgvector compose
document/chunk schema
fake embedding provider
retrieval-only API
permission filter tests
```

OpenAI API, 답변 생성, eval, admin dashboard는 이 첫 단위에 넣지 않는다.

## 기록 방식

작업 단위마다 `.ai-runs/<run-id>/`를 만들고 아래 파일을 남긴다.

```text
goal.md
agent-plan.md
changed-files.md
decisions.md
verification.md
```

압축된 대화 요약보다 현재 파일, Git 상태, `.ai-runs` 기록을 우선해서 판단한다.

## 주의 사항

- API key가 없어도 테스트와 로컬 검증이 가능해야 한다.
- 외부 LLM API 호출은 provider 인터페이스 뒤에 둔다.
- 공개 README에는 특정 채용공고나 개인 지원 전략을 직접 넣지 않는다.
- 포트폴리오 문서는 사람이 직접 관리하는 톤으로 작성한다.
- 빌드/생성 산출물은 원본 소스에서 다시 생성한다.
