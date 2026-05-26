import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_auth_session_defaults_to_demo_context_without_credentials(monkeypatch):
    monkeypatch.delenv("AUTH_CONTEXT_PROVIDER", raising=False)
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/auth/session")

    assert response.status_code == 200
    assert response.json() == {
        "workspace_id": "acme",
        "user_id": "mina-security",
        "display_name": "Mina Kim",
        "department_ids": ["security"],
        "role": "employee",
        "auth_mode": "demo",
        "source": "demo_persona",
    }


@pytest.mark.asyncio
async def test_auth_session_maps_trusted_sso_headers(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/auth/session",
            headers={
                "x-enterprise-workspace-id": "acme",
                "x-enterprise-user-id": "joon-finance",
                "x-enterprise-display-name": "Joon Park",
                "x-enterprise-department-ids": " finance, security, finance ",
                "x-enterprise-role": "employee",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "workspace_id": "acme",
        "user_id": "joon-finance",
        "display_name": "Joon Park",
        "department_ids": ["finance", "security"],
        "role": "employee",
        "auth_mode": "trusted_headers",
        "source": "trusted_headers",
    }


@pytest.mark.asyncio
async def test_auth_retrieve_uses_session_context_instead_of_body_persona(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/auth/retrieve",
            headers={
                "x-enterprise-workspace-id": "acme",
                "x-enterprise-user-id": "joon-finance",
                "x-enterprise-display-name": "Joon Park",
                "x-enterprise-department-ids": "finance",
                "x-enterprise-role": "employee",
            },
            json={
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    assert response.status_code == 200
    titles = {result["title"] for result in response.json()["results"]}
    assert "Security Incident Manual" not in titles


@pytest.mark.asyncio
async def test_auth_answer_uses_session_context_for_citations(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/auth/answer",
            headers={
                "x-enterprise-workspace-id": "acme",
                "x-enterprise-user-id": "joon-finance",
                "x-enterprise-display-name": "Joon Park",
                "x-enterprise-department-ids": "finance",
                "x-enterprise-role": "employee",
            },
            json={
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    assert response.status_code == 200
    titles = {citation["title"] for citation in response.json()["citations"]}
    assert "Security Incident Manual" not in titles


@pytest.mark.asyncio
async def test_trusted_header_auth_requires_identity_headers(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/auth/session")

    assert response.status_code == 401
    assert response.json() == {"detail": "missing trusted identity headers"}
