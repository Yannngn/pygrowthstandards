"""
Immunization/Vaccination configuration based on Brazilian Ministry of Health recommendations.

This module provides configuration for the Brazilian National Immunization Calendar,
including vaccine types, schedules, and validation rules.

References:
- Calendário Nacional de Vacinação (2024): https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/calendario-nacional-de-vacinacao
- Manual dos Centros de Referência para Imunobiológicos Especiais (CRIE)
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pygrowthstandards.utils.date_utils import months_to_days, years_to_days


class VaccineType(StrEnum):
    """Vaccine types following Brazilian Ministry of Health calendar."""

    BCG = "bcg"
    HEPATITIS_B = "hepatitis_b"
    VIP_VOP = "vip_vop"  # Polio vaccine
    PENTA = "penta"  # DTP + Hib + HepB
    PNEUMOCOCCAL = "pneumococcal"
    ROTAVIRUS = "rotavirus"
    MENINGOCOCCAL_C = "meningococcal_c"
    YELLOW_FEVER = "yellow_fever"
    SRC = "src"  # Measles, Rubella, Mumps (Tríplice viral)
    HEPATITIS_A = "hepatitis_a"
    DTP = "dtp"  # Diphtheria, Tetanus, Pertussis
    VARICELLA = "varicella"
    MENINGOCOCCAL_ACWY = "meningococcal_acwy"
    HPV = "hpv"  # Human Papillomavirus
    DT = "dt"  # Adult Diphtheria and Tetanus
    INFLUENZA = "influenza"
    COVID19 = "covid19"


class VaccinationStatus(StrEnum):
    """Vaccination status for tracking compliance."""

    ON_TIME = "on_time"
    DELAYED = "delayed"
    OVERDUE = "overdue"
    CONTRAINDICATED = "contraindicated"
    NOT_DUE = "not_due"


class DoseNumber(StrEnum):
    """Dose numbers and types."""

    BIRTH = "birth"
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    FOURTH = "4th"
    FIFTH = "5th"
    BOOSTER = "booster"
    ANNUAL = "annual"


# Type aliases for better type hints
VaccineTypeType = Literal[
    "bcg",
    "hepatitis_b",
    "vip_vop",
    "penta",
    "pneumococcal",
    "rotavirus",
    "meningococcal_c",
    "yellow_fever",
    "src",
    "hepatitis_a",
    "dtp",
    "varicella",
    "meningococcal_acwy",
    "hpv",
    "dt",
    "influenza",
    "covid19",
]

VaccinationStatusType = Literal["on_time", "delayed", "overdue", "contraindicated", "not_due"]

DoseNumberType = Literal["birth", "1st", "2nd", "3rd", "4th", "5th", "booster", "annual"]


@dataclass(frozen=True)
class VaccineSchedule:
    """
    Configuration for vaccine schedule with timing requirements.

    Attributes:
    - vaccine_type: Type of vaccine
    - dose_number: Which dose in the series
    - limits: Tuple of (min_age_days, max_age_days) where max_age_days can be None if no upper limit
    - interval_from_previous_days: Minimum interval from previous dose (None for first dose)
    - description: Human-readable description in Portuguese
    """

    vaccine_type: VaccineTypeType
    dose_number: DoseNumberType
    limits: tuple[int, int | None]
    interval_from_previous: int | None
    description: str

    def contains_age(self, age: int) -> bool:
        if self.limits[1] is None:
            return age >= self.limits[0]

        return self.limits[0] <= age <= self.limits[1]

    def due_age(self, previous_dose_age: int | None = None):
        if self.interval_from_previous is None:
            return self.limits[0]
        if previous_dose_age is None:
            raise ValueError("previous_dose_age must be provided for non-initial doses")

        return max(previous_dose_age + self.interval_from_previous, self.limits[0])


# Brazilian Ministry of Health Vaccination Calendar (2024)
# Based on: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/calendario-nacional-de-vacinacao

VACCINE_SCHEDULES: dict[str, VaccineSchedule] = {
    # BCG - Birth
    "bcg_birth": VaccineSchedule("bcg", "birth", (0, months_to_days(3)), None, "BCG - Ao nascer"),
    # Hepatitis B - Birth and series
    "hepatitis_b_birth": VaccineSchedule("hepatitis_b", "birth", (0, months_to_days(1)), None, "Hepatite B - Ao nascer"),
    "hepatitis_b_2nd": VaccineSchedule("hepatitis_b", "2nd", (months_to_days(1), months_to_days(4)), months_to_days(1), "Hepatite B - 1 mês"),
    "hepatitis_b_3rd": VaccineSchedule("hepatitis_b", "3rd", (months_to_days(6), months_to_days(9)), months_to_days(2), "Hepatite B - 6 meses"),
    # VIP/VOP (Polio) - 2, 4, 6 months, 15 months, 4 years
    "vip_vop_1st": VaccineSchedule("vip_vop", "1st", (months_to_days(2), months_to_days(4)), None, "VIP - 2 meses"),
    "vip_vop_2nd": VaccineSchedule("vip_vop", "2nd", (months_to_days(4), months_to_days(6)), months_to_days(2), "VIP - 4 meses"),
    "vip_vop_3rd": VaccineSchedule("vip_vop", "3rd", (months_to_days(6), months_to_days(8)), months_to_days(2), "VOP - 6 meses"),
    "vip_vop_booster_1": VaccineSchedule("vip_vop", "booster", (months_to_days(15), months_to_days(20)), months_to_days(6), "VOP - 15 meses"),
    "vip_vop_booster_2": VaccineSchedule("vip_vop", "booster", (years_to_days(4), years_to_days(5)), years_to_days(1), "VOP - 4 anos"),
    # Penta (DTP + Hib + HepB) - 2, 4, 6 months
    "penta_1st": VaccineSchedule("penta", "1st", (months_to_days(2), months_to_days(4)), None, "Pentavalente - 2 meses"),
    "penta_2nd": VaccineSchedule("penta", "2nd", (months_to_days(4), months_to_days(6)), months_to_days(2), "Pentavalente - 4 meses"),
    "penta_3rd": VaccineSchedule("penta", "3rd", (months_to_days(6), months_to_days(8)), months_to_days(2), "Pentavalente - 6 meses"),
    # Pneumococcal - 2, 4, 12 months
    "pneumococcal_1st": VaccineSchedule("pneumococcal", "1st", (months_to_days(2), months_to_days(4)), None, "Pneumocócica 10V - 2 meses"),
    "pneumococcal_2nd": VaccineSchedule(
        "pneumococcal", "2nd", (months_to_days(4), months_to_days(6)), months_to_days(2), "Pneumocócica 10V - 4 meses"
    ),
    "pneumococcal_booster": VaccineSchedule(
        "pneumococcal", "booster", (months_to_days(12), months_to_days(15)), months_to_days(6), "Pneumocócica 10V - 12 meses"
    ),
    # Rotavirus - 2, 4 months
    "rotavirus_1st": VaccineSchedule("rotavirus", "1st", (months_to_days(2), 105), None, "Rotavírus - 2 meses"),
    "rotavirus_2nd": VaccineSchedule("rotavirus", "2nd", (months_to_days(4), months_to_days(7)), months_to_days(1), "Rotavírus - 4 meses"),
    # Meningococcal C - 3, 5, 12 months
    "meningococcal_c_1st": VaccineSchedule("meningococcal_c", "1st", (months_to_days(3), months_to_days(5)), None, "Meningocócica C - 3 meses"),
    "meningococcal_c_2nd": VaccineSchedule(
        "meningococcal_c", "2nd", (months_to_days(5), months_to_days(7)), months_to_days(2), "Meningocócica C - 5 meses"
    ),
    "meningococcal_c_booster": VaccineSchedule(
        "meningococcal_c", "booster", (months_to_days(12), months_to_days(15)), months_to_days(6), "Meningocócica C - 12 meses"
    ),
    # Yellow Fever - 9 months
    "yellow_fever_1st": VaccineSchedule("yellow_fever", "1st", (months_to_days(9), months_to_days(12)), None, "Febre Amarela - 9 meses"),
    # SRC (Tríplice viral) - 12 months, 15 months
    "src_1st": VaccineSchedule("src", "1st", (months_to_days(12), months_to_days(15)), None, "Tríplice viral - 12 meses"),
    "src_2nd": VaccineSchedule("src", "2nd", (months_to_days(15), months_to_days(20)), months_to_days(3), "Tríplice viral - 15 meses"),
    # Hepatitis A - 15 months
    "hepatitis_a_1st": VaccineSchedule("hepatitis_a", "1st", (months_to_days(15), months_to_days(20)), None, "Hepatite A - 15 meses"),
    # DTP - 15 months, 4 years
    "dtp_1st": VaccineSchedule("dtp", "1st", (months_to_days(15), months_to_days(20)), None, "DTP - 15 meses"),
    "dtp_2nd": VaccineSchedule("dtp", "2nd", (years_to_days(4), years_to_days(5)), years_to_days(1), "DTP - 4 anos"),
    # Varicella - 15 months, 4 years
    "varicella_1st": VaccineSchedule("varicella", "1st", (months_to_days(15), months_to_days(20)), None, "Varicela - 15 meses"),
    "varicella_2nd": VaccineSchedule("varicella", "2nd", (years_to_days(4), years_to_days(5)), years_to_days(1), "Varicela - 4 anos"),
    # Meningococcal ACWY - 11-12 years
    "meningococcal_acwy_1st": VaccineSchedule(
        "meningococcal_acwy", "1st", (years_to_days(11), years_to_days(12)), None, "Meningocócica ACWY - 11 anos"
    ),
    # HPV - 9-14 years (2 doses)
    "hpv_1st": VaccineSchedule("hpv", "1st", (years_to_days(9), years_to_days(14)), None, "HPV - 9 anos"),
    "hpv_2nd": VaccineSchedule(
        "hpv", "2nd", (years_to_days(9) + months_to_days(6), years_to_days(14) + months_to_days(6)), months_to_days(6), "HPV - 2ª dose"
    ),
    # Annual vaccines
    "influenza_annual": VaccineSchedule("influenza", "annual", (months_to_days(6), None), None, "Influenza - Anual a partir de 6 meses"),
    "covid19_annual": VaccineSchedule("covid19", "annual", (years_to_days(5), None), None, "COVID-19 - Anual a partir de 5 anos"),
}


# Vaccine groups for easier management
VACCINE_GROUPS: dict[str, list[str]] = {
    "newborn": ["bcg_birth", "hepatitis_b_birth"],
    "0-2": [
        "vip_vop_1st",
        "vip_vop_2nd",
        "vip_vop_3rd",
        "penta_1st",
        "penta_2nd",
        "penta_3rd",
        "pneumococcal_1st",
        "pneumococcal_2nd",
        "rotavirus_1st",
        "rotavirus_2nd",
        "meningococcal_c_1st",
        "meningococcal_c_2nd",
    ],
    "2-5": [
        "pneumococcal_booster",
        "meningococcal_c_booster",
        "yellow_fever_1st",
        "src_1st",
        "src_2nd",
        "hepatitis_a_1st",
        "dtp_1st",
        "varicella_1st",
        "hepatitis_b_3rd",
    ],
    "5-10": ["vip_vop_booster_2", "dtp_2nd", "varicella_2nd"],
    "10-19": ["meningococcal_acwy_1st", "hpv_1st", "hpv_2nd"],
}

# Backward compatibility
VACCINE_TYPE_CHOICES = frozenset([e.value for e in VaccineType])
VACCINATION_STATUS_CHOICES = frozenset([e.value for e in VaccinationStatus])
DOSE_NUMBER_CHOICES = frozenset([e.value for e in DoseNumber])
