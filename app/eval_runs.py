from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any, Protocol

from app.models import EvalCaseResult, EvalRunResponse

try:
    import psycopg
    from psycopg.rows import dict_row
except ModuleNotFoundError:
    psycopg = None
    dict_row = None


class EvalRunRepository(Protocol):
    def add_eval_run(self, run: EvalRunResponse) -> EvalRunResponse:
        """Persist one eval run and its case results."""

    def list_eval_runs(self, workspace_id: str, limit: int | None = None) -> list[EvalRunResponse]:
        """Return recent eval runs for a workspace."""


class InMemoryEvalRunRepository:
    def __init__(self) -> None:
        self._runs: list[EvalRunResponse] = []

    def add_eval_run(self, run: EvalRunResponse) -> EvalRunResponse:
        self._runs.append(run)
        return run

    def list_eval_runs(self, workspace_id: str, limit: int | None = None) -> list[EvalRunResponse]:
        runs = [run for run in reversed(self._runs) if run.workspace_id == workspace_id]
        if limit is None:
            return runs
        return runs[:limit]


class PostgresEvalRunRepository:
    def __init__(self, dsn: str | None = None, connection: Any | None = None) -> None:
        if connection is None:
            if psycopg is None:
                raise RuntimeError("psycopg is required to use PostgresEvalRunRepository")
            connection = psycopg.connect(dsn)
        self._connection = connection

    def add_eval_run(self, run: EvalRunResponse) -> EvalRunResponse:
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO workspaces (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (run.workspace_id, run.workspace_id),
            )
            cursor.execute(
                """
                INSERT INTO eval_runs (
                    id, workspace_id, dataset_id, provider, case_count,
                    retrieval_hit_rate, citation_coverage, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run.id,
                    run.workspace_id,
                    run.dataset_id,
                    run.provider,
                    run.case_count,
                    run.retrieval_hit_rate,
                    run.citation_coverage,
                    run.created_at,
                ),
            )
            for case in run.cases:
                cursor.execute(
                    """
                    INSERT INTO eval_case_results (
                        id, eval_run_id, workspace_id, case_id, question, user_id,
                        expected_document_ids, retrieved_document_ids, citation_document_ids,
                        retrieval_hit, citation_covered
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        f"{run.id}_{case.case_id}",
                        run.id,
                        run.workspace_id,
                        case.case_id,
                        case.question,
                        case.user_id,
                        case.expected_document_ids,
                        case.retrieved_document_ids,
                        case.citation_document_ids,
                        case.retrieval_hit,
                        case.citation_covered,
                    ),
                )
        self._connection.commit()
        return run

    def list_eval_runs(self, workspace_id: str, limit: int | None = None) -> list[EvalRunResponse]:
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
                    id, workspace_id, dataset_id, provider, case_count,
                    retrieval_hit_rate, citation_coverage, created_at
                FROM eval_runs
                WHERE workspace_id = %s
                ORDER BY created_at DESC, id DESC
                {limit_clause}
                """,
                params,
            )
            runs = [_eval_run_from_row(row) for row in cursor.fetchall()]
            for index, run in enumerate(runs):
                cursor.execute(
                    """
                    SELECT
                        case_id, question, user_id, expected_document_ids,
                        retrieved_document_ids, citation_document_ids,
                        retrieval_hit, citation_covered
                    FROM eval_case_results
                    WHERE eval_run_id = %s
                    ORDER BY case_id
                    """,
                    (run.id,),
                )
                runs[index] = run.model_copy(update={"cases": [_eval_case_from_row(row) for row in cursor.fetchall()]})
        return runs

    def _cursor(self) -> Any:
        if dict_row is None:
            return self._connection.cursor()
        return self._connection.cursor(row_factory=dict_row)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _eval_run_from_row(row: dict[str, Any]) -> EvalRunResponse:
    created_at = row["created_at"]
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    return EvalRunResponse(
        id=row["id"],
        workspace_id=row["workspace_id"],
        dataset_id=row["dataset_id"],
        provider=row["provider"],
        case_count=row["case_count"],
        retrieval_hit_rate=float(row["retrieval_hit_rate"]),
        citation_coverage=float(row["citation_coverage"]),
        created_at=created_at,
        cases=[],
    )


def _eval_case_from_row(row: dict[str, Any]) -> EvalCaseResult:
    return EvalCaseResult(
        case_id=row["case_id"],
        question=row["question"],
        user_id=row["user_id"],
        expected_document_ids=_list(row["expected_document_ids"]),
        retrieved_document_ids=_list(row["retrieved_document_ids"]),
        citation_document_ids=_list(row["citation_document_ids"]),
        retrieval_hit=row["retrieval_hit"],
        citation_covered=row["citation_covered"],
    )


def _list(value: Sequence[str] | None) -> list[str]:
    return list(value or [])
