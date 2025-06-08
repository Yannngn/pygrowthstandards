import datetime
import json
import os
import sys
from typing import Literal, overload

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.utils.constants import MONTH, YEAR
from src.utils.stats import calculate_z_score, interpolate_lms, normal_cdf

MEASUREMENTS = Literal[
    "bmi",
    "head_circumference",
    "height",
    "lenght",
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
        return _zscore(measurement, value, kwargs["age"].days, sex)
    if (
        kwargs.get("birth_date") is not None
        and kwargs.get("measurement_date") is not None
    ):
        age_delta = kwargs["measurement_date"] - kwargs["birth_date"]
        return _zscore(measurement, value, age_delta.days, sex)
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
    table = _choose_table(measurement, age)
    lms = _get_table_data(table, age, sex)

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


def _get_table_data(table: str, age_days: int, sex: str) -> dict[str, float]:
    with open(os.path.join("data", table), "r") as f:
        data: list[dict] = json.load(f)["data"]

    age_key = list(data[0].keys())[0]  # The first key is the age in days

    if sex not in ["M", "F"]:
        sex = "F"

    data = [entry for entry in data if entry["sex"] == sex]

    entry = next((entry for entry in data if int(entry[age_key]) == age_days), None)

    if entry is None:
        entry = interpolate_lms(data, age_days)

        if entry is None:
            raise ValueError(f"No data available for age {age_days} days")

        return entry

    return {k: entry[k] for k in ("l", "m", "s")}


def _choose_table(measurement: MEASUREMENTS, age_days: int) -> str:
    if age_days == 0:
        if measurement in ["height", "lenght", "height_length"]:
            table = "intergrowth_21st_birth_size_length_for_gestational_age.json"
        elif measurement == "weight":
            table = "intergrowth_21st_birth_size_weight_for_gestational_age.json"
        elif measurement == "head_circumference":
            table = "intergrowth_21st_birth_size_head_circumference_for_gestational_age.json"
        elif measurement == "bmi":
            raise ValueError("No reference for birth BMI.")

    elif age_days <= 2 * YEAR:
        if measurement in ["height", "lenght", "height_length"]:
            table = "who_growth_0_to_2_length_for_age.json"
        elif measurement == "weight":
            table = "who_growth_0_to_2_weight_for_age.json"
        elif measurement == "head_circumference":
            table = "who_growth_0_to_2_head_circumference_for_age.json"
        elif measurement == "bmi":
            table = "who_growth_0_to_2_body_mass_index_for_age.json"

    elif age_days <= 5 * YEAR:
        if measurement in ["height", "lenght", "height_length"]:
            table = "who_growth_2_to_5_height_for_age.json"
        elif measurement == "weight":
            table = "who_growth_2_to_5_weight_for_age.json"
        elif measurement == "head_circumference":
            table = "who_growth_2_to_5_head_circumference_for_age.json"
        elif measurement == "bmi":
            table = "who_growth_2_to_5_body_mass_index_for_age.json"

    elif age_days <= 10 * YEAR:
        if measurement in ["height", "lenght", "height_length"]:
            table = "who_growth_5_to_10_height_for_age.json"
        elif measurement == "weight":
            table = "who_growth_5_to_10_weight_for_age.json"
        elif measurement == "bmi":
            table = "who_growth_5_to_10_body_mass_index_for_age.json"
        elif measurement == "head_circumference":
            raise ValueError("No reference for head circumference after 5 years.")

    elif age_days <= 19 * YEAR:
        if measurement in ["height", "lenght", "height_length"]:
            table = "who_growth_10_to_19_height_for_age.json"
        elif measurement == "weight":
            table = "who_growth_10_to_19_weight_for_age.json"
        elif measurement == "bmi":
            table = "who_growth_10_to_19_body_mass_index_for_age.json"
        elif measurement == "head_circumference":
            raise ValueError("No reference for head circumference after 5 years.")

    else:
        raise ValueError("Age exceeds the maximum reference age of 19 years.")

    return table


def main():
    measurement = "weight"
    value = 5.5
    age = datetime.timedelta(days=30)
    years, months, days = 0, 0, 30
    birth_date = datetime.date(2025, 1, 5)
    measurement_date = datetime.date(2025, 2, 4)
    sex = "M"

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


if __name__ == "__main__":
    main()
