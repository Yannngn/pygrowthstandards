"""Data module containing growth reference standards."""

from pathlib import Path

from pygrowthstandards.data.transform import GrowthData

# Get the directory containing this file
_DATA_DIR = Path(__file__).parent

# Path to the reference data file
REFERENCE_DATA_PATH = _DATA_DIR / f"pygrowthstandards_{GrowthData.version}.parquet"


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
