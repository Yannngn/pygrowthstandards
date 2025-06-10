import datetime
import json
import os
import sys
from typing import Literal, overload

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.utils.constants import MONTH, YEAR
from src.utils.stats import calculate_z_score, functional_interpolate_lms, normal_cdf

MEASUREMENTS = Literal[
    "bmi",
    "head_circumference",
    "height",
    "length",
    "height_length",
    "weight",
    "body_mass_index",
]

# TODO: add preterm measurements


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
    return _zscore(measurement, value, age.days)


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

    return _zscore(measurement, value, age.days)


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

    return _zscore(measurement, value, age.days)


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
        return _zscore(measurement, value, (kwargs["age"].days), sex)
    if (
        kwargs.get("birth_date") is not None
        and kwargs.get("measurement_date") is not None
    ):
        age_delta = kwargs["measurement_date"] - kwargs["birth_date"]
        return _zscore(measurement, value, (age_delta.days), sex)
    if (
        kwargs.get("years") is not None
        and kwargs.get("months") is not None
        and kwargs.get("days") is not None
    ):
        total_days = kwargs["years"] * YEAR + kwargs["months"] * MONTH + kwargs["days"]
        return _zscore(measurement, value, total_days, sex)


def _zscore(
    measurement: MEASUREMENTS,
    value: float,
    age: int,
    sex: Literal["M", "F", "U"] = "U",
) -> float | None:
    if sex not in ["M", "F"]:
        sex = "F"  # default

    age = int(age)  # ensure age is an integer

    table = _choose_table(measurement, age, sex)  # type: ignore
    lms = _get_table_data(table, age)

    return calculate_z_score(value, **lms)


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
    return _percentile(measurement, value, age.days, sex)


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
    return _percentile(measurement, value, age.days, sex)


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
    return _percentile(measurement, value, age.days, sex)


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
        return _percentile(measurement, value, kwargs["age"].days, sex)
    if (
        kwargs.get("birth_date") is not None
        and kwargs.get("measurement_date") is not None
    ):
        age_delta = kwargs["measurement_date"] - kwargs["birth_date"]
        return _percentile(measurement, value, age_delta.days, sex)
    if (
        kwargs.get("years") is not None
        and kwargs.get("months") is not None
        and kwargs.get("days") is not None
    ):
        total_days = kwargs["years"] * YEAR + kwargs["months"] * MONTH + kwargs["days"]
        return _percentile(measurement, value, total_days, sex)


def _percentile(
    measurement: MEASUREMENTS,
    value: float,
    age: int,
    sex: Literal["M", "F", "U"] = "U",
) -> float | None:
    z = _zscore(measurement, value, age, sex)

    if z is None:
        return None

    return normal_cdf(z)


def _get_table_data(table: str, age_days: int) -> dict[str, float]:
    with open(os.path.join("data", "functional", table), "r") as f:
        data: dict = json.load(f)

    age_key = "age" if "age" in data.keys() else "gestational_age"

    age_index = next(
        (i for i, entry in enumerate(data[age_key]) if int(entry) == age_days), None
    )

    if age_index is None:
        entry = functional_interpolate_lms(
            data[age_key], data["l"], data["m"], data["s"], age_days
        )

        if entry is None:
            raise ValueError(f"No data available for age {age_days} days")

        return entry

    return {k: data[k][age_index] for k in ("l", "m", "s")}


def _choose_table(
    measurement: MEASUREMENTS, age_days: int, sex: Literal["M", "F"]
) -> str:
    sex = sex.lower()  # type: ignore

    measurement_aliases = {
        "length": {"height", "length", "height_length"},
        "weight": {"weight"},
        "head_circumference": {"head_circumference"},
        "body_mass_index": {"bmi", "body_mass_index"},
    }

    def canonical_measurement(measurement: str) -> str:
        for key, aliases in measurement_aliases.items():
            if measurement in aliases:
                return key
        raise ValueError(f"Unknown measurement: {measurement}")

    key = canonical_measurement(measurement)
    age_key = "age"

    # TODO: add birth measurements with gestational age
    # if age_days == 0:
    #     if key == "bmi":
    #         raise ValueError("No reference for birth BMI.")
    #     source = "intergrowth_21st_birth_size"
    #     age_key = "gestational_age"
    if age_days <= 2 * YEAR:
        source = "who_growth_0_to_2"
    elif key == "head_circumference" and age_days > 5 * YEAR:
        raise ValueError("No reference for head circumference after 5 years.")
    elif age_days <= 5 * YEAR:
        source = "who_growth_2_to_5"
    elif age_days <= 10 * YEAR:
        source = "who_growth_5_to_10"
    elif key == "weight" and age_days > 10 * YEAR:
        raise ValueError("No reference for weight after 10 years.")
    elif age_days <= 19 * YEAR:
        source = "who_growth_10_to_19"
    else:
        raise ValueError("Age exceeds the maximum reference age of 19 years.")

    if age_days > 2 * YEAR and key == "length":
        key = "height"

    return f"{source}_{key}_for_{age_key}_{sex}.json"


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
