from typing import Self

from pygrowthstandards.oop.measurement import MeasurementGroup
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.utils.config import DataSexType
from pygrowthstandards.utils.date import DateInputType, handle_date_input


class PatientBuilder:
    """Builder class for creating Patient instances with a fluent interface."""

    patient: Patient
    measurements: list[MeasurementGroup]

    def __init__(self):
        self.measurements = []

    def build(self) -> Self:
        self.patient = Patient(
            getattr(self, "sex", "U"),
            getattr(self, "birthday_date", None),
            getattr(self, "gestational_age_weeks", 40),
            getattr(self, "gestational_age_days", 0),
            measurements=self.measurements,
        )
        return self

    def calculate(self) -> Self:
        # Guard: ensure `build()` has been called before `calculate()`
        if not hasattr(self, "patient") or self.patient is None:
            raise RuntimeError("build() must be called before calculate() - call PatientBuilder.build() first")

        self.patient.calculate_all()
        return self

    def build_and_calculate(self) -> Patient:
        return self.build().calculate().patient

    def with_sex(self, sex: DataSexType) -> Self:
        self.sex = sex
        return self

    def born_on(self, birthday_date: DateInputType) -> Self:
        self.birthday_date = handle_date_input(birthday_date)

        return self

    def gestational_age(self, weeks: int, days: int = 0) -> Self:
        self.gestational_age_weeks = weeks
        self.gestational_age_days = days
        return self

    def measured_at(
        self,
        date: DateInputType,
        weight: float | None = None,
        stature: float | None = None,
        head_circumference: float | None = None,
    ) -> Self:
        measurement_date = handle_date_input(date)

        measurement_group = MeasurementGroup(
            date=measurement_date,
            weight=weight,
            stature=stature,
            head_circumference=head_circumference,
        )

        self.measurements.append(measurement_group)
        return self
