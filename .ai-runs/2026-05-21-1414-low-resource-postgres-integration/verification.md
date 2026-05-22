# Verification

## Environment

- Installed Colima with `HOMEBREW_NO_AUTO_UPDATE=1 brew install colima`.
- Started Colima with:

```bash
colima start --cpu 1 --memory 1 --disk 10 --vm-type=vz --mount-type=virtiofs --runtime=docker
```

- Docker context after start: `colima`
- Docker server profile: `Server=29.2.1 CPUs=1 Mem=1002291200`
- Installed missing PostgreSQL driver:

```bash
python3 -m pip install 'psycopg[binary]>=3.2,<4.0'
```

## Compose Checks

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
```

Result: passed.

```bash
docker compose config -q
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml config -q
```

Result: passed.

## PostgreSQL Integration

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml up -d postgres
```

Result: pulled `pgvector/pgvector:pg16`, created volume `enterprise-policy-rag_postgres-data`, and started `enterprise-policy-rag-postgres`.

Healthcheck:

```text
healthy
```

Resource/tuning confirmation:

```text
NanoCpus=1000000000 Memory=536870912 ShmSize=67108864
shared_buffers=64MB
work_mem=4MB
maintenance_work_mem=32MB
max_connections=20
effective_cache_size=256MB
enterprise-policy-rag-postgres CPU=5.78% MEM=36.55MiB / 512MiB
```

Integration test:

```bash
RUN_POSTGRES_TESTS=1 \
DATABASE_URL=postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag \
pytest tests/test_postgres_repository_integration.py -q
```

Result:

```text
1 passed in 0.60s
```

## Cleanup

```bash
docker compose -f docker-compose.yml -f docker-compose.low-resource.yml stop postgres
colima stop
```

Result: Postgres stopped and Colima stopped.

Final status:

```text
colima is not running
```

## Regression

```bash
pytest -q
```

Result:

```text
28 passed, 1 skipped in 0.32s
```

```bash
python3 -m compileall -q app
```

Result: passed.
