import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..utils.stats import numpy_calculate_value_for_z_score


@dataclass
class GrowthTable:
    """
    Represents a growth table containing data points for growth standards.
    """

    source: str
    name: str
    measurement_type: str
    sex: str
    x_var_type: str
    x_var_unit: str
    x: np.ndarray
    L: np.ndarray
    M: np.ndarray
    S: np.ndarray
    is_derived: np.ndarray

    y: np.ndarray = field(init=False, repr=False)

    @classmethod
    def from_data(cls, data: pd.DataFrame, name: str, measurement_type: str, sex: str, x_var_type: str) -> "GrowthTable":
        """
        Loads a GrowthTable from a DataFrame, filtering by measurement_type, sex, and x_var_type.

        :param data: The DataFrame containing the growth data.
        :param name: The name of the growth table.
        :param measurement_type: The type of measurement (e.g., length, weight).
        :param sex: The sex of the subjects (e.g., male, female).
        :param x_var_type: The type of the x variable (e.g., age, height).
        :return: An instance of GrowthTable.
        """
        filtered = data[
            (data["name"] == name)
            & (data["measurement_type"] == measurement_type)
            & (data["sex"] == sex.upper())
            & (data["x_var_type"] == x_var_type)
        ]

        return cls(
            source=filtered["source"].iat[0],
            name=name,
            measurement_type=measurement_type,
            sex=sex,
            x_var_type=x_var_type,
            x_var_unit=filtered["x_var_unit"].iat[0],
            x=filtered["x"].to_numpy(),
            L=filtered["l"].to_numpy(),
            M=filtered["m"].to_numpy(),
            S=filtered["s"].to_numpy(),
            is_derived=filtered["is_derived"].to_numpy(),
        )

    def cut_data(self, lower_limit: float, upper_limit: float) -> None:
        """
        Cuts the data in the GrowthTable to the specified limits.

        :param lower_limit: The lower limit for the x variable.
        :param upper_limit: The upper limit for the x variable.
        """
        mask = (self.x >= lower_limit) & (self.x <= upper_limit)
        self.x = self.x[mask]
        self.L = self.L[mask]
        self.M = self.M[mask]
        self.S = self.S[mask]
        self.is_derived = self.is_derived[mask]

    def to_plot_data(self, z_scores=[-3, -2, 0, 2, 3]) -> pd.DataFrame:
        """
        Converts the GrowthTable to a DataFrame suitable for plotting.

        :return: A DataFrame with columns for x, L, M, S, and is_derived.
        """

        data = pd.DataFrame(
            {"x": self.x, "is_derived": self.is_derived, **{z: numpy_calculate_value_for_z_score(z, self.L, self.M, self.S) for z in z_scores}}
        )

        if hasattr(self, "y"):
            data["y"] = self.y

        return data

    def add_child_data(self, child_data: pd.DataFrame) -> None:
        """
        Adds child data to the GrowthTable.

        :param child_data: A DataFrame containing child data with columns 'x' and 'child'.
        """
        if not isinstance(child_data, pd.DataFrame) or not all(col in child_data.columns for col in ["x", "child"]):
            raise ValueError("child_data must be a DataFrame with 'x' and 'child' columns.")

        # Add new x values from child_data to self.x
        x = child_data["x"].to_numpy()
        y = child_data["child"].to_numpy()
        self.x = np.unique(np.sort(np.concatenate([self.x, x])))
        self.y = np.full_like(self.x, fill_value=None, dtype=object)
        x_indices = {val: idx for idx, val in enumerate(self.x)}
        for x_val, y_val in zip(x, y):
            idx = x_indices.get(x_val)
            if idx is not None:
                self.y[idx] = y_val


def load_reference():
    """
    Loads the growth reference data from a CSV file and returns a DataFrame.

    :return: A DataFrame containing the growth reference data.
    """
    data_path = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "data", "pygrowthstandards_0.1.0.parquet")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Growth reference data file not found at {data_path}")

    return pd.read_parquet(data_path)


def main():
    """
    Main function to demonstrate loading and using the GrowthTable.
    """
    data = load_reference()
    print(data.head())


if __name__ == "__main__":
    main()
