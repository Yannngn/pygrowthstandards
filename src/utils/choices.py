import os
import sys
from enum import Enum, StrEnum
from typing import FrozenSet, Literal, NamedTuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


TABLE_NAME_TYPE = Literal["growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"]
TABLE_NAME_CHOICES = frozenset(["growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"])


AGE_GROUP_TYPE = Literal[
    "0-1",
    "0-2",
    "2-5",
    "5-10",
    "10-19",
    "newborn",
    "very_preterm_newborn",
    "very_preterm_growth",
]
AGE_GROUP_CHOICES = frozenset(
    [
        "0-1",
        "0-2",
        "2-5",
        "5-10",
        "10-19",
        "newborn",
        "very_preterm_newborn",
        "very_preterm_growth",
    ]
)

MEASUREMENT_TYPE_CHOICES = frozenset(
    [
        "body_mass_index",
        "head_circumference",
        "stature",
        "weight",
        "weight_stature",
        "head_circumference_velocity",
        "length_velocity",
        "weight_velocity",
    ]
)
MEASUREMENT_TYPE_TYPE = Literal[
    "stature",
    "weight",
    "weight_stature",
    "head_circumference",
    "body_mass_index",
    "weight_velocity",
    "length_velocity",
    "head_circumference_velocity",
]


class PlotAgeChoices(StrEnum):
    """Enum for age choices with associated age group and range."""

    ZERO_ONE_YEARS = "0-1"
    ZERO_TWO_YEARS = "0-2"
    TWO_FIVE_YEARS = "2-5"
    FIVE_TEN_YEARS = "5-10"
    TEN_NINETEEN_YEARS = "10-19"
    NEWBORN = "newborn"
    VERY_PRETERM_NEWBORN = "very_preterm_newborn"
    VERY_PRETERM = "very_preterm"


class PlotAgeValues(Enum):
    """Enum for age values with associated age group and range."""

    ZERO_ONE_YEARS = (0, 1)
    ZERO_TWO_YEARS = (0, 2)
    TWO_FIVE_YEARS = (2, 5)
    FIVE_TEN_YEARS = (5, 10)
    TEN_NINETEEN_YEARS = (10, 19)
    NEWBORN = (231, 300)
    VERY_PRETERM_NEWBORN = (168, 230)
    VERY_PRETERM = (189, 448)


class MeasurementChoices(StrEnum):
    """Enum for measurement choices with aliases."""

    STATURE = "stature"
    WEIGHT = "weight"
    HEAD_CIRCUMFERENCE = "head_circumference"
    BODY_MASS_INDEX = "body_mass_index"
    WEIGHT_VELOCITY = "weight_velocity"
    LENGTH_VELOCITY = "length_velocity"
    HEAD_CIRCUMFERENCE_VELOCITY = "head_circumference_velocity"


class MeasurementAliases(Enum):
    STATURE = ("stature", "lfa", "hfa", "lhfa", "length", "height", "length_height")
    WEIGHT = ("wfa", "wfl", "wfh", "weight", "weight_height", "weight_length", "weight_stature")
    HEAD_CIRCUMFERENCE = ("hcfa", "hc", "head_circumference")
    BODY_MASS_INDEX = ("bfa", "bmi", "body_mass_index")
    WEIGHT_VELOCITY = ("weight_velocity",)
    LENGTH_VELOCITY = ("length_velocity",)
    HEAD_CIRCUMFERENCE_VELOCITY = ("head_circumference_velocity",)

    @classmethod
    def get_name(cls, value: str) -> str:
        """Get the measurement name from an alias."""
        for member in cls:
            if value in member.value:
                return member.name
        raise ValueError(f"Alias '{value}' not found in MeasurementAliases.")


class PlotType(StrEnum):
    """Enum for plot types."""

    WEIGHT_FOR_AGE = "weight_for_age"
    WEIGHT_FOR_STATURE = "weight_for_stature"
    STATURE_FOR_AGE = "stature_for_age"
    HEAD_CIRCUMFERENCE_FOR_AGE = "head_circumference_for_age"
    BODY_MASS_INDEX_FOR_AGE = "body_mass_index_for_age"
    WEIGHT_VELOCITY = "weight_velocity"
    LENGTH_VELOCITY = "length_velocity"
    HEAD_CIRCUMFERENCE_VELOCITY = "head_circumference_velocity"


