import json
import logging
import os
import sys
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal as D

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.utils.constants import MONTH, WEEK
from src.utils.decimal_stats import estimate_lms_from_sd

DATASETS = ["newborn_size", "very_preterm_growth", "growth"]

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
    "head_circumference_velocity": "cm/month",
    "length_velocity": "cm/month",
    "weight_velocity": "kg/month",
}

# TODO: Fix json


@dataclass
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


@dataclass
class Dataset:
    source: str
    name: str
    measurement_type: str
    sex: str
    points: list[DataPoint] = field(default_factory=list)
    x_axis: str = "days"
    min_age: int | None = None
    max_age: int | None = None

    def __post_init__(self):
        if self.points:
            self.points.sort(key=lambda p: p.x)

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
        source = parts[0]
        name = parts[1]
        measurement_type = parts[2]
        sex = parts[3]

        df.columns = [col.lower() for col in df.columns]
        x_column = df.columns[0]

        # Weight for Lenght/Height datasets
        if x_column == "length" or x_column == "height":
            df["x"] = df[x_column]
            return cls(source=source, name=name, measurement_type=measurement_type, x_axis=x_column.lower(), sex=sex, points=get_points(df))

        # Velocity datasets
        elif x_column == "interval":
            # Normalize dash types and strip whitespace
            df[x_column] = df[x_column].str.replace("–", "-").str.strip()

            interval_min_list, interval_max_list = [], []
            for value in df[x_column]:
                parts: list[str] = str(value).split("-")
                min_part, max_part = parts[0].strip(), parts[1].strip()

                def parse_interval(part: str) -> int:
                    if part.endswith("wks"):
                        return int(float(part.replace(" wks", "").strip()) * WEEK)
                    elif part.endswith("mo"):
                        return int(float(part.replace(" mo", "").strip()) * MONTH)
                    else:
                        return int(float(part) * MONTH)

                interval_min_list.append(parse_interval(min_part))
                interval_max_list.append(parse_interval(max_part))

            max_value = max(interval_max_list)
            df["x"] = interval_min_list
            return cls(
                source=source,
                name=name,
                measurement_type=measurement_type,
                sex=sex,
                min_age=min(interval_min_list),
                max_age=max_value,
                points=get_points(df),
            )

        # Age in days, weeks, or months
        elif x_column == "weeks":
            df["x"] = df[x_column].astype(float).mul(WEEK).astype(int)

        elif x_column == "month":
            df["x"] = df[x_column].astype(float).mul(MONTH).astype(int)

        else:
            df["x"] = df[x_column].astype(float).astype(int)

        min_age = df["x"].min()
        max_age = df["x"].max()

        return cls(
            source=source,
            name=name,
            measurement_type=measurement_type,
            sex=sex,
            min_age=min_age,
            max_age=max_age,
            points=get_points(df),
        )

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


@dataclass
class GrowthData:
    source: str
    name: str
    measurement_type: str
    sex: str
    datasets: list[Dataset] = field(default_factory=list)
    x_axis: str | None = None
    min_x: int | None = None
    max_x: int | None = None

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

    def consolidate_data(self) -> list[DataPoint]:
        consolidated_points = []
        min_x = max_x = x_axis = None

        for dataset in self.datasets:
            assert dataset.sex == self.sex, "All datasets must have the same sex."
            assert dataset.source == self.source, "All datasets must have the same source."
            assert dataset.measurement_type == self.measurement_type, "All datasets must have the same measurement type."

            if x_axis is None:
                x_axis = dataset.x_axis

            assert dataset.x_axis == x_axis, "All datasets must have the same x-axis."

            if dataset.min_age is not None and (min_x is None or dataset.min_age < min_x):
                min_x = int(dataset.min_age)  # type: ignore

            if dataset.max_age is not None and (max_x is None or dataset.max_age > max_x):
                max_x = int(dataset.max_age)  # type: ignore

            consolidated_points.extend(dataset.points)

        if self.measurement_type in ["weight_length", "weight_height"]:
            min_x = min(point.x for point in consolidated_points if point.x is not None)
            max_x = max(point.x for point in consolidated_points if point.x is not None)

        self.min_x = min_x
        self.max_x = max_x
        self.x_axis = x_axis

        # Remove duplicates based on x value, keeping the first occurrence
        seen_x = set()
        unique_points = []
        for point in consolidated_points:
            if point.x not in seen_x:
                unique_points.append(point)
                seen_x.add(point.x)
        consolidated_points = unique_points

        # Sort consolidated points by x value
        consolidated_points.sort(key=lambda p: p.x)

        return consolidated_points

    def to_csv(self, output_dir: str):
        """
        Save the consolidated data points to a CSV file in the specified output directory.
        Args:
            output_dir (str): Directory where the CSV file will be saved.
        """

        consolidated_points = self.consolidate_data()

        if not consolidated_points:
            logging.warning("No data points to save.")
            return

        points = [point.to_dict() for point in consolidated_points]

        data = {
            "x": [point["x"] for point in points],
            "L": [point["L"] for point in points],
            "M": [point["M"] for point in points],
            "S": [point["S"] for point in points],
        }

        df = pd.DataFrame(data)
        output_file = os.path.join(output_dir, f"{self.source}-{self.name}-{self.measurement_type}-{self.sex}-lms.csv")
        df.to_csv(output_file, index=False)

    def to_json(self, output_dir: str):
        """
        Save the consolidated data points to a JSON file in the specified output directory.
        Args:
            output_dir (str): Directory where the JSON file will be saved.
        """
        consolidated_points = self.consolidate_data()
        if not consolidated_points:
            logging.warning("No data points to save.")
            return

        def is_int(value: D | int) -> bool:
            """
            Check if a Decimal value is an integer.
            """
            if isinstance(value, int):
                return True

            return value == value.to_integral_value()

        data = {
            "source": self.source,
            "name": self.name,
            "measurement_type": self.measurement_type,
            "sex": self.sex,
            "x_axis": self.x_axis,
            "unit": UNITS.get(self.measurement_type, ""),
            "min_x": int(self.min_x) if is_int(self.min_x) else str(D(self.min_x).quantize(X_TEMPLATE)),  # type: ignore
            "max_x": int(self.max_x) if is_int(self.max_x) else str(D(self.max_x).quantize(X_TEMPLATE)),  # type: ignore
            "points": [
                {
                    "x": int(p.x) if is_int(p.x) else str(p.x.quantize(X_TEMPLATE)),
                    "L": str(p.L.quantize(LAMBDA_TEMPLATE)),
                    "M": str(p.M.quantize(MU_TEMPLATE)),
                    "S": str(p.S.quantize(SIGMA_TEMPLATE)),
                }
                for p in consolidated_points
            ],
        }

        output_file = os.path.join(output_dir, f"{self.source}-{self.name}-{self.measurement_type}-{self.sex}-lms.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
