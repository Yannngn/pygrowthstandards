import datetime
import os
import sys
from typing import Any, Collection, Literal

import numpy as np

from src.utils.choices import AGE_GROUP_TYPE, MEASUREMENT_TYPE_CHOICES

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from src.calculator.child import Child
from src.calculator.computer import Computer
from src.calculator.measurement import Measurement
from src.calculator.mixins import HandlerMixin
from src.calculator.plotter import Plotter
from src.utils.results import str_dataframe


class Calculator(Computer, Plotter, HandlerMixin):
    def __init__(self, child: Child, measurements: list[Measurement] | None = None):
        super().__init__(child)

        self._measurements: list[Measurement] = []

        if measurements:
            self.add_measurement_objects(measurements)

    def results(self, age_group: str = "all") -> list[dict]:
        """Calculates and returns measurement results with z-scores for a specific age group.

        Args:
            age_group: The age group to filter by. Defaults to "none" for all measurements.

        Returns:
            A list of dictionaries containing measurement values and z-scores.
            Each dict has measurement types as keys with "value" and "z" subkeys.
        """
        results = []
        measurements = self.get_measurements_by_age_group(age_group)
        for measurement in measurements:
            self.compute_measurement(measurement)

        for m in measurements:
            entry = {}
            values = m.values
            z_scores = m.z_scores
            for measurement_name in MEASUREMENT_TYPE_CHOICES:
                if measurement_name not in values:
                    continue

                entry[measurement_name] = {"value": values.get(measurement_name), "z": z_scores.get(measurement_name)}

            results.append(entry)

        return results

    def display_results(self, age_group: str = "all") -> str:
        """Displays measurement results as a formatted pandas DataFrame string.

        Args:
            age_group: The age group to filter by. Defaults to "all" for all measurements.

        Returns:
            A string representation of the DataFrame with measurement results,
            or "No measurements found." if no measurements exist.
        """

        results = self.results(age_group)
        if not results:
            return "No measurements found."

        date_list = [measurement.date for measurement in self.get_measurements_by_age_group(age_group)]
        age_list = [self.child.age(date).days for date in date_list]

        return str_dataframe(results, date_list, age_list)

    def get_plot_data(
        self,
        age_group: AGE_GROUP_TYPE,
        measurement_type: str,
        unit_type: str = "age",
        user_data: bool = True,
        percentiles_or_zscores: Collection[int | float] = [-3, -2, 0, 2, 3],
    ) -> dict[Any, np.ndarray]:
        """
        Returns a dictionary with x values and corresponding y values for the specified table and zscores or centiles.
        :param measurement_type: The measurement_type of the table (e.g., "stature").
        :param values: A list of zscores or centiles to plot.
        :return: A dictionary with x values and corresponding y values.
        """
        data = self._data.get_plot_table(age_group, measurement_type, self.child.sex, unit_type)

        plot_data: dict = {"x": data.x}

        for value in percentiles_or_zscores:
            if isinstance(value, float):
                assert 0 < value < 1, "Centile values must be between 0 and 1."
                plot_data[value] = self._numpy_compute_values_for_centile(data, value)
                continue

            plot_data[value] = self._numpy_compute_values_for_z_score(data, value)

        if not user_data:
            return plot_data

        measurements = self.get_measurements_by_age_group(age_group)

        if not measurements:
            raise ValueError(f"No measurements found for age group '{age_group}'.")

        user_x = [self.child.age(m.date).days for m in measurements]
        user_y = [m.values[measurement_type] for m in measurements if hasattr(m.values, measurement_type)]

        values_x = plot_data.pop("x")
        all_x = sorted(set(values_x).union(user_x))

        def align_to_all_x(x_list, y_list):
            x_to_y = dict(zip(x_list, y_list))
            return np.array([x_to_y.get(x, None) for x in all_x])

        aligned_values = {"x": np.array(all_x)}
        for k, v in plot_data.items():
            aligned_values[k] = align_to_all_x(values_x, v)

        aligned_values["user"] = align_to_all_x(user_x, user_y)

        return aligned_values

    @classmethod
    def from_child(
        cls,
        birthday_date: datetime.date,
        sex: Literal["M", "F", "U"] = "U",
        gestational_age_weeks: int = 40,
        gestational_age_days: int = 0,
    ) -> "Calculator":
        """Creates a Calculator instance from basic child information.

        Args:
            birthday_date: The child's date of birth.
            sex: The child's sex ("M", "F", or "U" for unknown). Defaults to "U".
            gestational_age_weeks: Gestational age in weeks, if known.
            gestational_age_days: Additional gestational age in days, if known.

        Returns:
            A Calculator instance initialized with a Child object.
        """

        child = Child(
            birthday_date=birthday_date,
            sex=sex,
            gestational_age_weeks=gestational_age_weeks,
            gestational_age_days=gestational_age_days,
        )

        return cls(child=child, measurements=[])

    def __str__(self) -> str:
        """Returns a string representation of the Calculator instance.

        Returns:
            A string containing child information and measurement count.
        """
        return f"Calculator(child={self.child}, measurements={len(self._measurements)})"
