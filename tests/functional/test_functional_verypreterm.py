import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)
from src.pygrowthstandards.functional import calculator, data


class TestFunctionalCalculator:
    def test_zscore_age_under_64w(self):
        # Example: stature, male, chronological age < 64 weeks (e.g., 420 days)
        result = calculator.zscore(
            "stature", 85, sex="M", age_days=210, gestational_age_days=210
        )
        assert isinstance(result, float)

    def test_percentile_under_64w(self):
        # Example: head_circumference, unknown sex, chronological age < 64 weeks
        result = calculator.percentile(
            "head_circumference", 48, sex="U", age_days=210, gestational_age_days=210
        )
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestFunctionalData:
    def test_get_keys_age_under_64w(self):
        # Example: chronological age < 64 weeks (e.g., 420 days)
        keys = data.get_keys("stature", sex="M", age_days=210, gestational_age_days=210)
        assert keys[-1] == "corrected_age"  # TODO: chronological age

    def test_normalized_measurement_alias_under_64w(self):
        # Example: chronological age < 64 weeks (e.g., 420 days)
        keys = data.get_keys("wfa", sex="M", age_days=210, gestational_age_days=210)  # type: ignore
        print(keys)
        assert keys[2] == "weight"
