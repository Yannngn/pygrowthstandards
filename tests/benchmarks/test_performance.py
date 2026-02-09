import pytest

from pygrowthstandards import functional as F
from pygrowthstandards.oop.calculator import Calculator
from pygrowthstandards.oop.measurement import MeasurementGroup

# Benchmark the Functional Calculator for a single measurement

pytestmark = pytest.mark.performance


def test_benchmark_functional_single(benchmark):
    benchmark(F.zscore, "stature", 50.0, "M", age_days=365)


# Benchmark the Functional Calculator for many measurements


def test_benchmark_functional_many(benchmark):
    def run_many_functional():
        for _ in range(100):
            F.zscore("stature", 50.0, "M", age_days=365)

    benchmark(run_many_functional)


# Benchmark the OOP Calculator for a single measurement


def test_benchmark_calculator_single(benchmark):
    """Benchmark Calculator.calculate_z_score for one MeasurementGroup"""
    calc = Calculator()
    mg = MeasurementGroup(stature=75.0, weight=10.0)
    benchmark(calc.calculate_z_score, mg, "stature", "M", age_days=365)


# Benchmark the OOP Calculator for many measurements


def test_benchmark_calculator_many(benchmark):
    """Benchmark Calculator.calculate_measurement_group over many MeasurementGroup instances"""
    calc = Calculator()
    groups = [MeasurementGroup(stature=75.0, weight=10.0) for _ in range(100)]

    def run_many_calculator():
        for mg in groups:
            calc.calculate_measurement_group(mg, "M", age_days=365)

    benchmark(run_many_calculator)
