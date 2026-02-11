from dataclasses import dataclass, field
from datetime import datetime as dt_datetime

from pygrowthstandards.config.development import (
    DEVELOPMENT_GOALS,
    DevelopmentGoalType,
    DevelopmentStatusType,
)
from pygrowthstandards.utils.constants import MONTH, WEEK, YEAR
from pygrowthstandards.utils.date import DateInputType, handle_date_input

# TODO: should development store the child age, or should it be only responsible for the goal and the assessment date?


@dataclass
class DevelopmentGoal:
    goal: DevelopmentGoalType
    date: DateInputType = field(default_factory=dt_datetime.now)

    status: DevelopmentStatusType = field(init=False)

    def __post_init__(self):
        # Validate that the development goal exists in the configuration

        self.date = handle_date_input(self.date)

        if self.goal not in DEVELOPMENT_GOALS:
            raise ValueError(f"Invalid development goal: {self.goal}")

    def validate(self, age: int, gestational_age: int | None = None):
        goal_config = DEVELOPMENT_GOALS[self.goal]

        # TODO: review this logic, and move it to config.development
        # For preterm infants, we need to correct the age based on gestational age
        # Before 64 weeks PMA, use corrected age; at/after 64 weeks PMA, use chronological age

        if (
            gestational_age is not None and gestational_age < 32 * WEEK and age < 3 * YEAR
        ):  # TODO: review threshold for preterm classification on the development context
            # (weeks premature)
            age -= 40 * WEEK - gestational_age  # age = chronological age - (40 weeks - gestational age)

        child_age_months = age / MONTH

        # TODO: review thresholds for "slightly delayed" and "delayed" status // Using Brazil MS guidelines
        if child_age_months <= goal_config.max_age_months:
            return "on_time"

        if child_age_months <= goal_config.max_age_months + 1:
            return "slightly_delayed"

        return "delayed"


# FIXME: Keep it like that or as a list of str
@dataclass
class DevelopmentGoalGroup:
    goals: list[DevelopmentGoal] = field(default_factory=list)
    date: DateInputType = field(default_factory=dt_datetime.now)

    def __post_init__(self):
        self.date = handle_date_input(self.date)

    def validate(self, age: int, gestational_age: int | None = None):
        for dev in self.goals:
            dev.validate(age, gestational_age)

    @classmethod
    def from_development_list(cls, development_list: list[DevelopmentGoalType], date: DateInputType | None = None) -> "DevelopmentGoalGroup":
        _date = handle_date_input(date)

        goals = [DevelopmentGoal(goal=goal, date=_date) for goal in development_list]
        return cls(goals=goals, date=_date)

    @classmethod
    def from_achieved_goals(cls, *development_goal: DevelopmentGoalType, date: DateInputType | None = None) -> "DevelopmentGoalGroup":
        _date = handle_date_input(date)

        goals = [DevelopmentGoal(goal=goal, date=_date) for goal in development_goal]
        return cls(goals=goals, date=_date)
