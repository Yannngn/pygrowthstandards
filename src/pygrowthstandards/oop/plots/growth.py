"""Plotting utilities for the OOP API."""

from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from pygrowthstandards.config.growth import (
    MEASUREMENT_CONFIG,
    PLOT_GROUP_CONFIG,
    ChoiceValidator,
    Measurements,
    PlotGroup,
)
from pygrowthstandards.oop.growth.load import get_patient_data, get_reference_data
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.typing.growth import (
    MeasurementAliasType,
    PlotGroupType,
)
from pygrowthstandards.utils.plot import style
from pygrowthstandards.utils.plot.xticks import set_velocity_xticks, set_xticks_by_range


# TODO: review if the heavy use of config in this mixin is appropriate
class GrowthPlotterMixin:
    """Create reference and patient plots for growth data."""

    patient: Patient

    def _resolve_plot_group(self, plot_group: str, measurement_type: str) -> tuple[PlotGroupType, MeasurementAliasType]:
        measurement_raw_str = str(measurement_type)
        resolved_measurement = ChoiceValidator.resolve_measurement_alias(measurement_raw_str) or measurement_raw_str

        if str(resolved_measurement).endswith("_velocity"):
            return PlotGroup.VELOCITY.value, cast(MeasurementAliasType, resolved_measurement)

        # TODO: Add validation to ensure the plot group is valid

        return cast(PlotGroupType, plot_group), cast(MeasurementAliasType, resolved_measurement)

    def _format_x_label(self, config, plot_group: PlotGroupType) -> str:
        if plot_group == PlotGroup.VELOCITY.value:
            return "Age Interval"

        if config.x_var_type in {"length", "height"}:
            return f"{config.x_var_type.title()} (cm)"

        return config.x_var_type.replace("_", " ").title()

    def _format_title(self, plot_group: PlotGroupType, measurement_display: str) -> str:
        if plot_group == PlotGroup.WEIGHT_FOR_LENGTH.value:
            return f"Weight for Length ({self.patient.sex})"
        if plot_group == PlotGroup.WEIGHT_FOR_HEIGHT.value:
            return f"Weight for Height ({self.patient.sex})"
        return f"{measurement_display} Reference Plot ({self.patient.sex})"

    def _apply_xticks(self, ax: Axes, config, plot_group: PlotGroupType, x_values) -> None:
        if plot_group == PlotGroup.VELOCITY.value:
            set_velocity_xticks(ax, x_values)
            return

        set_xticks_by_range(ax, *config.limits)

    def _plot_series(self, ax: Axes, x_values, y_values, plot_group: PlotGroupType, **style_kwargs):
        if plot_group == PlotGroup.VELOCITY.value:
            return ax.step(x_values, y_values, where="post", **style_kwargs)

        return ax.plot(x_values, y_values, **style_kwargs)

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
        resolved_plot_group, resolved_measurement = self._resolve_plot_group(plot_group, measurement_type)

        patient_data = get_patient_data(self.patient, resolved_plot_group, resolved_measurement)
        ax = self.reference_plot(resolved_plot_group, resolved_measurement, ax, False, "")

        self._plot_series(
            ax,
            patient_data["x"],
            patient_data["patient"],
            resolved_plot_group,
            label="patient",
            **style.get_group_label_style(resolved_plot_group, "patient"),
        )

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
        resolved_plot_group, resolved_measurement = self._resolve_plot_group(plot_group, measurement_type)
        plot_data = get_reference_data(self.patient, resolved_plot_group, resolved_measurement).convert_z_scores_to_values()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, ax)

        config = PLOT_GROUP_CONFIG[PlotGroup(resolved_plot_group)]

        measurement_config = MEASUREMENT_CONFIG[Measurements(resolved_measurement)]
        measurement_str = str(resolved_measurement)
        measurement_display = measurement_str.replace("_", " ").title()

        x_label = self._format_x_label(config, resolved_plot_group)
        y_label = f"{measurement_display} ({measurement_config.unit})"

        for z in [-3, -2, 0, 2, 3]:
            label = style.get_label_name(z)
            self._plot_series(
                ax,
                plot_data["x"],
                plot_data[z],
                resolved_plot_group,
                label=f"{measurement_str.replace('_', ' ').title()} (Z={z})",
                **style.get_group_label_style(resolved_plot_group, label),
            )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(self._format_title(resolved_plot_group, measurement_display))
        self._apply_xticks(ax, config, resolved_plot_group, plot_data["x"])

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax
