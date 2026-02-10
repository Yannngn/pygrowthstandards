import logging
from dataclasses import dataclass, field
from typing import cast

import numpy as np
import pandas as pd

from pygrowthstandards.config.growth import (
    AGE_GROUP_CHOICES,
    DATA_SEX_CHOICES,
    TABLE_NAME_CHOICES,
    AgeGroupType,
    ChoiceValidator,
    DataSexType,
    DataSourceType,
    DataXTypeType,
    MeasurementAliasType,
    TableNameType,
    resolve_x_var_type,
)
from pygrowthstandards.utils.constants import WEEK, YEAR
from pygrowthstandards.utils.errors import InvalidChoicesError
from pygrowthstandards.utils.stats import numpy_calculate_value_for_z_score


# FIXME: Move lower
@dataclass
class KeyObject:
    "This object has the job to get the user input and convert it to the correct format expected by the data loading functions. It also has the job to validate the user input and raise errors if the input is invalid."

    name: str
    measurement_type: MeasurementAliasType
    sex: DataSexType
    x_var_type: DataXTypeType
    x: float | None = None
    age_group: AgeGroupType | None = None

    @staticmethod
    def _normalize_age_group(age_group: str) -> AgeGroupType:
        normalized = age_group.lower().replace(" ", "_")
        if normalized in AGE_GROUP_CHOICES:
            return cast(AgeGroupType, normalized)

        raise ValueError(f"Invalid age group: {age_group}. Must be one of: {sorted(AGE_GROUP_CHOICES)}")

    @staticmethod
    def _normalize_measurement(measurement: str) -> MeasurementAliasType:
        normalized = measurement.lower().replace("-", "_")
        resolved = ChoiceValidator.resolve_measurement_alias(normalized)
        if resolved is None:
            raise ValueError(f"Unknown measurement: {measurement}")

        return resolved

    @staticmethod
    def _normalize_sex(sex: str | None) -> DataSexType:
        if sex is None:
            return "U"

        normalized = sex.upper()
        if normalized in DATA_SEX_CHOICES:
            return cast(DataSexType, normalized)

        logging.warning(f"Unrecognized sex value {sex}, defaulting to 'U'.")

        return "U"

    @staticmethod
    def _resolve_x_and_type(age_days: int | None, gestational_age: int | None) -> tuple[DataXTypeType, float]:
        if age_days is not None:
            if gestational_age is not None and gestational_age < 28 * WEEK:
                post_menstrual_age = age_days + gestational_age
                if post_menstrual_age <= 64 * WEEK:
                    return "post_menstrual_age", post_menstrual_age
            return "age", float(age_days)

        if gestational_age is not None:
            return "gestational_age", float(gestational_age)

        raise ValueError("Either age_days or gestational_age must be provided.")

    @staticmethod
    def _normalize_x_var_type(x_var_type: str) -> DataXTypeType:
        return resolve_x_var_type(x_var_type)

    # TODO: Move to utils.config
    @staticmethod
    def _get_name(
        measurement: MeasurementAliasType,
        x_var_type: DataXTypeType,
        age_days: int | None,
        gestational_age: int | None,
    ) -> TableNameType:
        if x_var_type == "post_menstrual_age":
            return "postnatal_growth_preterm"

        if x_var_type == "gestational_age":
            if measurement in ["body_mass_index"]:
                raise ValueError(f"No reference for {measurement} at birth or fetal age.")
            if gestational_age is None:
                raise ValueError("gestational_age is required for gestational_age tables.")
            return "newborn" if gestational_age > 28 * WEEK else "very_preterm_newborn"

        if x_var_type == "stature":
            return "child_growth"

        if age_days is None:
            raise ValueError("age_days is required for age tables.")

        if measurement in ["head_circumference", "weight_stature_ratio"] and age_days > 5 * YEAR:
            raise ValueError(f"No reference for {measurement} after 5 years.")

        if measurement in ["weight"] and age_days > 10 * YEAR:
            raise ValueError(f"No reference for {measurement} after 10 years.")

        return "growth" if age_days > 5 * YEAR else "child_growth"

    @staticmethod
    def _normalize_name(name: str) -> TableNameType:
        normalized = name.lower().replace(" ", "_")
        if normalized in TABLE_NAME_CHOICES:
            return cast(TableNameType, normalized)

        raise ValueError(f"Invalid table name: {name}. Must be one of: {sorted(TABLE_NAME_CHOICES)}")

    @staticmethod
    def _normalize_x(x_value: float | None) -> float:
        if x_value is None:
            raise ValueError("x_value is required for the selected x_var_type.")
        return float(x_value)

    @classmethod
    def from_functional(
        cls,
        measurement: MeasurementAliasType,
        sex: DataSexType | None = None,
        age_days: int | None = None,
        gestational_age: int | None = None,
        x_var_type: str | None = None,
        x_value: float | None = None,
    ) -> "KeyObject":
        normalized_measurement = cls._normalize_measurement(measurement)
        if x_var_type is not None:
            resolved_x_var_type = cls._normalize_x_var_type(x_var_type)
            x_value = cls._normalize_x(x_value)
        else:
            resolved_x_var_type, x_value = cls._resolve_x_and_type(age_days, gestational_age)

        if resolved_x_var_type == "stature" and normalized_measurement != "weight":
            raise ValueError("x_var_type='stature' is only supported for weight-for-stature calculations.")

        return cls(
            cls._get_name(normalized_measurement, resolved_x_var_type, age_days, gestational_age),
            normalized_measurement,
            cls._normalize_sex(sex),
            resolved_x_var_type,
            x_value,
            None,
        )

    @classmethod
    def from_oop(
        cls,
        name: str,
        measurement_type: MeasurementAliasType,
        age_group: AgeGroupType,
        x_var_type: DataXTypeType,
        sex: DataSexType | None = None,
    ) -> "KeyObject":
        return cls(
            cls._normalize_name(name),
            cls._normalize_measurement(measurement_type),
            cls._normalize_sex(sex),
            cls._normalize_x_var_type(x_var_type),
            None,  # X
            cls._normalize_age_group(age_group),
        )


