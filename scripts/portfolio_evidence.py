#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
DEFAULT_PROJECT = ROOT.name
DEFAULT_SCOPE = "pytest"
COUNT_FIELDS = ("tests", "failures", "errors", "skipped")


class PortfolioEvidenceError(ValueError):
    """Raised when a reproducible report cannot be built from the input."""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _direct_children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if _local_name(child.tag) == name]


def _reportable_suites(root: ET.Element) -> list[ET.Element]:
    root_name = _local_name(root.tag)
    if root_name not in {"testsuite", "testsuites"}:
        raise PortfolioEvidenceError(
            f"expected JUnit root element 'testsuite' or 'testsuites', got '{root_name}'"
        )

    suites: list[ET.Element] = []

    def visit(element: ET.Element) -> None:
        child_suites = _direct_children(element, "testsuite")
        direct_cases = _direct_children(element, "testcase")
        if _local_name(element.tag) == "testsuite" and (direct_cases or not child_suites):
            suites.append(element)
        for child in child_suites:
            visit(child)

    visit(root)
    if not suites:
        raise PortfolioEvidenceError("JUnit XML does not contain a test suite")
    return suites


def _derived_counts(suite: ET.Element) -> dict[str, int]:
    cases = _direct_children(suite, "testcase")
    failures = 0
    errors = 0
    skipped = 0
    for case in cases:
        child_names = {_local_name(child.tag) for child in case}
        failures += "failure" in child_names
        errors += "error" in child_names
        skipped += "skipped" in child_names
    return {
        "tests": len(cases),
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }


def _suite_counts(suite: ET.Element) -> dict[str, int]:
    derived = _derived_counts(suite)
    counts: dict[str, int] = {}
    for field in COUNT_FIELDS:
        raw_value = suite.get(field)
        if raw_value is None:
            counts[field] = derived[field]
            continue
        try:
            counts[field] = int(raw_value)
        except ValueError as exc:
            raise PortfolioEvidenceError(
                f"suite '{suite.get('name', 'unnamed')}' has invalid {field} count: {raw_value!r}"
            ) from exc
        if counts[field] < 0:
            raise PortfolioEvidenceError(
                f"suite '{suite.get('name', 'unnamed')}' has negative {field} count"
            )

    passed = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    if passed < 0:
        raise PortfolioEvidenceError(
            f"suite '{suite.get('name', 'unnamed')}' has inconsistent JUnit counts"
        )
    return {**counts, "passed": passed}


def parse_junit_xml(path: Path | str) -> list[dict[str, Any]]:
    junit_path = Path(path)
    if not junit_path.is_file():
        raise PortfolioEvidenceError(f"JUnit XML file does not exist: {junit_path}")

    try:
        root = ET.parse(junit_path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise PortfolioEvidenceError(f"failed to parse JUnit XML '{junit_path}': {exc}") from exc

    suites = [
        {
            "name": suite.get("name") or "unnamed",
            **_suite_counts(suite),
        }
        for suite in _reportable_suites(root)
    ]
    return sorted(
        suites,
        key=lambda suite: (
            suite["name"],
            suite["tests"],
            suite["failures"],
            suite["errors"],
            suite["skipped"],
        ),
    )


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PortfolioEvidenceError("unable to resolve the current git commit") from exc

    commit = result.stdout.strip()
    if not commit:
        raise PortfolioEvidenceError("git returned an empty commit identifier")
    return commit


def _generated_at_utc() -> str:
    source_date_epoch = os.getenv("SOURCE_DATE_EPOCH")
    if source_date_epoch is not None:
        try:
            timestamp = int(source_date_epoch)
        except ValueError as exc:
            raise PortfolioEvidenceError("SOURCE_DATE_EPOCH must be an integer") from exc
        if timestamp < 0:
            raise PortfolioEvidenceError("SOURCE_DATE_EPOCH must not be negative")
        return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace("+00:00", "Z")
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report(
    junit_xml: Path | str,
    *,
    project: str = DEFAULT_PROJECT,
    git_commit: str | None = None,
    generated_at_utc: str | None = None,
    scope: str = DEFAULT_SCOPE,
) -> dict[str, Any]:
    if not project.strip():
        raise PortfolioEvidenceError("project must not be empty")
    if not scope.strip():
        raise PortfolioEvidenceError("scope must not be empty")

    suites = parse_junit_xml(junit_xml)
    totals = {
        field: sum(suite[field] for suite in suites)
        for field in (*COUNT_FIELDS, "passed")
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "git_commit": git_commit or _git_commit(),
        "generated_at_utc": generated_at_utc or _generated_at_utc(),
        "scope": scope,
        "totals": totals,
        "suites": suites,
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def write_report(path: Path | str, report: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_report(report)
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(rendered)
            temporary_path = Path(temporary.name)
        temporary_path.replace(output_path)
    except OSError as exc:
        raise PortfolioEvidenceError(f"failed to write report '{output_path}': {exc}") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert pytest JUnit XML into stable portfolio evidence JSON."
    )
    parser.add_argument("junit_xml", type=Path, help="path to pytest JUnit XML")
    parser.add_argument("-o", "--output", type=Path, help="write JSON to this path; defaults to stdout")
    parser.add_argument("--project", default=DEFAULT_PROJECT, help="project identifier")
    parser.add_argument("--scope", default=DEFAULT_SCOPE, help="human-readable verification scope")
    parser.add_argument("--git-commit", help="commit identifier; defaults to git rev-parse HEAD")
    parser.add_argument(
        "--generated-at-utc",
        help="UTC generation timestamp; defaults to the current time",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        report = build_report(
            args.junit_xml,
            project=args.project,
            git_commit=args.git_commit,
            generated_at_utc=args.generated_at_utc,
            scope=args.scope,
        )
        if args.output is None:
            sys.stdout.write(render_report(report))
        else:
            write_report(args.output, report)
            print(args.output)
    except PortfolioEvidenceError as exc:
        parser.exit(1, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
