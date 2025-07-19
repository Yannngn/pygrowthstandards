import os
import sys
from functools import partial

import numpy as np
from scipy.stats import norm

from src.utils.choices import (
    AGE_GROUP_TYPE,
    MEASUREMENT_TYPE_CHOICES,
    MEASUREMENT_TYPE_TYPE,
    TABLE_NAME_TYPE,
    PlotAgeValues,
)
from src.utils.errors import InvalidKeyPairError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.calculator.child import Child
from src.calculator.measurement import Measurement
from src.calculator.mixins import HandlerMixin
from src.calculator.table_data import TableData
from src.utils.stats import calculate_value_for_z_score, calculate_z_score


class Computer(HandlerMixin):
    def __init__(self, child: Child):
        """Initializes a Computer instance with a child object.

        Args:
            child: An instance of the Child class.
        """
        self.child = child
        self._data = TableData(child.sex, child.age().days, child.is_very_preterm)

    def compute_measurement(self, measurement: Measurement) -> None:
        """Calculates and sets z-scores for all measurement types in a Measurement instance.

        Args:
            measurement: The measurement instance to calculate z-scores for.

        Raises:
            ValueError: If gestational age is required but not set for newborn measurements.
        """

        measurement_age_days = self.child.age(measurement.date).days

        for measurement_type in MEASUREMENT_TYPE_CHOICES:
            measurement_age_days = self.child.age(measurement.date).days
            table = self._get_table_name(measurement_age_days)
            try:
                measurement.compute_z_scores(partial(self.compute_z_score, x=measurement_age_days, measurement_type=measurement_type, table=table))  # type: ignore
            except InvalidKeyPairError:
                continue
            except ValueError:
                continue

    def compute_z_score(
        self, x: int | float, y: float, measurement_type: MEASUREMENT_TYPE_TYPE, table: TABLE_NAME_TYPE = "growth", unit_type: str = "age"
    ) -> float:
        data = self._data.get_table(table, measurement_type, self.child.sex, unit_type)

        return self._compute_z_score(float(y), *data.get_point(x))

    def compute_value_for_z_score(
        self, x: int | float, z_score: float, measurement_type: MEASUREMENT_TYPE_TYPE, table: TABLE_NAME_TYPE = "growth", unit_type: str = "age"
    ) -> float:
        data = self._data.get_table(table, measurement_type, self.child.sex, unit_type)

        return self._compute_value_for_z_score(z_score, *data.get_point(x))

    def _compute_z_score(self, y: float, lamb: float, mu: float, sigm: float) -> float:
        def fix_extremes(z: float) -> float:
            """
            Fixes extreme z-scores by adjusting them based on the calculated values for z-scores of -3 and 3.
            This is to ensure that extreme values do not skew the results.
            # https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/computation.pdf
            """

            if lamb == 1:
                return z

            if z > 3:
                sd3 = self._compute_value_for_z_score(3, lamb, mu, sigm)
                sd2 = self._compute_value_for_z_score(2, lamb, mu, sigm)
                return 3 + ((y - sd3) / (sd3 - sd2))
            elif z < -3:
                sd3neg = self._compute_value_for_z_score(-3, lamb, mu, sigm)
                sd2neg = self._compute_value_for_z_score(-2, lamb, mu, sigm)
                return -3 + ((y - sd3neg) / (sd2neg - sd3neg))

            return z

        z = calculate_z_score(y, lamb, mu, sigm)
        if -3 <= z <= 3:
            return z

        return fix_extremes(z)

    def _compute_value_for_z_score(self, z_score: float, lamb: float, mu: float, sigm: float) -> float:
        # TODO: read literature to fix logic for extremes

        if z_score > 3:
            sd3 = self._compute_value_for_z_score(3, lamb, mu, sigm)
            sd2 = self._compute_value_for_z_score(2, lamb, mu, sigm)
            return sd3 + (sd3 - sd2) * (z_score - 3)
        elif z_score < -3:
            sd3neg = self._compute_value_for_z_score(-3, lamb, mu, sigm)
            sd2neg = self._compute_value_for_z_score(-2, lamb, mu, sigm)
            return sd3neg + (sd2neg - sd3neg) * (z_score + 3)

        return calculate_value_for_z_score(z_score, lamb, mu, sigm)

    def _numpy_compute_values_for_z_score(self, data, z: float) -> np.ndarray:
        L, M, S = data.L, data.M, data.S
        return np.array([self._compute_value_for_z_score(z, _l, _m, _s) for _l, _m, _s in zip(L, M, S)])

    def _numpy_compute_values_for_centile(self, data, centile: float) -> np.ndarray:
        """
        Calculate values for a given centile based on the LMS parameters of the specified table.

        :param name: The name of the table (e.g., "growth_stature").
        :param centile: The centile value to calculate (e.g., 0.5 for 50th centile).
        :return: A NumPy array of calculated values.
        """

        zscore = norm.ppf(centile).item()
        L, M, S = data.L, data.M, data.S

        return np.array([calculate_value_for_z_score(zscore, _l, _m, _s) for _l, _m, _s in zip(L, M, S)])

    def _get_age_group(self, measurement_age_days: int, measurement_type: str = "") -> AGE_GROUP_TYPE:
        newborn = measurement_age_days == 0
        very_preterm = self.child.is_very_preterm is True

        if newborn and very_preterm:
            return "very_preterm_newborn"

        if newborn:
            return "newborn"

        if very_preterm and measurement_age_days <= PlotAgeValues.VERY_PRETERM.value[1]:
            return "very_preterm_growth"

        if (
            measurement_type in ["head_circumference_velocity", "length_velocity", "weight_velocity"]
            and measurement_age_days <= PlotAgeValues.ZERO_ONE_YEARS.value[1]
        ):
            return "0-1"

        if measurement_age_days <= PlotAgeValues.ZERO_TWO_YEARS.value[1]:
            return "0-2"
        if measurement_age_days <= PlotAgeValues.TWO_FIVE_YEARS.value[1]:
            return "2-5"
        if measurement_age_days <= PlotAgeValues.FIVE_TEN_YEARS.value[1]:
            return "5-10"
        if measurement_age_days <= PlotAgeValues.TEN_NINETEEN_YEARS.value[1]:
            return "10-19"

        raise ValueError(f"Invalid measurement {measurement_type} at age: {measurement_age_days}. Cannot determine age group.")

    def _get_table_name(self, measurement_age_days: int) -> TABLE_NAME_TYPE:
        """
        Returns the table name based on the measurement age and type.
        """
        if measurement_age_days == 0:
            return "newborn"

        if self.child.is_very_preterm is True and measurement_age_days <= PlotAgeValues.VERY_PRETERM.value[1]:
            return "very_preterm_growth"

        if measurement_age_days <= PlotAgeValues.TWO_FIVE_YEARS.value[1]:
            return "growth"

        return "child_growth"
