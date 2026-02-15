"""Extract growth reference tables from raw CSV and XLSX sources."""

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pygrowthstandards.config.growth import (
    DATA_SEX_CHOICES,
    ChoiceValidator,
    DataSexType,
    DataSourceType,
    MeasurementAliasType,
    TableNameType,
)
from pygrowthstandards.utils.constants import MONTH, WEEK
from pygrowthstandards.utils.stats import estimate_lms_from_sd


@dataclass
class DataPoint:
    """Single LMS data point for a given x value.

    Attributes:
        x: X-axis value (age in days or stature).
        L: Box-Cox power.
        M: Median value.
        S: Coefficient of variation.
        is_derived: True when LMS values were derived from SDs.
    """

    x: int | float
    L: float
    M: float
    S: float
    is_derived: bool = False

    def __post_init__(self):
        """Validate numeric inputs after initialization.

        Raises:
            ValueError: If any LMS values are not numeric.
        """
        if not all(isinstance(value, int | float) for value in (self.x, self.L, self.M, self.S)):
            raise ValueError("All attributes must be numeric values.")

    def to_dict(self) -> dict[str, float | bool]:
        """Convert the data point to a serializable dictionary.

        Returns:
            A dictionary with LMS fields and flags.
        """
        return {
            "x": self.x,
            "l": self.L,
            "m": self.M,
            "s": self.S,
            "is_derived": self.is_derived,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DataPoint":
        """Create a data point from a dict with LMS or SD fields.

        Args:
            data: Mapping containing LMS or SD columns.

        Returns:
            A populated DataPoint instance.
        """
        if "l" in data and "m" in data and "s" in data:
            return cls(
                x=data["x"],
                L=float(data["l"]),
                M=float(data["m"]),
                S=float(data["s"]),
            )

        L, M, S = DataPoint._create_lms_data(data)

        return cls(data["x"], L, M, S, True)

    @staticmethod
    def _create_lms_data(data: dict[str, float]) -> tuple[float, float, float]:
        """Derive LMS parameters from SD columns.

        Args:
            data: Mapping of SD columns.

        Returns:
            Tuple of (L, M, S).

        Raises:
            ValueError: If required SD columns are missing.
        """
        required_sd = ["sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3"]

        if not all(k in data for k in required_sd):
            raise ValueError("Required SD columns (sd3neg to sd3) are missing.")

        zscores = np.array([-3, -2, -1, 0, 1, 2, 3], dtype=float)
        values = np.array([data[sd] for sd in required_sd], dtype=float)

        return estimate_lms_from_sd(zscores, values)


# TODO: Business decision: use lenght or height or use stature as the standard term for both? For now, we will use stature as the standard term and map length and height to stature in the alias system.
@dataclass
class RawTable:
    """Container for raw reference data parsed from a single file.

    Attributes:
        source: Data source identifier.
        name: Table name identifier.
        sex: Sex identifier for the dataset.
        measurement_type: Measurement alias.
        x_var_type: Axis type string.
        x_var_unit: Axis unit string.
        points: LMS datapoints.
    """

    source: DataSourceType  # who, intergrowth, cdc, etc.
    name: TableNameType  # child_growth, growth, newborn, etc.
    sex: DataSexType  # M, F, U
    measurement_type: MeasurementAliasType  # stature, weight etc
    x_var_type: str
    x_var_unit: str
    points: list[DataPoint]

    def __post_init__(self):
        """Validate basic types for required attributes.

        Raises:
            ValueError: If required fields are invalid.
        """
        if not all(
            isinstance(value, str)
            for value in {
                self.source,
                self.name,
                self.measurement_type,
                self.x_var_type,
            }
        ):
            raise ValueError("Source, name, measurement_type, and x_var_type must be strings.")

        if not isinstance(self.points, list) or not all(isinstance(point, DataPoint) for point in self.points):
            raise ValueError("Points must be a list of DataPoint instances.")

        # Validate using the new config system
        if not ChoiceValidator.validate_choice(self.sex, DATA_SEX_CHOICES):
            raise ValueError(f"Invalid sex: {self.sex}")

    def to_dict(self) -> dict[str, str | list]:
        """Serialize the raw table for downstream transforms.

        Returns:
            A dictionary representation of the raw table.
        """
        return {
            "source": self.source,
            "name": self.name,
            "sex": self.sex,
            "measurement_type": self.measurement_type,
            "x_var_type": self.x_var_type,
            "x_var_unit": self.x_var_unit,
            "points": [point.to_dict() for point in self.points],
        }

    @classmethod
    def from_csv(cls, csv_path: str | Path) -> "RawTable":
        """Create a RawTable from a CSV file on disk.

        Args:
            csv_path: Path to the CSV file.

        Returns:
            Parsed RawTable instance.
        """
        df = pd.read_csv(csv_path, dtype=str, encoding="utf-8")
        filename = Path(csv_path).stem

        raw_kwargs = cls._process_path(csv_path)

        df.columns = [col.lower() for col in df.columns]
        x_column = df.columns[0]
        clean_dict: dict[str, Any] = {}

        # Weight for Length/Height/Stature datasets
        if x_column in {"length", "height", "stature"}:
            df["x"] = df[x_column].astype(float)

            clean_dict = cls._handle_weight_for_length(**raw_kwargs)

        # Velocity for age datasets
        elif x_column in ["interval"]:
            # Normalize dash types and strip whitespace
            df[x_column] = df[x_column].str.replace("\u2013", "-").str.strip()

            interval_min_list, interval_max_list = [], []
            for value in df[x_column]:
                age_parts: list[str] = str(value).split("-")
                if len(age_parts) != 2:
                    raise ValueError(f"Invalid interval format: {value}. Expected 'min-max' format.")
                min_part, max_part = age_parts[0].strip(), age_parts[1].strip()

                interval_min_list.append(cls._parse_interval(min_part))
                interval_max_list.append(cls._parse_interval(max_part))

            df["x"] = interval_min_list

            # Prefer 1-month windows for 0-12 months and 2-month windows afterward.
            if "1mon" in filename:
                df = df[df["x"].astype(float) < 12 * MONTH]
            elif "2mon" in filename:
                df = df[df["x"].astype(float) >= 12 * MONTH]
            clean_dict = cls._handle_velocity(**raw_kwargs)

        # Measurement for age datasets
        else:
            df["x"] = df[x_column].astype(float).astype(int)
            clean_dict = cls._handle_measurement_for_age(x_column, **raw_kwargs)

        return cls(**clean_dict, points=cls._get_points(df))

    @classmethod
    def from_xlsx(cls, xlsx_path: str | Path) -> "RawTable":
        """Create a RawTable from an XLSX file by converting to CSV.

        Args:
            xlsx_path: Path to the XLSX file.

        Returns:
            Parsed RawTable instance.
        """
        df = pd.read_excel(xlsx_path, sheet_name=None)

        # Assume we want the first sheet only
        first_sheet_name = list(df.keys())[0]
        first_sheet_data = df[first_sheet_name]

        import os

        # Use the Excel file name (without extension) for the temp CSV file
        base_name = Path(xlsx_path).stem
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", prefix=base_name + "-", delete=False) as tmpfile:
            first_sheet_data.to_csv(tmpfile.name, index=False)
            tmp_csv_path = tmpfile.name

        try:
            # Create Dataset from the temporary CSV
            dataset = cls.from_csv(tmp_csv_path)
            return dataset
        finally:
            os.remove(tmp_csv_path)

    @staticmethod
    def _process_path(filepath: str | Path) -> dict[str, str]:
        """Extract metadata from a raw filename.

        Args:
            filepath: Path to the raw file.

        Returns:
            Dictionary with parsed metadata.
        """
        raw_kwargs = {}
        filename = Path(filepath).stem

        def preprocess() -> list[str]:
            parts = filename.split("-")

            if len(parts) < 2:
                raise ValueError(f"Filename does not contain expected parts separated by '-': {filename}")

            if len(parts) > 4:
                extras = parts[4:]
                parts = parts[:4]
                logging.warning(f"Filename has more than 4 parts, ignoring extra parts: {extras} in {filename}")

            return parts

        parts = preprocess()

        def handle_sex() -> str:
            # Handling sex with validation
            sex = parts.pop().upper()
            if not parts:
                raise ValueError(f"Filename missing sex component: {filename}")

            if not ChoiceValidator.validate_choice(sex, DATA_SEX_CHOICES):  # 1mon and 2mon from velocity datasets
                if not parts:
                    raise ValueError(f"Invalid sex found in filename and no fallback available: {sex}")
                sex = parts.pop().upper()

            if not ChoiceValidator.validate_choice(sex, DATA_SEX_CHOICES):
                raise ValueError(f"Invalid sex found in filename: {sex}")

            return sex

        raw_kwargs["sex"] = handle_sex()

        def handle_measurement() -> tuple[str, str]:
            # Handling Measurement with alias resolution
            x_var_type = ""

            measurement_type = parts.pop()
            if measurement_type in {"weight_length", "weight_height"}:
                x_var_type = measurement_type.replace("weight_", "")
                measurement_type = "weight"

            # Try to resolve measurement alias
            resolved_measurement = ChoiceValidator.resolve_measurement_alias(measurement_type)
            if resolved_measurement:
                measurement_type = resolved_measurement

            return measurement_type, x_var_type

        # Handling Measurement with alias resolution
        raw_kwargs["measurement_type"], x_var_type = handle_measurement()

        # Handling table_name
        if not parts:
            raise ValueError(f"Filename missing expected table_name component: {filename}")
        table = parts.pop()
        raw_kwargs["table_name"] = table

        if not parts:
            raise ValueError(f"Filename missing expected source component: {filename}")
        source = parts.pop()
        raw_kwargs["source"] = source

        def handle_x_var_type(x_var_type: str) -> str:
            if not x_var_type:
                if "newborn" in filename:
                    x_var_type = "gestational_age"
                elif "preterm" in filename:
                    x_var_type = "post_menstrual_age"
                else:
                    x_var_type = "age"

            return x_var_type

        raw_kwargs["x_var_type"] = handle_x_var_type(x_var_type)

        return raw_kwargs

    @staticmethod
    def _handle_weight_for_length(
        source: str,
        table_name: str,
        sex: str,
        measurement_type: str,
        x_var_type: str,
        **kwargs,
    ):
        """Build kwargs for weight-for-length/height tables.

        Args:
            source: Data source identifier.
            table_name: Table name identifier.
            sex: Sex identifier.
            measurement_type: Measurement alias.
            x_var_type: Axis type.
            **kwargs: Ignored extra fields.

        Returns:
            Dictionary of normalized kwargs.
        """
        # Resolve measurement alias if needed
        resolved_measurement = ChoiceValidator.resolve_measurement_alias(measurement_type)
        if resolved_measurement:
            measurement_type = resolved_measurement

        return {
            "source": source,
            "name": table_name,
            "sex": sex,
            "measurement_type": measurement_type,
            "x_var_type": x_var_type,
            "x_var_unit": "cm",
        }

    @staticmethod
    def _handle_velocity(
        source: str,
        table_name: str,
        sex: str,
        measurement_type: str,
        x_var_type: str,
        **kwargs,
    ):
        """Build kwargs for velocity tables.

        Args:
            source: Data source identifier.
            table_name: Table name identifier.
            sex: Sex identifier.
            measurement_type: Measurement alias.
            x_var_type: Axis type.
            **kwargs: Ignored extra fields.

        Returns:
            Dictionary of normalized kwargs.
        """
        # Handle velocity measurement type resolution
        if measurement_type in {"length", "height", "stature"}:
            measurement_type = "stature_velocity"
        elif measurement_type == "weight":
            measurement_type = "weight_velocity"
        elif measurement_type == "head_circumference":
            measurement_type = "head_circumference_velocity"

        return {
            "source": source,
            "name": table_name,
            "sex": sex,
            "measurement_type": measurement_type,
            "x_var_type": x_var_type,
            "x_var_unit": "days",
        }

    @staticmethod
    def _handle_measurement_for_age(
        x_column: str,
        source: str,
        table_name: str,
        sex: str,
        measurement_type: str,
        x_var_type: str,
        **kwargs,
    ):
        """Build kwargs for standard measurement-by-age tables.

        Args:
            x_column: Axis column name.
            source: Data source identifier.
            table_name: Table name identifier.
            sex: Sex identifier.
            measurement_type: Measurement alias.
            x_var_type: Axis type.
            **kwargs: Ignored extra fields.

        Returns:
            Dictionary of normalized kwargs.
        """
        if measurement_type in {"weight_stature", "weight_stature_ratio"}:
            measurement_type = "weight_stature_ratio"

        # Try to resolve measurement alias
        resolved_measurement = ChoiceValidator.resolve_measurement_alias(measurement_type)
        if resolved_measurement:
            measurement_type = resolved_measurement

        return {
            "source": source,
            "name": table_name,
            "sex": sex,
            "measurement_type": measurement_type,
            "x_var_type": x_var_type,
            "x_var_unit": x_column,
        }

    @staticmethod
    def _get_points(data: pd.DataFrame):
        """Convert a DataFrame into a list of DataPoint objects.

        Args:
            data: Raw DataFrame with LMS/SD columns.

        Returns:
            List of DataPoint instances.
        """
        data_points = []

        for _, row in data.iterrows():
            data_point = DataPoint.from_dict(row.to_dict())
            data_points.append(data_point)

        return data_points

    @staticmethod
    def _parse_interval(part: str) -> int:
        """Parse interval text into days.

        Args:
            part: Interval string value.

        Returns:
            Interval value in days.
        """
        if part.endswith("wks"):
            return int(round(float(part.replace("wks", "").strip()) * WEEK))

        if part.endswith("mo"):
            return int(round(float(part.replace("mo", "").strip()) * MONTH))

        return int(round(float(part) * MONTH))
