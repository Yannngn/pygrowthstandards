import datetime
from dataclasses import dataclass, field
from typing import Literal

from src.patient.measurement import Measurement, MeasurementGroup
from src.utils.constants import WEEK


@dataclass
class Patient:
    """Represents a patient with demographic and medical information.

    Use birth gestational age or today's gestational age.
    """

    sex: Literal["M", "F", "U"]
    birthday_date: datetime.date | None
    gestational_age_weeks: int = 40
    gestational_age_days: int = 0

    measurements: list[MeasurementGroup] = field(default_factory=list)

    gestational_age: datetime.timedelta = field(init=False)
    is_born: bool = field(init=False)
    is_very_preterm: bool = field(init=False)

    def __post_init__(self):
        self._setup()

    def age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Returns the age in days on a specific date."""
        assert self.birthday_date is not None, "Patient must be born to calculate age."

        date = date or datetime.date.today()

        assert date >= self.birthday_date, "Date must be after the birthday date."

        return date - self.birthday_date

    def chronological_age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Returns the chronological age in days on a specific date."""

        date = date or datetime.date.today()

        if self.birthday_date is not None:
            return date - (self.birthday_date - self.gestational_age)

        return date - self.gestational_age  # type: ignore

    def robust_age(self, date: datetime.date | None = None) -> tuple[str, int]:
        date = date or datetime.date.today()
        chronological_days = self.chronological_age(date).days

        if self.birthday_date is not None:  # if is born
            age_days = self.age(date).days

            if age_days == 0:
                chronological_days = self.chronological_age(date).days
                return ("gestational_age", chronological_days)

            if self.is_very_preterm and chronological_days <= 64 * WEEK:
                return ("gestational_age", chronological_days)

            return ("age", age_days)

        return ("gestational_age", chronological_days)

    def get_age(self, age_type: str = "age", date: datetime.date | None = None) -> int:
        """Returns the age in days or gestational age in weeks."""
        if age_type == "age":
            return self.age(date).days
        elif age_type == "gestational_age":
            return self.gestational_age.days
        elif age_type == "chronological_age":
            return self.chronological_age(date).days

        raise ValueError(f"Invalid age type: {age_type}. Use 'age', 'gestational_age', or 'chronological_age'.")

    def add_measurement(self, measurement: Measurement) -> None:
        """
        Adds a single Measurement to the patient's measurements.
        If a MeasurementGroup for the same date exists, overwrite the attribute
        with measurement.measurement_type and .value. Otherwise, create a new group.

        :param measurement: The Measurement object to add.
        """
        # Search for a group with the same date
        for group in self.measurements:
            if group.date == measurement.date:
                # Overwrite the attribute in the group
                setattr(group, measurement.measurement_type, measurement.value)
                group._setup()
                return

        # If not found, create a new group and set the attribute
        new_group = MeasurementGroup(
            table_name=measurement.table_name, date=measurement.date, **{measurement.measurement_type: measurement.value}
        )
        self.measurements.append(new_group)

    def add_measurements(self, measurements: MeasurementGroup) -> None:
        """
        Adds a MeasurementGroup to the patient's measurements.

        :param measurements: The MeasurementGroup object to add.
        """
        self.measurements.append(measurements)

    def _setup(self):
        """
        Setup method to initialize any additional attributes or perform checks.
        This can be extended in subclasses if needed.
        """
        self.is_born = self.birthday_date is not None
        self.gestational_age = datetime.timedelta(weeks=self.gestational_age_weeks, days=self.gestational_age_days)

        if self.is_born:
            self.is_very_preterm = self.gestational_age_weeks < 32
