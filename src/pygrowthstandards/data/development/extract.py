"""Extract developmental milestone data from CSV files."""

import csv
from dataclasses import dataclass
from pathlib import Path

from pygrowthstandards.config.development import MilestoneValidator
from pygrowthstandards.typing.development import (
    DataSourceType,
    MilestoneDomainType,
    StatisticalThresholdType,
)


@dataclass
class MilestoneRow:
    """Raw milestone data from a single CSV row.

    Attributes:
        universal_concept_id: Universal concept identifier.
        source_ref_id: Source-specific reference ID.
        standardized_domain: Milestone domain.
        target_age_nominal_months: Nominal target age in months.
        age_window_min_days: Minimum age in days.
        age_window_max_days: Maximum age in days.
        description_en: English description.
        description_pt: Portuguese description.
        statistical_threshold: Statistical threshold (P25_90, P75).
        is_red_flag: Whether this is a red flag milestone.
        risk_factor_dependency: Optional risk factor dependency.
    """

    universal_concept_id: str
    source_ref_id: str
    standardized_domain: MilestoneDomainType
    target_age_nominal_months: float
    age_window_min_days: int
    age_window_max_days: int
    description_en: str
    description_pt: str
    statistical_threshold: StatisticalThresholdType
    is_red_flag: bool
    risk_factor_dependency: str | None


@dataclass
class RawMilestoneTable:
    """Container for raw milestone data from a single source.

    Attributes:
        source: Data source (cdc, brazil).
        rows: List of milestone rows.
    """

    source: DataSourceType
    rows: list[MilestoneRow]


# TODO: break into smaller functions and as methods of RawMilestoneTable
def parse_milestone_csv(file_path: Path) -> RawMilestoneTable:
    """Parse a milestone CSV file.

    Args:
        file_path: Path to the CSV file.

    Returns:
        RawMilestoneTable with parsed milestone data.

    Raises:
        ValueError: If file format is invalid or data validation fails.
    """
    # Determine source from filename
    filename = file_path.stem.lower()
    if "brazil" in filename:
        source: DataSourceType = "brazil"
    elif "cdc" in filename:
        source: DataSourceType = "cdc"
    else:
        raise ValueError(f"Cannot determine source from filename: {file_path.name}")

    # Validate source
    if not MilestoneValidator.validate_source(source):
        raise ValueError(f"Invalid source: {source}")

    rows: list[MilestoneRow] = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate headers
        expected_headers = {
            "universal_concept_id",
            "source_ref_id",
            "standardized_domain",
            "target_age_nominal_months",
            "age_window_min_days",
            "age_window_max_days",
            "description_en",
            "description_pt",
            "statistical_threshold",
            "is_red_flag",
            "risk_factor_dependency",
        }

        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no headers: {file_path}")

        actual_headers = set(reader.fieldnames)
        if actual_headers != expected_headers:
            missing = expected_headers - actual_headers
            extra = actual_headers - expected_headers
            msg = f"Invalid CSV headers in {file_path}."
            if missing:
                msg += f" Missing: {missing}."
            if extra:
                msg += f" Extra: {extra}."
            raise ValueError(msg)

        # Parse rows
        for line_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
            try:
                # Parse and validate domain
                domain = row["standardized_domain"].strip()
                if not MilestoneValidator.validate_domain(domain):
                    raise ValueError(f"Invalid domain: {domain}")

                # Parse and validate threshold
                threshold = row["statistical_threshold"].strip()
                if not MilestoneValidator.validate_threshold(threshold):
                    raise ValueError(f"Invalid threshold: {threshold}")

                # Parse boolean red flag
                is_red_flag_str = row["is_red_flag"].strip().upper()
                is_red_flag = is_red_flag_str == "TRUE"

                # Parse numeric fields
                target_age = float(row["target_age_nominal_months"])
                min_days = int(row["age_window_min_days"])
                max_days = int(row["age_window_max_days"])

                # Validate age window
                if not MilestoneValidator.validate_age_window(min_days, max_days):
                    raise ValueError(f"Invalid age window: min={min_days}, max={max_days}")

                # Parse risk factor (optional)
                risk_factor = row["risk_factor_dependency"].strip()
                risk_factor_value = risk_factor if risk_factor else None

                # Create milestone row
                milestone = MilestoneRow(
                    universal_concept_id=row["universal_concept_id"].strip(),
                    source_ref_id=row["source_ref_id"].strip(),
                    standardized_domain=domain,
                    target_age_nominal_months=target_age,
                    age_window_min_days=min_days,
                    age_window_max_days=max_days,
                    description_en=row["description_en"].strip(),
                    description_pt=row["description_pt"].strip(),
                    statistical_threshold=threshold,
                    is_red_flag=is_red_flag,
                    risk_factor_dependency=risk_factor_value,
                )

                rows.append(milestone)

            except (ValueError, KeyError) as e:
                raise ValueError(f"Error parsing line {line_num} in {file_path}: {e}") from e

    if not rows:
        raise ValueError(f"No milestones found in {file_path}")

    print(f"Parsed {len(rows)} milestones from {file_path.name} (source: {source})")

    return RawMilestoneTable(source=source, rows=rows)


def discover_milestone_files(data_dir: Path) -> list[Path]:
    """Discover milestone CSV files in a directory.

    Args:
        data_dir: Directory containing milestone CSV files.

    Returns:
        List of paths to milestone CSV files.
    """
    csv_files = list(data_dir.rglob("*_milestones_*.csv"))
    csv_files.sort()  # Ensure consistent ordering
    return csv_files
