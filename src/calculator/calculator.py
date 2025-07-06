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
        """
        Initializes a Calculator instance with a child object.

        :param child: An instance of the child class.
        """
        self.child = child

        self._data = TableData(child.sex)
        self._measurements: list[Measurement] = []

    def calculate_measurement_zscore(self, measurement: Measurement):
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
        """
        Retrieve measurements within a specific age range.

        Args:
            age_limits (tuple[int, int] | None): A tuple containing the minimum and maximum age in months.
                If None, returns all measurements.

        Returns:
            list[Measurement]: A list of Measurement instances within the specified age range.
        """
        min_age, max_age = self._get_age_limits(age_group)
        if age_group in ["newborn", "very_preterm"]:
            assert self.child.gestational_age is not None, "Gestational age must be set for newborn or very preterm measurements."
            return [m for m in self._measurements if min_age <= self.child.gestational_age.days <= max_age]

        return [m for m in self._measurements if min_age <= self.child.age(m.date).days <= max_age]

    def results(self, age_group: str = "none") -> list[dict]:
        results = []
        measurements = self.get_measurements_by_age_group(age_group)
        self._calculate_all(measurements)

        for m in measurements:
            entry = {}
            for measurement_name in ["stature", "weight", "head_circumference", "body_mass_index"]:
                entry[measurement_name] = {"value": getattr(m, measurement_name), "z": getattr(m, f"{measurement_name}_z")}

            results.append(entry)

        return results

    def display_results(self, age_group: str = "none") -> str:
        """
        Display the results of the measurements as a pandas DataFrame with MultiIndex columns and formatted floats.
        Adds measurement date and child age (in days) to the columns.

        Args:
            start_date (datetime.date | None, optional): The start date for filtering measurements.
            end_date (datetime.date | None, optional): The end date for filtering measurements.

        Returns:
            str: String representation of the DataFrame.
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

    @classmethod
    def from_child(
        cls,
        birthday_date: datetime.date,
        sex: Literal["M", "F", "U"] = "U",
        gestational_age_weeks: int | None = None,
        gestational_age_days: int | None = None,
    ) -> "Calculator":
        """
        Create a Calculator instance from basic child information.

        Args:
            birthday_date (datetime.date): The child's date of birth.
            sex (Literal["M", "F", "U"], optional): The child's sex ("M", "F", or "U" for unknown). Defaults to "U".
            gestational_age_weeks (int | None, optional): Gestational age in weeks, if known.
            gestational_age_days (int | None, optional): Additional gestational age in days, if known.

        Returns:
            Calculator: A Calculator instance initialized with a child object.
        """
        return cls(
            Child(
                birthday_date=birthday_date,
                sex=sex,
                gestational_age_weeks=gestational_age_weeks,
                gestational_age_days=gestational_age_days,
            )
        )

    def calculate_z_score(self, measurement_type: str, age_group: str, x: int | float, y: float) -> float:
        name = self._data.get_table_name(measurement_type, age_group)

        return self._data._calculate_z_score(y, *self._data.get_lms(name, x))

    def calculate_value_for_z_score(self, measurement_type: str, age_group: str, x: int | float, zscore: float) -> float:
        """
        Calculate the value for a given z-score based on the LMS parameters of the specified table.

        :param name: The name of the table (e.g., "who_growth_stature").
        :param x: The x value (e.g., age in months).
        :param zscore: The z-score to calculate the value for.
        :return: The calculated value.
        """
        name = self._data.get_table_name(measurement_type, age_group)

        return self._data._calculate_value_for_z_score(zscore, *self._data.get_lms(name, x))

    def _calculate_all(self, measurements: list[Measurement]):
        for measurement in measurements:
            self.calculate_measurement_zscore(measurement)

    def __str__(self):
        return f"Calculator(child={self.child}, measurements={len(self._measurements)})"
