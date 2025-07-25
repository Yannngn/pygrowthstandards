import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from src.data.load import GrowthTable
from src.oop.patient import Patient
from src.utils.constants import WEEK, YEAR
from src.utils.plot import style
from src.utils.plot.xticks import set_xticks_by_range


class Plotter:
    limits = {
        "very_preterm_newborn": (168, 230),
        "newborn": (230, 300),
        "very_preterm_growth": (27 * WEEK, 64 * WEEK),
        "0-1": (0, int(round(1 * YEAR))),
        "0-2": (0, int(round(2 * YEAR))),
        "2-5": (int(round(2 * YEAR)) + 1, int(round(5 * YEAR))),
        "5-10": (int(round(5 * YEAR)) + 1, int(round(10 * YEAR))),
        "10-19": (int(round(10 * YEAR)) + 1, int(round(19 * YEAR))),
    }
    names = {
        "very_preterm_newborn": "very_preterm_newborn",
        "newborn": "newborn",
        "very_preterm_growth": "very_preterm_growth",
        "0-1": "velocity",
        "0-2": "child_growth",
        "2-5": "child_growth",
        "5-10": "growth",
        "10-19": "growth",
    }
    x_var_types = {
        "very_preterm_newborn": "gestational_age",
        "newborn": "gestational_age",
        "very_preterm_growth": "gestational_age",
        "0-1": "age",
        "0-2": "age",
        "2-5": "age",
        "5-10": "age",
        "10-19": "age",
    }

    def __init__(self, patient: Patient):
        self.patient = patient

        self.setup()

    def setup(self):
        self.patient.calculate_all()

    def get_user_data(self, age_group: str, measurement_type: str) -> pd.DataFrame:
        lower_limit, upper_limit = self.limits[age_group]
        x_var_type = self.x_var_types[age_group]

        filtered_measurements = []
        for entry in self.patient.measurements:
            if age_group in ["newborn", "very_preterm_newborn"]:
                if self.patient.get_age("age", entry.date) != 0:
                    continue

            if x_var_type in ["gestational_age", "age"]:
                x_value = self.patient.get_age(x_var_type, entry.date)
            else:
                x_value: float = getattr(entry, x_var_type)

            if lower_limit <= x_value <= upper_limit and hasattr(entry, measurement_type) and getattr(entry, measurement_type) is not None:
                filtered_measurements.append((x_value, getattr(entry, measurement_type)))

        x = [item[0] for item in filtered_measurements]
        y = [item[1] for item in filtered_measurements]

        return pd.DataFrame({"x": x, "child": y})

    def get_reference_data(self, age_group: str, measurement_type: str) -> GrowthTable:
        if age_group not in self.limits:
            raise ValueError(f"Invalid age group: {age_group}")

        name = self.names[age_group]
        x_var_type = self.x_var_types[age_group]

        data = GrowthTable.from_data(self.patient.calculator.data, name, measurement_type, self.patient.sex, x_var_type)

        data.cut_data(*self.limits[age_group])

        return data

    def get_plot_data(self, age_group: str, measurement_type: str) -> pd.DataFrame:
        user_data = self.get_user_data(age_group, measurement_type)
        reference_data = self.get_reference_data(age_group, measurement_type)

        reference_data.add_child_data(user_data)

        return reference_data.to_plot_data()

    def plot(self, age_group: str, measurement_type: str, ax: Axes | None = None, show: bool = False, output_path: str = "") -> Axes:
        user_data = self.get_user_data(age_group, measurement_type)
        ax = self.reference_plot(age_group, measurement_type, ax, False, "")

        ax.plot(user_data["x"], user_data["child"], label="user", **style.get_label_style("user"))

        set_xticks_by_range(ax, self.limits[age_group][0], self.limits[age_group][1])

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax

    def reference_plot(self, age_group: str, measurement_type: str, ax: Axes | None = None, show: bool = False, output_path: str = "") -> Axes:
        plot_data = self.get_reference_data(age_group, measurement_type).to_plot_data()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, ax)

        x_label = "Gestational Age" if self.x_var_types[age_group] == "gestational_age" else "Age"
        y_label = measurement_type.replace("_", " ").capitalize()

        for z in [-3, -2, 0, 2, 3]:
            label = style.get_label_name(z)
            ax.plot(plot_data["x"], plot_data[z], label=f"{y_label} (Z={z})", **style.get_label_style(label))

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f"{y_label} Reference Plot ({self.patient.sex})")
        set_xticks_by_range(ax, self.limits[age_group][0], self.limits[age_group][1])

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax
