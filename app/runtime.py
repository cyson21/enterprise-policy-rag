from __future__ import annotations

import os
from collections.abc import Mapping

from app.eval_runs import InMemoryEvalRunRepository, PostgresEvalRunRepository
from app.providers import build_llm_provider_from_env
from app.query_logs import InMemoryQueryLogRepository, PostgresQueryLogRepository
from app.repository import InMemoryPolicyRepository, PostgresPolicyRepository
from app.services import PolicyRagServices


def build_services_from_env(environ: Mapping[str, str] | None = None) -> PolicyRagServices:
    env = environ or os.environ
    database_url = env.get("DATABASE_URL")
    llm_provider = build_llm_provider_from_env(env)
    if not database_url:
        return PolicyRagServices(
            repository=InMemoryPolicyRepository(),
            query_log_repository=InMemoryQueryLogRepository(),
            eval_run_repository=InMemoryEvalRunRepository(),
            llm_provider=llm_provider,
        )

    return PolicyRagServices(
        repository=PostgresPolicyRepository(dsn=database_url),
        query_log_repository=PostgresQueryLogRepository(dsn=database_url),
        eval_run_repository=PostgresEvalRunRepository(dsn=database_url),
        llm_provider=llm_provider,
    )
