"""CLI for rebuilding packaged growth reference data."""

import shutil
from pathlib import Path

from pygrowthstandards.data.growth.extract import RawTable
from pygrowthstandards.data.growth.transform import GrowthData

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
RAW_ROOT = _PROJECT_ROOT / "data" / "raw" / "growth"
OUTPUT_DIR = _PROJECT_ROOT / "data"

EXTRACT_CSV_ONLY = True


def _print_title(title: str) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)


def _prepare_backup_dir() -> Path:
    backup_dir = OUTPUT_DIR / "backup"
    print(f"\nProject root: {_PROJECT_ROOT}")
    print(f"Raw data directory: {RAW_ROOT}")
    print(f"Backup directory: {backup_dir}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def _discover_raw_files(raw_root: Path) -> list[Path]:
    print()
    _print_title("STEP 1: DISCOVER RAW FILES")

    raw_files: list[Path] = []

    if not EXTRACT_CSV_ONLY:
        xlsx_files = list(raw_root.rglob("*.xlsx"))
        print(f"Found {len(xlsx_files)} Excel file(s)")
        raw_files.extend(xlsx_files)

    csv_files = [raw_file for raw_file in raw_root.rglob("*.csv") if raw_file.name.startswith("who") or raw_file.name.startswith("intergrowth")]
    print(f"Found {len(csv_files)} CSV file(s)")
    raw_files.extend(csv_files)

    if not raw_files:
        print(f"ERROR: No raw files found in {raw_root}")

    return raw_files


def _parse_raw_files(raw_files: list[Path]) -> list[RawTable] | None:
    if not raw_files:
        return None

    print()
    _print_title("STEP 2: EXTRACT (PARSE RAW FILES)")

    tables: list[RawTable] = []
    for raw_file in raw_files:
        try:
            if raw_file.suffix.lower() == ".xlsx":
                dataset = RawTable.from_xlsx(raw_file)
            else:
                dataset = RawTable.from_csv(raw_file)
            tables.append(dataset)
        except Exception as exc:
            print(f"ERROR: Failed to parse {raw_file.name}: {exc}")
            return None

    print(f"\nSuccessfully parsed {len(tables)} table(s)")
    return tables


def _build_growth_data(tables: list[RawTable]) -> GrowthData:
    """Assemble GrowthData from parsed RawTable objects.

    Args:
        tables: Parsed raw tables.

    Returns:
        GrowthData with all tables attached.
    """
    print()
    _print_title("STEP 3: TRANSFORM (ASSEMBLE GROWTH DATA)")

    data = GrowthData()
    for dataset in tables:
        print(f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points.")
        data.add_table(dataset)
    return data


def _copy_parquet_to_package(project_root: Path, version: str) -> None:
    """Copy generated parquet into the package data directory.

    Args:
        project_root: Root of the repository.
        version: Version string used for the parquet name.
    """
    src_parquet = OUTPUT_DIR / f"pygrowthstandards_{version}.parquet"
    dst_dir = Path(__file__).resolve().parent
    dst_parquet = dst_dir / f"pygrowthstandards_{version}.parquet"

    if not src_parquet.exists():
        print(f"Source parquet not found: {src_parquet}")
        return

    for parquet in dst_dir.glob("pygrowthstandards_*.parquet"):
        try:
            parquet.unlink()
            print(f"Deleted old destination Parquet: {parquet}")
        except Exception as exc:
            print(f"Failed to delete {parquet}: {exc}")

    shutil.copy2(src_parquet, dst_parquet)
    print(f"Copied {src_parquet} -> {dst_parquet}")


def _move_files_to_backup(project_root: Path, version: str) -> None:
    """Archive generated artifacts into the backup folder.

    Args:
        project_root: Root of the repository.
        version: Version string used for the artifact names.
    """
    src_parquet = project_root / "data" / f"pygrowthstandards_{version}.parquet"
    dst_dir = project_root / "data" / "backup"
    dst_parquet = dst_dir / f"pygrowthstandards_{version}.parquet"

    if not src_parquet.exists():
        print(f"Source parquet not found: {src_parquet}")
        return

    dst_dir.mkdir(parents=True, exist_ok=True)

    shutil.move(src_parquet, dst_parquet)
    print(f"Moved {src_parquet} -> {dst_parquet}")

    src_csv = src_parquet.with_suffix(".csv")
    if src_csv.exists():
        shutil.move(src_csv, dst_parquet.with_suffix(".csv"))
        print(f"Moved {src_csv} -> {dst_parquet.with_suffix('.csv')}")
    else:
        print(f"CSV file not found, skipping: {src_csv}")


def _save_outputs(data: GrowthData) -> None:
    print()
    _print_title("STEP 4: SAVE OUTPUT FILES")
    print(f"GrowthData version: {data.version}")
    data.save_parquet(OUTPUT_DIR)


def _copy_to_package(version: str) -> None:
    print()
    _print_title("STEP 5: COPY TO PACKAGE DIRECTORY")
    _copy_parquet_to_package(_PROJECT_ROOT, version)


def _archive_outputs(version: str) -> None:
    print()
    _print_title("STEP 6: ARCHIVE TO BACKUP")
    _move_files_to_backup(_PROJECT_ROOT, version)


def run_growth_etl() -> None:
    """Execute the growth reference ETL pipeline."""
    _prepare_backup_dir()
    raw_files = _discover_raw_files(RAW_ROOT)
    tables = _parse_raw_files(raw_files)
    if tables is None:
        return
    data = _build_growth_data(tables)
    _save_outputs(data)
    _copy_to_package(data.version)
    _archive_outputs(data.version)


def run() -> None:
    run_growth_etl()


def main() -> None:
    """Generate and publish reference datasets from raw inputs."""
    _print_title("GROWTH REFERENCE ETL PIPELINE")
    run_growth_etl()
    print("\nGrowth data generation complete.")


if __name__ == "__main__":
    main()
