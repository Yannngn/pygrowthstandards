import contextlib
import datetime
from typing import TypeAlias

DateType: TypeAlias = datetime.date | datetime.datetime
DateInputType: TypeAlias = DateType | str


def handle_date_input(date_input: DateInputType) -> datetime.datetime:
    if isinstance(date_input, datetime.datetime):
        return date_input

    if isinstance(date_input, datetime.date):
        return datetime.datetime.combine(date_input, datetime.time.min)

    if isinstance(date_input, str):
        date_formats = [
            "%Y-%m-%d",  # ISO format
            "%Y/%m/%d",
            "%d-%m-%Y",  # DMY
            "%d/%m/%Y",
            "%m-%d-%Y",  # MDY
            "%m/%d/%Y",
        ]

        for fmt in date_formats:
            with contextlib.suppress(ValueError):
                return datetime.datetime.strptime(date_input, fmt)

        raise ValueError(f"Invalid date string: '{date_input}'. Supported formats: YYYY-MM-DD, DD-MM-YYYY, MM-DD-YYYY, and variants with '/'.")

    raise TypeError(f"Invalid date input type: {type(date_input)}. Expected datetime.date, datetime.datetime, or str.")
