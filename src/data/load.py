"""Load and manipulate growth standard reference data.

This module provides:

- GrowthTable: Dataclass for storing LMS parameters and transforming child data.
- load_reference: Function to read the compiled growth reference Parquet file.
- main: Demonstration entry point for loading and printing reference data.

Example:
    python -m src.data.load

Todo:
    * Support custom data paths and CLI integration.
"""

import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.utils.choices import (
    AgeGroupLiteral,
    DataSourceLiteral,
    MeasurementTypeLiteral,
    SexLiteral,
    TableNameLiteral,
    XVarNameLiteral,
    XVarUnitLiteral,
)

from ..utils.stats import numpy_calculate_value_for_z_score


# TODO: Age Group == array of strs?
@dataclass
class GrowthTable:
    """
    Stores LMS parameters and supports z-score/value transformations.

    Attributes:
        source (str): Origin of the data.
        name (str): Table identifier.
        age_group (str|None): Age group or None.
        measurement_type (str): Measurement category.
        sex (str): Sex code.
        x_var_type (str): Type of x variable.
        x_var_unit (str): Unit of x variable.
        x (np.ndarray): Independent variable values.
        L (np.ndarray): Lambda parameters.
        M (np.ndarray): Mu parameters.
        S (np.ndarray): Sigma parameters.
        is_derived (np.ndarray): Flags for derived LMS.
        y (np.ndarray): Child data values (populated by add_child_data).
    """

    source: DataSourceLiteral
    name: TableNameLiteral
    age_group: AgeGroupLiteral | None
    measurement_type: MeasurementTypeLiteral
    sex: SexLiteral
    x_var_type: XVarNameLiteral
    x_var_unit: XVarUnitLiteral
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
        name: TableNameLiteral | None,
        age_group: AgeGroupLiteral | None,
        measurement_type: MeasurementTypeLiteral,
        sex: SexLiteral,
        x_var_type: XVarNameLiteral | None,
    ) -> "GrowthTable":
        """
        Creates a GrowthTable by filtering reference DataFrame.

        Args:
            data (pandas.DataFrame): Reference data loaded.
            name (str|None): Specific table name filter.
            age_group (str|None): Age group filter.
            measurement_type (str): Measurement type to select.
            sex (str): Sex code to select.
            x_var_type (str|None): X variable type filter.

        Returns:
            GrowthTable: Populated growth table instance.

        Raises:
            AssertionError: If both name and age_group are None.
        """

        if all([name is None, age_group is None]):
            raise ValueError("Either name or age_group must be provided.")
        filtered: pd.DataFrame = data.copy()

        if name is not None:
            filtered = filtered[(filtered["name"] == name)]

        if age_group is not None:
            filtered = filtered[(filtered["age_group"] == age_group)]

        if x_var_type is not None:
            filtered = filtered[(filtered["x_var_type"] == x_var_type)]

        filtered = filtered[(filtered["measurement_type"] == measurement_type) & (filtered["sex"] == sex.upper())]

        unique_sources = filtered["source"].unique()
        unique_names = filtered["name"].unique()
        unique_age_groups = filtered["age_group"].unique()
        unique_x_var_types = filtered["x_var_type"].unique()
        unique_x_var_units = filtered["x_var_unit"].unique()

        if len(unique_sources) != 1:
            raise ValueError(f"Expected one source, found {len(unique_sources)}: {unique_sources}")
        if len(unique_names) != 1:
            raise ValueError(f"Expected one name, found {len(unique_names)}: {unique_names}")

        if len(unique_age_groups) > 1:
            unique_age_groups = None  # = unique_names

        # as default use 'age'/'gestational_age' for x_var_type if multiple types are found
        if len(unique_x_var_types) > 1:
            if age_group in [
                "very_preterm_newborn",
                "newborn",
                "very_preterm_growth",
            ] or name in [
                "very_preterm_newborn",
                "newborn",
                "very_preterm_growth",
            ]:
                filtered = filtered[(filtered["x_var_type"] == "gestational_age")]
            else:
                filtered = filtered[(filtered["x_var_type"] == "age")]

            unique_x_var_types = filtered["x_var_type"].unique()
            unique_x_var_units = filtered["x_var_unit"].unique()

        return cls(
            source=unique_sources[0],
            name=unique_names[0],
            age_group=unique_age_groups[0] if unique_age_groups is not None else None,
            measurement_type=measurement_type,
            sex=sex,
            x_var_type=unique_x_var_types[0],
            x_var_unit=unique_x_var_units[0],
            x=filtered["x"].to_numpy(),
            L=filtered["l"].to_numpy(),
            M=filtered["m"].to_numpy(),
            S=filtered["s"].to_numpy(),
            is_derived=filtered["is_derived"].to_numpy(),
        )

    def convert_z_scores_to_values(self, z_scores=[-3, -2, 0, 2, 3]) -> pd.DataFrame:
        """
        Computes measurement values at specified z-scores.

        Args:
            z_scores (list[int]): Z-scores to convert.

        Returns:
            pandas.DataFrame: Table with x, is_derived, and value columns per z-score.
        """

        data = pd.DataFrame(
            {
                "x": self.x,
                "is_derived": self.is_derived,
                **{z: numpy_calculate_value_for_z_score(z, self.L, self.M, self.S) for z in z_scores},
            }
        )

        if hasattr(self, "y"):
            data["y"] = self.y

        return data

    def add_child_data(self, child_data: pd.DataFrame) -> None:
        """
        Inserts child measurement series into the table.

        Args:
            child_data (pandas.DataFrame): Must contain 'x' and 'child' columns.

        Raises:
            ValueError: If child_data is improperly formatted.
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

    def cut_data(self, lower_limit: float, upper_limit: float) -> None:
        """
        Filters table rows by x variable limits.

        Args:
            lower_limit (float): Minimum x value to keep.
            upper_limit (float): Maximum x value to keep.
        """
        mask = (self.x >= lower_limit) & (self.x <= upper_limit)
        self.x = self.x[mask]
        self.L = self.L[mask]
        self.M = self.M[mask]
        self.S = self.S[mask]
        self.is_derived = self.is_derived[mask]


def load_reference():
    """
    Retrieves the compiled growth reference dataset.

    Returns:
        pandas.DataFrame: Loaded growth standards data.

    Raises:
        FileNotFoundError: If the parquet data file is missing.
    """
    data_path = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        os.pardir,
        "data",
        "pygrowthstandards_0.1.1.parquet",
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
