"""Configuration types and lookup helpers for growth standards."""

from dataclasses import dataclass
from enum import StrEnum
from typing import cast

from pygrowthstandards.typing.growth import (
    DataXVarType,
    MeasurementAliasType,
    PlotGroupType,
    TableNameType,
)
from pygrowthstandards.utils.constants import WEEK, YEAR

SexAlias = frozenset(["M", "F", "U"])
TableNameAlias = frozenset(["growth", "child_growth", "postnatal_growth_preterm", "very_preterm_newborn", "newborn"])
PlotGroupAlias = frozenset(
    [
        "0-2",
        "2-5",
        "5-10",
        "10-19",
        "newborn",
        "very_preterm_newborn",
        "postnatal_growth_preterm",
        "weight_for_length",
        "weight_for_height",
        "velocity",
    ]
)


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


class PlotGroup(StrEnum):
    """Supported plot group identifiers."""

    # Age related groups
    ZERO_TWO = "0-2"
    TWO_FIVE = "2-5"
    FIVE_TEN = "5-10"
    TEN_NINETEEN = "10-19"
    NEWBORN = "newborn"
    VERY_PRETERM_NEWBORN = "very_preterm_newborn"
    POSTNATAL_GROWTH_PRETERM = "postnatal_growth_preterm"

    # Weight for length/height groups
    WEIGHT_FOR_LENGTH = "weight_for_length"  # 0-2
    WEIGHT_FOR_HEIGHT = "weight_for_height"  # 2-5

    # Velocity group
    VELOCITY = "velocity"


# Type aliases using the enums


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

WeightAlias = frozenset(["wfa", "w", "weight"])

HeadCircumferenceAlias = frozenset(["hcfa", "hc", "head_circumference"])

BodyMassIndexAlias = frozenset(["bmi", "bfa", "body_mass_index"])

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


VelocityAlias = frozenset(["weight_velocity", "length_velocity", "head_circumference_velocity", "stature_velocity"])


@dataclass(frozen=True)
class PlotGroupConfig:
    """Configuration for an plot group slice of reference data.

    Attributes:
        name: Canonical plot group key.
        limits: Inclusive min/max bounds in days.
        x_var_type: Axis type associated with the group.
        table_name: Reference table name.
    """

    name: PlotGroupType
    limits: tuple[int, int]
    x_var_type: DataXVarType
    table_name: TableNameType

    def contains_value(self, x_value: int) -> bool:
        """Check whether the x_value is within the configured limits.

        Args:
            x_value: X value in days or cm.


        Returns:
            True when the x_value is within the inclusive limits.
        """
        return self.limits[0] <= x_value <= self.limits[1]


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
        return alias.lower() in self.aliases or alias.lower() == self.unit.lower()


