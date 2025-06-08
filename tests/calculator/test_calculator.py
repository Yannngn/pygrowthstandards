import datetime
from unittest.mock import MagicMock

import pytest

from src.calculator.calculator import Calculator

# TODO: Create actual tests using edge cases


@pytest.fixture
def mock_kid():
    kid = MagicMock()
    kid.age_days.return_value = 1000
    kid.very_preterm = False
    return kid


@pytest.fixture
def calculator(mock_kid):
    calc = Calculator(mock_kid)
    calc._measurements = []
    return calc


def test_init_sets_kid_and_measurements(mock_kid):
    calc = Calculator(mock_kid)
    assert calc.kid is mock_kid
    assert isinstance(calc._measurements, list)


def test_add_and_get_measurements(calculator):
    m1 = MagicMock()
    m2 = MagicMock()
    calculator.add_measurement(m1)
    calculator.add_measurement(m2)
    assert calculator.measurements == [m1, m2]
    # get_measurements returns all if date is None
    assert calculator.get_measurements(None) == [m1, m2]


def test_zscores_and_percentiles(monkeypatch, calculator):
    # Patch get_measurements to return fake measurements
    m = MagicMock()
    m.length_height = 100
    m.weight = 20
    m.head_circumference = 40
    m.bmi = 15
    calculator.measurements = [m]
    monkeypatch.setattr(calculator, "get_measurements", lambda date: [m])
    monkeypatch.setattr(calculator, "_calculate_z_score", lambda *a, **kw: 1.23)
    monkeypatch.setattr(calculator, "_calculate_percentile", lambda *a, **kw: 45.6)
    # Should return a list with one dict containing all keys
    z = calculator.zscores()
    p = calculator.percentiles()
    assert isinstance(z, list) and isinstance(z[0], dict)
    assert isinstance(p, list) and isinstance(p[0], dict)
    assert "height" in z[0] and "height" in p[0]


def test__calculate_z_score_returns_none_for_missing_entry(calculator):
    # Provide empty zscores so entry is None
    calculator.height = []
    result = calculator._calculate_z_score("height", 100, 1000, False)
    assert result is None


def test__calculate_z_score_returns_none_for_bad_lms(calculator):
    calculator.height = [{"age": 1000, "l": None, "m": 0, "s": 0}]
    result = calculator._calculate_z_score("height", 100, 1000, False)
    assert result is None


def test__calculate_z_score_calls_calculate_z_score(calculator, monkeypatch):
    calculator.height = [{"age": 1000, "l": 1, "m": 2, "s": 3}]
    monkeypatch.setattr(calculator, "calculate_z_score", lambda v, l, m, s: 42)
    result = calculator._calculate_z_score("height", 100, 1000, False)
    assert result == 42


def test__interpolate_entry(monkeypatch, calculator):

    zscores = [
        {"age": 100, "l": 1, "m": 2, "s": 3},
        {"age": 200, "l": 2, "m": 3, "s": 4},
        {"age": 300, "l": 3, "m": 4, "s": 5},
        {"age": 400, "l": 4, "m": 5, "s": 6},
    ]
    result = calculator._interpolate_entry(zscores, 250, n_points=2)
    assert isinstance(result, dict)
    assert set(result.keys()) == {"l", "m", "s"}


def test__interpolate_entry_raises_for_out_of_bounds(calculator):
    zscores = [
        {"age": 100, "l": 1, "m": 2, "s": 3},
        {"age": 200, "l": 2, "m": 3, "s": 4},
    ]
    with pytest.raises(ValueError):
        calculator._interpolate_entry(zscores, 50)


def test_get_zscores_returns_empty_list_when_no_measurements(calculator):
    calculator._measurements = []
    result = calculator.get_zscores()
    assert result == []


def test_get_zscores_returns_zscores_for_all_measurements(monkeypatch, calculator):
    m1 = MagicMock()
    m2 = MagicMock()
    calculator._measurements = [m1, m2]
    monkeypatch.setattr(
        calculator,
        "measurement_zscore",
        lambda m: {"height": 1.0} if m is m1 else {"weight": 2.0},
    )
    result = calculator.get_zscores()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"height": 1.0}
    assert result[1] == {"weight": 2.0}


