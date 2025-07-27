import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)


from src import functional as F


def main():
    print(f"{F.zscore('stature', 50, 'F', age_days=0, gestational_age=280):.2f}")
    print(f"{F.zscore('weight', 5, 'F', age_days=30):.2f}")
    print(f"{F.zscore('head_circumference', 40, 'F', age_days=180):.2f}")
    print(f"{F.zscore('stature', 80, 'F', age_days=365):.2f}")
    print(f"{F.zscore('weight', 12, 'F', age_days=730):.2f}")
    print(f"{F.zscore('head_circumference', 48, 'F', age_days=1460):.2f}")


if __name__ == "__main__":
    main()
