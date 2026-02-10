"""Patient models and operations for the object-oriented API."""

import datetime
from dataclasses import dataclass, field
from typing import Self

from matplotlib.axes import Axes

from pygrowthstandards.oop.calculator import Calculator
from pygrowthstandards.oop.measurement import Measurement, MeasurementGroup
from pygrowthstandards.config.growth import AgeGroupType, DataSexType, MeasurementAliasType, TableNameType
from pygrowthstandards.utils.date import DateInputType, handle_date_input
from pygrowthstandards.utils.results import str_dataframe


@dataclass
class PatientBase:
    """Base patient attributes and age calculations.

    Attributes:
        sex: Sex identifier.
        birthday_date: Birth date or None for unborn patients.
        gestational_age_weeks: Gestational age in weeks.
        gestational_age_days: Additional gestational days.
        gestational_age: Computed gestational age timedelta.
        is_born: True when birthday_date is set.
        is_very_preterm: True when gestational age < 32 weeks.
    """
    sex: DataSexType
    birthday_date: DateInputType | None
    gestational_age_weeks: int = 40
    gestational_age_days: int = 0

    gestational_age: datetime.timedelta = field(init=False)
    is_born: bool = field(init=False)
    is_very_preterm: bool = field(init=False)

    def __post_init__(self):
        """Initialize derived attributes and the calculator."""
        self._setup()
        self.calculator = Calculator()

    def age(self, date: DateInputType | None = None) -> datetime.timedelta:
        """Return chronological age at the given date.

        Args:
            date: Date to compute age against. Defaults to now.

        Returns:
            Age as a timedelta.
        """
        assert self.birthday_date is not None, "Patient must be born to calculate age."
        if date is not None:
            dt = handle_date_input(date)
        else:
            dt = datetime.datetime.now()

        assert dt >= self._birthday_date, "Date must be after the birthday date."

        return dt - self._birthday_date

    def post_menstrual_age(self, date: DateInputType | None = None) -> datetime.timedelta:
        """Return post-menstrual age (chronological + gestational).

        Args:
            date: Date to compute age against. Defaults to now.

        Returns:
            Post-menstrual age as a timedelta.
        """
        return self.age(date) + self.gestational_age

    def get_age(self, age_type: str = "age", date: DateInputType | None = None) -> int:
        """Return age in days for the requested age_type.

        Args:
            age_type: One of "age", "gestational_age", or "post_menstrual_age".
            date: Date to compute age against.

        Returns:
            Age in days.

        Raises:
            ValueError: If the age_type is invalid.
        """
        if age_type in ["age", "chronological_age"]:
            return self.age(date).days

        if age_type == "gestational_age":
            return self.gestational_age.days

        if age_type == "post_menstrual_age":
            return self.post_menstrual_age(date).days

        raise ValueError(f"Invalid age type: {age_type}. Use 'age', 'gestational_age', or 'post_menstrual_age'.")

    def _setup(self):
        """Populate derived fields from initial inputs."""
        self.gestational_age = datetime.timedelta(weeks=self.gestational_age_weeks, days=self.gestational_age_days)

        if self.birthday_date is not None:
            self.is_born = True
            # FIXME: Use private attribute to handle the type checks?
            self._birthday_date = handle_date_input(self.birthday_date)
            self.is_very_preterm = self.gestational_age_weeks < 32
        else:
            self.is_born = False
            self.is_very_preterm = False

    def _chronological_age_days(self, date: datetime.date | None = None) -> int | None:
        """Return chronological age in days if the patient is born.

        Args:
            date: Date to compute age against.

        Returns:
            Age in days, or None if unknown.
        """
        if self.birthday_date is None:
            return None
        return self.age(date).days


@dataclass
class AddMeasurementPatientMixin:
    """Mixin that stores and updates measurement groups."""
    measurements: list[MeasurementGroup] = field(default_factory=list)

    def add_measurement(self, measurement: Measurement) -> Self:
        """Add a single measurement to the appropriate group.

        Args:
            measurement: Measurement to add.

        Returns:
            Self for chaining.
        """
        for group in self.measurements:
            if group.date != measurement.date:
                continue

            setattr(group, measurement.measurement_type, measurement.value)
            group._setup()

            return self

        new_group = MeasurementGroup(
            table_name=measurement.table_name,
            date=measurement.date,
            **{measurement.measurement_type: measurement.value},
        )
        self.measurements.append(new_group)

        return self

    def add_measurements(self, measurements: MeasurementGroup) -> Self:
        """Append a measurement group to the patient.

        Args:
            measurements: MeasurementGroup to add.

        Returns:
            Self for chaining.
        """
        self.measurements.append(measurements)

        return self


