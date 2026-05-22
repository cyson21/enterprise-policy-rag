# Verification

## Targeted TDD Checks

```bash
pytest tests/test_operations_api.py::test_metrics_trend_api_groups_retrieval_and_answer_logs_by_date -q
```

Result:

```text
1 passed
```

```bash
pytest tests/test_operations_api.py tests/test_query_logs.py -q
```

Result:

```text
13 passed in 0.27s
```

## Local Regression

```bash
pytest -q
```

Result:

```text
46 passed, 2 skipped in 0.31s
```

```bash
python3 -m compileall -q app
```

Result: passed.

```bash
docker compose config -q && docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
```

Result: passed.

```bash
node scripts/check-package-manager.mjs
```

Result:

```text
package manager check passed
```

```bash
node scripts/run-web-task.mjs smoke
```

Result:

```text
frontend shell smoke passed
```

```bash
node scripts/run-web-task.mjs build
```

Result:

```text
vite v7.3.3 building client environment for production...
1587 modules transformed.
built in 1.02s
```

## Low-Resource PostgreSQL Runtime

```bash
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml up -d postgres
docker exec enterprise-policy-rag-postgres psql -U rag_app -d enterprise_policy_rag -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/001_schema.sql
RUN_POSTGRES_TESTS=1 DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

Result:

```text
2 passed in 0.38s
```

Schema tables observed:

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
enterprise-policy-rag-postgres   CPU 5.64%   MEM 54.72MiB / 512MiB
```

Cleanup: Postgres container stopped and Colima stopped.
