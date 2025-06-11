import json
import os
import sys
from typing import Any, Literal

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.utils.constants import YEAR
from src.utils.stats import functional_interpolate_lms

MEASUREMENTS = Literal[
    "bmi",
    "head_circumference",
    "height",
    "length",
    "height_length",
    "weight",
    "body_mass_index",
]

MEASUREMENT_ALIASES = {
    "length": {"height", "length", "height_length"},
    "weight": {"weight"},
    "head_circumference": {"head_circumference"},
    "body_mass_index": {"bmi", "body_mass_index"},
}

DATA_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, "data", "functional"
)


def get_lms_for_age(data: dict[str, Any], age_days: int) -> dict[str, float]:
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


def get_data(filename: str) -> dict[str, float]:

    with open(os.path.join(DATA_DIR, filename), "r") as f:
        data: dict = json.load(f)

    return data


def get_data_filename(
    measurement: MEASUREMENTS,
    age_days: int,
    sex: Literal["M", "F"],
    birth: bool = False,
    fetal: bool = False,
) -> str:

    def canonical_measurement(measurement: str) -> str:
        for key, aliases in MEASUREMENT_ALIASES.items():
            if measurement in aliases:
                return key
        raise ValueError(f"Unknown measurement: {measurement}")

    def get_source(
        age_days: int,
        birth: bool = False,
        fetal: bool = False,
    ) -> str:
        if fetal:
            raise NotImplementedError("Fetal references are not implemented yet.")
        if birth:
            return "intergrowth_21st_birth_size"
        if age_days <= 2 * YEAR:
            return "who_growth_0_to_2"
        if age_days <= 5 * YEAR:
            return "who_growth_2_to_5"
        if age_days <= 10 * YEAR:
            return "who_growth_5_to_10"
        if age_days <= 19 * YEAR:
            return "who_growth_10_to_19"

        raise ValueError("Age exceeds the maximum reference age of 19 years.")

    key = canonical_measurement(measurement)
    source = get_source(age_days, birth, fetal)
    age_key = "gestational_age" if birth or fetal else "age"
    sex = sex.lower()  # type: ignore

    if key == "body_mass_index" and birth or key == "body_mass_index" and fetal:
        raise ValueError("No reference for BMI at birth or fetal age.")

    if key == "head_circumference" and age_days > 5 * YEAR:
        raise ValueError("No reference for head circumference after 5 years.")

    if key == "weight" and age_days > 10 * YEAR:
        raise ValueError("No reference for weight after 10 years.")

    if age_days > 2 * YEAR and key == "length":
        key = "height"

    return f"{source}_{key}_for_{age_key}_{sex}.json"
