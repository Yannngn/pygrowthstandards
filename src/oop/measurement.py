from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from ..utils.config import MeasurementTypeType, TableNameType


@dataclass
class Measurement:
    value: float
    measurement_type: MeasurementTypeType
    table_name: TableNameType = "growth"
    date: dt_datetime | dt_date = field(default_factory=dt_datetime.now)


@dataclass
class MeasurementGroup:
    table_name: TableNameType = "growth"
    date: dt_datetime | dt_date = field(default_factory=dt_datetime.now)

    stature: float | None = None
    weight: float | None = None
    head_circumference: float | None = None

    body_mass_index: float | None = field(init=False, repr=False)
    weight_stature_ratio: float | None = field(init=False, repr=False)

    def __post_init__(self):
        self._setup()

    def to_dict(self) -> dict:
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
        measurements = []
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
        if self.weight is not None and self.stature is not None:
            self.body_mass_index = pow(100, 2) * self.weight / pow(self.stature, 2)
            self.weight_stature_ratio = self.weight / self.stature
