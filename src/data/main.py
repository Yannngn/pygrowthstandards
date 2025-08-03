import glob

from .extract import RawTable
from .transform import GrowthData


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
