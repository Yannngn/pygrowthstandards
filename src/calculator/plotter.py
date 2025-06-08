import os
import sys

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.calculator.handler import Handler
from src.calculator.kid import Kid
from src.calculator.measurement import Measurement
from src.calculator.table_data import TABLES, TableData
from src.utils.plot.style import get_label_style, set_style
from src.utils.plot.xticks import set_xticks_by_range


class Plotter(Handler):
    def __init__(self, kid: Kid):
        self.kid = kid
        self._data = TableData(kid)

        self._measurements: list[Measurement] = []

    def table_plot(
        self,
        name: TABLES,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ):
        """
        Plots the given measurements on a graph.

        :param name: The name of the measurement to plot.
        :param ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
        :param show: Whether to call plt.show(). Set to False if you want to add more lines before showing.
        :param kwargs: Additional keyword arguments for plt.plot.
        :return: The matplotlib Axes object with the plot.
        """

        ax = self._table_plot(name, ax, **kwargs)

        if output_path:
            output_path = (
                output_path
                if output_path.endswith(".png")
                else os.path.join(output_path, f"{name}_plot.png")
            )
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def stats_plot(
        self,
        name: TABLES,
        zscores: bool = True,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ):

        x, y = self._data.get_plot_data(name)

        title = " ".join(name.split("_")).title()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            set_style(fig, ax)

        for label in y.keys():
            if zscores:
                digit = -int(label[2]) if label.endswith("neg") else int(label[2])
            else:
                digit = float(label[1:])
            ax.axhline(y=digit, label=label, **get_label_style(label), **kwargs)

        set_xticks_by_range(ax, min(x), max(x))

        ax.set_xlabel("Age")
        ax.set_ylabel(title)
        ax.set_title(f"{title} for Age")
        ax.legend()
        ax.figure.tight_layout()  # type: ignore

        if output_path:
            output_path = (
                output_path
                if output_path.endswith(".png")
                else os.path.join(output_path, f"{name}_plot.png")
            )
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def plot_measurements(
        self,
        name: TABLES,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ):
        ax = self._table_plot(name, ax, **kwargs)

        start_date, end_date = self._data.get_table_cutoffs(name)

        measurements = self.get_measurements_by_date_range(start_date, end_date)

        label = self._data.get_measurement_label(name)

        ages = [self.kid.age_days(m.date) for m in measurements]
        values = [getattr(m, label) for m in measurements]
        ax.plot(
            ages,
            values,
            marker="o",
            linestyle="-",
            label=label,
            color="#2c2c2c",
            **kwargs,
        )
        if output_path:
            output_path = (
                output_path
                if output_path.endswith(".png")
                else os.path.join(output_path, f"{name}_plot.png")
            )
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def _table_plot(self, name: TABLES, ax: Axes | None = None, **kwargs):
        """
        Plots the given measurements on a graph.

        :param name: The name of the measurement to plot.
        :param ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
        :param show: Whether to call plt.show(). Set to False if you want to add more lines before showing.
        :param kwargs: Additional keyword arguments for plt.plot.
        :return: The matplotlib Axes object with the plot.
        """

        x, y = self._data.get_plot_data(name)

        title = " ".join(name.split("_")).title()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            set_style(fig, ax)

        for label, y_points in reversed(list(y.items())):
            ax.plot(x, y_points, label=label, **get_label_style(label), **kwargs)

        set_xticks_by_range(ax, min(x), max(x))

        ax.set_xlabel("Age")
        ax.set_ylabel(title)
        ax.set_title(f"{title} for Age")
        ax.legend()
        ax.figure.tight_layout()  # type: ignore

        return ax

    # TODO: Add shadow plot functionality
    def _shadow_table_plot(
        self, name: TABLES, ax: Axes | None = None, show: bool = True, **kwargs
    ):
        """
        Plots the given measurements on a graph with filled area between min and max percentiles.

        :param name: The name of the measurement to plot.
        :param ax: Optional matplotlib Axes to plot on. If None, creates a new figure and axes.
        :param show: Whether to call plt.show(). Set to False if you want to add more lines before showing.
        :param kwargs: Additional keyword arguments for plt.plot.
        :return: The matplotlib Axes object with the plot.
        """

        x, y = self._data.get_plot_data(name)

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            set_style(fig, ax)

        # Plot all lines
        for label, y_points in y.items():
            ax.plot(x, y_points, label=label, **get_label_style(label), **kwargs)

        # Fill between min and max percentiles if possible
        y_values = list(y.values())
        if len(y_values) >= 2:
            y_min = y_values[0]
            y_max = y_values[-1]
            ax.fill_between(x, y_min, y_max, color="gray", alpha=0.2, label="Range")

        set_xticks_by_range(ax, min(x), max(x))

        ax.set_xlabel("Age")
        ax.set_ylabel(name)
        ax.set_title(f"{name} for age (with range fill)")
        ax.legend()
        ax.figure.tight_layout()  # type: ignore

        if show:
            plt.show()

        return ax

    def save_plot(self, filename):
        raise NotImplementedError("Subclasses should implement this method")
