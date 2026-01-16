from __future__ import annotations
from typing import List, Optional, Union
from datetime import datetime, timezone, timedelta
import re

try:
    from dateutil import parser as _dateutil_parser
except Exception:
    _dateutil_parser = None


def _quote(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # Always wrap values in double quotes, escaping any internal quotes
    safe = text.replace('"', '\\"')
    return f'"{safe}"'


class QueryBuilder:
    def __init__(self):
        self.parts: List[str] = []
        self.sortBy: Optional[str] = None
        self.sortOrder: Optional[str] = None
        self.today_used: bool = False
        self.date_range_used: bool = False

    def title(self, text: str) -> "QueryBuilder":
        self.parts.append(f"ti:{_quote(text)}")
        return self

    def author(self, name: str) -> "QueryBuilder":
        self.parts.append(f"au:{_quote(name)}")
        return self

    def abstract(self, text: str) -> "QueryBuilder":
        self.parts.append(f"abs:{_quote(text)}")
        return self

    def comment(self, text: str) -> "QueryBuilder":
        self.parts.append(f"co:{_quote(text)}")
        return self

    def journal_ref(self, text: str) -> "QueryBuilder":
        self.parts.append(f"jr:{_quote(text)}")
        return self

    def category(self, cat: str) -> "QueryBuilder":
        self.parts.append(f"cat:{_quote(cat)}")
        return self

    def report_number(self, rn: str) -> "QueryBuilder":
        self.parts.append(f"rn:{_quote(rn)}")
        return self

    def and_(self) -> "QueryBuilder":
        self.parts.append("AND")
        return self

    def or_(self) -> "QueryBuilder":
        self.parts.append("OR")
        return self

    def andnot_(self) -> "QueryBuilder":
        self.parts.append("ANDNOT")
        return self

    def group(self, qb: Union["QueryBuilder", str]) -> "QueryBuilder":
        if isinstance(qb, QueryBuilder):
            self.parts.append(f"({qb.build()})")
        else:
            self.parts.append(f"({qb})")
        return self

    def sort_by(self, field: str, order: str) -> "QueryBuilder":
        self.sortBy = field
        self.sortOrder = order
        return self

    def _parse_date(self, date_input: str) -> datetime:
        if _dateutil_parser:
            dt = _dateutil_parser.parse(date_input)
            if dt.tzinfo is None:
                # assume UTC
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        # fallback parsing
        fmts = [
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y%m%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%Y-%m",
            "%Y",
        ]
        for fmt in fmts:
            try:
                dt = datetime.strptime(date_input, fmt)
                dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                continue
        raise ValueError(f"Unrecognized date format: {date_input}")

    def date_range(self, start: str, end: str, end_inclusive: bool = True) -> "QueryBuilder":
        s_dt = self._parse_date(start)
        e_dt = self._parse_date(end)
        # normalize date-only inputs: dateutil will set times if provided; fallback preserved
        # If user supplied a year or year-month without time, dateutil parses to start of period; for end inclusive, expand
        if end_inclusive:
            # if end has zeroed time and looks like date-only, extend to last minute
            if e_dt.hour == 0 and e_dt.minute == 0 and re.match(r"^\d{4}(-\d{2})?$", end):
                # if only year or year-month
                if re.match(r"^\d{4}$", end):
                    e_dt = e_dt.replace(month=12, day=31, hour=23, minute=59)
                elif re.match(r"^\d{4}-\d{2}$", end):
                    # last day of month
                    year = e_dt.year
                    month = e_dt.month
                    # naive last day calc
                    if month == 12:
                        last = 31
                    else:
                        next_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)
                        last = (next_month - timedelta(days=1)).day
                    e_dt = e_dt.replace(day=last, hour=23, minute=59)
        if s_dt > e_dt:
            raise ValueError("start date must be <= end date")
        start_fmt = s_dt.strftime("%Y%m%d%H%M")
        end_fmt = e_dt.strftime("%Y%m%d%H%M")
        self.parts.append(f"submittedDate:[{start_fmt} TO {end_fmt}]")
        self.date_range_used = True
        return self

    def today(self) -> "QueryBuilder":
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_fmt = start_of_day.strftime("%Y%m%d%H%M")
        end_fmt = end_of_day.strftime("%Y%m%d%H%M")
        self.parts.append(f"submittedDate:[{start_fmt} TO {end_fmt}]")
        self.today_used = True
        return self

    def build(self) -> str:
        #check and ensure that there isnt both a today and date_range call
        if self.today_used and self.date_range_used:
            raise ValueError("Cannot use both today() and date_range() in the same query")
        return " ".join(self.parts)
