def age_from_birthday(day: int, month: int, year: int) -> tuple[int, int, int]:
    """Calculate age in years, months, and days from a given birthday.

    Args:
        day (int): Day of the month of the birthday.
        month (int): Month of the birthday.
        year (int): Year of the birthday.

    Returns:
        tuple[int, int, int]: Age in years, months, and days.
    """
    from datetime import datetime

    today = datetime.now()
    birth_date = datetime(year, month, day)

    age_years = today.year - birth_date.year
    age_months = today.month - birth_date.month
    age_days = today.day - birth_date.day

    if age_days < 0:
        age_months -= 1
        age_days += (birth_date.replace(month=birth_date.month + 1) - birth_date).days

    if age_months < 0:
        age_years -= 1
        age_months += 12

    return age_years, age_months, age_days


def gestational_age_from_edd(
    day: int, month: int, year: int, gestational_age_days: int = 280
) -> tuple[int, int]:
    """Calculate gestational age in weeks and days from a given expected delivery date (EDD), using the 40W standard.

    Args:
        day (int): Day of the expected delivery date.
        month (int): Month of the expected delivery date.
        year (int): Year of the expected delivery date.

    Returns:
        tuple[int, int]: Gestational age in weeks and days.
    """
    from datetime import datetime

    today = datetime.now()
    edd_date = datetime(year, month, day)

    # Gestational age is 40 weeks at EDD
    delta = edd_date - today
    total_days_until_edd = delta.days

    gestational_age_days = 280 - total_days_until_edd  # 280 days = 40 weeks
    if gestational_age_days < 0:
        # EDD is in the past, gestational age > 40 weeks
        gestational_age_days = 280

    weeks = gestational_age_days // 7
    days = gestational_age_days % 7

    return weeks, days
