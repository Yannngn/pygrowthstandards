import datetime
import os
import sys
from abc import ABC, abstractmethod
from typing import Collection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.calculator.child import Child
from src.calculator.measurement import Measurement
from src.calculator.table_data import TableData
from src.utils.choices import PlotAgeChoices, PlotAgeValues


class BaseMixin(ABC):
    @abstractmethod
    def __init__(self, child: Child):
        self.child: Child = child
        self._measurements: list[Measurement] = []
        self._data = TableData(child.sex)

    @abstractmethod
    def compute_measurement(self, measurement: Measurement) -> None:
        """Placeholder for compute method to be implemented in subclasses."""
        ...


class AdderMixin(BaseMixin):
    def add_measurement(
        self,
        stature: float | None = None,
        weight: float | None = None,
        head_circumference: float | None = None,
        date: datetime.date | None = None,
    ) -> None:
        """
        Add a new measurement to the list.

        Creates a Measurement instance from the provided values and appends it to the internal list.
        The list is kept sorted by date.

        Args:
            stature (float | None): The length or height value.
            weight (float | None): The weight value.
            head_circumference (float | None): The head circumference value.
            date (datetime.date | None): The date of the measurement. Defaults to None overwriting to today's date.
        """
        if date is None:
            date = datetime.date.today()

        measurement = Measurement(stature=stature, weight=weight, head_circumference=head_circumference, date=date)

        self.add_measurement_object(measurement)

    def add_measurement_object(self, measurement: Measurement) -> None:
        """
        Add a Measurement instance to the list.

        Appends the given Measurement object to the internal list and keeps the list sorted by date.

        Args:
            measurement (Measurement): An instance of the Measurement class.
        """
        self.compute_measurement(measurement)
        self._measurements.append(measurement)
        self._measurements.sort(key=lambda m: m.date)

    def add_measurements(self, measurements: Collection[Collection]) -> None:
        """
        Add multiple measurements from collections following (stature, weight, head_circumference, date).

        Each element in the input should be a collection (e.g., list or tuple) of values suitable for the Measurement constructor.
        The list is kept sorted by date.

        Args:
            list_of_measurements (Collection[Collection]):
                A collection of collections, each representing measurement values.
        """

        self.add_measurement_objects([Measurement(*m) for m in measurements])

    def add_measurement_objects(self, measurements: Collection[Measurement]) -> None:
        """
        Add multiple Measurement instances to the list.

        Appends all provided Measurement objects to the internal list and keeps the list sorted by date.

        Args:
            *measurements (Measurement): Variable number of Measurement instances.
        """
        [self.compute_measurement(m) for m in measurements]

        self._measurements.extend(measurements)
        self._measurements.sort(key=lambda m: m.date)


class GetterMixin(BaseMixin):
    def get_measurements_by_age_group(self, age_group: str) -> list[Measurement]:
        """Retrieves measurements within a specific age group.

        Args:
            age_group: The age group to filter by (e.g., "0-2", "newborn", "very_preterm").
                Defaults to "none" which returns all measurements.

        Returns:
            A list of Measurement instances within the specified age group.

        Raises:
            ValueError: If gestational age is required but not set for newborn or very_preterm groups.
        """

        if age_group == "all":
            return self._measurements

        min_age, max_age = PlotAgeValues[PlotAgeChoices(age_group).name].value
        if age_group in ["newborn", "very_preterm", "very_preterm_newborn"]:
            if self.child.gestational_age is None:
                raise ValueError("Gestational age is required for newborn measurements. Use child.set_gestational_age() to set it.")
            return [m for m in self._measurements if min_age <= self.child.gestational_age.days <= max_age]

        return [m for m in self._measurements if min_age <= self.child.age(m.date).days <= max_age]

    # getters
    # measurements
    def get_measurements(self) -> list[Measurement]:
        """
        Retrieve measurements for a specific date or all measurements.

        If a date is provided, returns a list of Measurement instances that match the given date.
        If no date is provided (date is None), returns all Measurement instances.

        Args:
            date (datetime.date | None): The date to filter measurements by, or None to return all measurements.

        Returns:
            list[Measurement]: A list of Measurement instances matching the specified date, or all measurements if date is None.
        """
        return self._measurements

    # z-scores
    def get_z_scores(self) -> list[dict[str, float]]:
        """
        Return computed z-scores for all stored measurements.

        Iterates over all measurements added to the Calculator and computes the z-scores
        for each available measurement type (length/height, weight, head circumference, BMI).

        Returns:
            list[dict[str, float]]: A list of dictionaries, each containing the z-scores for a measurement.
        """
        return [m.z_scores for m in self.get_measurements()]

    # centiles
    def get_centiles(self) -> list[dict[str, float]]:
        """
        Calculate percentiles for all stored measurements.

        Iterates over all measurements added to the Calculator and computes the percentiles
        for each available measurement type (length/height, weight, head circumference, BMI).

        Returns:
            list[dict[str, float]]: A list of dictionaries, each containing the percentiles for a measurement.
        """

        return [m.z_scores for m in self.get_measurements()]


