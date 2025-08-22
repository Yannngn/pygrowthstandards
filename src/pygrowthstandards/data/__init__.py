"""Data module containing growth reference standards."""

import os
from pathlib import Path

# Get the directory containing this file
_DATA_DIR = Path(__file__).parent

# Path to the reference data file
REFERENCE_DATA_PATH = _DATA_DIR / "pygrowthstandards_0.1.0.parquet"


def get_data_path() -> Path:
    """Get the path to the reference data file.

    Returns:
        Path: Path to the pygrowthstandards reference data parquet file.
    """
    return REFERENCE_DATA_PATH


def data_exists() -> bool:
    """Check if the reference data file exists.

    Returns:
        bool: True if the data file exists, False otherwise.
    """
    return REFERENCE_DATA_PATH.exists()
