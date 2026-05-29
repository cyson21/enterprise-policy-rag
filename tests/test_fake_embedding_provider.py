# 임베딩 제공자 테스트: 동일 입력에 대한 결정성, 유사도 비교의 상대적 동작을 확인한다.
from app.providers import FakeEmbeddingProvider


def test_fake_embedding_provider_is_deterministic_and_normalized():
    provider = FakeEmbeddingProvider(dimensions=16)

    first = provider.embed("remote access vpn policy")
    second = provider.embed("remote access vpn policy")

    assert first == second
    assert len(first) == 16
    assert round(sum(value * value for value in first), 6) == 1.0


def test_fake_embedding_provider_keeps_related_texts_closer_than_unrelated_texts():
    provider = FakeEmbeddingProvider(dimensions=32)
    query = provider.embed("remote vpn access")
    related = provider.embed("VPN access is required for remote work")
    unrelated = provider.embed("expense reimbursement meal receipts")

    related_score = provider.similarity(query, related)
    unrelated_score = provider.similarity(query, unrelated)

    assert related_score > unrelated_score
