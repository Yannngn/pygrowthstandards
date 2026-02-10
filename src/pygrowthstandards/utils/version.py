"""Helpers for resolving package version information."""

from __future__ import annotations

import contextlib
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def get_package_version() -> str:
    """Return the package version with a repo fallback.

    Returns:
        Package version string.
    """
    with contextlib.suppress(PackageNotFoundError):
        return version("pygrowthstandards")

    for parent in Path(__file__).resolve().parents:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            with contextlib.suppress(tomllib.TOMLDecodeError):
                data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
                return data.get("project", {}).get("version", "0.0.0")

    return "0.0.0"
