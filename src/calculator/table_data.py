import csv
import os
import sys
from typing import Any, Collection

import numpy as np
from scipy.stats import norm

from src.utils.constants import WEEK, YEAR

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from src.utils.stats import (
    calculate_value_for_z_score,
    calculate_z_score,
    interpolate_lms,
)


class Tables:
    # Growth
    GROWTH_STATURE = "growth_stature"
    GROWTH_WEIGHT = "growth_weight"
    GROWTH_HEAD_CIRCUMFERENCE = "growth_head_circumference"
    GROWTH_BODY_MASS_INDEX = "growth_body_mass_index"

    # Weight/Stature
    GROWTH_WEIGHT_LENGTH = "growth_weight_length"
    GROWTH_WEIGHT_HEIGHT = "growth_weight_height"

    # Velocity
    GROWTH_WEIGHT_VELOCITY = "growth_weight_velocity"
    GROWTH_LENGTH_VELOCITY = "growth_length_velocity"
    GROWTH_CIRCUMFERENCE_VELOCITY = "growth_head_circumference_velocity"

    # Preterm Growth
    VERY_PRETERM_LENGTH = "very_preterm_growth_length"
    VERY_PRETERM_WEIGHT = "very_preterm_growth_weight"
    VERY_PRETERM_HEAD_CIRCUMFERENCE = "very_preterm_growth_head_circumference"

    # Birth
    BIRTH_LENGTH = "newborn_size_length"
    BIRTH_WEIGHT = "newborn_size_weight"
    BIRTH_HEAD_CIRCUMFERENCE = "newborn_size_head_circumference"


class TableFiles:
    # Growth
    GROWTH_STATURE = "who-growth-stature"
    GROWTH_WEIGHT = "who-growth-weight"
    GROWTH_HEAD_CIRCUMFERENCE = "who-growth-head_circumference"
    GROWTH_BODY_MASS_INDEX = "who-growth-body_mass_index"

    # Weight/Stature
    GROWTH_WEIGHT_LENGTH = "who-growth-weight_length"
    GROWTH_WEIGHT_HEIGHT = "who-growth-weight_height"

    # Velocity
    GROWTH_WEIGHT_VELOCITY = "who-growth-weight_velocity"
    GROWTH_LENGTH_VELOCITY = "who-growth-length_velocity"
    GROWTH_CIRCUMFERENCE_VELOCITY = "who-growth-head_circumference_velocity"

    # Preterm Growth
    VERY_PRETERM_LENGTH = "intergrowth-very_preterm_growth-length"
    VERY_PRETERM_WEIGHT = "intergrowth-very_preterm_growth-weight"
    VERY_PRETERM_HEAD_CIRCUMFERENCE = "intergrowth-very_preterm_growth-head_circumference"

    # Birth
    BIRTH_LENGTH = "intergrowth-newborn_size-length"
    BIRTH_WEIGHT = "intergrowth-newborn_size-weight"
    BIRTH_HEAD_CIRCUMFERENCE = "intergrowth-newborn_size-head_circumference"


