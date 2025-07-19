import datetime

from src import Calculator


def main():
    calculator = Calculator.from_child(birthday_date=datetime.date(2020, 1, 1), sex="M", gestational_age_weeks=40)
    # calculator.plot_all_standards()

    print(calculator.child)

    calculator.add_measurement(
        stature=115.0,
        weight=21.0,
        head_circumference=52.0,
        date=datetime.date(2025, 6, 1),
    )
    calculator.add_measurement(
        stature=50.0,
        weight=3.5,
        head_circumference=37.0,
        date=datetime.date(2020, 1, 1),
    )
    calculator.add_measurement(
        stature=55.0,
        weight=4.0,
        head_circumference=38.0,
        date=datetime.date(2020, 2, 1),
    )
    calculator.add_measurement(
        stature=60.0,
        weight=5.0,
        head_circumference=41.5,
        date=datetime.date(2020, 4, 1),
    )
    calculator.add_measurement(
        stature=65.0,
        weight=6.5,
        head_circumference=43.0,
        date=datetime.date(2020, 6, 1),
    )
    calculator.add_measurement(
        stature=70.0,
        weight=8.0,
        head_circumference=44.0,
        date=datetime.date(2020, 8, 1),
    )
    calculator.add_measurement(
        stature=75.0,
        weight=9.0,
        head_circumference=45.0,
        date=datetime.date(2020, 10, 1),
    )
    calculator.add_measurement(
        stature=80.0,
        weight=10.0,
        head_circumference=46.0,
        date=datetime.date(2021, 1, 1),
    )
    calculator.add_measurement(
        stature=85.0,
        weight=11.0,
        head_circumference=47.0,
        date=datetime.date(2021, 7, 1),
    )
    calculator.add_measurement(
        stature=88.0,
        weight=12.0,
        head_circumference=48.0,
        date=datetime.date(2021, 12, 1),
    )
    calculator.add_measurement(
        stature=92.0,
        weight=13.0,
        head_circumference=49.0,
        date=datetime.date(2022, 4, 1),
    )
    calculator.add_measurement(
        stature=98.0,
        weight=15.0,
        head_circumference=50.0,
        date=datetime.date(2023, 1, 1),
    )
    calculator.add_measurement(
        stature=104.0,
        weight=17.0,
        head_circumference=51.0,
        date=datetime.date(2024, 1, 1),
    )
    calculator.add_measurement(
        stature=110.0,
        weight=19.0,
        head_circumference=52.0,
        date=datetime.date(2024, 7, 1),
    )

    print(calculator.display_results())

    # calculator.plot_all_measurements()


if __name__ == "__main__":
    main()
