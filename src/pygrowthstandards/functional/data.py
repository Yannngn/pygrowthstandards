import logging
import os

import pandas as pd

from ..data.load import GrowthTable, load_reference
from ..utils import stats
from ..utils.config import (
    AgeGroupType,
    ChoiceValidator,
    DataSexType,
    DataXTypeType,
    MeasurementTypeType,
    TableNameType,
    resolve_measurement,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "data")


try:
    DATA = load_reference()
except FileNotFoundError:
    logging.warning(
        "Growth reference data file not found. Please ensure the data file is available."
    )
    DATA = None


def get_keys(
    measurement: str,
    sex: DataSexType = "U",
    age_days: int | None = None,
    gestational_age_days: int | None = None,
) -> tuple[
    TableNameType, AgeGroupType, MeasurementTypeType, DataSexType, DataXTypeType
]:
    if age_days is None and gestational_age_days is None:
        raise ValueError("Either age_days or gestational_age must be provided.")

    measurement_type = ChoiceValidator.resolve_measurement_alias(measurement)
    age_group = ChoiceValidator.get_age_group_from_ages(age_days, gestational_age_days)
    assert age_group is not None, "Could not determine age group from provided ages."
    name = ChoiceValidator.get_table_name_from_age_group(age_group)

    measurement_type = resolve_measurement(measurement)

    sex = sex.lower() if sex in ["M", "F"] else "f"  # type: ignore

    x_var_type = ChoiceValidator.get_age_type_from_age_group(age_group) or ""

    if name in ["growth"] and measurement_type in [
        "head_circumference",
        "weight_stature",
    ]:
        raise ValueError(f"No reference for {measurement_type} after 5 years.")

    if name in [
        "newborn",
        "very_preterm_newborn",
        "very_preterm_growth",
    ] and measurement_type in ["body_mass_index"]:
        raise ValueError(f"No reference for {measurement_type} at birth or fetal age.")

    if name in ["newborn"] and measurement_type in ["weight_stature"]:
        raise ValueError(f"No reference for {measurement_type} at birth.")

    if age_group in ["10-19"] and measurement_type in ["weight"]:
        raise ValueError(f"No reference for {measurement_type} after 10 years.")

    return name, age_group, measurement_type, sex, x_var_type  # type: ignore[reportReturnType]


def get_table(data: pd.DataFrame, keys: tuple) -> GrowthTable:
    # data = load_reference()
    return GrowthTable.from_data(data, *keys)


def get_lms(table: GrowthTable, x: float) -> tuple[float, float, float]:
    """
    Get the L, M, S values for a given x from the GrowthTable.

    :param table: The GrowthTable instance.
    :param x: The x value (e.g., age in days).
    :return: A tuple of (L, M, S).
    """
    if x not in table.x:
        return stats.interpolate_lms(x, table.x, table.L, table.M, table.S)

    index = list(table.x).index(x)

    return table.L[index], table.M[index], table.S[index]
