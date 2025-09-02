from datetime import date as dt_date
from datetime import datetime as dt_datetime

import pytz


def handle_date(
    date: dt_date | dt_datetime | None, tz: str = "America/Fortaleza"
) -> dt_datetime:
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
