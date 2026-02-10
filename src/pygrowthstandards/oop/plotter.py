"""Plotting utilities for the OOP API."""

from typing import cast

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from pygrowthstandards.config.growth import (
    AGE_GROUP_CONFIG,
    MEASUREMENT_CONFIG,
    AgeGroup,
    AgeGroupType,
    ChoiceValidator,
    MeasurementAliasType,
    MeasurementType,
)
from pygrowthstandards.data.load import GrowthTable, KeyObject
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.utils.plot import style
from pygrowthstandards.utils.plot.xticks import set_xticks_by_range


class Plotter:
    """Create reference and patient plots for growth data."""

    def __init__(self, patient: Patient):
        """Initialize the plotter with a patient instance.

        Args:
            patient: Patient containing measurements.
        """
        self.patient = patient
        self.setup()

    def setup(self):
        """Ensure patient calculations are up to date."""
        self.patient.calculate_all()

    def get_user_data(self, age_group: AgeGroupType, measurement_type: MeasurementAliasType) -> pd.DataFrame:
        """Return user measurements for a given age group and measurement.

        Args:
            age_group: Age group identifier.
            measurement_type: Measurement alias.

        Returns:
            DataFrame with columns "x" and "child".
        """
        config = AGE_GROUP_CONFIG[AgeGroup(age_group)]
        lower_limit, upper_limit = config.limits
        x_var_type = config.x_type

        filtered_measurements = []
        for entry in self.patient.measurements:
            if age_group in {"newborn", "very_preterm_newborn"}:
                if self.patient.get_age("age", entry.date) != 0:
                    continue

            if x_var_type in {"gestational_age", "age", "post_menstrual_age"}:
                x_value = self.patient.get_age(x_var_type, entry.date)
            else:
                x_value = getattr(entry, x_var_type)

            if lower_limit <= x_value <= upper_limit and hasattr(entry, measurement_type) and getattr(entry, measurement_type) is not None:
                filtered_measurements.append((x_value, getattr(entry, measurement_type)))

        x = [item[0] for item in filtered_measurements]
        y = [item[1] for item in filtered_measurements]

        return pd.DataFrame({"x": x, "child": y})

    def get_reference_data(self, age_group: AgeGroupType, measurement_type: MeasurementAliasType) -> GrowthTable:
        """Load reference data for a given age group and measurement.

        Args:
            age_group: Age group identifier.
            measurement_type: Measurement alias.

        Returns:
            GrowthTable containing reference LMS data.

        Raises:
            ValueError: If age_group is invalid or data is unavailable.
        """
        try:
            age_group_enum = AgeGroup(age_group)
        except ValueError as exc:
            raise ValueError(f"Invalid age group: {age_group}") from exc

        config = AGE_GROUP_CONFIG[age_group_enum]

        if self.patient.calculator.data is None:
            raise ValueError("Reference data is not available. Ensure the data file is present.")

        keys = KeyObject.from_oop(
            config.table_name,
            age_group=age_group,
            measurement_type=measurement_type,
            sex=self.patient.sex,
            x_var_type=config.x_type,
        )
        data = GrowthTable.from_data(self.patient.calculator.data, keys=keys)

        return data

    def get_plot_data(self, age_group: AgeGroupType, measurement_type: MeasurementAliasType) -> pd.DataFrame:
        """Return combined reference and user data for plotting.

        Args:
            age_group: Age group identifier.
            measurement_type: Measurement alias.

        Returns:
            DataFrame with reference curves and user data.
        """
        user_data = self.get_user_data(age_group, measurement_type)
        reference_data = self.get_reference_data(age_group, measurement_type)

        reference_data.add_child_data(user_data)
        return reference_data.convert_z_scores_to_values()

    def plot(
        self,
        age_group: AgeGroupType,
        measurement_type: MeasurementAliasType,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
    ) -> Axes:
        """Plot user measurements over reference curves.

        Args:
            age_group: Age group identifier.
            measurement_type: Measurement alias.
            ax: Optional Axes to draw into.
            show: Whether to display the plot.
            output_path: Optional file path for saving.

        Returns:
            Matplotlib Axes object.
        """
        user_data = self.get_user_data(age_group, measurement_type)
        ax = self.reference_plot(age_group, measurement_type, ax, False, "")

        ax.plot(
            user_data["x"],
            user_data["child"],
            label="user",
            **style.get_label_style("user"),
        )

        config = AGE_GROUP_CONFIG[AgeGroup(age_group)]
        set_xticks_by_range(ax, *config.limits)

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax

    def reference_plot(
        self,
        age_group: AgeGroupType,
        measurement_type: MeasurementAliasType,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
    ) -> Axes:
        """Plot only the reference curves.

        Args:
            age_group: Age group identifier.
            measurement_type: Measurement alias.
            ax: Optional Axes to draw into.
            show: Whether to display the plot.
            output_path: Optional file path for saving.

        Returns:
            Matplotlib Axes object.
        """
        plot_data = self.get_reference_data(age_group, measurement_type).convert_z_scores_to_values()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, cast(Axes, ax))

        config = AGE_GROUP_CONFIG[AgeGroup(age_group)]

        # Ensure measurement_type is treated as a string for formatting and lookup
        measurement_raw_str = str(measurement_type)
        resolved_measurement = ChoiceValidator.resolve_measurement_alias(measurement_raw_str) or measurement_raw_str
        measurement_config = MEASUREMENT_CONFIG[MeasurementType(resolved_measurement)]

        # Use a guaranteed string for label formatting
        measurement_str = str(resolved_measurement)

        x_label = config.x_type.replace("_", " ").title()
        y_label = f"{measurement_str.replace('_', ' ').title()} ({measurement_config.unit})"

        for z in [-3, -2, 0, 2, 3]:
            label = style.get_label_name(z)
            ax.plot(
                plot_data["x"],
                plot_data[z],
                label=f"{measurement_str.replace('_', ' ').title()} (Z={z})",
                **style.get_label_style(label),
            )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f"{measurement_str.replace('_', ' ').title()} Reference Plot ({self.patient.sex})")
        set_xticks_by_range(ax, *config.limits)

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax
