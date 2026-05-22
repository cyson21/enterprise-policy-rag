# Decisions

- Use Colima as the local Docker daemon for this project because it can run with a fixed 1 CPU / about 1GB VM profile and avoids keeping Docker Desktop open.
- Keep `docker-compose.yml` as the default project definition and add `docker-compose.low-resource.yml` as an opt-in override.
- Limit PostgreSQL integration smoke tests to the `postgres` service only; do not start frontend or backend dev servers.
- Install `psycopg[binary]` only if missing, rather than reinstalling the whole project dependency set.
- Stop containers and Colima after the check so Docker work does not keep consuming CPU/RAM.
