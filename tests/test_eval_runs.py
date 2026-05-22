from datetime import datetime, timezone

import pytest

from app.eval_runs import InMemoryEvalRunRepository, PostgresEvalRunRepository
from app.models import EvalCaseResult, EvalRunResponse
import app.eval_runs as eval_runs_module


class RecordingConnection:
    def __init__(self, rows_by_query: dict[str, list[dict[str, object]]] | None = None) -> None:
        self.rows_by_query = rows_by_query or {}
        self.statements: list[tuple[str, tuple[object, ...]]] = []
        self.committed = False

    def cursor(self, **_kwargs):
        return RecordingCursor(self)

    def commit(self) -> None:
        self.committed = True


class RecordingCursor:
    def __init__(self, connection: RecordingConnection) -> None:
        self.connection = connection
        self.rows: list[dict[str, object]] = []

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> None:
        normalized = " ".join(sql.split())
        self.connection.statements.append((normalized, params or ()))
        if "FROM eval_runs" in normalized:
            self.rows = self.connection.rows_by_query.get("eval_runs", [])
        elif "FROM eval_case_results" in normalized:
            self.rows = self.connection.rows_by_query.get("eval_case_results", [])

    def fetchall(self):
        return self.rows


def test_in_memory_eval_run_repository_lists_latest_first():
    repository = InMemoryEvalRunRepository()
    first = _eval_run("eval_1", created_at="2026-05-21T09:00:00+09:00")
    second = _eval_run("eval_2", created_at="2026-05-21T09:01:00+09:00")

    repository.add_eval_run(first)
    repository.add_eval_run(second)

    assert [run.id for run in repository.list_eval_runs("acme")] == ["eval_2", "eval_1"]


def test_postgres_eval_run_repository_requires_psycopg_when_connection_is_not_injected(monkeypatch):
    monkeypatch.setattr(eval_runs_module, "psycopg", None)

    with pytest.raises(RuntimeError, match="psycopg is required"):
        PostgresEvalRunRepository()


def test_postgres_eval_run_repository_inserts_run_and_cases():
    connection = RecordingConnection()
    repository = PostgresEvalRunRepository(connection=connection)

    repository.add_eval_run(_eval_run("eval_1"))

    statements = [statement for statement, _params in connection.statements]
    assert statements[0].startswith("INSERT INTO workspaces")
    assert statements[1].startswith("INSERT INTO eval_runs")
    assert statements[2].startswith("INSERT INTO eval_case_results")
    assert connection.committed is True


def test_postgres_eval_run_repository_maps_runs_with_cases():
    connection = RecordingConnection(
        rows_by_query={
            "eval_runs": [
                {
                    "id": "eval_1",
                    "workspace_id": "acme",
                    "dataset_id": "golden-demo",
                    "provider": "fake",
                    "case_count": 1,
                    "retrieval_hit_rate": 1.0,
                    "citation_coverage": 1.0,
                    "created_at": datetime(2026, 5, 21, 0, 0, tzinfo=timezone.utc),
                }
            ],
            "eval_case_results": [
                {
                    "case_id": "security-incident",
                    "question": "security incident evidence",
                    "user_id": "mina-security",
                    "expected_document_ids": ["doc_1"],
                    "retrieved_document_ids": ["doc_1"],
                    "citation_document_ids": ["doc_1"],
                    "retrieval_hit": True,
                    "citation_covered": True,
                }
            ],
        }
    )
    repository = PostgresEvalRunRepository(connection=connection)

    runs = repository.list_eval_runs("acme", limit=5)

    assert len(runs) == 1
    assert runs[0].id == "eval_1"
    assert runs[0].cases[0].case_id == "security-incident"
    assert connection.statements[0][1] == ("acme", 5)
    assert connection.statements[1][1] == ("eval_1",)


def _eval_run(run_id: str, created_at: str = "2026-05-21T09:00:00+09:00") -> EvalRunResponse:
    return EvalRunResponse(
        id=run_id,
        workspace_id="acme",
        dataset_id="golden-demo",
        provider="fake",
        case_count=1,
        retrieval_hit_rate=1.0,
        citation_coverage=1.0,
        created_at=created_at,
        cases=[
            EvalCaseResult(
                case_id="security-incident",
                question="security incident evidence",
                user_id="mina-security",
                expected_document_ids=["doc_1"],
                retrieved_document_ids=["doc_1"],
                citation_document_ids=["doc_1"],
                retrieval_hit=True,
                citation_covered=True,
            )
        ],
    )
