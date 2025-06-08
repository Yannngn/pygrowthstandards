import datetime
import json
import os
import sys
from typing import Literal

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.calculator.kid import Kid
from src.utils.constants import YEAR
from src.utils.stats import interpolate_lms

TABLES = Literal[
    "bmi",
    "birth_head_circumference",
    "birth_length",
    "birth_weight",
    "head_circumference",
    "height",
    "length",
    "weight",
    "preterm_head_circumference",
    "preterm_length",
    "preterm_weight",
]

SD_KEYS = [
    "sd5neg",
    "sd4neg",
    "sd3neg",
    "sd2neg",
    "sd1neg",
    "sd0",
    "sd1",
    "sd2",
    "sd3",
    "sd4",
    "sd5",
]
PERC_KEYS = [
    "p01",
    "p1",
    "p3",
    "p5",
    "p10",
    "p25",
    "p50",
    "p75",
    "p90",
    "p95",
    "p97",
    "p99",
    "p999",
]


class TableData:
    def __init__(self, kid: Kid):
        """
        Initializes a TableData instance with age in days and preterm status.

        :param age_days: Age of the child in days.
        :param is_very_preterm: Boolean indicating if the child is very preterm.
        """
        self.kid = kid

        self._setup()

    def _setup(self):
        """Sets up the data for various anthropometric measurements based on the child's age and preterm status."""
        age = self.kid.age_days()

        if self.kid.is_very_preterm:
            self.preterm_head_circumference = self.read_data(
                "intergrowth_21st_very_preterm_growth_head_circumference_for_age.json"
            )
            self.preterm_length = self.read_data(
                "intergrowth_21st_very_preterm_growth_length_for_age.json"
            )
            self.preterm_weight = self.read_data(
                "intergrowth_21st_very_preterm_growth_weight_for_age.json"
            )

        self.birth_head_circumference = self.read_data(
            "intergrowth_21st_birth_size_head_circumference_for_gestational_age.json"
        )
        self.birth_length = self.read_data(
            "intergrowth_21st_birth_size_length_for_gestational_age.json"
        )
        self.birth_weight = self.read_data(
            "intergrowth_21st_birth_size_weight_for_gestational_age.json"
        )

        self.head_circumference = self.read_data(
            "who_growth_0_to_2_head_circumference_for_age.json"
        )
        self.length = self.read_data("who_growth_0_to_2_length_for_age.json")
        self.height = []
        self.weight = self.read_data("who_growth_0_to_2_weight_for_age.json")
        self.bmi = self.read_data("who_growth_0_to_2_body_mass_index_for_age.json")

        if age >= 2 * YEAR:
            self.head_circumference.extend(
                self.read_data("who_growth_2_to_5_head_circumference_for_age.json")
            )

            self.height.extend(self.read_data("who_growth_2_to_5_height_for_age.json"))
            self.weight.extend(self.read_data("who_growth_2_to_5_weight_for_age.json"))
            self.bmi.extend(
                self.read_data("who_growth_2_to_5_body_mass_index_for_age.json")
            )

        if age >= 5 * YEAR:
            self.height.extend(self.read_data("who_growth_5_to_10_height_for_age.json"))
            self.weight.extend(self.read_data("who_growth_5_to_10_weight_for_age.json"))
            self.bmi.extend(
                self.read_data("who_growth_5_to_10_body_mass_index_for_age.json")
            )

        if age >= 10 * YEAR:
            self.height.extend(
                self.read_data("who_growth_10_to_19_height_for_age.json")
            )
            self.bmi.extend(
                self.read_data("who_growth_10_to_19_body_mass_index_for_age.json")
            )

    def get_table_cutoffs(self, name: TABLES) -> tuple[datetime.date, datetime.date]:
        if name.startswith("birth"):
            return self.kid.birthday_date, self.kid.birthday_date

        if name.startswith("preterm"):
            return self.kid.birthday_date, self.kid.birthday_date + datetime.timedelta(
                days=64 * 7
            )

        if "length" in name:
            return (
                self.kid.birthday_date,
                self.kid.birthday_date + datetime.timedelta(days=2 * YEAR),
            )

        if "head_circumference" in name:
            return (
                self.kid.birthday_date,
                self.kid.birthday_date + datetime.timedelta(days=5 * YEAR),
            )

        if "weight" in name:
            return (
                self.kid.birthday_date,
                self.kid.birthday_date + datetime.timedelta(days=10 * YEAR),
            )

        if "height" in name:
            return (
                self.kid.birthday_date + datetime.timedelta(days=2 * YEAR),
                self.kid.birthday_date + datetime.timedelta(days=19 * YEAR),
            )

        if "bmi" in name:
            return (
                self.kid.birthday_date,
                self.kid.birthday_date + datetime.timedelta(days=19 * YEAR),
            )
        else:
            raise ValueError(f"Unknown table name: {name}")

    def get_measurement_label(self, name: TABLES) -> str:
        if name in ["birth_length", "preterm_length", "length", "height"]:
            return "length_height"
        elif name in ["birth_weight", "preterm_weight", "weight"]:
            return "weight"
        elif name in [
            "birth_head_circumference",
            "preterm_head_circumference",
            "head_circumference",
        ]:
            return "head_circumference"
        elif name == "bmi":
            return "bmi"
        else:
            raise ValueError(f"Unknown table name: {name}")

    def read_data(self, name: str) -> list[dict]:
        with open(os.path.join("data", name), "r") as f:
            dict_: dict = json.load(f)

        data = dict_.get("data", [])

        kid_sex = getattr(self.kid, "sex", "U")
        if kid_sex == "U":
            kid_sex = "F"

        data = [entry for entry in data if entry.get("sex") == kid_sex]

        return data

    def get_lms(self, name: TABLES, age_days: int) -> dict:
        """
        Retrieve z-score data for a specified anthropometric measurement.

        Depending on the measurement name and whether the child is very preterm,
        returns the corresponding list of dictionaries containing z-score data.

        Parameters:
            name (str): The name of the measurement.
                Accepted values are:
                    - "length": Returns preterm or standard length data.
                    - "weight": Returns preterm or standard weight data.
                    - "head_circumference": Returns preterm or standard head circumference data.
                    - "bmi": Returns BMI data.
                    - "height": Returns height data.

        Returns:
            list[dict]: A list of dictionaries containing z-score data for the specified measurement.

        Raises:
            ValueError: If the provided name does not match any known measurement.
        """
        zscores = getattr(self, name, None)

        if zscores is None:
            raise ValueError(f"Unknown measurement name: {name}")

        age_key = "age" if "age" in zscores[0] else "gestational_age"

        # Find the z-score entry where 'age' matches 'age_days'
        entry = next((item for item in zscores if item.get(age_key) == age_days), None)

        if entry is None:
            # Interpolate LMS parameters if exact age_days not found
            entry = interpolate_lms(zscores, age_days)

            if entry is None:
                raise ValueError("No data available for the specified age.")

            return entry

        return {k: entry[k] for k in ["l", "m", "s"]}

    def get_plot_data(
        self, name: TABLES, zscores: bool = True
    ) -> tuple[list, dict[str, list]]:
        """
        Prepare data for plotting based on the specified measurement name.

        Depending on the measurement name, returns two lists:
        - x-axis values (age in days)
        - y-axis values (z-scores or raw values)

        Parameters:
            name (str): The name of the measurement.
                Accepted values are:
                    - "length"
                    - "weight"
                    - "head_circumference"
                    - "bmi"
                    - "height"
            zscores (bool): If True, returns z-scores; otherwise, returns raw values.

        Returns:
            tuple[list, list]: Two lists containing x and y values for plotting.
        """
        data = getattr(self, name, None)

        if data is None:
            raise ValueError(f"Unknown measurement name: {name}")

        age_key = (
            "gestational_age"
            if name in ["birth_length", "birth_weight", "birth_head_circumference"]
            else "age"
        )

        x = [entry[age_key] for entry in data]
        y = {}

        if zscores:

            for key in SD_KEYS:
                if key not in data[0]:
                    continue
                y[key] = [entry[key] for entry in data]
            return x, y

        for key in PERC_KEYS:
            if key not in data[0]:
                continue
            y[key] = [entry[key] for entry in data]

        return x, y
