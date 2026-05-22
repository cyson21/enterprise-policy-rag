from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from math import ceil
from typing import Any, Protocol
from uuid import uuid4

from app.models import (
    AnswerResponse,
    MetricsSummaryResponse,
    QueryAnswerSnapshot,
    QueryCitationSnapshot,
    QueryDetailResponse,
    QueryLogCreate,
    QueryRetrievalSnapshot,
    QueryTrendPoint,
    RecentQueriesResponse,
    RecentQuery,
    RetrievalResult,
    StoredQueryLog,
    TopEvidenceItem,
)

try:
    import psycopg
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    psycopg = None
    dict_row = None


class QueryLogRepository(Protocol):
    def add_query_log(self, entry: QueryLogCreate) -> StoredQueryLog:
        """Persist one query log row."""

    def list_query_logs(self, workspace_id: str, limit: int | None = None) -> list[StoredQueryLog]:
        """Return recent query logs for a workspace."""

    def get_query_detail(self, workspace_id: str, query_id: str) -> QueryDetailResponse | None:
        """Return one query log with stored evidence snapshots."""

    def add_retrieval_results(self, query_log_id: str, results: Sequence[RetrievalResult]) -> None:
        """Persist retrieved chunks for one query log."""

    def add_answer_record(self, query_log_id: str, response: AnswerResponse) -> None:
        """Persist answer metadata and citations for one query log."""

    def list_top_evidence(self, workspace_id: str, limit: int = 10) -> list[TopEvidenceItem]:
        """Return top evidence documents for Operations."""

    def list_query_trend(self, workspace_id: str, limit: int = 14) -> list[QueryTrendPoint]:
        """Return daily query trend points."""