@dataclass
class Patient(AddMeasurementPatientMixin, PatientBase):
    """Patient model with measurement tracking and z-score calculations."""
    z_scores: list[MeasurementGroup] = field(default_factory=list, init=False)

    # TODO: Simplify UX by calculating table_name based on birthdate and date of measurement.
    def measured_at(
        self,
        date: DateInputType | None = None,
        table_name: TableNameType = "growth",
        weight: float | None = None,
        stature: float | None = None,
        head_circumference: float | None = None,
    ) -> Self:
        """Record measurements on a specific date.

        Args:
            date: Measurement date. Defaults to now.
            table_name: Reference table name to associate.
            weight: Weight in kg.
            stature: Stature in cm.
            head_circumference: Head circumference in cm.

        Returns:
            Self for chaining.
        """
        if date is not None:
            date = handle_date_input(date)
        else:
            date = datetime.datetime.now()

        for group in self.measurements:
            if group.date != date:
                continue

            if weight is not None:
                group.weight = weight
            if stature is not None:
                group.stature = stature
            if head_circumference is not None:
                group.head_circumference = head_circumference

            group._setup()
            return self

        new_group = MeasurementGroup(
            table_name=table_name,
            date=date,
            weight=weight,
            stature=stature,
            head_circumference=head_circumference,
        )
        self.measurements.append(new_group)

        return self

    def calculate_all(self) -> Self:
        """Calculate z-scores for all measurement groups.

        Returns:
            Self with populated z_scores.
        """
        z_scores: list[MeasurementGroup] = []

        for group in self.measurements:
            age_days = self._chronological_age_days(group.date)
            gestational_age = self.gestational_age.days

            z_scores.append(
                self.calculator.calculate_measurement_group(
                    group,
                    self.sex,
                    age_days=age_days,
                    gestational_age=gestational_age,
                )
            )

        self.z_scores = z_scores

        return self

    def plot(self, age_group: AgeGroupType, measurement_type: MeasurementAliasType, show: bool = True, output_path: str = "") -> Axes:
        """Plot measurement history against reference curves.

        Args:
            age_group: Age group identifier.
            measurement_type: Measurement alias.
            show: Whether to show the plot.
            output_path: Optional output file path.

        Returns:
            Matplotlib Axes object.
        """
        from pygrowthstandards.oop.plotter import Plotter

        plotter = Plotter(self)

        ax = plotter.plot(age_group=age_group, measurement_type=measurement_type, show=show, output_path=output_path)

        return ax

    def display_measurements(self) -> str:
        """Return a formatted table of measurements and z-scores.

        Returns:
            Table string for display.
        """
        if not self.measurements:
            return "No measurements available."

        # Sort groups by date to ensure chronological order
        sorted_measurements = sorted(self.measurements, key=lambda mg: mg.date)
        sorted_z_scores = sorted(self.z_scores, key=lambda mg: mg.date)

        # Create a mapping from date to z-score group for easy lookup
        z_scores_map = {group.date: group for group in sorted_z_scores}

        results_list = []
        date_list = []
        age_list = []

        for m_group in sorted_measurements:
            result_dict = {}
            date = m_group.date
            m_dict = m_group.to_dict()

            date_list.append(date)

            age_days = self._chronological_age_days(date)
            age_list.append(age_days if age_days is not None else self.gestational_age.days)

            z_dict = z_scores_map.get(date, MeasurementGroup(date=date)).to_dict()

            for m_type, m_value in m_dict.items():
                if m_value is None or m_type == "date":
                    continue

                result_dict[m_type] = {"value": m_value}
                z_value = z_dict.get(m_type)

                if z_value is None:
                    continue

                result_dict[m_type]["z"] = z_value

            results_list.append(result_dict)

        return str_dataframe(results=results_list, date_list=date_list, age_list=age_list)
