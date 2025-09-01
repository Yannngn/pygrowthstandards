from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from ..utils.config import AgeGroupType, MeasurementTypeType


@dataclass
class Measurement:
    value: float
    measurement_type: MeasurementTypeType
    date: dt_datetime | dt_date = field(default_factory=dt_datetime.now)

    age_group: AgeGroupType | None = None


@dataclass
class MeasurementGroup:
    date: dt_datetime | dt_date = field(default_factory=dt_datetime.now)

    stature: float | None = None
    weight: float | None = None
    head_circumference: float | None = None

    body_mass_index: float | None = field(init=False, repr=False)
    weight_stature_ratio: float | None = field(init=False, repr=False)

    age_group: AgeGroupType | None = None

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

    @classmethod
    def from_dict(cls, data: dict) -> "MeasurementGroup":
        """
        Create a MeasurementGroup instance from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing measurement fields.
            Required key:
              - "date": an ISO-8601 string or a datetime.date / datetime.datetime object.
            Optional keys (if missing, the corresponding attributes will be set to None):
              - "stature"
              - "weight"
              - "head_circumference"

        Returns
        -------
        "MeasurementGroup"
            A new MeasurementGroup with the parsed/assigned date and optional measurement values.

        Raises
        ------
        AssertionError
            If the "date" key is missing from the input dictionary.
        ValueError
            If "date" is a string but cannot be parsed via datetime.fromisoformat.
        TypeError
            If "date" is provided but is not a str, datetime.date, or datetime.datetime.

        Notes
        -----
        - ISO-8601 strings are parsed using datetime.fromisoformat (e.g. "YYYY-MM-DD" or
          "YYYY-MM-DDTHH:MM:SS").
        - If a datetime.date or datetime.datetime is provided, it will be used as-is.
        - The method sets attributes `stature`, `weight`, and `head_circumference` from the dict
          (or to None if those keys are absent).

        Example
        -------
        >>> MeasurementGroup.from_dict({"date": "2020-01-01", "weight": 3.5})
        """
        assert "date" in data, "Date is required"

        date_value = data["date"]

        if isinstance(date_value, str):
            try:
                parsed = dt_datetime.fromisoformat(date_value)
            except (ValueError, TypeError) as err:
                raise ValueError(f"Invalid date string: {date_value!r}") from err

            group = cls(date=parsed)

        elif isinstance(date_value, dt_datetime | dt_date):
            group = cls(date=date_value)
        else:
            raise TypeError("date must be a str, datetime.datetime or datetime.date")

        group.stature = data.get("stature", None)
        group.weight = data.get("weight", None)
        group.head_circumference = data.get("head_circumference", None)

        return group

    def _setup(self):
        if self.weight is not None and self.stature is not None:
            self.body_mass_index = pow(100, 2) * self.weight / pow(self.stature, 2)
            self.weight_stature_ratio = self.weight / self.stature
