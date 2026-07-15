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
        # 메모리 기반에서는 최근 실행 이력을 실행 순서를 뒤집어 최신 우선으로 조회한다.
        self._runs: list[EvalRunResponse] = []

    def add_eval_run(self, run: EvalRunResponse) -> EvalRunResponse:
        # 테스트 재현성 유지를 위해 수신한 run을 있는 그대로 저장해 반환한다.
        self._runs.append(run)
        return run

    def list_eval_runs(self, workspace_id: str, limit: int | None = None) -> list[EvalRunResponse]:
        # 동일 워크스페이스 기준으로 조회하고, limit이 있으면 상위 항목만 잘라 낸다.
        runs = [run for run in reversed(self._runs) if run.workspace_id == workspace_id]
        if limit is None:
            return runs
        return runs[:limit]


class PostgresEvalRunRepository:
    def __init__(self, dsn: str | None = None, connection: Any | None = None) -> None:
        self._owns_connection = connection is None
        if connection is None:
            if psycopg is None:
                raise RuntimeError("psycopg is required to use PostgresEvalRunRepository")
            connection = psycopg.connect(dsn)
        self._connection = connection

    def close(self) -> None:
        if self._owns_connection and not self._connection.closed:
            self._connection.close()

    def add_eval_run(self, run: EvalRunResponse) -> EvalRunResponse:
        # 평가 실행 결과는 eval_runs와 케이스를 분리 저장해 분석 쿼리의 조회 범위를 최소화한다.
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
        # 필요 시 limit를 붙여 최신 케이스 위주로 읽고, case 테이블은 run별로 보강 로드한다.
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
    # 운영/데모 시나리오에서 동일 형식 타임스탬프를 사용하도록 초 단위로 truncate 한다.
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _eval_run_from_row(row: dict[str, Any]) -> EvalRunResponse:
    # DB row와 Pydantic 모델 간 타입 정합성(특히 datetime/string) 차이를 보정한다.
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
    # 케이스 결과의 배열 필드는 null-safe하게 list로 정규화한다.
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
    # DB driver가 NULL을 None으로 전달해도 타입 안정성을 유지한다.
    return list(value or [])
