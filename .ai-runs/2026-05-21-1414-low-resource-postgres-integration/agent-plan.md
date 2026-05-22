# Agent Plan

1. Confirm Docker context and Colima resource limits.
2. Add a compose override that keeps PostgreSQL suitable for integration smoke tests:
   - 1 CPU
   - 512MB container memory
   - reduced shared buffers and connection count
3. Install only the missing Python database dependency if the active Python environment lacks `psycopg`.
4. Start only `postgres` with the base compose file plus the low-resource override.
5. Wait for the PostgreSQL healthcheck.
6. Run `tests/test_postgres_repository_integration.py` with `RUN_POSTGRES_TESTS=1`.
7. Stop the PostgreSQL container and Colima after verification.
8. Record results and update README/TODO/project tracking/bootstrap docs.
