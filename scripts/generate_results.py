import datetime
from pathlib import Path
from typing import cast

import matplotlib
from matplotlib.figure import Figure

from pygrowthstandards.oop.patient import Patient

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402 (must import after backend set)

from pygrowthstandards.oop.builders import PatientBuilder

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def build_sample_patient():
    builder = PatientBuilder().with_sex("M").born_on(datetime.date(2012, 6, 1)).gestational_age(weeks=40, days=0)

    patient = builder.build().patient

    measurement_dates = [
        datetime.date(2012, 6, 1),
        datetime.date(2012, 7, 1),
        datetime.date(2012, 8, 1),
        datetime.date(2012, 9, 1),
        datetime.date(2012, 12, 1),
        datetime.date(2013, 6, 1),
        datetime.date(2014, 6, 1),
        datetime.date(2015, 6, 1),
        datetime.date(2016, 6, 1),
        datetime.date(2017, 6, 1),
        datetime.date(2018, 6, 1),
        datetime.date(2019, 6, 1),
        datetime.date(2020, 6, 1),
        datetime.date(2021, 6, 1),
        datetime.date(2022, 6, 1),
        datetime.date(2023, 6, 1),
        datetime.date(2024, 1, 1),
        datetime.date(2024, 4, 1),
        datetime.date(2024, 6, 1),
        datetime.date(2024, 6, 15),
    ]

    statures = [
        51.0,
        54.0,
        57.0,
        60.0,
        65.0,
        75.0,
        87.0,
        96.0,
        104.0,
        111.0,
        117.0,
        123.0,
        129.0,
        134.0,
        139.0,
        144.0,
        146.0,
        148.0,
        150.0,
        150.5,
    ]
    weights = [
        3.4,
        4.5,
        5.5,
        6.2,
        7.5,
        9.5,
        12.5,
        14.5,
        16.5,
        18.5,
        21.0,
        24.0,
        27.0,
        30.0,
        33.0,
        36.0,
        37.0,
        38.0,
        39.0,
        39.2,
    ]
    head_circumferences = [
        35.0,
        37.0,
        39.0,
        40.5,
        42.0,
        45.0,
        48.0,
        49.0,
        50.0,
        51.0,
        52.0,
        52.5,
        53.0,
        53.5,
        54.0,
        54.5,
        54.7,
        54.8,
        55.0,
        55.0,
    ]

    for date, stature, weight, hc in zip(measurement_dates, statures, weights, head_circumferences, strict=True):
        patient.measured_at(date, weight=weight, stature=stature, head_circumference=hc)

    return patient


def build_newborn_patient(gestational_weeks, gestational_days, birth_date, weight, stature, head_circumference):
    builder = PatientBuilder().with_sex("F").born_on(birth_date).gestational_age(weeks=gestational_weeks, days=gestational_days)

    patient = builder.build().patient
    patient.measured_at(birth_date, weight=weight, stature=stature, head_circumference=head_circumference)
    return patient


def save_plot(patient: Patient, age_group, measurement_type, filename, dpi=150):
    ax = patient.plot(age_group=age_group, measurement_type=measurement_type, show=False, output_path="")
    output_path = RESULTS_DIR / filename
    cast(Figure, ax.figure).savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(cast(Figure, ax.figure))


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    patient = build_sample_patient()

    save_plot(patient, "0-2", "stature", "stature_0_2.png")
    save_plot(patient, "0-2", "weight", "weight_0_2.png")
    save_plot(patient, "0-2", "head_circumference", "head_circumference_0_2.png")
    save_plot(patient, "10-19", "stature", "stature_10_19.png")

    newborn_patient = build_newborn_patient(
        gestational_weeks=38,
        gestational_days=0,
        birth_date=datetime.date(2024, 6, 1),
        weight=3.2,
        stature=50.0,
        head_circumference=34.0,
    )
    save_plot(newborn_patient, "newborn", "weight", "weight_newborn.png")

    save_plot(newborn_patient, "newborn", "weight", "weight_newborn.png")

    very_preterm_patient = build_newborn_patient(
        gestational_weeks=30,
        gestational_days=0,
        birth_date=datetime.date(2024, 6, 1),
        weight=1.4,
        stature=40.0,
        head_circumference=29.0,
    )
    save_plot(very_preterm_patient, "very_preterm_newborn", "weight", "weight_very_preterm_newborn.png")


if __name__ == "__main__":
    main()
