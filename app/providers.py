from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any, Protocol


TOKEN_PATTERN = re.compile(r"[0-9A-Za-z가-힣]+")


class EmbeddingProvider(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for text."""

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for multiple text inputs."""


class LLMProvider(Protocol):
    provider_name: str

    def complete(self, prompt: str) -> str:
        """Provider interface reserved for later answer-generation phases."""


class OpenAITransport(Protocol):
    def complete(self, api_key: str, payload: dict[str, object]) -> str:
        """Complete one OpenAI request payload."""


class OpenAIEmbeddingTransportProtocol(Protocol):
    def embed(self, api_key: str, payload: dict[str, object]) -> list[list[float]]:
        """Create embeddings for one OpenAI request payload."""


class FakeEmbeddingProvider:
    """키 없이 동작하는 로컬 임베딩 공급자."""

    # 관측 로그가 실제 사용 provider를 식별할 수 있도록 이름을 노출한다.
    provider_name = "fake"

    def __init__(self, dimensions: int = 64) -> None:
        if dimensions < 8:
            raise ValueError("dimensions must be at least 8")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        # 정규식 토큰 단위로 해시 기반 카운트 임베딩을 만들고 L2 정규화해 재현성을 확보한다.
        vector = [0.0] * self.dimensions
        for token in _tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]

    def similarity(self, left: list[float], right: list[float]) -> float:
        return sum(a * b for a, b in zip(left, right))


