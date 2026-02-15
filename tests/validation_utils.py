from typing import Any

import pandas as pd

from pygrowthstandards.typing.growth import DataSexType, MeasurementAliasType, PlotGroupType, TableNameType
from pygrowthstandards.data.growth.load import load_reference
from pygrowthstandards.oop.growth import MeasurementGroup


def get_reference_row(
    *,
    plot_group: PlotGroupType,
    name: TableNameType,
    measurement_type: MeasurementAliasType,
    sex: DataSexType,
    x_var_type: str,
    min_x: float | None = None,
    max_x: float | None = None,
) -> pd.Series:
    data = load_reference()
    filtered = data[
        (data["plot_group"] == plot_group)
        & (data["name"] == name)
        & (data["measurement_type"] == measurement_type)
        & (data["sex"].str.upper() == sex.upper())
        & (data["x_var_type"] == x_var_type)
    ]

    if min_x is not None:
        filtered = filtered[filtered["x"] >= float(min_x)]
    if max_x is not None:
        filtered = filtered[filtered["x"] <= float(max_x)]

    if filtered.empty:
        raise AssertionError("No reference data found for requested filters.")

    return filtered.sort_values("x").iloc[0]


def get_measurements(
    *,
    plot_group: PlotGroupType,
    name: TableNameType,
    sex: DataSexType,
    x_var_type: str,
    desired: list[str] | None = None,
) -> list[str]:
    data = load_reference()
    filtered = data[
        (data["plot_group"] == plot_group)
        & (data["name"] == name)
        & (data["sex"].str.upper() == sex.upper())
        & (data["x_var_type"] == x_var_type)
    ]

    measurements = sorted({str(m) for m in filtered["measurement_type"].unique()})
    if desired is None:
        return measurements

    desired_set = set(desired)
    return [m for m in measurements if m in desired_set]


def as_int_x(value: Any) -> int:
    x_val = float(value)
    x_int = int(round(x_val))
    if abs(x_val - x_int) > 1e-6:
        raise AssertionError(f"Reference x is not an integer day: {x_val}")
    return x_int


def make_measurement_group(measurement_type: str, value: float) -> MeasurementGroup:
    if measurement_type == "weight":
        return MeasurementGroup(weight=value)
    if measurement_type == "stature":
        return MeasurementGroup(stature=value)
    if measurement_type == "head_circumference":
        return MeasurementGroup(head_circumference=value)

    raise AssertionError(f"Unsupported measurement_type for validation: {measurement_type}")
