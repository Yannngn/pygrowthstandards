import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal as D
from typing import Literal

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.utils.choices import (
    AGE_GROUP_CHOICES,
    AGE_GROUP_TYPE,
    MEASUREMENT_TYPE_TYPE,
    TABLE_NAME_TYPE,
)
from src.utils.constants import MONTH, WEEK, YEAR
from src.utils.decimal_stats import estimate_lms_from_sd

X_TEMPLATE = D("0.00")
MU_TEMPLATE = D("0.0000")
LAMBDA_TEMPLATE = D("0.0000")
SIGMA_TEMPLATE = D("0.00000")

UNITS = {
    "stature": "cm",
    "weight": "kg",
    "head_circumference": "cm",
    "body_mass_index": "kg/m²",
    "weight_length": "kg/cm",
    "weight_height": "kg/cm",
    "stature_velocity": "cm/month",
    "weight_velocity": "kg/month",
    "head_circumference_velocity": "cm/month",
}

DataSourceType = Literal["who", "intergrowth"]
DataSexType = Literal["M", "F", "U"]
DataUnitType = Literal["days", "cm"]
DataUnitNameType = Literal["age", "gestational_age", "stature"]


@dataclass(order=True, eq=True)
class DataPoint:
    x: D
    L: D
    M: D
    S: D

    @classmethod
    def from_dict(cls, data: dict) -> "DataPoint":
        """
        Create a DataPoint instance from a dictionary.

        Args:
            data (dict): Dictionary containing 'x', 'L', 'M', and 'S' keys.

        Returns:
            DataPoint: An instance of DataPoint.
        """
        if "l" in data and "m" in data and "s" in data:
            return cls(
                x=D(data["x"]),
                L=D(data["l"]),
                M=D(data["m"]),
                S=D(data["s"]),
            )

        L, M, S = DataPoint._create_lms_data(data)

        return cls(D(data["x"]), L, M, S)

    def to_dict(self) -> dict:
        """
        Convert the DataPoint instance to a dictionary.

        Returns:
            dict: Dictionary representation of the DataPoint.
        """
        return {
            "x": str(self.x),
            "L": str(self.L.quantize(LAMBDA_TEMPLATE)),
            "M": str(self.M.quantize(MU_TEMPLATE)),
            "S": str(self.S.quantize(SIGMA_TEMPLATE)),
        }

    @staticmethod
    def _create_lms_data(data: dict) -> tuple[D, D, D]:
        required_sd = ["sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3"]
        if not all(k in data for k in required_sd):
            raise ValueError("Required SD columns (sd3neg to sd3) are missing.")

        sd_keys = [f"sd{i}neg" for i in range(5, 0, -1) if f"sd{i}neg" in data]
        sd_keys += [f"sd{i}" for i in range(0, 6) if f"sd{i}" in data]

        zscores = np.array([-int(sd[2]) if sd.endswith("neg") else int(sd[2]) for sd in sd_keys])
        values = np.array([data[sd] for sd in sd_keys], dtype=float)

        return estimate_lms_from_sd(zscores, values)

    def __eq__(self, other):
        if not isinstance(other, DataPoint):
            return NotImplemented
        return self.x == other.x


