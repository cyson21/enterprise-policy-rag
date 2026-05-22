from datetime import datetime, timezone

import pytest

from app.models import QueryLogCreate
from app.models import AnswerCitation, AnswerResponse, RetrievalResult, Visibility
import app.query_logs as query_logs_module
from app.query_logs import (
    InMemoryQueryLogRepository,
    PostgresQueryLogRepository,
    build_metrics_summary,
    build_recent_queries,
)


class RecordingConnection:
    def __init__(
        self,
        rows: list[dict[str, object]] | None = None,
        rows_by_query: dict[str, list[dict[str, object]]] | None = None,
    ) -> None:
        self.rows = rows or []
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
        if "SELECT workspace_id FROM query_logs" in normalized:
            self.rows = self.connection.rows_by_query.get("query_log", [])
        elif "WITH evidence AS" in normalized:
            self.rows = self.connection.rows_by_query.get("top_evidence", [])
        elif "DATE(created_at) AS date" in normalized:
            self.rows = self.connection.rows_by_query.get("query_trend", [])
        elif "FROM retrieval_results" in normalized:
            self.rows = self.connection.rows_by_query.get("retrieval_detail", [])
        elif "FROM answers" in normalized:
            self.rows = self.connection.rows_by_query.get("answer_detail", [])
        elif "FROM citations" in normalized:
            self.rows = self.connection.rows_by_query.get("citation_detail", [])
        elif "FROM query_logs" in normalized:
            self.rows = self.connection.rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


def test_in_memory_query_logs_build_recent_rows_and_metrics():
    repository = InMemoryQueryLogRepository()
    repository.add_query_log(
        QueryLogCreate(
            workspace_id="acme",
            user_id="mina-security",
            query="vpn enrollment",
            mode="retrieval",
            latency_ms=40,
            retrieved_count=1,
            top_score=0.75,
            provider="fake",
            created_at="2026-05-21T09:00:00+09:00",
        )
    )
    repository.add_query_log(
        QueryLogCreate(
            workspace_id="acme",
            user_id="hana-people",
            query="unknown policy",
            mode="answer",
            latency_ms=200,
            retrieved_count=0,
            top_score=0,
            provider="fake",
            token_count=3,
            created_at="2026-05-21T09:01:00+09:00",
        )
    )

    logs = repository.list_query_logs("acme")
    recent = build_recent_queries(logs)
    metrics = build_metrics_summary("acme", logs)

    assert [row.query for row in recent.queries] == ["unknown policy", "vpn enrollment"]
    assert recent.queries[0].mode == "answer"
    assert metrics.searches == 2
    assert metrics.p95_latency_ms == 200
    assert metrics.retrieval_hit_rate == 0.5
    assert metrics.zero_result_rate == 0.5


def test_in_memory_query_logs_store_evidence_details_for_top_evidence():
    repository = InMemoryQueryLogRepository()
    retrieval_log = repository.add_query_log(
        QueryLogCreate(
            workspace_id="acme",
            user_id="mina-security",
            query="security incident evidence",
            mode="retrieval",
            latency_ms=20,
            retrieved_count=1,
            top_score=0.91,
            provider="fake",
        )
    )
    repository.add_retrieval_results(
        retrieval_log.id,
        [
            RetrievalResult(
                rank=1,
                chunk_id="chunk_1",
                document_id="doc_1",
                workspace_id="acme",
                title="Security Incident Manual",
                source_uri="policy://security",
                chunk_index=0,
                text="Preserve evidence first.",
                score=0.91,
                visibility=Visibility.DEPARTMENT,
                department_ids=["security"],
                access_reason="department_match",
            )
        ],
    )
    answer_log = repository.add_query_log(
        QueryLogCreate(
            workspace_id="acme",
            user_id="mina-security",
            query="security incident evidence",
            mode="answer",
            latency_ms=40,
            retrieved_count=1,
            top_score=0.91,
            provider="fake",
        )
    )
    repository.add_answer_record(
        answer_log.id,
        AnswerResponse(
            query="security incident evidence",
            answer="Use the preserved evidence.",
            citations=[
                AnswerCitation(
                    rank=1,
                    chunk_id="chunk_1",
                    document_id="doc_1",
                    title="Security Incident Manual",
                    source_uri="policy://security",
                    quote="Preserve evidence first.",
                    score=0.91,
                )
            ],
            refusal_reason=None,
            provider="fake",
            token_count=32,
            estimated_cost_usd=0.0,
            latency_ms=40,
            retrieved_count=1,
        ),
    )

    top = repository.list_top_evidence("acme")

    assert len(top) == 1
    assert top[0].title == "Security Incident Manual"
    assert top[0].retrieval_count == 1
    assert top[0].citation_count == 1
    assert top[0].avg_score == 0.91


