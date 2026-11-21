"""HER AI — Temporal Grounding & Date Normalization.

Defines:
  - Temporal precision levels: day, month, year, decade, unknown.
  - Normalization helpers converting date strings or partial dates into standardized
    date objects with explicit precision tracking.
  - Invariant: Never fabricate precision; store exact granularity provided.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

VALID_PRECISIONS = {"day", "month", "year", "decade", "unknown"}
TemporalPrecision = Literal["day", "month", "year", "decade", "unknown"]

# Regular expressions for date recognition
_RE_YEAR = re.compile(r"^\b(\d{4})\b$")
_RE_YEAR_MONTH = re.compile(r"^(\d{4})[-/](0[1-9]|1[0-2])$")
_RE_ISO_DATE = re.compile(r"^(\d{4})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])$")
_RE_DECADE = re.compile(r"^\b(\d{4})s\b$", re.IGNORECASE)


def normalize_event_date(
    raw_date: str | date | datetime | None,
    explicit_precision: TemporalPrecision | None = None,
) -> tuple[date | None, TemporalPrecision]:
    """
    Normalize raw date input into an exact (date | None, TemporalPrecision) tuple.

    Rules:
      1. If raw_date is None or empty: (None, 'unknown').
      2. If raw_date is '2021-06-15' (YYYY-MM-DD): (date(2021, 6, 15), 'day').
      3. If raw_date is '2021-06' (YYYY-MM): (date(2021, 6, 1), 'month').
      4. If raw_date is '2021' (YYYY): (date(2021, 1, 1), 'year').
      5. If raw_date is '2010s': (date(2010, 1, 1), 'decade').
      6. If date object passed directly with explicit_precision, respect precision.
      7. Never fabricate precision — if only year is known, precision must remain 'year'.
    """
    if raw_date is None:
        return None, "unknown"

    if isinstance(raw_date, datetime):
        d = raw_date.date()
        prec = explicit_precision or "day"
        return d, prec

    if isinstance(raw_date, date):
        prec = explicit_precision or "day"
        return raw_date, prec

    cleaned = str(raw_date).strip()
    if not cleaned or cleaned.lower() in ("unknown", "none", "null"):
        return None, "unknown"

    # Match exact ISO Date (YYYY-MM-DD)
    m_day = _RE_ISO_DATE.match(cleaned)
    if m_day:
        year, month, day = map(int, m_day.groups())
        return date(year, month, day), explicit_precision or "day"

    # Match Year-Month (YYYY-MM)
    m_month = _RE_YEAR_MONTH.match(cleaned)
    if m_month:
        year, month = map(int, m_month.groups())
        return date(year, month, 1), explicit_precision or "month"

    # Match Decade (e.g. 2010s)
    m_decade = _RE_DECADE.match(cleaned)
    if m_decade:
        decade_start = int(m_decade.group(1))
        return date(decade_start, 1, 1), explicit_precision or "decade"

    # Match Full Year (YYYY)
    m_year = _RE_YEAR.match(cleaned)
    if m_year:
        year = int(m_year.group(1))
        return date(year, 1, 1), explicit_precision or "year"

    # Fallback: attempt ISO parse
    try:
        dt = date.fromisoformat(cleaned)
        return dt, explicit_precision or "day"
    except (ValueError, TypeError):
        return None, "unknown"

