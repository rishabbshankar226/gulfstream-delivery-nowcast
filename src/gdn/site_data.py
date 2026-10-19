"""site/data.json (§3.10): every figure the dashboard shows, read at runtime by site/app.js."""
import re
from pathlib import Path

from . import events, live, model
from .fiscal import Calendar, qidx, qrange
from .files import read_csv, read_json, write_json

QS = qrange("2016Q1", "2026Q2")


def live_quarters(root):
    root = Path(root)
    qs = set()
    for p in list((root / "predictions").glob("*.json")) + list((root / "results/live").glob("*_latest.json")) \
            + list((root / "results/live").glob("*_build.json")):
        m = re.match(r"(\d{4}Q[1-4])", p.name)
        if m:
            qs.add(m[1])
    return sorted(qs, key=qidx)


def _maybe(p):
    return read_json(p) if p.exists() else None


def path_rows(p):
    out = []
    for r in read_csv(p):
        row = {"date": r["date"]}
        for k, v in r.items():
            if k != "date":
                row[k] = int(v) if k.startswith(("events_", "trailing_")) else float(v)
        out.append(row)
    return out


def build(root="."):
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    chosen = m["definition"]
    rep = {r["quarter"]: r for r in read_csv(root / "data/processed/gd_deliveries.csv")}
    reg = {r["quarter"]: r for r in read_csv(root / "data/processed/registry_quarterly.csv")}
    bt = {k: [None] * len(QS) for k in ("seasonal", "last", "guidance", "raw", "ratio")}
    for f in ("results/design.csv", "results/holdout.csv"):
        for r in read_csv(root / f):
            if r["definition"] in ("none", chosen):
                bt[r["model"]][QS.index(r["quarter"])] = float(r["total"])
    dates = live.table_dates(root)
    pipe_snap = dates[-1] if dates else read_json(root / "data/snapshots/MANIFEST.json")["backtest"]
    pipe = events.pipeline(live.read_table(root, pipe_snap)) if dates else {}
    est = read_json(root / "results/estimates.json")
    cfg = read_json(root / "config/calendar.json")
    cal, Y, calls = Calendar.load(root), live.reported_history(root), model.load_guidance(root)
    lv = root / "results/live"
    lives, paths = [], {}
    for q in live_quarters(root):
        pace = model.guidance_pace(q, Y, calls, cal) if all(qrange(f"{q[:4]}Q1", q)[:-1][i] in Y
                                                             for i in range(int(q[5]) - 1)) else None
        lives.append({"quarter": q, "build": _maybe(lv / f"{q}_build.json"), "latest": _maybe(lv / f"{q}_latest.json"),
                      "locked": _maybe(root / "predictions" / f"{q}.json"), "lock": _maybe(lv / f"{q}_lock.json"),
                      "score": _maybe(lv / f"{q}_score.json"), "guidance_pace": pace["total"] if pace else None,
                      "release_date": cfg.get("releases", {}).get(q)})
        if (lv / f"{q}_path.csv").exists():
            paths[q] = path_rows(lv / f"{q}_path.csv")
    data = {
        "snapshot": read_json(root / "data/snapshots/MANIFEST.json")["backtest"],
        "definition": chosen,
        "metrics": m,
        "quarters": QS,
        "reported": {c: [int(rep[q][c]) for q in QS] for c in ("large", "mid", "total")},
        "registry": {c: [int(reg[q][f"{chosen.lower()}_{c}"]) for q in QS] for c in ("large", "mid")},
        "backtest": bt,
        "pipeline": pipe,
        "pipeline_snapshot": pipe_snap,
        "estimates": {k: v for k, v in est.items() if k != "basis"},
        "live": lives,
    }
    if paths:
        data["path"] = paths
    write_json(root / "site/data.json", data)
    return data


def run(root="."):
    root = Path(root)
    if not (root / "results/estimates.json").exists():
        print("skip site data: no estimates yet")
        return 0
    build(root)
    print("wrote site/data.json")
    return 0