@dataclass
class Dataset:
    source: DataSourceType  # who
    table: TABLE_NAME_TYPE  # child_growth
    measurement_type: MEASUREMENT_TYPE_TYPE  # stature
    sex: DataSexType  # M
    unit_name: DataUnitNameType  # age
    unit_type: DataUnitType  # days

    points: list[DataPoint] = field(default_factory=list)

    min_x: D = field(init=False)
    max_x: D = field(init=False)

    age_group: AGE_GROUP_TYPE = field(init=False)

    def __post_init__(self):
        if not self.points:
            raise ValueError("Points list cannot be empty.")

        xs = [point.x for point in self.points if point.x is not None]
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.points.sort(key=lambda p: p.x)

        if self.measurement_type.endswith("_height"):
            self.age_group = self.table if self.table in AGE_GROUP_CHOICES else "2-5"  # type: ignore
            self.measurement_type = "weight"
            return

        if self.measurement_type.endswith("_length"):
            self.age_group = self.table if self.table in AGE_GROUP_CHOICES else "0-2"  # type: ignore
            self.measurement_type = "weight"
            return

        if self.table in AGE_GROUP_CHOICES:
            self.age_group = self.table  # type: ignore

            return

        group = f"{int(round(float(self.min_x) / YEAR))}-{int(round(float(self.max_x) / YEAR))}"
        if group in list(AGE_GROUP_CHOICES) + ["0-5", "5-19"]:
            self.age_group = group  # type: ignore

            return

        raise ValueError(f"Invalid age group '{group}' for dataset {self.source} - {self.table} - {self.measurement_type} - {self.sex}")

    @classmethod
    def from_csv(cls, csv_path: str) -> "Dataset":
        """
        Create a Dataset instance from a CSV file.

        Args:
            csv_path (str): Path to the CSV file.

        Returns:
            Dataset: An instance of Dataset.
        """
        df = pd.read_csv(csv_path, dtype=str, encoding="utf-8")

        def get_points(data: pd.DataFrame):
            data_points = []

            for _, row in data.iterrows():
                data_point = DataPoint.from_dict(row.to_dict())
                data_points.append(data_point)

            return data_points

        filename = os.path.splitext(os.path.basename(csv_path))[0]
        parts = filename.split("-")
        print(filename)
        if len(parts) > 4:
            _ = parts.pop()

        sex = parts.pop().upper()

        if sex not in ["M", "F", "U"]:  # 1mon and 2mon from velocity datasets
            sex = parts.pop().upper()

        measurement_type = parts.pop()
        table = parts.pop().replace("birth", "newborn")
        source = parts.pop()
        unit = "gestational_age" if "birth" in filename else "age"

        df.columns = [col.lower() for col in df.columns]
        x_column = df.columns[0]

        # Weight for Length/Height datasets
        if x_column in ["length", "height"]:
            df["x"] = df[x_column]

            return cls(source=source, table=table, measurement_type=measurement_type, sex=sex, unit_name="stature", unit_type="cm", points=get_points(df))  # type: ignore

        # Velocity datasets
        elif x_column in ["interval"]:
            # Normalize dash types and strip whitespace
            df[x_column] = df[x_column].str.replace("\u2013", "-").str.strip()

            interval_min_list, interval_max_list = [], []
            for value in df[x_column]:
                age_parts: list[str] = str(value).split("-")
                min_part, max_part = age_parts[0].strip(), age_parts[1].strip()

                def parse_interval(part: str) -> int:
                    if part.endswith("wks"):
                        return int(float(part.replace("wks", "").strip()) * WEEK)

                    if part.endswith("mo"):
                        return int(float(part.replace("mo", "").strip()) * MONTH)

                    return int(float(part) * MONTH)

                interval_min_list.append(parse_interval(min_part))
                interval_max_list.append(parse_interval(max_part))

            df["x"] = interval_min_list
            return cls(source=source, table=table, measurement_type=measurement_type, sex=sex, unit_name=unit, unit_type="days", points=get_points(df))  # type: ignore

        # Age in days, weeks, or months
        elif x_column in ["weeks"]:
            df["x"] = df[x_column].astype(float).mul(WEEK).astype(int)

        elif x_column in ["month"]:
            df["x"] = df[x_column].astype(float).mul(MONTH).astype(int)

        else:
            df["x"] = df[x_column].astype(float).astype(int)

        return cls(source=source, table=table, measurement_type=measurement_type, sex=sex, unit_name=unit, unit_type="days", points=get_points(df))  # type: ignore

    @classmethod
    def from_xlsx(cls, xlsx_path: str) -> "Dataset":
        """
        Create a Dataset instance from an XLSX file.

        Args:
            xlsx_path (str): Path to the XLSX file.

        Returns:
            Dataset: An instance of Dataset.
        """

        df = pd.read_excel(xlsx_path, sheet_name=None)

        # Assume we want the first sheet only
        first_sheet_name = list(df.keys())[0]
        first_sheet_data = df[first_sheet_name]

        # Use the Excel file name (without extension) for the temp CSV file
        base_name = os.path.splitext(os.path.basename(xlsx_path))[0]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", prefix=base_name + "-", delete=False) as tmpfile:
            first_sheet_data.to_csv(tmpfile.name, index=False)
            tmp_csv_path = tmpfile.name

        # Create Dataset from the temporary CSV
        dataset = cls.from_csv(tmp_csv_path)

        # Remove the temporary file
        os.remove(tmp_csv_path)

        return dataset

    def to_dict(self) -> dict:
        """
        Convert the Dataset instance to a dictionary.

        Returns:
            dict: Dictionary representation of the Dataset.
        """
        return {
            # "source": self.source,
            "table": self.table,
            "age_group": self.age_group,
            "sex": self.sex,
            "measurement_type": self.measurement_type,
            "unit_name": self.unit_name,
            # "unit_type": self.unit_type,
            "points": [point.to_dict() for point in self.points],
        }


