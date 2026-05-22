# Changed Files

| File | Purpose |
|---|---|
| `.gitignore` | Ignore local Python, pytest, env, and database artifacts |
| `pyproject.toml` | Declare FastAPI, pydantic, psycopg, uvicorn, and test dependencies |
| `docker-compose.yml` | Define local PostgreSQL + pgvector service |
| `infra/postgres/init/001_schema.sql` | Define workspace, document, chunk, vector, and permission indexes |
| `app/chunking.py` | Deterministic paragraph chunking |
| `app/models.py` | Request/response and stored domain models |
| `app/providers.py` | `EmbeddingProvider`, `LLMProvider`, and fake embedding implementation |
| `app/repository.py` | In-memory repository for first retrieval slice |
| `app/retrieval.py` | Permission-aware retrieval service |
| `app/services.py` | Document ingestion and retrieval orchestration |
| `app/main.py` | FastAPI app skeleton and local fallback route wiring |
| `tests/test_chunking.py` | Chunking tests |
| `tests/test_fake_embedding_provider.py` | Fake embedding determinism tests |
| `tests/test_retrieval_permissions.py` | Permission filter tests |
| `tests/test_api_retrieval.py` | Retrieval-only API flow tests |
| `README.md` | Current implementation and verification notes |
| `TODO.md` | Phase 1 retrieval core status update |
| `docs/project-tracking.md` | Phase/status and verification snapshot update |
