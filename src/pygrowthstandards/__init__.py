"""
PyGrowthStandards: A Python library for calculating child growth z-scores and percentiles,
and tracking developmental milestones.

This library provides tools for:
- Calculating z-scores and percentiles for common anthropometric measurements using WHO
  and INTERGROWTH-21st growth standards
- Tracking and assessing developmental milestones using CDC and Brazilian Ministry of
  Health standards

The package includes pre-processed reference data from WHO, INTERGROWTH-21st, CDC, and
Brazilian standards, so no additional data files need to be downloaded.

Example usage (growth):
    >>> import pygrowthstandards as pgs
    >>> # Functional API
    >>> z_score = pgs.functional.zscore("weight", 10.5, "M", age_days=365)
    >>> percentile = pgs.functional.percentile("stature", 75, "F", age_days=365)
    >>>
    >>> # Object-oriented API
    >>> patient = pgs.Patient(sex="M", birthday_date="2020-01-01")
    >>> patient.add_measurements(pgs.MeasurementGroup(weight=10.5, stature=75))
    >>> patient.calculate_all()

Example usage (milestones):
    >>> import pygrowthstandards as pgs
    >>> # Functional API
    >>> milestones = pgs.functional.get_milestones_for_age(180, source="brazil")
    >>> expected = pgs.functional.check_milestone_expected("MOTOR-SITS", 210, "brazil")
    >>>
    >>> # Object-oriented API
    >>> tracker = pgs.MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
    >>> tracker.record_achievement("MOTOR-SITS", "achieved", datetime.now(), 180)
    >>> summary = tracker.get_achievement_summary()
"""

from pygrowthstandards.utils.version import get_package_version

__version__ = get_package_version()
__author__ = "Yannngn"
__email__ = "contato.yannnobrega@gmail.com"
__license__ = "MIT"

from pygrowthstandards import functional, utils
from pygrowthstandards.data import data_exists, get_data_path
from pygrowthstandards.oop import (
    Calculator,
    Measurement,
    MeasurementGroup,
    MilestoneTracker,
    Patient,
    Plotter,
)


def check_data():
    """Check that reference data is available and report status.

    Returns:
        None
    """
    if data_exists():
        print(f"✓ Reference data is available at: {get_data_path()}")
        from pygrowthstandards.data.growth.load import load_reference

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
    "MilestoneTracker",
    "Patient",
    "Plotter",
    # Utility functions
    "check_data",
]
