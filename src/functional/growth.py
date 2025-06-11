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
from src.utils.constants import MONTH, YEAR


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
    return calculator_percentile(measurement, value, age.days, sex)


@overload
def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    years: int = 0,
    months: int = 0,
    days: int = 0,
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on the age of the individual.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        years (int): Years of age.
        months (int): Months of age.
        days (int): Days of age.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    total_days = years * YEAR + months * MONTH + days
    age = datetime.timedelta(days=total_days)
    return calculator_percentile(measurement, value, age.days, sex)


@overload
def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    birth_date: datetime.date,
    measurement_date: datetime.date = datetime.date.today(),
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on birth date and measurement date.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        birth_date (datetime.date): Birth date of the individual.
        measurement_date (datetime.date): Date when the measurement was taken.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    age = measurement_date - birth_date
    return calculator_percentile(measurement, value, age.days, sex)


def percentile(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    years: int | None = None,
    months: int | None = None,
    days: int | None = None,
    birth_date: datetime.date | None = None,
    measurement_date: datetime.date | None = None,
    age: datetime.timedelta | None = None,
    **kwargs,
) -> float | None:
    """
    Calculate the percentile for a given measurement value based on the age or other user-friendly inputs.

    This function supports multiple ways to specify age (timedelta, years/months/days, or birth/measurement dates)
    and dispatches to the correct calculation.

    Args:
        measurement (MEASUREMENTS): The type of measurement.
        value (float): The measurement value.
        sex (Literal["M", "F", "U"]): Sex of the individual.
        years (int | None): Years of age.
        months (int | None): Months of age.
        days (int | None): Days of age.
        birth_date (datetime.date | None): Birth date.
        measurement_date (datetime.date | None): Measurement date.
        age (datetime.timedelta | None): Age as timedelta.

    Returns:
        float | None: The calculated percentile or None if not applicable.
    """
    kwargs = locals().copy()

    if kwargs.get("age") is not None:
        return calculator_percentile(measurement, value, kwargs["age"].days, sex)
    if (
        kwargs.get("birth_date") is not None
        and kwargs.get("measurement_date") is not None
    ):
        age_delta = kwargs["measurement_date"] - kwargs["birth_date"]
        return calculator_percentile(measurement, value, age_delta.days, sex)
    if (
        kwargs.get("years") is not None
        and kwargs.get("months") is not None
        and kwargs.get("days") is not None
    ):
        total_days = kwargs["years"] * YEAR + kwargs["months"] * MONTH + kwargs["days"]
        return calculator_percentile(measurement, value, total_days, sex)


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
    return calculator_zscore(measurement, value, age.days, sex=sex)


@overload
def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    years: int = 0,
    months: int = 0,
    days: int = 0,
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on the age of the individual.

    Args:
        measurement (MEASUREMENTS): The type of measurement (bmi, head_circumference, height_length, weight).
        value (float): The measurement value to calculate the z-score for.
        years (int): Years of age.
        months (int): Months of age.
        days (int): Days of age.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated z-score or None if the calculation is not applicable.
    """
    total_days = years * YEAR + months * MONTH + days
    age = datetime.timedelta(days=total_days)

    return calculator_zscore(measurement, value, age.days, sex=sex)


@overload
def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    birth_date: datetime.date,
    measurement_date: datetime.date = datetime.date.today(),
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on birth date and measurement date.

    Args:
        measurement (MEASUREMENTS): The type of measurement (bmi, head_circumference, height_length, weight).
        value (float): The measurement value to calculate the z-score for.
        birth_date (datetime.date): Birth date of the individual.
        measurement_date (datetime.date): Date when the measurement was taken.
        sex (Literal["M", "F", "U"]): Sex of the individual.

    Returns:
        float | None: The calculated z-score or None if the calculation is not applicable.
    """
    age = measurement_date - birth_date

    return calculator_zscore(measurement, value, age.days, sex=sex)


