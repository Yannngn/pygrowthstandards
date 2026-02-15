from typing import Literal

DataSourceType = Literal["who", "intergrowth"]
DataSexType = Literal["M", "F", "U"]
DataXVarType = Literal["age", "gestational_age", "post_menstrual_age", "length", "height"]
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
WeightAliasType = Literal["wfa", "w", "weight"]
HeadCircumferenceAliasType = Literal["hcfa", "hc", "head_circumference"]
BodyMassIndexAliasType = Literal["bmi", "bfa", "body_mass_index"]
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
VelocityAliasType = Literal["weight_velocity", "length_velocity", "head_circumference_velocity", "stature_velocity"]

MeasurementAliasType = (
    StatureAliasType | WeightAliasType | HeadCircumferenceAliasType | BodyMassIndexAliasType | WeightStatureAliasType | VelocityAliasType
)

PlotGroupType = Literal[
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

TableNameType = Literal["growth", "child_growth", "postnatal_growth_preterm", "very_preterm_newborn", "newborn"]
