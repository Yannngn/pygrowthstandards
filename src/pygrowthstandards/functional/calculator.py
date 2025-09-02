from pygrowthstandards.utils.errors import NoReferenceDataException

from ..utils.config import DataSexType, MeasurementTypeType
from ..utils.stats import calculate_z_score, normal_cdf
from .data import DATA, get_keys, get_lms, get_table


def zscore(
    measurement: MeasurementTypeType,
    value: float,
    sex: DataSexType = "U",
    age_days: int | None = None,
    gestational_age_days: int | None = None,
) -> float:
    keys = get_keys(
        measurement=measurement,
        sex=sex,
        age_days=age_days,
        gestational_age_days=gestational_age_days,
    )

    if keys[1] in {"very_preterm_growth"}:
        x = (age_days or 0) + (gestational_age_days or 0)
    elif keys[1] in {"very_preterm_newborn", "newborn"}:
        x = gestational_age_days
    else:
        x = age_days

    assert x is not None and x > 0, (
        "Either age_days or gestational_age must be provided."
    )

    data = get_table(DATA, keys)
    try:
        lms = get_lms(data, x)
    except NoReferenceDataException as err:
        raise NoReferenceDataException(keys[2], keys[1], x, sex) from err
    return calculate_z_score(value, *lms)


def percentile(
    measurement: MeasurementTypeType,
    value: float,
    sex: DataSexType = "U",
    age_days: int | None = None,
    gestational_age_days: int | None = None,
) -> float:
    z = zscore(measurement, value, sex, age_days, gestational_age_days)

    return normal_cdf(z)
