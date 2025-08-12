from decimal import Decimal as D
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

DataSourceLiteral = Literal["who", "intergrowth"]
DATA_SOURCE_CHOICES: frozenset[DataSourceLiteral] = frozenset(["who", "intergrowth"])

SexLiteral = Literal["M", "F", "U"]
SEX_CHOICES: frozenset[SexLiteral] = frozenset(["M", "F", "U"])

XVarNameLiteral = Literal["age", "gestational_age", "stature"]
X_VAR_NAME_CHOICES: frozenset[XVarNameLiteral] = frozenset(["age", "gestational_age", "stature"])

XVarUnitLiteral = Literal["day", "cm"]
X_VAR_UNIT_CHOICES: frozenset[XVarUnitLiteral] = frozenset(["day", "cm"])

TableNameLiteral = Literal["growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"]
TABLE_NAME_CHOICES: frozenset[TableNameLiteral] = frozenset(
    ["growth", "child_growth", "very_preterm_growth", "very_preterm_newborn", "newborn"]
)


AgeGroupLiteral = Literal[
    "0-1",
    "0-2",
    "2-5",
    "5-10",
    "10-19",
    "newborn",
    "very_preterm_newborn",
    "very_preterm_growth",
]
AGE_GROUP_CHOICES: frozenset[AgeGroupLiteral] = frozenset(
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
MeasurementTypeLiteral = Literal[
    "stature",
    "weight",
    "weight_stature_ratio",
    "head_circumference",
    "body_mass_index",
    "weight_velocity",
    "length_velocity",
    "head_circumference_velocity",
]
MEASUREMENT_TYPE_CHOICES: frozenset[MeasurementTypeLiteral] = frozenset(
    [
        "stature",
        "weight",
        "weight_stature_ratio",
        "head_circumference",
        "body_mass_index",
        "weight_velocity",
        "length_velocity",
        "head_circumference_velocity",
    ]
)


MEASUREMENT_ALIASES: dict[MeasurementTypeLiteral, set[str]] = {
    "head_circumference": {"hcfa", "hc"},
    "stature": {"lfa", "hfa", "lhfa", "sfa", "l", "h", "s"},
    "weight": {"wfa", "w"},
    "body_mass_index": {"bmi", "bfa"},
    "weight_stature_ratio": {
        "wfs",
        "wfl",
        "wfh",
        "weight_stature",
        "weight_length",
        "weight_height",
        "weight_for_stature",
        "weight_for_length",
        "weight_for_height",
    },
    "weight_velocity": set(),
    "length_velocity": set(),
    "head_circumference_velocity": set(),
}
