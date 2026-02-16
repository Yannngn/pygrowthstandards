"""Tests for developmental milestone ETL and API."""

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from pygrowthstandards import functional as F
from pygrowthstandards.data.development import (
    MilestoneData,
    MilestoneRow,
    RawMilestoneTable,
    aggregate_milestone_tables,
    load_milestone_reference,
    parse_milestone_csv,
)
from pygrowthstandards.oop import MilestoneTracker


class TestMilestoneETL:
    """Test ETL pipeline components."""
    
    def test_parse_brazil_csv(self):
        """Test parsing Brazil milestone CSV file."""
        csv_path = Path(__file__).parent.parent.parent / "data" / "raw" / "development" / "brazil_milestones_2024.csv"
        
        if not csv_path.exists():
            pytest.skip(f"CSV file not found: {csv_path}")
        
        table = parse_milestone_csv(csv_path)
        
        assert table.source == "brazil"
        assert len(table.rows) > 0
        assert all(isinstance(row, MilestoneRow) for row in table.rows)
    
    def test_parse_cdc_csv(self):
        """Test parsing CDC milestone CSV file."""
        csv_path = Path(__file__).parent.parent.parent / "data" / "raw" / "development" / "cdc_milestones_2022.csv"
        
        if not csv_path.exists():
            pytest.skip(f"CSV file not found: {csv_path}")
        
        table = parse_milestone_csv(csv_path)
        
        assert table.source == "cdc"
        assert len(table.rows) > 0
        assert all(isinstance(row, MilestoneRow) for row in table.rows)
    
    def test_aggregate_tables(self):
        """Test aggregating milestone tables."""
        # Create minimal test data
        row1 = MilestoneRow(
            universal_concept_id="TEST-1",
            source_ref_id="BR_TEST_1",
            standardized_domain="MOTOR_GROSS",
            target_age_nominal_months=6.0,
            age_window_min_days=150,
            age_window_max_days=210,
            description_en="Test milestone 1",
            description_pt="Marco de teste 1",
            statistical_threshold="P25_90",
            is_red_flag=False,
            risk_factor_dependency=None,
        )
        
        table1 = RawMilestoneTable(source="brazil", rows=[row1])
        
        data = aggregate_milestone_tables([table1])
        
        assert isinstance(data, MilestoneData)
        assert isinstance(data.dataframe, pd.DataFrame)
        assert len(data.dataframe) == 1
        assert "age_window_center_days" in data.dataframe.columns


class TestFunctionalAPI:
    """Test functional milestone API."""
    
    def test_get_milestones_for_age(self):
        """Test getting milestones for a specific age."""
        milestones = F.get_milestones_for_age(180, source="brazil")
        
        assert isinstance(milestones, pd.DataFrame)
        assert len(milestones) > 0
        
        # All milestones should be within age window
        for _, m in milestones.iterrows():
            assert m["age_window_min_days"] <= 180 <= m["age_window_max_days"]
    
    def test_get_milestones_by_domain(self):
        """Test getting milestones filtered by domain."""
        motor_milestones = F.get_milestones_by_domain("MOTOR_GROSS", source="brazil")
        
        assert isinstance(motor_milestones, pd.DataFrame)
        assert len(motor_milestones) > 0
        assert all(motor_milestones["standardized_domain"] == "MOTOR_GROSS")
    
    def test_get_domains(self):
        """Test getting list of available domains."""
        domains = F.get_domains("brazil")
        
        assert isinstance(domains, list)
        assert len(domains) > 0
        assert "MOTOR_GROSS" in domains
        assert "COMMUNICATION" in domains
    
    def test_check_milestone_expected(self):
        """Test checking if milestone is expected at age."""
        # Get a milestone first
        milestones = F.get_milestones_for_age(180, source="brazil")
        
        if len(milestones) > 0:
            milestone_id = milestones.iloc[0]["universal_concept_id"]
            
            # Should be expected at 180 days
            assert F.check_milestone_expected(milestone_id, 180, "brazil") is True
            
            # Should not be expected at 0 days (newborn)
            assert F.check_milestone_expected(milestone_id, 0, "brazil") is False


