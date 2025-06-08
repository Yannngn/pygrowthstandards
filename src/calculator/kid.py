import datetime
from typing import Literal

from dateutil.relativedelta import relativedelta


class Kid:
    def __init__(
        self,
        birthday_date: datetime.date,
        sex: Literal["M", "F", "U"] = "U",
        gestational_age_weeks: int | None = None,
        gestational_age_days: int | None = None,
    ):
        """
        Initializes a Kid instance. Can be used with very preterm kids (gestational age < 32 weeks).
        Gestational age is optional, but if provided, it will be used to calculate the last menstrual date (LMD)
        Chronological age will also be calculated if the kid is very preterm until 64 weeks of age.

        :param birthday_date: The date of birth of the kid.
        :param gestational_age_weeks: The gestational age in weeks (optional).
        :param gestational_age_days: The gestational age in days (optional).
        """
        self.sex = sex
        self.birthday_date: datetime.date = birthday_date
        self.gestational_age_weeks: int | None = gestational_age_weeks
        self.gestational_age_days: int | None = gestational_age_days

        self._setup()

    def _setup(self):
        self.term = self._get_term_status()

        self.is_very_preterm = None
        self.lmd = None
        self.chronological_age = None

        if self.gestational_age_weeks is not None:
            self.lmfd = self._get_lmd()
            self.is_very_preterm = self.gestational_age_weeks < 32

        if self.is_very_preterm:
            self.chronological_age = self._get_chronological_age()

    def age_on_date(
        self, date: datetime.date = datetime.date.today()
    ) -> datetime.timedelta:
        """Returns the age in days on a specific date."""
        if self.is_very_preterm:
            age = date - self._get_lmd()

            if age.days <= 64 * 7:
                return age

        age = date - self.birthday_date

        return age

    def age_days(self, date: datetime.date = datetime.date.today()) -> int:
        return self.age_on_date(date).days

    def get_birth_weight_status(self, weight_kg: float | None):
        if weight_kg is None:
            return None

        if weight_kg < 1.0:
            return "extreme_low_birth_weight"

        if weight_kg < 1.5:
            return "very_low_birth_weight"

        if weight_kg < 2.5:
            return "low_birth_weight"

        return "normal_birth_weight"

    def _get_lmd(self) -> datetime.date:
        if self.gestational_age_weeks is None and self.gestational_age_days is None:
            raise ValueError("Gestational age must be set to calculate LMD.")

        # Calculate the last menstrual date (LMD)
        lmd = self.birthday_date - datetime.timedelta(
            weeks=self.gestational_age_weeks or 0, days=self.gestational_age_days or 0
        )
        return lmd

    def _get_term_status(self, simplified: bool = False):
        if self.gestational_age_weeks is None:
            return None

        if simplified:
            if self.gestational_age_weeks < 37:
                return "preterm"
            if self.gestational_age_weeks < 42:
                return "term"

            return "postterm"

        if self.gestational_age_weeks < 28:
            return "extreme_preterm"

        if self.gestational_age_weeks < 32:
            return "very_preterm"

        if self.gestational_age_weeks < 34:
            return "moderate_preterm"

        if self.gestational_age_weeks < 37:
            return "late_preterm"

        if self.gestational_age_weeks < 39:
            return "early_term"

        if self.gestational_age_weeks < 42:
            return "full_term"

        return "postterm"

    def _get_chronological_age(self) -> datetime.timedelta:
        if self.gestational_age_weeks is None:
            raise ValueError(
                "Gestational age must be set to calculate chronological age."
            )

        # Calculate the chronological age
        lmd = self._get_lmd()
        current_date = datetime.date.today()
        return current_date - lmd

    def __str__(self):
        age = self.age_on_date()

        end_date = self.birthday_date + age
        delta = relativedelta(end_date, self.birthday_date)
        return f"Kid(birthday_date={self.birthday_date.strftime('%d-%m-%Y')}, age={delta.years}y {delta.months}m {delta.days}d)"