class GetterByDateMixin(BaseMixin):
    def get_measurements_by_date(self, date: datetime.date) -> list[Measurement]:
        """
        Retrieve measurements for a specific date.

        If multiple measurements exist for the date, returns all of them.
        If no measurement exists for the date, returns an empty list.

        Args:
            date (datetime.date): The date to filter measurements by.

        Returns:
            list[Measurement]: A list of Measurement instances matching the specified date, or an empty list if no measurements exist.
        """
        return [m for m in self._measurements if m.date == date]

    def get_z_scores_by_date(self, date: datetime.date) -> list[dict[str, float]]:
        """
        Return computed z-scores for measurements on a specific date.

        Args:
            date (datetime.date): The date to filter measurements by.

        Returns:
            list[dict[str, float]]: A list of dictionaries with z-scores for each measurement on the given date.
        """
        return [m.z_scores for m in self.get_measurements_by_date(date)]

    def get_centiles_by_date(self, date: datetime.date) -> list[dict[str, float]]:
        """
        Calculate percentiles for measurements on a specific date.

        Args:
            date (datetime.date): The date to filter measurements by.

        Returns:
            list[dict[str, float]]: A list of dictionaries with percentiles for each measurement on the given date.
        """

        return [m.z_scores for m in self.get_measurements_by_date(date)]


class GetterByDateRangeMixin(BaseMixin):
    def get_measurements_by_date_range(self, start_date: datetime.date | None, end_date: datetime.date | None) -> list[Measurement]:
        """
        Retrieve measurements within a specific date range.

        Args:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.

        Returns:
            list[Measurement]: A list of Measurement instances within the specified date range.
        """
        if start_date is not None and end_date is not None:
            return [m for m in self._measurements if start_date <= m.date <= end_date]

        if start_date is not None:
            return [m for m in self._measurements if m.date >= start_date]

        if end_date is not None:
            return [m for m in self._measurements if m.date <= end_date]

        return self._measurements

    def get_z_scores_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> list[dict[str, float]]:
        """
        Return computed z-scores for measurements within a specific date range.

        Args:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.

        Returns:
            list[dict[str, float]]: A list of dictionaries with z-scores for each measurement in the date range.
        """

        return [m.z_scores for m in self.get_measurements_by_date_range(start_date, end_date)]

    def get_centiles_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> list[dict[str, float]]:
        """
        Calculate percentiles for measurements within a specific date range.

        Args:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.

        Returns:
            list[dict[str, float]]: A list of dictionaries with percentiles for each measurement in the date range.
        """
        measurements = self.get_measurements_by_date_range(start_date, end_date)

        return [m.z_scores for m in measurements]


class HandlerMixin(AdderMixin, GetterMixin, GetterByDateMixin, GetterByDateRangeMixin):
    """
    Mixin class that combines adding and retrieving measurements with z-scores and centiles.

    This class provides methods to add measurements, retrieve them by age group, date, or date range,
    and compute z-scores and centiles for the measurements.
    """