def test_get_zscores_skips_none_entries(monkeypatch, calculator):
    m1 = MagicMock()
    m2 = MagicMock()
    calculator._measurements = [m1, m2]
    monkeypatch.setattr(
        calculator, "measurement_zscore", lambda m: None if m is m1 else {"weight": 2.0}
    )
    result = calculator.get_zscores()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == {"weight": 2.0}


def test_calculate_measurement_zscore_calls__calculate_z_score(monkeypatch, calculator):
    m = MagicMock()
    m.length_height = 100
    m.weight = 20
    m.head_circumference = 40
    m.bmi = 15
    m.date = datetime.date(2020, 1, 1)
    calculator.kid.age_days.return_value = 100
    calculator.kid.gestational_age_weeks = 40
    calculator.kid.gestational_age_days = 0

    called = {}

    def fake_calc(table, value, age):
        called[(table, value, age)] = True
        return 1.0

    monkeypatch.setattr(calculator, "_calculate_z_score", fake_calc)
    calculator.calculate_measurement_zscore(m)
    assert ("length", 100, 100) in called or ("height", 100, 100) in called
    assert ("weight", 20, 100) in called
    assert ("head_circumference", 40, 100) in called
    assert ("bmi", 15, 100) in called


def test_results_returns_expected_structure(monkeypatch, calculator):
    m = MagicMock()
    m.length_height = 100
    m.weight = 20
    m.head_circumference = 40
    m.bmi = 15
    m.get_percentiles.return_value = {
        "length_height": 50,
        "weight": 60,
        "head_circumference": 70,
        "bmi": 80,
    }
    m.length_height_z = 1.1
    m.weight_z = 2.2
    m.head_circumference_z = 3.3
    m.bmi_z = 4.4
    m.date = datetime.date(2020, 1, 1)
    calculator._measurements = [m]
    monkeypatch.setattr(calculator, "get_measurements_by_date_range", lambda s, e: [m])
    monkeypatch.setattr(calculator, "_calculate", lambda ms: None)
    results = calculator.results()
    assert isinstance(results, list)
    assert "length_height" in results[0]
    assert "weight" in results[0]
    assert "head_circumference" in results[0]
    assert "bmi" in results[0]
    assert results[0]["length_height"]["z"] == 1.1
    assert results[0]["weight"]["p"] == 60


def test_display_results_returns_no_measurements(monkeypatch, calculator):
    monkeypatch.setattr(calculator, "results", lambda s=None, e=None: [])
    assert calculator.display_results() == "No measurements found."


def test_display_results_returns_dataframe_string(monkeypatch, calculator):
    m = MagicMock()
    m.length_height = 100
    m.weight = 20
    m.head_circumference = 40
    m.bmi = 15
    m.get_percentiles.return_value = {
        "length_height": 50,
        "weight": 60,
        "head_circumference": 70,
        "bmi": 80,
    }
    m.length_height_z = 1.1
    m.weight_z = 2.2
    m.head_circumference_z = 3.3
    m.bmi_z = 4.4
    m.date = datetime.date(2020, 1, 1)
    calculator._measurements = [m]
    monkeypatch.setattr(calculator, "get_measurements_by_date_range", lambda s, e: [m])
    monkeypatch.setattr(
        calculator,
        "results",
        lambda s=None, e=None: [
            {
                "length_height": {"value": 100, "z": 1.1, "p": 50},
                "weight": {"value": 20, "z": 2.2, "p": 60},
                "head_circumference": {"value": 40, "z": 3.3, "p": 70},
                "bmi": {"value": 15, "z": 4.4, "p": 80},
            }
        ],
    )
    calculator.kid.age_days.return_value = 100
    result = calculator.display_results()
    assert "Idx" in result
    assert "length_height" in result
    assert "weight" in result


def test_from_kid_creates_calculator(monkeypatch):
    birthday = datetime.date(2020, 1, 1)
    calc = Calculator.from_kid(
        birthday, sex="F", gestational_age_weeks=38, gestational_age_days=2
    )
    assert isinstance(calc, Calculator)
    assert calc.kid.birthday_date == birthday
    assert calc.kid.sex == "F"
    assert calc.kid.gestational_age_weeks == 38
    assert calc.kid.gestational_age_days == 2


def test_str_returns_expected(monkeypatch, calculator):
    calculator._measurements = [1, 2, 3]
    calculator.kid = MagicMock()
    calculator.kid.__str__ = lambda s: "KidObject"
    s = str(calculator)
    assert "Calculator(kid=KidObject, measurements=3)" in s
