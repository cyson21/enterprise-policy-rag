# 페르소나 API 테스트: 기본 데모 사용자 목록과 ID/권한 메타데이터 제공을 확인한다.
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_current_workspace_endpoint_returns_demo_workspace():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/workspaces/current")

    assert response.status_code == 200
    assert response.json() == {
        "id": "acme",
        "name": "ACME Enterprise",
        "environment": "local-demo",
        "provider": "fake",
    }


@pytest.mark.asyncio
async def test_personas_endpoint_returns_permission_demo_personas():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/personas")

    assert response.status_code == 200
    personas = response.json()["personas"]
    assert [persona["id"] for persona in personas] == [
        "mina-security",
        "joon-finance",
        "hana-people",
        "admin-platform",
    ]
    assert personas[0]["department_ids"] == ["security"]
    assert personas[-1]["role"] == "admin"
