import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_eval_run_api_returns_retrieval_and_citation_metrics():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/eval-runs", json={"workspace_id": "acme", "dataset_id": "golden-demo"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"].startswith("eval_")
    assert body["workspace_id"] == "acme"
    assert body["dataset_id"] == "golden-demo"
    assert body["provider"] == "fake"
    assert body["case_count"] == 3
    assert body["retrieval_hit_rate"] >= 0.66
    assert body["citation_coverage"] >= 0.66
    assert {case["case_id"] for case in body["cases"]} == {
        "security-incident",
        "finance-reimbursement",
        "executive-access",
    }


@pytest.mark.asyncio
async def test_eval_runs_api_lists_seeded_latest_run():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/eval-runs", params={"workspace_id": "acme"})

    assert response.status_code == 200
    runs = response.json()["runs"]
    assert len(runs) == 1
    assert runs[0]["dataset_id"] == "golden-demo"
    assert runs[0]["case_count"] == 3


@pytest.mark.asyncio
async def test_eval_run_api_persists_created_runs_for_history():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        first = await client.post("/eval-runs", json={"workspace_id": "acme", "dataset_id": "golden-demo"})
        second = await client.post("/eval-runs", json={"workspace_id": "acme", "dataset_id": "golden-demo"})
        response = await client.get("/eval-runs", params={"workspace_id": "acme"})

    assert first.status_code == 200
    assert second.status_code == 200
    runs = response.json()["runs"]
    assert len(runs) >= 2
    assert runs[0]["id"] != runs[1]["id"]
    assert runs[0]["cases"]
    assert runs[0]["dataset_id"] == "golden-demo"
