from __future__ import annotations

import os
from collections.abc import Mapping

from app.eval_runs import InMemoryEvalRunRepository, PostgresEvalRunRepository
from app.providers import build_embedding_provider_from_env, build_llm_provider_from_env
from app.query_logs import InMemoryQueryLogRepository, PostgresQueryLogRepository
from app.repository import InMemoryPolicyRepository, PostgresPolicyRepository
from app.services import PolicyRagServices


def build_services_from_env(environ: Mapping[str, str] | None = None) -> PolicyRagServices:
    # 런타임 부팅점에서 DB/LLM 유무에 따라 인프라 바인딩을 전환한다.
    env = environ or os.environ
    database_url = env.get("DATABASE_URL")
    embedding_provider = build_embedding_provider_from_env(env)
    llm_provider = build_llm_provider_from_env(env)
    if embedding_provider.dimensions != 64:
        raise RuntimeError("embedding provider dimensions must match vector(64)")
    if not database_url:
        # DB 미설정이면 완전 인메모리 파이프라인으로 동작해 데모/로컬 실행을 단순화한다.
        return PolicyRagServices(
            repository=InMemoryPolicyRepository(),
            query_log_repository=InMemoryQueryLogRepository(),
            eval_run_repository=InMemoryEvalRunRepository(),
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
        )

    return PolicyRagServices(
        repository=PostgresPolicyRepository(dsn=database_url),
        query_log_repository=PostgresQueryLogRepository(dsn=database_url),
        eval_run_repository=PostgresEvalRunRepository(dsn=database_url),
        embedding_provider=embedding_provider,
        llm_provider=llm_provider,
    )
