"""Convert PDF files under data/raw into CSV.

This is a thin wrapper around the library's PDF table extraction utility:
`pygrowthstandards.pdf.convert`.

Designed to be run from the repository root.

Examples:
    uv run python scripts/convert_pdf_to_csv.py
    uv run python scripts/convert_pdf_to_csv.py --root data/raw --pattern "**/*.pdf"

Requirements:
    The PDF conversion uses the optional dependency `docling`.
    Install via:
        uv sync --group pdf
    or
        pip install "pygrowthstandards[pdf]"

Behavior:
- Recursively finds PDFs under --root
- Writes a CSV next to each PDF (same basename)
"""

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/raw"), help="Root folder to search")
    parser.add_argument("--pattern", default="**/*.pdf", help="Glob pattern within root")
    args = parser.parse_args()

    root: Path = args.root
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    sources = sorted(root.glob(args.pattern))
    sources = [p for p in sources if p.is_file() and p.suffix.lower() == ".pdf"]

    if not sources:
        print(f"No PDF files found under {root} matching {args.pattern}")
        return 0

    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise SystemExit("Missing optional dependency 'docling'. Install with: uv sync --group pdf") from exc

    from pygrowthstandards.pdf.convert import docling_extract_tables

    converter = DocumentConverter()
    failures: list[Path] = []
    for src in sources:
        print(f"Converting {src}...")
        out = src.with_suffix(".csv")
        try:
            result = docling_extract_tables(converter, src)
        except Exception as exc:  # surface unexpected errors
            print(f"ERROR: conversion failed for {src} -> {out}: {exc}")
            failures.append(src)
            continue

        # If the extractor signals failure via False, surface it
        if result is False:
            print(f"WARNING: conversion reported failure for {src} -> {out}")
            failures.append(src)
            continue

        # Ensure output exists, warn if not
        if not out.exists():
            print(f"WARNING: expected output not found for {src} -> {out}")
            failures.append(src)
            continue

        print(f"  -> {out}")

    if failures:
        print("\nFailed conversions:")
        for f in failures:
            print(f" - {f}")
        return 2

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
