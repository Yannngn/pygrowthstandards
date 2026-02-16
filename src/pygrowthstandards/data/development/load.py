"""Load and query developmental milestone reference data."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

from pygrowthstandards.typing.development import AchievementStatusType, DataSourceType, MilestoneDomainType


@dataclass
class PatientMilestoneRecord:
    """Record of a patient's milestone achievement.

    Attributes:
        universal_concept_id: Milestone identifier.
        status: Achievement status.
        assessment_date: Date of assessment.
        age_at_assessment_days: Patient age in days at assessment.
        notes: Optional clinical notes.
    """

    universal_concept_id: str
    status: AchievementStatusType
    assessment_date: datetime
    age_at_assessment_days: int
    notes: str | None = None


@dataclass
class MilestoneTable:
    """Milestone reference data with patient tracking capability.

    Attributes:
        source: Data source filter (None for all sources).
        milestones: DataFrame with milestone reference data.
        patient_records: Dict mapping patient IDs to milestone records.
    """

    source: DataSourceType | None
    milestones: pd.DataFrame
    patient_records: dict[str, list[PatientMilestoneRecord]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate data after initialization."""
        if self.milestones.empty:
            raise ValueError("Milestone DataFrame is empty")

        # Validate source filter
        if self.source is not None:
            if self.source not in self.milestones["source"].unique():
                raise ValueError(f"Source {self.source} not found in milestone data")

    def filter_by_age(self, age_days: int, domain: MilestoneDomainType | None = None) -> pd.DataFrame:
        """Get milestones applicable for a given age.

        Args:
            age_days: Age in days.
            domain: Optional domain filter.

        Returns:
            DataFrame of applicable milestones.
        """
        # Filter by age window
        mask = (self.milestones["age_window_min_days"] <= age_days) & (self.milestones["age_window_max_days"] >= age_days)

        # Apply domain filter if specified
        if domain is not None:
            mask = mask & (self.milestones["standardized_domain"] == domain)

        result = self.milestones[mask].copy()

        # Sort by domain and age window center
        result = result.sort_values(
            by=["standardized_domain", "age_window_center_days"],
            ignore_index=True,
        )

        return result

    def filter_by_domain(self, domain: MilestoneDomainType) -> pd.DataFrame:
        """Get all milestones for a specific domain.

        Args:
            domain: Domain to filter by.

        Returns:
            DataFrame of milestones in the domain.
        """
        result = self.milestones[self.milestones["standardized_domain"] == domain].copy()

        # Sort by age window center
        result = result.sort_values(by=["age_window_center_days"], ignore_index=True)

        return result

    def get_milestone(self, universal_concept_id: str) -> pd.Series | None:
        """Get a specific milestone by ID.

        Args:
            universal_concept_id: Milestone identifier.

        Returns:
            Series with milestone data, or None if not found.
        """
        matches = self.milestones[self.milestones["universal_concept_id"] == universal_concept_id]

        if matches.empty:
            return None

        if len(matches) > 1:
            # Multiple sources have this milestone; return first match
            return matches.iloc[0]

        return matches.iloc[0]

    def check_milestone_expected(
        self,
        universal_concept_id: str,
        age_days: int,
    ) -> bool:
        """Check if a milestone is expected (within age window) for given age.

        Args:
            universal_concept_id: Milestone identifier.
            age_days: Age in days.

        Returns:
            True if milestone is within expected age window.
        """
        milestone = self.get_milestone(universal_concept_id)

        if milestone is None:
            return False

        return milestone["age_window_min_days"] <= age_days <= milestone["age_window_max_days"]

    def add_patient_milestone(
        self,
        patient_id: str,
        record: PatientMilestoneRecord,
    ) -> None:
        """Record a patient's milestone achievement.

        Args:
            patient_id: Patient identifier.
            record: Milestone achievement record.
        """
        if patient_id not in self.patient_records:
            self.patient_records[patient_id] = []

        self.patient_records[patient_id].append(record)

    def get_patient_milestones(
        self,
        patient_id: str,
    ) -> list[PatientMilestoneRecord]:
        """Get all milestone records for a patient.

        Args:
            patient_id: Patient identifier.

        Returns:
            List of milestone records for the patient.
        """
        return self.patient_records.get(patient_id, [])

    def get_patient_milestone_summary(
        self,
        patient_id: str,
        current_age_days: int,
    ) -> dict[str, dict]:
        """Get summary of patient's milestone achievements by domain.

        Args:
            patient_id: Patient identifier.
            current_age_days: Patient's current age in days.

        Returns:
            Dict mapping domain to summary statistics.
        """
        records = self.get_patient_milestones(patient_id)

        if not records:
            return {}

        # Get applicable milestones for current age
        applicable = self.filter_by_age(current_age_days)

        # Create record lookup
        record_lookup = {r.universal_concept_id: r for r in records}

        # Calculate summary by domain
        summary: dict[str, dict] = {}

        for domain in applicable["standardized_domain"].unique():
            domain_milestones = applicable[applicable["standardized_domain"] == domain]

            achieved_count = 0
            not_achieved_count = 0
            not_assessed_count = 0

            for _, milestone in domain_milestones.iterrows():
                milestone_id = milestone["universal_concept_id"]

                if milestone_id in record_lookup:
                    record = record_lookup[milestone_id]
                    if record.status == "achieved":
                        achieved_count += 1
                    elif record.status == "not_achieved":
                        not_achieved_count += 1
                    else:
                        not_assessed_count += 1
                else:
                    not_assessed_count += 1

            total = len(domain_milestones)

            summary[domain] = {
                "total": total,
                "achieved": achieved_count,
                "not_achieved": not_achieved_count,
                "not_assessed": not_assessed_count,
                "achievement_rate": achieved_count / total if total > 0 else 0.0,
            }

        return summary


def load_milestone_reference(
    data_path: Path | None = None,
    source: DataSourceType | None = None,
) -> MilestoneTable:
    """Load milestone reference data from packaged parquet file.

    Args:
        data_path: Path to parquet file (None = use default packaged data).
        source: Optional source filter (None = load all sources).

    Returns:
        MilestoneTable with loaded data.

    Raises:
        FileNotFoundError: If data file not found.
        ValueError: If data is invalid.
    """
    if data_path is None:
        # Use default packaged data location
        package_dir = Path(__file__).parent
        data_path = package_dir / "development_milestones.parquet"

    if not data_path.exists():
        raise FileNotFoundError(f"Milestone data file not found: {data_path}")

    # Load parquet file
    df = pd.read_parquet(data_path)

    if df.empty:
        raise ValueError("Loaded milestone data is empty")

    # Apply source filter if specified
    if source is not None:
        df = df[df["source"] == source].copy()

        if df.empty:
            raise ValueError(f"No milestones found for source: {source}")

    return MilestoneTable(source=source, milestones=df)
