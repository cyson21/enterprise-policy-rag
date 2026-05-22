# Verification

## RED

```bash
pytest tests/test_operations_api.py::test_evidence_top_api_counts_retrieval_results_and_answer_citations tests/test_query_logs.py::test_in_memory_query_logs_store_evidence_details_for_top_evidence -q
```

Expected failure before implementation:

```text
2 failed
404 for /evidence/top
AttributeError: 'InMemoryQueryLogRepository' object has no attribute 'add_retrieval_results'
```

## Targeted GREEN

```bash
pytest tests/test_operations_api.py::test_evidence_top_api_counts_retrieval_results_and_answer_citations tests/test_query_logs.py::test_in_memory_query_logs_store_evidence_details_for_top_evidence -q
```

Result:

```text
2 passed in 0.23s
```

```bash
pytest tests/test_query_logs.py tests/test_operations_api.py -q
```

Result:

```text
11 passed in 0.27s
```

```bash
pytest tests/test_operations_api.py tests/test_query_logs.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
11 passed, 1 skipped in 0.27s
```

## Regression

```bash
pytest -q
```

Result:

```text
39 passed, 2 skipped in 0.48s
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
built in 1.02s
```

## PostgreSQL Runtime Smoke

Started Colima:

```bash
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
```

Started Postgres and waited for health:

```text
healthy
```

Applied idempotent schema:

```bash
docker exec enterprise-policy-rag-postgres \
  psql -U rag_app -d enterprise_policy_rag \
  -v ON_ERROR_STOP=1 \
  -f /docker-entrypoint-initdb.d/001_schema.sql
```

Tables after schema apply:

```text
answers
citations
document_chunks
documents
query_logs
retrieval_results
workspaces
```

Integration:

```bash
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
2 passed in 0.31s
```

Resource sample:

```text
enterprise-policy-rag-postgres CPU=6.14% MEM=55.28MiB / 512MiB
```

Cleanup:

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```