class InMemoryQueryLogRepository:
    def __init__(self) -> None:
        self._sequence = 0
        self._answer_sequence = 0
        self._logs: list[StoredQueryLog] = []
        self._retrieval_results: list[dict[str, object]] = []
        self._citations: list[dict[str, object]] = []
        self._answers: list[dict[str, object]] = []

    def add_query_log(self, entry: QueryLogCreate) -> StoredQueryLog:
        self._sequence += 1
        stored = StoredQueryLog(
            id=f"query_{self._sequence:03d}",
            **entry.model_dump(exclude={"created_at"}),
            created_at=entry.created_at or _utc_now(),
        )
        self._logs.append(stored)
        return stored

    def list_query_logs(self, workspace_id: str, limit: int | None = None) -> list[StoredQueryLog]:
        logs = [log for log in reversed(self._logs) if log.workspace_id == workspace_id]
        if limit is None:
            return logs
        return logs[:limit]

    def add_retrieval_results(self, query_log_id: str, results: Sequence[RetrievalResult]) -> None:
        for result in results:
            self._retrieval_results.append(
                {
                    "query_log_id": query_log_id,
                    "workspace_id": result.workspace_id,
                    "rank": result.rank,
                    "chunk_id": result.chunk_id,
                    "document_id": result.document_id,
                    "title": result.title,
                    "source_uri": result.source_uri,
                    "score": result.score,
                    "access_reason": result.access_reason,
                }
            )

    def add_answer_record(self, query_log_id: str, response: AnswerResponse) -> None:
        log = self._find_log(query_log_id)
        if log is None:
            return
        self._answer_sequence += 1
        answer_id = f"answer_{self._answer_sequence:03d}"
        self._answers.append(
            {
                "id": answer_id,
                "query_log_id": query_log_id,
                "workspace_id": log.workspace_id,
                "answer": response.answer,
                "refusal_reason": response.refusal_reason,
                "provider": response.provider,
                "token_count": response.token_count,
                "estimated_cost_usd": response.estimated_cost_usd,
                "latency_ms": response.latency_ms,
            }
        )
        for citation in response.citations:
            self._citations.append(
                {
                    "answer_id": answer_id,
                    "query_log_id": query_log_id,
                    "workspace_id": log.workspace_id,
                    "rank": citation.rank,
                    "chunk_id": citation.chunk_id,
                    "document_id": citation.document_id,
                    "title": citation.title,
                    "source_uri": citation.source_uri,
                    "quote": citation.quote,
                    "score": citation.score,
                }
            )

    def list_top_evidence(self, workspace_id: str, limit: int = 10) -> list[TopEvidenceItem]:
        by_document: dict[str, dict[str, object]] = {}
        for row in self._retrieval_results:
            if row["workspace_id"] == workspace_id:
                _merge_evidence_row(by_document, row, retrieval_increment=1, citation_increment=0)
        for row in self._citations:
            if row["workspace_id"] == workspace_id:
                _merge_evidence_row(by_document, row, retrieval_increment=0, citation_increment=1)
        items = [_top_evidence_from_aggregate(document_id, row) for document_id, row in by_document.items()]
        items.sort(key=lambda item: (-item.citation_count, -item.retrieval_count, -item.avg_score, item.title))
        return items[:limit]

    def list_query_trend(self, workspace_id: str, limit: int = 14) -> list[QueryTrendPoint]:
        by_date: dict[str, dict[str, int]] = {}
        for log in self._logs:
            if log.workspace_id != workspace_id:
                continue
            bucket = (log.created_at or "")[:10] or "unknown"
            row = by_date.setdefault(
                bucket,
                {
                    "retrieval_count": 0,
                    "answer_count": 0,
                    "zero_result_count": 0,
                    "latency_sum": 0,
                    "latency_count": 0,
                },
            )
            if log.mode == "retrieval":
                row["retrieval_count"] += 1
            elif log.mode == "answer":
                row["answer_count"] += 1
            if log.retrieved_count == 0:
                row["zero_result_count"] += 1
            row["latency_sum"] += log.latency_ms
            row["latency_count"] += 1
        points = [_trend_point(date, row) for date, row in sorted(by_date.items())]
        return points[-limit:]

    def get_query_detail(self, workspace_id: str, query_id: str) -> QueryDetailResponse | None:
        log = self._find_log(query_id)
        if log is None or log.workspace_id != workspace_id:
            return None
        answer_rows = [row for row in self._answers if row["query_log_id"] == query_id and row["workspace_id"] == workspace_id]
        retrieval_rows = [
            row for row in self._retrieval_results if row["query_log_id"] == query_id and row["workspace_id"] == workspace_id
        ]
        citation_rows = [row for row in self._citations if row["query_log_id"] == query_id and row["workspace_id"] == workspace_id]
        retrieval_rows.sort(key=lambda row: int(row["rank"]))
        citation_rows.sort(key=lambda row: int(row["rank"]))
        return QueryDetailResponse(
            query=_recent_query_from_log(log),
            retrieval_results=[_retrieval_snapshot_from_row(row) for row in retrieval_rows],
            answer=_answer_snapshot_from_row(answer_rows[0]) if answer_rows else None,
            citations=[_citation_snapshot_from_row(row) for row in citation_rows],
        )

    def _find_log(self, query_log_id: str) -> StoredQueryLog | None:
        for log in self._logs:
            if log.id == query_log_id:
                return log
        return None


