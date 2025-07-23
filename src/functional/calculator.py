import os
import sys
from typing import Literal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.data.load import load_reference
from src.functional.data import MEASUREMENTS, get_keys, get_lms, get_table
from src.utils.stats import calculate_z_score, normal_cdf

DATA = load_reference()


def zscore(
    measurement: MEASUREMENTS,
    sex: Literal["M", "F", "U"] = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:

    keys = get_keys(measurement, sex, age_days, gestational_age=gestational_age)

    x = age_days if keys[-1] == "age" else gestational_age

    assert x is not None, "Either age_days or gestational_age must be provided."

    data = get_table(DATA, keys)
    lms = get_lms(data, x)

    return calculate_z_score(x, *lms)


def percentile(
    measurement: MEASUREMENTS,
    sex: Literal["M", "F", "U"] = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:
    z = zscore(measurement, sex, age_days, gestational_age)

    return normal_cdf(z)
