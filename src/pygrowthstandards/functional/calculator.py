"""Helpers for building partially applied calculation callables."""

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
    """Return a callable that computes z-scores or percentiles.

    Args:
        sex: Sex value for reference selection.
        birth_date: Optional date of birth to compute age from dates.
        gestational_age_weeks: Optional gestational age in weeks.
        gestational_age_days: Additional gestational days when weeks provided.
        output_stat: Selects between z-score and percentile outputs.

    Returns:
        A partially applied function with the provided parameters baked in.

    Raises:
        ValueError: If gestational_age_days is provided without weeks.
    """
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
