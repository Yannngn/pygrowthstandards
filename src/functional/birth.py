import datetime
import os
import sys
from typing import Literal, overload

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)
from src.functional.calculator import percentile as calculator_percentile
from src.functional.calculator import zscore as calculator_zscore
from src.functional.data import MEASUREMENTS

# TODO: add preterm measurements


@overload
def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    age: datetime.timedelta,
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on the age of the individual.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        age (datetime.timedelta): The age of the individual.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    return calculator_percentile(measurement, value, age.days, sex=sex, birth=True)


@overload
def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    gestational_age_weeks: int,
    gestational_age_days: int = 0,
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on gestational age in weeks and days.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        gestational_age_weeks (int): Gestational age in weeks.
        gestational_age_days (int): Additional gestational days.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    total_gestational_days = gestational_age_weeks * 7 + gestational_age_days
    return calculator_percentile(
        measurement, value, total_gestational_days, sex=sex, birth=True
    )


@overload
def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    gestational_age_in_days: int,
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on gestational age in days.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        gestational_age_in_days (int): Gestational age in days.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    return calculator_percentile(
        measurement, value, gestational_age_in_days, sex=sex, birth=True
    )


def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    age: datetime.timedelta | None = None,
    gestational_age_weeks: int | None = None,
    gestational_age_days: int | None = None,
    gestational_age_in_days: int | None = None,
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on the age or gestational age.

    This function supports multiple ways to specify age (timedelta, gestational age in weeks/days, or gestational age in days)
    and dispatches to the correct calculation.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        sex (Literal["M", "F", "U"]): Sex of the individual.
        age (datetime.timedelta | None): Age as timedelta.
        gestational_age_weeks (int | None): Gestational age in weeks.
        gestational_age_days (int | None): Additional gestational days.
        gestational_age_in_days (int | None): Gestational age in days.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    kwargs = locals().copy()
    if age is not None:
        return calculator_percentile(measurement, value, age.days, sex=sex, birth=True)

    if gestational_age_in_days is not None:
        return calculator_percentile(
            measurement, value, gestational_age_in_days, sex=sex, birth=True
        )

    if gestational_age_weeks is not None:
        total_gestational_days = gestational_age_weeks * 7
        if gestational_age_days is not None:
            total_gestational_days += gestational_age_days
        return calculator_percentile(
            measurement, value, total_gestational_days, sex=sex, birth=True
        )


@overload
def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    age: datetime.timedelta,
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on the age of the individual.

    Args:
        measurement (MEASUREMENTS): The type of measurement (bmi, head_circumference, height_length, weight).
        value (float): The measurement value to calculate the z-score for.
        age (datetime.timedelta): The age of the individual.

    Returns:
        float | None: The calculated z-score or None if the calculation is not applicable.
    """
    return calculator_zscore(measurement, value, age.days, sex=sex, birth=True)


@overload
def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    gestational_age_weeks: int,
    gestational_age_days: int = 0,
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on gestational age in weeks and days.

    Args:
        measurement (MEASUREMENTS): The type of measurement (bmi, head_circumference, height_length, weight).
        value (float): The measurement value to calculate the z-score for.
        gestational_age_weeks (int): Gestational age in weeks.
        gestational_age_days (int): Additional gestational days.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated z-score or None if the calculation is not applicable.
    """
    total_gestational_days = gestational_age_weeks * 7 + gestational_age_days
    return calculator_zscore(
        measurement, value, total_gestational_days, sex=sex, birth=True
    )


@overload
def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    gestational_age_in_days: int,
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on gestational age in days.

    Args:
        measurement (MEASUREMENTS): The type of measurement (bmi, head_circumference, height_length, weight).
        value (float): The measurement value to calculate the z-score for.
        gestational_age_in_days (int): Gestational age in days.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated z-score or None if the calculation is not applicable.
    """
    return calculator_zscore(
        measurement, value, gestational_age_in_days, sex=sex, birth=True
    )


def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    age: datetime.timedelta | None = None,
    gestational_age_weeks: int | None = None,
    gestational_age_days: int | None = None,
    gestational_age_in_days: int | None = None,
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on the age or other user-friendly inputs.

    This function supports multiple ways to specify age (timedelta, years/months/days, or birth/measurement dates)
    and dispatches to the correct calculation.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        sex (Literal["M", "F", "U"]): Sex of the individual.
        age (datetime.timedelta | None): Gestational age as timedelta.
        gestational_age_weeks (int | None): Gestational age in weeks.
        gestational_age_days (int | None): Additional gestational days.
        gestational_age_in_days (int | None): Gestational age in days.

    Returns:
        float | None: The calculated z-score or None if not applicable.
    """
    if age is not None:
        return calculator_zscore(measurement, value, age.days, sex=sex, birth=True)

    if gestational_age_in_days is not None:
        return calculator_zscore(
            measurement, value, gestational_age_in_days, sex=sex, birth=True
        )

    if gestational_age_weeks is not None:
        total_gestational_days = gestational_age_weeks * 7
        if gestational_age_days is not None:
            total_gestational_days += gestational_age_days
        return calculator_zscore(
            measurement, value, total_gestational_days, sex=sex, birth=True
        )

    return None


def _run_one(
    measurement: MEASUREMENTS,
    value: float,
    age: datetime.timedelta,
    sex: Literal["M", "F", "U"] = "U",
):
    weeks = age.days // 7
    days = age.days % 7

    age_days = age.days

    z_score = zscore(measurement, value, sex, age=age)
    print(f"The z-score for {measurement} is: {z_score:.3f}")

    z_score = zscore(
        measurement, value, sex, gestational_age_weeks=weeks, gestational_age_days=days
    )
    print(f"The z-score for {measurement} is: {z_score:.3f}")

    z_score = zscore(
        measurement,
        value,
        sex,
        gestational_age_in_days=age_days,
    )
    print(f"The z-score for {measurement} is: {z_score:.3f}")

    percentile_value = percentile(measurement, value, sex, age=age)
    print(f"The percentile for {measurement} is: {percentile_value:.3f}")

    percentile_value = percentile(
        measurement, value, sex, gestational_age_weeks=weeks, gestational_age_days=days
    )
    print(f"The percentile for {measurement} is: {percentile_value:.3f}")

    percentile_value = percentile(
        measurement, value, sex, gestational_age_in_days=age.days
    )
    print(f"The percentile for {measurement} is: {percentile_value:.3f}")


def main():
    # Example 1: Newborn, weight (gestational age: 40 weeks)
    age = datetime.timedelta(weeks=40)
    _run_one("weight", 3.4, age, sex="M")

    # Example 2: Newborn, length (gestational age: 40 weeks)
    age = datetime.timedelta(weeks=40)
    _run_one("length", 50.0, age, sex="F")

    # Example 3: Newborn, head circumference (gestational age: 40 weeks)
    age = datetime.timedelta(weeks=40)
    _run_one("head_circumference", 34.5, age, sex="M")

    # Example 4: Newborn, height (gestational age: 39 weeks)
    age = datetime.timedelta(weeks=39)
    _run_one("height", 49.0, age, sex="F")
    try:
        # Example 5: Newborn, bmi (gestational age: 41 weeks)
        age = datetime.timedelta(weeks=41)
        _run_one("bmi", 13.8, age, sex="M")
    except ValueError as e:
        print(e)
    # Example 6: Newborn, height (male, gestational age: 40 weeks, 3 days)
    age = datetime.timedelta(weeks=40, days=3)
    _run_one("height", 50.5, age, sex="M")


if __name__ == "__main__":
    main()
