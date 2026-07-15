# 런타임 DI 테스트: DATABASE_URL 존재 유무에 따른 저장소 교체를 검증한다.
import pytest

from app.query_logs import InMemoryQueryLogRepository
from app.providers import OpenAIEmbeddingProvider
from app.repository import InMemoryPolicyRepository
from app.eval_runs import InMemoryEvalRunRepository
from app.services import PolicyRagServices


def test_build_services_from_env_uses_in_memory_repositories_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from app.runtime import build_services_from_env

    services = build_services_from_env()

    assert isinstance(services.repository, InMemoryPolicyRepository)
    assert isinstance(services.query_log_repository, InMemoryQueryLogRepository)
    assert isinstance(services.eval_run_repository, InMemoryEvalRunRepository)


def test_build_services_from_env_injects_embedding_provider(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from app.runtime import build_services_from_env

    services = build_services_from_env(
        {
            "EMBEDDING_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_EMBEDDING_MODEL": "text-embedding-test",
        }
    )

    assert isinstance(services.embedding_provider, OpenAIEmbeddingProvider)
    assert services.embedding_provider.model == "text-embedding-test"


def test_build_services_from_env_uses_postgres_repositories_with_database_url(monkeypatch):
    created: dict[str, str] = {}

    class RecordingPolicyRepository:
        def __init__(self, dsn: str) -> None:
            created["policy_dsn"] = dsn

    class RecordingQueryLogRepository:
        def __init__(self, dsn: str) -> None:
            created["query_log_dsn"] = dsn

    class RecordingEvalRunRepository:
        def __init__(self, dsn: str) -> None:
            created["eval_run_dsn"] = dsn

    monkeypatch.setenv("DATABASE_URL", "postgresql://example/app")

    import app.runtime as runtime

    monkeypatch.setattr(runtime, "PostgresPolicyRepository", RecordingPolicyRepository)
    monkeypatch.setattr(runtime, "PostgresQueryLogRepository", RecordingQueryLogRepository)
    monkeypatch.setattr(runtime, "PostgresEvalRunRepository", RecordingEvalRunRepository)

    services = runtime.build_services_from_env()

    assert services.repository.__class__ is RecordingPolicyRepository
    assert services.query_log_repository.__class__ is RecordingQueryLogRepository
    assert created == {
        "policy_dsn": "postgresql://example/app",
        "query_log_dsn": "postgresql://example/app",
        "eval_run_dsn": "postgresql://example/app",
    }


def test_services_close_each_shared_runtime_component_once():
    class Closable:
        def __init__(self) -> None:
            self.close_count = 0

        def close(self) -> None:
            self.close_count += 1

    shared = Closable()
    separate = Closable()
    services = PolicyRagServices(
        repository=shared,
        query_log_repository=shared,
        eval_run_repository=separate,
    )

    services.close()

    assert shared.close_count == 1
    assert separate.close_count == 1


@pytest.mark.asyncio
async def test_app_lifespan_closes_runtime_services_once(monkeypatch):
    class RecordingServices:
        def __init__(self) -> None:
            self.close_count = 0

        def close(self) -> None:
            self.close_count += 1

    services = RecordingServices()

    import app.main as main

    monkeypatch.setattr(main, "build_services_from_env", lambda: services)
    app = main.create_app(seed_demo=False)

    async with app.router.lifespan_context(app):
        assert services.close_count == 0

    assert services.close_count == 1
