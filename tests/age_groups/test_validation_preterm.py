import pytest

from pygrowthstandards.functional import zscore
from pygrowthstandards.oop.calculator import Calculator
from pygrowthstandards.config.growth import MeasurementAliasType
from pygrowthstandards.utils.constants import WEEK
from pygrowthstandards.utils.stats import calculate_z_score
from tests.validation_utils import (
    get_measurements,
    get_reference_row,
    make_measurement_group,
)

MEASUREMENTS = get_measurements(
    age_group="postnatal_growth_preterm",
    name="postnatal_growth_preterm",
    sex="F",
    x_var_type="post_menstrual_age",
    desired=["weight", "stature", "head_circumference"],
)

if not MEASUREMENTS:
    pytest.skip("No preterm measurements available for validation.", allow_module_level=True)


@pytest.mark.parametrize("measurement_type", MEASUREMENTS)
def test_preterm_postnatal_matches_parquet(measurement_type: MeasurementAliasType):
    gestational_age = 27 * WEEK
    row = get_reference_row(
        age_group="postnatal_growth_preterm",
        name="postnatal_growth_preterm",
        measurement_type=measurement_type,
        sex="F",
        x_var_type="post_menstrual_age",
        min_x=gestational_age + 1,
        max_x=64 * WEEK,
    )
    x_value = float(row["x"])
    age_days = int(round(x_value - gestational_age))
    if age_days <= 0:
        raise AssertionError("Derived age_days must be positive for postnatal preterm validation.")

    value = float(row["m"]) * 1.05
    expected = calculate_z_score(value, row["l"], row["m"], row["s"])

    func = zscore(
        measurement_type,
        value,
        sex="F",
        age_days=age_days,
        gestational_age=gestational_age,
    )
    calc = Calculator()
    oop = calc.calculate_z_score(
        make_measurement_group(measurement_type, value),
        measurement_type,
        "F",
        age_days=age_days,
        gestational_age=gestational_age,
    )

    assert func == pytest.approx(expected, rel=1e-6, abs=1e-8)
    assert oop == pytest.approx(expected, rel=1e-6, abs=1e-8)
    assert oop == pytest.approx(func, rel=1e-8, abs=1e-10)
