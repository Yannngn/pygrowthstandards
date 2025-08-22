import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.utils.errors import InvalidChoicesError

from ..utils.config import (
    AgeGroupType,
    DataSexType,
    DataSourceType,
    DataXTypeType,
    MeasurementTypeType,
    TableNameType,
)
from ..utils.stats import numpy_calculate_value_for_z_score


# TODO: Age Group == array of strs?
@dataclass
class GrowthTable:
    """
    Represents a growth table containing data points for growth standards.
    """

    source: DataSourceType
    name: TableNameType
    age_group: AgeGroupType | None
    measurement_type: MeasurementTypeType
    sex: DataSexType
    x_var_type: DataXTypeType
    x: np.ndarray
    L: np.ndarray
    M: np.ndarray
    S: np.ndarray
    is_derived: np.ndarray

    y: np.ndarray = field(init=False, repr=False)

    @classmethod
    def from_data(
        cls,
        data: pd.DataFrame,
        name: TableNameType | None,
        age_group: AgeGroupType | None,
        measurement_type: MeasurementTypeType,
        sex: DataSexType,
        x_var_type: DataXTypeType | None,
    ) -> "GrowthTable":
        """
        Loads a GrowthTable from a DataFrame, filtering by measurement_type, sex, and x_var_type.

        :param data: The DataFrame containing the growth data.
        :param name: The name of the growth table.
        :param measurement_type: The type of measurement (e.g., length, weight).
        :param sex: The sex of the subjects (e.g., male, female).
        :param x_var_type: The type of the x variable (e.g., age, height).
        :return: An instance of GrowthTable.
        """

        assert not all([name is None, age_group is None]), (
            "Either name or age_group must be provided."
        )
        filtered: pd.DataFrame = data.copy()

        if name is not None:
            filtered = filtered[(filtered["name"] == name)]

        if age_group is not None:
            filtered = filtered[(filtered["age_group"] == age_group)]

        if x_var_type is not None:
            filtered = filtered[(filtered["x_var_type"] == x_var_type)]

        filtered = filtered[
            (filtered["measurement_type"] == measurement_type)
            & (filtered["sex"] == sex.upper())
        ]

        unique_sources = filtered["source"].unique()
        unique_names = filtered["name"].unique()
        unique_age_groups = filtered["age_group"].unique()
        unique_x_var_types = filtered["x_var_type"].unique()

        if filtered.empty:
            raise InvalidChoicesError(measurement_type, age_group)

        if len(unique_age_groups) > 1:
            unique_age_groups = None  # = unique_names

        # as default use 'age'/'gestational_age' for x_var_type if multiple types are found
        if len(unique_x_var_types) > 1:
            gestational = {"very_preterm_newborn", "newborn", "very_preterm_growth"}

            if age_group in gestational or name in gestational:
                filtered = filtered[(filtered["x_var_type"] == "gestational_age")]
            else:
                filtered = filtered[(filtered["x_var_type"] == "age")]

            unique_x_var_types = filtered["x_var_type"].unique()

        return cls(
            source=unique_sources[0],
            name=unique_names[0],
            age_group=unique_age_groups[0] if unique_age_groups is not None else None,
            measurement_type=measurement_type,
            sex=sex,
            x_var_type=unique_x_var_types[0],
            x=filtered["x"].to_numpy(),
            L=filtered["l"].to_numpy(),
            M=filtered["m"].to_numpy(),
            S=filtered["s"].to_numpy(),
            is_derived=filtered["is_derived"].to_numpy(),
        )

    def convert_z_scores_to_values(self, z_scores=[-3, -2, 0, 2, 3]) -> pd.DataFrame:
        """
        Converts the GrowthTable to a DataFrame suitable for plotting.

        :return: A DataFrame with columns for x, L, M, S, and is_derived.
        """

        data = pd.DataFrame(
            {
                "x": self.x,
                "is_derived": self.is_derived,
                **{
                    z: numpy_calculate_value_for_z_score(z, self.L, self.M, self.S)
                    for z in z_scores
                },
            }
        )

        if hasattr(self, "y"):
            data["y"] = self.y

        return data

    def add_child_data(self, child_data: pd.DataFrame) -> None:
        """
        Adds child data to the GrowthTable.

        :param child_data: A DataFrame containing child data with columns 'x' and 'child'.
        """
        if not isinstance(child_data, pd.DataFrame) or not all(
            col in child_data.columns for col in ["x", "child"]
        ):
            raise ValueError(
                "child_data must be a DataFrame with 'x' and 'child' columns."
            )

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


def load_reference():
    """
    Loads the growth reference data from a CSV file and returns a DataFrame.

    :return: A DataFrame containing the growth reference data.
    """
    data_path = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        "data",
        "pygrowthstandards_0.1.2.parquet",
    )
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
