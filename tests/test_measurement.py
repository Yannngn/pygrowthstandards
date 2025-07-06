import datetime

from src.calculator.measurement import Measurement


class TestMeasurement:
    """Test suite for the Measurement class."""

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        date = datetime.date(2023, 1, 1)
        measurement = Measurement(stature=150.5, weight=50.0, head_circumference=35.2, date=date)

        assert measurement.stature == 150.5
        assert measurement.weight == 50.0
        assert measurement.head_circumference == 35.2
        assert measurement.date == date

    def test_init_with_default_date(self):
        """Test initialization with default date (today)."""
        measurement = Measurement(stature=150.5, weight=50.0)

        assert measurement.date == datetime.date.today()

    def test_init_with_none_values(self):
        """Test initialization with None values."""
        measurement = Measurement()

        assert measurement.stature is None
        assert measurement.weight is None
        assert measurement.head_circumference is None
        assert measurement.date == datetime.date.today()

    def test_body_mass_index_calculation(self):
        """Test BMI calculation."""
        measurement = Measurement(stature=170.0, weight=70.0)

        # BMI = 100^2 * weight / (stature^2)
        # BMI = 10000 * 70 / (170^2) = 700000 / 28900 ≈ 24.22
        expected_bmi = 100**2 * 70 / (170**2)
        assert measurement.body_mass_index is not None
        assert abs(measurement.body_mass_index - expected_bmi) < 0.01

    def test_body_mass_index_with_missing_stature(self):
        """Test BMI calculation when stature is missing."""
        measurement = Measurement(weight=70.0)

        assert measurement.body_mass_index is None

    def test_body_mass_index_with_missing_weight(self):
        """Test BMI calculation when weight is missing."""
        measurement = Measurement(stature=170.0)

        assert measurement.body_mass_index is None

    def test_body_mass_index_with_both_missing(self):
        """Test BMI calculation when both weight and stature are missing."""
        measurement = Measurement()

        assert measurement.body_mass_index is None

    def test_weight_stature_ratio_calculation(self):
        """Test weight-to-stature ratio calculation."""
        measurement = Measurement(stature=170.0, weight=70.0)

        expected_ratio = 70.0 / 170.0
        assert measurement.weight_stature_ratio is not None
        assert abs(measurement.weight_stature_ratio - expected_ratio) < 0.01

    def test_weight_stature_ratio_with_missing_values(self):
        """Test weight-to-stature ratio when values are missing."""
        measurement1 = Measurement(weight=70.0)
        measurement2 = Measurement(stature=170.0)
        measurement3 = Measurement()

        assert measurement1.weight_stature_ratio is None
        assert measurement2.weight_stature_ratio is None
        assert measurement3.weight_stature_ratio is None

    def test_str_representation(self):
        """Test string representation of the measurement."""
        date = datetime.date(2023, 1, 1)
        measurement = Measurement(stature=170.0, weight=70.0, head_circumference=35.2, date=date)

        expected_str = f"Measurement(stature=170.0, weight=70.0, head_circumference=35.2, body_mass_index={measurement.body_mass_index:.2f}, date=2023-01-01)"
        assert str(measurement) == expected_str

    def test_get_z_scores_empty(self):
        """Test get_z_scores when no z-scores are set."""
        measurement = Measurement()

        assert measurement.get_z_scores() == {}

    def test_get_z_scores_partial(self):
        """Test get_z_scores with some z-scores set."""
        measurement = Measurement()
        measurement.stature_z = 1.5
        measurement.weight_z = -0.5

        scores = measurement.get_z_scores()
        assert scores == {"stature": 1.5, "weight": -0.5}

    def test_get_z_scores_complete(self):
        """Test get_z_scores with all z-scores set."""
        measurement = Measurement()
        measurement.stature_z = 1.5
        measurement.weight_z = -0.5
        measurement.head_circumference_z = 0.8
        measurement.body_mass_index_z = 0.2
        measurement.weight_stature_ratio_z = -1.0

        scores = measurement.get_z_scores()
        expected_scores = {"stature": 1.5, "weight": -0.5, "head_circumference": 0.8, "body_mass_index": 0.2, "weight_stature_ratio": -1.0}
        assert scores == expected_scores

    def test_get_percentiles_empty(self):
        """Test get_percentiles when no z-scores are set."""
        measurement = Measurement()

        assert measurement.get_percentiles() == {}

    def test_get_percentiles_with_z_scores(self):
        """Test get_percentiles with z-scores set."""
        measurement = Measurement()
        measurement.stature_z = 0.0  # Should be 50th percentile
        measurement.weight_z = 1.0  # Should be approximately 84th percentile
        measurement.head_circumference_z = -1.0  # Should be approximately 16th percentile

        percentiles = measurement.get_percentiles()

        # Check that percentiles are reasonable
        assert abs(percentiles["stature"] - 0.5) < 0.01  # 50th percentile
        assert abs(percentiles["weight"] - 0.8413) < 0.01  # ~84th percentile
        assert abs(percentiles["head_circumference"] - 0.1587) < 0.01  # ~16th percentile

    def test_z_score_attributes_default_none(self):
        """Test that z-score attributes default to None."""
        measurement = Measurement()

        assert measurement.stature_z is None
        assert measurement.weight_z is None
        assert measurement.head_circumference_z is None
        assert measurement.body_mass_index_z is None
        assert measurement.weight_stature_ratio_z is None

    def test_z_score_attributes_assignment(self):
        """Test assignment of z-score attributes."""
        measurement = Measurement()

        measurement.stature_z = 1.5
        measurement.weight_z = -0.5
        measurement.head_circumference_z = 0.8
        measurement.body_mass_index_z = 0.2
        measurement.weight_stature_ratio_z = -1.0

        assert measurement.stature_z == 1.5
        assert measurement.weight_z == -0.5
        assert measurement.head_circumference_z == 0.8
        assert measurement.body_mass_index_z == 0.2
        assert measurement.weight_stature_ratio_z == -1.0
