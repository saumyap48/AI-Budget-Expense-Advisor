from datetime import date, datetime, timedelta
import calendar
from typing import Tuple


def get_current_month_year() -> Tuple[int, int]:
    now = datetime.now()
    return now.month, now.year


def get_month_date_range(year: int, month: int) -> Tuple[date, date]:
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    return start_date, end_date


def format_date_human(d: date) -> str:
    return d.strftime("%B %d, %Y") if d else ""
