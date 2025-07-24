import datetime

import pytest

from src.functional.calculator import percentile, zscore
from src.patient.patient import Patient


@pytest.mark.parametrize(
    "measurement,sex,age_days,gestational_age",
    [
        ("weight", "M", 100, None),
        ("stature", "F", 200, None),
        ("head_circumference", "U", None, 38 * 7),
    ],
)
def test_zscore_valid_inputs(measurement, sex, age_days, gestational_age):
    result = zscore(measurement, sex, age_days, gestational_age)
    assert isinstance(result, float)


def test_zscore_requires_age_or_gestational_age():
    with pytest.raises(ValueError):
        zscore("weight", "M", None, None)


@pytest.mark.parametrize(
    "measurement,sex,age_days,gestational_age",
    [
        ("weight", "M", 100, None),
        ("stature", "F", 200, None),
        ("head_circumference", "U", None, 38 * 7),
    ],
)
def test_percentile_valid_inputs(measurement, sex, age_days, gestational_age):
    result = percentile(measurement, sex, age_days, gestational_age)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# Example for src/patient dir code (assuming a Patient class exists)
# You may need to adjust imports and parameters based on actual implementation


def test_patient_creation():
    patient = Patient(sex="M", birthday_date=datetime.date(2012, 6, 1))
    assert patient.sex == "M"
    assert patient.age(datetime.date(2024, 6, 1)).days == 4383
