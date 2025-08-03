from decimal import Decimal as D
from enum import Enum, StrEnum
from typing import Literal

X_TEMPLATE = D("0.00")
MU_TEMPLATE = D("0.0000")
LAMBDA_TEMPLATE = D("0.0000")
SIGMA_TEMPLATE = D("0.00000")

UNITS = {
    "stature": "cm",
    "weight": "kg",
    "head_circumference": "cm",
    "body_mass_index": "kg/m²",
    "weight_length": "kg/cm",
    "weight_height": "kg/cm",
    "stature_velocity": "cm/month",
    "weight_velocity": "kg/month",
    "head_circumference_velocity": "cm/month",
}

DataSourceType = Literal["who", "intergrowth"]
DataSexType = Literal["M", "F", "U"]
DataUnitType = Literal["days", "cm"]
DataUnitNameType = Literal["age", "gestational_age", "stature"]

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
