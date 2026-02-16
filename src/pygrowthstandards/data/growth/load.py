"""Load and query growth reference data for calculations and plotting."""

import logging
from dataclasses import dataclass, field
from typing import cast

import numpy as np
import pandas as pd

from pygrowthstandards.config.growth import (
    ChoiceValidator,
    PlotGroupAlias,
    SexAlias,
    TableNameAlias,
    resolve_table_context,
    resolve_x_var_type,
)
from pygrowthstandards.typing.growth import (
    DataSexType,
    DataSourceType,
    DataXVarType,
    MeasurementAliasType,
    PlotGroupType,
    TableNameType,
)
from pygrowthstandards.utils.errors import InvalidChoicesError
from pygrowthstandards.utils.stats import interpolate_lms, numpy_calculate_value_for_z_score


@dataclass
class KeyObject:
    """Normalized lookup keys for reference data selection.

    Attributes:
        name: Table name identifier.
        measurement_type: Canonical measurement alias.
        sex: Sex identifier.
        x_var_type: Axis type identifier.
        x: Axis value for lookup.
        plot_group: Optional plot group identifier.
    """

    name: str
    measurement_type: MeasurementAliasType
    sex: DataSexType
    x_var_type: DataXVarType
    x: float | None = None
    plot_group: PlotGroupType | None = None

    @staticmethod
    def _normalize_age_group(plot_group: str) -> PlotGroupType:
        """Normalize a human-readable plot group into a canonical key.

        Args:
            plot_group: Input plot group string.

        Returns:
            Canonical plot group key.

        Raises:
            ValueError: If the plot group is not recognized.
        """
        normalized = plot_group.lower().replace(" ", "_")
        if normalized in PlotGroupAlias:
            return cast(PlotGroupType, normalized)

        raise ValueError(f"Invalid plot group: {plot_group}. Must be one of: {sorted(PlotGroupAlias)}")

    @staticmethod
    def _normalize_measurement(measurement: str) -> MeasurementAliasType:
        """Normalize a measurement label into a canonical alias.

        Args:
            measurement: Input measurement string.

        Returns:
            Canonical measurement alias.

        Raises:
            ValueError: If the measurement cannot be resolved.
        """
        normalized = measurement.lower().replace("-", "_")
        resolved = ChoiceValidator.resolve_measurement_alias(normalized)
        if resolved is None:
            raise ValueError(f"Unknown measurement: {measurement}")

        return resolved

    @staticmethod
    def _normalize_sex(sex: str | None) -> DataSexType:
        """Normalize sex input, defaulting unknowns to 'U'.

        Args:
            sex: Input sex value.

        Returns:
            Canonical sex value.
        """
        if sex is None:
            return "U"

        normalized = sex.upper()
        if normalized in SexAlias:
            return cast(DataSexType, normalized)

        logging.warning(f"Unrecognized sex value {sex}, defaulting to 'U'.")

        return "U"

    @staticmethod
    def _normalize_x_var_type(x_var_type: str) -> DataXVarType:
        """Normalize an x_var_type alias to its canonical value.

        Args:
            x_var_type: Input axis type string.

        Returns:
            Canonical axis type.
        """
        return resolve_x_var_type(x_var_type)

    @staticmethod
    def _normalize_name(name: str) -> TableNameType:
        """Normalize a table name to its canonical value.

        Args:
            name: Input table name.

        Returns:
            Canonical table name.

        Raises:
            ValueError: If the table name is not recognized.
        """
        normalized = name.lower().replace(" ", "_")
        if normalized in TableNameAlias:
            return cast(TableNameType, normalized)

        raise ValueError(f"Invalid table name: {name}. Must be one of: {sorted(TableNameAlias)}")

    @staticmethod
    def _normalize_x(x_value: float | None) -> float:
        """Normalize and validate an x value.

        Args:
            x_value: Input x value.

        Returns:
            Normalized x value.

        Raises:
            ValueError: If the value is missing.
        """
        if x_value is None:
            raise ValueError("x_value is required for the selected x_var_type.")
        return float(x_value)

    @classmethod
    def from_functional(
        cls,
        measurement: MeasurementAliasType,
        sex: DataSexType | None = None,
        age_days: int | None = None,
        gestational_age: int | None = None,
        x_var_type: str | None = None,
        x_value: float | None = None,
    ) -> "KeyObject":
        """Build a KeyObject from functional API inputs.

        Args:
            measurement: Measurement alias.
            sex: Sex identifier.
            age_days: Chronological age in days.
            gestational_age: Gestational age in days.
            x_var_type: Explicit axis type when providing x_value.
            x_value: Explicit axis value.

        Returns:
            KeyObject for reference lookup.
        """
        normalized_measurement = cls._normalize_measurement(measurement)
        name, resolved_x_var_type, resolved_x_value, resolved_age_group = resolve_table_context(
            normalized_measurement,
            age_days=age_days,
            gestational_age=gestational_age,
            x_var_type=x_var_type,
            x_value=x_value,
        )

        if resolved_x_var_type == "stature" and normalized_measurement != "weight":
            raise ValueError("x_var_type='stature' is only supported for weight-for-stature calculations.")

        return cls(
            name,
            normalized_measurement,
            cls._normalize_sex(sex),
            resolved_x_var_type,
            resolved_x_value,
            resolved_age_group,
        )

    @classmethod
    def from_oop(
        cls,
        name: str,
        measurement_type: MeasurementAliasType,
        plot_group: PlotGroupType,
        x_var_type: DataXVarType,
        sex: DataSexType | None = None,
    ) -> "KeyObject":
        """Build a KeyObject from object-oriented API inputs.

        Args:
            name: Table name identifier.
            measurement_type: Measurement alias.
            plot_group: Age group identifier.
            x_var_type: Axis type.
            sex: Sex identifier.

        Returns:
            KeyObject for reference lookup.
        """
        return cls(
            cls._normalize_name(name),
            cls._normalize_measurement(measurement_type),
            cls._normalize_sex(sex),
            cls._normalize_x_var_type(x_var_type),
            None,  # X
            cls._normalize_age_group(plot_group),
        )


