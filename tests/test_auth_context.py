import time

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


OIDC_ISSUER = "https://idp.example.test/"
OIDC_AUDIENCE = "enterprise-policy-rag"
OIDC_SECRET = "local-oidc-secret-with-32-bytes-min"


def configure_oidc(monkeypatch: pytest.MonkeyPatch, *, secret: str = OIDC_SECRET) -> None:
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "oidc_jwt")
    monkeypatch.setenv("OIDC_ISSUER", OIDC_ISSUER)
    monkeypatch.setenv("OIDC_AUDIENCE", OIDC_AUDIENCE)
    monkeypatch.setenv("OIDC_HS256_SECRET", secret)


def make_oidc_token(
    *,
    secret: str = OIDC_SECRET,
    subject: str = "joon-finance",
    display_name: str = "Joon Park",
    department_ids: list[str] | None = None,
    role: str = "employee",
) -> str:
    now = int(time.time())
    claims = {
        "iss": OIDC_ISSUER,
        "aud": OIDC_AUDIENCE,
        "sub": subject,
        "name": display_name,
        "workspace_id": "acme",
        "department_ids": department_ids or ["finance"],
        "role": role,
        "iat": now,
        "exp": now + 300,
    }
    return jwt.encode(claims, secret, algorithm="HS256")


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


@pytest.mark.asyncio
async def test_auth_session_maps_oidc_jwt_bearer_token(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)
    token = make_oidc_token(department_ids=[" finance ", "security", "finance"], role="admin")

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/auth/session", headers={"authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "workspace_id": "acme",
        "user_id": "joon-finance",
        "display_name": "Joon Park",
        "department_ids": ["finance", "security"],
        "role": "admin",
        "auth_mode": "oidc_jwt",
        "source": OIDC_ISSUER,
    }


@pytest.mark.asyncio
async def test_auth_retrieve_uses_oidc_session_claims_instead_of_body_persona(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)
    token = make_oidc_token(subject="joon-finance", department_ids=["finance"], role="employee")

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/auth/retrieve",
            headers={"authorization": f"Bearer {token}"},
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
async def test_oidc_jwt_rejects_missing_bearer_token(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/auth/session")

    assert response.status_code == 401
    assert response.json() == {"detail": "missing bearer token"}


@pytest.mark.asyncio
async def test_oidc_jwt_rejects_invalid_signature(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)
    token = make_oidc_token(secret="wrong-secret-with-32-bytes-minimum")

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/auth/session", headers={"authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid oidc token"}
