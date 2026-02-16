"""Transform and validate developmental milestone data."""

from dataclasses import dataclass, field

import pandas as pd

from pygrowthstandards.data.development.extract import RawMilestoneTable
from pygrowthstandards.utils.version import get_package_version


@dataclass
class MilestoneData:
    """Aggregated milestone data from multiple sources.

    Attributes:
        tables: List of raw milestone tables.
        dataframe: Consolidated DataFrame with all milestones.
    """

    dataframe: pd.DataFrame
    version: str = field(default_factory=get_package_version)
    tables: list[RawMilestoneTable] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate data after initialization."""
        if not self.tables:
            raise ValueError("No milestone tables provided")

        if self.dataframe.empty:
            raise ValueError("DataFrame is empty")

        # Validate required columns
        required_columns = {
            "source",
            "universal_concept_id",
            "source_ref_id",
            "standardized_domain",
            "target_age_nominal_months",
            "age_window_min_days",
            "age_window_max_days",
            "age_window_center_days",
            "description_en",
            "description_pt",
            "statistical_threshold",
            "is_red_flag",
            "risk_factor_dependency",
        }

        actual_columns = set(self.dataframe.columns)
        missing = required_columns - actual_columns
        if missing:
            raise ValueError(f"Missing required columns: {missing}")


def aggregate_milestone_tables(tables: list[RawMilestoneTable]) -> MilestoneData:
    """Aggregate raw milestone tables into a consolidated dataset.

    Args:
        tables: List of raw milestone tables to aggregate.

    Returns:
        MilestoneData with consolidated DataFrame.

    Raises:
        ValueError: If validation fails.
    """
    if not tables:
        raise ValueError("No tables provided for aggregation")

    all_records: list[dict] = []

    for table in tables:
        for row in table.rows:
            # Calculate age window center for sorting/display
            age_window_center = (row.age_window_min_days + row.age_window_max_days) / 2

            record = {
                "source": table.source,
                "universal_concept_id": row.universal_concept_id,
                "source_ref_id": row.source_ref_id,
                "standardized_domain": row.standardized_domain,
                "target_age_nominal_months": row.target_age_nominal_months,
                "age_window_min_days": row.age_window_min_days,
                "age_window_max_days": row.age_window_max_days,
                "age_window_center_days": age_window_center,
                "description_en": row.description_en,
                "description_pt": row.description_pt,
                "statistical_threshold": row.statistical_threshold,
                "is_red_flag": row.is_red_flag,
                "risk_factor_dependency": row.risk_factor_dependency,
            }

            all_records.append(record)

    if not all_records:
        raise ValueError("No milestone records found in tables")

    # Create DataFrame
    df = pd.DataFrame(all_records)

    # Sort by source, age window center, and domain for consistent ordering
    df = df.sort_values(
        by=["source", "age_window_center_days", "standardized_domain"],
        ignore_index=True,
    )

    # Validate data consistency
    _validate_milestone_data(df)

    print(f"Aggregated {len(df)} milestones from {len(tables)} sources")
    print(f"  Sources: {df['source'].unique().tolist()}")
    print(f"  Domains: {df['standardized_domain'].nunique()}")
    print(f"  Age range: {df['age_window_min_days'].min()}-{df['age_window_max_days'].max()} days")

    return MilestoneData(tables=tables, dataframe=df)


def _validate_milestone_data(df: pd.DataFrame) -> None:
    """Validate milestone data consistency.

    Args:
        df: DataFrame to validate.

    Raises:
        ValueError: If validation fails.
    """
    # Check for null values in critical fields
    critical_fields = [
        "source",
        "universal_concept_id",
        "source_ref_id",
        "standardized_domain",
        "target_age_nominal_months",
        "age_window_min_days",
        "age_window_max_days",
        "statistical_threshold",
    ]

    for critical in critical_fields:
        null_count = df[critical].isnull().sum()
        if null_count > 0:
            raise ValueError(f"Found {null_count} null values in critical field: {critical}")

    # Check age window consistency
    invalid_windows = df[df["age_window_min_days"] >= df["age_window_max_days"]]
    if not invalid_windows.empty:
        raise ValueError(f"Found {len(invalid_windows)} milestones with invalid age windows (min >= max)")

    # Check for negative ages
    negative_ages = df[(df["age_window_min_days"] < 0) | (df["age_window_max_days"] < 0)]
    if not negative_ages.empty:
        raise ValueError(f"Found {len(negative_ages)} milestones with negative ages")

    # Check for duplicate source_ref_ids within same source (these should be unique)
    duplicates = df[df.duplicated(subset=["source", "source_ref_id"], keep=False)]
    if not duplicates.empty:
        dup_ids = duplicates.groupby("source")["source_ref_id"].apply(list)
        raise ValueError(f"Found duplicate source_ref_ids within sources: {dup_ids.to_dict()}")

    # Note: Same universal_concept_id can appear multiple times with different
    # age windows - this is expected and valid

    print("Data validation passed")
