import logging
from typing import overload

import pandas as pd

from pygrowthstandards.data.load import GrowthTable, KeyObject, load_reference
from pygrowthstandards.utils import stats
from pygrowthstandards.utils.config import DataSexType, MeasurementAliasType

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
