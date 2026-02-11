"""Measurement value containers for the OOP API."""

from dataclasses import dataclass, field
from datetime import datetime as dt_datetime
from typing import cast

from pygrowthstandards.config.growth import MeasurementAliasType, TableNameType
from pygrowthstandards.utils.date import DateType


@dataclass
class Measurement:
    """
    Holds a single measurement value and its context.

    Attributes:
        value: The measurement value.
        measurement_type: Type of measurement (e.g., "stature").
        table_name: Contextual table name.
        date: Date of the measurement.
    """

    value: float
    measurement_type: MeasurementAliasType
    table_name: TableNameType = "growth"
    date: DateType = field(default_factory=dt_datetime.now)


@dataclass
class MeasurementGroup:
    """Grouped measurements recorded at a single date.

    Attributes:
        table_name: Reference table name.
        date: Date of the measurement group.
        stature: Stature value in cm.
        weight: Weight value in kg.
        head_circumference: Head circumference in cm.
    """

    table_name: TableNameType = "growth"
    date: DateType = field(default_factory=dt_datetime.now)

    stature: float | None = None
    weight: float | None = None
    head_circumference: float | None = None

    body_mass_index: float | None = field(init=False, repr=False, default=None)
    weight_stature_ratio: float | None = field(init=False, repr=False, default=None)

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
        raw_fields = ["stature", "weight", "head_circumference"]

        for key in raw_fields:
            value = getattr(self, key)
            if value is None:
                continue
            measurements.append(
                Measurement(
                    value=value,
                    measurement_type=cast(MeasurementAliasType, key),
                    table_name=self.table_name,
                    date=self.date,
                )
            )

        return measurements

    @classmethod
    def from_measurements(cls, measurements: list[Measurement]) -> "MeasurementGroup":
        """Create a measurement group from individual Measurement objects.

        Args:
            measurements: List of Measurement values.

        Returns:
            MeasurementGroup with shared date.

        Raises:
            ValueError: If measurements are empty or have mixed dates.
        """
        if not measurements:
            raise ValueError("Measurements list cannot be empty")

        if not all(m.date == measurements[0].date for m in measurements):
            raise ValueError("All measurements must have the same date")

        section = cls(date=measurements[0].date)
        for measurement in measurements:
            section.date = measurement.date

            if measurement.measurement_type == "stature":
                section.stature = measurement.value
                continue

            if measurement.measurement_type == "weight":
                section.weight = measurement.value
                continue

            if measurement.measurement_type == "head_circumference":
                section.head_circumference = measurement.value
                continue

        section._setup()
        return section

    def _setup(self):
        """
        Compute derived metrics: BMI and weight-to-stature ratio.
        """
        if self.weight is not None and self.stature is not None and self.stature != 0:
            self.body_mass_index = (100**2) * self.weight / (self.stature**2)
            self.weight_stature_ratio = self.weight / self.stature
        else:
            self.body_mass_index = None
            self.weight_stature_ratio = None
