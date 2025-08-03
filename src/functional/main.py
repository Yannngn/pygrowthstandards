from .. import functional as F


def main():
    print(F.zscore("stature", 50, "F", age_days=0, gestational_age=280))
    print(F.zscore("weight", 5, "F", age_days=30))
    print(F.zscore("head_circumference", 40, "F", age_days=180))
    print(F.zscore("stature", 80, "F", age_days=365))
    print(F.zscore("weight", 12, "F", age_days=730))
    print(F.zscore("head_circumference", 48, "F", age_days=1460))


if __name__ == "__main__":
    main()
