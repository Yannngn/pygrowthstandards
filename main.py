import datetime

from src import Calculator, MeasurementGroup, Patient, Plotter


def main():
    patient = Patient(birthday_date=datetime.date(2020, 1, 1), sex="M", gestational_age_weeks=38)
    # calculator.plot_all_standards()
    calculator = Calculator(patient)

    patient.add_measurements(
        MeasurementGroup(
            stature=115.0,
            weight=21.0,
            head_circumference=52.0,
            date=datetime.date(2025, 6, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            table_name="newborn",
            stature=50.0,
            weight=3.5,
            head_circumference=37.0,
            date=datetime.date(2020, 1, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=55.0,
            weight=4.0,
            head_circumference=38.0,
            date=datetime.date(2020, 2, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=60.0,
            weight=5.0,
            head_circumference=41.5,
            date=datetime.date(2020, 4, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=65.0,
            weight=6.5,
            head_circumference=43.0,
            date=datetime.date(2020, 6, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=70.0,
            weight=8.0,
            head_circumference=44.0,
            date=datetime.date(2020, 8, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=75.0,
            weight=9.0,
            head_circumference=45.0,
            date=datetime.date(2020, 10, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=80.0,
            weight=10.0,
            head_circumference=46.0,
            date=datetime.date(2021, 1, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=85.0,
            weight=11.0,
            head_circumference=47.0,
            date=datetime.date(2021, 7, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=88.0,
            weight=12.0,
            head_circumference=48.0,
            date=datetime.date(2021, 12, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=92.0,
            weight=13.0,
            head_circumference=49.0,
            date=datetime.date(2022, 4, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=98.0,
            weight=15.0,
            head_circumference=50.0,
            date=datetime.date(2023, 1, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=104.0,
            weight=17.0,
            head_circumference=51.0,
            date=datetime.date(2024, 1, 1),
        )
    )
    patient.add_measurements(
        MeasurementGroup(
            stature=110.0,
            weight=19.0,
            head_circumference=52.0,
            date=datetime.date(2024, 7, 1),
        )
    )
    calculator.calculate_all()

    plotter = Plotter(patient)
    for age_group in ["0-2", "2-5", "5-10", "10-19", "newborn"]:
        for measurement_type in ["stature", "weight", "head_circumference", "body_mass_index"]:
            try:
                plotter.plot(age_group, measurement_type, output_path=f"results/user_table_{age_group}_{measurement_type}.png")
            except Exception as e:
                print(f"Error plotting {age_group} {measurement_type}: {e}")


if __name__ == "__main__":
    main()
