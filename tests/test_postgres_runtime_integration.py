import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_TESTS") != "1",
    reason="set RUN_POSTGRES_TESTS=1 with DATABASE_URL to run PostgreSQL runtime integration",
)


@pytest.mark.asyncio
async def test_app_runtime_uses_postgres_for_documents_retrieval_and_query_logs(monkeypatch):
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag",
    )
    workspace_id = f"runtime-{uuid4().hex}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        created = await client.post(
            "/documents",
            json={
                "workspace_id": workspace_id,
                "title": "Runtime Security Manual",
                "source_uri": "policy://runtime-security",
                "content": "Runtime security incident evidence must be preserved.",
                "content_type": "text/plain",
                "owner_user_id": "mina-security",
                "department_ids": ["security"],
                "visibility": "department",
            },
        )
        retrieval = await client.post(
            "/retrieve",
            json={
                "workspace_id": workspace_id,
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
            },
        )
        recent = await client.get("/queries/recent", params={"workspace_id": workspace_id})
        query_id = recent.json()["queries"][0]["id"]
        detail = await client.get(f"/queries/{query_id}", params={"workspace_id": workspace_id})
        metrics = await client.get("/metrics/summary", params={"workspace_id": workspace_id})
        trend = await client.get("/metrics/trend", params={"workspace_id": workspace_id})
        evidence = await client.get("/evidence/top", params={"workspace_id": workspace_id})
        eval_run = await client.post(
            "/eval-runs",
            json={"workspace_id": workspace_id, "dataset_id": "golden-demo"},
        )
        eval_runs = await client.get("/eval-runs", params={"workspace_id": workspace_id})

    assert created.status_code == 201
    assert retrieval.status_code == 200
    assert retrieval.json()["results"][0]["title"] == "Runtime Security Manual"
    assert recent.status_code == 200
    assert recent.json()["queries"][0]["query"] == "security incident evidence"
    assert detail.status_code == 200
    assert detail.json()["query"]["id"] == query_id
    assert detail.json()["retrieval_results"][0]["title"] == "Runtime Security Manual"
    assert metrics.status_code == 200
    assert metrics.json()["searches"] == 1
    assert metrics.json()["retrieval_hit_rate"] == 1.0
    assert trend.status_code == 200
    assert trend.json()["points"][-1]["retrieval_count"] >= 1
    assert evidence.status_code == 200
    assert evidence.json()["items"][0]["title"] == "Runtime Security Manual"
    assert evidence.json()["items"][0]["retrieval_count"] == 1
    assert eval_run.status_code == 200
    assert eval_runs.status_code == 200
    assert eval_runs.json()["runs"][0]["id"] == eval_run.json()["id"]
    assert eval_runs.json()["runs"][0]["cases"]