@dataclass
class GrowthData:
    version: str = "0.1.0"
    datasets: list[Dataset] = field(default_factory=list)

    consolidated_data: dict[str, str | list[dict]] = field(init=False, default_factory=dict)

    def __post_init__(self):
        if self.datasets is None:
            self.datasets = []

    def add_dataset(self, dataset: Dataset):
        """
        Add a Dataset to the GrowthData instance.

        Args:
            dataset (Dataset): The Dataset to add.
        """
        if not isinstance(dataset, Dataset):
            raise TypeError("Expected a Dataset instance.")
        self.datasets.append(dataset)

    def add_csv(self, csv_path: str):
        """
        Add a Dataset from a CSV file to the GrowthData instance.

        Args:
            csv_path (str): Path to the CSV file.
        """
        dataset = Dataset.from_csv(csv_path)
        self.add_dataset(dataset)

    def add_xlsx(self, xlsx_path: str):
        """
        Add a Dataset from an XLSX file to the GrowthData instance.

        Args:
            xlsx_path (str): Path to the XLSX file.
        """
        dataset = Dataset.from_xlsx(xlsx_path)
        self.add_dataset(dataset)

    def process_data(self):
        complete_data = []
        for dataset in self.datasets:
            data = dataset.to_dict()
            points: list[dict] = data.pop("points", [])
            complete_data.extend([{**data, **point} for point in points])

        for item in complete_data:
            if item.get("age_group") == "0-5":
                x_years = float(item["x"]) / YEAR
                item["age_group"] = "0-2" if x_years < 2 else "2-5"
            elif item.get("age_group") == "5-19":
                x_years = float(item["x"]) / YEAR
                item["age_group"] = "5-10" if x_years < 10 else "10-19"

        self.consolidated_data = {"version": self.version, "data": complete_data}

    def to_csv(self, output_dir: str):
        """
        Save the consolidated data points to a CSV file in the specified output directory.
        Args:
            output_dir (str): Directory where the CSV file will be saved.
        """

        self.process_data()

        df = pd.DataFrame(self.consolidated_data["data"])
        df.to_csv(os.path.join(output_dir, "pygrowthstandards.csv"), index=False)

    def to_json(self, output_dir: str):
        """
        Save the consolidated data points to a JSON file in the specified output directory.
        Args:
            output_dir (str): Directory where the JSON file will be saved.
        """
        self.process_data()

        output_file = os.path.join(output_dir, "pygrowthstandards.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.consolidated_data, f, ensure_ascii=False)
        self.process_data()

        output_file = os.path.join(output_dir, "pygrowthstandards.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.consolidated_data, f, ensure_ascii=False)
