# Verification

## RED

```bash
pytest tests/test_operations_api.py::test_query_detail_api_returns_retrieval_snapshots_for_recent_row tests/test_operations_api.py::test_query_detail_api_returns_answer_and_citation_snapshots_for_answer_row -q
```

Result before implementation:

```text
2 failed
expected detail status 200, actual 404
```

## Targeted Checks

```bash
pytest tests/test_operations_api.py::test_query_detail_api_returns_retrieval_snapshots_for_recent_row tests/test_operations_api.py::test_query_detail_api_returns_answer_and_citation_snapshots_for_answer_row -q
```

Result after implementation:

```text
2 passed in 0.29s
```

```bash
pytest tests/test_operations_api.py tests/test_query_logs.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
17 passed, 1 skipped in 0.34s
```

## Local Regression

```bash
pytest -q
```

Result:

```text
50 passed, 2 skipped in 0.27s
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
built in 898ms
```

Note: the first build after UI wiring caught a TypeScript narrowing issue for `selectedQueryId`; it was fixed by capturing a non-null local `queryId` after the guard, then build passed.

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
2 passed in 0.36s
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
enterprise-policy-rag-postgres   CPU 7.26%   MEM 54.95MiB / 512MiB
```

Cleanup: Postgres container stopped and Colima stopped.

## Browser Render Check

```bash
node scripts/run-web-task.mjs dev -- --host 127.0.0.1 --port 5173
```

Browser verification:

```text
Opened http://127.0.0.1:5173/
Clicked Operations
Query Detail present: true
Stored evidence present: true
Citation snapshot present: true
Console error count: 0
Horizontal overflow: false
```

Cleanup: dev server on port 5173 stopped.

Note: in-app browser screenshot capture timed out twice, so this run uses DOM/layout verification instead of a saved screenshot.
