import numpy as np
import pandas as pd
import pytest

from src.data.load import GrowthTable


def make_dummy_df():
    # Create a DataFrame with two rows for the same table
    return pd.DataFrame(
        [
            {
                "source": "who",
                "name": "child_growth",
                "age_group": "child_growth",
                "measurement_type": "stature",
                "sex": "M",
                "x_var_type": "age",
                "x_var_unit": "day",
                "x": 0,
                "l": 1.0,
                "m": 2.0,
                "s": 0.1,
                "is_derived": False,
            },
            {
                "source": "who",
                "name": "child_growth",
                "age_group": "child_growth",
                "measurement_type": "stature",
                "sex": "M",
                "x_var_type": "age",
                "x_var_unit": "day",
                "x": 1,
                "l": 1.5,
                "m": 2.5,
                "s": 0.2,
                "is_derived": True,
            },
        ]
    )


def test_from_data_success():
    df = make_dummy_df()
    gt = GrowthTable.from_data(
        data=df,
        name="child_growth",
        age_group=None,
        measurement_type="stature",
        sex="M",
        x_var_type="age",
    )
    assert isinstance(gt, GrowthTable)
    # x values preserved and sorted
    assert np.array_equal(gt.x, np.array([0, 1]))
    # attributes match
    assert gt.source == "who"
    assert gt.name == "child_growth"
    assert gt.sex == "M"


def test_from_data_missing_filters():
    df = make_dummy_df()
    # Both name and age_group None should error
    with pytest.raises(ValueError):
        GrowthTable.from_data(data=df, name=None, age_group=None, measurement_type="stature", sex="M", x_var_type="age")


def test_from_data_multiple_sources():
    df = make_dummy_df()
    # Second row has different source
    df.loc[1, "source"] = "intergrowth"
    with pytest.raises(ValueError):
        GrowthTable.from_data(
            data=df,
            name="child_growth",
            age_group=None,
            measurement_type="stature",
            sex="M",
            x_var_type="age",
        )


def test_convert_z_scores_to_values():
    df = make_dummy_df()
    gt = GrowthTable.from_data(
        data=df,
        name="child_growth",
        age_group=None,
        measurement_type="stature",
        sex="M",
        x_var_type="age",
    )
    result_df = gt.convert_z_scores_to_values(z_scores=[-2, 0, 2])
    # Should have columns x, is_derived, -2, 0, 2
    for col in ["x", "is_derived", -2, 0, 2]:
        assert col in result_df.columns
    # y absent when not set
    assert "y" not in result_df.columns


def test_add_child_data_and_merge():
    df = make_dummy_df()
    gt = GrowthTable.from_data(
        data=df,
        name="child_growth",
        age_group=None,
        measurement_type="stature",
        sex="M",
        x_var_type="age",
    )
    # Prepare child data
    child_df = pd.DataFrame({"x": [2], "child": [50.0]})
    gt.add_child_data(child_df)
    # merge should include new x
    assert 2 in gt.x.tolist()
    # y attribute set
    assert hasattr(gt, "y")
