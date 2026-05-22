import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_document_ingestion_and_retrieval_api_filters_by_permission():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        health = await client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        public_doc = await client.post(
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
        assert public_doc.status_code == 201
        assert public_doc.json()["chunk_count"] == 1

        private_doc = await client.post(
            "/documents",
            json={
                "workspace_id": "acme",
                "title": "Executive Access",
                "source_uri": "policy://exec",
                "content": "Executive VPN exception checklist.",
                "content_type": "text/plain",
                "owner_user_id": "owner-2",
                "department_ids": ["executive"],
                "visibility": "private",
            },
        )
        assert private_doc.status_code == 201

        retrieval = await client.post(
            "/retrieve",
            json={
                "workspace_id": "acme",
                "user_id": "user-1",
                "department_ids": ["security"],
                "query": "vpn checklist",
                "top_k": 10,
            },
        )

        assert retrieval.status_code == 200
        body = retrieval.json()
        assert body["query"] == "vpn checklist"
        assert [result["title"] for result in body["results"]] == ["Remote Access"]
        assert "answer" not in body


@pytest.mark.asyncio
async def test_document_api_rejects_unsupported_content_type():
    app = create_app(seed_demo=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/documents",
            json={
                "workspace_id": "acme",
                "title": "Binary",
                "content": "not a pdf parser yet",
                "content_type": "application/pdf",
                "owner_user_id": "owner-1",
                "department_ids": [],
                "visibility": "public",
            },
        )

    assert response.status_code == 422
