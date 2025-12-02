"""
Immunization calculator for determining vaccination schedules and compliance.

This module provides the ImmunizationCalculator class that handles vaccination
schedule calculations based on Brazilian Ministry of Health recommendations.
"""

import logging
from datetime import date as dt_date
from datetime import timedelta

from ..config.immunization import VACCINE_SCHEDULES, VaccineSchedule
from ..utils.date_utils import add_days, days_between
from .vaccination import VaccinationRecordA, VaccinationStatus


class ImmunizationCalculator:
    """
    Calculator for determining vaccination schedules and compliance based on
    Brazilian Ministry of Health recommendations.
    """

    def __init__(self):
        """Initialize the immunization calculator."""
        self.schedules = VACCINE_SCHEDULES
        logging.info(f"Loaded {len(self.schedules)} vaccine schedules")

    def get_due_date(self, vaccine_key: str, birth_date: dt_date) -> dt_date:
        """
        Calculate the due date for a specific vaccine dose.

        Args:
            vaccine_key: Key from vaccine schedule
            birth_date: Patient's birth date

        Returns:
            Due date for the vaccine

        Raises:
            ValueError: If vaccine_key is not found in schedules
        """
        if vaccine_key not in self.schedules:
            raise ValueError(f"Unknown vaccine key: {vaccine_key}")

        schedule = self.schedules[vaccine_key]

        return add_days(birth_date, schedule.min_age_days)

    def get_overdue_date(self, vaccine_key: str, birth_date: dt_date) -> dt_date | None:
        """
        Calculate when a vaccine becomes overdue.

        Args:
            vaccine_key: Key from vaccine schedule
            birth_date: Patient's birth date

        Returns:
            Date when vaccine becomes overdue, or None if no upper limit

        Raises:
            ValueError: If vaccine_key is not found in schedules
        """
        if vaccine_key not in self.schedules:
            raise ValueError(f"Unknown vaccine key: {vaccine_key}")

        schedule = self.schedules[vaccine_key]
        if schedule.max_age_days is None:
            return None

        return add_days(birth_date, schedule.max_age_days)

    def check_vaccination_status(
        self,
        vaccine_key: str,
        birth_date: dt_date,
        current_date: dt_date,
        given_date: dt_date | None = None,
        previous_dose_date: dt_date | None = None,
    ) -> VaccinationStatus:
        """
        Check the vaccination status for a specific vaccine dose.

        Args:
            vaccine_key: Key from vaccine schedule
            birth_date: Patient's birth date
            current_date: Current date for status evaluation
            given_date: Date vaccine was given (if applicable)
            previous_dose_date: Date of previous dose in series (if applicable)

        Returns:
            VaccinationStatus object with current status

        Raises:
            ValueError: If vaccine_key is not found in schedules
        """
        if vaccine_key not in self.schedules:
            raise ValueError(f"Unknown vaccine key: {vaccine_key}")

        schedule = self.schedules[vaccine_key]
        due_date = self.get_due_date(vaccine_key, birth_date)
        overdue_date = self.get_overdue_date(vaccine_key, birth_date)

        # Check if patient is old enough for this vaccine
        patient_age_days = days_between(birth_date, current_date)
        if patient_age_days < schedule.min_age_days:
            return VaccinationStatus(
                vaccine_key=vaccine_key,
                vaccine_type=schedule.vaccine_type,
                dose_number=schedule.dose_number,
                status="not_due",
                due_date=due_date,
                description=schedule.description,
            )

        # Check if vaccine was given
        if given_date is not None:
            # Validate timing
            given_age_days = days_between(birth_date, given_date)

            # Check minimum age
            if given_age_days < schedule.min_age_days:
                return VaccinationStatus(
                    vaccine_key=vaccine_key,
                    vaccine_type=schedule.vaccine_type,
                    dose_number=schedule.dose_number,
                    status="contraindicated",
                    due_date=due_date,
                    given_date=given_date,
                    description=f"{schedule.description} - Administrada muito cedo",
                )

            # Check interval from previous dose
            if schedule.interval_from_previous is not None and previous_dose_date is not None:
                interval_days = days_between(previous_dose_date, given_date)
                if interval_days < schedule.interval_from_previous:
                    return VaccinationStatus(
                        vaccine_key=vaccine_key,
                        vaccine_type=schedule.vaccine_type,
                        dose_number=schedule.dose_number,
                        status="contraindicated",
                        due_date=due_date,
                        given_date=given_date,
                        description=f"{schedule.description} - Intervalo insuficiente",
                    )

            # Vaccine was given appropriately
            status = "on_time" if given_date <= due_date else "delayed"
            return VaccinationStatus(
                vaccine_key=vaccine_key,
                vaccine_type=schedule.vaccine_type,
                dose_number=schedule.dose_number,
                status=status,
                due_date=due_date,
                given_date=given_date,
                description=schedule.description,
            )

        # Vaccine not yet given - check if overdue
        if overdue_date is not None and current_date > overdue_date:
            days_overdue = days_between(overdue_date, current_date)
            return VaccinationStatus(
                vaccine_key=vaccine_key,
                vaccine_type=schedule.vaccine_type,
                dose_number=schedule.dose_number,
                status="overdue",
                due_date=due_date,
                days_overdue=days_overdue,
                description=f"{schedule.description} - {days_overdue} dias em atraso",
            )
        elif current_date >= due_date:
            return VaccinationStatus(
                vaccine_key=vaccine_key,
                vaccine_type=schedule.vaccine_type,
                dose_number=schedule.dose_number,
                status="delayed",
                due_date=due_date,
                description=f"{schedule.description} - Em atraso",
            )

        # Not yet due
        return VaccinationStatus(
            vaccine_key=vaccine_key,
            vaccine_type=schedule.vaccine_type,
            dose_number=schedule.dose_number,
            status="not_due",
            due_date=due_date,
            description=schedule.description,
        )

    def get_next_vaccines_due(
        self,
        birth_date: dt_date,
        current_date: dt_date,
        vaccination_history: list[VaccinationRecordA],
        days_ahead: int = 30,
    ) -> list[VaccinationStatus]:
        """
        Get vaccines that are due or will be due within a specified period.

        Args:
            birth_date: Patient's birth date
            current_date: Current date
            vaccination_history: List of vaccination records
            days_ahead: Look ahead this many days for upcoming vaccines

        Returns:
            List of VaccinationStatus objects for vaccines due soon
        """
        due_vaccines = []
        future_date = current_date + timedelta(days=days_ahead)

        # Create lookup of given vaccines
        given_vaccines = {}
        for record in vaccination_history:
            key = f"{record.vaccine_type}_{record.dose_number}"
            given_vaccines[key] = record.date_given

        for vaccine_key, schedule in self.schedules.items():
            due_date = self.get_due_date(vaccine_key, birth_date)

            # Skip if due date is too far in future
            if due_date > future_date:
                continue

            # Check if this vaccine was already given
            lookup_key = f"{schedule.vaccine_type}_{schedule.dose_number}"
            given_date = given_vaccines.get(lookup_key)

            # Get previous dose date if needed
            previous_dose_date = self._find_previous_dose_date(schedule, vaccination_history)

            status = self.check_vaccination_status(vaccine_key, birth_date, current_date, given_date, previous_dose_date)

            # Include if due, delayed, or overdue
            if status.status in ["delayed", "overdue"] or (status.status == "not_due" and due_date <= future_date):
                due_vaccines.append(status)

        # Sort by due date
        due_vaccines.sort(key=lambda x: x.due_date)
        return due_vaccines

    def generate_complete_schedule(self, birth_date: dt_date, max_age_years: int = 18) -> list[VaccinationStatus]:
        """
        Generate complete vaccination schedule for a patient.

        Args:
            birth_date: Patient's birth date
            max_age_years: Generate schedule up to this age

        Returns:
            List of all scheduled vaccines with due dates
        """
        max_age_days = max_age_years * 365
        schedule_list = []

        for vaccine_key, schedule in self.schedules.items():
            # Skip vaccines beyond max age
            if schedule.min_age_days > max_age_days:
                continue

            due_date = self.get_due_date(vaccine_key, birth_date)

            status = VaccinationStatus(
                vaccine_key=vaccine_key,
                vaccine_type=schedule.vaccine_type,
                dose_number=schedule.dose_number,
                status="not_due",
                due_date=due_date,
                description=schedule.description,
            )
            schedule_list.append(status)

        # Sort by due date
        schedule_list.sort(key=lambda x: x.due_date)
        return schedule_list

    def _find_previous_dose_date(self, schedule: VaccineSchedule, vaccination_history: list[VaccinationRecordA]) -> dt_date | None:
        """
        Find the date of the previous dose in a vaccine series.

        Args:
            schedule: Current vaccine schedule
            vaccination_history: List of vaccination records

        Returns:
            Date of previous dose or None if not found
        """
        if schedule.interval_from_previous is None:
            return None

        # This is a simplified implementation
        # In a full implementation, you would need more sophisticated logic
        # to determine which dose is "previous" in a series
        previous_doses = [record for record in vaccination_history if record.vaccine_type == schedule.vaccine_type]

        if not previous_doses:
            return None

        # Return the most recent dose date
        return max(record.date_given for record in previous_doses)

    def get_vaccine_series_completion(self, vaccine_type: str, vaccination_history: list[VaccinationRecordA]) -> dict[str, int]:
        """
        Get completion status for a vaccine series.

        Args:
            vaccine_type: Type of vaccine to check
            vaccination_history: List of vaccination records

        Returns:
            Dictionary with completion information
        """
        # Count doses given for this vaccine type
        given_doses = [record for record in vaccination_history if record.vaccine_type == vaccine_type]

        # Count expected doses for this vaccine type
        expected_doses = [schedule for schedule in self.schedules.values() if schedule.vaccine_type == vaccine_type]

        return {
            "given": len(given_doses),
            "expected": len(expected_doses),
            "completion_percentage": int(len(given_doses) / len(expected_doses) * 100) if expected_doses else 0,
        }
