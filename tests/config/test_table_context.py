import pytest

from pygrowthstandards.config.growth import resolve_table_context


def test_resolve_table_context_prefers_wider_age_group():
    table_name, x_var_type, x_value, age_group = resolve_table_context("weight", age_days=0)

    assert table_name == "child_growth"
    assert x_var_type == "age"
    assert x_value == pytest.approx(0.0)
    assert age_group == "0-2"
