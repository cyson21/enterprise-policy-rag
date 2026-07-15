# PostgreSQL 레포지토리 통합 테스트: 실 DB 스킵 조건과 실사용 검색-추출 라운드트립을 점검한다.
import os
from uuid import uuid4

import pytest

from app.chunking import chunk_text
from app.models import DocumentCreate, RetrievalQuery, Visibility
from app.providers import FakeEmbeddingProvider
from app.repository import PostgresPolicyRepository
from app.retrieval import RetrievalService


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_TESTS") != "1",
    reason="set RUN_POSTGRES_TESTS=1 with DATABASE_URL to run PostgreSQL repository integration",
)


def _delete_test_workspaces(connection, *workspace_ids: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM workspaces WHERE id = ANY(%s)", (list(workspace_ids),))
    connection.commit()


def test_postgres_repository_round_trip_retrieval():
    try:
        import psycopg
    except ModuleNotFoundError as exc:
        raise pytest.skip("psycopg is not installed in this environment") from exc

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag",
    )
    connection = psycopg.connect(database_url)
    workspace_id = f"integration-round-trip-{uuid4().hex}"
    try:
        repository = PostgresPolicyRepository(connection=connection)
        embedding_provider = FakeEmbeddingProvider()
        document = DocumentCreate(
            workspace_id=workspace_id,
            title="Integration Security Manual",
            source_uri="policy://integration-security",
            content="Security incident evidence must be preserved before remediation starts.",
            content_type="text/plain",
            owner_user_id="mina-security",
            department_ids=["security"],
            visibility=Visibility.DEPARTMENT,
        )
        chunks = chunk_text(document.content)
        repository.add_document(document, chunks, embedding_provider.embed_many([chunk.text for chunk in chunks]))

        response = RetrievalService(repository=repository, embedding_provider=embedding_provider).retrieve(
            RetrievalQuery(
                workspace_id=workspace_id,
                user_id="mina-security",
                department_ids=["security"],
                query="security incident evidence",
                top_k=5,
            )
        )

        assert response.results
        assert response.results[0].title == "Integration Security Manual"
    finally:
        _delete_test_workspaces(connection, workspace_id)
        connection.close()


def test_postgres_repository_retrieval_filters_mixed_access_control_rows():
    try:
        import psycopg
    except ModuleNotFoundError as exc:
        raise pytest.skip("psycopg is not installed in this environment") from exc

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://rag_app:rag_app_password@127.0.0.1:5432/enterprise_policy_rag",
    )
    connection = psycopg.connect(database_url)
    workspace_id = f"integration-{uuid4().hex}"
    other_workspace_id = f"integration-denied-{uuid4().hex}"
    try:
        repository = PostgresPolicyRepository(connection=connection)
        embedding_provider = FakeEmbeddingProvider()

        def add_document(
            workspace_id: str,
            title: str = "",
            owner_user_id: str = "",
            department_ids: list[str] | None = None,
            visibility: Visibility = Visibility.PRIVATE,
        ) -> None:
            document = DocumentCreate(
                workspace_id=workspace_id,
                title=title,
                source_uri=f"policy://{title.lower().replace(' ', '-')}",
                content="Security incident policy references remote access and audit procedures.",
                content_type="text/plain",
                owner_user_id=owner_user_id,
                department_ids=department_ids or [],
                visibility=visibility,
            )
            chunks = chunk_text(document.content)
            repository.add_document(
                document,
                chunks,
                embedding_provider.embed_many([chunk.text for chunk in chunks]),
            )

        add_document(
            workspace_id=workspace_id,
            title="Allowed Public Document",
            owner_user_id="user-denied",
            department_ids=["finance"],
            visibility=Visibility.PUBLIC,
        )
        add_document(
            workspace_id=workspace_id,
            title="Allowed Department Document",
            owner_user_id="user-denied",
            department_ids=["security"],
            visibility=Visibility.DEPARTMENT,
        )
        add_document(
            workspace_id=workspace_id,
            title="Allowed Private Owner Document",
            owner_user_id="authorized-user",
            department_ids=["finance"],
            visibility=Visibility.PRIVATE,
        )
        add_document(
            workspace_id=workspace_id,
            title="Disallowed Department Document",
            owner_user_id="user-denied",
            department_ids=["finance"],
            visibility=Visibility.DEPARTMENT,
        )
        add_document(
            workspace_id=workspace_id,
            title="Disallowed Private Owner Document",
            owner_user_id="other-user",
            department_ids=["security"],
            visibility=Visibility.PRIVATE,
        )
        add_document(
            workspace_id=other_workspace_id,
            title="Disallowed Workspace Document",
            owner_user_id="authorized-user",
            department_ids=["security"],
            visibility=Visibility.PUBLIC,
        )

        query_embedding = embedding_provider.embed("security incident policy")
        candidates = repository.search_candidate_chunks(
            workspace_id,
            query_embedding,
            owner_user_id="authorized-user",
            department_ids=["security"],
            limit=12,
        )
        expected_titles = {
            "Allowed Public Document",
            "Allowed Department Document",
            "Allowed Private Owner Document",
        }
        assert {candidate.title for candidate in candidates} == expected_titles

        response = RetrievalService(repository=repository, embedding_provider=embedding_provider).retrieve(
            RetrievalQuery(
                workspace_id=workspace_id,
                user_id="authorized-user",
                department_ids=["security"],
                query="security incident policy",
                top_k=12,
            )
        )

        assert {result.title for result in response.results} == expected_titles
    finally:
        _delete_test_workspaces(connection, workspace_id, other_workspace_id)
        connection.close()
