# 관리자 워크플로우 테스트: 문서 수정/삭제 시 권한 검증과 감사 로그 반영을 확인한다.
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


ADMIN_HEADERS = {
    "x-enterprise-workspace-id": "acme",
    "x-enterprise-user-id": "admin-platform",
    "x-enterprise-display-name": "Admin Choi",
    "x-enterprise-department-ids": "platform,security",
    "x-enterprise-role": "admin",
}

EMPLOYEE_HEADERS = {
    "x-enterprise-workspace-id": "acme",
    "x-enterprise-user-id": "mina-security",
    "x-enterprise-display-name": "Mina Kim",
    "x-enterprise-department-ids": "security",
    "x-enterprise-role": "employee",
}


async def ingest_document(client: AsyncClient) -> str:
    response = await client.post(
        "/documents",
        headers=ADMIN_HEADERS,
        json={
            "workspace_id": "acme",
            "title": "Draft VPN Policy",
            "source_uri": "policy://vpn-draft",
            "content": "Old VPN enrollment steps.",
            "content_type": "text/markdown",
            "owner_user_id": "admin-platform",
            "department_ids": ["platform"],
            "visibility": "private",
        },
    )
    assert response.status_code == 201
    return response.json()["document_id"]


@pytest.mark.asyncio
async def test_admin_can_replace_document_content_and_records_audit_log(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        document_id = await ingest_document(client)
        response = await client.patch(
            f"/admin/documents/{document_id}",
            headers=ADMIN_HEADERS,
            json={
                "title": "VPN Access Policy",
                "content": "New VPN enrollment requires device posture review.",
                "visibility": "department",
                "department_ids": ["security", "platform"],
            },
        )
        detail = await client.get("/admin/audit-logs", headers=ADMIN_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["document"]["id"] == document_id
    assert body["document"]["title"] == "VPN Access Policy"
    assert body["document"]["visibility"] == "department"
    assert body["document"]["department_ids"] == ["platform", "security"]
    assert body["document"]["indexing_status"] == "ready"
    assert body["chunk_count"] == 1

    assert detail.status_code == 200
    logs = detail.json()["logs"]
    assert logs[0]["action"] == "document.updated"
    assert logs[0]["actor_user_id"] == "admin-platform"
    assert logs[0]["document_id"] == document_id
    assert logs[0]["details"]["title"] == "VPN Access Policy"


@pytest.mark.asyncio
async def test_admin_delete_document_removes_it_from_retrieval_and_records_audit(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        document_id = await ingest_document(client)
        delete_response = await client.delete(f"/admin/documents/{document_id}", headers=ADMIN_HEADERS)
        retrieval = await client.post(
            "/auth/retrieve",
            headers=ADMIN_HEADERS,
            json={"query": "VPN enrollment", "top_k": 5},
        )
        logs = await client.get("/admin/audit-logs", headers=ADMIN_HEADERS)

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "document_id": document_id,
        "workspace_id": "acme",
        "deleted": True,
    }
    assert retrieval.status_code == 200
    assert retrieval.json()["results"] == []
    assert logs.json()["logs"][0]["action"] == "document.deleted"
    assert logs.json()["logs"][0]["document_id"] == document_id


@pytest.mark.asyncio
async def test_admin_workflow_rejects_non_admin_session(monkeypatch):
    monkeypatch.setenv("AUTH_CONTEXT_PROVIDER", "trusted_headers")
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        document_id = await ingest_document(client)
        response = await client.patch(
            f"/admin/documents/{document_id}",
            headers=EMPLOYEE_HEADERS,
            json={"title": "Unauthorized"},
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "admin role required"}
