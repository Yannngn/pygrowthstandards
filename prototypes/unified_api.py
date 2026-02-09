"""
Prototype: Unified API Facade

This prototype demonstrates a facade pattern that provides a simplified,
unified entry point for all PyGrowthStandards functionality. It intelligently
routes calls to the appropriate underlying implementation.

Key Features:
- Single import for all functionality
- Smart routing between functional and OOP APIs
- Convenience methods for common operations
- Batch processing support
"""

import datetime
from typing import Any

# NOTE: In real implementation, these would import from actual modules
# import pandas as pd
# from .. import functional
# from ..oop import Patient, MeasurementGroup
# from ..builders import PatientBuilder


class API:
    """
    Unified API facade for PyGrowthStandards.

    This class provides a single entry point for all common operations
    with intelligent routing to the appropriate underlying implementation.

    Example:
        >>> import pygrowthstandards as pgs
        >>> z = pgs.calculate("weight", 10.5, sex="M", age_days=365)
        >>> patient = pgs.patient(sex="M", birthday="2022-01-01")
    """

    @staticmethod
    def calculate(
        measurement: str,
        value: float,
        sex: str = "U",
        age_days: int | None = None,
        gestational_age: int | None = None,
        method: str = "zscore",
        **kwargs: Any,
    ) -> float:
        """
        Calculate z-score or percentile for a measurement.

        This is the universal calculation method that works with simple
        parameters for quick, one-off calculations.

        Args:
            measurement: Measurement type (e.g., "weight", "stature", "head_circumference")
            value: Measurement value
            sex: Patient sex ("M", "F", or "U")
            age_days: Age in days (for postnatal measurements)
            gestational_age: Gestational age in days (for prenatal/newborn)
            method: "zscore" or "percentile"
            **kwargs: Additional options

        Returns:
            Calculated z-score or percentile value

        Example:
            >>> z = API.calculate("weight", 10.5, sex="M", age_days=365)
            >>> p = API.calculate("stature", 75, sex="F", age_days=365, method="percentile")
        """
        # In real implementation:
        # if method == "zscore":
        #     return functional.zscore(
        #         measurement, value, sex, age_days, gestational_age, **kwargs
        #     )
        # elif method == "percentile":
        #     return functional.percentile(
        #         measurement, value, sex, age_days, gestational_age, **kwargs
        #     )
        # else:
        #     raise ValueError(f"Unknown method: {method}")

        # Mock for prototype
        print(f"[MOCK] Calculating {method} for {measurement}={value}, sex={sex}, age={age_days}")
        return 0.5  # Mock z-score

    @staticmethod
    def zscore(
        measurement: str,
        value: float,
        sex: str = "U",
        age_days: int | None = None,
        gestational_age: int | None = None,
    ) -> float:
        """
        Convenience method for z-score calculation.

        Args:
            measurement: Measurement type
            value: Measurement value
            sex: Patient sex
            age_days: Age in days
            gestational_age: Gestational age in days

        Returns:
            Z-score value

        Example:
            >>> z = API.zscore("weight", 10.5, "M", age_days=365)
        """
        return API.calculate(measurement, value, sex, age_days, gestational_age, method="zscore")

    @staticmethod
    def percentile(
        measurement: str,
        value: float,
        sex: str = "U",
        age_days: int | None = None,
        gestational_age: int | None = None,
    ) -> float:
        """
        Convenience method for percentile calculation.

        Args:
            measurement: Measurement type
            value: Measurement value
            sex: Patient sex
            age_days: Age in days
            gestational_age: Gestational age in days

        Returns:
            Percentile value (0.0 to 1.0)

        Example:
            >>> p = API.percentile("weight", 10.5, "M", age_days=365)
        """
        return API.calculate(measurement, value, sex, age_days, gestational_age, method="percentile")

    @staticmethod
    def patient(
        sex: str,
        birthday: datetime.date | str | None = None,
        gestational_age_weeks: int = 40,
        **kwargs: Any,
    ) -> Any:  # Returns PatientBuilder
        """
        Create a patient using the builder pattern.

        Returns a PatientBuilder that can be used to construct a patient
        with a fluent interface.

        Args:
            sex: Patient sex ("M", "F", or "U")
            birthday: Birthday date (optional)
            gestational_age_weeks: Gestational age in weeks
            **kwargs: Additional patient parameters

        Returns:
            PatientBuilder for fluent construction

        Example:
            >>> patient = (pgs.patient(sex="M", birthday="2022-01-01")
            ...     .measured_at("2022-07-01", weight=8.6, stature=68.4)
            ...     .build_and_calculate())
        """
        # In real implementation:
        # from ..builders import PatientBuilder
        # builder = PatientBuilder().with_sex(sex)
        #
        # if birthday:
        #     if isinstance(birthday, str):
        #         birthday = datetime.date.fromisoformat(birthday)
        #     builder = builder.born_on(birthday)
        #
        # if gestational_age_weeks != 40:
        #     builder = builder.gestational_age(gestational_age_weeks)
        #
        # return builder

        # Mock for prototype
        class MockBuilder:
            def __init__(self, sex, birthday):
                self.sex = sex
                self.birthday = birthday

            def measured_at(self, date, **measurements):
                print(f"[MOCK] Adding measurement at {date}: {measurements}")
                return self

            def build_and_calculate(self):
                print(f"[MOCK] Building patient: sex={self.sex}, birthday={self.birthday}")
                return self

        if isinstance(birthday, str):
            birthday = datetime.date.fromisoformat(birthday)

        return MockBuilder(sex, birthday)

    @staticmethod
    def quick_patient(
        sex: str,
        birthday: datetime.date | str,
        measurements: list[dict[str, Any]],
        gestational_age_weeks: int = 40,
    ) -> Any:  # Returns Patient
        """
        Quickly create a patient with measurements.

        This is a convenience method for creating a patient when you already
        have all the measurement data ready.

        Args:
            sex: Patient sex
            birthday: Birthday date
            measurements: List of measurement dictionaries with 'date' and values
            gestational_age_weeks: Gestational age in weeks

        Returns:
            Patient object with measurements added

        Example:
            >>> patient = pgs.quick_patient(
            ...     sex="M",
            ...     birthday="2022-01-01",
            ...     measurements=[
            ...         {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
            ...         {"date": "2023-01-01", "weight": 10.2, "stature": 75.7}
            ...     ]
            ... )
        """
        # In real implementation:
        # return (API.patient(sex, birthday, gestational_age_weeks)
        #     .with_measurements(measurements)
        #     .build())

        # Mock for prototype
        print(f"[MOCK] Creating quick patient with {len(measurements)} measurements")

        class MockPatient:
            def __init__(self):
                self.measurements = measurements

            def calculate_all(self):
                return self

        return MockPatient()

    @staticmethod
    def batch_calculate(
        data: Any,  # pd.DataFrame
        measurement_col: str,
        value_col: str,
        sex_col: str,
        age_days_col: str | None = None,
        gestational_age_col: str | None = None,
        method: str = "zscore",
    ) -> Any:  # pd.DataFrame
        """
        Calculate z-scores or percentiles for a batch of measurements.

        This method accepts a pandas DataFrame and adds a column with
        calculated results.

        Args:
            data: DataFrame with measurement data
            measurement_col: Column name with measurement types
            value_col: Column name with measurement values
            sex_col: Column name with sex values
            age_days_col: Column name with age in days
            gestational_age_col: Column name with gestational age
            method: "zscore" or "percentile"

        Returns:
            DataFrame with calculated values added in new column

        Example:
            >>> import pandas as pd
            >>> df = pd.DataFrame({
            ...     "measurement": ["weight", "stature"],
            ...     "value": [10.5, 75],
            ...     "sex": ["M", "F"],
            ...     "age_days": [365, 365]
            ... })
            >>> results = pgs.batch_calculate(
            ...     df,
            ...     measurement_col="measurement",
            ...     value_col="value",
            ...     sex_col="sex",
            ...     age_days_col="age_days"
            ... )
        """
        # In real implementation:
        # result_col = f"{method}_result"
        #
        # def calculate_row(row):
        #     return API.calculate(
        #         measurement=row[measurement_col],
        #         value=row[value_col],
        #         sex=row[sex_col],
        #         age_days=row[age_days_col] if age_days_col else None,
        #         gestational_age=row[gestational_age_col] if gestational_age_col else None,
        #         method=method
        #     )
        #
        # data[result_col] = data.apply(calculate_row, axis=1)
        # return data

        # Mock for prototype
        print(f"[MOCK] Batch calculating {method} for {len(data) if hasattr(data, '__len__') else 'N'} rows")
        return data


