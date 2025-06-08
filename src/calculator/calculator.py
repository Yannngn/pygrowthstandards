import datetime
import os
import sys
from typing import Literal

import pandas as pd

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)


from src.calculator.handler import Handler
from src.calculator.kid import Kid
from src.calculator.measurement import Measurement
from src.calculator.plotter import Plotter
from src.calculator.table_data import TABLES, TableData
from src.utils.constants import YEAR
from src.utils.stats import calculate_z_score


class Calculator(Plotter, Handler):
    def __init__(self, kid: Kid):
        """
        Initializes a Calculator instance with a Kid object.

        :param kid: An instance of the Kid class.
        """
        self.kid = kid

        self._data = TableData(kid)
        self._measurements: list[Measurement] = []

    def calculate_measurement_zscore(self, measurement: Measurement):
        kid_age_days = self.kid.age_days(measurement.date)
        ga = (self.kid.gestational_age_weeks or 40) * 7 + (
            self.kid.gestational_age_days or 0
        )

        # Length/Height Z-score
        if measurement.length_height is not None:
            if kid_age_days == 0:
                table = "birth_length"
                age = ga
            else:
                table = "height" if kid_age_days > 2 * YEAR else "length"
                age = kid_age_days

            measurement.length_height_z = self._calculate_z_score(
                table, measurement.length_height, age
            )

        # Weight Z-score
        if measurement.weight is not None:
            table = "birth_weight" if kid_age_days == 0 else "weight"
            age = ga if kid_age_days == 0 else kid_age_days

            measurement.weight_z = self._calculate_z_score(
                table, measurement.weight, age
            )

        # Head Circumference Z-score
        if measurement.head_circumference is not None and kid_age_days <= 5 * YEAR:
            table = (
                "birth_head_circumference"
                if kid_age_days == 0
                else "head_circumference"
            )
            age = ga if kid_age_days == 0 else kid_age_days
            measurement.head_circumference_z = self._calculate_z_score(
                table, measurement.head_circumference, age
            )

        # BMI Z-score
        if measurement.bmi is not None and kid_age_days != 0:
            measurement.bmi_z = self._calculate_z_score(
                "bmi", measurement.bmi, kid_age_days
            )

    def _calculate_z_score(
        self,
        name: TABLES,
        value: float,
        age_days: int,
    ) -> float | None:
        lms = self._data.get_lms(name, age_days)

        return calculate_z_score(value, **lms)

    def _calculate(self, measurements: list[Measurement]):
        for measurement in measurements:
            self.calculate_measurement_zscore(measurement)

    def results(
        self,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> list[dict]:
        results = []
        measurements = self.get_measurements_by_date_range(start_date, end_date)

        self._calculate(measurements)

        for m in measurements:
            entry = {}
            mp = m.get_percentiles()
            # Length/height
            if m.length_height is not None:
                entry["length_height"] = {
                    "value": m.length_height,
                    "z": m.length_height_z,
                    "p": mp.get("length_height", None),
                }

            # Weight
            if m.weight is not None:
                entry["weight"] = {
                    "value": m.weight,
                    "z": m.weight_z,
                    "p": mp.get("weight", None),
                }

            # Head circumference
            if m.head_circumference is not None:
                entry["head_circumference"] = {
                    "value": m.head_circumference,
                    "z": m.head_circumference_z,
                    "p": mp.get("head_circumference", None),
                }

            # BMI
            if m.bmi is not None:
                entry["bmi"] = {
                    "value": m.bmi,
                    "z": m.bmi_z,
                    "p": mp.get("bmi", None),
                }

            results.append(entry)
        return results

    def display_results(
        self,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
    ) -> str:
        """
        Display the results of the measurements as a pandas DataFrame with MultiIndex columns and formatted floats.
        Adds measurement date and kid age (in days) to the columns.

        Args:
            start_date (datetime.date | None, optional): The start date for filtering measurements.
            end_date (datetime.date | None, optional): The end date for filtering measurements.

        Returns:
            str: String representation of the DataFrame.
        """

        results = self.results(start_date, end_date)

        if not results:
            return "No measurements found."

        # Flatten results for DataFrame with MultiIndex columns
        rows = []
        columns = set()
        subkey_order = ["value", "z", "p"]
        for idx, (result, measurement) in enumerate(
            zip(results, self.get_measurements_by_date_range(start_date, end_date)), 1
        ):
            row: dict = {("Idx", ""): idx}
            # Add measurement date and kid age (in days)
            row[("Date", "")] = measurement.date
            row[("Age (days)", "")] = self.kid.age_days(measurement.date)
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
        measurement_types = sorted(
            {
                mtype
                for mtype, _ in columns
                if mtype not in ["Idx", "Date", "Age (days)"]
            }
        )
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
        df[float_cols] = df[float_cols].map(
            lambda x: f"{x:.2f}" if pd.notnull(x) else pd.NA
        )

        pd.set_option("display.max_columns", None)
        # Use to_string with custom formatting for better visual separation
        return df.to_string(
            index=False,
            justify="center",
            col_space=6,
        )

    @classmethod
    def from_kid(
        cls,
        birthday_date: datetime.date,
        sex: Literal["M", "F", "U"] = "U",
        gestational_age_weeks: int | None = None,
        gestational_age_days: int | None = None,
    ) -> "Calculator":
        """
        Create a Calculator instance from basic kid information.

        Args:
            birthday_date (datetime.date): The child's date of birth.
            sex (Literal["M", "F", "U"], optional): The child's sex ("M", "F", or "U" for unknown). Defaults to "U".
            gestational_age_weeks (int | None, optional): Gestational age in weeks, if known.
            gestational_age_days (int | None, optional): Additional gestational age in days, if known.

        Returns:
            Calculator: A Calculator instance initialized with a Kid object.
        """
        return cls(
            Kid(
                birthday_date=birthday_date,
                sex=sex,
                gestational_age_weeks=gestational_age_weeks,
                gestational_age_days=gestational_age_days,
            )
        )

    def __str__(self):
        return f"Calculator(kid={self.kid}, measurements={len(self._measurements)})"
