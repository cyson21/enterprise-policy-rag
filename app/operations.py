from __future__ import annotations

from app.models import QueryLogCreate
from app.services import PolicyRagServices


DEMO_QUERY_LOGS = [
    QueryLogCreate(
        workspace_id="acme",
        user_id="mina-security",
        query="security incident evidence",
        mode="retrieval",
        latency_ms=142,
        retrieved_count=2,
        top_score=0.603023,
        provider="fake",
        created_at="2026-05-21T08:42:00+09:00",
    ),
    QueryLogCreate(
        workspace_id="acme",
        user_id="joon-finance",
        query="meal reimbursement receipt",
        mode="retrieval",
        latency_ms=118,
        retrieved_count=1,
        top_score=0.512401,
        provider="fake",
        created_at="2026-05-21T08:35:00+09:00",
    ),
    QueryLogCreate(
        workspace_id="acme",
        user_id="hana-people",
        query="executive access exception",
        mode="retrieval",
        latency_ms=166,
        retrieved_count=0,
        top_score=0.0,
        provider="fake",
        created_at="2026-05-21T08:21:00+09:00",
    ),
]


def seed_demo_query_logs(services: PolicyRagServices) -> None:
    # 초기 화면에서 메트릭과 최근 쿼리 목록이 비지 않도록 데모 로그를 사전 주입한다.
    for log in DEMO_QUERY_LOGS:
        services.query_log_repository.add_query_log(log)
