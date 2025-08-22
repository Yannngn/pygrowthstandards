import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from ..data.load import GrowthTable
from ..utils.config import (
    AGE_GROUP_CONFIG,
    MEASUREMENT_CONFIG,
    AgeGroupType,
    MeasurementTypeType,
)
from ..utils.plot import style
from ..utils.plot.xticks import set_xticks_by_range
from .patient import Patient


class Plotter:
    def __init__(self, patient: Patient):
        self.patient = patient
        self.setup()

    def setup(self):
        self.patient.calculate_all()

    def get_user_data(self, age_group: AgeGroupType, measurement_type: MeasurementTypeType) -> pd.DataFrame:
        config = AGE_GROUP_CONFIG[age_group]
        lower_limit, upper_limit = config.limits
        x_var_type = config.x_type

        filtered_measurements = []
        for entry in self.patient.measurements:
            if age_group in {"newborn", "very_preterm_newborn"}:
                if self.patient.get_age("age", entry.date) != 0:
                    continue

            if x_var_type in {"gestational_age", "age"}:
                x_value = self.patient.get_age(x_var_type, entry.date)
            else:
                x_value: float = getattr(entry, x_var_type)

            if lower_limit <= x_value <= upper_limit and hasattr(entry, measurement_type) and getattr(entry, measurement_type) is not None:
                filtered_measurements.append((x_value, getattr(entry, measurement_type)))

        x = [item[0] for item in filtered_measurements]
        y = [item[1] for item in filtered_measurements]

        return pd.DataFrame({"x": x, "child": y})

    def get_reference_data(self, age_group: AgeGroupType, measurement_type: MeasurementTypeType) -> GrowthTable:
        if age_group not in AGE_GROUP_CONFIG:
            raise ValueError(f"Invalid age group: {age_group}")

        config = AGE_GROUP_CONFIG[age_group]
        name = config.table_name
        x_var_type = config.x_type

        data = GrowthTable.from_data(
            self.patient.calculator.data,
            name=name,
            age_group=age_group,
            measurement_type=measurement_type,
            sex=self.patient.sex,
            x_var_type=x_var_type,
        )

        return data

    def get_plot_data(self, age_group: AgeGroupType, measurement_type: MeasurementTypeType) -> pd.DataFrame:
        user_data = self.get_user_data(age_group, measurement_type)
        reference_data = self.get_reference_data(age_group, measurement_type)

        reference_data.add_child_data(user_data)
        return reference_data.convert_z_scores_to_values()

    def plot(
        self,
        age_group: AgeGroupType,
        measurement_type: MeasurementTypeType,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
    ) -> Axes:
        user_data = self.get_user_data(age_group, measurement_type)
        ax = self.reference_plot(age_group, measurement_type, ax, False, "")

        ax.plot(
            user_data["x"],
            user_data["child"],
            label="user",
            **style.get_label_style("user"),
        )

        config = AGE_GROUP_CONFIG[age_group]
        set_xticks_by_range(ax, *config.limits)

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax

    def reference_plot(
        self,
        age_group: AgeGroupType,
        measurement_type: MeasurementTypeType,
        ax: Axes | None = None,
        show: bool = False,
        output_path: str = "",
    ) -> Axes:
        plot_data = self.get_reference_data(age_group, measurement_type).convert_z_scores_to_values()

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            style.set_style(fig, ax)

        config = AGE_GROUP_CONFIG[age_group]
        measurement_config = MEASUREMENT_CONFIG[measurement_type]

        x_label = config.x_type.replace("_", " ").title()
        y_label = f"{measurement_type.replace('_', ' ').title()} ({measurement_config.unit})"

        for z in [-3, -2, 0, 2, 3]:
            label = style.get_label_name(z)
            ax.plot(
                plot_data["x"],
                plot_data[z],
                label=f"{measurement_type.replace('_', ' ').title()} (Z={z})",
                **style.get_label_style(label),
            )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f"{measurement_type.replace('_', ' ').title()} Reference Plot ({self.patient.sex})")
        set_xticks_by_range(ax, *config.limits)

        if show:
            plt.show()

        if output_path:
            plt.savefig(output_path)

        return ax
