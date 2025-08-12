"""Functional API for growth standards calculations.

This module provides functions to compute z-scores and percentiles using WHO
and INTERGROWTH-21st reference data.

Functions:
    zscore: Calculate a z-score for a measurement.
    percentile: Compute percentile from a measurement value.

Example:
    >>> from src.functional.calculator import zscore, percentile
    >>> z = zscore('stature', 50.0, 'M', age_days=365)
    >>> p = percentile('stature', 50.0, 'M', age_days=365)
"""

from ..data.load import load_reference
from ..utils.choices import MeasurementTypeLiteral, SexLiteral
from ..utils.stats import calculate_z_score, normal_cdf
from .data import get_keys, get_lms, get_table

DATA = load_reference()


def zscore(
    measurement: MeasurementTypeLiteral,
    value: float,
    sex: SexLiteral = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:
    """
    Calculate the z-score for a given measurement using reference LMS values.

    Args:
        measurement: The type of measurement (e.g., stature, weight).
        value: The observed measurement value.
        sex: Biological sex, one of 'M', 'F', or 'U' (unknown).
        age_days: Age in days. Required unless gestational_age is provided.
        gestational_age: Gestational age in days. Required for newborn standards.

    Returns:
        The z-score as a float.

    Raises:
        AssertionError: If neither age_days nor gestational_age is provided.
    """
    keys = get_keys(measurement, sex, age_days, gestational_age=gestational_age)

    x = age_days if keys[-1] == "age" else gestational_age

    if x is None:
        raise ValueError("Either age_days or gestational_age must be provided.")

    data = get_table(DATA, keys)
    lms = get_lms(data, x)

    return calculate_z_score(value, *lms)


def percentile(
    measurement: MeasurementTypeLiteral,
    value: float,
    sex: SexLiteral = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:
    """
    Calculate the percentile corresponding to a measurement value.

    Uses the z-score from the reference distribution and returns the cumulative
    probability (percentile).

    Args:
        measurement: The type of measurement (e.g., stature, weight).
        value: The observed measurement value.
        sex: Biological sex, one of 'M', 'F', or 'U' (unknown).
        age_days: Age in days. Required unless gestational_age is provided.
        gestational_age: Gestational age in days. Required for newborn standards.

    Returns:
        The percentile (0-1) as a float.
    """
    z = zscore(measurement, value, sex, age_days, gestational_age)

    return normal_cdf(z)
