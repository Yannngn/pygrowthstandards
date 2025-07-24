import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from src.functional import calculator, data


class TestFunctionalCalculator(unittest.TestCase):
    def test_zscore_age(self):
        # Example: stature, male, age_days=365
        result = calculator.zscore("stature", sex="M", age_days=365)
        self.assertIsInstance(result, float)

    def test_zscore_gestational_age(self):
        # Example: weight, female, gestational_age=280
        result = calculator.zscore("weight", sex="F", gestational_age=280)
        self.assertIsInstance(result, float)

    def test_percentile(self):
        # Example: head_circumference, unknown sex, age_days=100
        result = calculator.percentile("head_circumference", sex="U", age_days=100)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)


class TestFunctionalData(unittest.TestCase):
    def test_get_keys_age(self):
        keys = data.get_keys("stature", sex="M", age_days=365)
        self.assertEqual(keys[-1], "age")

    def test_get_keys_gestational_age(self):
        keys = data.get_keys("weight", sex="F", gestational_age=280)
        self.assertEqual(keys[-1], "gestational_age")

    def test_normalized_measurement_alias(self):
        keys = data.get_keys("wfa", sex="M", age_days=365)  # type: ignore
        self.assertEqual(keys[1], "weight")


if __name__ == "__main__":
    unittest.main()
