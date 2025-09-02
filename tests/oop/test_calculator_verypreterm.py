import datetime
import os
import sys

import pytest

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)

from src.pygrowthstandards.oop.measurement import Measurement, MeasurementGroup
from src.pygrowthstandards.oop.patient import Patient


@pytest.fixture
def setup_patient():
    """Set up a very preterm patient for testing."""
    patient = Patient(
        sex="M",
        birthday_date=datetime.date(2023, 1, 1),
        gestational_age_weeks=30,  # Very preterm baby (30 weeks gestation)
    )
    measurements = [
        MeasurementGroup(
            date=datetime.date(2023, 2, 1),  # Chronological age: 31 days
            weight=1.8,  # Example weight in kg
            stature=40.0,  # Example length in cm
            head_circumference=28.0,  # Example HC in cm
        ),
        MeasurementGroup(
            date=datetime.date(2023, 3, 1),  # Chronological age: 59 days
            weight=2.5,
            stature=45.0,
            head_circumference=32.0,
        ),
    ]
    for mg in measurements:
        patient.add_measurements(mg)
    return patient


def test_patient_creation():
    """Test that the Patient object is initialized correctly for very preterm babies."""
    patient = Patient(
        sex="F", birthday_date=datetime.date(2023, 1, 1), gestational_age_weeks=28
    )
    assert patient.sex == "F"
    assert patient.is_born is True
    assert patient.gestational_age_weeks == 28

    assert patient.age(datetime.date(2023, 2, 1)).days == 31  # Age
    assert (
        patient.get_age_with_type("corrected_age", datetime.date(2023, 2, 1))
        == 28 * 7 + 31
    )  # Corrected age


def test_add_measurement(setup_patient: Patient):
    """Test adding a single measurement to a very preterm patient."""
    patient = setup_patient
    initial_groups = len(patient.measurements)

    # Add a measurement to an existing date
    patient.add_measurement(
        Measurement(
            measurement_type="weight",
            value=3.0,
            date=datetime.date(2023, 3, 1),
        )
    )
    assert len(patient.measurements) == initial_groups  # No new group should be added

    # Add a measurement to a new date
    patient.add_measurement(
        Measurement(
            measurement_type="stature",
            value=50.0,
            date=datetime.date(2023, 4, 1),
        )
    )
    assert len(patient.measurements) == initial_groups + 1


def test_calculator_z_scores(setup_patient: Patient):
    """Test the z-score calculation process for very preterm babies."""
    patient = setup_patient
    patient.calculate_all()

    assert len(patient.z_scores) == 2
    for group in patient.z_scores:
        assert isinstance(group, MeasurementGroup)
        if group.weight is not None:
            assert isinstance(group.weight, float)
        if group.stature is not None:
            assert isinstance(group.stature, float)


def test_display_measurements(setup_patient: Patient):
    """Test that display_measurements returns a formatted string for very preterm babies."""
    patient = setup_patient
    patient.calculate_all()

    output = patient.display_measurements()
    assert isinstance(output, str)
    assert "Age (days)" in output
    assert "weight" in output
    assert "stature" in output
    assert "1.80" in output
    assert "40.00" in output
