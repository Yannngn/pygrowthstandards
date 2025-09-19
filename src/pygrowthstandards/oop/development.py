from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from pygrowthstandards.config import (
    DEVELOPMENT_GOALS,
    DevelopmentGoalType,
    DevelopmentStatusType,
)
from pygrowthstandards.utils.constants import MONTH
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

    def validate(self, birth_date: dt_date | dt_datetime):
        goal_config = DEVELOPMENT_GOALS[self.development_goal]
        child_age_months = (self.date - handle_date(birth_date)).days / MONTH

        if child_age_months <= goal_config.max_age_months:
            return "on_time"
        elif child_age_months <= goal_config.max_age_months + 1:
            return "slightly_delayed"
        else:
            return "delayed"


# FIXME: Keep it like that or as a list of str
@dataclass
class DevelopmentGoalGroup:
    developments: list[DevelopmentGoal] = field(default_factory=list)
    date: dt_date | dt_datetime = field(default_factory=dt_datetime.now)

    def __post_init__(self):
        self.date = handle_date(self.date)

    def validate(self, birth_date: dt_date | dt_datetime):
        for dev in self.developments:
            dev.validate(birth_date)

    @classmethod
    def from_development_list(
        cls,
        development_list: list[DevelopmentGoalType],
        date: dt_date | dt_datetime | None = None,
    ) -> "DevelopmentGoalGroup":
        if date is None:
            date = dt_datetime.now()

        developments = [
            DevelopmentGoal(development_goal=goal, date=date)
            for goal in development_list
        ]
        return cls(developments=developments, date=date)

    @classmethod
    def from_achieved_goals(
        cls,
        *development_goal: DevelopmentGoalType,
        date: dt_date | dt_datetime | None = None,
    ) -> "DevelopmentGoalGroup":
        if date is None:
            date = dt_datetime.now()

        developments = [
            DevelopmentGoal(development_goal=goal, date=date)
            for goal in development_goal
        ]
        return cls(developments=developments, date=date)
