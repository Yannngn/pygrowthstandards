"""Configuration types and lookup helpers for growth standards."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, cast

from pygrowthstandards.utils.constants import WEEK, YEAR


class MeasurementType(StrEnum):
    """Canonical measurement identifiers used across the library."""

    STATURE = "stature"
    WEIGHT = "weight"
    WEIGHT_STATURE_RATIO = "weight_stature_ratio"
    HEAD_CIRCUMFERENCE = "head_circumference"
    BODY_MASS_INDEX = "body_mass_index"
    WEIGHT_VELOCITY = "weight_velocity"
    STATURE_VELOCITY = "stature_velocity"
    HEAD_CIRCUMFERENCE_VELOCITY = "head_circumference_velocity"


class AgeGroup(StrEnum):
    """Supported age group identifiers."""

    ZERO_ONE = "0-1"
    ZERO_TWO = "0-2"
    TWO_FIVE = "2-5"
    FIVE_TEN = "5-10"
    TEN_NINETEEN = "10-19"
    NEWBORN = "newborn"
    VERY_PRETERM_NEWBORN = "very_preterm_newborn"
    POSTNATAL_GROWTH_PRETERM = "postnatal_growth_preterm"


# Type aliases using the enums
DataSourceType = Literal["who", "intergrowth"]
DataSexType = Literal["M", "F", "U"]
DataXTypeType = Literal["age", "gestational_age", "post_menstrual_age", "stature"]

StatureAlias = frozenset(
    [
        "hfa",
        "lfa",
        "lhfa",
        "sfa",
        "h",
        "l",
        "lh",
        "s",
        "height",
        "length",
        "length_height",
        "stature",
        "height_for_age",
        "length_for_age",
        "length_height_for_age",
        "stature_for_age",
    ]
)
StatureAliasType = Literal[
    "hfa",
    "lfa",
    "lhfa",
    "sfa",
    "h",
    "l",
    "lh",
    "s",
    "height",
    "length",
    "length_height",
    "stature",
    "height_for_age",
    "length_for_age",
    "length_height_for_age",
    "stature_for_age",
]
WeightAlias = frozenset(["wfa", "w", "weight"])
WeightAliasType = Literal["wfa", "w", "weight"]

HeadCircumferenceAlias = frozenset(["hcfa", "hc", "head_circumference"])
HeadCircumferenceAliasType = Literal["hcfa", "hc", "head_circumference"]

BodyMassIndexAlias = frozenset(["bmi", "bfa", "body_mass_index"])
BodyMassIndexAliasType = Literal["bmi", "bfa", "body_mass_index"]

WeightStatureAlias = frozenset(
    [
        "wfs",
        "wfl",
        "wfh",
        "weight_length",
        "weight_height",
        "weight_stature",
        "weight_stature_ratio",
        "weight_for_stature",
        "weight_for_length",
        "weight_for_height",
    ]
)
WeightStatureAliasType = Literal[
    "wfs",
    "wfl",
    "wfh",
    "weight_length",
    "weight_height",
    "weight_stature",
    "weight_stature_ratio",
    "weight_for_stature",
    "weight_for_length",
    "weight_for_height",
]

VelocityAlias = frozenset(["weight_velocity", "length_velocity", "head_circumference_velocity", "stature_velocity"])
VelocityAliasType = Literal["weight_velocity", "length_velocity", "head_circumference_velocity", "stature_velocity"]

MeasurementAliasType = (
    StatureAliasType | WeightAliasType | HeadCircumferenceAliasType | BodyMassIndexAliasType | WeightStatureAliasType | VelocityAliasType
)

AgeGroupType = Literal[
    "0-1",
    "0-2",
    "2-5",
    "5-10",
    "10-19",
    "newborn",
    "very_preterm_newborn",
    "postnatal_growth_preterm",
]

TableNameType = Literal["growth", "child_growth", "postnatal_growth_preterm", "very_preterm_newborn", "newborn"]


@dataclass(frozen=True)
class AgeGroupConfig:
    """Configuration for an age group slice of reference data.

    Attributes:
        name: Canonical age group key.
        limits: Inclusive min/max bounds in days.
        x_type: Axis type associated with the group.
        table_name: Reference table name.
    """

    name: AgeGroupType
    limits: tuple[int, int]
    x_type: DataXTypeType
    table_name: TableNameType

    def contains_age(self, age: int) -> bool:
        """Check whether the age is within the configured limits.

        Args:
            age: Age in days.

        Returns:
            True when the age is within the inclusive limits.
        """
        return self.limits[0] <= age <= self.limits[1]


@dataclass(frozen=True)
class MeasurementConfig:
    """Configuration for a measurement, including units and aliases.

    Attributes:
        name: Canonical measurement key.
        unit: Display unit string.
        aliases: Alias set accepted for this measurement.
    """

    name: MeasurementAliasType
    unit: str
    aliases: frozenset[str] = frozenset()

    def matches_alias(self, alias: str) -> bool:
        """Check whether a string matches a configured alias or unit.

        Args:
            alias: Candidate alias or unit.

        Returns:
            True when the alias matches.
        """
        return alias.lower() in self.aliases or alias == self.unit


# Configuration mappings
AGE_GROUP_CONFIG: dict[AgeGroup, AgeGroupConfig] = {
    AgeGroup.VERY_PRETERM_NEWBORN: AgeGroupConfig(AgeGroup.VERY_PRETERM_NEWBORN.value, (168, 230), "gestational_age", "very_preterm_newborn"),
    AgeGroup.NEWBORN: AgeGroupConfig(AgeGroup.NEWBORN.value, (230, 300), "gestational_age", "newborn"),
    AgeGroup.POSTNATAL_GROWTH_PRETERM: AgeGroupConfig(
        AgeGroup.POSTNATAL_GROWTH_PRETERM.value, (27 * WEEK, 64 * WEEK), "post_menstrual_age", "postnatal_growth_preterm"
    ),
    AgeGroup.ZERO_ONE: AgeGroupConfig(AgeGroup.ZERO_ONE.value, (0, int(round(1 * YEAR))), "age", "child_growth"),
    AgeGroup.ZERO_TWO: AgeGroupConfig(AgeGroup.ZERO_TWO.value, (0, int(round(2 * YEAR))), "age", "child_growth"),
    AgeGroup.TWO_FIVE: AgeGroupConfig(AgeGroup.TWO_FIVE.value, (int(round(2 * YEAR)) + 1, int(round(5 * YEAR))), "age", "child_growth"),
    AgeGroup.FIVE_TEN: AgeGroupConfig(AgeGroup.FIVE_TEN.value, (int(round(5 * YEAR)) + 1, int(round(10 * YEAR))), "age", "growth"),
    AgeGroup.TEN_NINETEEN: AgeGroupConfig(AgeGroup.TEN_NINETEEN.value, (int(round(10 * YEAR)) + 1, int(round(19 * YEAR))), "age", "growth"),
}

MEASUREMENT_CONFIG: dict[MeasurementType, MeasurementConfig] = {
    MeasurementType.STATURE: MeasurementConfig(MeasurementType.STATURE.value, "cm", StatureAlias),
    MeasurementType.WEIGHT: MeasurementConfig(MeasurementType.WEIGHT.value, "kg", WeightAlias),
    MeasurementType.HEAD_CIRCUMFERENCE: MeasurementConfig(MeasurementType.HEAD_CIRCUMFERENCE.value, "cm", HeadCircumferenceAlias),
    MeasurementType.BODY_MASS_INDEX: MeasurementConfig(MeasurementType.BODY_MASS_INDEX.value, "kg/m²", BodyMassIndexAlias),
    MeasurementType.WEIGHT_STATURE_RATIO: MeasurementConfig(MeasurementType.WEIGHT_STATURE_RATIO.value, "kg/cm", WeightStatureAlias),
    MeasurementType.STATURE_VELOCITY: MeasurementConfig(
        MeasurementType.STATURE_VELOCITY.value, "cm/month", aliases=frozenset(["length_velocity", "height_velocity", "stature_velocity"])
    ),
    MeasurementType.WEIGHT_VELOCITY: MeasurementConfig(
        MeasurementType.WEIGHT_VELOCITY.value, "kg/month", aliases=frozenset(["weight_velocity"])
    ),
    MeasurementType.HEAD_CIRCUMFERENCE_VELOCITY: MeasurementConfig(
        MeasurementType.HEAD_CIRCUMFERENCE_VELOCITY.value, "cm/month", aliases=frozenset(["head_circumference_velocity"])
    ),
}


class ChoiceValidator:
    """Helpers for validating and resolving configuration choices."""

    @staticmethod
    def resolve_measurement_alias(alias: str) -> MeasurementAliasType | None:
        """Resolve a measurement alias into its canonical name.

        Args:
            alias: Input alias or unit.

        Returns:
            Canonical measurement name if found, otherwise None.
        """
        alias_lower = alias.lower()
        for config in MEASUREMENT_CONFIG.values():
            # compare against the enum value (string) and configured aliases/units
            if config.matches_alias(alias_lower):
                return config.name
        return None

    @staticmethod
    def get_age_group_for_age(age: int, x_type: DataXTypeType) -> AgeGroupType | None:
        """Return the matching age group for the given age and x_type.

        Args:
            age: Age in days.
            x_type: Axis type to match.

        Returns:
            Age group key if found, otherwise None.
        """
        for config in AGE_GROUP_CONFIG.values():
            if config.x_type == x_type and config.contains_age(age):
                return config.name
        return None

    @staticmethod
    def validate_choice(value: str, choices: frozenset[str]) -> bool:
        """Check whether a value is in the allowed choices.

        Args:
            value: Candidate value to validate.
            choices: Set of allowed values.

        Returns:
            True when the value is allowed.
        """
        return value in choices


def resolve_x_var_type(x_type: str) -> DataXTypeType:
    """Normalize x_var_type aliases to canonical values.

    Args:
        x_type: Input axis type string.

    Returns:
        Canonical axis type.

    Raises:
        ValueError: If the axis type is not supported.
    """
    normalized = x_type.lower().replace(" ", "_")
    if normalized == "chronological_age":
        return "age"
    if normalized in {"length", "height"}:
        return "stature"
    if normalized in {"age", "gestational_age", "post_menstrual_age", "stature"}:
        return cast(DataXTypeType, normalized)

    raise ValueError(f"Invalid x_var_type: {x_type}. Must be 'age', 'gestational_age', 'post_menstrual_age', 'stature', 'length', or 'height'.")


def get_age_group(age: int, x_type: DataXTypeType = "age") -> AgeGroupType:
    """Return the configured age group for the given age and x_type.

    Args:
        age: Age in days.
        x_type: Axis type to match.

    Returns:
        The resolved age group.

    Raises:
        ValueError: If no matching age group exists.
    """
    result = ChoiceValidator.get_age_group_for_age(age, x_type)
    if result is None:
        raise ValueError(f"No age group found for age {age} with x_type {x_type}")
    return result


# Backward compatibility - keep existing variables
DATA_SEX_CHOICES = frozenset(["M", "F", "U"])
AGE_GROUP_CHOICES = frozenset([e.value for e in AgeGroup])
TABLE_NAME_CHOICES = frozenset(["growth", "child_growth", "postnatal_growth_preterm", "very_preterm_newborn", "newborn"])
