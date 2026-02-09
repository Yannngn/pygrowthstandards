from __future__ import annotations

import contextlib
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def get_package_version() -> str:
    """Return the package version with a repo fallback.

    Uses import metadata when installed; falls back to pyproject.toml
    when running from a source checkout.
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
