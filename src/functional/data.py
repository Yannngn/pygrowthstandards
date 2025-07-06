import json
import os
import sys
from typing import Any, Literal

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.utils.constants import YEAR
from src.utils.stats import interpolate_lms

MEASUREMENTS = Literal[
    "head_circumference",
    "height",
    "length",
    "height_length",
    "stature",
    "weight",
    "body_mass_index",
]

MEASUREMENT_ALIASES = {
    "stature": {"height", "length", "height_length", "stature", "lfa", "hfa", "lhfa"},
    "weight": {"weight", "wfa"},
    "head_circumference": {"head_circumference", "hcfa"},
    "body_mass_index": {"bmi", "body_mass_index", "bfa"},
}

DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "data", "functional")


def get_filename(
    measurement: MEASUREMENTS,
    age_days: int,
    sex: Literal["M", "F", "U"] = "U",
    birth: bool = False,
    very_preterm: bool = False,
    fetal: bool = False,
) -> str:
    def normalized_measurement() -> str:
        for key, aliases in MEASUREMENT_ALIASES.items():
            if measurement in aliases:
                return key
        raise ValueError(f"Unknown measurement: {measurement}")

    def get_source() -> str:
        if fetal:
            raise NotImplementedError("Fetal references are not implemented yet.")
        if birth:
            return "intergrowth-newborn_size"
        if very_preterm:
            return "intergrowth-very_preterm-growth"

        return "who-growth"

    key = normalized_measurement()
    source = get_source()
    sex = sex.lower()  # type: ignore

    if key in ["body_mass_index"] and any((birth, fetal, very_preterm)):
        raise ValueError("No reference for BMI at birth or fetal age.")

    if key in ["head_circumference"] and age_days > 5 * YEAR:
        raise ValueError("No reference for head circumference after 5 years.")

    if key in ["weight"] and age_days > 10 * YEAR:
        raise ValueError("No reference for weight after 10 years.")

    if key in ["stature"] and any((birth, fetal, very_preterm)):
        key = "length"

    return f"{source}-{key}-{sex}-lms.json"


def get_data(filename: str) -> dict[str, float]:
    with open(os.path.join(DATA_DIR, filename), "r") as f:
        data: dict = json.load(f)

    return data


def get_lms(data: dict[str, Any], x: int | float) -> tuple[float, float, float]:
    points = data.get("points", [])

    if not points:
        raise ValueError("No data points available for the given measurement.")

    point = next((p for p in points if float(p["x"]) == float(x)), None)

    if point:
        return float(point["L"]), float(point["M"]), float(point["S"])

    x_values = np.array([float(p["x"]) for p in points])
    l_values = np.array([float(p["L"]) for p in points])
    m_values = np.array([float(p["M"]) for p in points])
    s_values = np.array([float(p["S"]) for p in points])

    entry = interpolate_lms(x_values, l_values, m_values, s_values, x)

    if entry is None:
        raise ValueError(f"No data available for age {x} days")

    return entry
