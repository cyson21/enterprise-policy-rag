# 답변 API 테스트: 허가된 사용자만 증거 기반 답변/인용문을 받는지 검증한다.
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_answer_api_returns_fake_answer_with_citations_from_allowed_retrieval():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
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

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "fake"
    assert body["refusal_reason"] is None
    assert body["answer"]
    assert body["retrieved_count"] >= 1
    assert body["token_count"] > 0
    assert body["estimated_cost_usd"] == 0.0
    assert body["latency_ms"] >= 0
    assert body["citations"][0]["title"] == "Security Incident Manual"
    assert "Security incident evidence" in body["citations"][0]["quote"]


@pytest.mark.asyncio
async def test_answer_api_keeps_retrieval_permission_filter_for_citations():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/answer",
            json={
                "workspace_id": "acme",
                "user_id": "joon-finance",
                "department_ids": ["finance"],
                "query": "security incident evidence",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    assert response.status_code == 200
    titles = {citation["title"] for citation in response.json()["citations"]}
    assert "Security Incident Manual" not in titles


@pytest.mark.asyncio
async def test_answer_api_refuses_when_no_evidence_is_available():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/answer",
            json={
                "workspace_id": "acme",
                "user_id": "hana-people",
                "department_ids": ["people"],
                "query": "nonexistent policy phrase",
                "top_k": 5,
                "score_threshold": 0.95,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] is None
    assert body["citations"] == []
    assert body["refusal_reason"] == "insufficient_evidence"
