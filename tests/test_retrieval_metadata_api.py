import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_retrieval_api_returns_ui_metadata_and_access_reason():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/documents",
            json={
                "workspace_id": "acme",
                "title": "Security VPN",
                "source_uri": "policy://security-vpn",
                "content": "Security VPN rotation checklist for incident response.",
                "content_type": "text/plain",
                "owner_user_id": "owner-security",
                "department_ids": ["security"],
                "visibility": "department",
            },
        )

        response = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "vpn incident checklist",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["rank"] == 1
    assert result["title"] == "Security VPN"
    assert result["visibility"] == "department"
    assert result["department_ids"] == ["security"]
    assert result["access_reason"] == "department_match"
    assert "answer" not in response.json()


@pytest.mark.asyncio
async def test_score_threshold_filters_low_similarity_results():
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
                "owner_user_id": "owner-security",
                "department_ids": ["security"],
                "visibility": "public",
            },
        )

        low_threshold = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "vpn enrollment",
                "top_k": 5,
                "score_threshold": 0,
            },
        )
        high_threshold = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "vpn enrollment",
                "top_k": 5,
                "score_threshold": 1,
            },
        )

    assert len(low_threshold.json()["results"]) == 1
    assert high_threshold.json()["results"] == []


@pytest.mark.asyncio
async def test_demo_personas_return_different_results_for_same_query():
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        security_response = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "보안 사고 발생 시 누구에게 알려야 해?",
                "top_k": 5,
                "score_threshold": 0,
            },
        )
        finance_response = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "joon-finance",
                "department_ids": ["finance"],
                "query": "보안 사고 발생 시 누구에게 알려야 해?",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    security_titles = {result["title"] for result in security_response.json()["results"]}
    finance_titles = {result["title"] for result in finance_response.json()["results"]}
    assert "Security Incident Manual" in security_titles
    assert "Security Incident Manual" not in finance_titles
