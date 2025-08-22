import datetime

from .measurement import MeasurementGroup
from .patient import Patient
from .plotter import Plotter


def main():
    # Create a patient (12 years old)
    patient = Patient(
        sex="M",
        birthday_date=datetime.date(2012, 6, 1),
        gestational_age_weeks=40,
        gestational_age_days=0,
    )

    # Generate 20 measurement groups, more frequent in early years
    measurement_dates = [
        datetime.date(2012, 6, 1),  # birth
        datetime.date(2012, 7, 1),  # 1 month
        datetime.date(2012, 8, 1),  # 2 months
        datetime.date(2012, 9, 1),  # 3 months
        datetime.date(2012, 12, 1),  # 6 months
        datetime.date(2013, 6, 1),  # 1 year
        datetime.date(2014, 6, 1),  # 2 years
        datetime.date(2015, 6, 1),  # 3 years
        datetime.date(2016, 6, 1),  # 4 years
        datetime.date(2017, 6, 1),  # 5 years
        datetime.date(2018, 6, 1),  # 6 years
        datetime.date(2019, 6, 1),  # 7 years
        datetime.date(2020, 6, 1),  # 8 years
        datetime.date(2021, 6, 1),  # 9 years
        datetime.date(2022, 6, 1),  # 10 years
        datetime.date(2023, 6, 1),  # 11 years
        datetime.date(2024, 1, 1),  # 11.5 years
        datetime.date(2024, 4, 1),  # 11.8 years
        datetime.date(2024, 6, 1),  # 12 years
        datetime.date(2024, 6, 15),  # 12 years, 2 weeks
    ]

    # Example data: values are illustrative and should be replaced with real measurements if available
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
        mg = MeasurementGroup(date=date, stature=stature, weight=weight, head_circumference=hc)
        patient.add_measurements(mg)

    # Calculate z-scores for all measurements
    patient.calculate_all()

    plotter = Plotter(patient)
    plotter.plot(
        age_group="0-2",
        measurement_type="stature",
        show=False,
        output_path="results/user_table_0_2_stature.png",
    )
    plotter.plot(
        age_group="2-5",
        measurement_type="stature",
        show=False,
        output_path="results/user_table_2_5_stature.png",
    )
    plotter.plot(
        age_group="5-10",
        measurement_type="stature",
        show=False,
        output_path="results/user_table_5_10_stature.png",
    )
    plotter.plot(
        age_group="10-19",
        measurement_type="stature",
        show=False,
        output_path="results/user_table_10_19_stature.png",
    )

    print(patient.display_measurements())


if __name__ == "__main__":
    main()
