# OpenAI 실전 스모크 테스트: 플래그/환경 설정 기반 실행 조건과 민감정보 출력 금지 경로를 검증한다.
from __future__ import annotations

import io

from app.models import AnswerCitation, AnswerResponse
from scripts import openai_live_smoke


class RecordingServices:
    def __init__(self) -> None:
        self.answer_payloads = []

    def answer(self, payload):
        self.answer_payloads.append(payload)
        return AnswerResponse(
            query=payload.query,
            answer="controlled live response",
            citations=[
                AnswerCitation(
                    rank=1,
                    chunk_id="chunk_1",
                    document_id="doc_1",
                    title="Remote Access Policy",
                    source_uri="policy://remote-access",
                    quote="VPN enrollment evidence.",
                    score=0.91,
                )
            ],
            refusal_reason=None,
            provider="openai",
            token_count=42,
            estimated_cost_usd=0,
            latency_ms=123,
            retrieved_count=1,
        )


def test_openai_live_smoke_skips_without_explicit_flag():
    stdout = io.StringIO()

    exit_code = openai_live_smoke.run_live_smoke(
        environ={},
        env_file=None,
        stdout=stdout,
        stderr=io.StringIO(),
    )

    assert exit_code == 0
    assert "skipped" in stdout.getvalue()


def test_openai_live_smoke_requires_api_key_when_enabled():
    stderr = io.StringIO()

    exit_code = openai_live_smoke.run_live_smoke(
        environ={"RUN_OPENAI_LIVE_SMOKE": "1"},
        env_file=None,
        stdout=io.StringIO(),
        stderr=stderr,
    )

    assert exit_code == 2
    assert "OPENAI_API_KEY" in stderr.getvalue()


def test_openai_live_smoke_forces_openai_provider_without_printing_key():
    services = RecordingServices()
    captured_env = {}
    seeded_services = []
    stdout = io.StringIO()

    def build_services(environ):
        captured_env.update(environ)
        return services

    def seed_demo(service):
        seeded_services.append(service)

    exit_code = openai_live_smoke.run_live_smoke(
        environ={
            "RUN_OPENAI_LIVE_SMOKE": "1",
            "OPENAI_API_KEY": "sk-test-secret",
            "OPENAI_MODEL": "gpt-test",
            "DATABASE_URL": "postgresql://should-not-be-used",
        },
        env_file=None,
        build_services=build_services,
        seed_demo=seed_demo,
        stdout=stdout,
        stderr=io.StringIO(),
    )

    assert exit_code == 0
    assert captured_env["LLM_PROVIDER"] == "openai"
    assert captured_env["OPENAI_MODEL"] == "gpt-test"
    assert "DATABASE_URL" not in captured_env
    assert services.answer_payloads[0].workspace_id == "acme"
    assert seeded_services == [services]
    assert "provider=openai" in stdout.getvalue()
    assert "sk-test-secret" not in stdout.getvalue()