class TestMilestoneTracker:
    """Test OOP milestone tracker."""
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        
        assert tracker.patient_id == "P001"
        assert tracker.age_days == 180
        assert tracker.source == "brazil"
    
    def test_get_applicable_milestones(self):
        """Test getting applicable milestones."""
        tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        
        milestones = tracker.get_applicable_milestones()
        
        assert isinstance(milestones, pd.DataFrame)
        assert len(milestones) > 0
    
    def test_record_achievement(self):
        """Test recording milestone achievement."""
        tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        
        # Get a milestone to record
        milestones = tracker.get_applicable_milestones()
        if len(milestones) > 0:
            milestone_id = milestones.iloc[0]["universal_concept_id"]
            
            # Record achievement
            tracker.record_achievement(
                milestone_id,
                "achieved",
                datetime.now(),
                180,
                notes="Test achievement",
            )
            
            # Verify it was recorded
            records = tracker.get_patient_records()
            assert len(records) == 1
            assert records[0].universal_concept_id == milestone_id
            assert records[0].status == "achieved"
    
    def test_get_achievement_summary(self):
        """Test getting achievement summary by domain."""
        tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        
        # Record some achievements
        milestones = tracker.get_applicable_milestones()
        if len(milestones) > 0:
            milestone_id = milestones.iloc[0]["universal_concept_id"]
            tracker.record_achievement(
                milestone_id,
                "achieved",
                datetime.now(),
                180,
            )
        
        summary = tracker.get_achievement_summary()
        
        assert isinstance(summary, dict)
        # Should have at least one domain
        if len(summary) > 0:
            domain_key = list(summary.keys())[0]
            domain_summary = summary[domain_key]
            
            assert "total" in domain_summary
            assert "achieved" in domain_summary
            assert "achievement_rate" in domain_summary
    
    def test_update_age(self):
        """Test updating patient age."""
        tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        
        tracker.update_age(365)
        assert tracker.age_days == 365
        
        # Applicable milestones should change
        milestones = tracker.get_applicable_milestones()
        for _, m in milestones.iterrows():
            assert m["age_window_min_days"] <= 365 <= m["age_window_max_days"]
    
    def test_check_milestone_status(self):
        """Test checking milestone status for patient."""
        tracker = MilestoneTracker(patient_id="P001", age_days=180, source="brazil")
        
        milestones = tracker.get_applicable_milestones()
        if len(milestones) > 0:
            milestone_id = milestones.iloc[0]["universal_concept_id"]
            
            # Before recording
            assessed, status = tracker.check_milestone_status(milestone_id)
            assert assessed is False
            assert status is None
            
            # Record achievement
            tracker.record_achievement(
                milestone_id,
                "achieved",
                datetime.now(),
                180,
            )
            
            # After recording
            assessed, status = tracker.check_milestone_status(milestone_id)
            assert assessed is True
            assert status == "achieved"


class TestDataValidation:
    """Test data validation and integrity."""
    
    def test_milestone_reference_loads(self):
        """Test that milestone reference data loads successfully."""
        table = load_milestone_reference(source="brazil")
        
        assert table.source == "brazil"
        assert not table.milestones.empty
        assert len(table.milestones) > 0
    
    def test_milestone_columns(self):
        """Test that milestone data has required columns."""
        table = load_milestone_reference(source="brazil")
        
        required_columns = [
            "source",
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
        ]
        
        for col in required_columns:
            assert col in table.milestones.columns
    
    def test_age_window_validity(self):
        """Test that all age windows are valid (min < max)."""
        table = load_milestone_reference(source="brazil")
        
        invalid = table.milestones[
            table.milestones["age_window_min_days"] >= table.milestones["age_window_max_days"]
        ]
        
        assert len(invalid) == 0, f"Found {len(invalid)} invalid age windows"
    
    def test_domain_values(self):
        """Test that all domains are valid."""
        table = load_milestone_reference(source="brazil")
        
        valid_domains = {
            "MOTOR_GROSS",
            "MOTOR_FINE",
            "SOCIAL_EMOTIONAL",
            "COMMUNICATION",
            "COGNITIVE",
            "SENSORY",
        }
        
        actual_domains = set(table.milestones["standardized_domain"].unique())
        
        assert actual_domains.issubset(valid_domains), f"Invalid domains: {actual_domains - valid_domains}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
