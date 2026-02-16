"""Object-oriented tracker for developmental milestone assessment."""

from datetime import datetime

import pandas as pd

from pygrowthstandards.data.development.load import (
    MilestoneTable,
    PatientMilestoneRecord,
    load_milestone_reference
)
from pygrowthstandards.typing.development import (
    AchievementStatusType,
    DataSourceType,
    MilestoneDomainType
)


class MilestoneTracker:
    """Tracker for patient developmental milestone achievements.
    
    This class provides an object-oriented interface for tracking and querying
    developmental milestones for a patient. It uses a source-specific milestone
    reference and maintains patient achievement records.
    
    Attributes:
        patient_id: Identifier for the patient being tracked.
        source: Data source for milestone reference ("cdc" or "brazil").
        milestone_table: Reference data and patient records.
    
    Example:
        >>> tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        >>> milestones = tracker.get_applicable_milestones()
        >>> tracker.record_achievement(
        ...     "MOTOR-SITS_WITHOUT_SUPPORT",
        ...     "achieved",
        ...     datetime.now(),
        ...     180
        ... )
        >>> summary = tracker.get_achievement_summary()
    """
    
    def __init__(
        self,
        patient_id: str,
        age_days: int,
        source: DataSourceType = "brazil",
    ):
        """Initialize milestone tracker for a patient.
        
        Args:
            patient_id: Unique patient identifier.
            age_days: Patient's current age in days.
            source: Data source for milestone reference ("cdc" or "brazil").
        """
        self.patient_id = patient_id
        self.age_days = age_days
        self.source = source
        self.milestone_table = load_milestone_reference(source=source)
    
    def get_applicable_milestones(
        self,
        domain: MilestoneDomainType | None = None,
    ) -> pd.DataFrame:
        """Get milestones applicable for patient's current age.
        
        Args:
            domain: Optional domain filter.
            
        Returns:
            DataFrame of applicable milestones.
        """
        return self.milestone_table.filter_by_age(self.age_days, domain=domain)
    
    def get_milestones_by_domain(
        self,
        domain: MilestoneDomainType,
    ) -> pd.DataFrame:
        """Get all milestones for a specific domain.
        
        Args:
            domain: Domain to filter by.
            
        Returns:
            DataFrame of milestones in the domain.
        """
        return self.milestone_table.filter_by_domain(domain)
    
    def record_achievement(
        self,
        universal_concept_id: str,
        status: AchievementStatusType,
        assessment_date: datetime,
        age_at_assessment_days: int,
        notes: str | None = None,
    ) -> None:
        """Record a milestone achievement for the patient.
        
        Args:
            universal_concept_id: Milestone identifier.
            status: Achievement status ("achieved", "not_achieved", "not_assessed").
            assessment_date: Date of assessment.
            age_at_assessment_days: Patient age in days at assessment.
            notes: Optional clinical notes.
        """
        record = PatientMilestoneRecord(
            universal_concept_id=universal_concept_id,
            status=status,
            assessment_date=assessment_date,
            age_at_assessment_days=age_at_assessment_days,
            notes=notes,
        )
        
        self.milestone_table.add_patient_milestone(self.patient_id, record)
    
    def get_patient_records(self) -> list[PatientMilestoneRecord]:
        """Get all milestone records for the patient.
        
        Returns:
            List of milestone records.
        """
        return self.milestone_table.get_patient_milestones(self.patient_id)
    
    def get_achievement_summary(
        self,
    ) -> dict[str, dict]:
        """Get summary of patient's milestone achievements by domain.
        
        Returns:
            Dict mapping domain to summary statistics (total, achieved, not_achieved, etc.).
        """
        return self.milestone_table.get_patient_milestone_summary(
            self.patient_id,
            self.age_days,
        )
    
    def get_delayed_milestones(self) -> pd.DataFrame:
        """Get milestones that patient has not achieved but age is past the window.
        
        Returns:
            DataFrame of delayed milestones.
        """
        records = self.get_patient_records()
        
        # Create lookup of recorded milestones
        achieved_ids = {
            r.universal_concept_id for r in records if r.status == "achieved"
        }
        
        # Get milestones where max age has passed
        all_milestones = self.milestone_table.milestones
        
        delayed = all_milestones[
            (all_milestones["age_window_max_days"] < self.age_days)
            & (~all_milestones["universal_concept_id"].isin(achieved_ids))
        ].copy()
        
        # Sort by how far past the window we are
        delayed["days_overdue"] = self.age_days - delayed["age_window_max_days"]
        delayed = delayed.sort_values(by=["days_overdue"], ascending=False, ignore_index=True)
        
        return delayed
    
    def get_red_flag_milestones(self) -> pd.DataFrame:
        """Get red flag milestones applicable for patient's age.
        
        Returns:
            DataFrame of red flag milestones.
        """
        applicable = self.get_applicable_milestones()
        red_flags = applicable[applicable["is_red_flag"] == True].copy()  # noqa: E712
        return red_flags
    
    def update_age(self, age_days: int) -> None:
        """Update the patient's current age.
        
        Args:
            age_days: New age in days.
        """
        self.age_days = age_days
    
    def check_milestone_status(
        self,
        universal_concept_id: str,
    ) -> tuple[bool, AchievementStatusType | None]:
        """Check if a milestone has been assessed for this patient.
        
        Args:
            universal_concept_id: Milestone identifier.
            
        Returns:
            Tuple of (assessed, status) where assessed is True if recorded.
        """
        records = self.get_patient_records()
        
        for record in records:
            if record.universal_concept_id == universal_concept_id:
                return (True, record.status)
        
        return (False, None)
