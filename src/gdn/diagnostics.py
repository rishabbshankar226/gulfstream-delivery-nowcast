"""Registry events against reported deliveries by year, 2016 to 2019 only (Phase 2)."""
from pathlib import Path

from . import events
from .fiscal import Calendar, qrange
from .files import read_csv, write_csv

COLS = ["year", "definition", "level", "group", "registry", "reported", "ratio"]
YEARS = range(2016, 2020)


def coverage_rows(rows, reported, cal):
    out = []
    for y in YEARS:
        qs = qrange(f"{y}Q1", f"{y}Q4")
        lo, hi = cal.window(qs[0])[0], cal.window(qs[-1])[1]
        for e in ("E1", "E2"):
            key = e.lower()
            inyear = [r for r in rows if r[key] and lo < r[key] <= hi]
            for c in ("large", "mid", "total"):
                n = sum(1 for r in inyear if c == "total" or r["cabin"] == c)
                rep = sum(reported[q][c] for q in qs)
                out.append({"year": y, "definition": e, "level": "cabin" if c != "total" else "total", "group": c,
                            "registry": n, "reported": rep, "ratio": n / rep if rep else None})
            for m in sorted({r["model"] for r in inyear}):
                n = sum(1 for r in inyear if r["model"] == m)
                out.append({"year": y, "definition": e, "level": "model", "group": m, "registry": n,
                            "reported": None, "ratio": None})
    return out


def flagged(cov):
    """Cabin-years whose registry/reported ratio falls outside 0.5 to 1.5 under both definitions."""
    bad = {}
    for r in cov:
        if r["level"] == "cabin" and not (0.5 <= r["ratio"] <= 1.5):
            bad.setdefault((r["year"], r["group"]), set()).add(r["definition"])
    return sorted(k for k, v in bad.items() if v == {"E1", "E2"})


def run(root="."):
    root = Path(root)
    rows = events.read_serials_rows(read_csv(root / "data/processed/serials.csv"))
    rep = {r["quarter"]: {"large": int(r["large"]), "mid": int(r["mid"]), "total": int(r["total"])}
           for r in read_csv(root / "data/processed/gd_deliveries.csv")}
    cov = coverage_rows(rows, rep, Calendar.load(root))
    write_csv(root / "results/diagnostics/coverage_design.csv", COLS, cov)
    for r in cov:
        if r["level"] != "model":
            print(r["year"], r["definition"], r["group"], r["registry"], r["reported"], round(r["ratio"], 3))
    bad = flagged(cov)
    print("outside 0.5 to 1.5 under both definitions:", bad or "none")
    return 0
