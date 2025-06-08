import datetime

from src import Calculator
from src import functional as F


def main():
    calculator = Calculator.from_kid(birthday_date=datetime.date(2020, 1, 1), sex="M")

    print(calculator.kid)

    calculator.add_measurement(
        length_height=115.0,
        weight=21.0,
        head_circumference=52.0,
        date=datetime.date(2025, 6, 1),
    )
    calculator.add_measurement(
        length_height=50.0,
        weight=3.5,
        head_circumference=37.0,
        date=datetime.date(2020, 1, 1),
    )
    calculator.add_measurement(
        length_height=55.0,
        weight=4.0,
        head_circumference=38.0,
        date=datetime.date(2020, 2, 1),
    )
    calculator.add_measurement(
        length_height=60.0,
        weight=5.0,
        head_circumference=41.5,
        date=datetime.date(2020, 4, 1),
    )
    calculator.add_measurement(
        length_height=65.0,
        weight=6.5,
        head_circumference=43.0,
        date=datetime.date(2020, 6, 1),
    )
    calculator.add_measurement(
        length_height=70.0,
        weight=8.0,
        head_circumference=44.0,
        date=datetime.date(2020, 8, 1),
    )
    calculator.add_measurement(
        length_height=75.0,
        weight=9.0,
        head_circumference=45.0,
        date=datetime.date(2020, 10, 1),
    )
    calculator.add_measurement(
        length_height=80.0,
        weight=10.0,
        head_circumference=46.0,
        date=datetime.date(2021, 1, 1),
    )
    calculator.add_measurement(
        length_height=85.0,
        weight=11.0,
        head_circumference=47.0,
        date=datetime.date(2021, 7, 1),
    )
    calculator.add_measurement(
        length_height=88.0,
        weight=12.0,
        head_circumference=48.0,
        date=datetime.date(2021, 12, 1),
    )
    calculator.add_measurement(
        length_height=92.0,
        weight=13.0,
        head_circumference=49.0,
        date=datetime.date(2022, 4, 1),
    )
    calculator.add_measurement(
        length_height=98.0,
        weight=15.0,
        head_circumference=50.0,
        date=datetime.date(2023, 1, 1),
    )
    calculator.add_measurement(
        length_height=104.0,
        weight=17.0,
        head_circumference=51.0,
        date=datetime.date(2024, 1, 1),
    )
    calculator.add_measurement(
        length_height=110.0,
        weight=19.0,
        head_circumference=52.0,
        date=datetime.date(2024, 7, 1),
    )

    print(calculator.display_results())

    for m in ["height", "length", "weight", "head_circumference", "bmi"]:
        calculator.table_plot(m, output_path=f"results/{m}_plot.png")  # type: ignore
        calculator.plot_measurements(m, output_path=f"results/{m}_measurements_plot.png")  # type: ignore

    print(
        F.zscore(
            "height",
            115,
            "M",
            birth_date=datetime.date(2020, 1, 1),
            measurement_date=datetime.date(2025, 6, 1),
        )
    )


if __name__ == "__main__":
    main()
