"""Utility class for validating and resolving choices."""

from pygrowthstandards.utils.date_utils import months_to_days

from .development import DEVELOPMENT_GOALS, DevelopmentGoalType, DevelopmentStatus, DevelopmentStatusType
from .growth import (
    AGE_GROUP_CONFIG,
    AGE_GROUP_TABLE_NAME,
    MEASUREMENT_CONFIG,
    AgeGroupType,
    DataXTypeType,
    MeasurementTypeType,
    TableNameType,
)


def resolve_measurement_alias(alias: str) -> MeasurementTypeType | None:
    """Resolve measurement alias to canonical name."""
    alias_lower = alias.lower()
    for measurement, config in MEASUREMENT_CONFIG.items():
        # compare against the enum value (string) and configured aliases/units
        if measurement == alias_lower or config.matches_alias(alias_lower):
            return measurement
    return None


def validate_choice(value: str, choices: frozenset[str]) -> bool:
    """Validate if value is in choices."""
    return value in choices


def get_measurement_unit(measurement: MeasurementTypeType) -> str:
    """Get unit for measurement type."""
    return MEASUREMENT_CONFIG[measurement].unit


def get_age_type_from_table(table_name: TableNameType) -> DataXTypeType | None:
    """Get age type for table name."""
    for _, config in AGE_GROUP_CONFIG.items():
        if config.table_name == table_name:
            return config.x_type
    return None


def get_age_type_from_age_group(age_group: AgeGroupType) -> DataXTypeType | None:
    """Get age type for age group."""
    for key, config in AGE_GROUP_CONFIG.items():
        if key == age_group:
            return config.x_type
    return None


def get_age_group_from_ages(age: int | None = None, gestational_age: int | None = None) -> AgeGroupType | None:
    def get_age_group(age: int, x_type: DataXTypeType) -> AgeGroupType | None:
        """Find the appropriate age group for given age and x_type."""
        for age_group, config in AGE_GROUP_CONFIG.items():
            if config.x_type == x_type and config.contains_age(age):
                return age_group

        return None

    if gestational_age is None and age is None:
        raise ValueError("Either age or gestational_age must be provided.")

    if age is not None and gestational_age is None:
        return get_age_group(age, "age")

    assert gestational_age is not None, "Either age or gestational_age must be provided. Only for typing"

    if AGE_GROUP_CONFIG["very_preterm_newborn"].contains_age(gestational_age):
        if not age:
            return "very_preterm_newborn"

        if AGE_GROUP_CONFIG["very_preterm_growth"].contains_age(age + gestational_age):
            return "very_preterm_growth"

        return get_age_group(age, "age")

    if not age:
        return "newborn"

    return get_age_group(age, "age")


def get_table_name_from_age_group(age_group: AgeGroupType) -> TableNameType | None:
    """Get table name for age group."""
    return AGE_GROUP_TABLE_NAME.get(age_group)  # type: ignore


def validate_development_goal(
    key: DevelopmentGoalType, age_in_days: int, verified: bool = True, achievable: bool = True
) -> DevelopmentStatusType | None:
    """
    Validate if a child has achieved a development goal within the expected age range.

    Parameters:
    - key: The key of the development goal.
    - child_age_months: The child's age in months.
    - achieved: Whether the child has achieved the goal.

    Returns:
    - A message indicating the validation result, or None if no issues are found.
    """
    goal = DEVELOPMENT_GOALS.get(key)
    if not goal:
        return None

    if not achievable:
        return DevelopmentStatus.NOT_ACHIEVABLE  # type: ignore

    if not verified:
        return DevelopmentStatus.NOT_VERIFIED  # type: ignore

    if age_in_days < goal.limits[0]:
        return DevelopmentStatus.ON_TRACK  # type: ignore

    if age_in_days < goal.limits[1]:
        return DevelopmentStatus.ACHIEVED  # type: ignore

    if age_in_days < goal.limits[1] + months_to_days(1):
        return DevelopmentStatus.SLIGHTLY_DELAYED  # type: ignore

    return DevelopmentStatus.DELAYED  # type: ignore
