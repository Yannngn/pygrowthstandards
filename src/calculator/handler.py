import datetime
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)
from collections.abc import Collection

from src.calculator.measurement import Measurement


class Handler:
    def __init__(self):
        self._measurements: list[Measurement] = []

    # adders

    def add_measurement(
        self,
        length_height: float | None = None,
        weight: float | None = None,
        head_circumference: float | None = None,
        date: datetime.date = datetime.date.today(),
    ) -> None:
        """
        Add a new measurement to the list.

        Creates a Measurement instance from the provided values and appends it to the internal list.
        The list is kept sorted by date.

        Args:
            length_height (float | None): The length or height value.
            weight (float | None): The weight value.
            head_circumference (float | None): The head circumference value.
            date (datetime.date): The date of the measurement. Defaults to today.
        """
        self._measurements.append(
            Measurement(length_height, weight, head_circumference, date)
        )
        self._measurements.sort(key=lambda m: m.date)

    def add_measurement_object(self, measurement: Measurement) -> None:
        """
        Add a Measurement instance to the list.

        Appends the given Measurement object to the internal list and keeps the list sorted by date.

        Args:
            measurement (Measurement): An instance of the Measurement class.
        """
        self._measurements.append(measurement)
        self._measurements.sort(key=lambda m: m.date)

    def add_measurements(self, list_of_measurements: Collection[Collection]) -> None:
        """
        Add multiple measurements from collections.

        Each element in the input should be a collection (e.g., list or tuple) of values suitable for the Measurement constructor.
        The list is kept sorted by date.

        Args:
            list_of_measurements (Collection[Collection]):
                A collection of collections, each representing measurement values.
        """
        for m in list_of_measurements:
            self._measurements.append(Measurement(*m))

        self._measurements.sort(key=lambda m: m.date)

    def add_measurement_objects(self, *measurements: Measurement) -> None:
        """
        Add multiple Measurement instances to the list.

        Appends all provided Measurement objects to the internal list and keeps the list sorted by date.

        Args:
            *measurements (Measurement): Variable number of Measurement instances.
        """
        self._measurements.extend(measurements)
        self._measurements.sort(key=lambda m: m.date)

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

    def get_measurements_by_date_range(
        self, start_date: datetime.date | None, end_date: datetime.date | None
    ) -> list[Measurement]:
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

    # z-scores
    def get_zscores(self) -> list[dict[str, float]]:
        """
        Calculate z-scores for all stored measurements.

        Iterates over all measurements added to the Calculator and computes the z-scores
        for each available measurement type (length/height, weight, head circumference, BMI).

        Returns:
            list[dict[str, float]]: A list of dictionaries, each containing the z-scores for a measurement.
        """
        measurements = self.get_measurements()

        self._calculate(measurements)

        return [m.get_z_scores() for m in measurements]

    def get_zscores_by_date(self, date: datetime.date) -> list[dict[str, float]]:
        """
        Calculate z-scores for measurements on a specific date.

        Args:
            date (datetime.date): The date to filter measurements by.

        Returns:
            list[dict[str, float]]: A list of dictionaries with z-scores for each measurement on the given date.
        """
        measurements = self.get_measurements_by_date(date)

        self._calculate(measurements)

        return [m.get_z_scores() for m in measurements]

    def get_zscores_by_date_range(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> list[dict[str, float]]:
        """
        Calculate z-scores for measurements within a specific date range.

        Args:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.

        Returns:
            list[dict[str, float]]: A list of dictionaries with z-scores for each measurement in the date range.
        """

        measurements = self.get_measurements_by_date_range(start_date, end_date)

        self._calculate(measurements)

        return [m.get_z_scores() for m in measurements]

    # percentiles
    def get_percentiles(self) -> list[dict[str, float]]:
        """
        Calculate percentiles for all stored measurements.

        Iterates over all measurements added to the Calculator and computes the percentiles
        for each available measurement type (length/height, weight, head circumference, BMI).

        Returns:
            list[dict[str, float]]: A list of dictionaries, each containing the percentiles for a measurement.
        """
        measurements = self.get_measurements()

        self._calculate(measurements)

        return [m.get_percentiles() for m in measurements]

    def get_percentiles_by_date(self, date: datetime.date) -> list[dict[str, float]]:
        """
        Calculate percentiles for measurements on a specific date.

        Args:
            date (datetime.date): The date to filter measurements by.

        Returns:
            list[dict[str, float]]: A list of dictionaries with percentiles for each measurement on the given date.
        """
        measurements = self.get_measurements_by_date(date)

        self._calculate(measurements)

        return [m.get_percentiles() for m in measurements]

    def get_percentiles_by_date_range(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> list[dict[str, float]]:
        """
        Calculate percentiles for measurements within a specific date range.

        Args:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.

        Returns:
            list[dict[str, float]]: A list of dictionaries with percentiles for each measurement in the date range.
        """
        measurements = self.get_measurements_by_date_range(start_date, end_date)

        self._calculate(measurements)

        return [m.get_percentiles() for m in measurements]

    def _calculate(self, measurements: list[Measurement]):
        raise (NotImplementedError("Subclasses should implement this method"))
