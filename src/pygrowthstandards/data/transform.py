import glob
import os
from dataclasses import dataclass, field

import pandas as pd

from ..utils.config import AGE_GROUP_CHOICES, AgeGroupType
from ..utils.constants import MONTH, WEEK, YEAR
from .extract import RawTable


@dataclass
class GrowthData:
    version: str = "1.1"
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
        self.tables = list(map(self._transform_age_to_days, self.tables))

    def join_data(self) -> pd.DataFrame:
        """
        Joins all RawTables in the GrowthData collection into a single DataFrame.

        :return: A pandas DataFrame containing all data points from the tables.
        """
        records = []
        for table in self.tables:
            table_dict = table.to_dict()
            table_dict.pop("x_var_unit")
            points: list[dict] = table_dict.pop("points")

            for point in points:
                record = {**table_dict, **point}
                records.append(record)

        df = pd.DataFrame(records)

        df["age_group"] = df.apply(
            lambda r: self._extract_age_group(
                r["name"], r["measurement_type"], r["x_var_type"], r["x"]
            ),
            axis=1,
        )

        df["x_var_type"] = df.apply(
            lambda r: "stature"
            if r["x_var_type"] in {"length", "height"}
            else r["x_var_type"],
            axis=1,
        )

        # ensure required columns exist
        required = [
            "source",
            "age_group",
            "name",
            "sex",
            "measurement_type",
            "x_var_type",
            "x",
            "l",
            "m",
            "s",
            "is_derived",
        ]

        return df[required]

    def save_parquet(self, path: str = "data") -> None:
        """
        Saves the joined data to a Parquet file for efficient storage.

        :param path: The file path to save the Parquet file.
        """
        self.transform_all()
        df = self.join_data()

        if path.endswith(".parquet"):
            df.to_parquet(path, index=False)
            return

        df.to_parquet(
            os.path.join(path, f"pygrowthstandards_{self.version}.parquet"), index=False
        )
        df.to_csv(
            os.path.join(path, f"pygrowthstandards_{self.version}.csv"), index=False
        )

    @staticmethod
    def _transform_age_to_days(data: RawTable) -> RawTable:
        if data.x_var_unit.lower().startswith("da"):
            data.x_var_unit = "days"
            return data

        for point in data.points:
            if data.x_var_unit.lower().startswith("we"):
                point.x = int(round(point.x * WEEK))
            elif data.x_var_unit.lower().startswith("mo"):
                point.x = int(round(point.x * MONTH))

        data.x_var_unit = "days"

        return data

    @staticmethod
    def _extract_age_group(
        table_name: str, measurement_type: str, x_var_type: str, age: int
    ) -> AgeGroupType:
        if x_var_type in {"height", "length"}:
            return "0-2" if x_var_type == "length" else "2-5"

        if table_name in AGE_GROUP_CHOICES:
            return table_name  # type: ignore

        if measurement_type.endswith("velocity"):
            if age < 1 * YEAR:
                return "0-1"

        if age < 2 * YEAR:
            return "0-2"
        if age < 5 * YEAR:
            return "2-5"
        if age < 10 * YEAR:
            return "5-10"

        return "10-19"


def main():
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

    data.save_parquet()


if __name__ == "__main__":
    main()
