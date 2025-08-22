from dataclasses import dataclass
from decimal import Decimal as D
from enum import StrEnum
from typing import Literal

from .constants import WEEK, YEAR

# Templates
X_TEMPLATE = D("0.00")
MU_TEMPLATE = D("0.0000")
LAMBDA_TEMPLATE = D("0.0000")
SIGMA_TEMPLATE = D("0.00000")


class DataSource(StrEnum):
    WHO = "who"
    INTERGROWTH = "intergrowth"


class DataSex(StrEnum):
    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class DataXType(StrEnum):
    AGE = "age"
    GESTATIONAL_AGE = "gestational_age"
    STATURE = "stature"


class MeasurementType(StrEnum):
    STATURE = "stature"
    WEIGHT = "weight"
    WEIGHT_STATURE = "weight_stature"
    HEAD_CIRCUMFERENCE = "head_circumference"
    BODY_MASS_INDEX = "body_mass_index"
    WEIGHT_VELOCITY = "weight_velocity"
    STATURE_VELOCITY = "stature_velocity"
    HEAD_CIRCUMFERENCE_VELOCITY = "head_circumference_velocity"


class AgeGroup(StrEnum):
    ZERO_ONE = "0-1"
    ZERO_TWO = "0-2"
    TWO_FIVE = "2-5"
    FIVE_TEN = "5-10"
    TEN_NINETEEN = "10-19"
    NEWBORN = "newborn"
    VERY_PRETERM_NEWBORN = "very_preterm_newborn"
    VERY_PRETERM_GROWTH = "very_preterm_growth"


# Type aliases using the enums
DataSourceType = Literal["who", "intergrowth"]
DataSexType = Literal["M", "F", "U"]
DataXTypeType = Literal["age", "gestational_age", "stature"]
MeasurementTypeType = Literal[
    "stature",
    "weight",
    "weight_stature",
    "head_circumference",
    "body_mass_index",
    "weight_velocity",
    "stature_velocity",
    "head_circumference_velocity",
]
AgeGroupType = Literal[
    "0-1",
    "0-2",
    "2-5",
    "5-10",
    "10-19",
    "newborn",
    "very_preterm_newborn",
    "very_preterm_growth",
]
TableNameType = Literal[
    "growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"
]


@dataclass(frozen=True)
class AgeGroupConfig:
    """Configuration for age groups with limits, x_type, and table name."""

    limits: tuple[int, int]
    x_type: DataXTypeType
    table_name: TableNameType

    def contains_age(self, age: int) -> bool:
        return self.limits[0] <= age <= self.limits[1]


@dataclass(frozen=True)
class MeasurementConfig:
    """Configuration for measurements with units and aliases."""

    unit: str
    aliases: frozenset[str] = frozenset()

    def matches_alias(self, alias: str) -> bool:
        return alias.lower() in self.aliases or alias == self.unit


# Configuration mappings
AGE_GROUP_CONFIG: dict[AgeGroupType, AgeGroupConfig] = {
    AgeGroup.VERY_PRETERM_NEWBORN: AgeGroupConfig(
        (168, 230), "gestational_age", "very_preterm_newborn"
    ),
    AgeGroup.NEWBORN: AgeGroupConfig((230, 300), "gestational_age", "newborn"),
    AgeGroup.VERY_PRETERM_GROWTH: AgeGroupConfig(
        (27 * WEEK, 64 * WEEK), "gestational_age", "very_preterm_growth"
    ),
    AgeGroup.ZERO_ONE: AgeGroupConfig((0, int(round(1 * YEAR))), "age", "child_growth"),
    AgeGroup.ZERO_TWO: AgeGroupConfig((0, int(round(2 * YEAR))), "age", "child_growth"),
    AgeGroup.TWO_FIVE: AgeGroupConfig(
        (int(round(2 * YEAR)) + 1, int(round(5 * YEAR))), "age", "child_growth"
    ),
    AgeGroup.FIVE_TEN: AgeGroupConfig(
        (int(round(5 * YEAR)) + 1, int(round(10 * YEAR))), "age", "growth"
    ),
    AgeGroup.TEN_NINETEEN: AgeGroupConfig(
        (int(round(10 * YEAR)) + 1, int(round(19 * YEAR))), "age", "growth"
    ),
}  # type: ignore

