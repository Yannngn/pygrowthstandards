import os
import sys
from typing import Literal

# Use relative imports instead of modifying sys.path

from ..data.load import load_reference
from .data import MEASUREMENTS, get_keys, get_lms, get_table
from ..utils.stats import calculate_z_score, normal_cdf

DATA = load_reference()


def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:

    keys = get_keys(measurement, sex, age_days, gestational_age=gestational_age)

    x = age_days if keys[-1] == "age" else gestational_age

    assert x is not None, "Either age_days or gestational_age must be provided."

    data = get_table(DATA, keys)
    lms = get_lms(data, x)

    return calculate_z_score(value, *lms)


def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:
    z = zscore(measurement, value, sex, age_days, gestational_age)

    return normal_cdf(z)