# TODO: Plot Group == array of strs?
# TODO: make another layer of abstraction for the growth table and separate standards and patient data
@dataclass
class GrowthTable:
    """Structured LMS arrays for a single measurement and cohort.

    Attributes:
        source: Data source identifier.
        name: Table name identifier.
        plot_group: Age group identifier.
        measurement_type: Measurement alias.
        sex: Sex identifier.
        x_var_type: Axis type identifier.
        x: Array of x values.
        L: Array of L values.
        M: Array of M values.
        S: Array of S values.
        is_derived: Array of derivation flags.
    """

    source: DataSourceType
    name: TableNameType
    plot_group: PlotGroupType | None  # helper column, not required
    measurement_type: MeasurementAliasType
    sex: DataSexType
    x_var_type: DataXVarType
    x: np.ndarray
    L: np.ndarray
    M: np.ndarray
    S: np.ndarray
    is_derived: np.ndarray

    y: np.ndarray = field(init=False, repr=False, default_factory=lambda: np.array([]))
    _patient_x: np.ndarray = field(init=False, repr=False, default_factory=lambda: np.array([]))
    _patient_y: np.ndarray = field(init=False, repr=False, default_factory=lambda: np.array([]))

    @staticmethod
    def filter_by_keys(data: pd.DataFrame, keys: KeyObject) -> pd.DataFrame:
        """Filter reference data to the rows matching the given keys.

        Args:
            data: Reference data DataFrame.
            keys: Normalized lookup keys.

        Returns:
            Filtered DataFrame.

        Raises:
            InvalidChoicesError: If no data matches the keys.
        """
        filtered = data.copy()
        filtered = filtered[(filtered["name"] == keys.name)]
        if keys.plot_group is not None:
            filtered = filtered[(filtered["plot_group"] == keys.plot_group)]
        filtered = filtered[(filtered["x_var_type"] == keys.x_var_type)]
        filtered = filtered[(filtered["measurement_type"] == keys.measurement_type)]

        if keys.sex == "U":
            available = set(filtered["sex"].str.upper().unique())
            if "U" in available:
                filtered = filtered[(filtered["sex"].str.upper() == "U")]
            elif "F" in available:
                filtered = filtered[(filtered["sex"].str.upper() == "F")]
            elif "M" in available:
                filtered = filtered[(filtered["sex"].str.upper() == "M")]
        else:
            filtered = filtered[(filtered["sex"].str.upper() == keys.sex)]

        if filtered.empty:
            raise InvalidChoicesError(keys.measurement_type, keys.plot_group)

        return filtered

    @classmethod
    def from_data(cls, data: pd.DataFrame, keys: KeyObject) -> "GrowthTable":
        """Load a GrowthTable from a normalized DataFrame.

        Args:
            data: Reference data DataFrame.
            keys: Normalized lookup keys.

        Returns:
            GrowthTable populated from the data.
        """
        # Normalize incoming reference-style DataFrame columns to canonical values
        data = _normalize_reference_data(data.copy())
        filtered = cls.filter_by_keys(data, keys)

        source = filtered["source"].unique()[0]
        name = filtered["name"].unique()[0]
        age_groups = filtered["plot_group"].dropna().unique()
        if len(age_groups) > 1:
            raise ValueError("Multiple age groups found for keys; provide plot_group to disambiguate.")
        plot_group = age_groups[0] if len(age_groups) == 1 else None
        x_var_type = filtered["x_var_type"].unique()[0]

        # FIXME: if x_var_type_unique > 1 causes problems
        return cls(
            source=source,
            name=name,
            plot_group=plot_group,
            measurement_type=keys.measurement_type,
            sex=keys.sex,
            x_var_type=x_var_type,
            x=filtered["x"].to_numpy(),
            L=filtered["l"].to_numpy(),
            M=filtered["m"].to_numpy(),
            S=filtered["s"].to_numpy(),
            is_derived=filtered["is_derived"].to_numpy(),
        )

    def convert_z_scores_to_values(self, z_scores: list[float] | None = None) -> pd.DataFrame:
        """Compute value curves for the requested z-scores.

        Args:
            z_scores: Z-scores to compute. Defaults to [-3, -2, 0, 2, 3].

        Returns:
            DataFrame of x values and computed curves. Includes reference curves and patient data if available.
        """
        if not z_scores:
            z_scores = [-3, -2, 0, 2, 3]

        # Build reference data using original arrays
        data = pd.DataFrame(
            {
                "x": self.x,
                "is_derived": self.is_derived,
                **{z: numpy_calculate_value_for_z_score(z, self.L, self.M, self.S) for z in z_scores},
            }
        )

        # Add patient data row if available
        if len(self._patient_x) > 0:
            patient_rows = []
            for patient_x, patient_y in zip(self._patient_x, self._patient_y, strict=False):
                # Try to interpolate L, M, S for the patient x value
                row = {
                    "x": patient_x,
                    "is_derived": False,
                    "y": patient_y,
                }

                try:
                    results = interpolate_lms(patient_x, self.x, self.L, self.M, self.S)
                    # Add computed curve values for this patient point
                    for z in z_scores:
                        row[str(z)] = numpy_calculate_value_for_z_score(z, *map(lambda v: np.array(v), results))
                except ValueError:
                    # If patient x is out of bounds, still include the point but with NaN for curves
                    for z in z_scores:
                        row[str(z)] = np.nan

                patient_rows.append(row)

            # Append patient data rows to the dataframe
            if patient_rows:
                patient_df = pd.DataFrame(patient_rows)
                # Ensure column order matches when concatenating
                data = pd.concat([data, patient_df], ignore_index=True, sort=False)

        if hasattr(self, "y"):
            data["y"] = self.y

        return data

    def add_patient_data(self, patient_data: pd.DataFrame) -> None:
        """Store patient observations separately for use in conversions and plotting.

        Args:
            patient_data: DataFrame with columns 'x' and 'patient'.

        Raises:
            ValueError: If the data is missing required columns.
        """
        if not isinstance(patient_data, pd.DataFrame) or not all(col in patient_data.columns for col in ["x", "patient"]):
            raise ValueError("patient_data must be a DataFrame with 'x' and 'patient' columns.")

        # Store patient x and y values separately without modifying reference arrays
        self._patient_x = patient_data["x"].to_numpy()
        self._patient_y = patient_data["patient"].to_numpy()

    def cut_data(self, lower_limit: float, upper_limit: float) -> None:
        """Trim the table arrays to the provided x range.

        Args:
            lower_limit: Lower bound for x values.
            upper_limit: Upper bound for x values.
        """
        mask = (self.x >= lower_limit) & (self.x <= upper_limit)
        self.x = self.x[mask]
        self.L = self.L[mask]
        self.M = self.M[mask]
        self.S = self.S[mask]
        self.is_derived = self.is_derived[mask]
        if hasattr(self, "y"):
            self.y = self.y[mask]

        # Filter patient data to the same x range
        if len(self._patient_x) > 0:
            patient_mask = (self._patient_x >= lower_limit) & (self._patient_x <= upper_limit)
            self._patient_x = self._patient_x[patient_mask]
            self._patient_y = self._patient_y[patient_mask]


def load_reference():
    """Load the packaged reference data into a DataFrame.

    Returns:
        DataFrame of reference data.

    Raises:
        FileNotFoundError: If the packaged data is missing.
    """
    from pygrowthstandards.data import data_exists, get_data_path

    data_path = get_data_path()

    if not data_exists():
        raise FileNotFoundError(f"Growth reference data file not found at {data_path}. Please ensure the package was installed correctly.")

    data = pd.read_parquet(data_path)
    return _normalize_reference_data(data)


def _normalize_reference_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize reference data columns to canonical config values.

    Args:
        data: Input reference DataFrame.

    Returns:
        Normalized DataFrame.
    """

    def resolve_measurement(value: str) -> str:
        if value is None:
            return value
        resolved = ChoiceValidator.resolve_measurement_alias(str(value))
        return resolved if resolved is not None else value

    data = data.copy()
    data["x_var_type"] = data["x_var_type"].apply(resolve_x_var_type)
    data["measurement_type"] = data["measurement_type"].apply(resolve_measurement)

    return data
