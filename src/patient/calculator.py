import datetime
import logging
import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from src.patient.measurement import MeasurementGroup, TableNames
from src.patient.patient import Patient
from src.utils import stats
from src.utils.errors import NoReferenceDataException


class Calculator:
    """
    A class to perform calculations based on growth standards.
    """

    path = "data"
    version = "0.1.0"

    x_var_types = {
        "very_preterm_newborn": "gestational_age",
        "newborn": "gestational_age",
        "very_preterm_growth": "gestational_age",
        "growth": "age",
        "child_growth": "age",
    }

    def __init__(self, patient: Patient):
        """
        Initializes the Calculator with a Patient object.

        :param patient: An instance of the Patient class.
        """
        self.patient = patient
        self.data = pd.read_parquet(os.path.join(self.path, f"pygrowthstandards_{self.version}.parquet"))

    def calculate_all(self):
        """
        Calculates all measurements for the patient and updates the patient's z_scores.
        """
        self.patient.z_scores = self.calculate_measurements()

    def calculate_z_score(self, table_name: TableNames, measurement_type: str, date: datetime.date | None = None):
        """
        Calculates the z-score for a specific measurement type on a given date.

        :param measurement_type: The type of measurement (e.g., stature, weight).
        :param date: The date for which to calculate the z-score. Defaults to today.
        :return: The z-score as a float.
        """
        if date is None:
            date = datetime.date.today()

        value = self._validate_and_get_measurement(measurement_type, date)

        age_type = self.x_var_types[table_name]
        age_value = self.patient.get_age(age_type, date)

        filtered_data = self._filter_measurement_data(self.data, measurement_type, age_type, age_value)
        L, M, S = self._get_lms_params(filtered_data, age_value)

        return stats.calculate_z_score(value, L, M, S)

    def calculate_measurement_group(self, date: datetime.date | None = None) -> MeasurementGroup:
        """
        Calculates a MeasurementGroup for the patient on a specific date.

        :param date: The date for which to calculate the measurement group. Defaults to today.
        :return: A MeasurementGroup object containing the calculated measurements.
        """
        if date is None:
            date = datetime.date.today()

        measurement_group = next((mg for mg in self.patient.measurements if getattr(mg, "date", None) == date), None)

        if measurement_group is None:
            raise ValueError(f"No measurements found for patient on date {date}.")

        table_name = self.patient.measurements[0].table_name
        z_score_group = MeasurementGroup(table_name=table_name, date=date)

        data = measurement_group.to_dict()

        for key, value in data.items():
            if value is None or key == "date":
                continue

            try:
                z_score = self.calculate_z_score(table_name, key, date)
                setattr(z_score_group, key, z_score)
            except NoReferenceDataException as e:
                logging.debug(f"Skipping {key} for date {date}: {e}")

        return z_score_group

    def calculate_measurements(self) -> list[MeasurementGroup]:
        """
        Calculates all measurements for the patient based on their data.

        :return: A list of MeasurementGroup objects containing the calculated measurements.
        """
        z_scores = []
        for measurement in self.patient.measurements:
            z_scores.append(self.calculate_measurement_group(measurement.date))

        return z_scores

    def _validate_and_get_measurement(self, measurement_type, date):
        # Search for MeasurementGroup with the given date
        measurement_group = next((mg for mg in self.patient.measurements if getattr(mg, "date", None) == date), None)

        if measurement_group is None:
            raise ValueError(f"No MeasurementGroup found for patient on date {date}.")

        # Check if MeasurementGroup has the measurement type data
        value = getattr(measurement_group, measurement_type, None)
        if value is None:
            raise ValueError(f"MeasurementGroup on date {date} does not have data for '{measurement_type}'.")

        return value

    @staticmethod
    def _filter_measurement_data(data: pd.DataFrame, measurement_type: str, age_type: str, age_value: int) -> pd.DataFrame:
        filtered_data = data[(data["measurement_type"] == measurement_type) & (data["x_var_type"] == age_type)].copy()

        if filtered_data.empty:
            raise NoReferenceDataException(measurement_type, age_type, age_value)

        return filtered_data

    @staticmethod
    def _get_lms_params(fdata: pd.DataFrame, age_value: int) -> tuple[float, float, float]:
        if age_value not in fdata["x"].values:
            return stats.interpolate_lms(age_value, fdata["x"].to_numpy(), fdata["l"].to_numpy(), fdata["m"].to_numpy(), fdata["s"].to_numpy())
        else:
            # Use LMS directly
            row = fdata[fdata["x"] == age_value].iloc[0]

            return row["l"], row["m"], row["s"]
