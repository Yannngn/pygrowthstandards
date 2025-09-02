import csv
import datetime
from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from pygrowthstandards.oop.development import DevelopmentGoal, DevelopmentGoalGroup
from pygrowthstandards.utils.config import (
    AgeGroup,
    AgeGroupType,
    ChoiceValidator,
    DataSexType,
)
from pygrowthstandards.utils.constants import WEEK
from pygrowthstandards.utils.date_utils import handle_date

from ..utils.results import str_dataframe
from .calculator import Calculator
from .measurement import Measurement, MeasurementGroup


@dataclass
class Patient:
    sex: DataSexType
    birthday_date: dt_date | dt_datetime | None
    gestational_age_weeks: int = 40
    gestational_age_days: int = 0

    measurements: list[MeasurementGroup] = field(default_factory=list)
    z_scores: list[MeasurementGroup] = field(default_factory=list, init=False)

    developments: list[DevelopmentGoalGroup] = field(default_factory=list)

    gestational_age: datetime.timedelta = field(init=False)
    is_born: bool = field(init=False)
    is_very_preterm: bool = field(init=False)

    def __post_init__(self):
        self._setup()
        self.calculator = Calculator()

    def age(self, date: dt_date | dt_datetime | None = None) -> datetime.timedelta:
        """Age from birth"""
        date = handle_date(date)

        assert self.birthday_date is not None, "Patient must be born to calculate age."

        date = date or dt_date.today()

        assert date >= self.birthday_date, "Date must be after the birthday date."

        return date - self.birthday_date  # type: ignore

    def corrected_age(
        self, date: dt_date | dt_datetime | None = None
    ) -> datetime.timedelta:
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
        datetime.timedelta
            The corrected age or post-birth age, depending on the child's age.
        """
        date = handle_date(date)

        if self.birthday_date is not None:
            age = self.age(date) + self.gestational_age
            if age.days > 64 * WEEK:
                return self.age(date)

            return age

        return date - self.gestational_age  # type: ignore

    def get_age_with_type(
        self, age_type: str = "age", date: dt_date | dt_datetime | None = None
    ) -> int:
        if age_type == "age":
            return self.age(date).days

        if age_type == "corrected_age":
            return self.corrected_age(date).days

        if age_type == "gestational_age":
            return self.gestational_age.days

        raise ValueError(
            f"Invalid age type: {age_type}. Use 'age', 'gestational_age', or 'corrected_age'."
        )

    def get_age_for_age_group(
        self, age_group: AgeGroupType, date: dt_date | dt_datetime | None = None
    ) -> int:
        age_type = self._get_age_type(age_group)
        return self.get_age_with_type(age_type, date=date)

    def add_measurement(self, measurement: Measurement) -> None:
        for group in self.measurements:
            if group.date == measurement.date:
                setattr(group, measurement.measurement_type, measurement.value)
                group._setup()
                return

        age_group = self._get_age_group(date=measurement.date)
        measurement.age_group = age_group

        new_group = MeasurementGroup(
            date=measurement.date,
            **{measurement.measurement_type: measurement.value},  # type: ignore
        )
        new_group.age_group = age_group
        self.measurements.append(new_group)

    def add_measurements(self, measurements: MeasurementGroup) -> None:
        if measurements.age_group is None:
            measurements.age_group = self._get_age_group(date=measurements.date)

        self.measurements.append(measurements)

    def add_development_achievement(self, development_goal: DevelopmentGoal) -> None:
        """
        Add a single development achievement to the patient's development goals.

        If a DevelopmentGoalGroup with the same date already exists, update it.
        Otherwise, create a new DevelopmentGoalGroup for the given date.

        Parameters
        ----------
        development_goal : DevelopmentGoal
            The development goal to add.

        Returns
        -------
        None
        """
        for group in self.developments:
            if group.date == development_goal.date:
                # Update the existing group
                for existing_goal in group.developments:
                    if (
                        existing_goal.development_goal
                        == development_goal.development_goal
                    ):
                        existing_goal.date = development_goal.date
                        return
                # If the goal doesn't exist in the group, add it
                group.developments.append(development_goal)
                return

        # If no group with the same date exists, create a new group
        new_group = DevelopmentGoalGroup(
            developments=[development_goal], date=development_goal.date
        )
        self.developments.append(new_group)

    def add_development_achievements(
        self, development_goal_group: DevelopmentGoalGroup
    ) -> None:
        """
        Add multiple development achievements to the patient's development goals.

        If a DevelopmentGoalGroup with the same date already exists, update it.
        Otherwise, append the new DevelopmentGoalGroup.

        Parameters
        ----------
        development_goal_group : DevelopmentGoalGroup
            A group of development goals to add.

        Returns
        -------
        None
        """
        for group in self.developments:
            if group.date == development_goal_group.date:
                # Update the existing group
                for new_goal in development_goal_group.developments:
                    for existing_goal in group.developments:
                        if existing_goal.development_goal == new_goal.development_goal:
                            existing_goal.date = new_goal.date
                            break
                    else:
                        # If the goal doesn't exist in the group, add it
                        group.developments.append(new_goal)
                return

        # If no group with the same date exists, append the new group
        self.developments.append(development_goal_group)

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

    def calculate_all(self) -> None:
        """
        Calculates z-scores for all measurement groups in the patient.
        """
        self.z_scores = [
            self.calculator.calculate_measurement_group(
                group, self.get_age_with_type(date=group.date)
            )
            for group in self.measurements
        ]

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
            assert m_group.age_group is not None, (
                "No valid age group found for the given ages."
            )
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

        return str_dataframe(
            results=results_list, date_list=date_list, age_list=age_list
        )

    def _setup(self):
        self.is_born = self.birthday_date is not None
        self.gestational_age = datetime.timedelta(
            weeks=self.gestational_age_weeks, days=self.gestational_age_days
        )

        if self.is_born:
            self.birthday_date = handle_date(self.birthday_date)
            self.is_very_preterm = self.gestational_age_weeks < 32

    def _get_age_group(self, date: dt_date | dt_datetime | None):
        age_group = ChoiceValidator.get_age_group_from_ages(
            age=self.get_age_with_type("age", date=date),
            gestational_age=self.get_age_with_type("gestational_age", date=date),
        )
        print(
            f"age={self.get_age_with_type('age', date=date)}, gestational_age={self.get_age_with_type('gestational_age', date=date)}"
        )
        assert age_group is not None, "No valid age group found for the given ages."
        return age_group

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