def _tokens(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


# 모델별 blended USD 단가(1K 토큰당). 입력/출력 토큰을 분리 집계하지 않는
# 현재 토큰 추정 방식에 맞춰 단일 근사 단가를 사용한다.
# 출처: OpenAI 공개 가격표 기준 근사값이며, 실제 청구액과는 차이가 있을 수 있다.
OPENAI_USD_PER_1K_TOKENS: dict[str, float] = {
    "gpt-4.1-mini": 0.0008,
    "gpt-4.1": 0.004,
    "gpt-4o-mini": 0.0006,
    "gpt-4o": 0.005,
}
OPENAI_DEFAULT_USD_PER_1K_TOKENS = 0.0008


class FakeLLMProvider:
    """키가 없어도 동작하는 로컬 LLM 폴백."""

    provider_name = "fake"

    def estimate_cost_usd(self, token_count: int) -> float:
        # 로컬 fake 응답은 외부 호출이 없으므로 과금 비용이 0이다.
        return 0.0

    def complete(self, prompt: str) -> str:
        # 주어진 증거 블록에서 첫 근거를 우선 사용해 일관된 fallback 응답을 생성한다.
        evidence_lines = [
            line.removeprefix("- ").strip()
            for line in prompt.splitlines()
            if line.startswith("- ")
        ]
        if not evidence_lines:
            return "근거가 충분하지 않아 답변할 수 없습니다."

        first = evidence_lines[0]
        if len(first) > 180:
            first = f"{first[:177]}..."
        return f"제공된 근거 기준으로 답변합니다. {first}"


class OpenAILLMProvider:
    """운영 모드에서만 쓰는 OpenAI LLM 연결 어댑터."""

    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        transport: OpenAITransport | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key is required")
        if not model.strip():
            raise ValueError("model is required")
        self.api_key = api_key
        self.model = model
        self._transport = transport or OpenAIHTTPTransport()

    def estimate_cost_usd(self, token_count: int) -> float:
        # 모델 단가 테이블에서 1K 토큰당 단가를 찾아 추정 비용을 계산한다.
        rate = OPENAI_USD_PER_1K_TOKENS.get(self.model, OPENAI_DEFAULT_USD_PER_1K_TOKENS)
        return round(max(0, token_count) / 1000 * rate, 6)

    def build_request_payload(self, prompt: str) -> dict[str, object]:
        return {
            "model": self.model,
            "input": prompt,
            "store": False,
        }

    def complete(self, prompt: str) -> str:
        return self._transport.complete(self.api_key, self.build_request_payload(prompt))


class OpenAIHTTPTransport:
    """OpenAI Responses API 전송을 담당하는 경량 Transport."""

    def __init__(
        self,
        endpoint: str = "https://api.openai.com/v1/responses",
        timeout_seconds: float = 20.0,
        opener: Any | None = None,
    ) -> None:
        if not endpoint.strip():
            raise ValueError("endpoint is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._opener = opener or urllib.request.urlopen

    def complete(self, api_key: str, payload: dict[str, object]) -> str:
        # HTTP 요청/응답 파싱 실패를 사용자 메시지로 변환해 상위 계층이 일관된 에러 형식을 받도록 한다.
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            message = _extract_openai_error(exc.read())
            raise RuntimeError(f"OpenAI request failed: {message}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI request failed: {exc.reason}") from exc

        return _extract_openai_text(body)


class OpenAIEmbeddingProvider:
    """OpenAI Embeddings API adapter pinned to the repository vector schema."""

    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int = 64,
        transport: OpenAIEmbeddingTransportProtocol | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key is required")
        if not model.strip():
            raise ValueError("model is required")
        if dimensions != 64:
            raise ValueError("OpenAI embedding dimensions must match vector(64)")
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self._transport = transport or OpenAIEmbeddingTransport()

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        payload: dict[str, object] = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimensions,
        }
        vectors = self._transport.embed(self.api_key, payload)
        if len(vectors) != len(texts):
            raise RuntimeError("OpenAI embedding response count did not match input count")
        normalized: list[list[float]] = []
        for vector in vectors:
            if len(vector) != self.dimensions:
                raise RuntimeError(f"OpenAI embedding response must contain {self.dimensions} dimensions")
            normalized.append(_normalize_vector(vector))
        return normalized


class OpenAIEmbeddingTransport:
    """OpenAI Embeddings API 전송을 담당하는 경량 Transport."""

    def __init__(
        self,
        endpoint: str = "https://api.openai.com/v1/embeddings",
        timeout_seconds: float = 20.0,
        opener: Any | None = None,
    ) -> None:
        if not endpoint.strip():
            raise ValueError("endpoint is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._opener = opener or urllib.request.urlopen

    def embed(self, api_key: str, payload: dict[str, object]) -> list[list[float]]:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            message = _extract_openai_error(exc.read())
            raise RuntimeError(f"OpenAI embedding request failed: {message}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenAI embedding request failed: {exc.reason}") from exc

        return _extract_openai_embeddings(body)


def _normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [float(value) for value in vector]
    return [float(value) / norm for value in vector]


def _extract_openai_text(body: bytes) -> str:
    # output_text가 비어 있어도 output 구조에서 텍스트 조각을 수집해 답변을 복원한다.
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI response was not valid JSON") from exc

    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    texts: list[str] = []
    output = payload.get("output")
    if not isinstance(output, list):
        output = []

    for item in output:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text)
        content = item.get("content")
        if not isinstance(content, list):
            content = []
        for content_item in content:
            if not isinstance(content_item, dict):
                continue
            content_text = content_item.get("text")
            if isinstance(content_text, str) and content_text.strip():
                texts.append(content_text)

    if texts:
        return "\n".join(texts)

    raise RuntimeError("OpenAI response did not include output text")


def _extract_openai_embeddings(body: bytes) -> list[list[float]]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenAI embedding response was not valid JSON") from exc

    data = payload.get("data")
    if not isinstance(data, list):
        raise RuntimeError("OpenAI embedding response did not include data")

    vectors: list[list[float]] = []
    for item in data:
        if not isinstance(item, dict):
            raise RuntimeError("OpenAI embedding response data item was not an object")
        embedding = item.get("embedding")
        if not isinstance(embedding, list):
            raise RuntimeError("OpenAI embedding response data item did not include embedding")
        vectors.append([float(value) for value in embedding])
    return vectors


def _extract_openai_error(body: bytes) -> str:
    # OpenAI 실패 응답에서 message/문자열 폴백을 순차적으로 찾는다.
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return body.decode("utf-8", errors="replace") or "unknown error"

    error = payload.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message
    if isinstance(error, str) and error.strip():
        return error
    return "unknown error"


def _openai_timeout_seconds(environ: Mapping[str, str]) -> float:
    raw = environ.get("OPENAI_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return 20.0
    try:
        timeout = float(raw)
    except ValueError as exc:
        raise ValueError("OPENAI_TIMEOUT_SECONDS must be a positive number") from exc
    if timeout <= 0:
        raise ValueError("OPENAI_TIMEOUT_SECONDS must be a positive number")
    return timeout


def build_embedding_provider_from_env(environ: Mapping[str, str]) -> EmbeddingProvider:
    provider = environ.get("EMBEDDING_PROVIDER", "fake").strip().lower()
    if provider in {"", "fake"}:
        return FakeEmbeddingProvider(dimensions=64)
    if provider == "openai":
        api_key = environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        model = environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip() or "text-embedding-3-small"
        timeout_seconds = _openai_timeout_seconds(environ)
        return OpenAIEmbeddingProvider(
            api_key=api_key,
            model=model,
            dimensions=64,
            transport=OpenAIEmbeddingTransport(timeout_seconds=timeout_seconds),
        )
    raise ValueError(f"unsupported EMBEDDING_PROVIDER: {provider}")


def build_llm_provider_from_env(environ: Mapping[str, str]) -> LLMProvider:
    # 운영 설정에 따라 fake/openai 공급자를 선택하고, 필요한 환경변수 미비 시 조기 종료한다.
    provider = environ.get("LLM_PROVIDER", "fake").strip().lower()
    if provider in {"", "fake"}:
        return FakeLLMProvider()
    if provider == "openai":
        api_key = environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        model = environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
        return OpenAILLMProvider(
            api_key=api_key,
            model=model,
            transport=OpenAIHTTPTransport(timeout_seconds=_openai_timeout_seconds(environ)),
        )
    raise ValueError(f"unsupported LLM_PROVIDER: {provider}")