MEASUREMENT_CONFIG: dict[MeasurementTypeType, MeasurementConfig] = {
    MeasurementType.STATURE: MeasurementConfig(
        "cm", frozenset({"lfa", "hfa", "lhfa", "sfa", "l", "h", "s"})
    ),
    MeasurementType.WEIGHT: MeasurementConfig("kg", frozenset({"wfa", "w"})),
    MeasurementType.HEAD_CIRCUMFERENCE: MeasurementConfig(
        "cm", frozenset({"hcfa", "hc"})
    ),
    MeasurementType.BODY_MASS_INDEX: MeasurementConfig(
        "kg/m²", frozenset({"bmi", "bfa"})
    ),
    MeasurementType.WEIGHT_STATURE: MeasurementConfig(
        "kg/cm",
        frozenset(
            {
                "wfs",
                "wfl",
                "wfh",
                "weight_length",
                "weight_height",
                "weight_for_stature",
                "weight_for_length",
                "weight_for_height",
            }
        ),
    ),
    MeasurementType.STATURE_VELOCITY: MeasurementConfig("cm/month"),
    MeasurementType.WEIGHT_VELOCITY: MeasurementConfig("kg/month"),
    MeasurementType.HEAD_CIRCUMFERENCE_VELOCITY: MeasurementConfig("cm/month"),
}  # type: ignore


class ChoiceValidator:
    """Utility class for validating and resolving choices."""

    @staticmethod
    def resolve_measurement_alias(alias: str) -> MeasurementTypeType | None:
        """Resolve measurement alias to canonical name."""
        alias_lower = alias.lower()
        for measurement, config in MEASUREMENT_CONFIG.items():
            # compare against the enum value (string) and configured aliases/units
            if measurement == alias_lower or config.matches_alias(alias_lower):
                return measurement
        return None

    @staticmethod
    def get_age_group_for_age(age: int, x_type: DataXTypeType) -> AgeGroupType | None:
        """Find the appropriate age group for given age and x_type."""
        for age_group, config in AGE_GROUP_CONFIG.items():
            if config.x_type == x_type and config.contains_age(age):
                return age_group
        return None

    @staticmethod
    def validate_choice(value: str, choices: frozenset[str]) -> bool:
        """Validate if value is in choices."""
        return value in choices

    @staticmethod
    def get_measurement_unit(measurement: MeasurementTypeType) -> str:
        """Get unit for measurement type."""
        return MEASUREMENT_CONFIG[measurement].unit


# Convenience functions
def resolve_measurement(alias: str) -> MeasurementTypeType:
    """Resolve measurement alias with error handling."""
    result = ChoiceValidator.resolve_measurement_alias(alias)
    if result is None:
        raise ValueError(f"Unknown measurement alias: {alias}")
    return result


def get_age_group(age: int, x_type: DataXTypeType = "age") -> AgeGroupType:
    """Get age group with error handling."""
    result = ChoiceValidator.get_age_group_for_age(age, x_type)
    if result is None:
        raise ValueError(f"No age group found for age {age} with x_type {x_type}")
    return result


# Backward compatibility - keep existing variables
DATA_SOURCE_CHOICES = frozenset([e.value for e in DataSource])
DATA_SEX_CHOICES = frozenset([e.value for e in DataSex])
DATA_X_CHOICES = frozenset([e.value for e in DataXType])
MEASUREMENT_TYPE_CHOICES = frozenset([e.value for e in MeasurementType])
AGE_GROUP_CHOICES = frozenset([e.value for e in AgeGroup])

# Legacy dictionaries (derived from configs)
UNITS = {measurement: config.unit for measurement, config in MEASUREMENT_CONFIG.items()}
AGE_GROUP_LIMITS = {
    age_group: config.limits for age_group, config in AGE_GROUP_CONFIG.items()
}
AGE_GROUP_X = {
    age_group: config.x_type for age_group, config in AGE_GROUP_CONFIG.items()
}
AGE_GROUP_TABLE_NAME = {
    age_group: config.table_name for age_group, config in AGE_GROUP_CONFIG.items()
}
MEASUREMENT_ALIASES = {
    measurement: config.aliases
    for measurement, config in MEASUREMENT_CONFIG.items()
    if config.aliases
}
