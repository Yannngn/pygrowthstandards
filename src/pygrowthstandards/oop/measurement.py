import csv
from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from pygrowthstandards.oop.utils import AgeMixin
from pygrowthstandards.utils.results import str_dataframe

from ..config import AgeGroupType, MeasurementTypeType


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
            measurements.append(Measurement(value=value, measurement_type=key, date=data["date"]))

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


class MeasurementMixin(AgeMixin):
    measurements: list[MeasurementGroup]
    z_scores: list[MeasurementGroup]

    def add_measurement(self, measurement: Measurement) -> None:
        for group in self.measurements:
            if group.date == measurement.date:
                setattr(group, measurement.measurement_type, measurement.value)
                group._setup()
                return

        age_group = self._get_age_group(date=measurement.date)  # type: ignore
        measurement.age_group = age_group

        new_group = MeasurementGroup(
            date=measurement.date,
            **{measurement.measurement_type: measurement.value},  # type: ignore
        )
        new_group.age_group = age_group
        self.measurements.append(new_group)

    def add_measurements(self, measurements: MeasurementGroup) -> None:
        if measurements.age_group is None:
            measurements.age_group = self._get_age_group(date=measurements.date)  # type: ignore

        self.measurements.append(measurements)

    def display_measurements(self) -> str:
        if not self.measurements:
            return "No measurements available."

        # Sort groups by date to ensure chronological order
        sorted_measurements = sorted(self.measurements, key=lambda mg: mg.date)
        sorted_z_scores = sorted(self.z_scores, key=lambda mg: mg.date)

        # Create a mapping from date to z-score group for easy lookup
        z_scores_map = {group.date: group for group in sorted_z_scores}

        results_list = []
        date_list = []
        age_list = []

        for m_group in sorted_measurements:
            date = m_group.date
            assert m_group.age_group is not None, "No valid age group found for the given ages."
            age_type = self._get_age_type(m_group.age_group)
            age = self.get_age_with_type(age_type=age_type, date=date)

            date_list.append(date)
            age_list.append(age)

            result_dict = {}
            m_dict = m_group.to_dict()
            z_dict = z_scores_map.get(date, MeasurementGroup(date=date)).to_dict()

            for m_type, m_value in m_dict.items():
                if m_value is None or m_type == "date":
                    continue

                result_dict[m_type] = {"value": m_value}
                z_value = z_dict.get(m_type)
                if z_value is not None:
                    result_dict[m_type]["z"] = z_value

            results_list.append(result_dict)

        return str_dataframe(results=results_list, date_list=date_list, age_list=age_list)

    def load_measurements_from_csv(self, csv_path: str) -> None:
        """
        Load measurements from a CSV file into this Patient instance.

        This method opens the CSV file at csv_path, iterates over its rows using csv.DictReader,
        converts each row to a MeasurementGroup via MeasurementGroup.from_dict, and adds the
        resulting groups to the patient's measurements using self.add_measurements. After all
        rows are processed the patient's z_scores are recalculated for every measurement group
        by calling self.calculator.calculate_measurement_group(group, self.get_age_with_type(date=group.date)).

        Parameters
        ----------
        csv_path : str | os.PathLike
            Path to a CSV file. The CSV is read in text mode using the platform default encoding.
            Each row is expected to contain at least a "date" field (ISO-8601 string or date/datetime).
            Other optional fields (e.g. "stature", "weight", "head_circumference") are forwarded to MeasurementGroup.from_dict.

        Returns
        -------
        None
            The method mutates the Patient instance by appending measurements and setting/refreshing self.z_scores.

        Raises
        ------
        FileNotFoundError
            If the file specified by csv_path does not exist.
        csv.Error
            If the CSV is malformed or cannot be parsed by csv.DictReader.
        AssertionError
            If a row lacks the required "date" key and MeasurementGroup.from_dict asserts.
        ValueError
            If a date string cannot be parsed by MeasurementGroup.from_dict (datetime.fromisoformat) or other row validation fails.
        TypeError
            If a row contains an unsupported type for the date field or if MeasurementGroup.from_dict raises TypeError.

        Notes
        -----
        - Rows are converted to MeasurementGroup instances via MeasurementGroup.from_dict.
        - Existing measurements on the Patient are preserved and new groups are appended.
        - After loading, z-scores are recomputed for every measurement group and stored on self.z_scores.
        - The method intentionally propagates parsing/validation errors from MeasurementGroup.from_dict to the caller.

        Example
        -------
        >>> patient.load_measurements_from_csv("/path/to/measurements.csv")
        """

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                measurements = MeasurementGroup.from_dict(row)
                self.add_measurements(measurements)
