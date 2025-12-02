from datetime import date as dt_date
from datetime import datetime as dt_datetime
from datetime import timedelta

import pytz

from pygrowthstandards.utils.constants import MONTH, WEEK, YEAR


def handle_date(date: dt_date | dt_datetime | None, tz: str = "America/Fortaleza") -> dt_datetime:
    """
    Transforms a date or datetime into a timezone-aware datetime object.

    Parameters
    ----------
    date : dt_date | dt_datetime
        The input date or datetime to be transformed.
    tz : str
        The timezone to apply. Defaults to 'America/Fortaleza'.

    Returns
    -------
    dt_datetime
        A timezone-aware datetime object.
    """

    timezone = pytz.timezone(tz)

    if date is None:
        return dt_datetime.now(timezone)

    if isinstance(date, dt_date) and not isinstance(date, dt_datetime):
        # Convert date to datetime
        date = dt_datetime.combine(date, dt_datetime.min.time())

    # Make the datetime timezone-aware
    if date.tzinfo is None:
        return timezone.localize(date)
    else:
        return date.astimezone(timezone)


# Immunization date utility functions


def days_between(start_date: dt_date, end_date: dt_date) -> int:
    """
    Calculate the number of days between two dates.

    Args:
        start_date: Starting date
        end_date: Ending date

    Returns:
        Number of days between dates (can be negative if end_date < start_date)
    """
    return (end_date - start_date).days


def add_days(date: dt_date, days: int) -> dt_date:
    """
    Add a number of days to a date.

    Args:
        date: Starting date
        days: Number of days to add

    Returns:
        New date after adding days
    """
    return date + timedelta(days=days)


def weeks_to_days(weeks: int | float) -> int:
    """
    Convert weeks to days.

    Args:
        weeks: Number of weeks

    Returns:
        Number of days
    """
    return int(weeks * WEEK)


def months_to_days(months: int | float) -> int:
    """
    Convert months to approximate days (using 30.44 days per month).

    Args:
        months: Number of months

    Returns:
        Approximate number of days
    """
    return int(months * MONTH)


def years_to_days(years: int | float) -> int:
    """
    Convert years to approximate days (using 365.25 days per year).

    Args:
        years: Number of years

    Returns:
        Approximate number of days
    """
    return int(years * YEAR)


def get_age_in_days(birth_date: dt_date, reference_date: dt_date | None = None) -> int:
    """
    Get age in days from birth date to reference date.

    Args:
        birth_date: Patient's birth date
        reference_date: Date to calculate age at (defaults to today)

    Returns:
        Age in days
    """
    if reference_date is None:
        reference_date = dt_date.today()
    return days_between(birth_date, reference_date)


def is_date_in_range(date_to_check: dt_date, start_date: dt_date, end_date: dt_date) -> bool:
    """
    Check if a date falls within a range (inclusive).

    Args:
        date_to_check: Date to check
        start_date: Start of range
        end_date: End of range

    Returns:
        True if date is within range, False otherwise
    """
    return start_date <= date_to_check <= end_date


def get_next_date_at_age(birth_date: dt_date, age_days: int) -> dt_date:
    """
    Get the date when patient will be a specific age in days.

    Args:
        birth_date: Patient's birth date
        age_days: Target age in days

    Returns:
        Date when patient will be age_days old
    """
    return add_days(birth_date, age_days)
