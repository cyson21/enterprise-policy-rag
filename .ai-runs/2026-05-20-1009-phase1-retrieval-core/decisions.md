# Decisions

| Decision | Reason | Alternatives |
|---|---|---|
| Keep OpenAI and answer generation out of Phase 1 | The first slice is retrieval core only and must run without API keys | Add OpenAI adapter now |
| Use deterministic fake embeddings | Tests and CI need stable retrieval behavior without external calls | Random vectors or live embeddings |
| Use in-memory repository for first API tests | It proves ingestion, chunking, retrieval, and permission filters without requiring local DB runtime | Build psycopg adapter immediately |
| Add PostgreSQL/pgvector compose and schema now | The project needs the target storage shape even before the persistence adapter is wired | Delay DB artifacts until later |
| Permission access is workspace plus public, owner, or department match | This covers the first enterprise authorization model without adding roles/admin flows | Add full RBAC now |
