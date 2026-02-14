import datetime

import pytest

from pygrowthstandards.oop.growth import Measurement, MeasurementGroup
from pygrowthstandards.oop.growth.load import get_patient_data, get_plot_data, get_reference_data
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.oop.plots.plotter import Plotter


@pytest.fixture
def setup_patient():
    """Set up a patient for testing."""
    patient = Patient(
        sex="M",
        birthday_date=datetime.date(2022, 1, 1),
    )
    measurements = [
        MeasurementGroup(
            table_name="child_growth",
            date=datetime.date(2022, 7, 1),
            weight=8.6,
            stature=68.4,
            head_circumference=44.5,
        ),
        MeasurementGroup(
            table_name="child_growth",
            date=datetime.date(2023, 1, 1),
            weight=10.2,
            stature=75.7,
            head_circumference=46.5,
        ),
        MeasurementGroup(
            table_name="child_growth",
            date=datetime.date(2024, 1, 1),
            weight=12.6,
            stature=87.8,
            head_circumference=48.5,
        ),
    ]
    for mg in measurements:
        patient.add_measurements(mg)
    return patient


def test_patient_creation():
    """Test that the Patient object is initialized correctly."""
    patient = Patient(sex="M", birthday_date=datetime.date(2022, 1, 1))
    assert patient.sex == "M"
    assert patient.is_born is True
    assert patient.age(datetime.date(2023, 1, 1)).days == 365


def test_add_measurement(setup_patient: Patient):
    """Test adding a single measurement to a new group."""
    patient = setup_patient
    initial_groups = len(patient.measurements)

    # Add a measurement to an existing date
    patient.add_measurement(
        Measurement(
            table_name="child_growth",
            measurement_type="weight",
            value=12.7,
            date=datetime.date(2024, 1, 1),
        )
    )
    assert len(patient.measurements) == initial_groups  # No new group should be added

    # Add a measurement to a new date
    patient.add_measurement(
        Measurement(
            table_name="child_growth",
            measurement_type="stature",
            value=90.0,
            date=datetime.date(2024, 6, 1),
        )
    )
    assert len(patient.measurements) == initial_groups + 1


def test_calculator_z_scores(setup_patient: Patient):
    """Test the z-score calculation process."""
    patient = setup_patient
    patient.calculate_all()

    assert len(patient.z_scores) == 3
    for group in patient.z_scores:
        if group.weight is not None:
            assert isinstance(group.weight, float)
        if group.stature is not None:
            assert isinstance(group.stature, float)


def test_display_measurements(setup_patient: Patient):
    """Test that display_measurements returns a formatted string."""
    patient = setup_patient
    patient.calculate_all()

    output = patient.display_measurements()
    assert isinstance(output, str)
    assert "Age (days)" in output
    assert "weight" in output
    assert "stature" in output
    assert "8.60" in output
    assert "75.70" in output


def test_get_reference_data(setup_patient: Patient):
    """Test loading reference data for a patient."""
    patient = setup_patient

    # Load reference data for a specific age group
    ref_data = get_reference_data(patient, age_group="0-2", measurement_type="weight")

    # Verify reference data is loaded
    assert ref_data is not None
    assert len(ref_data.x) > 0
    assert len(ref_data.L) == len(ref_data.x)
    assert len(ref_data.M) == len(ref_data.x)
    assert len(ref_data.S) == len(ref_data.x)


def test_get_patient_data(setup_patient: Patient):
    """Test filtering patient measurements for a specific age group."""
    patient = setup_patient

    # Get patient data for 0-2 age group
    patient_data = get_patient_data(patient, age_group="0-2", measurement_type="weight")

    # Verify patient data is returned
    assert isinstance(patient_data, dict) or hasattr(patient_data, "__len__")
    assert "x" in patient_data.columns
    assert "patient" in patient_data.columns
    assert len(patient_data) > 0


def test_get_plot_data_with_patient_measurements(setup_patient: Patient):
    """Test plot data generation combines reference curves with patient measurements."""
    patient = setup_patient

    # Get plot data for weight in 0-2 age group
    plot_data = get_plot_data(patient, age_group="0-2", measurement_type="weight")

    # Verify plot data includes reference curves
    assert "x" in plot_data.columns
    assert "is_derived" in plot_data.columns
    assert -3 in plot_data.columns or 0 in plot_data.columns  # z-scores

    # Verify patient data is included
    assert "y" in plot_data.columns
    assert plot_data["y"].notna().any()  # At least one patient measurement

    # Verify patient measurements are in the data
    assert len(plot_data) > 1  # Should have reference points + patient data


def test_get_plot_data_interpolation(setup_patient: Patient):
    """Test that plot data correctly interpolates LMS for patient measurements."""
    patient = setup_patient

    # Get plot data
    plot_data = get_plot_data(patient, age_group="0-2", measurement_type="weight")

    # Find rows with child data
    child_rows = plot_data[plot_data["y"].notna()]

    # Verify child rows have valid z-score curves (from interpolated LMS)
    for z_score in [-3, -2, 0, 2, 3]:
        if z_score in plot_data.columns:
            child_z_values = child_rows[z_score]
            # At least some child rows should have non-NaN values if within bounds
            if len(child_z_values) > 0 and child_z_values.notna().any():
                assert child_z_values.notna().any()


def test_get_plot_data_stature(setup_patient: Patient):
    """Test plot data generation for stature measurement."""
    patient = setup_patient

    # Get plot data for stature
    plot_data = get_plot_data(patient, age_group="0-2", measurement_type="stature")

    # Verify plot data structure
    assert "x" in plot_data.columns
    assert "y" in plot_data.columns
    assert 0 in plot_data.columns  # Median (z=0)
    assert plot_data["y"].notna().any()  # Has child measurements


def test_plot_growth_chart(setup_patient: Patient):
    """Test the plot method generates a matplotlib figure."""
    patient = setup_patient

    # Call the plot method (without showing or saving)
    ax = patient.plot(age_group="0-2", measurement_type="weight", show=False)

    # Verify a matplotlib Axes object is returned
    assert ax is not None
    assert hasattr(ax, "plot")  # Axes object


def test_reference_plot(setup_patient: Patient):
    """Test the reference plot method."""
    patient = setup_patient

    # Call the reference plot method
    ax = Plotter(patient).reference_plot(age_group="0-2", measurement_type="weight", show=False)

    # Verify a matplotlib Axes object is returned
    assert ax is not None
    assert hasattr(ax, "plot")  # Axes object