# Configuration mappings
PLOT_GROUP_CONFIG: dict[PlotGroup, PlotGroupConfig] = {
    PlotGroup.VERY_PRETERM_NEWBORN: PlotGroupConfig(
        PlotGroup.VERY_PRETERM_NEWBORN.value, (168, 230), "gestational_age", "very_preterm_newborn"
    ),
    PlotGroup.NEWBORN: PlotGroupConfig(PlotGroup.NEWBORN.value, (230, 300), "gestational_age", "newborn"),
    PlotGroup.POSTNATAL_GROWTH_PRETERM: PlotGroupConfig(
        PlotGroup.POSTNATAL_GROWTH_PRETERM.value, (27 * WEEK, 64 * WEEK), "post_menstrual_age", "postnatal_growth_preterm"
    ),
    PlotGroup.ZERO_TWO: PlotGroupConfig(PlotGroup.ZERO_TWO.value, (0, int(round(2 * YEAR))), "age", "child_growth"),
    PlotGroup.TWO_FIVE: PlotGroupConfig(PlotGroup.TWO_FIVE.value, (int(round(2 * YEAR)) + 1, int(round(5 * YEAR))), "age", "child_growth"),
    PlotGroup.FIVE_TEN: PlotGroupConfig(PlotGroup.FIVE_TEN.value, (int(round(5 * YEAR)) + 1, int(round(10 * YEAR))), "age", "growth"),
    PlotGroup.TEN_NINETEEN: PlotGroupConfig(PlotGroup.TEN_NINETEEN.value, (int(round(10 * YEAR)) + 1, int(round(19 * YEAR))), "age", "growth"),
    PlotGroup.WEIGHT_FOR_LENGTH: PlotGroupConfig(PlotGroup.WEIGHT_FOR_LENGTH.value, (45, 110), "length", "child_growth"),  # length in cm
    PlotGroup.WEIGHT_FOR_HEIGHT: PlotGroupConfig(PlotGroup.WEIGHT_FOR_HEIGHT.value, (65, 120), "height", "child_growth"),  # height in cm
    PlotGroup.VELOCITY: PlotGroupConfig(
        PlotGroup.VELOCITY.value, (0, int(round(2 * YEAR))), "age", "child_growth"
    ),  # velocity data only available for 0-2 age group
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
    def get_plot_group(x_value: int, x_type: DataXVarType) -> PlotGroupType | None:
        """Return the matching plot group for the given age and x_type.

        Args:
            x_value: X value in days or cm.
            x_type: Axis type to match.

        Returns:
            Plot group key if found, otherwise None.
        """
        candidates: list[PlotGroupConfig] = []
        for config in PLOT_GROUP_CONFIG.values():
            if config.x_var_type == x_type and config.contains_value(x_value):
                candidates.append(config)

        if not candidates:
            return None

        candidates.sort(key=lambda item: item.limits[1] - item.limits[0], reverse=True)
        return candidates[0].name

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


def resolve_x_var_type(x_type: str, age_days: int | None = None) -> DataXVarType:
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

    # if normalized in {"length", "height"}:
    #     return "stature"

    if normalized == "stature":
        if age_days is None or age_days <= 2 * YEAR:
            return "length"
        return "height"

    if normalized in {"age", "gestational_age", "post_menstrual_age", "height", "length"}:  # , "stature"}:
        return cast(DataXVarType, normalized)

    raise ValueError(f"Invalid x_var_type: {x_type}. Must be 'age', 'gestational_age', 'post_menstrual_age', 'stature', 'length', or 'height'.")


def get_plot_group(x_value: int, x_type: DataXVarType = "age") -> PlotGroupType:
    """Return the configured plot group for the given x_value and x_type.

    Args:
        x_value: X value in days or cm.
        x_type: Axis type to match.

    Returns:
        The resolved plot group.

    Raises:
        ValueError: If no matching plot group exists.
    """
    result = ChoiceValidator.get_plot_group(x_value, x_type)
    if result is None:
        raise ValueError(f"No plot group found for x_value {x_value} with x_type {x_type}")
    return result


def resolve_table_context(
    measurement: MeasurementAliasType,
    *,
    age_days: int | None = None,
    gestational_age: int | None = None,
    x_var_type: str | None = None,
    x_value: float | None = None,
    plot_group: PlotGroupType | None = None,
) -> tuple[TableNameType, DataXVarType, float | None, PlotGroupType | None]:
    """Resolve table selection context and derive missing keys.

    Args:
        measurement: Measurement alias.
        age_days: Chronological age in days.
        gestational_age: Gestational age in days.
        x_var_type: Explicit axis type when providing x_value.
        x_value: Explicit axis value.
        plot_group: Optional plot group override.

    Returns:
        Tuple of (table name, x_var_type, x_value, plot_group).

    Raises:
        ValueError: If the inputs are inconsistent with available data.
    """
    resolved_measurement = ChoiceValidator.resolve_measurement_alias(str(measurement)) or measurement

    def _resolve_x_value_and_type():
        if x_var_type is not None:
            resolved_x_var_type = resolve_x_var_type(x_var_type, age_days)
            if x_value is None:
                raise ValueError("x_value is required when x_var_type is provided.")
            return float(x_value), resolved_x_var_type

        if age_days is not None:
            if gestational_age is not None and gestational_age < 28 * WEEK:
                post_menstrual_age = age_days + gestational_age
                if post_menstrual_age <= 64 * WEEK:
                    return float(post_menstrual_age), "post_menstrual_age"

            return float(age_days), "age"

        if gestational_age is not None:
            return float(gestational_age), "gestational_age"

        raise ValueError("Either age_days or gestational_age must be provided.")

    resolved_x_value, resolved_x_var_type = _resolve_x_value_and_type()

    def _get_table_name():
        if resolved_x_var_type == "post_menstrual_age":
            return "postnatal_growth_preterm"

        if resolved_x_var_type == "gestational_age":
            if resolved_measurement in ["body_mass_index"]:
                raise ValueError(f"No reference for {resolved_measurement} at birth or fetal age.")
            gestational_days = gestational_age if gestational_age is not None else int(resolved_x_value)
            return "newborn" if gestational_days > 28 * WEEK else "very_preterm_newborn"

        age_value = age_days if age_days is not None else int(resolved_x_value)

        # TODO: move this logic into the measurement config
        if resolved_measurement in ["head_circumference", "weight_stature_ratio"] and age_value > 5 * YEAR:
            raise ValueError(f"No reference for {resolved_measurement} after 5 years.")

        if resolved_measurement in ["weight"] and age_value > 10 * YEAR:
            raise ValueError(f"No reference for {resolved_measurement} after 10 years.")

        return "growth" if age_value > 5 * YEAR else "child_growth"

    table_name = _get_table_name()

    def _resolve_plot_group():
        resolved_plot_group = plot_group
        if resolved_plot_group is not None:
            return resolved_plot_group

        if resolved_x_var_type == "stature":
            if age_days is not None:
                return ChoiceValidator.get_plot_group(age_days, "age")

        plot_group_candidate = ChoiceValidator.get_plot_group(int(resolved_x_value), resolved_x_var_type)

        if plot_group_candidate is None:
            raise ValueError(f"No plot group found for age {resolved_x_value} with x_type {resolved_x_var_type}")

        return plot_group_candidate

    resolved_plot_group = _resolve_plot_group()

    return table_name, resolved_x_var_type, resolved_x_value, resolved_plot_group


def infer_table_name(
    measurement: MeasurementAliasType,
    *,
    age_days: int | None = None,
    gestational_age: int | None = None,
) -> TableNameType:
    """Infer the reference table name from measurement and age inputs.

    Args:
        measurement: Measurement alias.
        age_days: Chronological age in days.
        gestational_age: Gestational age in days.

    Returns:
        Table name identifier.

    Raises:
        ValueError: If the inputs are inconsistent with available data.
    """
    table_name, _, _, _ = resolve_table_context(
        measurement,
        age_days=age_days,
        gestational_age=gestational_age,
    )
    return table_name
