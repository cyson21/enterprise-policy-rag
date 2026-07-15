from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from uuid import uuid4

import pytest


@pytest.fixture
def postgres_connection() -> Iterator[object]:
    if os.getenv("RUN_POSTGRES_TESTS") != "1":
        pytest.skip("set RUN_POSTGRES_TESTS=1 to run PostgreSQL integration tests")
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.fail("TEST_DATABASE_URL is required when RUN_POSTGRES_TESTS=1")
    psycopg = pytest.importorskip("psycopg")
    connection = psycopg.connect(database_url, connect_timeout=5)
    with connection.cursor() as cursor:
        cursor.execute("SET statement_timeout = '10s'")
        cursor.execute("SET lock_timeout = '3s'")
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture
def postgres_workspace_factory(
    postgres_connection: object,
) -> Iterator[Callable[[str], str]]:
    workspace_ids: list[str] = []

    def create(prefix: str) -> str:
        workspace_id = f"{prefix}-{uuid4().hex}"
        workspace_ids.append(workspace_id)
        return workspace_id

    try:
        yield create
    finally:
        with postgres_connection.cursor() as cursor:
            cursor.execute("DELETE FROM workspaces WHERE id = ANY(%s)", (workspace_ids,))
        postgres_connection.commit()
