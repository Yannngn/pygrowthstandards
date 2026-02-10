"""Functional data access helpers for reference tables."""

import logging
from typing import overload

import pandas as pd

from pygrowthstandards.data.load import GrowthTable, KeyObject, load_reference
from pygrowthstandards.utils import stats
from pygrowthstandards.config.growth import DataSexType, MeasurementAliasType

try:
    DATA: pd.DataFrame | None = load_reference()
except FileNotFoundError:
    msg = "Growth reference data file not found. Please ensure the data file is available."
    logging.error(msg)
    DATA = None


# Easier usage if the user imports from functional.data directly with key object
@overload
def get_table(data: pd.DataFrame, *, keys: KeyObject) -> GrowthTable: ...


# Easier usage if the user imports from functional.data directly with arguments
@overload
def get_table(
    data: pd.DataFrame,
    *,
    measurement: MeasurementAliasType,
    sex: DataSexType | None = None,
    age_days: int | None = None,
    gestational_age: int | None = None,
    x_var_type: str | None = None,
    x_value: float | None = None,
) -> GrowthTable: ...


def get_table(
    data: pd.DataFrame,
    *,
    keys: KeyObject | None = None,
    measurement: MeasurementAliasType | None = None,
    sex: DataSexType | None = None,
    age_days: int | None = None,
    gestational_age: int | None = None,
    x_var_type: str | None = None,
    x_value: float | None = None,
) -> GrowthTable:
    """Return a GrowthTable filtered to the requested measurement context.

    Args:
        data: Reference data DataFrame.
        keys: Pre-built lookup keys.
        measurement: Measurement alias.
        sex: Sex identifier.
        age_days: Chronological age in days.
        gestational_age: Gestational age in days.
        x_var_type: Explicit axis type when providing x_value.
        x_value: Explicit axis value.

    Returns:
        GrowthTable filtered to the requested context.

    Raises:
        TypeError: If neither keys nor measurement are provided.
    """
    # If keys provided, use them directly.
    if keys is not None:
        return GrowthTable.from_data(data, keys)

    # Otherwise require a measurement to build keys.
    if measurement is None:
        raise TypeError("Either 'keys' or 'measurement' must be provided to get_table")

    keys_obj = KeyObject.from_functional(
        measurement,
        sex,
        age_days,
        gestational_age,
        x_var_type=x_var_type,
        x_value=x_value,
    )
    return GrowthTable.from_data(data, keys_obj)


def get_lms(table: GrowthTable, x: float) -> tuple[float, float, float]:
    """Return LMS parameters at a given x, interpolating if needed.

    Args:
        table: GrowthTable instance.
        x: Axis value to lookup.

    Returns:
        Tuple of (L, M, S) values.

    Raises:
        ValueError: If interpolation is attempted out of range.
    """
    if x not in table.x:
        return stats.interpolate_lms(x, table.x, table.L, table.M, table.S)

    index = list(table.x).index(x)

    return table.L[index], table.M[index], table.S[index]
