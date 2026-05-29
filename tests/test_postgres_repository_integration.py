# PostgreSQL 레포지토리 통합 테스트: 실 DB 스킵 조건과 실사용 검색-추출 라운드트립을 점검한다.
import os

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
    repository = PostgresPolicyRepository(connection=connection)
    embedding_provider = FakeEmbeddingProvider()
    document = DocumentCreate(
        workspace_id="integration-acme",
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
            workspace_id="integration-acme",
            user_id="mina-security",
            department_ids=["security"],
            query="security incident evidence",
            top_k=5,
        )
    )

    assert response.results
    assert response.results[0].title == "Integration Security Manual"
