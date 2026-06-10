"""Small shared helpers."""

from datetime import date, datetime

# Month names per language — avoids both the GNU-only "%-d" strftime
# flag and depending on the server's locale.
_MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "sv": ["januari", "februari", "mars", "april", "maj", "juni", "juli",
           "augusti", "september", "oktober", "november", "december"],
    "da": ["januar", "februar", "marts", "april", "maj", "juni", "juli",
           "august", "september", "oktober", "november", "december"],
    "no": ["januar", "februar", "mars", "april", "mai", "juni", "juli",
           "august", "september", "oktober", "november", "desember"],
}


def human_date(
    value: date | datetime | int | float | str | None, lang: str = "en"
) -> str:
    """Render a date as e.g. "June 9, 2026" (en) or "9 juni 2026" (sv/da/no).

    Accepts a date/datetime, a Unix timestamp, or an ISO date string.
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
    if lang not in _MONTHS:
        lang = "en"
    month = _MONTHS[lang][d.month - 1]
    if lang == "en":
        return f"{month} {d.day}, {d.year}"
    return f"{d.day} {month} {d.year}"
