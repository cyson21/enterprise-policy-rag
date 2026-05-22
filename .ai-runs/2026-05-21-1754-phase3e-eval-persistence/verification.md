# Verification

## RED

```bash
pytest tests/test_eval_api.py::test_eval_run_api_persists_created_runs_for_history -q
```

Expected failure before implementation:

```text
1 failed
assert len(runs) >= 2
```

## Targeted GREEN

```bash
pytest tests/test_eval_api.py tests/test_runtime_storage.py -q
```

Result:

```text
5 passed in 1.05s
```

```bash
pytest tests/test_eval_runs.py tests/test_eval_api.py tests/test_runtime_storage.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
9 passed, 1 skipped in 0.29s
```

## Regression

```bash
pytest -q
```

Result:

```text
44 passed, 2 skipped in 0.28s
```

```bash
python3 -m compileall -q app
```

Result: passed.

```bash
docker compose config -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
```

Result: passed.

```bash
node scripts/check-package-manager.mjs
node scripts/run-web-task.mjs smoke
node scripts/run-web-task.mjs build
```

Result:

```text
package manager check passed
frontend shell smoke passed
vite v7.3.3 building client environment for production...
1587 modules transformed.
built in 1.12s
```

## PostgreSQL Runtime Smoke

Started low-resource Colima and Postgres, applied idempotent schema, then ran:

```bash
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
2 passed in 0.41s
```

Tables after schema apply:

```text
answers
citations
document_chunks
documents
eval_case_results
eval_runs
query_logs
retrieval_results
workspaces
```

Resource sample:

```text
enterprise-policy-rag-postgres CPU=3.89% MEM=55.21MiB / 512MiB
```

Cleanup:

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```
