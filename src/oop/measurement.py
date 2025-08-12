"""Measurement classes for OOP growth standards API.

This module defines data structures for capturing single measurements and groups
of measurements at specific dates, including derived metrics like BMI and
weight-stature ratio.

Classes:
    Measurement: Represents a single measurement value and metadata.
    MeasurementGroup: Aggregates measurements for a date and computes derived fields.

Example:
    >>> from src.oop.measurement import MeasurementGroup
    >>> mg = MeasurementGroup(stature=75.0, weight=10.0)
    >>> mg.body_mass_index  # BMI = weight/(stature/100)**2
    17.78

Todo:
    * Validate measurement_type against allowed types.
"""
import datetime
from dataclasses import dataclass, field
from typing import Literal

TableNames = Literal["newborn", "growth", "child_growth", "very_preterm_growth", "very_preterm_newborn"]


@dataclass
class Measurement:
    """
    Holds a single measurement value and its context.

    Attributes:
        value (float): The measurement value.
        measurement_type (str): Type of measurement (e.g., 'stature').
        table_name (TableNames): Contextual table name.
        date (datetime.date): Date of the measurement.
    """

    value: float
    measurement_type: str
    table_name: TableNames = "growth"
    date: datetime.date = field(default_factory=datetime.date.today)


@dataclass
class MeasurementGroup:
    """
    Aggregates measurements recorded at the same date and computes derived metrics.

    Attributes:
        table_name (TableNames): Contextual table name for lookup.
        date (datetime.date): Date of measurements.
        stature (float | None): Height in cm.
        weight (float | None): Weight in kg.
        head_circumference (float | None): Head circumference in cm.
        body_mass_index (float | None): Computed BMI (kg/m^2) if stature and weight present.
        weight_stature_ratio (float | None): Computed weight-to-stature ratio.
    """

    table_name: TableNames = "growth"
    date: datetime.date = field(default_factory=datetime.date.today)

    stature: float | None = None
    weight: float | None = None
    head_circumference: float | None = None

    body_mass_index: float | None = field(init=False, repr=False)
    weight_stature_ratio: float | None = field(init=False, repr=False)

    def __post_init__(self):
        """
        Initializes derived metrics after dataclass init.
        """
        self._setup()

    def to_dict(self) -> dict:
        """
        Convert the measurement group to a dictionary.

        Returns:
            dict: Keys include 'date', 'stature', 'weight', 'head_circumference',
                'body_mass_index', 'weight_stature_ratio'.
        """
        data = {
            "date": self.date,
            "stature": self.stature,
            "weight": self.weight,
            "head_circumference": self.head_circumference,
        }

        if hasattr(self, "body_mass_index"):
            data["body_mass_index"] = self.body_mass_index
        if hasattr(self, "weight_stature_ratio"):
            data["weight_stature_ratio"] = self.weight_stature_ratio

        return data

    def to_measurements(self) -> list[Measurement]:
        """
        Convert stored values into Measurement objects.

        Returns:
            list[Measurement]: List of Measurement instances for non-null values.
        """
        measurements: list[Measurement] = []
        data = self.to_dict()

        for key, value in data.items():
            if value is None or key == "date":
                continue
            measurements.append(
                Measurement(value=value, measurement_type=key, date=data["date"])
            )

        return measurements

    @classmethod
    def from_measurements(cls, measurements: list[Measurement]) -> "MeasurementGroup":
        """
        Build a MeasurementGroup from a list of Measurement objects.

        Args:
            measurements (list[Measurement]): Measurements sharing the same date.

        Returns:
            MeasurementGroup: Group initialized with provided measurements.
        """
        section = cls()
        for measurement in measurements:
            if measurement.measurement_type == "stature":
                section.stature = measurement.value
            elif measurement.measurement_type == "weight":
                section.weight = measurement.value
            elif measurement.measurement_type == "head_circumference":
                section.head_circumference = measurement.value

            section.date = measurement.date

        section._setup()
        return section

    def _setup(self):
        """
        Compute derived metrics: BMI and weight-to-stature ratio.
        """
        if self.weight is not None and self.stature is not None:
            self.body_mass_index = (100 ** 2) * self.weight / (self.stature ** 2)
            self.weight_stature_ratio = self.weight / self.stature