def test_in_memory_query_logs_return_query_detail_snapshots():
    repository = InMemoryQueryLogRepository()
    retrieval_log = repository.add_query_log(
        QueryLogCreate(
            workspace_id="acme",
            user_id="mina-security",
            query="security incident evidence",
            mode="retrieval",
            latency_ms=20,
            retrieved_count=1,
            top_score=0.91,
            provider="fake",
        )
    )
    repository.add_retrieval_results(
        retrieval_log.id,
        [
            RetrievalResult(
                rank=1,
                chunk_id="chunk_1",
                document_id="doc_1",
                workspace_id="acme",
                title="Security Incident Manual",
                source_uri="policy://security",
                chunk_index=0,
                text="Preserve evidence first.",
                score=0.91,
                visibility=Visibility.DEPARTMENT,
                department_ids=["security"],
                access_reason="department_match",
            )
        ],
    )

    detail = repository.get_query_detail("acme", retrieval_log.id)

    assert detail is not None
    assert detail.query.id == retrieval_log.id
    assert detail.retrieval_results[0].chunk_id == "chunk_1"
    assert detail.retrieval_results[0].access_reason == "department_match"
    assert detail.answer is None
    assert repository.get_query_detail("other", retrieval_log.id) is None


def test_postgres_query_log_repository_requires_psycopg_when_connection_is_not_injected(monkeypatch):
    monkeypatch.setattr(query_logs_module, "psycopg", None)

    with pytest.raises(RuntimeError, match="psycopg is required"):
        PostgresQueryLogRepository()


def test_postgres_query_log_repository_inserts_workspace_and_query_log():
    connection = RecordingConnection()
    repository = PostgresQueryLogRepository(connection=connection)

    stored = repository.add_query_log(
        QueryLogCreate(
            workspace_id="acme",
            user_id="mina-security",
            query="security incident evidence",
            mode="answer",
            latency_ms=123,
            retrieved_count=2,
            top_score=0.82,
            provider="fake",
            token_count=48,
            estimated_cost_usd=0.0,
            created_at="2026-05-21T09:02:00+09:00",
        )
    )

    assert stored.id.startswith("query_")
    assert stored.mode == "answer"
    assert connection.committed is True
    assert connection.statements[0][0].startswith("INSERT INTO workspaces")
    assert connection.statements[1][0].startswith("INSERT INTO query_logs")
    assert connection.statements[1][1][3] == "security incident evidence"
    assert connection.statements[1][1][4] == "answer"


def test_postgres_query_log_repository_maps_recent_rows():
    connection = RecordingConnection(
        rows=[
            {
                "id": "query_1",
                "workspace_id": "acme",
                "user_id": "mina-security",
                "query": "security incident evidence",
                "mode": "retrieval",
                "latency_ms": 88,
                "retrieved_count": 2,
                "top_score": 0.81,
                "provider": "fake",
                "token_count": 0,
                "estimated_cost_usd": 0,
                "refusal_reason": None,
                "created_at": datetime(2026, 5, 21, 0, 3, tzinfo=timezone.utc),
            }
        ]
    )
    repository = PostgresQueryLogRepository(connection=connection)

    logs = repository.list_query_logs("acme", limit=20)

    assert len(logs) == 1
    assert logs[0].query == "security incident evidence"
    assert logs[0].top_score == 0.81
    assert logs[0].created_at == "2026-05-21T00:03:00+00:00"
    assert connection.statements[0][1] == ("acme", 20)


