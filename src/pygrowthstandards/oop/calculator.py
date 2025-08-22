import logging
import os

import pandas as pd

from ..utils import stats
from ..utils.errors import NoReferenceDataException
from .measurement import MeasurementGroup


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
        "child_growth": "age",
        "growth": "age",
    }

    def __init__(self):
        self.data = pd.read_parquet(os.path.join(self.path, f"pygrowthstandards_{self.version}.parquet"))

    def calculate_z_score(self, measurement_group: MeasurementGroup, measurement_type: str, age_value: int) -> float:
        value = getattr(measurement_group, measurement_type, None)
        if value is None:
            raise ValueError(f"MeasurementGroup with age {age_value} does not have data for '{measurement_type}'.")

        age_type = self.x_var_types[measurement_group.table_name]

        filtered_data = self._filter_measurement_data(self.data, measurement_type, age_type, age_value)
        L, M, S = self._get_lms_params(filtered_data, age_value)

        return stats.calculate_z_score(value, L, M, S)

    def calculate_measurement_group(
        self,
        measurement_group: MeasurementGroup,
        age_value: int,
    ) -> MeasurementGroup:
        z_score_group = MeasurementGroup(table_name=measurement_group.table_name, date=measurement_group.date)

        data = measurement_group.to_dict()

        for key, value in data.items():
            if value is None or key in ["date", "table_name"]:
                continue

            try:
                z_score = self.calculate_z_score(measurement_group, key, age_value)
                setattr(z_score_group, key, z_score)
            except NoReferenceDataException as e:
                logging.debug(f"Skipping {key} for date {measurement_group.date}: {e}")

        return z_score_group

    @staticmethod
    def _filter_measurement_data(data: pd.DataFrame, measurement_type: str, age_type: str, age_value: int) -> pd.DataFrame:
        filtered_data = data[(data["measurement_type"] == measurement_type) & (data["x_var_type"] == age_type)].copy()

        if filtered_data.empty:
            raise NoReferenceDataException(measurement_type, age_type, age_value)

        return filtered_data

    @staticmethod
    def _get_lms_params(fdata: pd.DataFrame, age_value: int) -> tuple[float, float, float]:
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
