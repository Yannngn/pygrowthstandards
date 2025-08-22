from ..utils.config import DataSexType, MeasurementTypeType
from ..utils.stats import calculate_z_score, normal_cdf
from .data import DATA, get_keys, get_lms, get_table


def zscore(
    measurement: MeasurementTypeType,
    value: float,
    sex: DataSexType = "U",
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
    measurement: MeasurementTypeType,
    value: float,
    sex: DataSexType = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> float:
    z = zscore(measurement, value, sex, age_days, gestational_age)

    return normal_cdf(z)
