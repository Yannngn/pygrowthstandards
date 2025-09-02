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
    """Set up a very preterm patient for testing (more than 64 weeks of life)."""
    patient = Patient(
        sex="F",
        birthday_date=datetime.date(2021, 1, 1),
        gestational_age_weeks=30,  # Very preterm baby (30 weeks gestation)
    )
    measurements = [
        MeasurementGroup(
            date=datetime.date(2022, 7, 1),  # Chronological age: ~78 weeks
            weight=8.6,
            stature=68.4,
            head_circumference=44.5,
        ),
        MeasurementGroup(
            date=datetime.date(2023, 1, 1),  # Chronological age: ~104 weeks
            weight=10.2,
            stature=75.7,
            head_circumference=46.5,
        ),
        MeasurementGroup(
            date=datetime.date(2024, 1, 1),  # Chronological age: ~156 weeks
            weight=12.6,
            stature=87.8,
            head_circumference=48.5,
        ),
    ]
    for mg in measurements:
        patient.add_measurements(mg)
    return patient


def test_patient_creation():
    """Test that the Patient object is initialized correctly for very preterm babies."""
    patient = Patient(
        sex="F", birthday_date=datetime.date(2021, 1, 1), gestational_age_weeks=30
    )
    assert patient.sex == "F"
    assert patient.is_born is True
    assert patient.gestational_age_weeks == 30
    assert patient.age(datetime.date(2023, 1, 1)).days == 730  # Age
    assert (
        patient.get_age_with_type("corrected_age", datetime.date(2023, 1, 1)) == 730
    )  # after 64w corrected age falls back to age


def test_add_measurement(setup_patient: Patient):
    """Test adding a single measurement to a new group for very preterm babies."""
    patient = setup_patient
    initial_groups = len(patient.measurements)

    # Add a measurement to an existing date
    patient.add_measurement(
        Measurement(
            measurement_type="weight",
            value=13.0,
            date=datetime.date(2024, 1, 1),
        )
    )
    assert len(patient.measurements) == initial_groups  # No new group should be added

    # Add a measurement to a new date
    patient.add_measurement(
        Measurement(
            measurement_type="stature",
            value=90.0,
            date=datetime.date(2024, 6, 1),
        )
    )
    assert len(patient.measurements) == initial_groups + 1


def test_calculator_z_scores(setup_patient: Patient):
    """Test the z-score calculation process for very preterm babies."""
    patient = setup_patient
    patient.calculate_all()

    assert len(patient.z_scores) == 3
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
    assert "8.60" in output
    assert "75.70" in output
