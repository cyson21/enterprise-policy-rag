# PostgreSQL 레포지토리 통합 테스트: 실 DB 스킵 조건과 실사용 검색-추출 라운드트립을 점검한다.
import os
from collections.abc import Callable
from typing import Any

import pytest

from app.chunking import chunk_text
from app.models import DocumentCreate, RetrievalQuery, Visibility
from app.providers import FakeEmbeddingProvider
from app.repository import PostgresPolicyRepository
from app.retrieval import RetrievalService


pytestmark = [
    pytest.mark.postgres,
    pytest.mark.skipif(
        os.getenv("RUN_POSTGRES_TESTS") != "1",
        reason="set RUN_POSTGRES_TESTS=1 with TEST_DATABASE_URL to run PostgreSQL repository integration",
    ),
]


def test_postgres_repository_round_trip_retrieval(
    postgres_connection: Any,
    postgres_workspace_factory: Callable[[str], str],
):
    workspace_id = postgres_workspace_factory("integration-round-trip")
    repository = PostgresPolicyRepository(connection=postgres_connection)
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
    repository.add_document(
        document,
        chunks,
        embedding_provider.embed_many([chunk.text for chunk in chunks]),
    )

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


def test_postgres_repository_retrieval_filters_mixed_access_control_rows(
    postgres_connection: Any,
    postgres_workspace_factory: Callable[[str], str],
):
    workspace_id = postgres_workspace_factory("integration")
    other_workspace_id = postgres_workspace_factory("integration-denied")
    repository = PostgresPolicyRepository(connection=postgres_connection)
    embedding_provider = FakeEmbeddingProvider()

    def add_document(
        workspace_id: str,
        title: str = "",
        owner_user_id: str = "",
        department_ids: list[str] | None = None,
        visibility: Visibility = Visibility.PRIVATE,
    ) -> str:
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
        return repository.add_document(
            document,
            chunks,
            embedding_provider.embed_many([chunk.text for chunk in chunks]),
        ).id

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

    pending_document_id = add_document(
        workspace_id=workspace_id,
        title="Disallowed Pending Document",
        owner_user_id="authorized-user",
        department_ids=["security"],
        visibility=Visibility.PUBLIC,
    )
    with postgres_connection.cursor() as cursor:
        cursor.execute(
            "UPDATE documents SET indexing_status = 'pending' WHERE id = %s",
            (pending_document_id,),
        )
    postgres_connection.commit()

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
    assert {candidate.workspace_id for candidate in candidates} == {workspace_id}

    owner_and_public_candidates = repository.search_candidate_chunks(
        workspace_id,
        query_embedding,
        owner_user_id="authorized-user",
        department_ids=[],
        limit=12,
    )
    assert {candidate.title for candidate in owner_and_public_candidates} == {
        "Allowed Public Document",
        "Allowed Private Owner Document",
    }

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
