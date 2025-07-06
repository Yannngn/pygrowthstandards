import datetime
from typing import Literal

from dateutil.relativedelta import relativedelta

from src.utils.constants import WEEK


class Child:
    def __init__(
        self,
        birthday_date: datetime.date,
        sex: Literal["M", "F", "U"] = "U",
        gestational_age_weeks: int | None = None,
        gestational_age_days: int | None = None,
    ):
        """
        Initializes a child instance. Can be used with very preterm childs (gestational age < 32 weeks).
        Gestational age is optional, but if provided, it will be used to calculate the last menstrual date (LMD)
        Chronological age will also be calculated if the child is very preterm until 64 weeks of age.

        :param birthday_date: The date of birth of the child.
        :param gestational_age_weeks: The gestational age in weeks (optional).
        :param gestational_age_days: The gestational age in days (optional).
        """
        self.sex = sex
        self.birthday_date: datetime.date = birthday_date

        self.is_very_preterm: bool | None = None
        self.gestational_age: datetime.timedelta | None = None

        if gestational_age_weeks is not None:
            weeks = gestational_age_weeks or 0
            days = gestational_age_days or 0

            self.gestational_age = datetime.timedelta(weeks=weeks, days=days)

            self.is_very_preterm = gestational_age_weeks < 32

        self._setup()

    def _setup(self):
        self.term = self._get_term_status()
        self.lmp_date = None

        if self.gestational_age:
            self.lmp_date = self.birthday_date - self.gestational_age

            self.is_very_preterm = self.gestational_age.days < 32 * WEEK

        self.chronological_age = None

        if self.is_very_preterm:
            self.chronological_age = self._get_chronological_age()

    def set_gestational_age(self, gestational_age_weeks: int, gestational_age_days: int = 0):
        self.gestational_age = datetime.timedelta(weeks=gestational_age_weeks, days=gestational_age_days)

        self._setup()

    def age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Returns the age in days on a specific date."""

        if date is None:
            date = datetime.date.today()

        if self.is_very_preterm:
            if self.lmp_date is None:
                raise ValueError("LMP date is not set. Cannot calculate age for very preterm child.")

            age = date - self.lmp_date

            if age.days <= 64 * WEEK:
                return age

        return date - self.birthday_date

    def _get_term_status(self, simplified: bool = False):
        if self.gestational_age is None:
            return None

        ga_days = self.gestational_age.days

        if simplified:
            if ga_days < 37 * WEEK:
                return "preterm"

            if ga_days < 42 * WEEK:
                return "term"

            return "postterm"

        if ga_days < 28 * WEEK:
            return "extreme_preterm"

        if ga_days < 32 * WEEK:
            return "very_preterm"

        if ga_days < 34 * WEEK:
            return "moderate_preterm"

        if ga_days < 37 * WEEK:
            return "late_preterm"

        if ga_days < 39 * WEEK:
            return "early_term"

        if ga_days < 42 * WEEK:
            return "full_term"

        return "postterm"

    def _get_chronological_age(self) -> datetime.timedelta:
        if self.lmp_date is None:
            raise ValueError("Gestational age must be given to calculate chronological age.")

        # Calculate the chronological age
        current_date = datetime.date.today()
        return current_date - self.lmp_date

    def __str__(self):
        age = self.age()

        end_date = self.birthday_date + age
        delta = relativedelta(end_date, self.birthday_date)
        return f"child(birthday_date={self.birthday_date.strftime('%d-%m-%Y')}, age={delta.years}y {delta.months}m {delta.days}d)"

    def _get_birth_weight_status(self, weight_kg: float):
        if weight_kg < 1.0:
            return "extreme_low_birth_weight"

        if weight_kg < 1.5:
            return "very_low_birth_weight"

        if weight_kg < 2.5:
            return "low_birth_weight"

        return "normal_birth_weight"
