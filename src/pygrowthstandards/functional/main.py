from pygrowthstandards import functional as F


def main():
    print(f"{F.zscore('stature', 50, 'F', age_days=0, gestational_age=280):.2f}")
    print(f"{F.zscore('weight', 5, 'F', age_days=30):.2f}")
    print(f"{F.zscore('head_circumference', 40, 'F', age_days=180):.2f}")
    print(f"{F.zscore('stature', 80, 'F', age_days=365):.2f}")
    print(f"{F.zscore('weight', 12, 'F', age_days=730):.2f}")
    print(f"{F.zscore('head_circumference', 48, 'F', age_days=1460):.2f}")

    calculator_1 = F.calculator("F", birth_date="2020-01-01")

    print(f"{calculator_1('stature', 50, measurement_date='2020-01-01'):.2f}")
    print(f"{calculator_1('weight', 3.5, measurement_date='2020-01-15'):.2f}")
    print(f"{calculator_1('head_circumference', 35, measurement_date='2020-02-01'):.2f}")
    print(f"{calculator_1('weight', 6, measurement_date='2020-03-01'):.2f}")
    print(f"{calculator_1('stature', 60, measurement_date='2020-06-01'):.2f}")
    print(f"{calculator_1('weight', 9, measurement_date='2020-12-01'):.2f}")
    print(f"{calculator_1('head_circumference', 45, measurement_date='2021-01-01'):.2f}")


if __name__ == "__main__":
    main()