# =============================================================================
# Module-level convenience functions
# =============================================================================

# Create singleton instance
_api = API()

# Expose methods as module-level functions for easier access
calculate = _api.calculate
zscore = _api.zscore
percentile = _api.percentile
patient = _api.patient
quick_patient = _api.quick_patient
batch_calculate = _api.batch_calculate


__all__ = [
    "API",
    "calculate",
    "zscore",
    "percentile",
    "patient",
    "quick_patient",
    "batch_calculate",
]


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Unified API Facade Prototype - Usage Examples")
    print("=" * 80)

    # Example 1: Simple calculations
    print("\n1. Simple Calculations via Facade")
    print("-" * 80)

    z1 = calculate("weight", 10.5, sex="M", age_days=365)
    z2 = zscore("stature", 75, "F", age_days=365)
    p1 = percentile("weight", 10.5, "M", age_days=365)

    print(f"Z-score (method 1): {z1}")
    print(f"Z-score (method 2): {z2}")
    print(f"Percentile: {p1}")

    # Example 2: Patient creation via facade
    print("\n2. Patient Creation via Facade")
    print("-" * 80)

    patient_obj = (
        patient(sex="M", birthday="2022-01-01")
        .measured_at("2022-07-01", weight=8.6, stature=68.4)
        .measured_at("2023-01-01", weight=10.2, stature=75.7)
        .build_and_calculate()
    )

    print("Patient created and calculated via facade")

    # Example 3: Quick patient with measurements
    print("\n3. Quick Patient Creation")
    print("-" * 80)

    measurements = [
        {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
        {"date": "2023-01-01", "weight": 10.2, "stature": 75.7},
    ]

    quick_pt = quick_patient(sex="F", birthday="2022-01-01", measurements=measurements)

    print(f"Quick patient created with {len(quick_pt.measurements)} measurements")

    # Example 4: Batch calculation
    print("\n4. Batch Processing")
    print("-" * 80)

    # Mock DataFrame
    class MockDataFrame:
        def __init__(self):
            self.data = [
                {"measurement": "weight", "value": 10.5, "sex": "M", "age_days": 365},
                {"measurement": "stature", "value": 75, "sex": "F", "age_days": 365},
            ]

        def __len__(self):
            return len(self.data)

    df = MockDataFrame()
    results = batch_calculate(
        df,
        measurement_col="measurement",
        value_col="value",
        sex_col="sex",
        age_days_col="age_days",
    )

    print("Batch calculation completed")

    # Example 5: Compare import styles
    print("\n5. Import Style Comparison")
    print("-" * 80)
    print("Old style:")
    print("  from pygrowthstandards import functional as F")
    print("  from pygrowthstandards import Patient, MeasurementGroup")
    print("  z = F.zscore(...)")
    print()
    print("New facade style:")
    print("  import pygrowthstandards as pgs")
    print("  z = pgs.zscore(...)")
    print("  patient = pgs.patient(...)")
    print()
    print("Simpler imports, consistent namespace!")

    print("\n" + "=" * 80)
    print("Prototype demonstration complete!")
    print("=" * 80)
