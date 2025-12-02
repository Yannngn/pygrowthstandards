import logging
import os

import pandas as pd

from pygrowthstandards.config import (
    MeasurementTypeType,
    validator,
)
from pygrowthstandards.config.development import DEVELOPMENT_GOALS
from pygrowthstandards.config.immunization import VACCINE_SCHEDULES
from pygrowthstandards.data.transform import GrowthData
from pygrowthstandards.oop.development import DevelopmentGoalGroup
from pygrowthstandards.oop.vaccination import VaccinationRecordGroup

from ..utils import stats
from ..utils.errors import NoReferenceDataException
from .measurement import Measurement, MeasurementGroup


class Calculator:
    """
    A class to perform calculations based on growth standards.
    """

    path = "data"

    def __init__(self):
        self.data = pd.read_parquet(os.path.join(self.path, f"pygrowthstandards_{GrowthData.version}.parquet"))

    def calculate_z_score(
        self,
        measurement_group: MeasurementGroup,
        measurement_type: MeasurementTypeType,
        age_in_days: int,
    ) -> float:
        value = getattr(measurement_group, measurement_type, None)
        if value is None:
            raise ValueError(f"MeasurementGroup with age {age_in_days} does not have data for '{measurement_type}'.")

        assert measurement_group.age_group is not None, "MeasurementGroup must have an age_group to calculate z-score."
        age_type = validator.get_age_type_from_age_group(measurement_group.age_group)
        assert age_type is not None, f"No valid age type found for age group '{measurement_group.age_group}'."

        filtered_data = self._filter_measurement_data(self.data, measurement_type, age_type, age_in_days)

        L, M, S = self._get_lms_params(filtered_data, age_in_days)

        return stats.calculate_z_score(value, L, M, S)

    def calculate_measurement_group(
        self,
        measurement_group: MeasurementGroup,
        age_in_days: int,
    ) -> MeasurementGroup:
        z_score_group = MeasurementGroup(date=measurement_group.date)
        z_score_group.age_group = measurement_group.age_group

        data = measurement_group.to_dict()

        for key, value in data.items():
            if value is None or key in ["date", "age_group"]:
                continue

            try:
                z_score = self.calculate_z_score(measurement_group, key, age_in_days)
                setattr(z_score_group, key, z_score)
            except NoReferenceDataException as e:
                logging.debug(f"Skipping {key} for date {measurement_group.date}: {e}")

        return z_score_group

    # Will not work because we condense data in MeasurementGroup in Patient class
    def _calculate_z_score(self, measurement: Measurement, age_in_days: int) -> float:
        if measurement.value is None:
            raise ValueError(f"Measurement with age {age_in_days} does not have a value.")

        assert measurement.age_group is not None, "Measurement must have an age_group to calculate z-score."
        age_type = validator.get_age_type_from_age_group(measurement.age_group)
        assert age_type is not None, f"No valid age type found for age group '{measurement.age_group}'."

        filtered_data = self._filter_measurement_data(self.data, measurement.measurement_type, age_type, age_in_days)

        L, M, S = self._get_lms_params(filtered_data, age_in_days)

        return stats.calculate_z_score(measurement.value, L, M, S)

    @staticmethod
    def _filter_measurement_data(data: pd.DataFrame, measurement_type: str, age_type: str, age_in_days: int) -> pd.DataFrame:
        filtered_data = data[(data["measurement_type"] == measurement_type) & (data["x_var_type"] == age_type)].copy()

        if filtered_data.empty:
            raise NoReferenceDataException(measurement_type, age_type, age_in_days)

        return filtered_data

    @staticmethod
    def _get_lms_params(fdata: pd.DataFrame, age_in_days: int) -> tuple[float, float, float]:
        if age_in_days not in fdata["x"].values:
            return stats.interpolate_lms(
                age_in_days,
                fdata["x"].to_numpy(),
                fdata["l"].to_numpy(),
                fdata["m"].to_numpy(),
                fdata["s"].to_numpy(),
            )
        else:
            # Use LMS directly
            row = fdata[fdata["x"] == age_in_days].iloc[0]

            return row["l"], row["m"], row["s"]


class DevelopmentCalculator:
    def __init__(self):
        self.data = DEVELOPMENT_GOALS

    def validate_measurement_group(self, development_goal_group: DevelopmentGoalGroup, age_in_days: int) -> None:
        development_goal_group.validate(age_in_days)


class ImmunizationCalculator:
    def __init__(self):
        self.data = VACCINE_SCHEDULES

    def validate(self, immunization: list[VaccinationRecordGroup], age_in_days: int): ...
