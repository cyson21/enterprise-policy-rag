import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_metrics_summary_api_starts_empty_without_query_logs():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/metrics/summary", params={"workspace_id": "acme"})

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "workspace_id": "acme",
        "searches": 0,
        "p95_latency_ms": 0,
        "estimated_cost_usd": 0.0,
        "retrieval_hit_rate": 0.0,
        "zero_result_rate": 0.0,
        "provider": "fake",
    }


@pytest.mark.asyncio
async def test_retrieve_api_writes_recent_query_log_and_metrics():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/documents",
            json={
                "workspace_id": "acme",
                "title": "Remote Access",
                "source_uri": "policy://remote",
                "content": "Remote access requires VPN enrollment.",
                "content_type": "text/plain",
                "owner_user_id": "owner-1",
                "department_ids": ["security"],
                "visibility": "public",
            },
        )
        retrieval = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "vpn enrollment",
                "top_k": 3,
            },
        )
        recent = await client.get("/queries/recent", params={"workspace_id": "acme"})
        metrics = await client.get("/metrics/summary", params={"workspace_id": "acme"})

    assert retrieval.status_code == 200
    assert recent.status_code == 200
    rows = recent.json()["queries"]
    assert len(rows) == 1
    assert rows[0]["workspace_id"] == "acme"
    assert rows[0]["user_id"] == "mina-security"
    assert rows[0]["query"] == "vpn enrollment"
    assert rows[0]["mode"] == "retrieval"
    assert rows[0]["retrieved_count"] == 1
    assert rows[0]["top_score"] > 0
    assert rows[0]["provider"] == "fake"
    assert "answer" not in rows[0]

    assert metrics.status_code == 200
    summary = metrics.json()
    assert summary["searches"] == 1
    assert summary["retrieval_hit_rate"] == 1.0
    assert summary["zero_result_rate"] == 0.0


@pytest.mark.asyncio
async def test_answer_api_writes_answer_mode_query_log_with_cost_metadata():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        before = await client.get("/queries/recent", params={"workspace_id": "acme"})
        response = await client.post(
            "/answer",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
            },
        )
        after = await client.get("/queries/recent", params={"workspace_id": "acme"})
        metrics = await client.get("/metrics/summary", params={"workspace_id": "acme"})

    assert response.status_code == 200
    answer = response.json()
    before_rows = before.json()["queries"]
    after_rows = after.json()["queries"]
    assert len(after_rows) == len(before_rows) + 1
    assert after_rows[0]["query"] == "security incident evidence"
    assert after_rows[0]["mode"] == "answer"
    assert after_rows[0]["retrieved_count"] == answer["retrieved_count"]
    assert after_rows[0]["top_score"] == answer["citations"][0]["score"]
    assert after_rows[0]["provider"] == "fake"
    assert metrics.json()["searches"] == len(after_rows)


@pytest.mark.asyncio
async def test_evidence_top_api_counts_retrieval_results_and_answer_citations():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        retrieval = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
                "score_threshold": 0,
            },
        )
        answer = await client.post(
            "/answer",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
                "score_threshold": 0,
            },
        )
        evidence = await client.get("/evidence/top", params={"workspace_id": "acme"})

    assert retrieval.status_code == 200
    assert answer.status_code == 200
    assert evidence.status_code == 200
    items = evidence.json()["items"]
    security = next(item for item in items if item["title"] == "Security Incident Manual")
    assert security["retrieval_count"] >= 1
    assert security["citation_count"] >= 1
    assert security["avg_score"] > 0


@pytest.mark.asyncio
async def test_metrics_trend_api_groups_retrieval_and_answer_logs_by_date():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
            },
        )
        await client.post(
            "/answer",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
            },
        )
        response = await client.get("/metrics/trend", params={"workspace_id": "acme"})

    assert response.status_code == 200
    points = response.json()["points"]
    assert points
    latest = points[-1]
    assert latest["retrieval_count"] >= 1
    assert latest["answer_count"] >= 1
    assert latest["avg_latency_ms"] >= 0


@pytest.mark.asyncio
async def test_query_detail_api_returns_retrieval_snapshots_for_recent_row():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/documents",
            json={
                "workspace_id": "acme",
                "title": "Remote Access",
                "source_uri": "policy://remote",
                "content": "Remote access requires VPN enrollment.",
                "content_type": "text/plain",
                "owner_user_id": "owner-1",
                "department_ids": ["security"],
                "visibility": "public",
            },
        )
        await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "vpn enrollment",
                "top_k": 3,
            },
        )
        recent = await client.get("/queries/recent", params={"workspace_id": "acme"})
        query_id = recent.json()["queries"][0]["id"]
        detail = await client.get(f"/queries/{query_id}", params={"workspace_id": "acme"})
        wrong_workspace = await client.get(f"/queries/{query_id}", params={"workspace_id": "other"})

    assert detail.status_code == 200
    body = detail.json()
    assert body["query"]["id"] == query_id
    assert body["query"]["query"] == "vpn enrollment"
    assert body["answer"] is None
    assert body["citations"] == []
    assert body["retrieval_results"][0]["title"] == "Remote Access"
    assert body["retrieval_results"][0]["rank"] == 1
    assert body["retrieval_results"][0]["access_reason"] == "public"
    assert wrong_workspace.status_code == 404


@pytest.mark.asyncio
async def test_query_detail_api_returns_answer_and_citation_snapshots_for_answer_row():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/answer",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 3,
                "score_threshold": 0,
            },
        )
        recent = await client.get("/queries/recent", params={"workspace_id": "acme"})
        query_id = recent.json()["queries"][0]["id"]
        detail = await client.get(f"/queries/{query_id}", params={"workspace_id": "acme"})

    assert detail.status_code == 200
    body = detail.json()
    assert body["query"]["id"] == query_id
    assert body["query"]["mode"] == "answer"
    assert body["answer"]["provider"] == "fake"
    assert body["answer"]["token_count"] > 0
    assert body["answer"]["estimated_cost_usd"] == 0.0
    assert body["citations"]
    assert body["citations"][0]["title"] == "Security Incident Manual"
    assert body["citations"][0]["quote"]
