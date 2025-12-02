import datetime
from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from pygrowthstandards.config import (
    DataSexType,
)
from pygrowthstandards.oop.development import DevelopmentGoalGroup, DevelopmentMixin
from pygrowthstandards.oop.utils import AgeMixin
from pygrowthstandards.oop.vaccination import VaccinationRecordGroup
from pygrowthstandards.utils.date_utils import handle_date

from .calculator import Calculator, DevelopmentCalculator, ImmunizationCalculator
from .measurement import MeasurementGroup, MeasurementMixin


@dataclass
class Patient(DevelopmentMixin, MeasurementMixin, AgeMixin):
    sex: DataSexType
    birthday_date: dt_date | dt_datetime | None
    gestational_age_weeks: int = 40
    gestational_age_days: int = 0

    measurements: list[MeasurementGroup] = field(default_factory=list)
    z_scores: list[MeasurementGroup] = field(default_factory=list, init=False)

    development_goals: list[DevelopmentGoalGroup] = field(default_factory=list)
    immunization: list[VaccinationRecordGroup] = field(default_factory=list)

    gestational_age: datetime.timedelta = field(init=False)
    is_born: bool = field(init=False)
    is_very_preterm: bool = field(init=False)

    def __post_init__(self):
        self._setup()
        self.calculator = Calculator()
        self.development_calculator = DevelopmentCalculator()
        self.immunization_calculator = ImmunizationCalculator()

    def _setup(self):
        self.is_born = self.birthday_date is not None
        self.gestational_age = datetime.timedelta(weeks=self.gestational_age_weeks, days=self.gestational_age_days)

        if self.is_born:
            self.birthday_date = handle_date(self.birthday_date)
            self.is_very_preterm = self.gestational_age_weeks < 32

    def calculate_all(self) -> None:
        """
        Calculates z-scores for all measurement groups in the patient.
        """

        if self.measurements:
            self.z_scores = [
                self.calculator.calculate_measurement_group(group, self.get_age_with_type(date=group.date)) for group in self.measurements
            ]

        if self.development_goals:
            for dev in self.development_goals:
                age_in_days = self.get_age_with_type(date=dev.date)
                self.development_calculator.validate_measurement_group(dev, age_in_days)

        if self.immunization:
            for record in self.immunization:
                age_in_days = self.get_age_with_type(date=record.date)
                self.immunization_calculator.validate_measurement_group(record, age_in_days)

    @classmethod
    def from_csv(
        cls,
        sex: DataSexType,
        birthday: dt_date | dt_datetime | None,
        csv_path: str,
        gestational_age_weeks: int = 40,
        gestational_age_days: int = 0,
    ) -> "Patient":
        obj = cls(
            birthday_date=birthday,
            sex=sex,
            gestational_age_weeks=gestational_age_weeks,
            gestational_age_days=gestational_age_days,
        )

        # Load measurements from CSV
        obj.load_measurements_from_csv(csv_path)

        return obj
