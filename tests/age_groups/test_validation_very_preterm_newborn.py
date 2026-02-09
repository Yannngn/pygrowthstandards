import pytest

from pygrowthstandards.functional import zscore
from pygrowthstandards.oop.calculator import Calculator
from pygrowthstandards.utils.config import MeasurementAliasType
from pygrowthstandards.utils.stats import calculate_z_score
from tests.validation_utils import (
    as_int_x,
    get_measurements,
    get_reference_row,
    make_measurement_group,
)

MEASUREMENTS = get_measurements(
    age_group="very_preterm_newborn",
    name="very_preterm_newborn",
    sex="M",
    x_var_type="gestational_age",
    desired=["weight", "stature", "head_circumference"],
)

if not MEASUREMENTS:
    pytest.skip("No very preterm newborn measurements available for validation.", allow_module_level=True)


def _build_very_preterm_newborn_inputs(measurement_type: MeasurementAliasType):
    row = get_reference_row(
        age_group="very_preterm_newborn",
        name="very_preterm_newborn",
        measurement_type=measurement_type,
        sex="M",
        x_var_type="gestational_age",
    )
    gestational_age = as_int_x(row["x"])
    value = float(row["m"]) * 1.05
    expected = calculate_z_score(value, row["l"], row["m"], row["s"])

    func = zscore(measurement_type, value, sex="M", gestational_age=gestational_age)
    calc = Calculator()
    oop = calc.calculate_z_score(
        make_measurement_group(measurement_type, value),
        measurement_type,
        "M",
        gestational_age=gestational_age,
    )

    return measurement_type, gestational_age, value, expected, func, oop


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_very_preterm_newborn_functional_matches_parquet(measurement_type: MeasurementAliasType):
    _, gestational_age, value, expected, func, _ = _build_very_preterm_newborn_inputs(measurement_type)
    assert func == pytest.approx(expected, rel=1e-6, abs=1e-8)


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_very_preterm_newborn_oop_matches_parquet(measurement_type: MeasurementAliasType):
    _, gestational_age, value, expected, _, oop = _build_very_preterm_newborn_inputs(measurement_type)
    assert oop == pytest.approx(expected, rel=1e-6, abs=1e-8)


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_very_preterm_newborn_oop_matches_functional(measurement_type: MeasurementAliasType):
    _, gestational_age, value, _, func, oop = _build_very_preterm_newborn_inputs(measurement_type)
    assert oop == pytest.approx(func, rel=1e-8, abs=1e-10)
