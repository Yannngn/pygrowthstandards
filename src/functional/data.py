import os
from typing import Literal

import pandas as pd

from ..data.load import GrowthTable
from ..utils import stats
from ..utils.constants import WEEK, YEAR

MEASUREMENTS = Literal["head_circumference", "stature", "weight", "body_mass_index", "weight_stature"]


MEASUREMENT_ALIASES = {
    "head_circumference": {"hcfa", "hc"},
    "stature": {"lfa", "hfa", "lhfa", "sfa", "l", "h", "s"},
    "weight": {"wfa", "w"},
    "body_mass_index": {"bmi", "bfa"},
    "weight_stature": {
        "wfs",
        "wfl",
        "wfh",
        "weight_length",
        "weight_height",
        "weight_for_stature",
        "weight_for_length",
        "weight_for_height",
    },
}

DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "data")


def get_keys(
    measurement: MEASUREMENTS,
    sex: Literal["M", "F", "U"] = "U",
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> tuple[str, str, str, str]:
    if age_days is None and gestational_age is None:
        raise ValueError("Either age_days or gestational_age must be provided.")

    def normalized_measurement() -> str:
        for key, aliases in MEASUREMENT_ALIASES.items():
            normalized = measurement.lower().replace("-", "_")
            if normalized in aliases | {key}:
                return key
        raise ValueError(f"Unknown measurement: {measurement}")

    measurement_type = normalized_measurement()
    sex = sex.lower() if sex in ["M", "F"] else "f"  # type: ignore

    name = ""
    x_var_type = ""

    if age_days is not None:
        x_var_type = "age"
        if measurement_type in ["head_circumference", "weight_stature"] and age_days > 5 * YEAR:
            raise ValueError(f"No reference for {measurement_type} after 5 years.")

        if measurement_type in ["weight"] and age_days > 10 * YEAR:
            raise ValueError(f"No reference for {measurement_type} after 10 years.")

        name = "growth" if age_days > 5 * YEAR else "child_growth"

        if gestational_age is not None and age_days < 64 * WEEK:
            if gestational_age < 28:
                name = "very_preterm_growth"

    if gestational_age is not None and (age_days == 0 or age_days is None):
        x_var_type = "gestational_age"
        if measurement_type in ["body_mass_index"]:
            raise ValueError(f"No reference for {measurement_type} at birth or fetal age.")

        if gestational_age > 28:
            if measurement_type in ["weight_stature"]:
                raise ValueError(f"No reference for {measurement_type} at birth or fetal age.")
            name = "newborn"
        else:
            name = "very_preterm_newborn"

    return name, measurement_type, sex, x_var_type


def get_table(data: pd.DataFrame, keys: tuple) -> GrowthTable:
    # data = load_reference()
    name, measurement, sex, x_var_type = keys
    return GrowthTable.from_data(data, name, None, measurement, sex, x_var_type)


def get_lms(table: GrowthTable, x: float) -> tuple[float, float, float]:
    """
    Get the L, M, S values for a given x from the GrowthTable.

    :param table: The GrowthTable instance.
    :param x: The x value (e.g., age in days).
    :return: A tuple of (L, M, S).
    """
    if x not in table.x:
        return stats.interpolate_lms(x, table.x, table.L, table.M, table.S)

    index = list(table.x).index(x)

    return table.L[index], table.M[index], table.S[index]
