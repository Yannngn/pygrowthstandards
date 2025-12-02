"""
Vaccination record classes for tracking immunization history.

This module provides classes to represent vaccination records and vaccination status
for individual patients in the immunization tracking system.
"""

from dataclasses import dataclass, field
from datetime import date as dt_date
from datetime import datetime as dt_datetime

from pygrowthstandards.utils.date_utils import handle_date

from ..config.immunization import (
    VACCINE_TYPE_CHOICES,
    DoseNumberType,
    VaccinationStatusType,
    VaccineTypeType,
)


@dataclass
class VaccinationRecord:
    name: VaccineTypeType
    dose_number: DoseNumberType
    date: dt_date | dt_datetime = field(default_factory=dt_datetime.now)

    status: VaccinationStatusType = field(init=False)

    def __post_init__(self):
        self.date = handle_date(self.date)

        if self.name not in VACCINE_TYPE_CHOICES:
            raise ValueError(f"Invalid vaccine type: {self.name}")

    def validate(self, age_days: int):
        self.status = ""


@dataclass
class VaccinationRecordGroup:
    immunization: list[VaccinationRecord] = field(default_factory=list)

    date: dt_date | dt_datetime = field(default_factory=dt_datetime.now)

    def __post_init__(self):
        self.date = handle_date(self.date)

    def validate(self, age_days: int):
        for vac in self.immunization:
            vac.validate(age_days)

    @classmethod
    def from_vaccination_list(
        cls,
        vaccination_list: list[VaccinationRecord],
        date: dt_date | dt_datetime | None = None,
    ) -> "VaccinationRecordGroup":
        if date is None:
            date = dt_datetime.now()

        return cls(immunization=vaccination_list, date=date)


@dataclass
class VaccinationRecordA:
    """
    Represents a single vaccination record for a patient.

    Attributes:
    - vaccine_type: Type of vaccine administered
    - dose_number: Which dose in the series
    - date_given: Date when vaccine was administered
    - batch_number: Vaccine batch/lot number (optional)
    - manufacturer: Vaccine manufacturer (optional)
    - healthcare_provider: Who administered the vaccine (optional)
    - notes: Additional notes about the vaccination (optional)
    """

    vaccine_type: VaccineTypeType
    dose_number: DoseNumberType
    date_given: dt_date
    batch_number: str | None = None
    manufacturer: str | None = None
    healthcare_provider: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert vaccination record to dictionary."""
        return {
            "vaccine_type": self.vaccine_type,
            "dose_number": self.dose_number,
            "date_given": self.date_given,
            "batch_number": self.batch_number,
            "manufacturer": self.manufacturer,
            "healthcare_provider": self.healthcare_provider,
            "notes": self.notes,
        }

    def __str__(self) -> str:
        """String representation of vaccination record."""
        return f"{self.vaccine_type} ({self.dose_number}) - {self.date_given}"


@dataclass
class VaccinationStatus:
    """
    Represents the vaccination status for a specific vaccine dose.

    Attributes:
    - vaccine_key: Key from vaccine schedule (e.g., "bcg_birth")
    - vaccine_type: Type of vaccine
    - dose_number: Which dose in the series
    - status: Current vaccination status
    - due_date: When the vaccine is/was due
    - given_date: When the vaccine was actually given (if applicable)
    - days_overdue: Number of days overdue (if applicable)
    - description: Human-readable description
    """

    vaccine_key: str
    vaccine_type: VaccineTypeType
    dose_number: DoseNumberType
    status: VaccinationStatusType
    due_date: dt_date
    given_date: dt_date | None = None
    days_overdue: int | None = None
    description: str = ""

    def to_dict(self) -> dict:
        """Convert vaccination status to dictionary."""
        return {
            "vaccine_key": self.vaccine_key,
            "vaccine_type": self.vaccine_type,
            "dose_number": self.dose_number,
            "status": self.status,
            "due_date": self.due_date,
            "given_date": self.given_date,
            "days_overdue": self.days_overdue,
            "description": self.description,
        }

    def __str__(self) -> str:
        """String representation of vaccination status."""
        status_map = {
            "on_time": "Em dia",
            "delayed": "Em atraso",
            "overdue": "Vencida",
            "contraindicated": "Contraindicada",
            "not_due": "Não devido ainda",
        }
        status_str = status_map.get(self.status, self.status)

        if self.given_date:
            return f"{self.description} - {status_str} (Aplicada em {self.given_date})"
        elif self.days_overdue:
            return f"{self.description} - {status_str} ({self.days_overdue} dias)"
        else:
            return f"{self.description} - {status_str} (Devido em {self.due_date})"

    @property
    def is_completed(self) -> bool:
        """Check if vaccination is completed."""
        return self.given_date is not None and self.status in ["on_time", "delayed"]

    @property
    def needs_attention(self) -> bool:
        """Check if vaccination needs attention (overdue or contraindicated)."""
        return self.status in ["overdue", "contraindicated"]
