import pytest

from pygrowthstandards.functional import zscore
from pygrowthstandards.oop.calculator import Calculator
from pygrowthstandards.config.growth import MeasurementAliasType
from pygrowthstandards.utils.stats import calculate_z_score
from tests.validation_utils import (
    as_int_x,
    get_measurements,
    get_reference_row,
    make_measurement_group,
)

MEASUREMENTS = get_measurements(
    age_group="5-10",
    name="growth",
    sex="F",
    x_var_type="age",
    desired=["weight", "stature", "head_circumference"],
)

if not MEASUREMENTS:
    pytest.skip("No growth measurements available for validation.", allow_module_level=True)


def _build_growth_inputs(measurement_type: MeasurementAliasType):
    row = get_reference_row(
        age_group="5-10",
        name="growth",
        measurement_type=measurement_type,
        sex="F",
        x_var_type="age",
    )
    age_days = as_int_x(row["x"])
    value = float(row["m"]) * 1.05
    expected = calculate_z_score(value, row["l"], row["m"], row["s"])

    func = zscore(measurement_type, value, sex="F", age_days=age_days)
    calc = Calculator()
    oop = calc.calculate_z_score(
        make_measurement_group(measurement_type, value),
        measurement_type,
        "F",
        age_days=age_days,
    )

    return measurement_type, age_days, value, expected, func, oop


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_growth_functional_matches_parquet(measurement_type: MeasurementAliasType):
    _, age_days, value, expected, func, _ = _build_growth_inputs(measurement_type)
    assert func == pytest.approx(expected, rel=1e-6, abs=1e-8)


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_growth_oop_matches_parquet(measurement_type: MeasurementAliasType):
    _, age_days, value, expected, _, oop = _build_growth_inputs(measurement_type)
    assert oop == pytest.approx(expected, rel=1e-6, abs=1e-8)


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_growth_oop_matches_functional(measurement_type: MeasurementAliasType):
    _, age_days, value, _, func, oop = _build_growth_inputs(measurement_type)
    assert oop == pytest.approx(func, rel=1e-8, abs=1e-10)
