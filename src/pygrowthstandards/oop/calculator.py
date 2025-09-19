import logging
import os

import pandas as pd

from pygrowthstandards.config import ChoiceValidator, MeasurementTypeType
from pygrowthstandards.data.transform import GrowthData

from ..utils import stats
from ..utils.errors import NoReferenceDataException
from .measurement import MeasurementGroup


class Calculator:
    """
    A class to perform calculations based on growth standards.
    """

    path = "data"

    def __init__(self):
        self.data = pd.read_parquet(
            os.path.join(self.path, f"pygrowthstandards_{GrowthData.version}.parquet")
        )

    def calculate_z_score(
        self,
        measurement_group: MeasurementGroup,
        measurement_type: MeasurementTypeType,
        age_value: int,
    ) -> float:
        value = getattr(measurement_group, measurement_type, None)
        if value is None:
            raise ValueError(
                f"MeasurementGroup with age {age_value} does not have data for '{measurement_type}'."
            )

        assert measurement_group.age_group is not None, (
            "MeasurementGroup must have an age_group to calculate z-score."
        )
        age_type = ChoiceValidator.get_age_type_from_age_group(
            measurement_group.age_group
        )
        assert age_type is not None, (
            f"No valid age type found for age group '{measurement_group.age_group}'."
        )

        filtered_data = self._filter_measurement_data(
            self.data, measurement_type, age_type, age_value
        )

        L, M, S = self._get_lms_params(filtered_data, age_value)

        return stats.calculate_z_score(value, L, M, S)

    def calculate_measurement_group(
        self,
        measurement_group: MeasurementGroup,
        age_value: int,
    ) -> MeasurementGroup:
        z_score_group = MeasurementGroup(date=measurement_group.date)
        z_score_group.age_group = measurement_group.age_group

        data = measurement_group.to_dict()

        for key, value in data.items():
            if value is None or key in ["date", "age_group"]:
                continue

            try:
                z_score = self.calculate_z_score(measurement_group, key, age_value)
                setattr(z_score_group, key, z_score)
            except NoReferenceDataException as e:
                logging.debug(f"Skipping {key} for date {measurement_group.date}: {e}")

        return z_score_group

    @staticmethod
    def _filter_measurement_data(
        data: pd.DataFrame, measurement_type: str, age_type: str, age_value: int
    ) -> pd.DataFrame:
        filtered_data = data[
            (data["measurement_type"] == measurement_type)
            & (data["x_var_type"] == age_type)
        ].copy()

        if filtered_data.empty:
            raise NoReferenceDataException(measurement_type, age_type, age_value)

        return filtered_data

    @staticmethod
    def _get_lms_params(
        fdata: pd.DataFrame, age_value: int
    ) -> tuple[float, float, float]:
        if age_value not in fdata["x"].values:
            return stats.interpolate_lms(
                age_value,
                fdata["x"].to_numpy(),
                fdata["l"].to_numpy(),
                fdata["m"].to_numpy(),
                fdata["s"].to_numpy(),
            )
        else:
            # Use LMS directly
            row = fdata[fdata["x"] == age_value].iloc[0]

            return row["l"], row["m"], row["s"]
