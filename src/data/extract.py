import glob
import os
import sys
import tempfile
from dataclasses import dataclass

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from src.utils.constants import MONTH, WEEK
from src.utils.stats import estimate_lms_from_sd


@dataclass
class DataPoint:
    x: float
    L: float
    M: float
    S: float
    is_derived: bool = False

    def __post_init__(self):
        if not all(isinstance(value, (int, float)) for value in (self.x, self.L, self.M, self.S)):
            raise ValueError("All attributes must be numeric values.")

    def to_dict(self) -> dict:
        """
        Converts the DataPoint instance to a dictionary.

        Returns:
            dict: A dictionary representation of the DataPoint.
        """
        return {"x": self.x, "l": self.L, "m": self.M, "s": self.S, "is_derived": self.is_derived}

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
                x=float(data["x"]),
                L=float(data["l"]),
                M=float(data["m"]),
                S=float(data["s"]),
            )

        L, M, S = DataPoint._create_lms_data(data)

        return cls(data["x"], L, M, S, True)

    @staticmethod
    def _create_lms_data(data: dict) -> tuple[float, float, float]:
        required_sd = ["sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3"]
        if not all(k in data for k in required_sd):
            raise ValueError("Required SD columns (sd3neg to sd3) are missing.")

        zscores = np.array([-3, -2, -1, 0, 1, 2, 3], dtype=float)
        values = np.array([data[sd] for sd in required_sd], dtype=float)

        return estimate_lms_from_sd(zscores, values)


@dataclass
class RawTable:
    source: str
    name: str
    measurement_type: str
    sex: str
    x_var_type: str
    x_var_unit: str
    points: list[DataPoint]

    def __post_init__(self):
        if not all(isinstance(value, str) for value in (self.source, self.name, self.measurement_type, self.x_var_type)):
            raise ValueError("Source, name, measurement_type, and x_var_type must be strings.")
        if not isinstance(self.points, list) or not all(isinstance(point, DataPoint) for point in self.points):
            raise ValueError("Points must be a list of DataPoint instances.")

    def to_dict(self) -> dict:
        """
        Converts the RawTable instance to a dictionary.

        Returns:
            dict: A dictionary representation of the RawTable.
        """
        return {
            "source": self.source,
            "name": self.name,
            "measurement_type": self.measurement_type,
            "sex": self.sex,
            "x_var_type": self.x_var_type,
            "x_var_unit": self.x_var_unit,
            "points": [point.to_dict() for point in self.points],
        }

    @classmethod
    def from_csv(cls, csv_path: str) -> "RawTable":
        """
        Create a RawTable instance from a CSV file.

        Args:
            csv_path (str): Path to the CSV file.

        Returns:
            Dataset: An instance of Dataset.
        """
        df = pd.read_csv(csv_path, dtype=str, encoding="utf-8")

        source, table, sex, measurement_type, x_var_type = cls._process_path(csv_path)

        df.columns = [col.lower() for col in df.columns]
        x_column = df.columns[0]

        # Weight for Length/Height datasets
        if x_column in ["length", "height"]:
            df["x"] = df[x_column]

            return cls(
                source=source,
                name=table,
                measurement_type=measurement_type,
                sex=sex,
                x_var_type="stature",
                x_var_unit="cm",
                points=cls._get_points(df),
            )

        # Velocity datasets
        if x_column in ["interval"]:
            # Normalize dash types and strip whitespace
            df[x_column] = df[x_column].str.replace("\u2013", "-").str.strip()

            interval_min_list, interval_max_list = [], []
            for value in df[x_column]:
                age_parts: list[str] = str(value).split("-")
                min_part, max_part = age_parts[0].strip(), age_parts[1].strip()

                interval_min_list.append(cls._parse_interval(min_part))
                interval_max_list.append(cls._parse_interval(max_part))

            df["x"] = interval_min_list

            return cls(
                source=source,
                name=table,
                measurement_type=measurement_type,
                sex=sex,
                x_var_type=x_var_type,
                x_var_unit="days",
                points=cls._get_points(df),
            )

        df["x"] = df[x_column].astype(float).astype(int)

        measurement_type = measurement_type.replace("weight_stature", "weight_stature_ratio")

        return cls(
            source=source,
            name=table,
            measurement_type=measurement_type,
            sex=sex,
            x_var_type=x_var_type,
            x_var_unit=x_column,
            points=cls._get_points(df),
        )

    @classmethod
    def from_xlsx(cls, xlsx_path: str) -> "RawTable":
        """
        Create a RawTable instance from an XLSX file.

        Args:
            xlsx_path (str): Path to the XLSX file.

        Returns:
            RawTable: An instance of RawTable.
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

    @staticmethod
    def _get_points(data: pd.DataFrame):
        data_points = []

        for _, row in data.iterrows():
            data_point = DataPoint.from_dict(row.to_dict())
            data_points.append(data_point)

        return data_points

    @staticmethod
    def _process_path(filepath: str) -> tuple[str, str, str, str, str]:
        filename = os.path.splitext(os.path.basename(filepath))[0]

        parts = filename.split("-")
        if len(parts) > 4:
            _ = parts.pop()

        sex = parts.pop().upper()

        if sex not in ["M", "F", "U"]:  # 1mon and 2mon from velocity datasets
            sex = parts.pop().upper()

        measurement_type = parts.pop()
        table = parts.pop().replace("birth", "newborn")
        source = parts.pop()
        x_var_type = "gestational_age" if "birth" in filename else "age"

        if measurement_type in ["weight_length", "weight_height"]:
            measurement_type = "weight"
            x_var_type = "stature"

        return source, table, sex, measurement_type, x_var_type

    @staticmethod
    def _parse_interval(part: str) -> int:
        if part.endswith("wks"):
            return int(round(float(part.replace("wks", "").strip()) * WEEK))

        if part.endswith("mo"):
            return int(round(float(part.replace("mo", "").strip()) * MONTH))

        return int(round(float(part) * MONTH))


def main():
    for f in glob.glob("data/raw/**/*.xlsx"):
        dataset = RawTable.from_xlsx(f)
        print(f"Processed {dataset.name} for {dataset.measurement_type} ({dataset.sex}) with {len(dataset.points)} points.")


if __name__ == "__main__":
    main()