def test_postgres_query_log_repository_persists_retrieval_results_and_answer_citations():
    connection = RecordingConnection(
        rows_by_query={
            "query_log": [
                {
                    "workspace_id": "acme",
                }
            ]
        }
    )
    repository = PostgresQueryLogRepository(connection=connection)

    repository.add_retrieval_results(
        "query_1",
        [
            RetrievalResult(
                rank=1,
                chunk_id="chunk_1",
                document_id="doc_1",
                workspace_id="acme",
                title="Security Incident Manual",
                source_uri="policy://security",
                chunk_index=0,
                text="Preserve evidence first.",
                score=0.91,
                visibility=Visibility.DEPARTMENT,
                department_ids=["security"],
                access_reason="department_match",
            )
        ],
    )
    repository.add_answer_record(
        "query_2",
        AnswerResponse(
            query="security incident evidence",
            answer="Use the preserved evidence.",
            citations=[
                AnswerCitation(
                    rank=1,
                    chunk_id="chunk_1",
                    document_id="doc_1",
                    title="Security Incident Manual",
                    source_uri="policy://security",
                    quote="Preserve evidence first.",
                    score=0.91,
                )
            ],
            refusal_reason=None,
            provider="fake",
            token_count=32,
            estimated_cost_usd=0,
            latency_ms=40,
            retrieved_count=1,
        ),
    )

    statements = [statement for statement, _params in connection.statements]
    assert any(statement.startswith("INSERT INTO retrieval_results") for statement in statements)
    assert any(statement.startswith("INSERT INTO answers") for statement in statements)
    assert any(statement.startswith("INSERT INTO citations") for statement in statements)
    assert connection.committed is True


def test_postgres_query_log_repository_maps_top_evidence_rows():
    connection = RecordingConnection(
        rows_by_query={
            "top_evidence": [
                {
                    "document_id": "doc_1",
                    "title": "Security Incident Manual",
                    "source_uri": "policy://security",
                    "retrieval_count": 3,
                    "citation_count": 2,
                    "avg_score": 0.91,
                }
            ]
        }
    )
    repository = PostgresQueryLogRepository(connection=connection)

    top = repository.list_top_evidence("acme", limit=5)

    assert len(top) == 1
    assert top[0].title == "Security Incident Manual"
    assert top[0].retrieval_count == 3
    assert top[0].citation_count == 2
    assert top[0].avg_score == 0.91
    assert connection.statements[0][1] == ("acme", 5)


def test_postgres_query_log_repository_maps_query_trend_rows():
    connection = RecordingConnection(
        rows_by_query={
            "query_trend": [
                {
                    "date": "2026-05-21",
                    "retrieval_count": 2,
                    "answer_count": 1,
                    "zero_result_count": 1,
                    "avg_latency_ms": 123.4,
                }
            ]
        }
    )
    repository = PostgresQueryLogRepository(connection=connection)

    points = repository.list_query_trend("acme", limit=14)

    assert len(points) == 1
    assert points[0].date == "2026-05-21"
    assert points[0].retrieval_count == 2
    assert points[0].answer_count == 1
    assert points[0].zero_result_count == 1
    assert points[0].avg_latency_ms == 123


def test_postgres_query_log_repository_maps_query_detail_rows():
    connection = RecordingConnection(
        rows=[
            {
                "id": "query_1",
                "workspace_id": "acme",
                "user_id": "mina-security",
                "query": "security incident evidence",
                "mode": "answer",
                "latency_ms": 88,
                "retrieved_count": 1,
                "top_score": 0.91,
                "provider": "fake",
                "token_count": 32,
                "estimated_cost_usd": 0,
                "refusal_reason": None,
                "created_at": datetime(2026, 5, 21, 0, 3, tzinfo=timezone.utc),
            }
        ],
        rows_by_query={
            "retrieval_detail": [
                {
                    "rank": 1,
                    "chunk_id": "chunk_1",
                    "document_id": "doc_1",
                    "title": "Security Incident Manual",
                    "source_uri": "policy://security",
                    "score": 0.91,
                    "access_reason": "department_match",
                }
            ],
            "answer_detail": [
                {
                    "answer": "Use the preserved evidence.",
                    "refusal_reason": None,
                    "provider": "fake",
                    "token_count": 32,
                    "estimated_cost_usd": 0,
                    "latency_ms": 88,
                }
            ],
            "citation_detail": [
                {
                    "rank": 1,
                    "chunk_id": "chunk_1",
                    "document_id": "doc_1",
                    "title": "Security Incident Manual",
                    "source_uri": "policy://security",
                    "quote": "Preserve evidence first.",
                    "score": 0.91,
                }
            ],
        },
    )
    repository = PostgresQueryLogRepository(connection=connection)

    detail = repository.get_query_detail("acme", "query_1")

    assert detail is not None
    assert detail.query.id == "query_1"
    assert detail.retrieval_results[0].title == "Security Incident Manual"
    assert detail.answer is not None
    assert detail.answer.provider == "fake"
    assert detail.citations[0].quote == "Preserve evidence first."