class PostgresQueryLogRepository:
    def __init__(self, dsn: str | None = None, connection: Any | None = None) -> None:
        if connection is None:
            if psycopg is None:
                raise RuntimeError("psycopg is required to use PostgresQueryLogRepository")
            connection = psycopg.connect(dsn)
        self._connection = connection

    def add_query_log(self, entry: QueryLogCreate) -> StoredQueryLog:
        log_id = f"query_{uuid4().hex}"
        created_at = entry.created_at or _utc_now()
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO workspaces (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (entry.workspace_id, entry.workspace_id),
            )
            cursor.execute(
                """
                INSERT INTO query_logs (
                    id, workspace_id, user_id, query, mode, latency_ms,
                    retrieved_count, top_score, provider, token_count,
                    estimated_cost_usd, refusal_reason, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    log_id,
                    entry.workspace_id,
                    entry.user_id,
                    entry.query,
                    entry.mode,
                    entry.latency_ms,
                    entry.retrieved_count,
                    entry.top_score,
                    entry.provider,
                    entry.token_count,
                    entry.estimated_cost_usd,
                    entry.refusal_reason,
                    created_at,
                ),
            )
        self._connection.commit()
        return StoredQueryLog(id=log_id, **entry.model_dump(exclude={"created_at"}), created_at=created_at)

    def list_query_logs(self, workspace_id: str, limit: int | None = None) -> list[StoredQueryLog]:
        params: tuple[object, ...]
        limit_clause = ""
        if limit is None:
            params = (workspace_id,)
        else:
            limit_clause = "LIMIT %s"
            params = (workspace_id, limit)

        with self._cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    id, workspace_id, user_id, query, mode, latency_ms,
                    retrieved_count, top_score, provider, token_count,
                    estimated_cost_usd, refusal_reason, created_at
                FROM query_logs
                WHERE workspace_id = %s
                ORDER BY created_at DESC, id DESC
                {limit_clause}
                """,
                params,
            )
            return [_query_log_from_row(row) for row in cursor.fetchall()]

    def get_query_detail(self, workspace_id: str, query_id: str) -> QueryDetailResponse | None:
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id, workspace_id, user_id, query, mode, latency_ms,
                    retrieved_count, top_score, provider, token_count,
                    estimated_cost_usd, refusal_reason, created_at
                FROM query_logs
                WHERE workspace_id = %s AND id = %s
                """,
                (workspace_id, query_id),
            )
            log_row = cursor.fetchone()
            if log_row is None:
                return None
            log = _query_log_from_row(log_row)

            cursor.execute(
                """
                SELECT rank, chunk_id, document_id, title, source_uri, score, access_reason
                FROM retrieval_results
                WHERE workspace_id = %s AND query_log_id = %s
                ORDER BY rank ASC
                """,
                (workspace_id, query_id),
            )
            retrieval_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT
                    answer_text AS answer, refusal_reason, provider, token_count,
                    estimated_cost_usd, latency_ms
                FROM answers
                WHERE workspace_id = %s AND query_log_id = %s
                """,
                (workspace_id, query_id),
            )
            answer_row = cursor.fetchone()

            cursor.execute(
                """
                SELECT rank, chunk_id, document_id, title, source_uri, quote_text AS quote, score
                FROM citations
                WHERE workspace_id = %s AND query_log_id = %s
                ORDER BY rank ASC
                """,
                (workspace_id, query_id),
            )
            citation_rows = cursor.fetchall()

        return QueryDetailResponse(
            query=_recent_query_from_log(log),
            retrieval_results=[_retrieval_snapshot_from_row(row) for row in retrieval_rows],
            answer=_answer_snapshot_from_row(answer_row) if answer_row else None,
            citations=[_citation_snapshot_from_row(row) for row in citation_rows],
        )

    def add_retrieval_results(self, query_log_id: str, results: Sequence[RetrievalResult]) -> None:
        with self._cursor() as cursor:
            for result in results:
                cursor.execute(
                    """
                    INSERT INTO retrieval_results (
                        id, query_log_id, workspace_id, chunk_id, document_id, title,
                        source_uri, rank, score, access_reason
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        f"retrieval_result_{uuid4().hex}",
                        query_log_id,
                        result.workspace_id,
                        result.chunk_id,
                        result.document_id,
                        result.title,
                        result.source_uri,
                        result.rank,
                        result.score,
                        result.access_reason,
                    ),
                )
        self._connection.commit()

    def add_answer_record(self, query_log_id: str, response: AnswerResponse) -> None:
        answer_id = f"answer_{uuid4().hex}"
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT workspace_id
                FROM query_logs
                WHERE id = %s
                """,
                (query_log_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return
            workspace_id = row["workspace_id"]
            cursor.execute(
                """
                INSERT INTO answers (
                    id, query_log_id, workspace_id, answer_text, refusal_reason,
                    provider, token_count, estimated_cost_usd, latency_ms
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    answer_id,
                    query_log_id,
                    workspace_id,
                    response.answer,
                    response.refusal_reason,
                    response.provider,
                    response.token_count,
                    response.estimated_cost_usd,
                    response.latency_ms,
                ),
            )
            for citation in response.citations:
                cursor.execute(
                    """
                    INSERT INTO citations (
                        id, answer_id, query_log_id, workspace_id, rank, chunk_id,
                        document_id, title, source_uri, quote_text, score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        f"citation_{uuid4().hex}",
                        answer_id,
                        query_log_id,
                        workspace_id,
                        citation.rank,
                        citation.chunk_id,
                        citation.document_id,
                        citation.title,
                        citation.source_uri,
                        citation.quote,
                        citation.score,
                    ),
                )
        self._connection.commit()

    def list_top_evidence(self, workspace_id: str, limit: int = 10) -> list[TopEvidenceItem]:
        with self._cursor() as cursor:
            cursor.execute(
                """
                WITH evidence AS (
                    SELECT workspace_id, document_id, title, source_uri, score, 1 AS retrieval_count, 0 AS citation_count
                    FROM retrieval_results
                    UNION ALL
                    SELECT workspace_id, document_id, title, source_uri, score, 0 AS retrieval_count, 1 AS citation_count
                    FROM citations
                )
                SELECT
                    document_id,
                    title,
                    MAX(source_uri) AS source_uri,
                    SUM(retrieval_count) AS retrieval_count,
                    SUM(citation_count) AS citation_count,
                    AVG(score) AS avg_score
                FROM evidence
                WHERE workspace_id = %s
                GROUP BY document_id, title
                ORDER BY citation_count DESC, retrieval_count DESC, avg_score DESC, title ASC
                LIMIT %s
                """,
                (workspace_id, limit),
            )
            return [_top_evidence_from_row(row) for row in cursor.fetchall()]

    def list_query_trend(self, workspace_id: str, limit: int = 14) -> list[QueryTrendPoint]:
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM (
                    SELECT
                        DATE(created_at) AS date,
                        COUNT(*) FILTER (WHERE mode = 'retrieval') AS retrieval_count,
                        COUNT(*) FILTER (WHERE mode = 'answer') AS answer_count,
                        COUNT(*) FILTER (WHERE retrieved_count = 0) AS zero_result_count,
                        AVG(latency_ms) AS avg_latency_ms
                    FROM query_logs
                    WHERE workspace_id = %s
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at) DESC
                    LIMIT %s
                ) trend_points
                ORDER BY date ASC
                """,
                (workspace_id, limit),
            )
            return [_trend_point_from_row(row) for row in cursor.fetchall()]

    def _cursor(self) -> Any:
        if dict_row is None:
            return self._connection.cursor()
        return self._connection.cursor(row_factory=dict_row)


def build_metrics_summary(workspace_id: str, logs: Sequence[StoredQueryLog]) -> MetricsSummaryResponse:
    if not logs:
        return MetricsSummaryResponse(
            workspace_id=workspace_id,
            searches=0,
            p95_latency_ms=0,
            estimated_cost_usd=0.0,
            retrieval_hit_rate=0.0,
            zero_result_rate=0.0,
            provider="fake",
        )

    searches = len(logs)
    hit_count = sum(1 for log in logs if log.retrieved_count > 0)
    zero_count = searches - hit_count
    providers = sorted({log.provider for log in logs})
    return MetricsSummaryResponse(
        workspace_id=workspace_id,
        searches=searches,
        p95_latency_ms=_nearest_rank_p95([log.latency_ms for log in logs]),
        estimated_cost_usd=round(sum(log.estimated_cost_usd for log in logs), 6),
        retrieval_hit_rate=round(hit_count / searches, 4),
        zero_result_rate=round(zero_count / searches, 4),
        provider=providers[0] if len(providers) == 1 else "mixed",
    )


def build_recent_queries(logs: Sequence[StoredQueryLog]) -> RecentQueriesResponse:
    return RecentQueriesResponse(
        queries=[_recent_query_from_log(log) for log in logs]
    )


def _nearest_rank_p95(values: Sequence[int]) -> int:
    ordered = sorted(values)
    index = max(0, ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _recent_query_from_log(log: StoredQueryLog) -> RecentQuery:
    return RecentQuery(
        id=log.id,
        workspace_id=log.workspace_id,
        user_id=log.user_id,
        query=log.query,
        mode=log.mode,
        latency_ms=log.latency_ms,
        retrieved_count=log.retrieved_count,
        top_score=log.top_score,
        provider=log.provider,
        created_at=log.created_at or "",
    )


def _merge_evidence_row(
    by_document: dict[str, dict[str, object]],
    row: dict[str, object],
    *,
    retrieval_increment: int,
    citation_increment: int,
) -> None:
    document_id = str(row["document_id"])
    aggregate = by_document.setdefault(
        document_id,
        {
            "title": row["title"],
            "source_uri": row["source_uri"],
            "retrieval_count": 0,
            "citation_count": 0,
            "score_sum": 0.0,
            "score_count": 0,
        },
    )
    aggregate["retrieval_count"] = int(aggregate["retrieval_count"]) + retrieval_increment
    aggregate["citation_count"] = int(aggregate["citation_count"]) + citation_increment
    aggregate["score_sum"] = float(aggregate["score_sum"]) + float(row["score"])
    aggregate["score_count"] = int(aggregate["score_count"]) + 1


def _top_evidence_from_aggregate(document_id: str, row: dict[str, object]) -> TopEvidenceItem:
    score_count = int(row["score_count"])
    avg_score = float(row["score_sum"]) / score_count if score_count else 0.0
    return TopEvidenceItem(
        document_id=document_id,
        title=str(row["title"]),
        source_uri=row["source_uri"] if row["source_uri"] is None else str(row["source_uri"]),
        retrieval_count=int(row["retrieval_count"]),
        citation_count=int(row["citation_count"]),
        avg_score=round(avg_score, 6),
    )


def _top_evidence_from_row(row: dict[str, Any]) -> TopEvidenceItem:
    return TopEvidenceItem(
        document_id=row["document_id"],
        title=row["title"],
        source_uri=row["source_uri"],
        retrieval_count=int(row["retrieval_count"]),
        citation_count=int(row["citation_count"]),
        avg_score=round(float(row["avg_score"]), 6),
    )


def _retrieval_snapshot_from_row(row: dict[str, Any]) -> QueryRetrievalSnapshot:
    return QueryRetrievalSnapshot(
        rank=int(row["rank"]),
        chunk_id=str(row["chunk_id"]),
        document_id=str(row["document_id"]),
        title=str(row["title"]),
        source_uri=row["source_uri"] if row["source_uri"] is None else str(row["source_uri"]),
        score=round(float(row["score"]), 6),
        access_reason=str(row["access_reason"]),
    )


def _answer_snapshot_from_row(row: dict[str, Any]) -> QueryAnswerSnapshot:
    return QueryAnswerSnapshot(
        answer=row["answer"] if row["answer"] is None else str(row["answer"]),
        refusal_reason=row["refusal_reason"] if row["refusal_reason"] is None else str(row["refusal_reason"]),
        provider=str(row["provider"]),
        token_count=int(row["token_count"]),
        estimated_cost_usd=float(row["estimated_cost_usd"]),
        latency_ms=int(row["latency_ms"]),
    )


def _citation_snapshot_from_row(row: dict[str, Any]) -> QueryCitationSnapshot:
    return QueryCitationSnapshot(
        rank=int(row["rank"]),
        chunk_id=str(row["chunk_id"]),
        document_id=str(row["document_id"]),
        title=str(row["title"]),
        source_uri=row["source_uri"] if row["source_uri"] is None else str(row["source_uri"]),
        quote=str(row["quote"]),
        score=round(float(row["score"]), 6),
    )


def _trend_point(date: str, row: dict[str, int]) -> QueryTrendPoint:
    latency_count = row["latency_count"]
    return QueryTrendPoint(
        date=date,
        retrieval_count=row["retrieval_count"],
        answer_count=row["answer_count"],
        zero_result_count=row["zero_result_count"],
        avg_latency_ms=round(row["latency_sum"] / latency_count) if latency_count else 0,
    )


def _trend_point_from_row(row: dict[str, Any]) -> QueryTrendPoint:
    return QueryTrendPoint(
        date=str(row["date"]),
        retrieval_count=int(row["retrieval_count"]),
        answer_count=int(row["answer_count"]),
        zero_result_count=int(row["zero_result_count"]),
        avg_latency_ms=round(float(row["avg_latency_ms"] or 0)),
    )


def _query_log_from_row(row: dict[str, Any]) -> StoredQueryLog:
    created_at = row["created_at"]
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    return StoredQueryLog(
        id=row["id"],
        workspace_id=row["workspace_id"],
        user_id=row["user_id"],
        query=row["query"],
        mode=row["mode"],
        latency_ms=row["latency_ms"],
        retrieved_count=row["retrieved_count"],
        top_score=float(row["top_score"]),
        provider=row["provider"],
        token_count=row["token_count"],
        estimated_cost_usd=float(row["estimated_cost_usd"]),
        refusal_reason=row["refusal_reason"],
        created_at=created_at,
    )
