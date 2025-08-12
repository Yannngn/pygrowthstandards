"""Manage patient data and compute growth standard z-scores.

Provides the Patient class to record demographics, measurements, and
calculate z-scores and formatted output.

Classes:
    Patient: Pediatric patient with measurement management and analysis.

Example:
    >>> from src.oop.patient import Patient
    >>> p = Patient(sex='M', birthday_date=date(2020,1,1))
    >>> p.add_measurement(Measurement(value=75.0, measurement_type='stature'))
    >>> p.calculate_all()
    >>> print(p.display_measurements())
"""

import datetime
from dataclasses import dataclass, field
from typing import Literal

from ..utils.results import str_dataframe
from .calculator import Calculator
from .measurement import Measurement, MeasurementGroup


@dataclass
class Patient:
    """Patient class to manage demographics and measurements.

    Attributes:
        sex (Literal["M", "F", "U"]): The sex of the patient.
        birthday_date (datetime.date | None): The birth date of the patient.
        gestational_age_weeks (int): The gestational age in weeks. Defaults to 40.
        gestational_age_days (int): The gestational age in days. Defaults to 0.
        measurements (list[MeasurementGroup]): List of measurement groups for the patient.
        z_scores (list[MeasurementGroup]): Calculated z-scores for the measurement groups.

    Methods:
        age(date: datetime.date | None = None) -> datetime.timedelta:
            Calculate the age of the patient as of the given date.
        chronological_age(date: datetime.date | None = None) -> datetime.timedelta:
            Calculate the chronological age of the patient as of the given date.
        get_age(age_type: str = "age", date: datetime.date | None = None) -> int:
            Get the age of the patient in days for the specified age type.
        add_measurement(measurement: Measurement) -> None:
            Add a single measurement to the patient's record.
        add_measurements(measurements: MeasurementGroup) -> None:
            Add a group of measurements to the patient's record.
        calculate_all() -> None:
            Calculate z-scores for all measurement groups in the patient's record.
        display_measurements() -> str:
            Generate a formatted string of the patient's measurements and z-scores.
    """

    sex: Literal["M", "F", "U"]
    birthday_date: datetime.date | None
    gestational_age_weeks: int = 40
    gestational_age_days: int = 0

    measurements: list[MeasurementGroup] = field(default_factory=list)
    z_scores: list[MeasurementGroup] = field(default_factory=list, init=False)

    gestational_age: datetime.timedelta = field(init=False)
    is_born: bool = field(init=False)
    is_very_preterm: bool = field(init=False)

    def __post_init__(self):
        self._setup()
        self.calculator = Calculator()

    def age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Calculate the age of the patient as of the given date.

        Args:
            date (datetime.date | None): The date to calculate the age at. Defaults to today.

        Returns:
            datetime.timedelta: The age of the patient.
        """
        if self.birthday_date is None:
            raise ValueError("Patient must be born to calculate age.")

        date = date or datetime.date.today()

        if date < self.birthday_date:
            raise ValueError("Date must be after the birthday date.")

        return date - self.birthday_date

    def chronological_age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Calculate the chronological age of the patient as of the given date.

        Args:
            date (datetime.date | None): The date to calculate the chronological age at. Defaults to today.

        Returns:
            datetime.timedelta: The chronological age of the patient.
        """
        date = date or datetime.date.today()

        if self.birthday_date is not None:
            age = date - (self.birthday_date - self.gestational_age)
            if age.days > 64:
                return self.age(date)

            return age

        return date - self.gestational_age  # type: ignore

    def get_age(self, age_type: str = "age", date: datetime.date | None = None) -> int:
        """Get the age of the patient in days for the specified age type.

        Args:
            age_type (str): The type of age to retrieve. Can be 'age', 'gestational_age', or 'chronological_age'.
            date (datetime.date | None): The date to calculate the age at. Defaults to None.

        Returns:
            int: The age of the patient in days.

        Raises:
            ValueError: If an invalid age type is provided.
        """
        if age_type == "age":
            return self.age(date).days
        elif age_type == "gestational_age":
            return self.gestational_age.days
        elif age_type == "chronological_age":
            return self.chronological_age(date).days

        raise ValueError(f"Invalid age type: {age_type}. Use 'age', 'gestational_age', or 'chronological_age'.")

    def add_measurement(self, measurement: Measurement) -> None:
        """Add a single measurement to the patient's record.

        Args:
            measurement (Measurement): The measurement to add.
        """

        for group in self.measurements:
            if group.date == measurement.date:
                setattr(group, measurement.measurement_type, measurement.value)
                group._setup()
                return

        new_group = MeasurementGroup(
            table_name=measurement.table_name, date=measurement.date, **{measurement.measurement_type: measurement.value}
        )
        self.measurements.append(new_group)

    def add_measurements(self, measurements: MeasurementGroup) -> None:
        """Add a group of measurements to the patient's record.

        Args:
            measurements (MeasurementGroup): The group of measurements to add.
        """
        self.measurements.append(measurements)

    def calculate_all(self) -> None:
        """Calculates z-scores for all measurement groups in the patient."""
        self.z_scores = [self.calculator.calculate_measurement_group(group, self.get_age(date=group.date)) for group in self.measurements]

    def display_measurements(self) -> str:
        """Generate a formatted string of the patient's measurements and z-scores.

        Returns:
            str: A formatted string displaying the patient's measurements and z-scores.
        """
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
            age_type = self._get_age_type(m_group.table_name)
            age = self.get_age(age_type=age_type, date=date)

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

    def _setup(self):
        """Perform post-initialization setup for the Patient object."""
        self.is_born = self.birthday_date is not None
        self.gestational_age = datetime.timedelta(weeks=self.gestational_age_weeks, days=self.gestational_age_days)

        if self.is_born:
            self.is_very_preterm = self.gestational_age_weeks < 32

    @staticmethod
    def _get_age_type(table_name: str) -> str:
        """Determine the age type based on the table name.

        Args:
            table_name (str): The name of the table.

        Returns:
            str: The age type corresponding to the table name.
        """
        if table_name in ["very_preterm_newborn", "newborn"]:
            return "gestational_age"
        if table_name in ["very_preterm_growth"]:
            return "chronological_age"

        return "age"
