"""
Patient class extended with immunization tracking capabilities.

This module provides the PatientWithImmunization class that combines growth tracking
with vaccination schedule management based on Brazilian Ministry of Health recommendations.
"""

import logging
from datetime import date as dt_date
from typing import Any

from .immunization_calculator import ImmunizationCalculator
from .patient import Patient
from .vaccination import VaccinationRecordA, VaccinationStatus


class PatientWithImmunization(Patient):
    """
    Patient class extended with immunization tracking capabilities.

    This class inherits all functionality from the base Patient class and adds
    comprehensive vaccination schedule management and compliance tracking.

    Attributes:
        immunization_calculator: Calculator for vaccination schedules and compliance
        vaccination_history: List of vaccination records for this patient
    """

    def __init__(
        self,
        sex: str,
        birth_date: dt_date,
        gestational_age_weeks: int | None = None,
        birth_weight_grams: int | None = None,
        birth_length_cm: float | None = None,
        birth_head_circumference_cm: float | None = None,
    ):
        """
        Initialize a patient with immunization tracking capabilities.

        Args:
            patient_id: Unique identifier for the patient
            birth_date: Patient's birth date
            sex: Patient's sex ('M', 'F', or 'U')
            name: Optional patient name
            gestational_age_weeks: Optional gestational age at birth
            birth_weight_grams: Optional birth weight in grams
            birth_length_cm: Optional birth length in centimeters
            birth_head_circumference_cm: Optional birth head circumference in centimeters
        """
        # Initialize base Patient class
        super().__init__(
            birth_date=birth_date,
            sex=sex,
            gestational_age_weeks=gestational_age_weeks,
            birth_weight_grams=birth_weight_grams,
            birth_length_cm=birth_length_cm,
            birth_head_circumference_cm=birth_head_circumference_cm,
        )

        # Initialize immunization tracking
        self.immunization_calculator = ImmunizationCalculator(birth_date)
        self.vaccination_history: list[VaccinationRecordA] = []

        logging.info(f"Created patient with immunization tracking: {patient_id}")

    def add_vaccination_record(
        self,
        vaccine_type: str,
        vaccination_date: dt_date,
        dose_number: int,
        batch_number: str | None = None,
        administrator: str | None = None,
        location: str | None = None,
        notes: str | None = None,
    ) -> None:
        """
        Add a vaccination record to the patient's history.

        Args:
            vaccine_type: Type of vaccine administered
            vaccination_date: Date the vaccine was given
            dose_number: Dose number in the series
            batch_number: Optional vaccine batch number
            administrator: Optional name of person who administered vaccine
            location: Optional location where vaccine was given
            notes: Optional additional notes
        """
        record = VaccinationRecordA(
            vaccine_type=vaccine_type,
            vaccination_date=vaccination_date,
            dose_number=dose_number,
            batch_number=batch_number,
            administrator=administrator,
            location=location,
            notes=notes,
        )

        self.vaccination_history.append(record)
        logging.info(f"Added vaccination record: {vaccine_type} dose {dose_number} for patient {self.patient_id}")

    def get_vaccination_status(self, reference_date: dt_date | None = None) -> VaccinationStatus:
        """
        Get comprehensive vaccination status for the patient.

        Args:
            reference_date: Date to calculate status for (defaults to today)

        Returns:
            VaccinationStatus object with comprehensive vaccination information
        """
        if reference_date is None:
            reference_date = dt_date.today()

        return self.immunization_calculator.get_vaccination_status(self.vaccination_history, reference_date)

    def get_due_vaccines(self, reference_date: dt_date | None = None) -> list[dict[str, Any]]:
        """
        Get list of vaccines that are due for the patient.

        Args:
            reference_date: Date to calculate due vaccines for (defaults to today)

        Returns:
            List of dictionaries containing due vaccine information
        """
        if reference_date is None:
            reference_date = dt_date.today()

        return self.immunization_calculator.get_due_vaccines(self.vaccination_history, reference_date)

    def get_overdue_vaccines(self, reference_date: dt_date | None = None) -> list[dict[str, Any]]:
        """
        Get list of vaccines that are overdue for the patient.

        Args:
            reference_date: Date to calculate overdue vaccines for (defaults to today)

        Returns:
            List of dictionaries containing overdue vaccine information
        """
        if reference_date is None:
            reference_date = dt_date.today()

        return self.immunization_calculator.get_overdue_vaccines(self.vaccination_history, reference_date)

    def get_upcoming_vaccines(self, days_ahead: int = 30, reference_date: dt_date | None = None) -> list[dict[str, Any]]:
        """
        Get list of vaccines coming due within the specified timeframe.

        Args:
            days_ahead: Number of days to look ahead (default: 30)
            reference_date: Date to calculate from (defaults to today)

        Returns:
            List of dictionaries containing upcoming vaccine information
        """
        if reference_date is None:
            reference_date = dt_date.today()

        return self.immunization_calculator.get_upcoming_vaccines(self.vaccination_history, reference_date, days_ahead)

    def check_series_completion(self, vaccine_type: str) -> dict[str, int]:
        """
        Check completion status for a specific vaccine series.

        Args:
            vaccine_type: Type of vaccine to check

        Returns:
            Dictionary with series completion information
        """
        return self.immunization_calculator.check_series_completion(vaccine_type, self.vaccination_history)

    def is_vaccine_series_complete(self, vaccine_type: str) -> bool:
        """
        Check if a vaccine series is complete.

        Args:
            vaccine_type: Type of vaccine to check

        Returns:
            True if series is complete, False otherwise
        """
        completion_info = self.check_series_completion(vaccine_type)
        return completion_info["completion_percentage"] == 100

    def get_vaccination_history_summary(self) -> dict[str, Any]:
        """
        Get a summary of the patient's vaccination history.

        Returns:
            Dictionary containing vaccination history summary
        """
        vaccine_counts = {}
        earliest_vaccine = None
        latest_vaccine = None

        for record in self.vaccination_history:
            # Count vaccines by type
            if record.vaccine_type in vaccine_counts:
                vaccine_counts[record.vaccine_type] += 1
            else:
                vaccine_counts[record.vaccine_type] = 1

            # Track date range
            if earliest_vaccine is None or record.vaccination_date < earliest_vaccine:
                earliest_vaccine = record.vaccination_date
            if latest_vaccine is None or record.vaccination_date > latest_vaccine:
                latest_vaccine = record.vaccination_date

        return {
            "total_vaccinations": len(self.vaccination_history),
            "unique_vaccine_types": len(vaccine_counts),
            "vaccine_counts": vaccine_counts,
            "earliest_vaccination": earliest_vaccine,
            "latest_vaccination": latest_vaccine,
            "vaccination_period_days": ((latest_vaccine - earliest_vaccine).days if earliest_vaccine and latest_vaccine else 0),
        }

    def generate_immunization_report(self, reference_date: dt_date | None = None, include_upcoming_days: int = 60) -> dict[str, Any]:
        """
        Generate a comprehensive immunization report for the patient.

        Args:
            reference_date: Date to generate report for (defaults to today)
            include_upcoming_days: Days ahead to include upcoming vaccines

        Returns:
            Dictionary containing comprehensive immunization report
        """
        if reference_date is None:
            reference_date = dt_date.today()

        status = self.get_vaccination_status(reference_date)
        due_vaccines = self.get_due_vaccines(reference_date)
        overdue_vaccines = self.get_overdue_vaccines(reference_date)
        upcoming_vaccines = self.get_upcoming_vaccines(include_upcoming_days, reference_date)
        history_summary = self.get_vaccination_history_summary()

        return {
            "patient_info": {
                "patient_id": self.patient_id,
                "name": self.name,
                "birth_date": self.birth_date,
                "age_days": (reference_date - self.birth_date).days,
                "sex": self.sex,
            },
            "report_date": reference_date,
            "vaccination_status": {
                "total_vaccines_given": status.total_vaccines_given,
                "vaccines_up_to_date": status.vaccines_up_to_date,
                "vaccines_due": status.vaccines_due,
                "vaccines_overdue": status.vaccines_overdue,
                "overall_compliance_percentage": status.overall_compliance_percentage,
            },
            "due_vaccines": due_vaccines,
            "overdue_vaccines": overdue_vaccines,
            "upcoming_vaccines": upcoming_vaccines,
            "vaccination_history_summary": history_summary,
            "recommendations": self._generate_recommendations(due_vaccines, overdue_vaccines, upcoming_vaccines),
        }

    def _generate_recommendations(
        self, due_vaccines: list[dict[str, Any]], overdue_vaccines: list[dict[str, Any]], upcoming_vaccines: list[dict[str, Any]]
    ) -> list[str]:
        """
        Generate vaccination recommendations based on current status.

        Args:
            due_vaccines: List of due vaccines
            overdue_vaccines: List of overdue vaccines
            upcoming_vaccines: List of upcoming vaccines

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if overdue_vaccines:
            recommendations.append(f"URGENT: {len(overdue_vaccines)} vaccine(s) are overdue. Schedule appointment immediately.")

        if due_vaccines:
            recommendations.append(f"{len(due_vaccines)} vaccine(s) are due now. Schedule appointment as soon as possible.")

        if upcoming_vaccines:
            next_vaccine = min(upcoming_vaccines, key=lambda x: x["due_date"])
            recommendations.append(f"Next vaccine due: {next_vaccine['vaccine_type']} on {next_vaccine['due_date']}")

        if not due_vaccines and not overdue_vaccines:
            recommendations.append("Patient is up to date with vaccinations.")

        return recommendations

    def __str__(self) -> str:
        """String representation of the patient with immunization info."""
        base_str = super().__str__()
        vaccination_count = len(self.vaccination_history)
        return f"{base_str} | Vaccinations: {vaccination_count}"

    def __repr__(self) -> str:
        """Detailed representation of the patient with immunization info."""
        return (
            f"PatientWithImmunization("
            f"patient_id='{self.patient_id}', "
            f"birth_date={self.birth_date}, "
            f"sex='{self.sex}', "
            f"vaccinations={len(self.vaccination_history)})"
        )
