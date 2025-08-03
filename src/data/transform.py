import glob
import os
from dataclasses import dataclass, field

import pandas as pd

from ..utils.constants import MONTH, WEEK
from .extract import RawTable


def transform_age_to_days(data: RawTable) -> RawTable:
    """
    Transforms the age in weeks to days for each DataPoint in the RawTable.

    :param data: The RawTable object containing the data points.
    :return: A new RawTable object with age converted to days.
    """
    if data.x_var_unit.lower().startswith("da"):
        return data

    for point in data.points:
        if data.x_var_unit.lower().startswith("we"):
            point.x = int(round(point.x * WEEK))
        elif data.x_var_unit.lower().startswith("mo"):
            point.x = int(round(point.x * MONTH))

    data.x_var_unit = "days"

    return data


@dataclass
class GrowthData:
    version: str = "0.1.0"
    tables: list[RawTable] = field(default_factory=list)

    def add_table(self, table: RawTable) -> None:
        """
        Adds a RawTable to the GrowthData collection.

        :param table: The RawTable object to add.
        """
        self.tables.append(table)

    def transform_all(self) -> None:
        """
        Transforms all tables in the GrowthData collection by converting age to days.
        """
        for i, table in enumerate(self.tables):
            self.tables[i] = transform_age_to_days(table)
            print(f"Transformed table {table.name} with {len(table.points)} points to days.")

    def join_data(self) -> pd.DataFrame:
        """
        Joins all RawTables in the GrowthData collection into a single DataFrame.

        :return: A pandas DataFrame containing all data points from the tables.
        """
        records = []
        for table in self.tables:
            table_dict = table.to_dict()
            points: list[dict] = table_dict.pop("points")

            for point in points:
                record = {**table_dict, **point}
                records.append(record)

        return pd.DataFrame(records)

    def save_parquet(self, path: str = "data") -> None:
        """
        Saves the joined data to a Parquet file for efficient storage.

        :param path: The file path to save the Parquet file.
        """
        df = self.join_data()

        if path.endswith(".parquet"):
            df.to_parquet(path, index=False)
            return

        df.to_parquet(os.path.join(path, f"pygrowthstandards_{self.version}.parquet"), index=False)
        df.to_csv(os.path.join(path, f"pygrowthstandards_{self.version}.csv"), index=False)


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
