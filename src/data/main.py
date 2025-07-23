import glob
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.data.extract import RawTable
from src.data.transform import GrowthData

# TODO: Add a curated list of growth tables to load


def main():
    data = GrowthData()
    for f in glob.glob("data/raw/**/*.xlsx"):
        dataset = RawTable.from_xlsx(f)

        print(f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points.")

        data.add_table(dataset)

    for f in glob.glob("data/raw/**/*.csv"):
        if "cdc" in f:
            continue

        dataset = RawTable.from_csv(f)

        print(f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points.")

        data.add_table(dataset)

    data.transform_all()
    data.save_parquet()


if __name__ == "__main__":
    main()
