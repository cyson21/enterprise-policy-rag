# 검색 권한 테스트: 워크스페이스/공개/부서/소유자 필터 규칙이 검색 결과에 반영되는지 확인한다.
from app.chunking import chunk_text
from app.models import DocumentCreate, RetrievalQuery, Visibility
from app.providers import FakeEmbeddingProvider
from app.repository import InMemoryPolicyRepository
from app.retrieval import RetrievalService


def _add_document(repository, **overrides):
    payload = {
        "workspace_id": "acme",
        "title": "Remote Work Policy",
        "source_uri": "policy://remote",
        "content": "Remote work requires VPN access.",
        "content_type": "text/plain",
        "owner_user_id": "owner-1",
        "department_ids": ["security"],
        "visibility": Visibility.PUBLIC,
    }
    payload.update(overrides)
    document = DocumentCreate(**payload)
    chunks = chunk_text(document.content)
    return repository.add_document(document, chunks, FakeEmbeddingProvider().embed_many([chunk.text for chunk in chunks]))


def test_retrieval_filters_chunks_by_workspace_before_ranking():
    repository = InMemoryPolicyRepository()
    _add_document(repository, workspace_id="acme", content="VPN setup guide for employees.")
    _add_document(repository, workspace_id="other", content="VPN setup guide for contractors.")
    service = RetrievalService(repository=repository, embedding_provider=FakeEmbeddingProvider())

    response = service.retrieve(
        RetrievalQuery(
            workspace_id="acme",
            user_id="user-1",
            department_ids=["security"],
            query="vpn setup",
            top_k=5,
        )
    )

    assert len(response.results) == 1
    assert response.results[0].workspace_id == "acme"


def test_retrieval_allows_public_owner_and_department_documents_only():
    repository = InMemoryPolicyRepository()
    _add_document(repository, title="Public VPN", content="Remote VPN setup is public.", visibility=Visibility.PUBLIC)
    _add_document(
        repository,
        title="Security VPN",
        content="Security VPN rotation instructions.",
        visibility=Visibility.DEPARTMENT,
        department_ids=["security"],
    )
    _add_document(
        repository,
        title="Finance VPN",
        content="Finance VPN exception process.",
        visibility=Visibility.DEPARTMENT,
        department_ids=["finance"],
    )
    _add_document(
        repository,
        title="Owner VPN",
        content="Owner VPN private checklist.",
        visibility=Visibility.PRIVATE,
        owner_user_id="user-1",
        department_ids=["finance"],
    )
    _add_document(
        repository,
        title="Other Private VPN",
        content="Other user VPN private checklist.",
        visibility=Visibility.PRIVATE,
        owner_user_id="user-2",
        department_ids=["security"],
    )
    service = RetrievalService(repository=repository, embedding_provider=FakeEmbeddingProvider())

    response = service.retrieve(
        RetrievalQuery(
            workspace_id="acme",
            user_id="user-1",
            department_ids=["security"],
            query="vpn checklist",
            top_k=10,
        )
    )

    titles = {result.title for result in response.results}
    assert titles == {"Public VPN", "Security VPN", "Owner VPN"}


def test_retrieval_returns_empty_results_when_permissions_do_not_match():
    repository = InMemoryPolicyRepository()
    _add_document(
        repository,
        title="Finance Policy",
        content="Payroll VPN approval is finance only.",
        visibility=Visibility.DEPARTMENT,
        department_ids=["finance"],
    )
    service = RetrievalService(repository=repository, embedding_provider=FakeEmbeddingProvider())

    response = service.retrieve(
        RetrievalQuery(
            workspace_id="acme",
            user_id="user-1",
            department_ids=["security"],
            query="payroll vpn",
            top_k=5,
        )
    )

    assert response.results == []


def test_in_memory_candidate_search_prefilters_permissions_and_orders_by_similarity():
    repository = InMemoryPolicyRepository()
    _add_document(repository, title="Public VPN", content="Remote VPN setup is public.", visibility=Visibility.PUBLIC)
    _add_document(
        repository,
        title="Security VPN",
        content="Security VPN rotation instructions.",
        visibility=Visibility.DEPARTMENT,
        department_ids=["security"],
    )
    _add_document(
        repository,
        title="Finance VPN",
        content="Finance VPN exception process.",
        visibility=Visibility.DEPARTMENT,
        department_ids=["finance"],
    )

    provider = FakeEmbeddingProvider()
    candidates = repository.search_candidate_chunks(
        "acme",
        provider.embed("security vpn"),
        owner_user_id="user-1",
        department_ids=["security"],
        limit=10,
    )

    titles = [chunk.title for chunk in candidates]
    assert "Finance VPN" not in titles
    assert titles[0] == "Security VPN"


class SignedEmbeddingProvider:
    provider_name = "signed"
    dimensions = 64

    def embed(self, text: str) -> list[float]:
        value = -0.25 if "negative" in text else 1.0
        return [value] + [0.0] * 63

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


def test_retrieval_uses_threshold_only_without_positive_score_cutoff():
    repository = InMemoryPolicyRepository()
    provider = SignedEmbeddingProvider()
    document = DocumentCreate(
        workspace_id="acme",
        title="Signed Score Policy",
        source_uri="policy://signed",
        content="negative but still above threshold",
        content_type="text/plain",
        owner_user_id="user-1",
        department_ids=[],
        visibility=Visibility.PRIVATE,
    )
    chunks = chunk_text(document.content)
    repository.add_document(document, chunks, provider.embed_many([chunk.text for chunk in chunks]))
    service = RetrievalService(repository=repository, embedding_provider=provider)

    response = service.retrieve(
        RetrievalQuery(
            workspace_id="acme",
            user_id="user-1",
            department_ids=[],
            query="negative query",
            top_k=5,
            score_threshold=-0.5,
        )
    )

    assert [result.title for result in response.results] == ["Signed Score Policy"]
