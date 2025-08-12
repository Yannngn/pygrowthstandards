"""Utilities for selecting and retrieving LMS growth standard data.

This module provides functions to resolve measurement keys, load GrowthTable objects,
and extract or interpolate LMS (Lambda-Mu-Sigma) parameters from reference data.

Functions:
    get_keys: Determine reference taxonomy and lookup keys.
    get_table: Instantiate GrowthTable using lookup keys.
    get_lms: Retrieve or interpolate LMS parameters for a given x value.

Example:
    >>> from src.functional.data import get_keys, get_table, get_lms
    >>> from ..data.load import load_reference
    >>> data = load_reference()
    >>> keys = get_keys("stature", sex="M", age_days=365)
    >>> table = get_table(data, keys)
    >>> l, m, s = get_lms(table, 365)
"""

import os

import pandas as pd

from ..data.load import GrowthTable
from ..utils import stats
from ..utils.choices import (
    MEASUREMENT_ALIASES,
    MeasurementTypeLiteral,
    SexLiteral,
    TableNameLiteral,
    XVarNameLiteral,
)
from ..utils.constants import WEEK, YEAR

DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "data")


def get_keys(
    measurement: MeasurementTypeLiteral,
    sex: SexLiteral = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> tuple[TableNameLiteral, MeasurementTypeLiteral, SexLiteral, XVarNameLiteral]:
    """Resolve measurement and demographic keys for reference lookup.

    Args:
        measurement (str): Measurement identifier or alias (e.g., 'stature', 'wfa').
        sex (Literal['M', 'F', 'U']): Biological sex code.
        age_days (int | None): Age in days, if applicable.
        gestational_age (int | None): Gestational age in days, for newborns.

    Returns:
        tuple[str, str, str, str]: Tuple of (table name, measurement type, sex, x variable type).

    Raises:
        ValueError: If neither age_days nor gestational_age is provided or measurement is unknown.
    """
    if age_days is None and gestational_age is None:
        raise ValueError("Either age_days or gestational_age must be provided.")

    def normalized_measurement() -> MeasurementTypeLiteral:
        for key, aliases in MEASUREMENT_ALIASES.items():
            normalized = measurement.lower().replace("-", "_")
            if normalized in aliases | {key}:
                return key
        raise ValueError(f"Unknown measurement: {measurement}")

    measurement_type = normalized_measurement()
    sex = sex.upper() if sex.upper() in ["M", "F"] else "F"  # type: ignore

    if age_days is not None:
        x_var_type = "age"
        name = _keys_handle_age_days(age_days, measurement_type)

        if (gestational_age is not None) and (gestational_age < 28) and (age_days < 64 * WEEK):
            return "very_preterm_growth", measurement_type, sex, x_var_type

        return name, measurement_type, sex, x_var_type

    if gestational_age is None:
        raise ValueError("Either age_days or gestational_age must be provided.")

    x_var_type = "gestational_age"
    name = _keys_handle_gestational_age(gestational_age, measurement_type)

    return name, measurement_type, sex, x_var_type


def _keys_handle_age_days(age_days: int, measurement_type: MeasurementTypeLiteral):
    if measurement_type in ["head_circumference", "weight_stature"] and age_days > 5 * YEAR:
        raise ValueError(f"No reference for {measurement_type} after 5 years.")

    if measurement_type in ["weight"] and age_days > 10 * YEAR:
        raise ValueError(f"No reference for {measurement_type} after 10 years.")

    return "growth" if age_days > 5 * YEAR else "child_growth"


def _keys_handle_gestational_age(gestational_age: int, measurement_type: MeasurementTypeLiteral):
    if measurement_type in ["weight_stature"] and gestational_age > 28:
        raise ValueError(f"No reference for {measurement_type} at birth or fetal age.")

    if measurement_type in ["body_mass_index"] and gestational_age < 28:
        raise ValueError(f"No reference for {measurement_type} at birth or fetal age.")

    return "newborn" if gestational_age > 28 else "very_preterm_newborn"


def get_table(data: pd.DataFrame, keys: tuple[TableNameLiteral, MeasurementTypeLiteral, SexLiteral, XVarNameLiteral]) -> GrowthTable:
    """Load a GrowthTable based on reference DataFrame and lookup keys.

    Args:
        data (pandas.DataFrame): Reference LMS data.
        keys (tuple[str, str, str, str]): Lookup keys from get_keys.

    Returns:
        GrowthTable: Populated growth table instance.
    """
    name, measurement, sex, x_var_type = keys
    return GrowthTable.from_data(data, name, None, measurement, sex, x_var_type)


def get_lms(table: GrowthTable, x: float) -> tuple[float, float, float]:
    """Retrieve or interpolate LMS parameters for a specified x value.

    Args:
        table (GrowthTable): The source growth table.
        x (float): Independent variable (e.g., age in days).

    Returns:
        tuple[float, float, float]: The (L, M, S) parameters.
    """
    if x not in table.x:
        return stats.interpolate_lms(x, table.x, table.L, table.M, table.S)

    index = list(table.x).index(x)

    return table.L[index], table.M[index], table.S[index]
