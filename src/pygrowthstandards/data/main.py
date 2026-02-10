"""CLI for rebuilding packaged growth reference data."""

import shutil
from pathlib import Path

from pygrowthstandards.data.extract import RawTable
from pygrowthstandards.data.transform import GrowthData

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_ROOT = _PROJECT_ROOT / "data" / "raw"
OUTPUT_ROOT = _PROJECT_ROOT / "data"

CSV_ONLY = True


def _iter_raw_tables(raw_root: Path) -> list[RawTable]:
    """Discover raw files and parse them into RawTable objects.

    Args:
        raw_root: Root path containing raw data files.

    Returns:
        List of parsed RawTable instances.
    """
    tables: list[RawTable] = []

    if not CSV_ONLY:
        for raw_file in raw_root.rglob("*.xlsx"):
            dataset = RawTable.from_xlsx(raw_file)
            tables.append(dataset)

    for raw_file in raw_root.rglob("*.csv"):
        if not raw_file.name.startswith("who") and not raw_file.name.startswith("intergrowth"):
            continue
        dataset = RawTable.from_csv(raw_file)
        tables.append(dataset)

    return tables


def _build_growth_data(tables: list[RawTable]) -> GrowthData:
    """Assemble GrowthData from parsed RawTable objects.

    Args:
        tables: Parsed raw tables.

    Returns:
        GrowthData with all tables attached.
    """
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
    src_parquet = project_root / "data" / f"pygrowthstandards_{version}.parquet"
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


def main() -> None:
    """Generate and publish reference datasets from raw inputs."""
    tables = _iter_raw_tables(RAW_ROOT)
    data = _build_growth_data(tables)

    print(f"GrowthData version: {data.version}")
    data.save_parquet(OUTPUT_ROOT)

    project_root = Path(__file__).resolve().parents[3]
    _copy_parquet_to_package(project_root, data.version)
    _move_files_to_backup(project_root, data.version)


if __name__ == "__main__":
    main()
