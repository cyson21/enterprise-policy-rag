# LLM 제공자 선택 테스트: 환경값 기반 기본값, API 키 필수 조건, HTTP 페이로드 구성을 검증한다.
import io
import json
import urllib.error

import pytest

from app.providers import (
    FakeLLMProvider,
    OpenAIHTTPTransport,
    OpenAILLMProvider,
    build_llm_provider_from_env,
)
from app.runtime import build_services_from_env


class RecordingOpenAITransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def complete(self, api_key: str, payload: dict[str, object]) -> str:
        self.calls.append((api_key, payload))
        return "openai adapter response"


class FakeHTTPResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


class RecordingHTTPOpener:
    def __init__(self, response_payload: dict[str, object]) -> None:
        self.response_payload = response_payload
        self.calls: list[tuple[object, float]] = []

    def __call__(self, request: object, timeout: float) -> FakeHTTPResponse:
        self.calls.append((request, timeout))
        return FakeHTTPResponse(self.response_payload)


def test_build_llm_provider_defaults_to_fake_without_api_key():
    provider = build_llm_provider_from_env({})

    assert isinstance(provider, FakeLLMProvider)
    assert provider.provider_name == "fake"


def test_build_llm_provider_requires_api_key_when_openai_is_selected():
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        build_llm_provider_from_env({"LLM_PROVIDER": "openai"})


def test_openai_llm_provider_builds_payload_and_uses_injected_transport_only():
    transport = RecordingOpenAITransport()
    provider = OpenAILLMProvider(api_key="sk-test", model="gpt-test", transport=transport)

    response = provider.complete("Question: security incident evidence")

    assert response == "openai adapter response"
    assert transport.calls[0][0] == "sk-test"
    payload = transport.calls[0][1]
    assert payload["model"] == "gpt-test"
    assert payload["input"] == "Question: security incident evidence"
    assert payload["store"] is False


def test_openai_http_transport_posts_responses_payload_and_extracts_output_text():
    opener = RecordingHTTPOpener({"output_text": "live response"})
    transport = OpenAIHTTPTransport(
        endpoint="https://api.openai.test/v1/responses",
        timeout_seconds=12.5,
        opener=opener,
    )

    response = transport.complete(
        api_key="sk-test",
        payload={"model": "gpt-test", "input": "Question", "store": False},
    )

    assert response == "live response"
    request, timeout = opener.calls[0]
    assert timeout == 12.5
    assert request.full_url == "https://api.openai.test/v1/responses"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == "Bearer sk-test"
    assert request.get_header("Content-type") == "application/json"
    assert json.loads(request.data.decode("utf-8")) == {
        "model": "gpt-test",
        "input": "Question",
        "store": False,
    }


def test_openai_http_transport_extracts_message_content_text():
    opener = RecordingHTTPOpener(
        {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": "first"},
                        {"type": "output_text", "text": "second"},
                    ],
                }
            ]
        }
    )
    transport = OpenAIHTTPTransport(opener=opener)

    assert transport.complete("sk-test", {"model": "gpt-test"}) == "first\nsecond"


def test_openai_http_transport_raises_clear_error_message():
    def failing_opener(request: object, timeout: float) -> FakeHTTPResponse:
        raise urllib.error.HTTPError(
            url="https://api.openai.test/v1/responses",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b'{"error":{"message":"invalid api key"}}'),
        )

    transport = OpenAIHTTPTransport(opener=failing_opener)

    with pytest.raises(RuntimeError, match="invalid api key"):
        transport.complete("sk-test", {"model": "gpt-test"})


def test_runtime_uses_fake_llm_provider_by_default_without_api_key():
    services = build_services_from_env({})

    assert isinstance(services.llm_provider, FakeLLMProvider)


def test_runtime_can_select_openai_llm_provider_explicitly_without_database_url():
    services = build_services_from_env(
        {
            "LLM_PROVIDER": "openai",
            "OPENAI_API_KEY": "sk-test",
            "OPENAI_MODEL": "gpt-test",
        }
    )

    assert isinstance(services.llm_provider, OpenAILLMProvider)
    assert services.llm_provider.model == "gpt-test"
