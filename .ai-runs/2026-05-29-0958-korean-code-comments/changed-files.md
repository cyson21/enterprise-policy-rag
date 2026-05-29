# Changed Files

## Added

- `.ai-runs/2026-05-29-0958-korean-code-comments/goal.md`
- `.ai-runs/2026-05-29-0958-korean-code-comments/agent-plan.md`
- `.ai-runs/2026-05-29-0958-korean-code-comments/changed-files.md`
- `.ai-runs/2026-05-29-0958-korean-code-comments/decisions.md`
- `.ai-runs/2026-05-29-0958-korean-code-comments/verification.md`

## Updated

- Backend Python: `app/__init__.py`, `app/answer.py`, `app/auth.py`, `app/chunking.py`, `app/demo_data.py`, `app/eval_runs.py`, `app/evaluation.py`, `app/main.py`, `app/models.py`, `app/operations.py`, `app/providers.py`, `app/query_logs.py`, `app/repository.py`, `app/retrieval.py`, `app/runtime.py`, `app/services.py`
- Frontend source: `web/index.html`, `web/scripts/smoke.mjs`, `web/src/api/client.ts`, `web/src/app/App.tsx`, `web/src/app/routes.tsx`, `web/src/components/layout/AppShell.tsx`, `web/src/components/persona/PersonaSelector.tsx`, `web/src/config/demoMode.ts`, `web/src/fixtures/personas.ts`, `web/src/routes/knowledge/KnowledgePage.tsx`, `web/src/routes/operations/OperationsPage.tsx`, `web/src/routes/retrieval-lab/RetrievalLabPage.tsx`, `web/src/routes/search/SearchPage.tsx`, `web/src/styles/tokens.css`, `web/src/utils/display.ts`, `web/src/vite-env.d.ts`, `web/vite.config.ts`
- Scripts/config/infra: `scripts/capture-portfolio-screenshots.mjs`, `scripts/check-package-manager.mjs`, `scripts/openai_live_smoke.py`, `scripts/run-web-task.mjs`, `scripts/smoke-static-demo.mjs`, `docker-compose.yml`, `docker-compose.low-resource.yml`, `infra/postgres/init/001_schema.sql`, `pnpm-workspace.yaml`, `pyproject.toml`
- Tests: `tests/test_admin_workflow.py`, `tests/test_answer_api.py`, `tests/test_api_retrieval.py`, `tests/test_auth_context.py`, `tests/test_chunking.py`, `tests/test_documents_api.py`, `tests/test_eval_api.py`, `tests/test_eval_runs.py`, `tests/test_fake_embedding_provider.py`, `tests/test_openai_live_smoke.py`, `tests/test_operations_api.py`, `tests/test_personas_api.py`, `tests/test_postgres_repository.py`, `tests/test_postgres_repository_integration.py`, `tests/test_postgres_runtime_integration.py`, `tests/test_provider_selection.py`, `tests/test_query_logs.py`, `tests/test_retrieval_metadata_api.py`, `tests/test_retrieval_permissions.py`, `tests/test_runtime_storage.py`

## Not Included In Commit

- `.ai-runs/templates/goal.md`
- `.ai-runs/templates/verification.md`

위 두 파일은 작업 시작 전부터 변경되어 있었으므로 이번 커밋 범위에서 제외한다.
