"""Compute percentiles using the functional API."""

from typing import overload

import pandas as pd

from pygrowthstandards.functional.growth.load import DATA, KeyObject, get_lms, get_table
from pygrowthstandards.typing.growth import DataSexType, MeasurementAliasType
from pygrowthstandards.utils.date import DateInputType, handle_date_input
from pygrowthstandards.utils.stats import calculate_z_score, normal_cdf


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    age_days: int,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    birth_date: DateInputType,
    measurement_date: DateInputType,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    birth_date: DateInputType,
    measurement_date: DateInputType,
    gestational_age: int,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    age_days: int,
    gestational_age: int,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    gestational_age: int,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    gestational_age_weeks: int,
    gestational_age_days: int = 0,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    birth_date: DateInputType,
    measurement_date: DateInputType,
    gestational_age_weeks: int | None = None,
    gestational_age_days: int = 0,
) -> float: ...


@overload
def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    *,
    x_var_type: str,
    x_value: float,
) -> float: ...


def percentile(
    measurement: MeasurementAliasType,
    value: float,
    sex: DataSexType | None = None,
    age_days: int | None = None,
    gestational_age: int | None = None,
    gestational_age_weeks: int | None = None,
    gestational_age_days: int = 0,
    birth_date: DateInputType | None = None,
    measurement_date: DateInputType | None = None,
    x_var_type: str | None = None,
    x_value: float | None = None,
) -> float:
    """Calculate a percentile for a measurement.

    Args:
        measurement: Measurement alias or canonical name.
        value: Observed measurement value.
        sex: Sex used for reference selection.
        age_days: Chronological age in days.
        gestational_age: Gestational age in days.
        gestational_age_weeks: Gestational age in weeks.
        gestational_age_days: Additional gestational days when weeks provided.
        birth_date: Date of birth to derive age from dates.
        measurement_date: Measurement date to derive age.
        x_var_type: Explicit x axis type when using x_value.
        x_value: Explicit x axis value.

    Returns:
        The percentile in [0, 1] from the standard normal CDF.

    Raises:
        ValueError: If required inputs are missing or inconsistent.
        RuntimeError: If reference data is unavailable.
    """
    if age_days is None and birth_date is not None and measurement_date is not None:
        birth_dt = handle_date_input(birth_date)
        measurement_dt = handle_date_input(measurement_date)
        age_days = (measurement_dt - birth_dt).days
        if age_days < 0:
            raise ValueError("measurement_date cannot be before birth_date")

    ga_days = gestational_age
    # Only compute gestational age days from weeks/day pair when weeks provided
    if ga_days is None and gestational_age_weeks is not None:
        ga_days = gestational_age_weeks * 7 + gestational_age_days

    keys = KeyObject.from_functional(
        measurement,
        sex,
        age_days,
        ga_days,
        x_var_type=x_var_type,
        x_value=x_value,
    )

    if keys.x is None:
        raise ValueError("X value must be provided to calculate percentile.")
    if not isinstance(DATA, pd.DataFrame):
        raise RuntimeError("Growth reference data is not available. Please ensure the data file is present.")

    data = get_table(DATA, keys=keys)
    lms = get_lms(data, keys.x)  # from functional will always return x.

    return normal_cdf(calculate_z_score(value, *lms))


#
