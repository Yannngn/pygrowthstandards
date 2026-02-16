"""Convert Excel files under data/raw into CSV.

Designed to be run from the repository root.

Examples:
    uv run python scripts/convert_excel_to_csv.py
    uv run python scripts/convert_excel_to_csv.py --root data/raw --pattern "**/*.xlsx"

Behavior:
- Recursively finds .xlsx files under --root
- Writes CSV next to the source file
- If an Excel file has multiple sheets, writes one CSV per sheet:
  <file>__<sheet>.csv
"""

import argparse
import re
from pathlib import Path

import pandas as pd


def _safe_sheet_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name or "sheet"


def convert_excel_file(path: Path, overwrite: bool) -> list[Path]:
    written: list[Path] = []

    with pd.ExcelFile(path) as xls:
        sheet_names = list(xls.sheet_names)

        for sheet_name in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)

            if len(sheet_names) == 1:
                out_path = path.with_suffix(".csv")
            else:
                out_path = path.with_name(f"{path.stem}__{_safe_sheet_name(str(sheet_name))}.csv")

            if out_path.exists() and not overwrite:
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out_path, index=False)
            written.append(out_path)

    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/raw"), help="Root folder to search")
    parser.add_argument("--pattern", default="**/*.xlsx", help="Glob pattern within root")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing CSV files")
    args = parser.parse_args()

    root: Path = args.root
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    sources = sorted(root.glob(args.pattern))
    sources = [p for p in sources if p.is_file() and p.suffix.lower() in {".xlsx"}]

    if not sources:
        print(f"No Excel files found under {root} matching {args.pattern}")
        return 0

    total_written = 0
    for src in sources:
        print(f"Converting {src}...")
        written = convert_excel_file(src, overwrite=args.overwrite)
        for out in written:
            print(f"  -> {out}")
        total_written += len(written)

    print(f"Done. Wrote {total_written} CSV file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
