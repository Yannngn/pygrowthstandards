"""Transform raw growth tables into normalized reference datasets."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pandas as pd

from pygrowthstandards.config.growth import (
    AGE_GROUP_CHOICES,
    AgeGroupType,
    resolve_x_var_type,
)
from pygrowthstandards.data.extract import RawTable
from pygrowthstandards.utils.constants import MONTH, WEEK, YEAR
from pygrowthstandards.utils.version import get_package_version


@dataclass
class GrowthData:
    """Aggregates raw tables and produces normalized reference data.

    Attributes:
        version: Package version for generated artifacts.
        tables: Raw tables accumulated for processing.
    """

    version: str = field(default_factory=get_package_version)
    tables: list[RawTable] = field(default_factory=list)

    def add_table(self, table: RawTable) -> None:
        """Append a RawTable to the collection.

        Args:
            table: RawTable instance to add.
        """
        self.tables.append(table)

    def transform_all(self) -> None:
        """Convert all tables to a common x-axis unit (days)."""
        self.tables = list(map(self._transform_age_to_days, self.tables))

    def join_data(self) -> pd.DataFrame:
        """Combine all raw tables into a single normalized DataFrame.

        Returns:
            Joined DataFrame with canonical columns.
        """
        records = []
        for table in self.tables:
            table_dict = table.to_dict()
            table_dict.pop("x_var_unit")
            points = table_dict.pop("points")

            for point in points:
                assert isinstance(point, dict)
                record = {**table_dict, **point}
                records.append(record)

        df = pd.DataFrame(records)

        df["age_group"] = df.apply(
            lambda r: self._extract_age_group(r["name"], r["measurement_type"], r["x_var_type"], r["x"]),
            axis=1,
        )

        df["x_var_type"] = df["x_var_type"].apply(resolve_x_var_type)

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

    def save_parquet(self, path: str | Path = "data") -> None:
        """Persist the normalized data to parquet and CSV files.

        Args:
            path: Output directory or parquet path.
        """
        self.transform_all()
        df = self.join_data()

        if Path(path).suffix == ".parquet":
            df.to_parquet(path, index=False)
            return

        df.to_parquet(os.path.join(path, f"pygrowthstandards_{self.version}.parquet"), index=False)
        df.to_csv(os.path.join(path, f"pygrowthstandards_{self.version}.csv"), index=False)

    @staticmethod
    def _transform_age_to_days(data: RawTable) -> RawTable:
        """Normalize x values to days in-place.

        Args:
            data: RawTable to mutate.

        Returns:
            Mutated RawTable instance.
        """
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
    def _extract_age_group(table_name: str, measurement_type: str, x_var_type: str, age: int) -> AgeGroupType:
        """Determine the age group for a given data point.

        Args:
            table_name: Source table name.
            measurement_type: Measurement alias.
            x_var_type: Axis type.
            age: Age in days.

        Returns:
            Age group key.
        """
        if x_var_type in {"height", "length"}:
            return "0-2" if x_var_type == "length" else "2-5"

        if table_name in AGE_GROUP_CHOICES:
            return cast(AgeGroupType, table_name)

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
