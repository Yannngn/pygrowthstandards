from age import age_from_birthday, gestational_age_from_edd


def age_weeks_to_days(age_in_weeks: int, days: int = 0) -> int:
    """Convert age in weeks to days.

    Args:
        age_in_weeks (int): Age in weeks.
        days (int, optional): Additional days to add. Defaults to 0.

    Returns:
        int: Total age in days.
    """
    return age_in_weeks * 7 + days


def age_months_to_days(age_in_months: int, days: int = 0) -> int:
    """Convert age in months to days.

    Args:
        age_in_months (int): Age in months.
        days (int, optional): Additional days to add. Defaults to 0.

    Returns:
        int: Total age in days.
    """
    return int(age_in_months * 30.44 + days)


def age_years_to_days(age_in_years: int, months: int = 0, days: int = 0) -> int:
    """Convert age in years to days.

    Args:
        age_in_years (int): Age in years.
        months (int, optional): Additional months to add. Defaults to 0.
        days (int, optional): Additional days to add. Defaults to 0.

    Returns:
        int: Total age in days.
    """
    return int(age_in_years * 365.25 + months * 30.44 + days)


def age_from_birthday_in_days(day: int, month: int, year: int) -> int:
    """Calculate age in days from a given birthday.

    Args:
        day (int): Day of the month of the birthday.
        month (int): Month of the birthday.
        year (int): Year of the birthday.

    Returns:
        int: Age in days.
    """
    age_years, age_months, age_days = age_from_birthday(day, month, year)
    return age_years_to_days(age_years, age_months, age_days)


def gestational_age_from_edd_in_days(
    day: int, month: int, year: int, gestational_age_days: int = 280
) -> int:
    """Calculate gestational age in days from a given expected delivery date (EDD), using the 40W standard.

    Args:
        day (int): Day of the expected delivery date.
        month (int): Month of the expected delivery date.
        year (int): Year of the expected delivery date.
        gestational_age_days (int, optional): Gestational age in days. Defaults to 280.

    Returns:
        int: Gestational age in days.
    """
    weeks, days = gestational_age_from_edd(day, month, year, gestational_age_days)

    return weeks * 7 + days
