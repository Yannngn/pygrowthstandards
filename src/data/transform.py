"""Transform and manage raw LMS growth data.

This module provides functions and classes to convert and aggregate LMS reference tables:

Functions:
    transform_age_to_days: Convert a RawTable's age units to days.

Classes:
    GrowthData: Collects multiple RawTable instances, transforms data, joins, and exports.

Examples:
    python -m src.data.transform

Todo:
    * Add CLI support for custom output paths and formats.
"""

import glob
import os
from dataclasses import dataclass, field

import pandas as pd

from ..utils.constants import MONTH, WEEK, YEAR
from .extract import RawTable


def transform_age_to_days(data: RawTable) -> RawTable:
    """
    Transforms the age values in a RawTable to days.

    Args:
        data (RawTable): The table whose data points are to be converted.

    Returns:
        RawTable: The same table with x values converted to days and unit updated.
    """
    if data.x_var_unit.lower().startswith("da"):
        data.x_var_unit = "day"
        return data

    for point in data.points:
        if data.x_var_unit.lower().startswith("we"):
            point.x = int(round(point.x * WEEK))
        elif data.x_var_unit.lower().startswith("mo"):
            point.x = int(round(point.x * MONTH))

    data.x_var_unit = "day"

    return data

# TODO: Assert types
@dataclass
class GrowthData:
    """
    Aggregates multiple RawTable instances and transforms them for output.

    Attributes:
        version (str): Version identifier for output files.
        tables (list[RawTable]): List of raw tables added.
    """
    version: str = "0.1.1"
    tables: list[RawTable] = field(default_factory=list)

    def add_table(self, table: RawTable) -> None:
        """
        Adds a RawTable to the collection.

        Args:
            table (RawTable): The table to append.
        """
        self.tables.append(table)

    def transform_all(self) -> None:
        """
        Converts all tables' x values to days in place.
        """
        for i, table in enumerate(self.tables):
            self.tables[i] = transform_age_to_days(table)
            print(f"Transformed table {table.name} with {len(table.points)} points to days.")

    def join_data(self) -> pd.DataFrame:
        """
        Joins all tables into one DataFrame of records.

        Returns:
            pandas.DataFrame: DataFrame with merged table and point fields.
        """
        records = []
        for table in self.tables:
            table_dict = table.to_dict()
            points: list[dict] = table_dict.pop("points")

            for point in points:
                record = {**table_dict, **point}
                records.append(record)

        df = pd.DataFrame(records)

        for idx, row in df.iterrows():
            if row["age_group"] in [
                "very_preterm_newborn",
                "newborn",
                "very_preterm_growth",
            ]:
                continue

            if row["x_var_type"] == "stature":
                df.at[idx, "x_var_unit"] = "cm"  # TODO: set this in extracting module
                continue

            if row["age_group"] == row["name"]:
                if row["x"] < 2 * YEAR:
                    df.at[idx, "age_group"] = "0-2"
                    continue
                if row["x"] < 5 * YEAR:
                    df.at[idx, "age_group"] = "2-5"
                    continue
                if row["x"] < 10 * YEAR:
                    df.at[idx, "age_group"] = "5-10"
                    continue

                df.at[idx, "age_group"] = "10-19"

        return df

    def save_parquet(self, path: str = "data") -> None:
        """
        Writes the joined data to Parquet (and CSV) in the specified path.

        Args:
            path (str): Directory or filepath for output.
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
