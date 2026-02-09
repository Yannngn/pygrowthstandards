"""
Prototype: Builder Pattern for Patient Construction

This prototype demonstrates the Builder pattern for constructing Patient objects
with a fluent, declarative interface. The builder provides validation at each
step and clear separation between construction and usage.

Key Features:
- Step-by-step construction with validation
- Convenient shorthand methods (male(), female(), preterm())
- Flexible measurement addition
- Clear separation of concerns
"""

import datetime
from typing import Any, Self


class PatientBuilder:
    """
    Builder for constructing Patient objects with a fluent interface.

    This builder provides a declarative way to construct patients with
    validation at each step.

    Example:
        >>> patient = (PatientBuilder()
        ...     .male()
        ...     .born_on("2022-01-01")
        ...     .measured_at("2022-07-01", weight=8.6, stature=68.4)
        ...     .build_and_calculate())
    """

    def __init__(self):
        """Initialize empty builder."""
        self._sex: str | None = None
        self._birthday: datetime.date | None = None
        self._gestational_age_weeks: int = 40
        self._gestational_age_days: int = 0
        self._measurements: list[dict[str, Any]] = []

    def with_sex(self, sex: str) -> Self:
        """
        Set patient sex.

        Args:
            sex: "M", "F", or "U"

        Returns:
            Self for chaining

        Raises:
            ValueError: If sex is not valid

        Example:
            >>> builder.with_sex("M")
        """
        if sex not in ["M", "F", "U"]:
            raise ValueError(f"Invalid sex: {sex}. Must be 'M', 'F', or 'U'")
        self._sex = sex
        return self

    def male(self) -> Self:
        """
        Convenience method to set sex to male.

        Returns:
            Self for chaining

        Example:
            >>> builder.male()
        """
        return self.with_sex("M")

    def female(self) -> Self:
        """
        Convenience method to set sex to female.

        Returns:
            Self for chaining

        Example:
            >>> builder.female()
        """
        return self.with_sex("F")

    def unknown_sex(self) -> Self:
        """
        Convenience method to set sex to unknown.

        Returns:
            Self for chaining

        Example:
            >>> builder.unknown_sex()
        """
        return self.with_sex("U")

    def born_on(self, date: datetime.date | str) -> Self:
        """
        Set birthday.

        Args:
            date: Birthday as date object or ISO string (YYYY-MM-DD)

        Returns:
            Self for chaining

        Example:
            >>> builder.born_on("2022-01-01")
            >>> builder.born_on(datetime.date(2022, 1, 1))
        """
        if isinstance(date, str):
            date = datetime.date.fromisoformat(date)
        self._birthday = date
        return self

    def gestational_age(self, weeks: int, days: int = 0) -> Self:
        """
        Set gestational age.

        Args:
            weeks: Gestational age in weeks (typically 37-42 for full term)
            days: Additional days beyond weeks

        Returns:
            Self for chaining

        Example:
            >>> builder.gestational_age(38, 3)  # 38 weeks, 3 days
        """
        if weeks < 20 or weeks > 45:
            raise ValueError(f"Gestational age {weeks} weeks is outside typical range (20-45)")
        self._gestational_age_weeks = weeks
        self._gestational_age_days = days
        return self

    def full_term(self) -> Self:
        """
        Convenience method for full-term infant (40 weeks).

        Returns:
            Self for chaining

        Example:
            >>> builder.full_term()
        """
        return self.gestational_age(40)

    def preterm(self, weeks: int = 35) -> Self:
        """
        Convenience method for preterm infant.

        Args:
            weeks: Gestational age in weeks (default 35)

        Returns:
            Self for chaining

        Example:
            >>> builder.preterm()  # Default 35 weeks
            >>> builder.preterm(32)  # Very preterm at 32 weeks
        """
        return self.gestational_age(weeks)

    def very_preterm(self, weeks: int = 30) -> Self:
        """
        Convenience method for very preterm infant (<32 weeks).

        Args:
            weeks: Gestational age in weeks (default 30)

        Returns:
            Self for chaining

        Example:
            >>> builder.very_preterm()
        """
        return self.gestational_age(weeks)

    def measured_at(self, date: datetime.date | str, **measurements: float) -> Self:
        """
        Add measurements at a specific date.

        Args:
            date: Measurement date
            **measurements: Measurement values (weight, stature, head_circumference, etc.)

        Returns:
            Self for chaining

        Example:
            >>> builder.measured_at("2022-07-01", weight=8.6, stature=68.4)
            >>> builder.measured_at(
            ...     datetime.date(2023, 1, 1),
            ...     weight=10.2,
            ...     stature=75.7,
            ...     head_circumference=46.5
            ... )
        """
        if isinstance(date, str):
            date = datetime.date.fromisoformat(date)

        self._measurements.append({"date": date, **measurements})
        return self

    def with_measurements(self, measurements: list[dict[str, Any]]) -> Self:
        """
        Add multiple measurements at once.

        Args:
            measurements: List of measurement dictionaries, each with 'date' and values

        Returns:
            Self for chaining

        Example:
            >>> builder.with_measurements([
            ...     {"date": "2022-07-01", "weight": 8.6, "stature": 68.4},
            ...     {"date": "2023-01-01", "weight": 10.2, "stature": 75.7}
            ... ])
        """
        for m in measurements:
            date = m.get("date")
            if date is None:
                raise ValueError("Each measurement must have a 'date' field")

            if isinstance(date, str):
                date = datetime.date.fromisoformat(date)

            measurement_data = {k: v for k, v in m.items() if k != "date"}
            self._measurements.append({"date": date, **measurement_data})
        return self

    def at_birth(self, **measurements: float) -> Self:
        """
        Convenience method to add measurements at birth (birthday).

        Args:
            **measurements: Measurement values at birth

        Returns:
            Self for chaining

        Example:
            >>> builder.born_on("2022-01-01").at_birth(weight=3.5, stature=50.0)
        """
        if self._birthday is None:
            raise ValueError("Birthday must be set before adding measurements at birth")

        return self.measured_at(self._birthday, **measurements)

    def validate(self) -> None:
        """
        Validate builder state before building.

        Raises:
            ValueError: If validation fails
        """
        if self._sex is None:
            raise ValueError("Sex must be set before building")

        if self._birthday is None and self._measurements:
            raise ValueError("Birthday required when measurements are provided")

        # Validate measurement dates are after birthday
        if self._birthday and self._measurements:
            for m in self._measurements:
                if m["date"] < self._birthday:
                    raise ValueError(f"Measurement date {m['date']} is before birthday {self._birthday}")

    def build(self) -> Any:
        """
        Build and return Patient instance.

        Returns:
            Configured Patient object

        Raises:
            ValueError: If validation fails

        Example:
            >>> patient = builder.build()
        """
        self.validate()

        # In real implementation:
        # from ..oop.patient import Patient
        # from ..oop.measurement import MeasurementGroup
        #
        # patient = Patient(
        #     sex=self._sex,
        #     birthday_date=self._birthday,
        #     gestational_age_weeks=self._gestational_age_weeks,
        #     gestational_age_days=self._gestational_age_days
        # )
        #
        # for m in self._measurements:
        #     date = m.pop("date")
        #     patient.add_measurements(
        #         MeasurementGroup(date=date, **m)
        #     )
        #
        # return patient

        # Mock for prototype
        class MockPatient:
            def __init__(self, sex, birthday, measurements):
                self.sex = sex
                self.birthday = birthday
                self.measurements = measurements

            def calculate_all(self):
                print(f"[MOCK] Calculating z-scores for {len(self.measurements)} measurements")
                return self

        return MockPatient(sex=self._sex, birthday=self._birthday, measurements=self._measurements)

    def build_and_calculate(self) -> Any:
        """
        Build patient and immediately calculate all z-scores.

        Returns:
            Patient with calculated z-scores

        Example:
            >>> patient = builder.build_and_calculate()
        """
        patient = self.build()
        patient.calculate_all()
        return patient

    def reset(self) -> Self:
        """
        Reset builder to initial state.

        Returns:
            Self for chaining

        Example:
            >>> builder.reset()  # Start over
        """
        self._sex = None
        self._birthday = None
        self._gestational_age_weeks = 40
        self._gestational_age_days = 0
        self._measurements = []
        return self


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Patient Builder Pattern Prototype - Usage Examples")
    print("=" * 80)

    # Example 1: Basic builder usage
    print("\n1. Basic Builder Pattern")
    print("-" * 80)

    patient = (
        PatientBuilder()
        .male()
        .born_on("2022-01-01")
        .measured_at("2022-07-01", weight=8.6, stature=68.4)
        .measured_at("2023-01-01", weight=10.2, stature=75.7)
        .build()
    )

    print(f"Built patient: sex={patient.sex}, birthday={patient.birthday}")
    print(f"Measurements: {len(patient.measurements)}")

    # Example 2: Using convenience methods
    print("\n2. Convenience Methods")
    print("-" * 80)

    preterm_patient = (
        PatientBuilder()
        .female()
        .preterm(weeks=35)
        .born_on("2023-01-15")
        .at_birth(weight=2.5, stature=45.0)
        .measured_at("2023-03-15", weight=3.8, stature=50.0)
        .build_and_calculate()
    )

    print("Built preterm patient with birth measurements")

    # Example 3: Bulk measurements
    print("\n3. Bulk Measurement Loading")
    print("-" * 80)

    measurements = [
        {
            "date": "2022-07-01",
            "weight": 8.6,
            "stature": 68.4,
            "head_circumference": 44.5,
        },
        {
            "date": "2023-01-01",
            "weight": 10.2,
            "stature": 75.7,
            "head_circumference": 46.5,
        },
        {
            "date": "2024-01-01",
            "weight": 12.6,
            "stature": 87.8,
            "head_circumference": 48.5,
        },
    ]

    patient_bulk = PatientBuilder().male().born_on("2022-01-01").with_measurements(measurements).build()

    print(f"Loaded {len(patient_bulk.measurements)} measurements in bulk")

    # Example 4: Validation catches errors
    print("\n4. Builder Validation")
    print("-" * 80)

    try:
        invalid_patient = PatientBuilder().build()
    except ValueError as e:
        print(f"✓ Validation caught error: {e}")

    try:
        invalid_gestational = PatientBuilder().male().gestational_age(50)
    except ValueError as e:
        print(f"✓ Validation caught error: {e}")

    # Example 5: Readable, self-documenting code
    print("\n5. Highly Readable Construction")
    print("-" * 80)

    descriptive_patient = (
        PatientBuilder()
        .female()
        .full_term()
        .born_on("2023-06-15")
        .at_birth(weight=3.4, stature=50.0, head_circumference=34.5)
        .measured_at("2023-12-15", weight=7.2, stature=65.0, head_circumference=42.0)
        .measured_at("2024-06-15", weight=9.0, stature=72.0, head_circumference=44.5)
        .build_and_calculate()
    )

    print("Builder pattern creates highly readable, self-documenting code!")

    print("\n" + "=" * 80)
    print("Prototype demonstration complete!")
    print("=" * 80)
