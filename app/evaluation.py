from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.eval_runs import utc_now
from app.models import AnswerQuery, EvalCaseResult, EvalRunRequest, EvalRunResponse, EvalRunsResponse
from app.services import PolicyRagServices


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    question: str
    user_id: str
    department_ids: list[str]
    expected_document_ids: list[str]


GOLDEN_CASES = [
    GoldenCase(
        case_id="security-incident",
        question="security incident evidence",
        user_id="mina-security",
        department_ids=["security"],
        expected_document_ids=["doc_2"],
    ),
    GoldenCase(
        case_id="finance-reimbursement",
        question="finance reimbursement requests",
        user_id="joon-finance",
        department_ids=["finance"],
        expected_document_ids=["doc_3"],
    ),
    GoldenCase(
        case_id="executive-access",
        question="executive access exceptions private approval",
        user_id="admin-platform",
        department_ids=["platform"],
        expected_document_ids=["doc_4"],
    ),
]


def run_eval(services: PolicyRagServices, request: EvalRunRequest) -> EvalRunResponse:
    cases = [_run_case(services, request.workspace_id, case) for case in GOLDEN_CASES]
    retrieval_hit_rate = _rate(case.retrieval_hit for case in cases)
    citation_coverage = _rate(case.citation_covered for case in cases)
    run = EvalRunResponse(
        id=f"eval_{request.dataset_id}_{uuid4().hex}",
        workspace_id=request.workspace_id,
        dataset_id=request.dataset_id,
        provider="fake",
        case_count=len(cases),
        retrieval_hit_rate=retrieval_hit_rate,
        citation_coverage=citation_coverage,
        created_at=utc_now(),
        cases=cases,
    )
    services.eval_run_repository.add_eval_run(run)
    return run


def list_eval_runs(services: PolicyRagServices, workspace_id: str) -> EvalRunsResponse:
    runs = services.eval_run_repository.list_eval_runs(workspace_id, limit=20)
    if not runs:
        runs = [run_eval(services, EvalRunRequest(workspace_id=workspace_id))]
    return EvalRunsResponse(runs=runs)


def _run_case(services: PolicyRagServices, workspace_id: str, case: GoldenCase) -> EvalCaseResult:
    answer = services.answer(
        AnswerQuery(
            workspace_id=workspace_id,
            user_id=case.user_id,
            department_ids=case.department_ids,
            query=case.question,
            top_k=5,
            score_threshold=0,
        )
    )
    citation_document_ids = [citation.document_id for citation in answer.citations]
    retrieved_document_ids = citation_document_ids
    retrieval_hit = _contains_expected(retrieved_document_ids, case.expected_document_ids)
    citation_covered = _contains_expected(citation_document_ids, case.expected_document_ids)
    return EvalCaseResult(
        case_id=case.case_id,
        question=case.question,
        user_id=case.user_id,
        expected_document_ids=case.expected_document_ids,
        retrieved_document_ids=retrieved_document_ids,
        citation_document_ids=citation_document_ids,
        retrieval_hit=retrieval_hit,
        citation_covered=citation_covered,
    )


def _contains_expected(actual: list[str], expected: list[str]) -> bool:
    return bool(set(actual).intersection(expected))


def _rate(values: object) -> float:
    items = list(values)
    if not items:
        return 0.0
    return round(sum(1 for item in items if item) / len(items), 4)
