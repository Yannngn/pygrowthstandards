"""Measurement value containers for the OOP API."""

import pandas as pd

from pygrowthstandards.config.growth import PLOT_GROUP_CONFIG, MeasurementAliasType, PlotGroup, PlotGroupType
from pygrowthstandards.data.growth.load import GrowthTable, KeyObject
from pygrowthstandards.oop.patient import Patient


# TODO: Refactor to separate data retrieval from plotting
def get_reference_data(patient: Patient, plot_group: PlotGroupType, measurement_type: MeasurementAliasType) -> GrowthTable:
    """Load reference data for a given plot group and measurement.

    Args:
        plot_group: Age group identifier.
        measurement_type: Measurement alias.

    Returns:
        GrowthTable containing reference LMS data.

    Raises:
        ValueError: If plot_group is invalid or data is unavailable.
    """
    try:
        age_group_enum = PlotGroup(plot_group)
    except ValueError as exc:
        raise ValueError(f"Invalid plot group: {plot_group}") from exc

    config = PLOT_GROUP_CONFIG[age_group_enum]

    if patient.calculator.data is None:
        raise ValueError("Reference data is not available. Ensure the data file is present.")

    keys = KeyObject.from_oop(
        config.table_name,
        plot_group=plot_group,
        measurement_type=measurement_type,
        sex=patient.sex,
        x_var_type=config.x_var_type,
    )
    data = GrowthTable.from_data(patient.calculator.data, keys=keys)

    return data


# TODO: Refactor to separate data retrieval from plotting
def get_patient_data(patient: Patient, plot_group: PlotGroupType, measurement_type: MeasurementAliasType) -> pd.DataFrame:
    """Return user measurements for a given plot group and measurement.

    Args:
        plot_group: Age group identifier.
        measurement_type: Measurement alias.

    Returns:
        DataFrame with columns "x" and "patient".
    """
    config = PLOT_GROUP_CONFIG[PlotGroup(plot_group)]
    lower_limit, upper_limit = config.limits
    x_var_type = config.x_var_type

    filtered_measurements = []
    for entry in patient.measurements:
        if plot_group in {"newborn", "very_preterm_newborn"}:
            if patient.get_age("age", entry.date) != 0:
                continue

        if x_var_type in {"gestational_age", "age", "post_menstrual_age"}:
            x_value = patient.get_age(x_var_type, entry.date)
        else:
            x_value = getattr(entry, x_var_type)

        if lower_limit <= x_value <= upper_limit and hasattr(entry, measurement_type) and getattr(entry, measurement_type) is not None:
            filtered_measurements.append((x_value, getattr(entry, measurement_type)))

    x = [item[0] for item in filtered_measurements]
    y = [item[1] for item in filtered_measurements]

    return pd.DataFrame({"x": x, "patient": y})


# TODO: Refactor to share call for growth and development plots
def get_plot_data(patient: Patient, plot_group: PlotGroupType, measurement_type: MeasurementAliasType) -> pd.DataFrame:
    """Return combined reference and patient data for plotting.

    Args:
        plot_group: Age group identifier.
        measurement_type: Measurement alias.

    Returns:
        DataFrame with reference curves and patient data.
    """
    data = get_patient_data(patient, plot_group, measurement_type)
    reference_data = get_reference_data(patient, plot_group, measurement_type)

    reference_data.add_patient_data(data)
    return reference_data.convert_z_scores_to_values()
