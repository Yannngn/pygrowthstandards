from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from pygrowthstandards.config import (
    DEVELOPMENT_GOALS,
    DevelopmentGoalType,
    DevelopmentStatusType,
    validator,
)
from pygrowthstandards.config.development import DevelopmentStatus
from pygrowthstandards.oop.utils import AgeMixin
from pygrowthstandards.utils.date_utils import handle_date


@dataclass
class DevelopmentGoal:
    development_goal: DevelopmentGoalType
    date: dt_date | dt_datetime = field(default_factory=dt_datetime.now)

    status: DevelopmentStatusType = field(init=False)

    def __post_init__(self):
        # Validate that the development goal exists in the configuration

        self.date = handle_date(self.date)

        if self.development_goal not in DEVELOPMENT_GOALS:
            raise ValueError(f"Invalid development goal: {self.development_goal}")

    def validate(self, age_in_days: int):
        status = validator.validate_development_goal(self.development_goal, age_in_days, True, True)
        if status is None:
            return
        self.status = status

    def not_achievable(self):
        status = validator.validate_development_goal(self.development_goal, 0, True, False)
        self.status = status or DevelopmentStatus.NOT_ACHIEVABLE  # type: ignore

    def not_verified(self):
        status = validator.validate_development_goal(self.development_goal, 0, False, True)

        self.status = status or DevelopmentStatus.NOT_VERIFIED  # type: ignore


# FIXME: Keep it like that or as a list of str
@dataclass
class DevelopmentGoalGroup:
    developments: list[DevelopmentGoal] = field(default_factory=list)
    date: dt_date | dt_datetime = field(default_factory=dt_datetime.now)

    def __post_init__(self):
        self.date = handle_date(self.date)

    def validate(self, age_in_days: int):
        for dev in self.developments:
            dev.validate(age_in_days)

    def not_achievable(self):
        for dev in self.developments:
            dev.not_achievable()

    def not_verified(self):
        for dev in self.developments:
            dev.not_verified()

    @classmethod
    def from_development_list(
        cls,
        development_list: list[DevelopmentGoalType],
        date: dt_date | dt_datetime | None = None,
    ) -> "DevelopmentGoalGroup":
        if date is None:
            date = dt_datetime.now()

        developments = [DevelopmentGoal(development_goal=goal, date=date) for goal in development_list]
        return cls(developments=developments, date=date)

    @classmethod
    def from_achieved_goals(
        cls,
        *development_goal: DevelopmentGoalType,
        date: dt_date | dt_datetime | None = None,
    ) -> "DevelopmentGoalGroup":
        if date is None:
            date = dt_datetime.now()

        developments = [DevelopmentGoal(development_goal=goal, date=date) for goal in development_goal]
        return cls(developments=developments, date=date)


class DevelopmentMixin(AgeMixin):
    development_goals: list[DevelopmentGoalGroup]

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
        for group in self.development_goals:
            if group.date == development_goal.date:
                # Update the existing group
                for existing_goal in group.developments:
                    if existing_goal.development_goal == development_goal.development_goal:
                        existing_goal.date = development_goal.date
                        return
                # If the goal doesn't exist in the group, add it
                group.developments.append(development_goal)
                return

        # If no group with the same date exists, create a new group
        new_group = DevelopmentGoalGroup(developments=[development_goal], date=development_goal.date)
        self.development_goals.append(new_group)

    def add_development_achievements(self, development_goal_group: DevelopmentGoalGroup) -> None:
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
        for group in self.development_goals:
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
        self.development_goals.append(development_goal_group)

    def display_development_achievements(self) -> str:
        """
        Display the development achievements of the patient.

        Returns
        -------
        str
            A formatted string showing the development achievements.
        """
        if not self.development_goals:
            return "No development achievements available."

        # Sort development groups by date
        sorted_developments = sorted(self.development_goals, key=lambda group: group.date)

        results = []
        for group in sorted_developments:
            group_date = group.date.strftime("%Y-%m-%d")
            results.append(f"Date: {group_date}")

            for goal in group.developments:
                goal_config = DEVELOPMENT_GOALS.get(goal.development_goal)
                description = goal_config.description if goal_config else "Unknown goal"
                results.append(f"  - Goal: {goal.development_goal}")
                results.append(f"    Description: {description}")
                results.append(f"    Achieved on: {goal.date.strftime('%Y-%m-%d')}")

        return "\n".join(results)
