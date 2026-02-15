import numpy as np
import pandas as pd

from pygrowthstandards.data.growth.load import GrowthTable, KeyObject

KEYS = KeyObject.from_oop(
    name="child_growth",
    measurement_type="stature",
    plot_group="0-2",
    x_var_type="age",
    sex="M",
)


def make_dummy_df():
    # Create a DataFrame with three rows for testing
    return pd.DataFrame(
        [
            {
                "source": "who",
                "name": "child_growth",
                "plot_group": "0-2",
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
                "plot_group": "0-2",
                "measurement_type": "stature",
                "sex": "M",
                "x_var_type": "chronological_age",
                "x_var_unit": "day",
                "x": 1,
                "l": 1.5,
                "m": 2.5,
                "s": 0.2,
                "is_derived": False,
            },
            {
                "source": "who",
                "name": "child_growth",
                "plot_group": "0-2",
                "measurement_type": "stature",
                "sex": "M",
                "x_var_type": "chronological_age",
                "x_var_unit": "day",
                "x": 2,
                "l": 2.0,
                "m": 3.0,
                "s": 0.3,
                "is_derived": False,
            },
        ]
    )


def test_from_data_success():
    df = make_dummy_df()
    gt = GrowthTable.from_data(data=df, keys=KEYS)
    assert isinstance(gt, GrowthTable)
    # x values preserved and sorted
    assert np.array_equal(gt.x, np.array([0, 1, 2])), f"Expected x to be [0, 1, 2], got {gt.x}"
    # attributes match
    assert gt.source == "who"
    assert gt.name == "child_growth"
    assert gt.sex == "M"


def test_convert_z_scores_to_values():
    df = make_dummy_df()
    gt = GrowthTable.from_data(data=df, keys=KEYS)
    result_df = gt.convert_z_scores_to_values(z_scores=[-2, 0, 2])
    # Should have columns x, is_derived, -2, 0, 2
    for col in ["x", "is_derived", -2, 0, 2]:
        assert col in result_df.columns
    # y absent when not set
    assert "y" not in result_df.columns


def test_add_patient_data_and_merge():
    df = make_dummy_df()
    gt = GrowthTable.from_data(data=df, keys=KEYS)
    # Prepare patient data
    patient_df = pd.DataFrame({"x": [3], "patient": [50.0]})
    gt.add_patient_data(patient_df)
    # patient data should be stored separately
    assert 3 in gt._patient_x.tolist()
    assert 50.0 in gt._patient_y.tolist()
    # reference x should not be modified
    assert 3 not in gt.x.tolist()
    # convert_z_scores_to_values should include patient data
    result = gt.convert_z_scores_to_values()
    assert 3 in result["x"].tolist()
    assert 50.0 in result["y"].tolist()
