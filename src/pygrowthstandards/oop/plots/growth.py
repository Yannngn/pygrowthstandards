"""Plotting utilities for the OOP API."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from pygrowthstandards.config.growth import (
    MEASUREMENT_CONFIG,
    PLOT_GROUP_CONFIG,
    ChoiceValidator,
    MeasurementAliasType,
    MeasurementType,
    PlotGroup,
    PlotGroupType,
)
from pygrowthstandards.oop.growth.load import get_patient_data, get_reference_data
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.utils.plot import style
from pygrowthstandards.utils.plot.xticks import set_xticks_by_range


# TODO: review if the heavy use of config in this mixin is appropriate
class GrowthPlotterMixin:
    """Create reference and patient plots for growth data."""

    patient: Patient

    def plot(
        self,
        plot_group: PlotGroupType,
        measurement_type: MeasurementAliasType,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
    ) -> Axes:
        """Plot patient measurements over reference curves.

        Args:
            plot_group: Age group identifier.
            measurement_type: Measurement alias.
            ax: Optional Axes to draw into.
            show: Whether to display the plot.
            output_path: Optional file path for saving.

        Returns:
            Matplotlib Axes object.
        """
        patient_data = get_patient_data(self.patient, plot_group, measurement_type)
        ax = self.reference_plot(plot_group, measurement_type, ax, False, "")

        ax.plot(
            patient_data["x"],
            patient_data["patient"],
            label="patient",
            **style.get_label_style("patient"),
        )

        config = PLOT_GROUP_CONFIG[PlotGroup(plot_group)]
        set_xticks_by_range(ax, *config.limits)

        if output_path:
            plt.savefig(output_path)

        if show:
            plt.show()

        return ax

    def reference_plot(
        self,
        plot_group: PlotGroupType,
        measurement_type: MeasurementAliasType,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
    ) -> Axes:
        """Plot only the reference curves.

        Args:
            plot_group: Age group identifier.
            measurement_type: Measurement alias.
            ax: Optional Axes to draw into.
            show: Whether to display the plot.
            output_path: Optional file path for saving.

        Returns:
            Matplotlib Axes object.
        """
        plot_data = get_reference_data(self.patient, plot_group, measurement_type).convert_z_scores_to_values()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, ax)

        config = PLOT_GROUP_CONFIG[PlotGroup(plot_group)]

        # Ensure measurement_type is treated as a string for formatting and lookup
        measurement_raw_str = str(measurement_type)
        resolved_measurement = ChoiceValidator.resolve_measurement_alias(measurement_raw_str) or measurement_raw_str
        measurement_config = MEASUREMENT_CONFIG[MeasurementType(resolved_measurement)]

        # Use a guaranteed string for label formatting
        measurement_str = str(resolved_measurement)

        x_label = config.x_var_type.replace("_", " ").title()
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
