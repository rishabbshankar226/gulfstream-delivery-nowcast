"""`make data`: the backtest subset, the airframe table, the registry counts and the SEC series."""
import datetime as dt
import sys
from pathlib import Path

from . import events, faa, sec
from .fiscal import START, LAST_PINNED, Calendar, qrange, shift
from .files import read_csv, write_csv, write_text

DELIVERY_COLS = ["quarter", "fiscal_end", "large", "mid", "total", "accn", "filed"]
SEGMENT_COLS = ["quarter", "segment", "revenue_usd", "operating_earnings_usd", "accn"]
BACKLOG_COLS = ["segment", "total_backlog_usd", "accn"]
BTB_COLS = ["quarter", "group", "ratio", "accn"]
SEG_QUARTERS = qrange("2024Q3", "2026Q2")


def backtest_date(root):
    man = faa.manifest(root)
    if man.get("backtest"):
        return man["backtest"]
    dates = faa.raw_dates(root)
    if not dates:
        sys.exit("No FAA zip under data/raw/faa and no stored subset: run the snapshot first.")
    return dates[-1]


def build_faa(root, log=print):
    """Store the backtest subset from its raw zip when present; return the subset texts."""
    date = backtest_date(root)
    z = faa.zip_path(root, date)
    if z.exists():
        texts = faa.zip_texts(z)
        sub = faa.subset(texts)
        faa.store_subset(root, date, sub, z, backtest=True)
        log(f"backtest subset {date} from its zip")
    else:
        sub = faa.read_subset(root, date)
        log(f"backtest subset {date} from the tracked files (raw zip absent)")
    return date, sub


def usd(m):
    return int(round(m * 1_000_000))


def build_sec(root, network=True, log=print):
    """gd_deliveries.csv, segments.csv, backlog_2026Q2.csv and book_to_bill.csv from GD's releases."""
    c = sec.Client(root, network=network)
    try:
        fs = c.filings()
    except sec.SECUnavailable as e:
        log(f"SEC not read ({e}); keeping the tracked SEC series.")
        return False
    ends = sec.quarter_ends_from_10q(fs)

    def end(q):
        return f"{q[:4]}-12-31" if q.endswith("Q4") else ends[q]

    parsed = {}

    def release(q):
        if q not in parsed:
            f = sec.results_8k(fs, end(q))
            if f is None:
                raise sec.SECUnavailable(f"no results 8-K for {q}")
            name, b = c.exhibit_991(f["accn"])
            parsed[q] = (f, sec.plain(b))
        return parsed[q]

    try:
        rows = []
        for q in qrange(START, LAST_PINNED):
            src = shift(q, 4) if q < "2017Q1" else q
            f, text = release(src)
            d = sec.parse_deliveries(text)
            pre = "prior_" if src != q else ""
            rows.append({"quarter": q, "fiscal_end": end(q), "large": d[pre + "large"], "mid": d[pre + "mid"],
                         "total": d[pre + "total"], "accn": f["accn"], "filed": f["filed"]})
            if d["sentence"]:
                log(f"{q}: delivery sentence {d['sentence']} agrees with the table")
        # Each release's prior-year column against the year-earlier release itself.
        by_q = {r["quarter"]: r for r in rows}
        for q in qrange("2018Q1", LAST_PINNED):
            d = sec.parse_deliveries(release(q)[1])
            p = by_q[shift(q, -4)]
            if (d["prior_large"], d["prior_mid"]) != (p["large"], p["mid"]):
                log(f"note: {q}'s prior-year column {d['prior_large']}/{d['prior_mid']} differs from "
                    f"{shift(q, -4)} as first reported {p['large']}/{p['mid']}")
        seg_rows = []
        for q in SEG_QUARTERS:
            f, text = release(q)
            for s, (rev, oe) in sec.parse_segments(text).items():
                seg_rows.append({"quarter": q, "segment": s, "revenue_usd": usd(rev),
                                 "operating_earnings_usd": usd(oe), "accn": f["accn"]})
        f, text = release("2026Q2")
        bl = sec.parse_backlog(text, "Second Quarter 2026")
        bl_rows = [{"segment": s, "total_backlog_usd": usd(v), "accn": f["accn"]} for s, v in bl.items()]
        btb = sec.book_to_bill(text) or {}
        btb_rows = [{"quarter": "2026Q2", "group": g, "ratio": v, "accn": f["accn"]} for g, v in btb.items()]
    except sec.SECUnavailable as e:
        log(f"SEC not read ({e}); keeping the tracked SEC series.")
        c.save_manifest()
        return False
    p = Path(root) / "data/processed"
    write_csv(p / "gd_deliveries.csv", DELIVERY_COLS, rows)
    write_csv(p / "segments.csv", SEGMENT_COLS, seg_rows)
    write_csv(p / "backlog_2026Q2.csv", BACKLOG_COLS, bl_rows)
    write_csv(p / "book_to_bill.csv", BTB_COLS, btb_rows)
    c.save_manifest()
    # The 91-day rule against the reported ends, for the record.
    for q in qrange("2016Q2", LAST_PINNED):
        if q[5] in "23":
            gap = (dt.date.fromisoformat(end(q)) - dt.date.fromisoformat(end(shift(q, -1)))).days
            if gap != 91:
                log(f"note: {q} ends {gap} days after the quarter before")
    return True


def run(root=".", network=True, log=print):
    root = Path(root)
    date, sub = build_faa(root, log)
    rows = events.airframes(sub)
    write_text(root / "data/processed/serials.csv", events.serials_text(rows))
    build_sec(root, network=network, log=log)
    if not (root / "data/processed/gd_deliveries.csv").exists():
        sys.exit("No gd_deliveries.csv and SEC unreadable.")
    cal = Calendar.load(root)
    write_csv(root / "data/processed/registry_quarterly.csv", events.REG_COLS,
              events.quarterly(rows, qrange(START, LAST_PINNED), cal))
    log(f"airframes {len(rows)}; serials.csv, registry_quarterly.csv written")
