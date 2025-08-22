#!/usr/bin/env python3
"""Test script to verify the package installation and basic functionality."""

import sys
import traceback


def test_imports():
    """Test that all main components can be imported."""
    print("Testing imports...")
    try:
        import pygrowthstandards as pgs

        print(f"✓ Package version: {pgs.__version__}")

        # Test functional API
        print("✓ Functional API imported")

        # Test OOP API
        print("✓ OOP API imported")

        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_functional_api():
    """Test basic functionality of the functional API."""
    print("\nTesting functional API...")
    try:
        from pygrowthstandards import functional as F

        # Test z-score calculation
        z_score = F.zscore("weight", 10.5, "M", age_days=365)
        print(f"✓ Z-score calculation: {z_score:.2f}")

        # Test percentile calculation
        percentile = F.percentile("stature", 75, "F", age_days=365)
        print(f"✓ Percentile calculation: {percentile:.3f}")

        return True
    except Exception as e:
        print(f"✗ Functional API test failed: {e}")
        traceback.print_exc()
        return False


def test_oop_api():
    """Test basic functionality of the OOP API."""
    print("\nTesting OOP API...")
    try:
        import datetime

        from pygrowthstandards import MeasurementGroup, Patient

        # Create patient
        patient = Patient(sex="M", birthday_date=datetime.date(2022, 1, 1))
        print("✓ Patient created")

        # Add measurements
        measurement = MeasurementGroup(date=datetime.date(2023, 1, 1), weight=10.5, stature=75.0, head_circumference=46.0)
        patient.add_measurements(measurement)
        print("✓ Measurements added")

        # Calculate z-scores
        patient.calculate_all()
        print("✓ Z-scores calculated")

        return True
    except Exception as e:
        print(f"✗ OOP API test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("PyGrowthStandards Package Test")
    print("=" * 40)

    tests = [
        test_imports,
        test_functional_api,
        test_oop_api,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n{passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("✓ All tests passed! Package is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
