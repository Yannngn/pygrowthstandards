"""Date parsing helpers and input type aliases."""

import contextlib
import datetime
from typing import TypeAlias

DateType: TypeAlias = datetime.date | datetime.datetime
DateInputType: TypeAlias = DateType | str

# Preferred date order for ambiguous inputs. Set to "DMY" (day-month-year) by
# default. Set to "MDY" to prefer month-day-year parsing. If strict ISO-only
# parsing is required, set to "ISO" and only ISO `YYYY-MM-DD` strings will be
# accepted.
DATE_ORDER = "DMY"  # one of: "DMY", "MDY", "ISO"


def handle_date_input(date_input: DateInputType | None) -> datetime.datetime:
    """Normalize a date input to a midnight datetime.

    Accepts multiple input formats and normalizes them to a datetime object at midnight.
    Supports flexible date string parsing with configurable day/month ordering via DATE_ORDER.

    Args:
        date_input: Date input as datetime, date, or string. If None, returns current datetime.
            - datetime.datetime: Returned as-is.
            - datetime.date: Converted to datetime at midnight.
            - str: Parsed as ISO format (YYYY-MM-DD) or flexible format based on DATE_ORDER setting.

    Returns:
        Parsed datetime at midnight (00:00:00).

    Raises:
        ValueError: If a string cannot be parsed as a date, or if ISO-only mode is enabled
            and the string is not in ISO format.
        TypeError: If an unsupported type is provided (not datetime, date, or str).

    Note:
        - When date_input is None, returns the current datetime.
        - String parsing respects the DATE_ORDER configuration:
          - "ISO": Only accepts YYYY-MM-DD format.
          - "DMY": Uses dayfirst=True for ambiguous dates.
          - Other values: Use dayfirst=False for ambiguous dates.
    """

    if date_input is None:
        return datetime.datetime.now()

    if isinstance(date_input, datetime.datetime):
        return date_input

    if isinstance(date_input, datetime.date):
        return datetime.datetime.combine(date_input, datetime.time.min)

    if isinstance(date_input, str):
        # Try strict ISO first (unambiguous)
        with contextlib.suppress(ValueError):
            return datetime.datetime.strptime(date_input, "%Y-%m-%d")

        # If configured for ISO-only behaviour, fail now with a clear message
        if DATE_ORDER == "ISO":
            raise ValueError(f"Invalid date string: '{date_input}'. Only ISO format 'YYYY-MM-DD' is accepted when DATE_ORDER='ISO'.")

        # Fall back to dateutil for flexible parsing, honoring dayfirst preference
        dayfirst = DATE_ORDER == "DMY"
        try:
            from dateutil.parser import parse as _dateutil_parse

            parsed = _dateutil_parse(date_input, dayfirst=dayfirst)
            # Ensure we return a datetime (not a date)
            if isinstance(parsed, datetime.date) and not isinstance(parsed, datetime.datetime):
                parsed = datetime.datetime.combine(parsed, datetime.time.min)

            return parsed

        except Exception as exc:
            raise ValueError(
                f"Invalid date string: '{date_input}'. Provide ISO 'YYYY-MM-DD' or an unambiguous date string. "
                f"(Parsing attempted with dayfirst={dayfirst}.)"
            ) from exc

    raise TypeError(f"Invalid date input type: {type(date_input)}. Expected datetime.date, datetime.datetime, or str.")
