"""
PyGrowthStandards - A Python library for pediatric growth standard calculations.
"""

__version__ = "0.1.0"

# Import main classes and functions, handling missing dependencies gracefully
try:
    from .src.pygrowthstandards import (
        Calculator,
        Measurement,
        MeasurementGroup,
        Patient,
        Plotter,
        functional,
        utils,
    )

    __all__ = [
        "functional",
        "Calculator",
        "Measurement",
        "MeasurementGroup",
        "Patient",
        "Plotter",
        "utils",
    ]

except ImportError as e:
    # If dependencies are missing, provide a helpful error message
    import warnings

    warnings.warn(
        f"PyGrowthStandards dependencies not available: {e}. "
        "Please install required packages: numpy, pandas, matplotlib, scipy. "
        "Run: pip install numpy pandas matplotlib scipy",
        ImportWarning,
        stacklevel=1,
    )

    # Define placeholder variables that don't raise errors during import
    functional = None
    Calculator = None
    Measurement = None
    MeasurementGroup = None
    Patient = None
    Plotter = None
    utils = None

    __all__ = [
        "functional",
        "Calculator",
        "Measurement",
        "MeasurementGroup",
        "Patient",
        "Plotter",
        "utils",
    ]
