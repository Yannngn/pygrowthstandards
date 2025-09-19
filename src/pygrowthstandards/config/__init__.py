from .development import (
    DEVELOPMENT_GOAL_CHOICES,
    DEVELOPMENT_GOALS,
    DEVELOPMENT_GOALS_ORDER,
    DevelopmentGoalConfig,
    DevelopmentGoals,
    DevelopmentGoalType,
    DevelopmentStatusType,
)
from .growth import (
    AGE_GROUP_CHOICES,
    AGE_GROUP_CONFIG,
    AGE_GROUP_LIMITS,
    AGE_GROUP_TABLE_NAME,
    AGE_GROUP_X,
    DATA_SEX_CHOICES,
    DATA_SOURCE_CHOICES,
    DATA_X_CHOICES,
    LAMBDA_TEMPLATE,
    MEASUREMENT_ALIASES,
    MEASUREMENT_CONFIG,
    MEASUREMENT_TYPE_CHOICES,
    MU_TEMPLATE,
    SIGMA_TEMPLATE,
    UNITS,
    X_TEMPLATE,
    AgeGroup,
    AgeGroupConfig,
    AgeGroupType,
    DataSex,
    DataSexType,
    DataSource,
    DataSourceType,
    DataXType,
    DataXTypeType,
    MeasurementConfig,
    MeasurementType,
    MeasurementTypeType,
    TableNameType,
)

__all__ = [
    # Templates
    "X_TEMPLATE",
    "MU_TEMPLATE",
    "LAMBDA_TEMPLATE",
    "SIGMA_TEMPLATE",
    # Development Goals
    "DEVELOPMENT_GOALS",
    "DEVELOPMENT_GOALS_ORDER",
    "DEVELOPMENT_GOAL_CHOICES",
    "DevelopmentGoals",
    "DevelopmentGoalConfig",
    "DevelopmentGoalType",
    "DevelopmentStatusType",
    # Growth/Age Groups
    "AGE_GROUP_CHOICES",
    "AGE_GROUP_CONFIG",
    "AGE_GROUP_LIMITS",
    "AGE_GROUP_TABLE_NAME",
    "AGE_GROUP_X",
    "AgeGroup",
    "AgeGroupConfig",
    "AgeGroupType",
    # Data Types
    "DATA_SEX_CHOICES",
    "DATA_SOURCE_CHOICES",
    "DATA_X_CHOICES",
    "DataSex",
    "DataSexType",
    "DataSource",
    "DataSourceType",
    "DataXType",
    "DataXTypeType",
    # Measurements
    "MEASUREMENT_ALIASES",
    "MEASUREMENT_CONFIG",
    "MEASUREMENT_TYPE_CHOICES",
    "MeasurementConfig",
    "MeasurementType",
    "MeasurementTypeType",
    "TableNameType",
    "UNITS",
    # Utility Classes
    "ChoiceValidator",
    # Convenience Functions
    "resolve_measurement",
    "get_age_group",
]

# Templates are now imported from growth.py


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

    @staticmethod
    def get_age_type_from_table(table_name: TableNameType) -> DataXTypeType | None:
        """Get age type for table name."""
        for _, config in AGE_GROUP_CONFIG.items():
            if config.table_name == table_name:
                return config.x_type
        return None

    @staticmethod
    def get_age_type_from_age_group(age_group: AgeGroupType) -> DataXTypeType | None:
        """Get age type for age group."""
        for key, config in AGE_GROUP_CONFIG.items():
            if key == age_group:
                return config.x_type
        return None

    @staticmethod
    def get_age_group_from_ages(
        age: int | None = None, gestational_age: int | None = None
    ) -> AgeGroupType | None:
        if gestational_age is None and age is None:
            raise ValueError("Either age or gestational_age must be provided.")

        if age is not None and gestational_age is None:
            return ChoiceValidator.get_age_group_for_age(age, "age")

        assert gestational_age is not None, (
            "Either age or gestational_age must be provided. Only for typing"
        )

        if AGE_GROUP_CONFIG["very_preterm_newborn"].contains_age(gestational_age):
            if not age:
                return "very_preterm_newborn"

            if AGE_GROUP_CONFIG["very_preterm_growth"].contains_age(
                age + gestational_age
            ):
                return "very_preterm_growth"

            return ChoiceValidator.get_age_group_for_age(age, "age")

        if not age:
            return "newborn"

        return ChoiceValidator.get_age_group_for_age(age, "age")

    @staticmethod
    def get_table_name_from_age_group(age_group: AgeGroupType) -> TableNameType | None:
        """Get table name for age group."""
        return AGE_GROUP_TABLE_NAME.get(age_group)  # type: ignore

    @staticmethod
    def validate_development_goal(
        key: DevelopmentGoals, child_age_months: int, achieved: bool
    ) -> str | None:
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
            return f"Unknown development goal: {key}"

        if achieved:
            return None  # No issues if the goal is achieved

        if child_age_months <= goal.max_age_months:
            return f"Child has not achieved '{goal.description}' but is within the expected age range."

        if child_age_months <= goal.max_age_months + 1:
            return f"Possible issue: Child is slightly delayed in achieving '{goal.description}'."

        return f"Developmental issue: Child has not achieved '{goal.description}' and is significantly delayed."


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
