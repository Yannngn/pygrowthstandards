import datetime
from dataclasses import dataclass, field
from typing import Literal

from src.oop.calculator import Calculator
from src.oop.measurement import Measurement, MeasurementGroup
from src.utils.results import str_dataframe


@dataclass
class Patient:
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
        assert self.birthday_date is not None, "Patient must be born to calculate age."

        date = date or datetime.date.today()

        assert date >= self.birthday_date, "Date must be after the birthday date."

        return date - self.birthday_date

    def chronological_age(self, date: datetime.date | None = None) -> datetime.timedelta:
        date = date or datetime.date.today()

        if self.birthday_date is not None:
            age = date - (self.birthday_date - self.gestational_age)
            if age.days > 64:
                return self.age(date)

            return age

        return date - self.gestational_age  # type: ignore

    def get_age(self, age_type: str = "age", date: datetime.date | None = None) -> int:
        if age_type == "age":
            return self.age(date).days
        elif age_type == "gestational_age":
            return self.gestational_age.days
        elif age_type == "chronological_age":
            return self.chronological_age(date).days

        raise ValueError(f"Invalid age type: {age_type}. Use 'age', 'gestational_age', or 'chronological_age'.")

    def add_measurement(self, measurement: Measurement) -> None:

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
        self.measurements.append(measurements)

    def calculate_all(self) -> None:
        """
        Calculates z-scores for all measurement groups in the patient.
        """
        self.z_scores = [self.calculator.calculate_measurement_group(group, self.get_age(date=group.date)) for group in self.measurements]

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
        self.is_born = self.birthday_date is not None
        self.gestational_age = datetime.timedelta(weeks=self.gestational_age_weeks, days=self.gestational_age_days)

        if self.is_born:
            self.is_very_preterm = self.gestational_age_weeks < 32

    @staticmethod
    def _get_age_type(table_name: str) -> str:
        if table_name in ["very_preterm_newborn", "newborn"]:
            return "gestational_age"
        if table_name in ["very_preterm_growth"]:
            return "chronological_age"

        return "age"
