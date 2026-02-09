import shutil
from pathlib import Path

from pygrowthstandards.data.extract import RawTable
from pygrowthstandards.data.transform import GrowthData

RAW_ROOT = Path("data/raw")
OUTPUT_ROOT = Path("data")


def _iter_raw_tables(raw_root: Path) -> list[RawTable]:
    tables: list[RawTable] = []

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
    data = GrowthData()
    for dataset in tables:
        print(f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points.")
        data.add_table(dataset)
    return data


def _copy_parquet_to_package(project_root: Path, version: str) -> None:
    src_parquet = project_root / "data" / f"pygrowthstandards_{version}.parquet"
    dst_dir = Path(__file__).resolve().parent
    dst_parquet = dst_dir / f"pygrowthstandards_{version}.parquet"

    for parquet in dst_dir.glob("pygrowthstandards_*.parquet"):
        try:
            parquet.unlink()
            print(f"Deleted old destination Parquet: {parquet}")
        except Exception as exc:
            print(f"Failed to delete {parquet}: {exc}")

    if not src_parquet.exists():
        print(f"Source parquet not found: {src_parquet}")
        return

    shutil.copy2(src_parquet, dst_parquet)
    print(f"Copied {src_parquet} -> {dst_parquet}")


def main() -> None:
    tables = _iter_raw_tables(RAW_ROOT)
    data = _build_growth_data(tables)

    print(f"GrowthData version: {data.version}")
    data.save_parquet(OUTPUT_ROOT)

    project_root = Path(__file__).resolve().parents[3]
    _copy_parquet_to_package(project_root, data.version)


if __name__ == "__main__":
    main()
