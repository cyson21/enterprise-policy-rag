# Goal

Run the PostgreSQL repository integration check with minimal local resource usage.

Scope:

- Use Colima instead of Docker Desktop for a lighter Docker daemon.
- Keep the Docker daemon at 1 CPU and about 1GB memory.
- Start only the PostgreSQL/pgvector service.
- Add a reusable low-resource compose override for PostgreSQL.
- Verify the repository round-trip test with `RUN_POSTGRES_TESTS=1`.
- Stop Docker workloads after verification.
