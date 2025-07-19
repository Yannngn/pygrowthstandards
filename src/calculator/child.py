import datetime
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Fetus:
    def __post_init__(self):
        raise NotImplementedError("Fetus class is not implemented yet.")


@dataclass
class Child:
    sex: Literal["M", "F", "U"]
    birthday_date: datetime.date
    gestational_age_weeks: int = 40
    gestational_age_days: int = 0

    gestational_age: datetime.timedelta = field(init=False)
    is_very_preterm: bool = field(init=False)

    def __post_init__(self):
        self.gestational_age = datetime.timedelta(weeks=self.gestational_age_weeks, days=self.gestational_age_days)
        self.is_very_preterm = self.gestational_age_weeks < 32

    def age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Returns the age in days on a specific date."""
        date = date or datetime.date.today()
        assert date >= self.birthday_date, "Date must be after the birthday date."

        return date - self.birthday_date

    def chronological_age(self, date: datetime.date | None = None) -> datetime.timedelta:
        """Returns the chronological age in days on a specific date."""

        date = date or datetime.date.today()
        return date - (self.birthday_date - self.gestational_age)
        return date - (self.birthday_date - self.gestational_age)
