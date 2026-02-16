"""Developmental milestone configuration and lookup data."""

from typing import Literal, TypeAlias

DataSourceType: TypeAlias = Literal["cdc", "brazil"]

MilestoneDomainType: TypeAlias = Literal[
    "MOTOR_GROSS",
    "MOTOR_FINE", 
    "SOCIAL_EMOTIONAL",
    "COMMUNICATION",
    "COGNITIVE",
    "SENSORY",
]

StatisticalThresholdType: TypeAlias = Literal["P25_90", "P75"]

AchievementStatusType: TypeAlias = Literal["achieved", "not_achieved", "not_assessed"]
