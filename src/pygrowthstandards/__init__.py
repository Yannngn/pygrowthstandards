"""
PyGrowthStandards: A Python library for calculating child growth z-scores and percentiles.

This library provides tools for calculating z-scores and percentiles for common
anthropometric measurements using WHO and INTERGROWTH-21st growth standards.

The package includes pre-processed reference data from WHO and INTERGROWTH-21st
standards, so no additional data files need to be downloaded.

Example usage:
    >>> import pygrowthstandards as pgs
    >>> # Functional API
    >>> z_score = pgs.functional.zscore("weight", 10.5, "M", age_days=365)
    >>> percentile = pgs.functional.percentile("stature", 75, "F", age_days=365)
    >>>
    >>> # Object-oriented API
    >>> patient = pgs.Patient(sex="M", birthday_date="2020-01-01")
    >>> patient.add_measurements(pgs.MeasurementGroup(weight=10.5, stature=75))
    >>> patient.calculate_all()
"""

__version__ = "0.1.0a1"
__author__ = "Yannngn"
__email__ = "contato.yannnob@gmail.com"
__license__ = "MIT"

from . import functional, utils
from .data import data_exists, get_data_path
from .oop import Calculator, Measurement, MeasurementGroup, Patient, Plotter


def check_data():
    """Check if reference data is available and print status information."""
    if data_exists():
        print(f"✓ Reference data is available at: {get_data_path()}")
        from .data.load import load_reference

        try:
            data = load_reference()
            print(f"✓ Data loaded successfully: {data.shape[0]:,} records")
            sources = data["source"].unique()
            print(f"✓ Available data sources: {', '.join(sources)}")
        except Exception as e:
            print(f"✗ Error loading data: {e}")
    else:
        print(f"✗ Reference data not found at: {get_data_path()}")
        print("Please ensure the package was installed correctly.")


__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Modules
    "functional",
    "utils",
    # Classes
    "Calculator",
    "Measurement",
    "MeasurementGroup",
    "Patient",
    "Plotter",
    # Utility functions
    "check_data",
]
