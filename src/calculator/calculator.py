import datetime
import os
import sys
from typing import Literal

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from src.calculator.child import Child
from src.calculator.handler import Handler
from src.calculator.measurement import Measurement
from src.calculator.plotter import Plotter
from src.calculator.table_data import TableData


class Calculator(Plotter, Handler):
    def __init__(self, child: Child):
        """Initializes a Calculator instance with a child object.

        Args:
            child: An instance of the Child class.
        """
        self.child = child

        self._data = TableData(child.sex)
        self._measurements: list[Measurement] = []

    def calculate_measurement_z_score(self, measurement: Measurement) -> None:
        """Calculates and sets z-scores for all measurement types in a Measurement instance.

        Args:
            measurement: The measurement instance to calculate z-scores for.

        Raises:
            ValueError: If gestational age is required but not set for newborn measurements.
        """
        child_age_days = self.child.age(measurement.date).days

        newborn = child_age_days == 0

        if newborn:
            if self.child.gestational_age is None:
                raise ValueError("Gestational age is required for newborn measurements. Use child.set_gestational_age() to set it.")

            child_age_days = self.child.gestational_age.days

        very_preterm = self.child.is_very_preterm is True

        age_group = self._data.get_age_group(child_age_days, newborn, very_preterm)

        for measurement_type in ["stature", "weight", "head_circumference", "body_mass_index"]:
            try:
                z_score = self.calculate_z_score(measurement_type, age_group, child_age_days, getattr(measurement, measurement_type))
                setattr(measurement, f"{measurement_type}_z", z_score)
            except ValueError as e:
                print(f"Error calculating z-score for {measurement_type} on {measurement.date}: {e}")
                continue

    def get_measurements_by_age_group(self, age_group: str = "none") -> list[Measurement]:
        """Retrieves measurements within a specific age group.

        Args:
            age_group: The age group to filter by (e.g., "0-2", "newborn", "very_preterm").
                Defaults to "none" which returns all measurements.

        Returns:
            A list of Measurement instances within the specified age group.

        Raises:
            ValueError: If gestational age is required but not set for newborn or very_preterm groups.
        """
        min_age, max_age = self._get_age_limits(age_group)
        if age_group in ["newborn", "very_preterm"]:
            if self.child.gestational_age is None:
                raise ValueError("Gestational age is required for newborn measurements. Use child.set_gestational_age() to set it.")
            return [m for m in self._measurements if min_age <= self.child.gestational_age.days <= max_age]

        return [m for m in self._measurements if min_age <= self.child.age(m.date).days <= max_age]

    def results(self, age_group: str = "none") -> list[dict]:
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
            self.calculate_measurement_z_score(measurement)

        for m in measurements:
            entry = {}
            for measurement_name in ["stature", "weight", "head_circumference", "body_mass_index"]:
                entry[measurement_name] = {"value": getattr(m, measurement_name), "z": getattr(m, f"{measurement_name}_z")}

            results.append(entry)

        return results

    def display_results(self, age_group: str = "none") -> str:
        """Displays measurement results as a formatted pandas DataFrame string.

        Args:
            age_group: The age group to filter by. Defaults to "none" for all measurements.

        Returns:
            A string representation of the DataFrame with measurement results,
            or "No measurements found." if no measurements exist.
        """

        results = self.results(age_group)
        if not results:
            return "No measurements found."

        # Flatten results for DataFrame with MultiIndex columns
        rows = []
        columns = set()
        subkey_order = ["value", "z"]
        for idx, (result, measurement) in enumerate(zip(results, self.get_measurements_by_age_group(age_group)), 1):
            row: dict = {("Idx", ""): idx}
            # Add measurement date and child age (in days)
            row[("Date", "")] = measurement.date
            row[("Age (days)", "")] = self.child.age(measurement.date).days
            columns.add(("Date", ""))
            columns.add(("Age (days)", ""))
            for mtype, mvals in result.items():
                for subkey in subkey_order:
                    if subkey not in mvals:
                        continue
                    row[(mtype, subkey)] = mvals[subkey]
                    columns.add((mtype, subkey))
            rows.append(row)

        # Ensure consistent column order: Idx, Date, Age (days), then each measurement type with subkeys in order
        measurement_types = sorted({mtype for mtype, _ in columns if mtype not in ["Idx", "Date", "Age (days)"]})
        ordered_columns = [("Idx", ""), ("Date", ""), ("Age (days)", "")]
        for mtype in measurement_types:
            for subkey in subkey_order:
                if (mtype, subkey) not in columns:
                    continue
                ordered_columns.append((mtype, subkey))

        df = pd.DataFrame(rows)
        df = df.reindex(columns=ordered_columns)
        df.columns = pd.MultiIndex.from_tuples(df.columns)  # type: ignore

        # Format float columns to 2 decimal places
        float_cols = df.select_dtypes(include="float").columns
        df[float_cols] = df[float_cols].map(lambda x: f"{x:.2f}" if pd.notnull(x) else pd.NA)

        pd.set_option("display.max_columns", None)
        # Use to_string with custom formatting for better visual separation
        return df.to_string(index=False, justify="center", col_space=6)

    def calculate_z_score(self, measurement_type: str, age_group: str, x: int | float, y: float) -> float:
        """Calculates the z-score for a given measurement value.

        Args:
            measurement_type: The type of measurement (e.g., "stature", "weight").
            age_group: The age group for selecting the appropriate growth table.
            x: The x value (typically age in days).
            y: The measurement value to calculate z-score for.

        Returns:
            The calculated z-score.
        """
        name = self._data.get_table_name(measurement_type, age_group)

        return self._data._calculate_z_score(y, *self._data.get_lms(name, x))

    def calculate_value_for_z_score(self, measurement_type: str, age_group: str, x: int | float, z_score: float) -> float:
        """Calculates the measurement value for a given z-score.

        Args:
            measurement_type: The type of measurement (e.g., "stature", "weight").
            age_group: The age group for selecting the appropriate growth table.
            x: The x value (typically age in days).
            z_score: The z-score to calculate the value for.

        Returns:
            The calculated measurement value.
        """
        name = self._data.get_table_name(measurement_type, age_group)

        return self._data._calculate_value_for_z_score(z_score, *self._data.get_lms(name, x))

    @classmethod
    def from_child(
        cls,
        birthday_date: datetime.date,
        sex: Literal["M", "F", "U"] = "U",
        gestational_age_weeks: int | None = None,
        gestational_age_days: int | None = None,
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
        return cls(
            Child(
                birthday_date=birthday_date,
                sex=sex,
                gestational_age_weeks=gestational_age_weeks,
                gestational_age_days=gestational_age_days,
            )
        )

    def __str__(self) -> str:
        """Returns a string representation of the Calculator instance.

        Returns:
            A string containing child information and measurement count.
        """
        return f"Calculator(child={self.child}, measurements={len(self._measurements)})"
