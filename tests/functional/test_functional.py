from pygrowthstandards.functional import percentile, zscore
from pygrowthstandards.functional.growth import data


class TestFunctionalCalculator:
    def test_zscore_age(self):
        # Example: stature, male, age_days=365
        result = zscore("stature", 78, sex="M", age_days=365)
        assert isinstance(result, float)

    def test_zscore_gestational_age(self):
        # Example: weight, female, gestational_age=280
        result = zscore("weight", 3.5, sex="F", gestational_age=280)
        assert isinstance(result, float)

    def test_percentile(self):
        # Example: head_circumference, unknown sex, age_days=100
        result = percentile("head_circumference", 42, sex="U", age_days=100)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestFunctionalData:
    def test_get_keys_age(self):
        keys = data.KeyObject.from_functional("stature", sex="M", age_days=365)
        assert keys.x_var_type == "age"

    def test_get_keys_gestational_age(self):
        keys = data.KeyObject.from_functional("weight", sex="F", gestational_age=280)
        assert keys.x_var_type == "gestational_age"

    def test_normalized_measurement_alias(self):
        keys = data.KeyObject.from_functional("wfa", sex="M", age_days=365)
        assert keys.measurement_type == "weight"
