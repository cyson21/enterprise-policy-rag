#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence


EXPECTED_TABLES = {
    "workspaces",
    "documents",
    "document_chunks",
    "query_logs",
    "retrieval_results",
    "answers",
    "citations",
    "eval_runs",
    "eval_case_results",
    "admin_audit_logs",
}
EXPECTED_INDEXES = {
    "idx_documents_workspace_visibility",
    "idx_documents_owner",
    "idx_documents_department_ids",
    "idx_document_chunks_workspace",
    "idx_document_chunks_embedding",
}


def inspect_schema(connection: Any) -> dict[str, Any]:
    extension_row = connection.execute(
        "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
    ).fetchone()
    dimension_row = connection.execute(
        """
        SELECT format_type(attribute.atttypid, attribute.atttypmod)
        FROM pg_attribute attribute
        JOIN pg_class relation ON relation.oid = attribute.attrelid
        WHERE relation.relname = 'document_chunks'
          AND attribute.attname = 'embedding'
          AND NOT attribute.attisdropped
        """
    ).fetchone()
    table_rows = connection.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
    ).fetchall()
    index_rows = connection.execute(
        "SELECT indexname FROM pg_indexes WHERE schemaname = 'public'"
    ).fetchall()

    tables = {str(row[0]) for row in table_rows}
    indexes = {str(row[0]) for row in index_rows}
    missing_tables = sorted(EXPECTED_TABLES - tables)
    missing_indexes = sorted(EXPECTED_INDEXES - indexes)
    vector_version = str(extension_row[0]) if extension_row else None
    embedding_type = str(dimension_row[0]) if dimension_row else None
    checks = {
        "vector_extension": vector_version is not None,
        "embedding_vector_64": embedding_type == "vector(64)",
        "required_tables": not missing_tables,
        "retrieval_indexes": not missing_indexes,
    }
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "vector_version": vector_version,
        "embedding_type": embedding_type,
        "missing_tables": missing_tables,
        "missing_indexes": missing_indexes,
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the PostgreSQL schema required by the pgvector retrieval path."
    )
    parser.add_argument("--output", type=Path, help="write JSON diagnostics to this path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("error: DATABASE_URL is required", file=sys.stderr)
        return 2

    try:
        import psycopg
    except ImportError as exc:
        report = {
            "status": "error",
            "error_type": type(exc).__name__,
            "error": "psycopg is not installed; install the postgres extra",
        }
    else:
        try:
            with psycopg.connect(database_url, connect_timeout=5) as connection:
                report = inspect_schema(connection)
        except (psycopg.Error, OSError, RuntimeError) as exc:
            report = {
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

    rendered = render_report(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        sys.stdout.write(rendered)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
