import os
import sys
from typing import Any, Collection

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from src.calculator.table_data import TableData
from src.utils.choices import (
    AGE_GROUP_CHOICES,
    AGE_GROUP_TYPE,
    MEASUREMENT_TYPE_CHOICES,
    MEASUREMENT_TYPE_TYPE,
)
from src.utils.errors import InvalidKeyPairError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.calculator.mixins import HandlerMixin
from src.utils.plot import style
from src.utils.plot.xticks import set_xticks_by_range


class Plotter(HandlerMixin):
    """A plotter for growth standards data visualization.

    This class provides functionality to plot growth standards data including
    percentile lines and measurement data points for children.

    Args:
        child: The Child object containing birth date and sex information.
    """

    def get_plot_data(
        self,
        age_group: AGE_GROUP_TYPE,
        measurement_type: str,
        unit_type: str = "age",
        user_data: bool = True,
        percentiles_or_zscores: Collection[int | float] = [-3, -2, 0, 2, 3],
    ) -> dict[Any, np.ndarray]:
        raise NotImplementedError("This method should be implemented in subclasses.")

    def plot_table(
        self,
        measurement_type: MEASUREMENT_TYPE_TYPE,
        age_group: AGE_GROUP_TYPE = "0-2",
        unit_type: str = "age",
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ) -> Axes:
        """Plot growth standards table with percentile lines.

        Creates a plot showing the growth standards table with percentile lines
        for the specified measurement type and age group. The plot can be displayed
        as an age-based plot or measurement-based plot depending on the measurement type.

        Args:
            measurement_type: The type of measurement to plot (e.g., 'weight', 'height').
            age_group: The age group for the plot (e.g., '0-2', '2-5'). Defaults to '0-2'.
            lines: Collection of z-score values to plot as percentile lines.
                Defaults to [-3, -2, 0, 2, 3].
            ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
            show: Whether to display the plot immediately. Defaults to False.
            output_path: Path to save the plot. If empty, plot is not saved.
            **kwargs: Additional keyword arguments passed to matplotlib plot functions.

        Returns:
            The matplotlib Axes object containing the plot.

        Raises:
            ValueError: If the measurement_type is not supported.
        """
        values = self.get_plot_data(age_group, measurement_type, unit_type, user_data=False)

        if unit_type in ["stature"]:
            ax = self._measurement_plot(values, measurement_type, unit_type, ax, **kwargs)
        elif measurement_type.endswith("_velocity"):
            raise NotImplementedError("Velocity plots are not implemented yet.")
        else:
            ax = self._age_plot(values, measurement_type, unit_type, ax, **kwargs)

        if output_path:
            output_path = output_path if output_path.endswith(".png") else os.path.join(output_path, f"{measurement_type}_{age_group}_plot.png")
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def plot_measurements(
        self,
        measurement_type: str,
        age_group: AGE_GROUP_TYPE = "0-2",
        unit_type: str = "age",
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ) -> Axes:
        """Plot child measurements with growth standards table.

        Creates a plot showing the child's measurements plotted against the growth
        standards table with percentile lines. The measurements are filtered to
        the appropriate date range based on the age group.

        Args:
            measurement_type: The type of measurement to plot (e.g., 'weight', 'height').
            age_group: The age group for the plot (e.g., '0-2', '2-5'). Defaults to '0-2'.
            lines: Collection of z-score values to plot as percentile lines.
                Defaults to [-3, -2, 0, 2, 3].
            ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
            show: Whether to display the plot immediately. Defaults to False.
            output_path: Path to save the plot. If empty, plot is not saved.
            **kwargs: Additional keyword arguments passed to matplotlib plot functions.

        Returns:
            The matplotlib Axes object containing the plot.

        Raises:
            ValueError: If the measurement_type is not supported.
        """
        values = self.get_plot_data(age_group, measurement_type, unit_type, True)

        if unit_type in ["stature"]:
            ax = self._measurement_plot(values, measurement_type, unit_type, ax, **kwargs)
        elif measurement_type.endswith("_velocity"):
            raise NotImplementedError("Velocity plots are not implemented yet.")
        else:
            ax = self._age_plot(values, measurement_type, unit_type, ax, **kwargs)

        if output_path:
            output_path = output_path if output_path.endswith(".png") else os.path.join(output_path, f"{measurement_type}_{age_group}_plot.png")
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def plot(
        self,
        measurement_type: str,
        age_group: AGE_GROUP_TYPE = "0-2",
        output_path: str = "",
        show: bool = True,
        **kwargs,
    ) -> Axes:
        """Plots the child's measurements against growth standards.

        Args:
            measurement_type: The type of measurement to plot (e.g., 'weight', 'stature').
            age_group: The age group for the plot (e.g., '0-2', '2-5'). Defaults to 'none'.
            **kwargs: Additional keyword arguments passed to the plotting function.
        """

        return self.plot_measurements(measurement_type, age_group, output_path=output_path, show=show, **kwargs)

    def save_plot(self, measurement_type: str, age_group: AGE_GROUP_TYPE = "0-2", output_path: str = "results", **kwargs):
        """Saves a plot of the child's measurements against growth standards.
        Args:
            measurement_type: The type of measurement to plot (e.g., 'weight', 'stature').
            age_group: The age group for the plot (e.g., '0-2', '2-5'). Defaults to 'none'.
            output_path: The file path where the plot will be saved. Defaults to None, which uses the current directory.
            **kwargs: Additional keyword arguments passed to the plotting function.
        """
        _ = self.plot(measurement_type, age_group, output_path=output_path, show=False, **kwargs)

    def plot_all_standards(self, output_path: str = "results", show: bool = False, **kwargs) -> None:
        """Plot all growth standards.

        This method iterates through all available measurement types and age groups,
        plotting each one using the `plot_measurements` method. The plots are saved
        to the specified output path.

        Args:
            output_path: The directory where the plots will be saved. Defaults to 'results'.
            show: Whether to display the plots immediately. Defaults to True.
            **kwargs: Additional keyword arguments passed to the plotting function.
        """
        self._data = TableData(None, None, None)
        for measurement_type in MEASUREMENT_TYPE_CHOICES:
            for age_group in AGE_GROUP_CHOICES:
                try:
                    self.plot_table(measurement_type, age_group, output_path=output_path, show=show, **kwargs)  # type: ignore
                except InvalidKeyPairError:
                    continue
                except NotImplementedError as e:
                    print(e)

                plt.close()

    def plot_all_measurements(self, output_path: str = "results", show: bool = False, **kwargs) -> None:
        """Plot all measurements for the child.

        This method iterates through all available measurement types and age groups,

        """
        for measurement_type in MEASUREMENT_TYPE_CHOICES:
            for age_group in AGE_GROUP_CHOICES:
                try:
                    self.plot_table(measurement_type, age_group, output_path=output_path, show=show, **kwargs)  # type: ignore
                except InvalidKeyPairError:
                    continue
                except NotImplementedError as e:
                    print(e)

                plt.close()

    def _plot(
        self,
        values: dict[str, np.ndarray],
        x_label: str = "x",
        y_label: str = "y",
        ax: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Create a generic plot with the given values and labels.

        This is a helper method that creates a matplotlib plot with the provided
        data and styling. It handles the creation of the figure and axes if needed,
        applies styling, and sets labels and titles.

        Args:
            values: Dictionary containing plot data where 'x' key contains x-axis values
                and other keys contain y-axis values for different lines.
            x_label: Label for the x-axis. Defaults to 'x'.
            y_label: Label for the y-axis. Defaults to 'y'.
            ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
            **kwargs: Additional keyword arguments passed to matplotlib plot functions.

        Returns:
            The matplotlib Axes object containing the plot.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, ax)

        x = values.pop("x")
        user = values.pop("user", None)
        for idx, y_points in values.items():
            label = style.get_label_name(int(idx))
            ax.plot(x, y_points, label=label, **style.get_label_style(label), **kwargs)

        if user is not None:
            ax.plot(x, user, label="User", **style.get_label_style("user"), **kwargs)

        set_xticks_by_range(ax, min(x), max(x))

        ax.set_xlabel(x_label.capitalize())
        ax.set_ylabel(y_label.capitalize())
        ax.set_title(f"{y_label.capitalize()} for {x_label.capitalize()}")
        ax.legend()
        ax.figure.tight_layout()  # type: ignore

        return ax

    def _age_plot(self, values: dict[str, np.ndarray], measurement_type: str, unit_type: str = "age", ax: Axes | None = None, **kwargs) -> Axes:
        """Create an age-based plot for the given measurement type.

        This method creates a plot where age is on the x-axis and the measurement
        values are on the y-axis. The plot is filtered to the specified age group.

        Args:
            measurement_type: The type of measurement to plot (e.g., 'weight', 'height').
            age_group: The age group for the plot (e.g., '0-2', '2-5'). Defaults to '0-2'.
            lines: Collection of z-score values to plot as percentile lines.
                Defaults to [-3, -2, 0, 2, 3].
            ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
            **kwargs: Additional keyword arguments passed to matplotlib plot functions.

        Returns:
            The matplotlib Axes object containing the plot.
        """
        x_label = unit_type.replace("_", " ").title()
        y_label = measurement_type.replace("_", " ").title()

        return self._plot(values, x_label=x_label, y_label=y_label, ax=ax, **kwargs)

    def _measurement_plot(self, values: dict[str, np.ndarray], measurement_type: str, unit_type: str, ax: Axes | None = None, **kwargs) -> Axes:
        """Create a measurement-based plot for weight-for-length/height type measurements.

        This method creates a plot where another measurement (length/height) is on the
        x-axis and the primary measurement (weight) is on the y-axis.

        Args:
            measurement_type: The type of measurement to plot (e.g., 'weight_length').
            lines: Collection of z-score values to plot as percentile lines.
                Defaults to [-3, -2, 0, 2, 3].
            ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
            **kwargs: Additional keyword arguments passed to matplotlib plot functions.

        Returns:
            The matplotlib Axes object containing the plot.
        """
        x_label = unit_type.replace("_", " ").title()
        y_label = measurement_type.replace("_", " ").title()

        return self._plot(values, x_label=x_label, y_label=y_label, ax=ax, **kwargs)
