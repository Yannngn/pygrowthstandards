import os
import sys
from typing import Literal

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.functional.data import (
    MEASUREMENTS,
    get_data,
    get_data_filename,
    get_lms_for_age,
)
from src.utils.stats import calculate_z_score, normal_cdf


def zscore(
    measurement: MEASUREMENTS,
    value: float,
    age_days: int,
    sex: Literal["M", "F", "U"] = "U",
    birth: bool = False,
    fetal: bool = False,
) -> float:
    if sex not in ["M", "F"]:
        sex = "F"  # default

    age_days = int(age_days)  # ensure age is an integer

    filename = get_data_filename(measurement, age_days, sex, birth=birth, fetal=fetal)  # type: ignore
    data = get_data(filename)
    lms = get_lms_for_age(data, age_days)

    return calculate_z_score(value, **lms)


def percentile(
    measurement: MEASUREMENTS,
    value: float,
    age: int,
    sex: Literal["M", "F", "U"] = "U",
    birth: bool = False,
    fetal: bool = False,
) -> float:
    z = zscore(measurement, value, age, sex, birth=birth, fetal=fetal)

    return normal_cdf(z)
