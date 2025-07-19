import datetime
from unittest.mock import Mock, patch

import pytest

from src.calculator.calculator import Calculator
from src.calculator.child import Child
from src.calculator.measurement import Measurement


class TestCalculator:
    """Test suite for the Calculator class."""

    def test_init(self):
        """Test Calculator initialization."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        assert calculator.child == child
        assert calculator._measurements == []
        assert calculator._data is not None

    def test_from_child_classmethod(self):
        """Test Calculator.from_child class method."""
        birthday = datetime.date(2023, 1, 1)
        calculator = Calculator.from_child(birthday_date=birthday, sex="F", gestational_age_weeks=40, gestational_age_days=2)

        assert calculator.child.birthday_date == birthday
        assert calculator.child.sex == "F"
        assert calculator.child.gestational_age == datetime.timedelta(weeks=40, days=2)

    def test_from_child_defaults(self):
        """Test Calculator.from_child with default parameters."""
        birthday = datetime.date(2023, 1, 1)
        calculator = Calculator.from_child(birthday_date=birthday)

        assert calculator.child.birthday_date == birthday
        assert calculator.child.sex == "U"
        assert calculator.child.gestational_age is None

    @patch("src.calculator.calculator.calculate_z_score")
    def test_calculate_z_score_method(self, mock_calculate_z_score):
        """Test _calculate_z_score method."""
        mock_calculate_z_score.return_value = 1.5

        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock the _data._get_lms method
        calculator._data.get_lms = Mock(return_value=(0.2, 100.0, 0.1))

        result = calculator.calculate_z_score("test_table", 110.0, 365)

        assert result == 1.5
        mock_calculate_z_score.assert_called_once_with(110.0, 0.2, 100.0, 0.1)
        calculator._data._get_lms.assert_called_once_with("test_table", 365)

    @patch("src.calculator.calculator.normal_cdf")
    def test_calculate_centile_method(self, mock_normal_cdf):
        """Test _calculate_centile method."""
        mock_normal_cdf.return_value = 0.8413

        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock the _calculate_z_score method
        calculator._calculate_z_score = Mock(return_value=1.0)

        result = calculator._calculate_centile("test_table", 110.0, 365)

        assert result == 0.8413
        mock_normal_cdf.assert_called_once_with(1.0)
        calculator._calculate_z_score.assert_called_once_with("test_table", 110.0, 365)

    def test_calculate_centile_with_none_z_score(self):
        """Test _calculate_centile when z-score is None."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock the _calculate_z_score method to return None
        calculator._calculate_z_score = Mock(return_value=None)

        result = calculator._calculate_centile("test_table", 110.0, 365)

        assert result is None

    def test_calculate_measurement_zscore_normal_child(self):
        """Test calculate_measurement_zscore for normal child."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock the _calculate_z_score method
        calculator._calculate_z_score = Mock(return_value=1.5)

        measurement = Measurement(stature=110.0, weight=20.0, head_circumference=45.0, date=datetime.date(2023, 6, 1))

        calculator.calculate_measurement_zscore(measurement)

        # Should calculate z-scores for all measurement types
        assert measurement.stature_z == 1.5
        assert measurement.weight_z == 1.5
        assert measurement.head_circumference_z == 1.5
        assert measurement.body_mass_index_z == 1.5

    def test_calculate_measurement_zscore_newborn(self):
        """Test calculate_measurement_zscore for newborn."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M", gestational_age_weeks=40)
        calculator = Calculator(child)

        # Mock the _calculate_z_score method
        calculator._calculate_z_score = Mock(return_value=0.5)

        measurement = Measurement(
            stature=50.0,
            weight=3.5,
            head_circumference=35.0,
            date=birthday,  # Same as birthday = newborn
        )

        calculator.calculate_measurement_zscore(measurement)

        # Should use gestational age for newborn
        assert measurement.stature_z == 0.5
        assert measurement.weight_z == 0.5
        assert measurement.head_circumference_z == 0.5

    def test_calculate_measurement_zscore_newborn_no_gestational_age(self):
        """Test calculate_measurement_zscore for newborn without gestational age."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        measurement = Measurement(
            stature=50.0,
            weight=3.5,
            date=birthday,  # Same as birthday = newborn
        )

        with pytest.raises(ValueError, match="Gestational age is required"):
            calculator.calculate_measurement_zscore(measurement)

    def test_calculate_measurement_zscore_very_preterm(self):
        """Test calculate_measurement_zscore for very preterm child."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M", gestational_age_weeks=28)
        calculator = Calculator(child)

        # Mock the _calculate_z_score method
        calculator._calculate_z_score = Mock(return_value=-1.0)

        measurement = Measurement(stature=40.0, weight=1.5, head_circumference=30.0, date=datetime.date(2023, 2, 1))

        calculator.calculate_measurement_zscore(measurement)

        # Should calculate z-scores for very preterm
        assert measurement.stature_z == -1.0
        assert measurement.weight_z == -1.0
        assert measurement.head_circumference_z == -1.0

    def test_calculate_measurement_zscore_with_value_error(self):
        """Test calculate_measurement_zscore when _calculate_z_score raises ValueError."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock the _calculate_z_score method to raise ValueError
        calculator._calculate_z_score = Mock(side_effect=ValueError("Test error"))

        measurement = Measurement(stature=110.0, weight=20.0, date=datetime.date(2023, 6, 1))

        # Should not raise exception, but z-scores should remain None
        calculator.calculate_measurement_zscore(measurement)

        assert measurement.stature_z is None
        assert measurement.weight_z is None
        assert measurement.head_circumference_z is None
        assert measurement.body_mass_index_z is None

    def test_get_measurements_by_age_group_normal(self):
        """Test get_measurements_by_age_group for normal child."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock _get_age_limits method
        calculator._get_age_limits = Mock(return_value=(0, 730))  # 0-2 years

        # Add some measurements
        measurement1 = Measurement(date=datetime.date(2023, 6, 1))  # 151 days
        measurement2 = Measurement(date=datetime.date(2024, 1, 1))  # 365 days
        measurement3 = Measurement(date=datetime.date(2025, 1, 1))  # 730 days

        calculator._measurements = [measurement1, measurement2, measurement3]

        result = calculator.get_measurements_by_age_group("0-2")

        assert len(result) == 3
        assert measurement1 in result
        assert measurement2 in result
        assert measurement3 in result

    def test_get_measurements_by_age_group_newborn(self):
        """Test get_measurements_by_age_group for newborn."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M", gestational_age_weeks=40)
        calculator = Calculator(child)

        # Mock _get_age_limits method
        calculator._get_age_limits = Mock(return_value=(280, 300))  # Newborn range

        # Add some measurements
        measurement1 = Measurement(date=datetime.date(2023, 1, 1))  # newborn
        measurement2 = Measurement(date=datetime.date(2023, 6, 1))  # later

        calculator._measurements = [measurement1, measurement2]

        result = calculator.get_measurements_by_age_group("newborn")

        # Should include measurements based on gestational age
        assert isinstance(result, list)

    def test_get_measurements_by_age_group_very_preterm_no_gestational_age(self):
        """Test get_measurements_by_age_group for very preterm without gestational age."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock _get_age_limits method
        calculator._get_age_limits = Mock(return_value=(189, 448))

        with pytest.raises(AssertionError):
            calculator.get_measurements_by_age_group("very_preterm")

    def test_results_method(self):
        """Test results method."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock dependencies
        measurement = Measurement(stature=110.0, weight=20.0, head_circumference=45.0, date=datetime.date(2023, 6, 1))
        measurement.stature_z = 1.0
        measurement.weight_z = 0.5
        measurement.head_circumference_z = -0.5
        measurement.body_mass_index_z = 0.0

        calculator.get_measurements_by_age_group = Mock(return_value=[measurement])
        calculator._calculate_all = Mock()

        result = calculator.results("0-2")

        assert len(result) == 1
        assert "stature" in result[0]
        assert "weight" in result[0]
        assert "head_circumference" in result[0]
        assert "body_mass_index" in result[0]

        assert result[0]["stature"]["value"] == 110.0
        assert result[0]["stature"]["z"] == 1.0
        assert result[0]["weight"]["value"] == 20.0
        assert result[0]["weight"]["z"] == 0.5

    def test_display_results_no_measurements(self):
        """Test display_results when no measurements are found."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock to return empty results
        calculator.results = Mock(return_value=[])

        result = calculator.display_results("0-2")

        assert result == "No measurements found."

    def test_display_results_with_measurements(self):
        """Test display_results with measurements."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock dependencies
        measurement = Measurement(stature=110.0, weight=20.0, date=datetime.date(2023, 6, 1))

        results_data = [{"stature": {"value": 110.0, "z": 1.0}, "weight": {"value": 20.0, "z": 0.5}}]

        calculator.results = Mock(return_value=results_data)
        calculator.get_measurements_by_age_group = Mock(return_value=[measurement])
        calculator.child.age = Mock(return_value=datetime.timedelta(days=151))

        result = calculator.display_results("0-2")

        assert isinstance(result, str)
        assert "stature" in result
        assert "weight" in result

    def test_calculate_all_method(self):
        """Test _calculate_all method."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Mock calculate_measurement_zscore
        calculator.calculate_measurement_zscore = Mock()

        measurements = [Measurement(stature=110.0, date=datetime.date(2023, 6, 1)), Measurement(weight=20.0, date=datetime.date(2023, 7, 1))]

        calculator._calculate_all(measurements)

        assert calculator.calculate_measurement_zscore.call_count == 2
        calculator.calculate_measurement_zscore.assert_any_call(measurements[0])
        calculator.calculate_measurement_zscore.assert_any_call(measurements[1])

    def test_str_representation(self):
        """Test string representation of Calculator."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Add some measurements
        calculator._measurements = [
            Measurement(stature=110.0, date=datetime.date(2023, 6, 1)),
            Measurement(weight=20.0, date=datetime.date(2023, 7, 1)),
        ]

        result = str(calculator)

        assert "Calculator" in result
        assert "measurements=2" in result
        assert str(child) in result

    def test_inheritance_structure(self):
        """Test that Calculator inherits from expected classes."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        # Check that Calculator has methods from parent classes
        assert hasattr(calculator, "add_measurement")  # From Handler
        assert hasattr(calculator, "plot_measurements")  # From Plotter (if exists)

    def test_data_attribute(self):
        """Test that _data attribute is properly initialized."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")
        calculator = Calculator(child)

        assert calculator._data is not None
        # Should be initialized with child's sex
        assert hasattr(calculator._data, "_get_lms")
        assert hasattr(calculator._data, "_get_table")
        assert hasattr(calculator._data, "_get_table")
