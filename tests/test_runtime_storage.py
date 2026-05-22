from app.query_logs import InMemoryQueryLogRepository
from app.repository import InMemoryPolicyRepository
from app.eval_runs import InMemoryEvalRunRepository


def test_build_services_from_env_uses_in_memory_repositories_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from app.runtime import build_services_from_env

    services = build_services_from_env()

    assert isinstance(services.repository, InMemoryPolicyRepository)
    assert isinstance(services.query_log_repository, InMemoryQueryLogRepository)
    assert isinstance(services.eval_run_repository, InMemoryEvalRunRepository)


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
