from datetime import date as dt_date
from datetime import datetime as dt_datetime
from datetime import timedelta

from pygrowthstandards.config import (
    AgeGroupType,
    validator,
)
from pygrowthstandards.config.growth import AgeGroup
from pygrowthstandards.utils.date_utils import handle_date, weeks_to_days


class AgeMixin:
    birthday_date: dt_date | dt_datetime | None
    gestational_age: timedelta

    def age(self, date: dt_date | dt_datetime | None = None) -> timedelta:
        """Age from birth"""
        date = handle_date(date)

        assert self.birthday_date is not None, "Patient must be born to calculate age."

        date = date or dt_date.today()

        assert date >= self.birthday_date, "Date must be after the birthday date."

        return date - self.birthday_date  # type: ignore

    def corrected_age(self, date: dt_date | dt_datetime | None = None) -> timedelta:
        """
        Calculates the corrected age for very preterm children.

        - If the child is not born, returns the gestational age.
        - If the child is born and corrected age < 64 weeks, returns the corrected age.
        - If the child is born and corrected age >= 64 weeks, returns the post-birth age.

        Parameters
        ----------
        date : dt_date | None
            The reference date for age calculation. Defaults to today.

        Returns
        -------
        timedelta
            The corrected age or post-birth age, depending on the child's age.
        """
        date = handle_date(date)

        if self.birthday_date is not None:
            age = self.age(date) + self.gestational_age
            if age.days > weeks_to_days(64):
                return self.age(date)

            return age

        return date - self.gestational_age  # type: ignore

    def get_age_with_type(self, age_type: str = "age", date: dt_date | dt_datetime | None = None) -> int:
        if age_type == "age":
            return self.age(date).days

        if age_type == "corrected_age":
            return self.corrected_age(date).days

        if age_type == "gestational_age":
            return self.gestational_age.days

        raise ValueError(f"Invalid age type: {age_type}. Use 'age', 'gestational_age', or 'corrected_age'.")

    def get_age_for_age_group(self, age_group: AgeGroupType, date: dt_date | dt_datetime | None = None) -> int:
        age_type = self._get_age_type(age_group)
        return self.get_age_with_type(age_type, date=date)

    def _get_age_group(self, date: dt_date | dt_datetime | None):
        age_group = validator.get_age_group_from_ages(
            age=self.get_age_with_type("age", date=date),
            gestational_age=self.get_age_with_type("gestational_age", date=date),
        )

        print(f"age={self.get_age_with_type('age', date=date)}, gestational_age={self.get_age_with_type('gestational_age', date=date)}")

        assert age_group is not None, "No valid age group found for the given ages."

        return age_group

    @staticmethod
    def _get_age_type(age_group: AgeGroupType) -> str:
        if age_group in [AgeGroup.VERY_PRETERM_NEWBORN, AgeGroup.NEWBORN]:
            return "gestational_age"
        if age_group in [AgeGroup.VERY_PRETERM_GROWTH]:
            return "corrected_age"

        return "age"

    # @staticmethod
    # def _get_age_type(table_name: str) -> str:
    #     if table_name in ["very_preterm_newborn", "newborn"]:
    #         return "gestational_age"
    #     if table_name in ["very_preterm_growth"]:
    #         return "corrected_age"

    #     return "age"
