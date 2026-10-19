"""GD's fiscal quarters and the event windows of §3.1."""
import datetime as dt
from pathlib import Path

from .files import read_csv, read_json

START = "2016Q1"
PRE_START_END = "2015-12-31"
LAST_PINNED = "2026Q2"
DESIGN = ("2017Q1", "2019Q4")
HOLDOUT = ("2020Q1", "2026Q2")
LIVE_FIRST = "2026Q3"


def qidx(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


def qlab(i):
    return f"{i // 4}Q{i % 4 + 1}"


def qrange(a, b):
    return [qlab(i) for i in range(qidx(a), qidx(b) + 1)]


def shift(q, k):
    return qlab(qidx(q) + k)


class Calendar:
    """Fiscal ends: reported quarters from gd_deliveries.csv (or a given map), then §3.1's rule."""

    def __init__(self, pinned, fiscal_ends=None):
        self.pinned = dict(pinned)
        self.pinned.setdefault("2015Q4", PRE_START_END)
        self.extra = dict(fiscal_ends or {})

    @classmethod
    def load(cls, root="."):
        root = Path(root)
        rows = read_csv(root / "data/processed/gd_deliveries.csv")
        pinned = {r["quarter"]: r["fiscal_end"] for r in rows}
        cal = root / "config/calendar.json"
        extra = read_json(cal).get("fiscal_ends", {}) if cal.exists() else {}
        return cls(pinned, extra)

    def end(self, q):
        if q in self.pinned and qidx(q) <= qidx(LAST_PINNED):
            return self.pinned[q]
        y, n = int(q[:4]), int(q[5])
        if n == 4:
            return f"{y}-12-31"
        if n in (2, 3):
            prev = self.end(shift(q, -1))
            return None if prev is None else (dt.date.fromisoformat(prev) + dt.timedelta(days=91)).isoformat()
        return self.extra.get(q)

    def window(self, q):
        """(window_start, window_end): events count when start < date <= end."""
        return self.end(shift(q, -1)), self.end(q)