# TODO: Age Group == array of strs?
# TODO: make another layer of abstraction for the growth table and separate standards and child data
@dataclass
class GrowthTable:
    """
    Represents a growth table containing data points for growth standards.
    """

    source: DataSourceType
    name: TableNameType
    age_group: AgeGroupType | None  # helper column, not required
    measurement_type: MeasurementAliasType
    sex: DataSexType
    x_var_type: DataXTypeType
    x: np.ndarray
    L: np.ndarray
    M: np.ndarray
    S: np.ndarray
    is_derived: np.ndarray

    y: np.ndarray = field(init=False, repr=False)

    @staticmethod
    def filter_by_keys(data: pd.DataFrame, keys: KeyObject) -> pd.DataFrame:
        filtered = data.copy()
        filtered = filtered[(filtered["name"] == keys.name)]
        if keys.age_group is not None:
            filtered = filtered[(filtered["age_group"] == keys.age_group)]
        filtered = filtered[(filtered["x_var_type"] == keys.x_var_type)]
        filtered = filtered[(filtered["measurement_type"] == keys.measurement_type)]

        if keys.sex == "U":
            available = set(filtered["sex"].str.upper().unique())
            if "U" in available:
                filtered = filtered[(filtered["sex"].str.upper() == "U")]
            elif "F" in available:
                filtered = filtered[(filtered["sex"].str.upper() == "F")]
            elif "M" in available:
                filtered = filtered[(filtered["sex"].str.upper() == "M")]
        else:
            filtered = filtered[(filtered["sex"].str.upper() == keys.sex)]

        if filtered.empty:
            raise InvalidChoicesError(keys.measurement_type, keys.age_group)

        return filtered

    @classmethod
    def from_data(cls, data: pd.DataFrame, keys: KeyObject) -> "GrowthTable":
        """
        Loads a GrowthTable from a DataFrame, filtering by measurement_type, sex, and x_var_type.

        :param data: The DataFrame containing the growth data.
        :param keys: The KeyObject containing filtering keys.
        :return: An instance of GrowthTable.
        """
        # Normalize incoming reference-style DataFrame columns to canonical values
        data = _normalize_reference_data(data.copy())
        filtered = cls.filter_by_keys(data, keys)

        source = filtered["source"].unique()[0]
        name = filtered["name"].unique()[0]
        age_group = filtered["age_group"].unique()[0]
        x_var_type = filtered["x_var_type"].unique()[0]

        # FIXME: if x_var_type_unique > 1 causes problems
        return cls(
            source=source,
            name=name,
            age_group=age_group,
            measurement_type=keys.measurement_type,
            sex=keys.sex,
            x_var_type=x_var_type,
            x=filtered["x"].to_numpy(),
            L=filtered["l"].to_numpy(),
            M=filtered["m"].to_numpy(),
            S=filtered["s"].to_numpy(),
            is_derived=filtered["is_derived"].to_numpy(),
        )

    def convert_z_scores_to_values(self, z_scores: list[float] | None = None) -> pd.DataFrame:
        """
        Converts the GrowthTable to a DataFrame suitable for plotting.

        :return: A DataFrame with columns for x, L, M, S, and is_derived.
        """
        if not z_scores:
            z_scores = [-3, -2, 0, 2, 3]

        data = pd.DataFrame(
            {
                "x": self.x,
                "is_derived": self.is_derived,
                **{z: numpy_calculate_value_for_z_score(z, self.L, self.M, self.S) for z in z_scores},
            }
        )

        if hasattr(self, "y"):
            data["y"] = self.y

        return data

    def add_child_data(self, child_data: pd.DataFrame) -> None:
        """
        Adds child data to the GrowthTable.

        :param child_data: A DataFrame containing child data with columns 'x' and 'child'.
        """
        if not isinstance(child_data, pd.DataFrame) or not all(col in child_data.columns for col in ["x", "child"]):
            raise ValueError("child_data must be a DataFrame with 'x' and 'child' columns.")

        # Add new x values from child_data to self.x
        x = child_data["x"].to_numpy()
        y = child_data["child"].to_numpy()

        self.x = np.unique(np.sort(np.concatenate([self.x, x])))
        self.y = np.full_like(self.x, fill_value=None, dtype=object)

        x_indices = {val: idx for idx, val in enumerate(self.x)}
        for x_val, y_val in zip(x, y, strict=True):
            idx = x_indices.get(x_val)
            if idx is not None:
                self.y[idx] = y_val

    def cut_data(self, lower_limit: float, upper_limit: float) -> None:
        """
        Cuts the data in the GrowthTable to the specified limits.

        :param lower_limit: The lower limit for the x variable.
        :param upper_limit: The upper limit for the x variable.
        """
        mask = (self.x >= lower_limit) & (self.x <= upper_limit)
        self.x = self.x[mask]
        self.L = self.L[mask]
        self.M = self.M[mask]
        self.S = self.S[mask]
        self.is_derived = self.is_derived[mask]


def load_reference():
    """
    Loads the growth reference data from the packaged parquet file and returns a DataFrame.

    :return: A DataFrame containing the growth reference data.
    """
    from pygrowthstandards.data import data_exists, get_data_path

    data_path = get_data_path()

    if not data_exists():
        raise FileNotFoundError(f"Growth reference data file not found at {data_path}. Please ensure the package was installed correctly.")

    data = pd.read_parquet(data_path)
    return _normalize_reference_data(data)


def _normalize_reference_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize reference data columns to canonical config values."""

    def resolve_measurement(value: str) -> str:
        if value is None:
            return value
        resolved = ChoiceValidator.resolve_measurement_alias(str(value))
        return resolved if resolved is not None else value

    data = data.copy()
    data["x_var_type"] = data["x_var_type"].apply(resolve_x_var_type)
    data["measurement_type"] = data["measurement_type"].apply(resolve_measurement)

    return data