class PlotConfiguration(NamedTuple):
    """
    Represents a plot configuration with a measurement and a set of ages.
    """

    measurement: MeasurementChoices
    ages: FrozenSet[PlotAgeChoices]


PLOT_DEFINITIONS = {
    PlotType.WEIGHT_FOR_AGE: PlotConfiguration(
        measurement=MeasurementChoices.WEIGHT,
        ages=frozenset(
            [
                PlotAgeChoices.ZERO_TWO_YEARS,
                PlotAgeChoices.TWO_FIVE_YEARS,
                PlotAgeChoices.FIVE_TEN_YEARS,
                PlotAgeChoices.NEWBORN,
                PlotAgeChoices.VERY_PRETERM_NEWBORN,
                PlotAgeChoices.VERY_PRETERM,
            ]
        ),
    ),
    PlotType.WEIGHT_FOR_STATURE: PlotConfiguration(
        measurement=MeasurementChoices.WEIGHT,
        ages=frozenset(
            [
                PlotAgeChoices.ZERO_TWO_YEARS,
                PlotAgeChoices.TWO_FIVE_YEARS,
                PlotAgeChoices.VERY_PRETERM_NEWBORN,
            ]
        ),
    ),
    PlotType.STATURE_FOR_AGE: PlotConfiguration(
        measurement=MeasurementChoices.STATURE,
        ages=frozenset(
            [
                PlotAgeChoices.ZERO_TWO_YEARS,
                PlotAgeChoices.TWO_FIVE_YEARS,
                PlotAgeChoices.FIVE_TEN_YEARS,
                PlotAgeChoices.TEN_NINETEEN_YEARS,
                PlotAgeChoices.NEWBORN,
                PlotAgeChoices.VERY_PRETERM_NEWBORN,
                PlotAgeChoices.VERY_PRETERM,
            ]
        ),
    ),
    PlotType.HEAD_CIRCUMFERENCE_FOR_AGE: PlotConfiguration(
        measurement=MeasurementChoices.HEAD_CIRCUMFERENCE,
        ages=frozenset(
            [
                PlotAgeChoices.ZERO_TWO_YEARS,
                PlotAgeChoices.NEWBORN,
                PlotAgeChoices.VERY_PRETERM_NEWBORN,
                PlotAgeChoices.VERY_PRETERM,
            ]
        ),
    ),
    PlotType.BODY_MASS_INDEX_FOR_AGE: PlotConfiguration(
        measurement=MeasurementChoices.BODY_MASS_INDEX,
        ages=frozenset(
            [
                PlotAgeChoices.ZERO_TWO_YEARS,
                PlotAgeChoices.TWO_FIVE_YEARS,
                PlotAgeChoices.FIVE_TEN_YEARS,
                PlotAgeChoices.TEN_NINETEEN_YEARS,
            ]
        ),
    ),
    PlotType.WEIGHT_VELOCITY: PlotConfiguration(
        measurement=MeasurementChoices.WEIGHT_VELOCITY, ages=frozenset([PlotAgeChoices.ZERO_ONE_YEARS])
    ),
    PlotType.LENGTH_VELOCITY: PlotConfiguration(
        measurement=MeasurementChoices.LENGTH_VELOCITY, ages=frozenset([PlotAgeChoices.ZERO_ONE_YEARS])
    ),
    PlotType.HEAD_CIRCUMFERENCE_VELOCITY: PlotConfiguration(
        measurement=MeasurementChoices.HEAD_CIRCUMFERENCE_VELOCITY,
        ages=frozenset([PlotAgeChoices.ZERO_ONE_YEARS]),
    ),
}


def main():
    for plot_type, config in PLOT_DEFINITIONS.items():
        if not isinstance(plot_type, PlotType):
            raise TypeError(f"Invalid plot type: {plot_type}")
        if not isinstance(config, PlotConfiguration):
            raise TypeError(f"Invalid plot configuration: {config}")
        if not isinstance(config.measurement, MeasurementChoices):
            raise TypeError(f"Invalid measurement choice: {config.measurement}")
        if not all(isinstance(age, PlotAgeChoices) for age in config.ages):
            raise TypeError(f"Invalid age choice in {config.ages}")

    print("Done!")


if __name__ == "__main__":
    main()