class TableData:
    def __init__(self, sex: str):
        """
        Initializes a TableData instance with age in days and preterm status.

        :param age_days: Age of the child in days.
        :param is_very_preterm: Boolean indicating if the child is very preterm.
        """
        self.sex = sex

        self._setup()

    def get_table_name(self, measurement_type: str, age_group: str) -> str:
        def normalize_measurement_type():
            if measurement_type in ["stature", "lfa", "hfa", "lhfa", "length", "height", "length_height"]:
                if age_group in ["newborn", "birth_size", "birth", "very_preterm", "very_preterm_growth"]:
                    return "length"
                return "stature"

            if measurement_type in ["w", "wfa", "weight"]:
                return "weight"

            if measurement_type in ["hc", "hcfa", "head_circumference"]:
                return "head_circumference"

            if measurement_type in ["bmi", "body_mass_index", "bfa"]:
                return "body_mass_index"

            if measurement_type in ["wlr", "weight_length", "weight_length_ratio"]:
                return "weight_length"

            if measurement_type in ["whr", "weight_height", "weight_height_ratio"]:
                return "weight_height"

            if measurement_type in ["weight_velocity"]:
                return "weight_velocity"

            if measurement_type in ["length_velocity"]:
                return "length_velocity"

            if measurement_type in ["head_circumference_velocity"]:
                return "head_circumference_velocity"

            raise ValueError(f"Unknown measurement type: {measurement_type}")

        def normalize_age_group():
            if age_group in ["newborn", "newborn_size", "birth_size", "birth"]:
                return "newborn_size"
            if age_group in ["very_preterm", "very_preterm_growth"]:
                return "very_preterm_growth"
            return "growth"

        return f"{normalize_age_group()}_{normalize_measurement_type()}"

    def get_table(self, name: str) -> dict[str, list[int | float]]:
        """
        Returns the LMS data for the specified table name.
        :param name: The name of the table (e.g., "growth_stature").
        :return: A dictionary with keys 'x', 'l', 'm', 's'.
        """
        data = getattr(self, name, {}).copy()
        if not data:
            raise ValueError(f"Unknown measurement name: {name}")

        return data

    def get_table_cutoffs(self, measurement_type: str, age_group: str = "none") -> tuple[int | float, int | float]:
        """
        Returns the start and end ages for the specified table.

        """
        name = self.get_table_name(measurement_type, age_group)
        data = getattr(self, name, {}).copy()
        if not data:
            raise ValueError(f"Unknown name: {name}")
        x = data.get("x", [])

        return min(x), max(x)

    def get_measurement_type(self, table_name: str) -> str:
        if table_name in [Tables.GROWTH_STATURE, Tables.BIRTH_LENGTH, Tables.VERY_PRETERM_LENGTH]:
            return "stature"

        if table_name in [Tables.GROWTH_WEIGHT, Tables.BIRTH_WEIGHT, Tables.VERY_PRETERM_WEIGHT]:
            return "weight"

        if table_name in [
            Tables.GROWTH_HEAD_CIRCUMFERENCE,
            Tables.BIRTH_HEAD_CIRCUMFERENCE,
            Tables.VERY_PRETERM_HEAD_CIRCUMFERENCE,
        ]:
            return "head_circumference"

        if table_name in [Tables.GROWTH_BODY_MASS_INDEX]:
            return "body_mass_index"

        if table_name in [Tables.GROWTH_WEIGHT_LENGTH]:
            return "weight_length_ratio"

        if table_name in [Tables.GROWTH_WEIGHT_HEIGHT]:
            return "weight_height_ratio"

        if table_name in [Tables.GROWTH_WEIGHT_VELOCITY]:
            return "weight_velocity"

        if table_name in [Tables.GROWTH_LENGTH_VELOCITY]:
            return "length_velocity"

        if table_name in [Tables.GROWTH_CIRCUMFERENCE_VELOCITY]:
            return "head_circumference_velocity"

        raise ValueError(f"Unknown measurement type: {table_name}")

    def get_age_group(self, age_days: int | float, newborn: bool = False, very_preterm: bool = False) -> str:
        if newborn:
            return "newborn"

        if very_preterm and age_days < 64 * WEEK:
            return "very_preterm"

        if age_days < 2 * YEAR:
            return "0-2"

        if age_days < 5 * YEAR:
            return "2-5"

        if age_days < 10 * YEAR:
            return "5-10"

        return "10-19"

    def get_plot_data(
        self, measurement_type: str, age_group: str = "none", values: Collection[int | float] = [-3, -2, 0, 2, 3]
    ) -> dict[Any, list[int | float]]:
        """
        Returns a dictionary with x values and corresponding y values for the specified table and zscores or centiles.
        :param measurement_type: The measurement_type of the table (e.g., "stature").
        :param values: A list of zscores or centiles to plot.
        :return: A dictionary with x values and corresponding y values.
        """
        name = self.get_table_name(measurement_type, age_group)
        data = self.get_table(name)

        plot_data: dict = {"x": np.array(data["x"])}

        for value in values:
            if isinstance(value, float):
                assert 0 < value < 1, "Centile values must be between 0 and 1."
                plot_data[value] = self._calculate_values_for_centile_array(name, value)
                continue

            plot_data[value] = self._calculate_values_for_z_score_array(name, value)

        return plot_data

    def get_lms(self, name: str, x: int | float) -> tuple[float, float, float]:
        data = self.get_table(name)

        x_ = np.array(data.pop("x", []))

        if x in x_:
            idx = np.where(x_ == x)[0][0]
            return data["l"][idx], data["m"][idx], data["s"][idx]

        l_values = np.array(data["l"])
        m_values = np.array(data["m"])
        s_values = np.array(data["s"])

        # Interpolate LMS parameters if exact x value not found
        return interpolate_lms(x_values=x_, l_values=l_values, m_values=m_values, s_values=s_values, x=x)

    def _setup(self):
        """Sets up the data for various anthropometric measurements based on the child's age and preterm status."""

        sex = self.sex.lower()

        self.growth_stature = self._read_data(f"{TableFiles.GROWTH_STATURE}-{sex}-lms.csv")
        self.growth_weight = self._read_data(f"{TableFiles.GROWTH_WEIGHT}-{sex}-lms.csv")
        self.growth_head_circumference = self._read_data(f"{TableFiles.GROWTH_HEAD_CIRCUMFERENCE}-{sex}-lms.csv")
        self.growth_body_mass_index = self._read_data(f"{TableFiles.GROWTH_BODY_MASS_INDEX}-{sex}-lms.csv")

        self.growth_weight_length = self._read_data(f"{TableFiles.GROWTH_WEIGHT_LENGTH}-{sex}-lms.csv")
        self.growth_weight_height = self._read_data(f"{TableFiles.GROWTH_WEIGHT_HEIGHT}-{sex}-lms.csv")

        self.growth_weight_velocity = self._read_data(f"{TableFiles.GROWTH_WEIGHT_VELOCITY}-{sex}-lms.csv")
        self.growth_length_velocity = self._read_data(f"{TableFiles.GROWTH_LENGTH_VELOCITY}-{sex}-lms.csv")
        self.growth_circumference_velocity = self._read_data(f"{TableFiles.GROWTH_CIRCUMFERENCE_VELOCITY}-{sex}-lms.csv")

        self.very_preterm_growth_length = self._read_data(f"{TableFiles.VERY_PRETERM_LENGTH}-{sex}-lms.csv")
        self.very_preterm_growth_weight = self._read_data(f"{TableFiles.VERY_PRETERM_WEIGHT}-{sex}-lms.csv")
        self.very_preterm_growth_head_circumference = self._read_data(f"{TableFiles.VERY_PRETERM_HEAD_CIRCUMFERENCE}-{sex}-lms.csv")

        self.newborn_size_length = self._read_data(f"{TableFiles.BIRTH_LENGTH}-{sex}-lms.csv")
        self.newborn_size_weight = self._read_data(f"{TableFiles.BIRTH_WEIGHT}-{sex}-lms.csv")
        self.newborn_size_head_circumference = self._read_data(f"{TableFiles.BIRTH_HEAD_CIRCUMFERENCE}-{sex}-lms.csv")

    def _read_data(self, name: str) -> dict[str, list[int | float]]:
        """
        Reads LMS data from a CSV file and returns a dictionary with keys 'x', 'l', 'm', 's'.
        Assumes the CSV has columns: x, l, m, s (with or without header).
        """

        data_path = os.path.join("data/tabular", name)
        result: dict[str, list[float]] = {"x": [], "l": [], "m": [], "s": []}

        with open(data_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                result["x"].append(float(row["x"]))
                result["l"].append(float(row["L"]))
                result["m"].append(float(row["M"]))
                result["s"].append(float(row["S"]))

        return result

    def _calculate_z_score(self, y: float, lamb: float, mu: float, sigm: float) -> float:
        def fix_extremes(z: float) -> float:
            """
            Fixes extreme z-scores by adjusting them based on the calculated values for z-scores of -3 and 3.
            This is to ensure that extreme values do not skew the results.
            # https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/computation.pdf
            """

            if lamb == 1:
                return z

            if z > 3:
                sd3 = self._calculate_value_for_z_score(3, lamb, mu, sigm)
                sd2 = self._calculate_value_for_z_score(2, lamb, mu, sigm)
                return 3 + ((y - sd3) / (sd3 - sd2))
            elif z < -3:
                sd3neg = self._calculate_value_for_z_score(-3, lamb, mu, sigm)
                sd2neg = self._calculate_value_for_z_score(-2, lamb, mu, sigm)
                return -3 + ((y - sd3neg) / (sd2neg - sd3neg))

            return z

        z = calculate_z_score(y, lamb, mu, sigm)
        if -3 <= z <= 3:
            return z

        return fix_extremes(z)

    def _calculate_value_for_z_score(self, z: float, lamb: float, mu: float, sigm: float) -> float:
        # TODO: read literature to adapt logic for extremes

        if z > 3:
            sd3 = self._calculate_value_for_z_score(3, lamb, mu, sigm)
            sd2 = self._calculate_value_for_z_score(2, lamb, mu, sigm)
            return sd3 + (sd3 - sd2) * (z - 3)
        elif z < -3:
            sd3neg = self._calculate_value_for_z_score(-3, lamb, mu, sigm)
            sd2neg = self._calculate_value_for_z_score(-2, lamb, mu, sigm)
            return sd3neg + (sd2neg - sd3neg) * (z + 3)

        return calculate_value_for_z_score(z, lamb, mu, sigm)

    def _calculate_values_for_z_score_array(self, name: str, z: float) -> np.ndarray:
        data = self.get_table(name)

        return np.array([self._calculate_value_for_z_score(z, _l, _m, _s) for _l, _m, _s in zip(data["l"], data["m"], data["s"])])

    def _calculate_values_for_centile_array(self, name: str, centile: float) -> np.ndarray:
        """
        Calculate values for a given centile based on the LMS parameters of the specified table.

        :param name: The name of the table (e.g., "growth_stature").
        :param centile: The centile value to calculate (e.g., 0.5 for 50th centile).
        :return: A NumPy array of calculated values.
        """

        data = self.get_table(name)

        zscore = norm.ppf(centile).item()

        return np.array([calculate_value_for_z_score(zscore, _l, _m, _s) for _l, _m, _s in zip(data["l"], data["m"], data["s"])])


"""    
    # OLD
    def _get_table(self, measurement_type: str, newborn: bool = False, very_preterm: bool = False) -> str:
        if measurement_type in ["stature", "lfa", "hfa", "lhfa", "length", "height", "length_height"]:
            if newborn:
                return Tables.BIRTH_LENGTH
            elif very_preterm:
                return Tables.VERY_PRETERM_LENGTH
            return Tables.GROWTH_STATURE

        if measurement_type in ["w", "wfa", "weight"]:
            if newborn:
                return Tables.BIRTH_WEIGHT
            elif very_preterm:
                return Tables.VERY_PRETERM_WEIGHT
            return Tables.GROWTH_WEIGHT

        if measurement_type in ["hc", "hcfa", "head_circumference"]:
            if newborn:
                return Tables.BIRTH_HEAD_CIRCUMFERENCE
            elif very_preterm:
                return Tables.VERY_PRETERM_HEAD_CIRCUMFERENCE
            return Tables.GROWTH_HEAD_CIRCUMFERENCE

        if measurement_type in ["bmi", "body_mass_index"]:
            return Tables.GROWTH_BODY_MASS_INDEX

        if measurement_type in ["wlr", "weight_length", "weight_length_ratio"]:
            return Tables.GROWTH_WEIGHT_LENGTH

        if measurement_type in ["whr", "weight_height", "weight_height_ratio"]:
            return Tables.GROWTH_WEIGHT_HEIGHT

        if measurement_type in ["weight_velocity"]:
            return Tables.GROWTH_WEIGHT_VELOCITY

        if measurement_type in ["length_velocity"]:
            return Tables.GROWTH_LENGTH_VELOCITY

        if measurement_type in ["head_circumference_velocity"]:
            return Tables.GROWTH_CIRCUMFERENCE_VELOCITY

        raise ValueError(f"Unknown measurement type: {measurement_type}")
"""
