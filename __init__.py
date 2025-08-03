"""
PyGrowthStandards - A Python library for pediatric growth standard calculations.
"""

__version__ = "0.1.1"

# Import main classes and functions, handling missing dependencies gracefully
try:
    from .src import functional
    from .src.oop import Calculator, Measurement, MeasurementGroup, Patient, Plotter

    __all__ = ["functional", "Calculator", "Measurement", "MeasurementGroup", "Patient", "Plotter"]
except ImportError as e:
    # If dependencies are missing, provide a helpful error message
    import warnings

    warnings.warn(
        f"PyGrowthStandards dependencies not available: {e}. "
        "Please install required packages: numpy, pandas, matplotlib, scipy. "
        "Run: pip install numpy pandas matplotlib scipy",
        ImportWarning,
    )

    # Define placeholder variables that don't raise errors during import
    functional = None
    Calculator = None
    Measurement = None
    MeasurementGroup = None
    Patient = None
    Plotter = None

    __all__ = ["functional", "Calculator", "Measurement", "MeasurementGroup", "Patient", "Plotter"]
