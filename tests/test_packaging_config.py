from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_setuptools_packages_only_the_runtime_app() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert config["build-system"]["build-backend"] == "setuptools.build_meta"
    assert config["tool"]["setuptools"]["packages"] == ["app"]


def test_postgres_driver_is_an_explicit_optional_dependency() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    runtime_dependencies = config["project"]["dependencies"]
    postgres_dependencies = config["project"]["optional-dependencies"]["postgres"]

    assert all(not dependency.startswith("psycopg") for dependency in runtime_dependencies)
    assert any(dependency.startswith("psycopg[binary]") for dependency in postgres_dependencies)
