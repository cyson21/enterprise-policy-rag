from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.portfolio_evidence import (
    PortfolioEvidenceError,
    build_report,
    main,
    parse_junit_xml,
    render_report,
    write_report,
)


def _write_xml(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "pytest.xml"
    path.write_text(content, encoding="utf-8")
    return path


def test_build_report_aggregates_suite_totals_and_sorts_suites(tmp_path):
    junit_xml = _write_xml(
        tmp_path,
        """
        <testsuites>
          <testsuite name="unit" tests="3" failures="1" errors="0" skipped="1" />
          <testsuite name="integration" tests="2" failures="0" errors="1" skipped="0" />
        </testsuites>
        """,
    )

    report = build_report(
        junit_xml,
        git_commit="abc123",
        generated_at_utc="2026-07-15T00:00:00Z",
        scope="full pytest with PostgreSQL",
    )

    assert report == {
        "schema_version": 1,
        "project": "enterprise-policy-rag",
        "git_commit": "abc123",
        "generated_at_utc": "2026-07-15T00:00:00Z",
        "scope": "full pytest with PostgreSQL",
        "totals": {
            "tests": 5,
            "failures": 1,
            "errors": 1,
            "skipped": 1,
            "passed": 2,
        },
        "suites": [
            {
                "name": "integration",
                "tests": 2,
                "failures": 0,
                "errors": 1,
                "skipped": 0,
                "passed": 1,
            },
            {
                "name": "unit",
                "tests": 3,
                "failures": 1,
                "errors": 0,
                "skipped": 1,
                "passed": 1,
            },
        ],
    }


def test_parse_junit_accepts_testsuite_root_and_derives_missing_counts(tmp_path):
    junit_xml = _write_xml(
        tmp_path,
        """
        <testsuite name="pytest">
          <testcase name="passes" />
          <testcase name="fails"><failure /></testcase>
          <testcase name="errors"><error /></testcase>
          <testcase name="skips"><skipped /></testcase>
        </testsuite>
        """,
    )

    assert parse_junit_xml(junit_xml) == [
        {
            "name": "pytest",
            "tests": 4,
            "failures": 1,
            "errors": 1,
            "skipped": 1,
            "passed": 1,
        }
    ]


def test_parse_junit_supports_namespaced_nested_suites_without_double_counting(tmp_path):
    junit_xml = _write_xml(
        tmp_path,
        """
        <testsuites xmlns="urn:junit">
          <testsuite name="aggregate" tests="2" failures="0" errors="0" skipped="0">
            <testsuite name="child-b" tests="1" failures="0" errors="0" skipped="0" />
            <testsuite name="child-a" tests="1" failures="0" errors="0" skipped="1" />
          </testsuite>
        </testsuites>
        """,
    )

    suites = parse_junit_xml(junit_xml)

    assert [suite["name"] for suite in suites] == ["child-a", "child-b"]
    assert sum(suite["tests"] for suite in suites) == 2


def test_parse_junit_rejects_missing_input(tmp_path):
    with pytest.raises(PortfolioEvidenceError, match="does not exist"):
        parse_junit_xml(tmp_path / "missing.xml")


def test_parse_junit_rejects_malformed_xml(tmp_path):
    junit_xml = _write_xml(tmp_path, "<testsuites><testsuite></testsuites>")

    with pytest.raises(PortfolioEvidenceError, match="failed to parse"):
        parse_junit_xml(junit_xml)


def test_parse_junit_rejects_document_without_suites(tmp_path):
    junit_xml = _write_xml(tmp_path, "<report />")

    with pytest.raises(PortfolioEvidenceError, match="expected JUnit root"):
        parse_junit_xml(junit_xml)


@pytest.mark.parametrize(
    "attributes, message",
    [
        ('tests="many" failures="0" errors="0" skipped="0"', "invalid tests count"),
        ('tests="1" failures="1" errors="1" skipped="0"', "inconsistent JUnit counts"),
        ('tests="-1" failures="0" errors="0" skipped="0"', "negative tests count"),
    ],
)
def test_parse_junit_rejects_invalid_counts(tmp_path, attributes, message):
    junit_xml = _write_xml(tmp_path, f'<testsuite name="pytest" {attributes} />')

    with pytest.raises(PortfolioEvidenceError, match=message):
        parse_junit_xml(junit_xml)


def test_render_and_write_report_are_byte_stable(tmp_path):
    report = {"z": 1, "a": {"value": 2}}
    first_path = tmp_path / "first" / "report.json"
    second_path = tmp_path / "second" / "report.json"

    write_report(first_path, report)
    write_report(second_path, report)

    assert first_path.read_bytes() == second_path.read_bytes()
    assert first_path.read_text(encoding="utf-8") == render_report(report)
    assert json.loads(first_path.read_text(encoding="utf-8")) == report


def test_build_report_uses_source_date_epoch_for_reproducible_timestamp(tmp_path, monkeypatch):
    junit_xml = _write_xml(tmp_path, '<testsuite name="pytest" tests="0" />')
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")

    report = build_report(junit_xml, git_commit="abc123")

    assert report["generated_at_utc"] == "1970-01-01T00:00:00Z"


@pytest.mark.parametrize("value", ["not-a-number", "-1"])
def test_build_report_rejects_invalid_source_date_epoch(tmp_path, monkeypatch, value):
    junit_xml = _write_xml(tmp_path, '<testsuite name="pytest" tests="0" />')
    monkeypatch.setenv("SOURCE_DATE_EPOCH", value)

    with pytest.raises(PortfolioEvidenceError, match="SOURCE_DATE_EPOCH"):
        build_report(junit_xml, git_commit="abc123")


def test_main_fails_when_junit_argument_is_missing():
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2
