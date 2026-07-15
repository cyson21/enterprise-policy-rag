from __future__ import annotations

from scripts.verify_postgres_schema import (
    EXPECTED_INDEXES,
    EXPECTED_TABLES,
    inspect_schema,
    render_report,
)


class FakeResult:
    def __init__(self, rows: list[tuple[str, ...]]) -> None:
        self.rows = rows

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(
        self,
        *,
        vector_version: str | None = "0.8.0",
        embedding_type: str | None = "vector(64)",
        tables: set[str] = EXPECTED_TABLES,
        indexes: set[str] = EXPECTED_INDEXES,
    ) -> None:
        self.vector_version = vector_version
        self.embedding_type = embedding_type
        self.tables = tables
        self.indexes = indexes

    def execute(self, sql: str) -> FakeResult:
        if "FROM pg_extension" in sql:
            return FakeResult([(self.vector_version,)] if self.vector_version else [])
        if "FROM pg_attribute" in sql:
            return FakeResult([(self.embedding_type,)] if self.embedding_type else [])
        if "FROM pg_tables" in sql:
            return FakeResult([(table,) for table in sorted(self.tables)])
        if "FROM pg_indexes" in sql:
            return FakeResult([(index,) for index in sorted(self.indexes)])
        raise AssertionError(f"unexpected SQL: {sql}")


def test_inspect_schema_reports_all_required_pgvector_contracts() -> None:
    report = inspect_schema(FakeConnection())

    assert report["status"] == "passed"
    assert all(report["checks"].values())
    assert report["embedding_type"] == "vector(64)"
    assert report["missing_tables"] == []
    assert report["missing_indexes"] == []


def test_inspect_schema_names_each_missing_contract() -> None:
    report = inspect_schema(
        FakeConnection(
            vector_version=None,
            embedding_type="vector(32)",
            tables=EXPECTED_TABLES - {"documents"},
            indexes=EXPECTED_INDEXES - {"idx_document_chunks_embedding"},
        )
    )

    assert report["status"] == "failed"
    assert report["checks"] == {
        "vector_extension": False,
        "embedding_vector_64": False,
        "required_tables": False,
        "retrieval_indexes": False,
    }
    assert report["missing_tables"] == ["documents"]
    assert report["missing_indexes"] == ["idx_document_chunks_embedding"]


def test_schema_report_rendering_is_deterministic() -> None:
    report = inspect_schema(FakeConnection())

    assert render_report(report) == render_report(report)
    assert render_report(report).endswith("\n")
