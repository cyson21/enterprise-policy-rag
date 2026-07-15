#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TextIO

# OpenAI 라이브 스모크는 RUN_OPENAI_LIVE_SMOKE 플래그로만 실행되어 실서비스 요청 유입을 제한한다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.demo_data import seed_demo_state
from app.models import AnswerQuery
from app.runtime import build_services_from_env


LIVE_FLAG = "RUN_OPENAI_LIVE_SMOKE"
DEFAULT_MODEL = "gpt-4.1-mini"
SMOKE_QUERY = "security incident evidence"


def run_live_smoke(
    *,
    environ: Mapping[str, str] | None = None,
    env_file: Path | None = ROOT / ".env.local",
    build_services: Callable[[Mapping[str, str]], Any] = build_services_from_env,
    seed_demo: Callable[[Any], None] = seed_demo_state,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    # 데모 데이터 시드와 동일한 환경에서 동작하도록 기본 env를 병합하고, 필요 시 .env.local로 보강한다.
    env = _merged_env(environ if environ is not None else os.environ, env_file=env_file)

    if env.get(LIVE_FLAG) != "1":
        print(f"skipped: set {LIVE_FLAG}=1 to run the controlled OpenAI live smoke", file=stdout)
        return 0

    if not env.get("OPENAI_API_KEY", "").strip():
        print("OPENAI_API_KEY is required when RUN_OPENAI_LIVE_SMOKE=1", file=stderr)
        return 2

    # 실제 통신에서 SSL 인증서 경로가 비정상인 환경을 보정해 예측 불가능한 실패를 줄인다.
    _configure_ssl_cert_file()
    smoke_env = dict(env)
    smoke_env["LLM_PROVIDER"] = "openai"
    smoke_env.setdefault("OPENAI_MODEL", DEFAULT_MODEL)
    smoke_env.pop("DATABASE_URL", None)

    services = build_services(smoke_env)
    seed_demo(services)
    response = services.answer(
        AnswerQuery(
            workspace_id="acme",
            user_id="mina-security",
            department_ids=["security"],
            query=SMOKE_QUERY,
            top_k=2,
            score_threshold=0,
        )
    )

    if response.provider != "openai":
        print(f"expected provider=openai, got provider={response.provider}", file=stderr)
        return 3
    if not response.answer:
        print("OpenAI smoke did not return an answer", file=stderr)
        return 4
    if not response.citations:
        print("OpenAI smoke did not preserve citations", file=stderr)
        return 5

    model = smoke_env.get("OPENAI_MODEL", DEFAULT_MODEL)
    print(
        "OpenAI live smoke passed: "
        f"provider={response.provider} model={model} "
        f"retrieved={response.retrieved_count} citations={len(response.citations)} "
        f"latency_ms={response.latency_ms} answer_chars={len(response.answer)}",
        file=stdout,
    )
    return 0


def _merged_env(environ: Mapping[str, str], *, env_file: Path | None = ROOT / ".env.local") -> dict[str, str]:
    env = dict(environ)
    if env_file is not None:
        for key, value in _load_env_file(env_file).items():
            env.setdefault(key, value)
    return env


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def _configure_ssl_cert_file() -> None:
    if os.environ.get("SSL_CERT_FILE"):
        return
    try:
        import certifi
    except ModuleNotFoundError:
        return
    os.environ["SSL_CERT_FILE"] = certifi.where()


def main() -> int:
    return run_live_smoke()


if __name__ == "__main__":
    raise SystemExit(main())
