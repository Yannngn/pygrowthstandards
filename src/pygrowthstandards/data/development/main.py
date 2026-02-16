"""Main orchestration for developmental milestone ETL pipeline."""

import shutil
from pathlib import Path

from pygrowthstandards.data.development.extract import discover_milestone_files, parse_milestone_csv
from pygrowthstandards.data.development.transform import aggregate_milestone_tables

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
RAW_ROOT = _PROJECT_ROOT / "data" / "raw" / "development"
OUTPUT_DIR = _PROJECT_ROOT / "data"


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


def _discover_csv_files() -> list[Path]:
    print()
    _print_title("STEP 1: DISCOVER MILESTONE FILES")

    csv_files = discover_milestone_files(RAW_ROOT)
    if not csv_files:
        print(f"ERROR: No milestone CSV files found in {RAW_ROOT}")
        return []

    print(f"Found {len(csv_files)} milestone CSV file(s):")
    for csv_file in csv_files:
        print(f"  - {csv_file.name}")

    return csv_files


def _parse_csv_files(csv_files: list[Path]) -> list | None:
    if not csv_files:
        return None
    print()
    _print_title("STEP 2: EXTRACT (PARSE CSV FILES)")

    raw_tables = []

    for csv_file in csv_files:
        try:
            table = parse_milestone_csv(csv_file)
            raw_tables.append(table)
        except Exception as e:
            print(f"ERROR: Failed to parse {csv_file.name}: {e}")
            return None

    print(f"\nSuccessfully parsed {len(raw_tables)} table(s)")
    return raw_tables


def _aggregate_tables(raw_tables):
    print()
    _print_title("STEP 3: TRANSFORM (VALIDATE AND AGGREGATE)")

    try:
        milestone_data = aggregate_milestone_tables(raw_tables)
    except Exception as e:
        print(f"ERROR: Failed to aggregate milestone data: {e}")
        return None

    print("\nTransform complete")

    return milestone_data


def _save_output_files(milestone_data):
    print()
    _print_title("STEP 4: SAVE OUTPUT FILES")
    output_basename = f"development_milestones_{milestone_data.version}"
    parquet_output = OUTPUT_DIR / f"{output_basename}.parquet"
    csv_output = OUTPUT_DIR / f"{output_basename}.csv"
    try:
        milestone_data.dataframe.to_parquet(parquet_output, index=False)
        print(f"Saved parquet: {parquet_output}")
        milestone_data.dataframe.to_csv(csv_output, index=False)
        print(f"Saved CSV: {csv_output}")
    except Exception as e:
        print(f"ERROR: Failed to save output files: {e}")
        return None, None, None

    return output_basename, parquet_output, csv_output


def _copy_to_package(output_basename: str, parquet_output: Path) -> Path | None:
    print()
    _print_title("STEP 5: COPY TO PACKAGE DIRECTORY")

    package_dir = Path(__file__).resolve().parents[1]
    package_versioned = package_dir / f"{output_basename}.parquet"

    for existing_file in package_dir.glob("development_milestones*.parquet"):
        if existing_file == package_versioned:
            continue
        try:
            existing_file.unlink()
            print(f"Deleted old package file: {existing_file}")
        except Exception as exc:
            print(f"Failed to delete {existing_file}: {exc}")

    try:
        shutil.copy2(parquet_output, package_versioned)
        print(f"Copied to package: {package_versioned}")
    except Exception as e:
        print(f"ERROR: Failed to copy to package directory: {e}")
        return None

    return package_versioned


def _archive_current_version(
    output_basename: str,
    parquet_output: Path,
    csv_output: Path,
    backup_dir: Path,
) -> tuple[Path, Path]:
    print()
    _print_title("STEP 6: ARCHIVE TO BACKUP")
    backup_parquet = backup_dir / f"{output_basename}.parquet"
    backup_csv = backup_dir / f"{output_basename}.csv"
    try:
        if backup_parquet.exists():
            backup_parquet.unlink()
        if backup_csv.exists():
            backup_csv.unlink()
        shutil.move(parquet_output, backup_parquet)
        print(f"Moved parquet to backup: {backup_parquet}")
        shutil.move(csv_output, backup_csv)
        print(f"Moved CSV to backup: {backup_csv}")
    except Exception as e:
        print(f"WARNING: Failed to archive files: {e}")

    return backup_parquet, backup_csv


def _print_summary(
    milestone_data,
    package_versioned: Path,
    backup_parquet: Path,
    backup_csv: Path,
) -> None:
    print()
    _print_title("ETL PIPELINE COMPLETE")
    print(f"\nProcessed {len(milestone_data.dataframe)} milestones")
    print(f"Sources: {milestone_data.dataframe['source'].unique().tolist()}")
    print(f"Domains: {milestone_data.dataframe['standardized_domain'].nunique()}")
    print("\nOutput files:")
    print(f"  - Package (versioned): {package_versioned}")
    print(f"  - Backup: {backup_parquet}")
    print(f"  - Backup CSV: {backup_csv}")
    print("\nSuccess!")


def run_milestone_etl() -> None:
    """Execute the full milestone ETL pipeline.

    Steps:
        1. Discover milestone CSV files in data/raw/development/
        2. Extract (parse CSV files)
        3. Transform (validate and aggregate)
        4. Save to parquet and CSV
        5. Copy to package directory
        6. Archive previous version
    """

    backup_dir = _prepare_backup_dir()
    csv_files = _discover_csv_files()
    raw_tables = _parse_csv_files(csv_files)

    if raw_tables is None:
        return

    milestone_data = _aggregate_tables(raw_tables)
    if milestone_data is None:
        return

    output_basename, parquet_output, csv_output = _save_output_files(milestone_data)
    if output_basename is None:
        return

    package_versioned = _copy_to_package(output_basename, parquet_output)
    if package_versioned is None:
        return

    backup_parquet, backup_csv = _archive_current_version(output_basename, parquet_output, csv_output, backup_dir)
    _print_summary(milestone_data, package_versioned, backup_parquet, backup_csv)


def main() -> None:
    print("=" * 80)
    print("DEVELOPMENTAL MILESTONE ETL PIPELINE")
    print("=" * 80)
    run_milestone_etl()


if __name__ == "__main__":
    run_milestone_etl()
