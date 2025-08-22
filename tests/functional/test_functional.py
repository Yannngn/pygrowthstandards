import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.pygrowthstandards.functional import calculator, data


class TestFunctionalCalculator:
    def test_zscore_age(self):
        # Example: stature, male, age_days=365
        result = calculator.zscore("stature", 78, sex="M", age_days=365)
        assert isinstance(result, float)

    def test_zscore_gestational_age(self):
        # Example: weight, female, gestational_age=280
        result = calculator.zscore("weight", 3.5, sex="F", gestational_age=280)
        assert isinstance(result, float)

    def test_percentile(self):
        # Example: head_circumference, unknown sex, age_days=100
        result = calculator.percentile("head_circumference", 42, sex="U", age_days=100)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestFunctionalData:
    def test_get_keys_age(self):
        keys = data.get_keys("stature", sex="M", age_days=365)
        assert keys[-1] == "age"

    def test_get_keys_gestational_age(self):
        keys = data.get_keys("weight", sex="F", gestational_age=280)
        assert keys[-1] == "gestational_age"

    def test_normalized_measurement_alias(self):
        keys = data.get_keys("wfa", sex="M", age_days=365)  # type: ignore
        assert keys[1] == "weight"
