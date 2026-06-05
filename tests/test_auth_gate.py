# 인증 강제 게이트 테스트: require_auth 모드에서 무인증 접근 차단, 본문 권한 컨텍스트 무시,
# workspace 스코프 강제를 검증한다. demo 모드(기본)는 기존 동작을 유지한다.
import time

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app

OIDC_ISSUER = "https://idp.example.test/"
OIDC_AUDIENCE = "enterprise-policy-rag"
OIDC_SECRET = "local-oidc-secret-with-32-bytes-min"


def configure_oidc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "oidc_jwt")
    monkeypatch.setenv("OIDC_ISSUER", OIDC_ISSUER)
    monkeypatch.setenv("OIDC_AUDIENCE", OIDC_AUDIENCE)
    monkeypatch.setenv("OIDC_HS256_SECRET", OIDC_SECRET)


def make_token(*, subject: str = "joon-finance", department_ids=None, workspace_id: str = "acme", role: str = "employee") -> str:
    now = int(time.time())
    claims = {
        "iss": OIDC_ISSUER,
        "aud": OIDC_AUDIENCE,
        "sub": subject,
        "name": subject,
        "workspace_id": workspace_id,
        "department_ids": department_ids or ["finance"],
        "role": role,
        "iat": now,
        "exp": now + 300,
    }
    return jwt.encode(claims, OIDC_SECRET, algorithm="HS256")


@pytest.mark.asyncio
async def test_retrieve_requires_auth_when_auth_mode_is_enforced(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "missing bearer token"}


@pytest.mark.asyncio
async def test_retrieve_ignores_body_permission_context_under_enforced_auth(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)
    token = make_token(subject="joon-finance", department_ids=["finance"])

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/retrieve",
            headers={"authorization": f"Bearer {token}"},
            json={
                "workspace_id": "acme",
                "user_id": "mina-security",
                "department_ids": ["security"],
                "query": "security incident evidence",
                "top_k": 5,
                "score_threshold": 0,
            },
        )

    assert response.status_code == 200
    titles = {result["title"] for result in response.json()["results"]}
    # 본문이 security 권한을 주장해도 세션(finance) 기준으로 필터되어 보안 전용 문서는 제외된다.
    assert "Security Incident Manual" not in titles


@pytest.mark.asyncio
async def test_workspace_scope_mismatch_is_rejected(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)
    token = make_token(workspace_id="acme")

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/documents",
            params={"workspace_id": "other"},
            headers={"authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "workspace scope mismatch"}


@pytest.mark.asyncio
async def test_metrics_requires_auth_under_enforced_auth(monkeypatch):
    configure_oidc(monkeypatch)
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/metrics/summary", params={"workspace_id": "acme"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rag_require_auth_flag_forces_demo_session_scope(monkeypatch):
    # demo provider는 항상 인증에 성공하지만, RAG_REQUIRE_AUTH=1이면 workspace 스코프를 강제한다.
    monkeypatch.delenv("AUTH_CONTEXT_PROVIDER", raising=False)
    monkeypatch.setenv("RAG_REQUIRE_AUTH", "1")
    app = create_app(seed_demo=True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        ok = await client.get("/metrics/summary", params={"workspace_id": "acme"})
        mismatch = await client.get("/metrics/summary", params={"workspace_id": "other"})

    assert ok.status_code == 200
    assert mismatch.status_code == 403


@pytest.mark.asyncio
async def test_demo_mode_keeps_open_endpoints(monkeypatch):
    # 기본 demo 모드는 인증 비강제 동작을 그대로 유지한다(회귀 방지).
    monkeypatch.delenv("AUTH_CONTEXT_PROVIDER", raising=False)
    monkeypatch.delenv("RAG_REQUIRE_AUTH", raising=False)
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/metrics/summary", params={"workspace_id": "acme"})

    assert response.status_code == 200


def test_demo_mode_emits_auth_not_enforced_warning(monkeypatch, caplog):
    monkeypatch.delenv("AUTH_CONTEXT_PROVIDER", raising=False)
    monkeypatch.delenv("RAG_REQUIRE_AUTH", raising=False)

    create_app(seed_demo=False)

    assert "RAG auth is not enforced" in caplog.text
