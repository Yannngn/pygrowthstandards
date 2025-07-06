import os
import sys
from datetime import timedelta
from typing import Collection

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from src.utils.constants import YEAR

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.calculator.child import Child
from src.calculator.handler import Handler
from src.calculator.measurement import Measurement
from src.calculator.table_data import TableData, TableFiles
from src.utils.plot import style
from src.utils.plot.xticks import set_xticks_by_range


class Plotter(Handler):
    def __init__(self, child: Child):
        self.child = child
        self._data = TableData(child.sex)

        self._measurements: list[Measurement] = []

    def plot_table(
        self,
        measurement_type: str,
        age_group: str = "0-2",
        lines: Collection[int | float] = [-3, -2, 0, 2, 3],
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

        name = self._data.get_table_name(measurement_type, age_group)

        if name in [TableFiles.GROWTH_WEIGHT_LENGTH, TableFiles.GROWTH_WEIGHT_HEIGHT]:
            ax = self._measurement_plot(measurement_type, lines, ax, **kwargs)
        else:
            ax = self._age_plot(measurement_type, age_group, lines, ax, **kwargs)

        if output_path:
            output_path = output_path if output_path.endswith(".png") else os.path.join(output_path, f"{name}_plot.png")
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def plot_measurements(
        self,
        measurement_type: str,
        age_group: str = "0-2",
        lines: Collection[int | float] = [-3, -2, 0, 2, 3],
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ):
        name = self._data.get_table_name(measurement_type, age_group)

        start_table, end_table = self._data.get_table_cutoffs(measurement_type, age_group)

        age_limits = self._get_age_limits(age_group)

        start_age = int(max(age_limits[0] if age_limits else -float("inf"), start_table))
        end_age = int(min(age_limits[1] if age_limits else float("inf"), end_table))

        bd = self.child.birthday_date

        if name in [TableFiles.GROWTH_WEIGHT_LENGTH, TableFiles.GROWTH_WEIGHT_HEIGHT]:
            ax = self._measurement_plot(measurement_type, lines, ax, **kwargs)

            start_date = bd if name in [TableFiles.GROWTH_WEIGHT_LENGTH] else bd + timedelta(YEAR * 2)
            end_date = bd + timedelta(YEAR * 2) if name in [TableFiles.GROWTH_WEIGHT_LENGTH] else bd + timedelta(YEAR * 5)

        else:
            ax = self._age_plot(measurement_type, age_group, lines, ax, **kwargs)

            start_date = bd + timedelta(start_age)
            end_date = bd + timedelta(end_age)

        measurements = self.get_measurements_by_date_range(start_date, end_date)

        label = self._data.get_measurement_type(name)

        ages = [self.child.age(m.date).days for m in measurements]
        values = [getattr(m, label) for m in measurements]

        label = label.replace("_", " ").title()

        ax.plot(ages, values, marker="o", linestyle="-", label=label, color="#2c2c2c", **kwargs)

        if output_path:
            output_path = output_path if output_path.endswith(".png") else os.path.join(output_path, f"{measurement_type}_plot.png")
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    def _age_plot(
        self,
        measurement_type: str,
        age_group: str = "0-2",
        lines: Collection[int | float] = [-3, -2, 0, 2, 3],
        ax: Axes | None = None,
        **kwargs,
    ):
        values = self._data.get_plot_data(measurement_type, age_group, values=lines)

        start_age, end_age = self._get_age_limits(age_group)

        filtered_indices = [idx for idx, age in enumerate(values["x"]) if start_age <= age <= end_age]
        for k in list(values.keys()):
            values[k] = [values[k][idx] for idx in filtered_indices]

        y_label = measurement_type.replace("_", " ").title()

        return self._plot(values, x_label="Age", y_label=y_label, ax=ax, **kwargs)

    def _measurement_plot(self, measurement_type: str, lines: Collection[int | float] = [-3, -2, 0, 2, 3], ax: Axes | None = None, **kwargs):
        values = self._data.get_plot_data(measurement_type, values=lines)

        y_label = measurement_type.split("_")[0].title()
        x_label = measurement_type.split("_")[-1].title()

        return self._plot(values, x_label=x_label, y_label=y_label, ax=ax, **kwargs)

    def _plot(
        self,
        values: dict[str, list[float]],
        x_label: str = "x",
        y_label: str = "y",
        ax: Axes | None = None,
        **kwargs,
    ):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, ax)

        x = values.pop("x")
        for idx, y_points in values.items():
            label = style.get_label_name(int(idx))
            ax.plot(x, y_points, label=label, **style.get_label_style(label), **kwargs)

        set_xticks_by_range(ax, min(x), max(x))

        ax.set_xlabel(x_label.capitalize())
        ax.set_ylabel(y_label.capitalize())
        ax.set_title(f"{y_label.capitalize()} for {x_label.capitalize()}")
        ax.legend()
        ax.figure.tight_layout()  # type: ignore

        return ax

    '''
    def _stats_plot(
        self,
        name: str,
        age_limits: str = "0-2",
        lines: Collection[int | float] = [-3, -2, 0, 2, 3],
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
        **kwargs,
    ):
        start_age = end_age = None

        values = self._data.get_plot_data(name, values=lines)

        if age_limits is not None and name not in [Tables.GROWTH_WEIGHT_LENGTH, Tables.GROWTH_WEIGHT_HEIGHT]:
            start_age, end_age = age_limits
            values = {k: v for k, v in values.items() if start_age <= k <= end_age}

        title = " ".join(name.split("_")).title()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            set_style(fig, ax)

        for line in lines:
            label = get_label_name(line)
            ax.axhline(y=line, label=label, **get_label_style(label), **kwargs)

        x = values.pop("x")

        if start_age is not None and end_age is not None:
            x.extend([start_age, end_age])

        set_xticks_by_range(ax, min(x), max(x))

        title = name.split("-")[-1].title()
        x_label = "Age"
        if name in [Tables.GROWTH_WEIGHT_LENGTH, Tables.GROWTH_WEIGHT_HEIGHT]:
            title = name.split("-")[-1].split("_")[0].title()
            x_label = name.split("-")[-1].split("_")[-1].title()

        ax.set_xlabel(x_label)
        ax.set_ylabel(title)
        ax.set_title(f"{title} for {x_label}")
        ax.legend()
        ax.figure.tight_layout()  # type: ignore

        if output_path:
            output_path = output_path if output_path.endswith(".png") else os.path.join(output_path, f"{name}_plot.png")
            ax.figure.savefig(output_path, dpi=300)  # type: ignore

        if show:
            plt.show()

        return ax

    # TODO: Add shadow plot functionality
    def _shadow_table_plot(self, name: str, ax: Axes | None = None, show: bool = True, **kwargs):
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
'''

    def save_plot(self, filename):
        raise NotImplementedError("Subclasses should implement this method")
        raise NotImplementedError("Subclasses should implement this method")
