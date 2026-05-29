# 문서 API 테스트: 워크스페이스 스코프 정합성 및 문서 상세/목록 응답 구조를 검증한다.
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def ingest_document(client: AsyncClient, *, workspace_id: str, title: str, content: str) -> str:
    response = await client.post(
        "/documents",
        json={
            "workspace_id": workspace_id,
            "title": title,
            "source_uri": f"policy://{title.lower().replace(' ', '-')}",
            "content": content,
            "content_type": "text/markdown",
            "owner_user_id": "owner-1",
            "department_ids": ["security"],
            "visibility": "department",
        },
    )
    assert response.status_code == 201
    return response.json()["document_id"]


@pytest.mark.asyncio
async def test_document_list_api_returns_metadata_and_chunk_count():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await ingest_document(
            client,
            workspace_id="acme",
            title="Remote Access Policy",
            content="VPN enrollment is required.\n\nDevice posture must be checked.",
        )
        await ingest_document(
            client,
            workspace_id="other",
            title="Other Workspace Policy",
            content="This document belongs to another workspace.",
        )

        response = await client.get("/documents", params={"workspace_id": "acme"})

    assert response.status_code == 200
    body = response.json()
    assert [document["title"] for document in body["documents"]] == ["Remote Access Policy"]
    assert body["documents"][0] == {
        "id": "doc_1",
        "workspace_id": "acme",
        "title": "Remote Access Policy",
        "source_uri": "policy://remote-access-policy",
        "content_type": "text/markdown",
        "owner_user_id": "owner-1",
        "department_ids": ["security"],
        "visibility": "department",
        "indexing_status": "ready",
        "chunk_count": 1,
    }


@pytest.mark.asyncio
async def test_document_detail_api_returns_chunk_previews():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        document_id = await ingest_document(
            client,
            workspace_id="acme",
            title="Incident Manual",
            content="Preserve evidence first.\n\nAssign incident commander.",
        )

        response = await client.get(f"/documents/{document_id}", params={"workspace_id": "acme"})

    assert response.status_code == 200
    body = response.json()
    assert body["document"]["id"] == document_id
    assert body["document"]["chunk_count"] == 1
    assert [chunk["chunk_index"] for chunk in body["chunks"]] == [0]
    assert body["chunks"][0]["text"] == "Preserve evidence first.\n\nAssign incident commander."
    assert body["chunks"][0]["embedding_dimensions"] > 0
    assert "embedding" not in body["chunks"][0]


@pytest.mark.asyncio
async def test_document_detail_api_returns_404_for_wrong_workspace():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        document_id = await ingest_document(
            client,
            workspace_id="private-workspace",
            title="Private Workspace Policy",
            content="Only this workspace can see it.",
        )

        response = await client.get(f"/documents/{document_id}", params={"workspace_id": "acme"})

    assert response.status_code == 404
