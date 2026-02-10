from collections.abc import Callable
from functools import partial
from typing import Literal

from pygrowthstandards import functional as F
from pygrowthstandards.config.growth import DataSexType
from pygrowthstandards.utils.date import DateInputType


def calculator(
    sex: DataSexType,
    birth_date: DateInputType | None = None,
    gestational_age_weeks: int | None = None,
    gestational_age_days: int = 0,
    output_stat: Literal["zscore", "percentile"] = "zscore",
) -> Callable[..., float]:
    gestational_age = None
    if gestational_age_weeks is None and gestational_age_days != 0:
        raise ValueError("gestational_age_days requires gestational_age_weeks to be specified")
    if gestational_age_weeks is not None:
        gestational_age = gestational_age_weeks * 7 + gestational_age_days

    func = F.percentile if output_stat == "percentile" else F.zscore

    if birth_date is not None and gestational_age is not None:
        return partial(func, sex=sex, birth_date=birth_date, gestational_age=gestational_age)

    if birth_date is not None:
        return partial(func, sex=sex, birth_date=birth_date)

    if gestational_age is not None:
        return partial(func, sex=sex, gestational_age=gestational_age)

    return partial(func, sex=sex)
