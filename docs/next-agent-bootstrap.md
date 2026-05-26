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
- 1차 목표: 권한 기반 retrieval core와 포트폴리오 시연용 필수 화면
- 실제 OpenAI API 연결: 후순위
- 온프레미스 배포: 1차 범위 제외
- 필수 화면: Search Console, Knowledge Library, Retrieval Lab, Operations

## 먼저 확인할 설계 문서

1. `docs/internal/design/2026-05-20-enterprise-policy-rag-product-architecture.md`
2. `docs/internal/plans/2026-05-20-enterprise-policy-rag-master-plan.md`
3. `docs/internal/plans/2026-05-20-architecture-first-ui-implementation-plan.md`
4. `docs/adr/0001-fake-provider-first-retrieval-rag.md`
5. `docs/api-data-model.md`
6. `docs/runbooks/local-demo.md`
7. `.ai-runs/2026-05-21-0931-docs-portfolio-package/`
8. `.ai-runs/2026-05-21-0926-phase3-fake-eval-runner/`
9. `.ai-runs/2026-05-21-0919-phase2-fake-answer-layer/`
10. `.ai-runs/2026-05-21-1426-phase3b-query-log-persistence/`
11. `.ai-runs/2026-05-21-1414-low-resource-postgres-integration/`
12. `.ai-runs/2026-05-21-1716-runtime-postgres-selection/`
13. `.ai-runs/2026-05-21-1747-phase3d-evidence-persistence/`
14. `.ai-runs/2026-05-21-1754-phase3e-eval-persistence/`
15. `.ai-runs/2026-05-21-1800-phase3f-operations-trend/`
16. `.ai-runs/2026-05-21-1809-phase3g-query-drilldown/`
17. `.ai-runs/2026-05-21-1820-phase3h-openai-adapter-skeleton/`
18. `.ai-runs/2026-05-22-0305-demo-polish-screenshots/`
19. `.ai-runs/2026-05-22-1812-phase4b-openai-and-portfolio-closeout/`
20. `.ai-runs/2026-05-23-0412-static-demo-deploy-readiness/`
21. `.ai-runs/2026-05-26-1005-github-remote-and-vercel-git-integration/`

## 첫 구현 단위 추천

이전 첫 구현 단위로 아래 backend retrieval core prototype이 만들어졌다.

```text
FastAPI skeleton
PostgreSQL + pgvector compose
document/chunk schema
fake embedding provider
retrieval-only API
permission filter tests
```

현재는 아래 범위가 진행되었다.

```text
React/Vite frontend skeleton
Search Console preview route
Knowledge Library preview route
Retrieval Lab preview route
Operations preview route
workspace/persona API
frontend static smoke
backend API smoke
pnpm workspace switch
Search Console live retrieval
retrieval access_reason metadata
demo documents
Knowledge Library document list/detail API
Knowledge Library live document/chunk preview
PostgresPolicyRepository implementation
PostgreSQL integration test entrypoint
Retrieval Lab live top-k/score threshold controls
Operations query-log metrics and recent query API
Fake LLM answer API with citations and refusal behavior
Search Console cited answer panel
Fake-provider golden eval runner and Operations eval table
Portfolio one-pager, local demo runbook, API/data model draft, architecture SVG
Colima low-resource PostgreSQL integration smoke
Query log repository, runtime query logging, and query-log-based Operations metrics
DATABASE_URL runtime repository selection for documents and query logs
Retrieval result, answer, citation persistence with Top Evidence Operations table
Eval run and eval case result persistence
Operations query trend API and table
Operations query drilldown API and detail panel
OpenAI Responses API transport behind `LLMProvider`
Operations demo polish and screenshot assets
Korean demo UI labels and refreshed non-clipped screenshot assets
Portfolio interview guide
Static read-only demo build with `VITE_DEMO_MODE=static`
Vercel static deploy config
Public Vercel demo: https://enterprise-policy-rag.vercel.app
GitHub repo: https://github.com/cyson21/enterprise-policy-rag
```

다음 구현 에이전트는 전체 제품 설계에 맞춰 아래 범위를 우선한다.

```text
Vercel GitHub App repo access approval for automatic deployments
Production auth/SSO design
Admin workflow expansion
```

PostgreSQL repository integration smoke는 Colima low-resource Docker daemon에서 완료되었다. 재검증이 필요하면 아래 명령을 사용한다.

```bash
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml up -d postgres
```

```bash
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
```

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

Frontend package manager:

```bash
corepack enable pnpm
pnpm install
pnpm web:dev
pnpm web:build
pnpm web:smoke
pnpm web:build:static
pnpm web:smoke:static
```

Static public-demo prep:

```bash
node scripts/run-web-task.mjs build:static
node scripts/smoke-static-demo.mjs
node scripts/run-web-task.mjs preview:static
```

The public static demo is deployed at `https://enterprise-policy-rag.vercel.app`. GitHub remote is `https://github.com/cyson21/enterprise-policy-rag`. Vercel Git integration is not connected yet because the Vercel GitHub App needs browser approval for this newly created repo.

외부 LLM 호출의 기본 실행, production auth/SSO, production admin dashboard는 다음 단위에 넣지 않는다.

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
- `LLM_PROVIDER` 기본값은 `fake`로 유지한다.
- `LLM_PROVIDER=openai`는 `OPENAI_API_KEY`가 있을 때만 OpenAI Responses API transport를 사용한다.
- Portfolio screenshots are in `docs/assets/operations-demo-*.jpg`.
- Portfolio interview/demo guide is `docs/portfolio-interview-guide.md`.
- Static demo deploy runbook is `docs/runbooks/static-demo-deploy.md`.
- Public demo URL: `https://enterprise-policy-rag.vercel.app`.
- GitHub repo URL: `https://github.com/cyson21/enterprise-policy-rag`.
- 공개 README에는 특정 채용공고나 개인 지원 전략을 직접 넣지 않는다.
- 포트폴리오 문서는 사람이 직접 관리하는 톤으로 작성한다.
- 빌드/생성 산출물은 원본 소스에서 다시 생성한다.
