# Verification

## RED

```bash
pytest tests/test_runtime_storage.py -q
```

Expected failure before implementation:

```text
2 failed
ModuleNotFoundError: No module named 'app.runtime'
```

## Unit GREEN

```bash
pytest tests/test_runtime_storage.py -q
```

Result:

```text
2 passed in 0.21s
```

## Docker-Free Regression

```bash
pytest tests/test_runtime_storage.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
2 passed, 1 skipped in 0.27s
```

```bash
pytest -q
```

Result:

```text
35 passed, 2 skipped in 0.36s
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
built in 1.11s
```

## PostgreSQL Runtime Integration

Started Colima:

```bash
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
```

Docker server:

```text
Server=29.2.1 CPUs=1 Mem=1002291200
```

Started Postgres only:

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml up -d postgres
```

Healthcheck:

```text
healthy
```

Root-cause check for initial failure:

```text
existing tables before schema reapply:
document_chunks
documents
workspaces
```

Existing Docker volume predated the `query_logs` table, so `001_schema.sql` was applied idempotently:

```bash
docker exec enterprise-policy-rag-postgres \
  psql -U rag_app -d enterprise_policy_rag \
  -v ON_ERROR_STOP=1 \
  -f /docker-entrypoint-initdb.d/001_schema.sql
```

Tables after schema reapply:

```text
document_chunks
documents
query_logs
workspaces
```

Targeted integration:

```bash
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py tests/test_postgres_runtime_integration.py -q
```

Result:

```text
2 passed in 0.33s
```

Resource sample:

```text
NanoCpus=1000000000 Memory=536870912 ShmSize=67108864
enterprise-policy-rag-postgres CPU=4.95% MEM=55.64MiB / 512MiB
```

Cleanup:

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

Final status:

```text
colima is not running
```
