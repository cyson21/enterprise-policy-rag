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


class FakeEmbeddingProvider:
    """Deterministic local embedding provider for tests and no-key development."""

    def __init__(self, dimensions: int = 64) -> None:
        if dimensions < 8:
            raise ValueError("dimensions must be at least 8")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
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


class FakeLLMProvider:
    """Deterministic local LLM provider for no-key answer-layer development."""

    provider_name = "fake"

    def complete(self, prompt: str) -> str:
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
    """OpenAI LLM provider kept outside the default fake path."""

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

    def build_request_payload(self, prompt: str) -> dict[str, object]:
        return {
            "model": self.model,
            "input": prompt,
            "store": False,
        }

    def complete(self, prompt: str) -> str:
        return self._transport.complete(self.api_key, self.build_request_payload(prompt))


class OpenAIHTTPTransport:
    """Small Responses API HTTP transport for explicit opt-in OpenAI runs."""

    def __init__(
        self,
        endpoint: str = "https://api.openai.com/v1/responses",
        timeout_seconds: float = 30.0,
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


def _extract_openai_text(body: bytes) -> str:
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


def _extract_openai_error(body: bytes) -> str:
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


def build_llm_provider_from_env(environ: Mapping[str, str]) -> LLMProvider:
    provider = environ.get("LLM_PROVIDER", "fake").strip().lower()
    if provider in {"", "fake"}:
        return FakeLLMProvider()
    if provider == "openai":
        api_key = environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        model = environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
        return OpenAILLMProvider(api_key=api_key, model=model)
    raise ValueError(f"unsupported LLM_PROVIDER: {provider}")
