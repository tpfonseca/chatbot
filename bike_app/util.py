"""Small shared helpers."""

from datetime import date, datetime


def human_date(value: date | datetime | int | float | str | None) -> str:
    """Render a date as e.g. "June 9, 2026".

    Accepts a date/datetime, a Unix timestamp, or an ISO date string.
    Avoids the GNU-only "%-d" strftime flag so it works on any platform.
    Unparseable strings are returned as-is; None becomes "".
    """
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        d = datetime.fromtimestamp(value)
    elif isinstance(value, str):
        try:
            d = date.fromisoformat(value)
        except ValueError:
            return value
    else:
        d = value
    return f"{d.strftime('%B')} {d.day}, {d.year}"