def zscore(
    measurement: MEASUREMENTS,
    value: float,
    sex: Literal["M", "F", "U"] = "U",
    *,
    years: int | None = None,
    months: int | None = None,
    days: int | None = None,
    birth_date: datetime.date | None = None,
    measurement_date: datetime.date | None = None,
    age: datetime.timedelta | None = None,
    **kwargs,
) -> float | None:
    """
    Calculate the z-score for a given measurement value based on the age or other user-friendly inputs.

    This function supports multiple ways to specify age (timedelta, years/months/days, or birth/measurement dates)
    and dispatches to the correct calculation.

    Args:
        measurement (MEASUREMENTS): The type of measurement (bmi, head_circumference, height_length, weight).
        value (float): The measurement value to calculate the z-score for.
        sex (Literal["M", "F", "U"]): Sex of the individual.
        years (int | None): Years of age.
        months (int | None): Months of age.
        days (int | None): Days of age.
        birth_date (datetime.date | None): Birth date.
        measurement_date (datetime.date | None): Measurement date.
        age (datetime.timedelta | None): Age as timedelta.

    Returns:
        float | None: The calculated z-score or None if the calculation is not applicable.
    """
    kwargs = locals().copy()

    if kwargs.get("age") is not None:
        return calculator_zscore(measurement, value, (kwargs["age"].days), sex)
    if (
        kwargs.get("birth_date") is not None
        and kwargs.get("measurement_date") is not None
    ):
        age_delta = kwargs["measurement_date"] - kwargs["birth_date"]
        return calculator_zscore(measurement, value, (age_delta.days), sex)
    if (
        kwargs.get("years") is not None
        and kwargs.get("months") is not None
        and kwargs.get("days") is not None
    ):
        total_days = kwargs["years"] * YEAR + kwargs["months"] * MONTH + kwargs["days"]
        return calculator_zscore(measurement, value, total_days, sex)


def _run_one(
    measurement: MEASUREMENTS,
    value: float,
    age: datetime.timedelta,
    birth_date: datetime.date,
    measurement_date: datetime.date,
    sex: Literal["M", "F", "U"] = "U",
):
    years = int(age.days // YEAR)
    months = int((age.days % YEAR) // MONTH)
    days = int(age.days % MONTH)

    z_score = zscore(measurement, value, sex, age=age)
    print(f"The z-score for {measurement} is: {z_score:.3f}")

    z_score = zscore(measurement, value, sex, years=years, months=months, days=days)
    print(f"The z-score for {measurement} is: {z_score:.3f}")

    z_score = zscore(
        measurement,
        value,
        sex,
        birth_date=birth_date,
        measurement_date=measurement_date,
    )
    print(f"The z-score for {measurement} is: {z_score:.3f}")

    percentile_value = percentile(measurement, value, sex, age=age)
    print(f"The percentile for {measurement} is: {percentile_value:.3f}")

    percentile_value = percentile(
        measurement, value, sex, years=years, months=months, days=days
    )
    print(f"The percentile for {measurement} is: {percentile_value:.3f}")

    percentile_value = percentile(
        measurement,
        value,
        sex,
        birth_date=birth_date,
        measurement_date=measurement_date,
    )
    print(f"The percentile for {measurement} is: {percentile_value:.3f}")


def main():
    # Example 1: Newborn, weight
    birth_date = datetime.date(2024, 6, 1)
    measurement_date = birth_date
    age = measurement_date - birth_date
    _run_one("weight", 3.2, age, birth_date, measurement_date, sex="M")

    # Example 2: 6 months old, length
    birth_date = datetime.date(2023, 12, 1)
    measurement_date = datetime.date(2024, 6, 1)
    age = measurement_date - birth_date
    _run_one("length", 67.0, age, birth_date, measurement_date, sex="F")

    # Example 3: 2 years old, head circumference
    birth_date = datetime.date(2022, 6, 1)
    measurement_date = datetime.date(2024, 6, 1)
    age = measurement_date - birth_date
    _run_one("head_circumference", 49.0, age, birth_date, measurement_date, sex="M")

    # Example 4: 7 years old, height
    birth_date = datetime.date(2017, 6, 1)
    measurement_date = datetime.date(2024, 6, 1)
    age = measurement_date - birth_date
    _run_one("height", 120.0, age, birth_date, measurement_date, sex="F")

    # Example 5: 15 years old, bmi
    birth_date = datetime.date(2009, 6, 1)
    measurement_date = datetime.date(2024, 6, 1)
    age = measurement_date - birth_date
    _run_one("bmi", 21.5, age, birth_date, measurement_date, sex="M")

    # Example 6: 18 years old, height
    birth_date = datetime.date(2006, 6, 1)
    measurement_date = datetime.date(2024, 6, 1)
    age = measurement_date - birth_date
    _run_one("height", 170.0, age, birth_date, measurement_date, sex="F")


if __name__ == "__main__":
    main()
