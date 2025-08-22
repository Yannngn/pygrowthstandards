import glob
import os
import shutil
from pathlib import Path

from .extract import RawTable
from .transform import GrowthData


def main():
    print(f"GrowthData version: {GrowthData.version}")

    # Delete older CSV files
    for f in glob.glob("data/pygrowthstandards_*.csv"):
        try:
            os.remove(f)
            print(f"Deleted old CSV: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")

    # Delete older Parquet files
    for f in glob.glob("data/pygrowthstandards_*.parquet"):
        try:
            os.remove(f)
            print(f"Deleted old Parquet: {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")

    data = GrowthData()
    for f in glob.glob("data/raw/**/*.xlsx"):
        dataset = RawTable.from_xlsx(f)

        print(
            f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points."
        )

        data.add_table(dataset)

    for f in glob.glob("data/raw/**/*.csv"):
        if "cdc" in f:
            continue

        dataset = RawTable.from_csv(f)

        print(
            f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points."
        )

        data.add_table(dataset)

    data.transform_all()
    data.save_parquet()


if __name__ == "__main__":
    main()

    # project_root -> .../pygrowthstandards (project root)
    project_root = Path(__file__).resolve().parents[3]
    src_parquet = (
        project_root / "data" / f"pygrowthstandards_{GrowthData.version}.parquet"
    )
    dst_parquet = (
        Path(__file__).resolve().parent
        / f"pygrowthstandards_{GrowthData.version}.parquet"
    )

    try:
        # Remove old parquet files in destination folder
        dst_dir = dst_parquet.parent
        for f in dst_dir.glob("pygrowthstandards_*.parquet"):
            try:
                if f.exists():
                    f.unlink()
                    print(f"Deleted old destination Parquet: {f}")
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

        if src_parquet.exists():
            shutil.copy2(src_parquet, dst_parquet)
            print(f"Copied {src_parquet} -> {dst_parquet}")
        else:
            print(f"Source parquet not found: {src_parquet}")
    except Exception as e:
        print(f"Failed to copy parquet: {e}")
