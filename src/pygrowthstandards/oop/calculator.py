import logging
from typing import cast

import pandas as pd

from pygrowthstandards.data.load import KeyObject, load_reference
from pygrowthstandards.functional.data import get_lms, get_table
from pygrowthstandards.oop.measurement import MeasurementGroup
from pygrowthstandards.utils import stats
from pygrowthstandards.config.growth import DataSexType, MeasurementAliasType
from pygrowthstandards.utils.errors import InvalidChoicesError, NoReferenceDataException


class Calculator:
    """
    A class to perform calculations based on growth standards.
    """

    def __init__(self):
        try:
            self.data = load_reference()
        except FileNotFoundError as exc:
            logging.error(str(exc))
            self.data = None

    def calculate_z_score(
        self,
        measurement_group: MeasurementGroup,
        measurement_type: MeasurementAliasType,
        sex: DataSexType,
        age_days: int | None = None,
        gestational_age: int | None = None,
    ) -> float:
        value = getattr(measurement_group, measurement_type, None)
        if value is None:
            raise ValueError(f"MeasurementGroup is missing data for '{measurement_type}'.")

        if not isinstance(self.data, pd.DataFrame):
            age_value = age_days if age_days is not None else (gestational_age if gestational_age is not None else -1)
            raise NoReferenceDataException(measurement_type, "reference_data", age_value)

        try:
            keys = KeyObject.from_functional(
                measurement=measurement_type,
                sex=sex,
                age_days=age_days,
                gestational_age=gestational_age,
            )
        except ValueError as exc:
            age_value = age_days if age_days is not None else (gestational_age if gestational_age is not None else -1)
            raise NoReferenceDataException(measurement_type, "age", age_value) from exc
        if keys.x is None:
            age_value = age_days if age_days is not None else (gestational_age if gestational_age is not None else -1)
            raise NoReferenceDataException(measurement_type, "age", age_value)
        table = get_table(self.data, keys=keys)
        lms = get_lms(table, keys.x)

        return stats.calculate_z_score(value, *lms)

    def calculate_measurement_group(
        self,
        measurement_group: MeasurementGroup,
        sex: DataSexType,
        age_days: int | None = None,
        gestational_age: int | None = None,
    ) -> MeasurementGroup:
        z_score_group = MeasurementGroup(table_name=measurement_group.table_name, date=measurement_group.date)

        data = measurement_group.to_dict()

        for key, value in data.items():
            if value is None or key in ["date", "table_name"]:
                continue

            try:
                z_score = self.calculate_z_score(
                    measurement_group,
                    cast(MeasurementAliasType, key),
                    sex,
                    age_days=age_days,
                    gestational_age=gestational_age,
                )
                setattr(z_score_group, key, z_score)
            except (InvalidChoicesError, NoReferenceDataException) as e:
                logging.debug(f"Skipping {key} for date {measurement_group.date}: {e}")

        return z_score_group
