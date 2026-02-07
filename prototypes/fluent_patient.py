"""
Prototype: Fluent Patient with Method Chaining

This prototype demonstrates how to enhance the existing Patient class with
method chaining capabilities while maintaining 100% backward compatibility.

Key Features:
- Returns self from mutation methods
- Adds convenient measured_at() method
- Integrates plotting directly
- Minimal changes to existing code
"""

import datetime
from typing import Any, Self

# NOTE: These imports would be from actual library in implementation
# from ..oop.patient import Patient
# from ..oop.measurement import Measurement, MeasurementGroup
# from ..oop.plotter import Plotter


class FluentPatient:  # In real implementation: class FluentPatient(Patient)
    """
    Enhanced Patient class with fluent interface support.
    
    This class extends Patient to enable method chaining while maintaining
    complete backward compatibility with existing code.
    
    Example:
        >>> patient = (FluentPatient(sex="M", birthday_date=datetime.date(2022, 1, 1))
        ...     .measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
        ...     .measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
        ...     .calculate_all()
        ...     .plot("weight", age_group="0-2"))
    """
    
    def __init__(self, sex: str, birthday_date: datetime.date | None,
                 gestational_age_weeks: int = 40,
                 gestational_age_days: int = 0):
        """Initialize patient with demographics."""
        # Call parent __init__
        # super().__init__(sex, birthday_date, gestational_age_weeks, gestational_age_days)
        
        # Mock initialization for prototype
        self.sex = sex
        self.birthday_date = birthday_date
        self.gestational_age_weeks = gestational_age_weeks
        self.measurements = []
        self.z_scores = []
    
    def add_measurement(self, measurement: Any) -> Self:
        """
        Add single measurement and return self for chaining.
        
        Args:
            measurement: Measurement object to add
        
        Returns:
            Self for method chaining
        
        Example:
            >>> patient.add_measurement(Measurement(...)).add_measurement(Measurement(...))
        """
        # super().add_measurement(measurement)  # Call parent method
        self.measurements.append(measurement)  # Mock for prototype
        return self
    
    def add_measurements(self, measurements: Any) -> Self:
        """
        Add measurement group and return self for chaining.
        
        Args:
            measurements: MeasurementGroup to add
        
        Returns:
            Self for method chaining
        
        Example:
            >>> patient.add_measurements(MeasurementGroup(...)).calculate_all()
        """
        # super().add_measurements(measurements)  # Call parent method
        self.measurements.append(measurements)  # Mock for prototype
        return self
    
    def calculate_all(self) -> Self:
        """
        Calculate all z-scores and return self for chaining.
        
        Returns:
            Self for method chaining
        
        Example:
            >>> patient.add_measurements(...).calculate_all().display_measurements()
        """
        # super().calculate_all()  # Call parent method
        # Mock calculation for prototype
        self.z_scores = [{"mock": "z-score"} for _ in self.measurements]
        return self
    
    def measured_at(self, date: datetime.date, **measurements: float) -> Self:
        """
        Convenient method to add measurements at a specific date.
        
        This is a new convenience method that doesn't exist in the parent class.
        It provides a more fluent way to add measurements.
        
        Args:
            date: Date of measurement
            **measurements: Measurement values (weight, stature, head_circumference, etc.)
        
        Returns:
            Self for chaining
        
        Example:
            >>> patient.measured_at(
            ...     datetime.date(2022, 7, 1),
            ...     weight=8.6,
            ...     stature=68.4,
            ...     head_circumference=44.5
            ... )
        """
        # In real implementation:
        # group = MeasurementGroup(date=date, **measurements)
        # self.add_measurements(group)
        
        # Mock for prototype
        measurement_data = {"date": date, **measurements}
        self.measurements.append(measurement_data)
        return self
    
    def plot(self, measurement_type: str, age_group: str | None = None, 
             **kwargs: Any) -> Self:
        """
        Plot growth chart and return self for chaining.
        
        This integrates the Plotter directly into the Patient API for convenience.
        
        Args:
            measurement_type: Type of measurement to plot (e.g., "weight", "stature")
            age_group: Age group for chart (e.g., "0-2", "2-5"). Auto-inferred if None.
            **kwargs: Additional plotting options (show, output_path, etc.)
        
        Returns:
            Self for chaining
        
        Example:
            >>> patient.calculate_all().plot("weight", show=False, output_path="chart.png")
        """
        # In real implementation:
        # from ..oop.plotter import Plotter
        # plotter = Plotter(self)
        # plotter.plot(
        #     measurement_type=measurement_type,
        #     age_group=age_group or self._infer_age_group(),
        #     **kwargs
        # )
        
        # Mock for prototype
        print(f"[MOCK] Plotting {measurement_type} for age group {age_group}")
        return self
    
    def filter(self, **criteria: Any) -> Self:
        """
        Filter measurements based on criteria.
        
        This is a potential future enhancement for filtering patient data.
        
        Args:
            **criteria: Filtering conditions
        
        Returns:
            New FluentPatient with filtered measurements (or self for in-place)
        
        Example:
            >>> filtered = patient.filter(date_after=datetime.date(2022, 6, 1))
        """
        # TODO: Implement actual filtering logic
        # For now, return self
        return self
    
    def _infer_age_group(self) -> str:
        """
        Infer appropriate age group from patient's current age.
        
        Returns:
            Age group string (e.g., "0-2", "2-5", "5-10", "10-19")
        """
        if not self.measurements:
            return "0-2"
        
        # In real implementation, calculate from actual patient age
        # For prototype, return default
        return "0-2"


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Fluent Patient API Prototype - Usage Examples")
    print("=" * 80)
    
    # Example 1: Basic method chaining
    print("\n1. Basic Method Chaining")
    print("-" * 80)
    
    patient = (FluentPatient(sex="M", birthday_date=datetime.date(2022, 1, 1))
        .measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
        .measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
        .calculate_all())
    
    print(f"Patient created with {len(patient.measurements)} measurements")
    
    # Example 2: Including plot in chain
    print("\n2. Method Chaining with Plotting")
    print("-" * 80)
    
    patient2 = (FluentPatient(sex="F", birthday_date=datetime.date(2022, 6, 15))
        .measured_at(datetime.date(2022, 12, 15), weight=8.0, stature=67.0)
        .measured_at(datetime.date(2023, 6, 15), weight=9.5, stature=73.0)
        .measured_at(datetime.date(2024, 1, 15), weight=11.0, stature=80.0)
        .calculate_all()
        .plot("weight", age_group="0-2", show=False, output_path="chart.png"))
    
    print(f"Patient created, calculated, and plotted")
    
    # Example 3: Backward compatible - non-chained usage still works
    print("\n3. Backward Compatible Usage (No Chaining)")
    print("-" * 80)
    
    patient3 = FluentPatient(sex="M", birthday_date=datetime.date(2022, 1, 1))
    patient3.measured_at(datetime.date(2022, 7, 1), weight=8.6, stature=68.4)
    patient3.measured_at(datetime.date(2023, 1, 1), weight=10.2, stature=75.7)
    patient3.calculate_all()
    
    print("Non-chained usage works exactly the same!")
    
    # Example 4: Comparison with current API
    print("\n4. Code Reduction Comparison")
    print("-" * 80)
    print("Current API (estimated lines): ~12-15")
    print("Fluent API (lines): ~6-7")
    print("Reduction: ~50-60%")
    
    print("\n" + "=" * 80)
    print("Prototype demonstration complete!")
    print("=" * 80)
