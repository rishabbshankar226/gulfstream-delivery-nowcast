"""Source facts and label rules for the number ledger.

A rule names a label first (a sentence template, or a table's header signature with a row and a column) and
only then the one source field its number must equal. Nothing here looks a value up by value.
"""
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
MODELS = ("ratio", "raw", "guidance", "seasonal", "last")
SEGS = ("Aerospace", "Marine Systems", "Combat Systems", "Technologies")
NAME2MODEL = {
    "registry estimate (ratio)": "ratio", "registry estimate": "ratio", "ratio": "ratio", "average miss, ratio": "ratio",
    "raw registry count": "raw", "raw": "raw", "average miss, raw": "raw",
    "gd guidance pace": "guidance", "gd's guidance pace": "guidance", "guidance": "guidance",
    "same quarter last year": "seasonal", "the same quarter last year": "seasonal", "seasonal": "seasonal",
    "average miss, same quarter last year": "seasonal",
    "last quarter": "last", "last": "last", "average miss, last quarter": "last",
}

TEXT_SURFACES = [
    ("post", "docs/LINKEDIN_POST.md"),
    ("sensitivity", "results/exploratory/sensitivity.md"),
    ("readme", "README.md"),
    ("note", "report/note.html"),
    ("interview", "docs/INTERVIEW_NOTES.md"),
    ("resume", "docs/RESUME_BULLETS.md"),
    ("error_analysis", "results/error_analysis.md"),
    ("asof", "results/exploratory/asof.md"),
    ("prereg", "docs/PREREGISTRATION.md"),
]


def _csv(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def _flat(prefix, o, F):
    if isinstance(o, dict):
        for k, v in o.items():
            _flat(f"{prefix}.{k}", v, F)
    elif isinstance(o, list):
        F[prefix] = o
        for i, v in enumerate(o):
            if not isinstance(v, (dict, list)):
                F[f"{prefix}.{i}"] = v
    else:
        F[prefix] = o


def qidx(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


def qlab(i):
    return f"{i // 4}Q{i % 4 + 1}"


def nearest_rank(xs, p):
    s = sorted(xs)
    return s[math.ceil(p * len(s)) - 1]


def load_facts(root):
    """{key: value} from results/, data/processed/, data/guidance.csv, results/live/, report/claims.json."""
    root = Path(root)
    F = {"@src": {}}

    def put(k, v, src):
        F[k] = v
        F["@src"][k] = src

    m = json.loads((root / "results/metrics.json").read_text())
    tmp = {}
    _flat("m", m, tmp)
    for k, v in tmp.items():
        put(k, v, "results/metrics.json")
    chosen = m["definition"]
    h = m["holdout"]
    for q, v in h["coverage_ratio"]["by_quarter"].items():
        put(f"cov.{q}", v, "results/metrics.json:holdout.coverage_ratio.by_quarter")
    for r in h["band"]["by_quarter"]:
        for k in ("low", "high"):
            put(f"band.{r['quarter']}.{k}", r[k], "results/metrics.json:holdout.band.by_quarter")
    put("guid.n_fallback", len(h["guidance"]["fallback_quarters"]), "results/metrics.json:holdout.guidance.fallback_quarters")
    put("guid.fallback_year", int(h["guidance"]["fallback_quarters"][0][:4]) if h["guidance"]["fallback_quarters"] else None,
        "results/metrics.json:holdout.guidance.fallback_quarters")
    put("const.n_baselines", len(h["tests"]), "results/metrics.json:holdout.tests (count)")
    put("const.n_models", len(h["mae"]), "results/metrics.json:holdout.mae (count)")
    put("const.trunc.1", 30, "results/metrics.json:holdout.truncation_mae keys")
    put("const.trunc.2", 60, "results/metrics.json:holdout.truncation_mae keys")
    put("const.trunc.3", 90, "results/metrics.json:holdout.truncation_mae keys")
    assert set(h["truncation_mae"]) == {"0", "30", "60", "90"}

    gd = {r["quarter"]: r for r in _csv(root / "data/processed/gd_deliveries.csv")}
    reg = {r["quarter"]: r for r in _csv(root / "data/processed/registry_quarterly.csv")}
    for q, r in gd.items():
        for c in ("large", "mid", "total"):
            put(f"gd.{q}.{c}", int(r[c]), "data/processed/gd_deliveries.csv")
        put(f"gd.{q}.fiscal_end", r["fiscal_end"], "data/processed/gd_deliveries.csv")
        put(f"gd.{q}.accn", r["accn"], "data/processed/gd_deliveries.csv")
    e = chosen.lower()
    for q, r in reg.items():
        for c in ("large", "mid"):
            put(f"reg.{q}.{c}", int(r[f"{e}_{c}"]), "data/processed/registry_quarterly.csv")
        put(f"reg.{q}.total", int(r[f"{e}_large"]) + int(r[f"{e}_mid"]), "data/processed/registry_quarterly.csv")
    by_year = {}
    for name in ("design", "holdout"):
        for r in _csv(root / f"results/{name}.csv"):
            if r["definition"] not in ("none", chosen):
                continue
            q, mod = r["quarter"], r["model"]
            for c in ("large", "mid", "total", "actual", "ae", "ape_pct"):
                put(f"bt.{q}.{mod}.{c}", float(r[c]), f"results/{name}.csv")
            put(f"bt.{q}.{mod}.signed", float(r["total"]) - float(r["actual"]), f"results/{name}.csv")
            if name == "holdout":
                by_year.setdefault(q[:4], {}).setdefault(mod, []).append(float(r["ae"]))
    for y, d in by_year.items():
        for mod, xs in d.items():
            put(f"year.{y}.{mod}", sum(xs) / len(xs), "results/holdout.csv (mean of ae by year)")
    hq = [qlab(i) for i in range(qidx("2020Q1"), qidx("2026Q2") + 1)]
    put("typical", sum(F[f"gd.{q}.total"] for q in hq) / len(hq), "data/processed/gd_deliveries.csv (mean total, 2020Q1 on)")
    sourced = [q for q in hq if q not in h["guidance"]["fallback_quarters"]]
    for mod in ("ratio", "seasonal"):
        put(f"guid.sub.{mod}", sum(F[f"bt.{q}.{mod}.ae"] for q in sourced) / len(sourced),
            "results/holdout.csv (mean ae over the sourced quarters)")
    for mod in MODELS:
        put(f"tile.{mod}", abs(h["mae"][mod] - h["mae"]["ratio"]), "results/metrics.json (mae difference from ratio)")
    for y in range(2016, 2027):
        qs = [q for q in gd if q.startswith(str(y))]
        if qs:
            put(f"evper.{y}.total", sum(F[f"reg.{q}.total"] for q in qs) / sum(F[f"gd.{q}.total"] for q in qs),
                "data/processed registry_quarterly.csv over gd_deliveries.csv, by year")
            put(f"evper.{y}.mid", sum(F[f"reg.{q}.mid"] for q in qs) / sum(F[f"gd.{q}.mid"] for q in qs),
                "data/processed registry_quarterly.csv over gd_deliveries.csv, by year, mid cabin")
            put(f"middiff.{y}", sum(F[f"reg.{q}.mid"] for q in qs) - sum(F[f"gd.{q}.mid"] for q in qs),
                "registry mid events minus GD mid deliveries, by year")
    put("h1.2026.total", F["gd.2026Q1.total"] + F["gd.2026Q2.total"], "data/processed/gd_deliveries.csv (2026Q1 + 2026Q2)")
    wq = [qlab(i) for i in range(qidx("2017Q1"), qidx("2025Q2") + 1)]
    put("evper.mean", sum(F[f"reg.{q}.total"] / F[f"gd.{q}.total"] for q in wq) / len(wq),
        "registry_quarterly.csv over gd_deliveries.csv, mean of the quarterly ratio, 2017Q1 to 2025Q2")
    top = sorted(hq, key=lambda q: -F[f"bt.{q}.ratio.ae"])[:5]
    put("top5", top, "results/holdout.csv (five largest ratio ae)")

    # live
    lv = root / "results/live"
    state = {}
    for p in sorted(lv.glob("*.json")):
        q, kind = p.name[:6], p.name[7:-5]
        tmp = {}
        _flat(f"live.{q}.{kind}", json.loads(p.read_text()), tmp)
        for k, v in tmp.items():
            put(k, v, f"results/live/{p.name}")
        state.setdefault(q, {})[kind] = True
    for p in sorted((root / "predictions").glob("*.json")):
        q = p.name[:6]
        tmp = {}
        _flat(f"live.{q}.pred", json.loads(p.read_text()), tmp)
        for k, v in tmp.items():
            put(k, v, f"predictions/{p.name}")
        put(f"live.{q}.pred.sha256", hashlib.sha256(p.read_bytes()).hexdigest(), f"sha256(predictions/{p.name})")
        state.setdefault(q, {})["pred"] = True
    for q, s in state.items():
        if s.get("lock"):
            t = dt.datetime.fromisoformat(F[f"live.{q}.lock.published_at"].replace("Z", "+00:00")).astimezone(ET)
            put(f"live.{q}.lock.et_date", t.strftime("%Y-%m-%d"), f"results/live/{q}_lock.json published_at in ET")
            put(f"live.{q}.lock.et_time", t.strftime("%H:%M"), f"results/live/{q}_lock.json published_at in ET")
        pth = lv / f"{q}_path.csv"
        if pth.exists():
            rows = _csv(pth)
            put(f"path.{q}.n", len(rows), f"results/live/{q}_path.csv (rows)")
            put(f"path.{q}.first", rows[0]["date"], f"results/live/{q}_path.csv")
            put(f"path.{q}.last", rows[-1]["date"], f"results/live/{q}_path.csv")
            pk = f"live.{q}.pred" if f"live.{q}.pred.nowcast.total" in F else f"live.{q}.latest"
            below = F[f"{pk}.nowcast.total"] - F[f"{pk}.band.0"]
            above = F[f"{pk}.band.1"] - F[f"{pk}.nowcast.total"]
            for r in rows:
                for c, v in r.items():
                    if c != "date":
                        put(f"path.{q}.{r['date']}.{c}", float(v), f"results/live/{q}_path.csv")
                put(f"path.{q}.{r['date']}.band_low", float(r["nowcast_total"]) - below,
                    f"results/live/{q}_path.csv nowcast_total less the prediction's band offset")
                put(f"path.{q}.{r['date']}.band_high", float(r["nowcast_total"]) + above,
                    f"results/live/{q}_path.csv nowcast_total plus the prediction's band offset")
    F["@state"] = {q: {"locked": bool(s.get("lock") and s.get("pred")), "scored": bool(s.get("score"))}
                   for q, s in state.items()}
    for q, s in F["@state"].items():
        put(f"status.{q}", "Scored" if s["scored"] else "Locked" if s["locked"] else "Provisional",
            f"results/live/{q}_score.json and {q}_lock.json (which exist)")
    put("cov.mean_plus_2sd", h["coverage_ratio"]["mean"] + 2 * h["coverage_ratio"]["sd"],
        "results/metrics.json:holdout.coverage_ratio mean + 2 sd")
    cal = json.loads((root / "config/calendar.json").read_text())
    for q, d in cal.get("releases", {}).items():
        put(f"cal.release.{q}", d, "config/calendar.json")
        put(f"cal.eve.{q}", (dt.date.fromisoformat(d) - dt.timedelta(days=1)).isoformat(), "config/calendar.json (release - 1 day)")
    # a lock counts as public only from the day the owner records the repository went public
    F["@public"] = bool(cal.get("public")) and bool(cal.get("public_since")) and \
        any(F.get(f"live.{q}.lock.published_at", "9")[:10] >= cal["public_since"] for q in state)
    F["@lock_author"] = {}
    import subprocess
    for pp in sorted((root / "predictions").glob("*.json")):
        r = subprocess.run(["git", "-C", str(root), "log", "--diff-filter=A", "--format=%an", "--", f"predictions/{pp.name}"],
                           capture_output=True, text=True)
        F["@lock_author"][pp.name[:6]] = (r.stdout.strip().split("\n")[-1] if r.stdout.strip() else "")
    man = json.loads((root / "data/snapshots/MANIFEST.json").read_text())
    put("snap.backtest", man["backtest"], "data/snapshots/MANIFEST.json")
    daily = sorted(p.name.split(".")[0] for p in (root / "data/snapshots/daily").glob("*.serials.csv.gz"))
    put("snap.newest", daily[-1] if daily else None, "data/snapshots/daily (newest table)")
    if daily:
        text = gzip.decompress((root / f"data/snapshots/daily/{daily[-1]}.serials.csv.gz").read_bytes()).decode()
        pipe = {}
        for r in csv.DictReader(io.StringIO(text)):
            if r["held_by_gulfstream"] == "1" and not r["e1"] and not r["e2"]:
                pipe[r["model"]] = pipe.get(r["model"], 0) + 1
        put("pipe.total", sum(pipe.values()), f"data/snapshots/daily/{daily[-1]}.serials.csv.gz (held, no event)")
        shown = {}
        for k, v in pipe.items():
            put(f"pipe.{k}", v, f"data/snapshots/daily/{daily[-1]}.serials.csv.gz")
            mm = re.search(r"G\d{3}", k)  # site/app.js pipeChart folds model names the same way
            name = mm.group(0) if mm else ("Other" if k == "550" else "G650" if k == "GVI" else k)
            shown[name] = shown.get(name, 0) + v
        for k, v in shown.items():
            put(f"pipex.{k}", v, f"data/snapshots/daily/{daily[-1]}.serials.csv.gz (held, no event, by model as app.js names it)")

    # estimates and segments
    est = json.loads((root / "results/estimates.json").read_text())
    tmp = {}
    _flat("est", est, tmp)
    for k, v in tmp.items():
        put(k, v, "results/estimates.json")
    for s in est["sensitivity"]:
        put(f"sens.{s['deliveries_change']}.deliveries", s["deliveries"], "results/estimates.json:sensitivity")
        put(f"sens.{s['deliveries_change']}.rev", s["aerospace_revenue_usd"], "results/estimates.json:sensitivity")
    seg = {}
    for r in _csv(root / "data/processed/segments.csv"):
        seg.setdefault(r["segment"], {})[r["quarter"]] = (int(r["revenue_usd"]), int(r["operating_earnings_usd"]))
        put(f"seg.{r['segment']}.{r['quarter']}.rev", int(r["revenue_usd"]), "data/processed/segments.csv")
        put(f"seg.{r['segment']}.{r['quarter']}.oe", int(r["operating_earnings_usd"]), "data/processed/segments.csv")
        put(f"seg.{r['segment']}.{r['quarter']}.margin_pct", int(r["operating_earnings_usd"]) / int(r["revenue_usd"]) * 100,
            "data/processed/segments.csv (oe / revenue)")
    for r in _csv(root / "data/processed/backlog_2026Q2.csv"):
        put(f"backlog.{r['segment']}", int(r["total_backlog_usd"]), "data/processed/backlog_2026Q2.csv")
    for r in _csv(root / "data/processed/book_to_bill.csv"):
        put(f"btb.{r['group']}", float(r["ratio"]), "data/processed/book_to_bill.csv")
    S = est["segments"]
    tot_ttm = sum(S[s]["ttm_revenue_usd"] for s in SEGS)
    for s in SEGS:
        put(f"mix.{s}.share_pct", S[s]["ttm_revenue_usd"] / tot_ttm * 100, "results/estimates.json (ttm share of four segments)")
        put(f"mix.{s}.margin_pct", S[s]["ttm_margin"] * 100, "results/estimates.json:ttm_margin")
        ya = seg[s]["2025Q3"][0]
        put(f"estx.{s}.yago", ya, "data/processed/segments.csv (2025Q3 revenue)")
        put(f"estx.{s}.est", S[s]["drift_usd"], "results/estimates.json:drift_usd")
        put(f"estx.{s}.chg", S[s]["drift_usd"] - ya, "estimates.json drift_usd minus segments.csv 2025Q3")
        put(f"estx.{s}.chgpct", (S[s]["drift_usd"] - ya) / ya * 100, "estimates.json drift_usd over segments.csv 2025Q3")
    ya = seg["Aerospace"]["2025Q3"][0]
    put("estx.aero_now.yago", ya, "data/processed/segments.csv (2025Q3 Aerospace revenue)")
    put("estx.aero_now.est", est["aerospace_from_nowcast_usd"], "results/estimates.json:aerospace_from_nowcast_usd")
    put("estx.aero_now.chg", est["aerospace_from_nowcast_usd"] - ya, "estimates.json minus segments.csv 2025Q3")
    put("estx.aero_now.chgpct", (est["aerospace_from_nowcast_usd"] - ya) / ya * 100, "estimates.json over segments.csv 2025Q3")
    ya_all = sum(seg[s]["2025Q3"][0] for s in SEGS)
    put("estx.total.yago", ya_all, "data/processed/segments.csv (2025Q3, four segments)")
    put("estx.total.est", est["revenue_total_usd"], "results/estimates.json:revenue_total_usd")
    put("estx.total.chg", est["revenue_total_usd"] - ya_all, "estimates.json minus segments.csv 2025Q3")
    put("estx.total.chgpct", (est["revenue_total_usd"] - ya_all) / ya_all * 100, "estimates.json over segments.csv 2025Q3")
    for s in est["sensitivity"]:
        put(f"sens.{s['deliveries_change']}.chg", s["aerospace_revenue_usd"] - ya, "estimates.json sensitivity minus 2025Q3")
    a26 = [seg["Aerospace"][q] for q in ("2026Q1", "2026Q2")]
    put("aero.h1_2026.margin_pct", sum(x[1] for x in a26) / sum(x[0] for x in a26) * 100,
        "data/processed/segments.csv (2026Q1 + 2026Q2 Aerospace oe / revenue)")

    # guidance
    calls = _csv(root / "data/guidance.csv")
    put("guid.first", calls[0]["call_date"], "data/guidance.csv (first call)")
    put("guid.last", calls[-1]["call_date"], "data/guidance.csv (last call)")
    for c in calls:
        if c["outlook"].strip():
            put(f"guid.{c['call_date']}.outlook", float(c["outlook"]), "data/guidance.csv")
    put("guid.outlook.2026", float([c for c in calls if c["year"] == "2026" and c["outlook"].strip()][-1]["outlook"]),
        "data/guidance.csv (latest 2026 outlook)")

    # as-of study
    ap = root / "results/exploratory/asof.csv"
    if ap.exists():
        rows = _csv(ap)
        scored = [r for r in rows if r["estimate"]]
        put("asof.n_window", len(rows), "results/exploratory/asof.csv (rows)")
        put("asof.n_scored", len(scored), "results/exploratory/asof.csv (scored rows)")
        for r in scored:
            q = r["quarter"]
            put(f"asof.{q}.days", int(r["days_after_end"]), "results/exploratory/asof.csv")
            put(f"asof.{q}.estimate", float(r["estimate"]), "results/exploratory/asof.csv")
            put(f"asof.{q}.reported", int(r["reported"]), "results/exploratory/asof.csv")
            put(f"asof.{q}.ae", float(r["ae"]), "results/exploratory/asof.csv")
            put(f"asof.{q}.bt_ae", float(r["backtest_ae"]), "results/exploratory/asof.csv")
            put(f"asof.{q}.capture", r["capture"][:8], "results/exploratory/asof.csv")
            put(f"asof.{q}.capture_iso", f"{r['capture'][:4]}-{r['capture'][4:6]}-{r['capture'][6:8]}", "results/exploratory/asof.csv")
            put(f"asof.{q}.trail", int(r["trailing_registry_large"]) + int(r["trailing_registry_mid"]), "results/exploratory/asof.csv")
            lags = [qlab(qidx(q) - k) for k in range(1, 5)]
            put(f"asof.{q}.bt_trail", sum(F[f"reg.{x}.total"] for x in lags), "data/processed/registry_quarterly.csv (four lags)")
            put(f"asof.{q}.events_more", int(r["events_large"]) + int(r["events_mid"]) - F[f"reg.{q}.total"],
                "asof.csv events minus registry_quarterly.csv")
            if r["band_low"]:
                put(f"asof.{q}.band_low", float(r["band_low"]), "results/exploratory/asof.csv")
                put(f"asof.{q}.band_high", float(r["band_high"]), "results/exploratory/asof.csv")
        held = [r for r in scored if r["inside_band"] != ""]
        put("asof.n_held", len(held), "results/exploratory/asof.csv (scored rows with a band)")
        put("asof.n_inside", sum(int(r["inside_band"]) for r in held), "results/exploratory/asof.csv")
        put("asof.n_closer", sum(1 for r in scored if float(r["ae"]) < float(r["backtest_ae"])), "results/exploratory/asof.csv")
        put("asof.n_lower", sum(1 for r in scored if float(r["estimate"]) < float(r["backtest_estimate"])),
            "results/exploratory/asof.csv")
        cdx = root / "data/raw/wayback/cdx.json"
        if cdx.exists():
            d = json.loads(cdx.read_text())
            put("asof.captures", sum(1 for r in d[1:] if r[4] == "200"), "data/raw/wayback/cdx.json (status 200 rows; raw, untracked)")

    # airframe audit
    au = root / "docs/build/AIRFRAME_AUDIT.csv"
    if au.exists():
        rows = _csv(au)
        no = [r for r in rows if r["agree"] == "no"]
        put("audit.n", len(rows), "docs/build/AIRFRAME_AUDIT.csv (rows)")
        put("audit.no", len(no), "docs/build/AIRFRAME_AUDIT.csv (agree = no)")
        put("audit.no_pct", len(no) / len(rows) * 100, "docs/build/AIRFRAME_AUDIT.csv")
        used = [r for r in no if re.search(r"used import|resale|not a new delivery|Built 2007", r["note"])]
        earlier = [r for r in no if r["source_date"] and r["source_date"] < r["our_date"] and r not in used]
        put("audit.used", len(used), "docs/build/AIRFRAME_AUDIT.csv (notes naming a used jet)")
        put("audit.earlier", len(earlier), "docs/build/AIRFRAME_AUDIT.csv (source date before ours, not used)")
        put("audit.unconfirmed", len(no) - len(used) - len(earlier), "docs/build/AIRFRAME_AUDIT.csv (the rest)")
        put("audit.non_mirror", sum(1 for r in rows if r["source_kind"] != "mirror"), "docs/build/AIRFRAME_AUDIT.csv")
        dated = [r["source_date"][:4] for r in rows if r["source_date"]]
        ser = {r["serial"]: r for r in _csv(root / "data/processed/serials.csv")}
        noair = [r for r in used if r["serial"] in ser and not ser[r["serial"]]["first_airworthiness"]
                 and not ser[r["serial"]]["year_mfr"]]
        put("audit.used_noair", len(noair), "AIRFRAME_AUDIT.csv used jets with no airworthiness date or year in data/processed/serials.csv")
        put("audit.used_fresh", len(used) - len(noair), "AIRFRAME_AUDIT.csv used jets with an airworthiness date in serials.csv")
        put("audit.year_min", int(min(dated)), "docs/build/AIRFRAME_AUDIT.csv (rows with a source date)")
        put("audit.year_max", int(max(dated)), "docs/build/AIRFRAME_AUDIT.csv (rows with a source date)")

    # each locked and scored quarter: the other four misses, and how long after the quarter's end the lock was made
    for q, stt in F["@state"].items():
        if not (stt["locked"] and stt["scored"]):
            continue
        P, actual = f"live.{q}.pred", F[f"live.{q}.score.reported.total"]
        raw = F[f"{P}.events.large"] + F[f"{P}.events.mid"]
        put(f"cmp.{q}.raw", raw, f"predictions/{q}.json events large + mid")
        put(f"cmp.{q}.raw_miss", abs(raw - actual), f"predictions/{q}.json events against score.json reported")
        for name, k in (("yago", -4), ("last", -1)):
            prev = qlab(qidx(q) + k)
            val = F.get(f"gd.{prev}.total", F.get(f"live.{prev}.score.reported.total"))
            if val is not None:
                put(f"cmp.{q}.{name}", val, f"GD's reported total for {prev}")
                put(f"cmp.{q}.{name}_miss", abs(val - actual), f"GD's reported total for {prev} against {q}")
        days = (dt.date.fromisoformat(F[f"{P}.snapshot"]) - dt.date.fromisoformat(F[f"{P}.window_end"])).days
        put(f"lockt.{q}.days", days, f"predictions/{q}.json snapshot minus window_end")
        put(f"live.{q}.pred.window_open", (dt.date.fromisoformat(F[f"{P}.window_start"]) + dt.timedelta(days=1)).isoformat(),
            f"predictions/{q}.json window_start plus one day (the window excludes its start date)")
        put(f"lockt.{q}.count", raw, f"predictions/{q}.json events large + mid")
        put(f"lockt.{q}.scale", (F[f"{P}.trailing.reported.large"] + F[f"{P}.trailing.reported.mid"])
            / (F[f"{P}.trailing.registry.large"] + F[f"{P}.trailing.registry.mid"]),
            f"predictions/{q}.json trailing reported over trailing registry")
        put(f"lockt.{q}.real", actual / raw, f"score.json reported over predictions/{q}.json events")
        # used jets in the lock: events three or more years old by the registry's year of manufacture
        tp = root / f"data/snapshots/daily/{F[f'{P}.snapshot']}.serials.csv.gz"
        if tp.exists():
            lr = list(csv.DictReader(io.StringIO(gzip.decompress(tp.read_bytes()).decode())))
            ev = [r for r in lr if r["e1"] and F[f"{P}.window_start"] < r["e1"] <= F[f"{P}.window_end"]]
            put(f"used.lock.{q}.n", len(ev), f"data/snapshots/daily/{tp.name} (E1 events in the window)")
            put(f"used.lock.{q}.old3", sum(1 for r in ev if r["year_mfr"] and int(r["e1"][:4]) - int(r["year_mfr"]) >= 3),
                f"data/snapshots/daily/{tp.name} (event year minus year_mfr at least 3)")
        if daily:
            later = [d for d in daily if d > F[f"{P}.snapshot"]]
            put(f"lockt.{q}.newest", daily[-1], "data/snapshots/daily (newest table)")
    # used jets in the backtest count, by the registry's own year of manufacture
    sr = _csv(root / "data/processed/serials.csv")
    lo, hi = reg[min(reg)]["window_start"], reg[max(reg)]["window_end"]
    ev = [r for r in sr if r[e] and lo < r[e] <= hi]
    old = [r for r in ev if r["year_mfr"] and int(r[e][:4]) - int(r["year_mfr"]) >= 3]
    put("used.n", len(ev), "data/processed/serials.csv (chosen-definition events, 2016Q1 to 2026Q2)")
    put("used.old3", len(old), "data/processed/serials.csv (event year minus year_mfr at least 3)")
    put("used.old3_pct", len(old) / len(ev) * 100, "data/processed/serials.csv")
    put("used.noyear", sum(1 for r in ev if not r["year_mfr"]), "data/processed/serials.csv (events with no year_mfr)")
    put("nobound.all", len(sr), "data/processed/serials.csv (airframes)")
    put("nobound.airframes", sum(1 for r in sr if not r["bound"]), "data/processed/serials.csv (airframes with no bound)")
    put("nobound.events", sum(1 for r in ev if not r["bound"]),
        "data/processed/serials.csv (chosen-definition events on airframes with no bound)")
    # registrations by GULFSTREAM LEASING LLC that the holder rule counts as customer deliveries
    mp = root / "data/snapshots" / F["snap.backtest"] / "MASTER.txt.gz"
    if mp.exists():
        rows = list(csv.reader(gzip.decompress(mp.read_bytes()).decode("utf-8", "replace").splitlines()))
        hd = [re.sub(r"[^A-Z0-9]", "", h.upper()) for h in rows[0]]
        ix = {k: hd.index(k) for k in ("SERIALNUMBER", "NAME", "CERTISSUEDATE")}
        byser = {}
        for r in ev:
            byser.setdefault(r["serial"], []).append(r)
        hit = []
        for r in rows[1:]:
            if len(r) > max(ix.values()) and r[ix["NAME"]].strip().upper().startswith("GULFSTREAM LEASING"):
                d = r[ix["CERTISSUEDATE"]].strip()
                iso = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
                hit += [x for x in byser.get(r[ix["SERIALNUMBER"]].strip(), []) if x[e] == iso]
        put("leasing.events", len(hit), f"data/snapshots/{F['snap.backtest']}/MASTER.txt.gz joined to data/processed/serials.csv "
            "(GULFSTREAM LEASING LLC certificates counted as events)")
    # G700s the FAA files under a type code the scope rule drops; only the raw zip holds them
    import zipfile
    zp = root / "data/raw/faa/ReleasableAircraft-2026-10-30.zip"
    if zp.exists():
        with zipfile.ZipFile(zp) as z:
            nm = {n.upper(): n for n in z.namelist()}
            ml = z.read(nm["MASTER.TXT"]).decode("utf-8", "replace").splitlines()
        mh = [re.sub(r"[^A-Z0-9]", "", h.upper()) for h in ml[0].split(",")]
        ci = mh.index("MFRMDLCODE")
        put("scope.g700_out", sum(1 for ln in ml[1:] if ln.split(",")[ci].strip() == "3980222"),
            "data/raw/faa/ReleasableAircraft-2026-10-30.zip MASTER rows under ACFTREF code 3980222 (the raw zip is not tracked)")
    else:
        put("scope.g700_out", 17, "docs/prepub/ERRATA.md E5 (counted from the FAA file of 2026-10-30; the raw zip is absent here)")
    put("scope.g700_date", "2026-10-30", "the FAA file the count was taken from (docs/prepub/ERRATA.md E5)")
    mid_names = ("GULFSTREAM 200", "GULFSTREAM 100", "GALAXY", "ASTRA", "G150", "G200", "G100")
    put("cabin.misfiled", sum(1 for r in sr if r["cabin"] == "large" and any(k in r["model"].upper() for k in mid_names)),
        "data/processed/serials.csv (mid-cabin model names filed as large)")
    twice = {}
    for r in ev:
        twice.setdefault(r["serial"], []).append(r)
    dbl = [k for k, v in twice.items() if len(v) > 1 and len({x["mfr_code"] for x in v}) > 1 and len({x["cabin"] for x in v}) == 1]
    alt = [r["serial"] for r in ev if not r["year_mfr"] and not r["first_airworthiness"]
           and any(o["serial"] == r["serial"] and o["mfr_code"] != r["mfr_code"] and o["cabin"] == r["cabin"]
                   and o[e] and o[e] < r[e] for o in sr)]
    put("used.double", len(set(dbl) | set(alt)), "data/processed/serials.csv (a serial with events under two maker-code prefixes)")
    for y in range(2016, 2027):
        if f"evper.{y}.total" in F:
            put(f"delper.{y}.total", 1 / F[f"evper.{y}.total"], "gd_deliveries.csv over registry_quarterly.csv, by year")
            put(f"delper.{y}.mid", 1 / F[f"evper.{y}.mid"], "gd_deliveries.csv over registry_quarterly.csv, by year, mid cabin")
    # sensitivity variants (exploratory)
    put("gdyear.2020", sum(F[f"gd.2020Q{k}.total"] for k in range(1, 5)), "data/processed/gd_deliveries.csv (2020 total)")
    sp = root / "results/exploratory/sensitivity.json"
    if sp.exists():
        put("sv.alt_sourced", json.loads(sp.read_text())["sourced_quarters_with_2021_as_117"], "results/exploratory/sensitivity.json")
        for v in json.loads(sp.read_text())["variants"]:
            k = v["key"]
            F.setdefault("@svlabel", {})[k] = v["label"]
            put(f"sv.{k}.n", v["n"], "results/exploratory/sensitivity.json")
            for mod, x in v["mae"].items():
                put(f"sv.{k}.mae.{mod}", x, "results/exploratory/sensitivity.json")
            put(f"sv.{k}.wins", v["ratio_vs_guidance"]["wins"], "results/exploratory/sensitivity.json")
            put(f"sv.{k}.of", sum(v["ratio_vs_guidance"][x] for x in ("wins", "losses", "ties")), "results/exploratory/sensitivity.json")
            put(f"sv.{k}.p", v["ratio_vs_guidance"]["p_one_sided"], "results/exploratory/sensitivity.json")
    # GD's stated plans for single quarters (data/quarter_plans.csv) and the pace they stand in for
    qp = root / "data/quarter_plans.csv"
    if qp.exists():
        pl = _csv(qp)
        put("qp.n", len(pl), "data/quarter_plans.csv (rows)")
        for r in pl:
            put(f"qp.{r['quarter']}.plan", float(r["plan"]), "data/quarter_plans.csv")
            put(f"qp.{r['quarter']}.call", r["call_date"], "data/quarter_plans.csv")
        far = max(pl, key=lambda r: abs(F[f"bt.{r['quarter']}.guidance.total"] - float(r["plan"])))
        put("qp.far.plan", float(far["plan"]), f"data/quarter_plans.csv ({far['quarter']}, the plan furthest from the pace)")
        put("qp.far.call", far["call_date"], "data/quarter_plans.csv")
        put("qp.far.pace", F[f"bt.{far['quarter']}.guidance.total"], f"results/holdout.csv ({far['quarter']}, guidance, total)")
    put("mid.min_holdout", min(F[f"gd.{q}.mid"] for q in hq),
        "data/processed/gd_deliveries.csv (fewest mid-cabin deliveries in a held-out quarter)")
    # what GD reported by segment for a scored quarter
    rp = root / "data/processed/segments_reported.csv"
    if rp.exists():
        rs = {}
        for r in _csv(rp):
            rs.setdefault(r["quarter"], {})[r["segment"]] = (int(r["revenue_usd"]), int(r["operating_earnings_usd"]))
            put(f"rseg.{r['quarter']}.{r['segment']}.rev", int(r["revenue_usd"]), "data/processed/segments_reported.csv")
            put(f"rseg.{r['quarter']}.{r['segment']}.oe", int(r["operating_earnings_usd"]), "data/processed/segments_reported.csv")
        tq = est["target"]
        if tq in rs:
            def miss(key, e_, r_):
                put(f"estx.{key}.rep", r_, "data/processed/segments_reported.csv")
                put(f"estx.{key}.miss", e_ - r_, "estimates.json less segments_reported.csv")
                put(f"estx.{key}.misspct", (e_ - r_) / r_ * 100, "estimates.json over segments_reported.csv")
            miss("aero_now", est["aerospace_from_nowcast_usd"], rs[tq]["Aerospace"][0])
            for s_ in SEGS:
                miss(s_, S[s_]["drift_usd"], rs[tq][s_][0])
            miss("total", est["revenue_total_usd"], sum(rs[tq][s_][0] for s_ in SEGS))
            put("rseg.oe_total", sum(rs[tq][s_][1] for s_ in SEGS), "data/processed/segments_reported.csv (four segments)")
    put("const.bound_days", 365, "src/gdn/events.py:50 timedelta(days=365)")
    put("const.ac_se", 1 / h["n"] ** 0.5, "1 / sqrt(n) with n from results/metrics.json:holdout.n")
    dq = [qlab(i) for i in range(qidx("2017Q1"), qidx("2019Q4") + 1)]
    differ = [q for q in dq if (reg[q]["e1_large"], reg[q]["e1_mid"]) != (reg[q]["e2_large"], reg[q]["e2_mid"])]
    put("design.same", len(dq) - len(differ), "data/processed/registry_quarterly.csv (design quarters where E1 and E2 agree)")
    put("design.gap", sum(abs(int(reg[q][f"e1_{c}"]) - int(reg[q][f"e2_{c}"])) for q in differ for c in ("large", "mid")),
        "data/processed/registry_quarterly.csv (E1 against E2 events in the design quarters that differ)")
    seq = [F[f"bt.{q}.guidance.ae"] < F[f"bt.{q}.ratio.ae"] for q in hq]
    for q, stt in sorted(F["@state"].items(), key=lambda kv: qidx(kv[0])):
        if stt["locked"] and stt["scored"] and F.get(f"live.{q}.score.guidance_ae") is not None:
            seq.append(F[f"live.{q}.score.guidance_ae"] < F[f"live.{q}.score.ae_total"])
    run = 0
    for closer in reversed(seq):
        if not closer:
            break
        run += 1
    put("guid.run", run, "results/holdout.csv and results/live score: latest quarters in a row with guidance closer")
    put("const.prereg_gap_min", 2, "git log: 2c62ad3 (preregistration) 11:02:12, 48c1ea0 (held-out scores) 11:04:28, 2026-10-19")
    put("const.ci_only_since", "2026-10-31", "git log origin/main: every commit after 2026-10-30 is by github-actions[bot]")
    put("const.alt2021", 117, "src/gdn/sensitivity.py ALT_2021 (127 less 10)")
    put("const.ten", 10, "data/guidance.csv 2021-01-27 quote: 10 fewer aircraft")
    put("const.g280_first_reg", 2012, "data/processed/serials.csv serial 2009 customer_cert 2012-08-01")

    claims = json.loads((root / "report/claims.json").read_text())
    F["@claims"] = {c["id"]: c for c in claims}

    wf = root / ".github/workflows/nowcast.yml"
    if wf.exists():
        mm = re.search(r"cron:\s*'\d+ ([\d,]+) ", wf.read_text())
        put("const.cron_runs", len(mm.group(1).split(",")) if mm else None, ".github/workflows/nowcast.yml (cron hours)")

    # method constants, each with the line that fixes it
    put("const.lags", 4, "src/gdn/model.py:44 range(1, 5)")
    put("const.key_chars", 3, "src/gdn/events.py:35 code[:3]")
    put("const.band_nominal_pct", 80, "src/gdn/model.py:231 nearest-rank 0.1 and 0.9")
    put("const.ci_level", 95, "src/gdn/stats.py clopper_pearson alpha=0.05")
    put("const.sd_mult", 2, "src/gdn/model.py:187 m + 2 * sd")
    put("const.recent_n", 3, "src/gdn/report.py:114 (2025Q4, 2026Q1, 2026Q2)")
    put("const.top_n", 5, "src/gdn/errors.py (five largest)")
    put("const.asof_lo", 20, "docs/PREREGISTRATION.md: 20 to 30 days")
    put("const.asof_hi", 30, "docs/PREREGISTRATION.md: 20 to 30 days")
    put("const.seven_limits", 7, "README ## Limitations (count)")
    put("ext.study.primes", 5, "external: the defense backlog study (checked in P3.3)")
    put("const.half", 0.5, "threshold named in the sentence")

    dates, hashes, accns = set(), set(), set()
    for k, v in F.items():
        if isinstance(v, str):
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                dates.add(v)
            elif re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:]+Z", v):
                dates.add(v)
            elif re.fullmatch(r"[0-9a-f]{64}", v):
                hashes.add(v)
            elif re.fullmatch(r"\d{10}-\d{2}-\d{6}", v):
                accns.add(v)
    for c in calls:
        dates.add(c["call_date"])
    for c in claims:
        accns.update(re.findall(r"\d{10}-\d{2}-\d{6}", c.get("url_or_accn", "")))
        if c.get("retrieved_on"):
            dates.add(c["retrieved_on"])
    for r in _csv(root / "data/processed/segments.csv"):
        accns.add(r["accn"])
    dates.update(reg[q]["window_start"] for q in reg)
    dates.update(daily)
    dates.update(man["snapshots"])
    F["@dates"], F["@hashes"], F["@accns"] = dates, hashes, accns
    return F


# ---------- templates ----------
NUMPAT = r"[-−+]?\$?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:%|B\b|M\b)?"
WORDPAT = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)"
SLOT = re.compile(r"\{([^{}:]+):([a-zA-Z0-9]+)\}")
PATS = {"date": r"\d{4}-\d{2}-\d{2}", "time": r"\d{2}:\d{2}", "hash": r"[0-9a-f]{64}", "word": WORDPAT, "year": r"(?:19|20)\d{2}"}


def _lit(s):
    return r"\s+".join(re.escape(x) for x in s.split(" ")) if s else ""


def compile_tpl(t):
    parts, keys, pos = [], [], 0
    for m in SLOT.finditer(t):
        parts.append(_lit(t[pos:m.start()]))
        parts.append("(" + PATS.get(m.group(2), NUMPAT) + ")")
        keys.append((m.group(1), m.group(2)))
        pos = m.end()
    parts.append(_lit(t[pos:]))
    return re.compile("".join(parts), re.I), keys


def T(surfaces, tpl):
    rx, keys = compile_tpl(tpl)
    return (set(surfaces.split(",")), rx, keys, tpl)


ALL = "post,readme,note,interview,resume,dashboard,error_analysis,asof,workbook,prereg,sensitivity"
HEAD = ("Over {m.holdout.n:int} held-out quarters the registry count was off by {m.holdout.mae.ratio:f1} jets a quarter on "
        "average, against {m.holdout.mae.guidance:f1} for GD's guidance pace")
LOW = "Simply repeating the same quarter last year missed by less on average, {m.holdout.mae.seasonal:f1}"
FRAME = "The backtest reads a registry copy from {snap.backtest:date}, which had months or years to fill in"
L3 = "live.2026Q3"

TEMPLATES = [
    # --- shared, generated ---
    T(ALL, HEAD), T(ALL, LOW), T(ALL, FRAME),
    # --- post ---
    T("post", "One locked quarter so far: off by {live.2026Q3.score.ae_total:f1}. I locked an estimate of "
              "{live.2026Q3.score.nowcast.total:f1} Gulfstream deliveries for 2026Q3 on GitHub before GD reported, and GD "
              "reported {live.2026Q3.score.reported.total:int}. {const.one:word} quarter shows how it works live"),
    T("post", "scaled the count by the last {const.lags:word} quarters, and checked it on {m.holdout.n:int} past quarters held "
              "out from setting the rules, against GD's guidance pace and {const.n_simple:word} simple baselines"),
    # --- README hand-written ---
    T("readme", "test the method on {m.holdout.n:int} past quarters against GD's own guidance"),
    T("readme", "Average miss in aircraft over the {m.holdout.n:int} held-out quarters, 2020Q1 to 2026Q2"),
    T("readme", "with Holm's correction across the {const.n_baselines:word}"),
    T("readme,note,dashboard", "GD stated a numeric delivery outlook covering {m.holdout.guidance.sourced:int} of the "
                               "{m.holdout.n:int} held-out quarters"),
    T("dashboard", "GD stated a numeric delivery outlook covering {m.holdout.guidance.sourced:int} of the {m.holdout.n:int} "
                   "test quarters; the other {guid.n_fallback:int} ("),
    T("readme", "The other {guid.n_fallback:int} quarters ("),
    T("readme", "because no {guid.fallback_year:year} call gave a full-year figure that the preregistered rule reads. On the {m.holdout.guidance.sourced:int} "
                "sourced quarters the guidance pace missed by {m.holdout.guidance.mae_sourced:f1} aircraft on average"),
    T("readme,note", "held GD's count in {m.holdout.band.hits:int} of {m.holdout.band.n:int} held-out quarters "
                     "({m.holdout.band.coverage_pct:pct1}, against a nominal {const.band_nominal_pct:pct0}; exact "
                     "{const.ci_level:pct0} interval {m.holdout.band.cp95_pct.0:pct1} to {m.holdout.band.cp95_pct.1:pct1})"),
    T("note", "held GD's count in {m.holdout.band.hits:int} of {m.holdout.band.n:int} held-out quarters "
              "({m.holdout.band.coverage_pct:pct1}, against a nominal {const.band_nominal_pct:pct0}; "
              "{const.ci_level:pct0} interval {m.holdout.band.cp95_pct.0:pct1} to {m.holdout.band.cp95_pct.1:pct1})"),
    T("dashboard", "held GD's count in {m.holdout.band.hits:int} of {m.holdout.band.n:int} test quarters "
                   "({m.holdout.band.coverage_pct:pct1}, against a nominal {const.band_nominal_pct:pct0}; "
                   "{const.ci_level:pct0} interval {m.holdout.band.cp95_pct.0:pct1} to {m.holdout.band.cp95_pct.1:pct1})"),
    T("readme", "The design window, 2017Q1 to 2019Q4 ({m.design.n:int} quarters), chose E1: the ratio model's average miss "
                "was {m.design.mae.E1.ratio:f2} under E1 and {m.design.mae.E2.ratio:f2} under E2. In that window the same "
                "quarter last year missed by {m.design.mae.none.seasonal:f2} and last quarter by {m.design.mae.none.last:f2}"),
    T("readme", "GD deliveries per registry event averaged {m.holdout.coverage_ratio.mean:f2} from 2017Q1 to 2025Q2"),
    T("readme,note,interview,dashboard", "Registry events per delivery averaged {evper.mean:f2} from 2017Q1 to 2025Q2"),
    T("readme,note,interview,dashboard", "Registry events per reported delivery averaged {evper.mean:f2} from 2017Q1 to 2025Q2"),
    T("readme,note", "above the mean plus {const.sd_mult:word} standard deviations"),
    T("readme", "the last {const.recent_n:word} quarters sit at {cov.2025Q4:f2}, {cov.2026Q1:f2}, {cov.2026Q2:f2} against the "
                "{m.holdout.coverage_ratio.mean:f2} mean"),
    T("note", "the last {const.recent_n:word} quarters sit at {cov.2025Q4:f2}, {cov.2026Q1:f2}, {cov.2026Q2:f2} against a "
              "mean of {m.holdout.coverage_ratio.mean:f2}"),
    T("dashboard", "GD delivered {cov.2025Q4:f2}, {cov.2026Q1:f2}, {cov.2026Q2:f2} jets per registry event in the last "
                   "{const.recent_n:word} quarters, against an average of {m.holdout.coverage_ratio.mean:f2}"),
    T("readme,asof", "with its {const.lags:word} lags left whole"),
    T("readme,asof", "and its {const.lags:word} lags all from that capture"),
    T("asof", "and its {const.lags:word} lag quarters from the same archived copy"),
    T("readme", "{const.top_n:word} quarters drive much of the average"),
    T("readme", "locked at {live.2026Q3.pred.nowcast.total:f1} (band {live.2026Q3.pred.band.0:f1} to "
                "{live.2026Q3.pred.band.1:f1}) from the {live.2026Q3.pred.snapshot:date} snapshot, as a timestamped GitHub "
                "release (lock-2026Q3) at {live.2026Q3.lock.et_time:time} ET on {live.2026Q3.lock.et_date:date}, sha256 "
                "{live.2026Q3.lock.sha256:hash}; GD's guidance pace for the quarter was "
                "{live.2026Q3.score.guidance_pace:f1}. GD reported {live.2026Q3.score.reported.total:int}: the lock missed "
                "by {live.2026Q3.score.ae_total:f1}, outside the band"),
    T("readme", "2026Q4: not locked yet. Its window runs to {live.2026Q4.latest.window_end:date}, so the "
                "{live.2026Q4.latest.snapshot:date} snapshot counts only part of it"),
    T("readme", "the first {const.key_chars:word} characters of its maker-model code"),
    T("readme,note,interview,dashboard", "over the {const.lags:word} quarters before"),
    T("readme", "Over the {m.holdout.n:int} held-out quarters, 2020Q1 to 2026Q2, I run one-sided exact sign tests"),
    T("readme", "cuts each quarter's own events {const.trunc.1:int}, {const.trunc.2:int} and {const.trunc.3:int} days early"),
    T("readme", "best next-quarter baseline for {ext.study.primes:word} other primes"),
    T("readme", "The Wayback Machine holds {asof.captures:int} successful captures of `ReleasableAircraft.zip`; "
                "{asof.n_window:word} quarters have one taken {const.asof_lo:int} to {const.asof_hi:int} days after the fiscal "
                "end, and {asof.n_scored:word} of them can be scored"),
    T("asof", "Wayback captures exist: {asof.captures:int} successful captures of ReleasableAircraft.zip; {asof.n_window:int} "
              "quarters have one taken {const.asof_lo:int} to {const.asof_hi:int} days after the fiscal end, and "
              "{asof.n_scored:int} of them can be scored"),
    T("readme", "In all {asof.n_closer:word} the copy from a few weeks after the quarter missed by less than the finished "
                "copy, and its past-miss band held GD's count in {asof.n_inside:word} of the {asof.n_held:word} held-out "
                "quarters"),
    T("readme", "({asof.2026Q2.trail:int} against {asof.2026Q2.bt_trail:int} for 2026Q2, {asof.2017Q1.trail:int} against "
                "{asof.2017Q1.bt_trail:int} for 2017Q1)"),
    T("readme", "In {asof.n_lower:word} of the {asof.n_scored:word} (2017Q1, 2026Q1 and 2026Q2)"),
    T("readme", "with {asof.2025Q3.events_more:word} more of the quarter's own events"),
    T("readme,asof,note", "{asof.n_scored:word} quarters prove nothing"),
    T("asof", "{asof.n_scored:word} quarters are too few to conclude anything"),
    T("note,interview", "a few weeks after {asof.n_scored:word} past quarter ends"),
    T("interview", "but {asof.n_scored:word} quarters prove nothing"),
    T("readme", "The backtest reads the snapshot downloaded on {snap.backtest:date}"),
    T("readme", "the delivered basis it adopted with ASC 606 on {const.asc606_date:date}, so {const.y2016:year} comes from the restated "
                "prior-year columns of the {const.y2017:year} releases"),
    T("readme", "stated on each earnings call from {guid.first:date} to {guid.last:date}"),
    T("readme,note", "Since {const.export_since:year} the registry's yearly mid-cabin count has stayed within a few jets of GD's"),
    T("readme", "registry events per reported delivery rose from {evper.2016.total:f2} in {const.y2016:year} to "
                "{evper.2019.total:f2} in {const.y2019:year}, and sat below {const.half:f1} for mid cabin in "
                "{const.y2016:year} and {const.y2017:year}"),
    T("readme", "I checked {audit.n:int} airframes against outside sources"),
    T("readme,note", "In {audit.no:int} of {audit.n:int} ({audit.no_pct:pct1}) the source disagreed with the registry reading "
                     "or could not confirm it: {audit.used:word} were used jets"),
    T("note", "in {audit.no:int} of {audit.n:int} airframes checked against outside sources ({audit.no_pct:pct1}), the source "
              "disagreed with the registry reading or could not confirm it: {audit.used:word} were used jets read as new "
              "deliveries, {audit.earlier:word} had an earlier stated delivery, and {audit.unconfirmed:word} could not be "
              "confirmed"),
    T("readme", "({audit.used_fresh:word} let through by a fresh US airworthiness date, {audit.used_noair:word} with no "
                "airworthiness date or year at all), {audit.earlier:word} had a stated delivery earlier than the registry date "
                "(a military G-V by {audit.gv_quarters:word} quarter, under E2 only, and a G650ER by {audit.g650_quarters:word}), "
                "and {audit.unconfirmed:word} could not be confirmed"),
    T("readme,note", "All but {audit.non_mirror:word} source was a registry mirror"),
    T("readme,note", "every event the audit could date fell between {audit.year_min:year} and {audit.year_max:year}"),
    T("readme", "runs the same job {const.cron_runs_word:word} a day as a fallback"),
    T("readme", "I run it on my Mac once a day"),
    # --- error_analysis.md ---
    T("error_analysis", "The registry counted {reg.%Q%.total:int} airframes in the window against {gd.%Q%.total:int} GD "
                        "deliveries, and the estimate of {bt.%Q%.ratio.total:f1} came out {bt.%Q%.ratio.ae:f1}"),
    T("error_analysis", "The company delivered {gd.2020Q2.total:int} aircraft during the quarter, up from "
                        "{gd.2020Q1.total:int} last quarter"),
    T("error_analysis", "Error analysis: the {const.top_n:word} largest held-out misses"),
    T("error_analysis", "the {const.top_n:word} held-out quarters with the largest absolute miss"),
    # --- note ---
    T("note", "My registry estimate for 2026Q3 is {live.2026Q3.pred.nowcast.total:f1} Gulfstream deliveries, with a past-miss "
              "band of {live.2026Q3.pred.band.0:f1} to {live.2026Q3.pred.band.1:f1}, against {gd.2025Q3.total:int} delivered "
              "in 2025Q3. I locked it as a timestamped GitHub release at {live.2026Q3.lock.et_time:time} ET on "
              "{live.2026Q3.lock.et_date:date}. GD reported {live.2026Q3.score.reported.total:int}, against a guidance pace of "
              "{live.2026Q3.score.guidance_pace:f1}"),
    T("note", "Data as of {live.2026Q3.pred.snapshot:date}"),
    T("note", "At trailing Aerospace revenue per delivery of {est.revenue_per_delivery_usd:usdM}, that estimate implies "
              "{est.aerospace_from_nowcast_usd:usdB} of Aerospace revenue for 2026Q3, against {seg.Aerospace.2025Q3.rev:usdB} a "
              "year earlier; scaling last year's quarter by trailing growth gives {est.segments.Aerospace.drift_usd:usdB} "
              "instead. The {est.revenue_per_delivery_usd:usdM} includes services"),
    T("note", "Exhibit 1. Segment revenue and operating margin, {const.lags:word} quarters to 2026Q2"),
    T("note", "GD reports {const.n_segments:word} segments. Over the {const.lags:word} quarters to 2026Q2, Aerospace, the "
              "segment that holds Gulfstream, earned {est.segments.Aerospace.ttm_revenue_usd:usdB} of revenue, "
              "{mix.Aerospace.share_pct:pct1} of the {const.n_segments:word} segments' total, at a "
              "{mix.Aerospace.margin_pct:pct1} operating margin"),
    T("note", "before I scored the {m.holdout.n:int} quarters from 2020Q1 to 2026Q2"),
    T("note", "Exhibit 2. Average miss on the {m.holdout.n:int} held-out quarters, aircraft"),
    T("note", "the other {guid.n_fallback:int}, all in {guid.fallback_year:year}, fall back to the same quarter last year. On "
              "those {m.holdout.guidance.sourced:int} quarters GD's guidance pace missed by "
              "{m.holdout.guidance.mae_sourced:f1} aircraft on average, against {guid.sub.ratio:f1} for the registry estimate "
              "and {guid.sub.seasonal:f1} for the same quarter last year"),
    T("note", "Exhibit 4. GD's reported deliveries against the {const.n_models:word} estimates"),
    T("note", "The {const.top_n:word} largest misses were 2022Q1 ({bt.2022Q1.ratio.total:f1} against {gd.2022Q1.total:int}), "
              "2020Q2 ({bt.2020Q2.ratio.total:f1} against {gd.2020Q2.total:int}), 2025Q4 ({bt.2025Q4.ratio.total:f1} against "
              "{gd.2025Q4.total:int}), 2021Q2 ({bt.2021Q2.ratio.total:f1} against {gd.2021Q2.total:int}), 2021Q1 "
              "({bt.2021Q1.ratio.total:f1} against {gd.2021Q1.total:int})"),
    T("note", "No {guid.fallback_year:year} call stated a full-year number, so guidance in {guid.fallback_year:year} is the "
              "same quarter last year"),
    T("note", "By the {live.2026Q3.pred.snapshot:date} registry snapshot, {live.2026Q3.pred.events.large:int} large-cabin and "
              "{live.2026Q3.pred.events.mid:int} mid-cabin airframes had a delivery event in 2026Q3's window "
              "({live.2026Q3.pred.window_start:date} to {live.2026Q3.pred.window_end:date}). Over the {const.lags:word} quarters "
              "before, GD reported {live.2026Q3.pred.trailing.reported.large:int} large-cabin and "
              "{live.2026Q3.pred.trailing.reported.mid:int} mid-cabin deliveries against "
              "{live.2026Q3.pred.trailing.registry.large:int} and {live.2026Q3.pred.trailing.registry.mid:int} registry events. "
              "Scaled the same way, the estimate is {live.2026Q3.pred.nowcast.total:f1} ({live.2026Q3.pred.nowcast.large:f1} "
              "large, {live.2026Q3.pred.nowcast.mid:f1} mid), with a past-miss band of {live.2026Q3.pred.band.0:f1} to "
              "{live.2026Q3.pred.band.1:f1}. I locked this estimate as a timestamped GitHub release at "
              "{live.2026Q3.lock.et_time:time} ET on {live.2026Q3.lock.et_date:date}. GD then reported "
              "{live.2026Q3.score.reported.total:int}. GD's guidance pace for the quarter had been "
              "{live.2026Q3.score.guidance_pace:f1}"),
    T("note", "Aerospace ended 2026Q2 with {backlog.Aerospace:usdB} of backlog, {est.segments.Aerospace.coverage_years:f2} "
              "years of its trailing revenue. For the quarter, GD's book-to-bill ratio, orders divided by revenue, was "
              "{btb.aerospace:f1}-to-{const.one:int} for Aerospace, {btb.defense:f1}-to-{const.one:int} for the defense "
              "segments and {btb.company:f1}-to-{const.one:int} company-wide"),
    T("note", "Segment operating earnings at trailing margins: {est.operating_earnings_total_usd:usdB}, Corporate excluded"),
    T("note", "That study tested {ext.study.primes:word} other defense primes; GD was left out because it stopped tagging "
              "backlog in XBRL in {ext.study.xbrl_year:year}. Pooled across those {ext.study.primes:word}, the next-quarter "
              "error was {ext.study.q1.backlog:pct1} for a backlog model, {ext.study.q1.naive:pct1} for the seasonal naive and "
              "{ext.study.q1.drift:pct1} for the seasonal naive with drift; {const.lags:word} quarters out it was "
              "{ext.study.q4.backlog:pct1} for backlog, {ext.study.q4.ttm:pct1} for trailing revenue and "
              "{ext.study.q4.ttmdrift:pct1} for trailing revenue with drift"),
    T("note", "GD delivered {h1.2026.total:int} jets in the first half of 2026, against an outlook of about "
              "{guid.outlook.2026:int} for the year"),
    T("note", "The Aerospace margin: {seg.Aerospace.2026Q2.margin_pct:pct1} in 2026Q2 and {aero.h1_2026.margin_pct:pct1} for "
              "the first half, against the {claimnum.os-margin:pct1} GD guided for 2026"),
    T("note", "Book-to-bill: {btb.aerospace:f1} for Aerospace and {btb.defense:f1} for the defense segments in 2026Q2"),
    T("note", "Marine Systems margins, 2025Q3 to 2026Q2: {seg.Marine Systems.2025Q3.margin_pct:pct1}, "
              "{seg.Marine Systems.2025Q4.margin_pct:pct1}, {seg.Marine Systems.2026Q1.margin_pct:pct1}, "
              "{seg.Marine Systems.2026Q2.margin_pct:pct1}"),
    T("note", "its outlook of about {guid.outlook.2026:int} Gulfstream deliveries from large-cabin aircraft"),
    T("note", "Design ({m.design.n:int} quarters)"),
    T("note", "Held out ({m.holdout.n:int} quarters)"),
    T("note", "Deliveries, {const.lags:word} quarters to 2026Q2"),
    T("note", "Revenue, all {const.n_segments:word} segments"),
    T("note", "Segment operating earnings, all {const.n_segments:word} segments"),
    T("note", "snapshot {snap.backtest:date} for the backtest, and daily snapshots since, the newest dated {snap.newest:date}"),
    T("note", "GD earnings calls from {guid.first:date} to {guid.last:date}"),
    # --- interview and resume (the sentences that are true today; stale ones are left for the staleness check) ---
    T("interview", "I fixed the rules on {m.design.n:int} design quarters and committed them before scoring {m.holdout.n:int} "
                   "held-out quarters. Over those {m.holdout.n:int} quarters the registry count was off by "
                   "{m.holdout.mae.ratio:f1} jets a quarter on average, against {m.holdout.mae.guidance:f1} for GD's guidance "
                   "pace. The difference is not statistically distinguishable, and simply repeating the same quarter last "
                   "year missed by less on average, {m.holdout.mae.seasonal:f1}"),
    T("interview", "GD stated a numeric full-year outlook covering {m.holdout.guidance.sourced:int} of the {m.holdout.n:int} "
                   "held-out quarters"),
    T("interview", "I also test against {const.n_simple:word} rules of thumb"),
    T("interview", "held GD's count in {m.holdout.band.hits:int} of {m.holdout.band.n:int} quarters"),
    T("interview", "The 60-second version"),
    T("resume", "tested on {m.holdout.n:int} held-out quarters against GD's guidance and naive baselines; off by "
                "{m.holdout.mae.ratio:f1} jets a quarter vs {m.holdout.mae.guidance:f1} for guidance"),
    # --- dashboard ---
    T("dashboard", "Off by {m.holdout.mae.ratio:f1} jets a quarter on average, when GD delivers about {typical:whole}, against "
                   "{m.holdout.mae.guidance:f1} for GD's guidance pace"),
    T("dashboard", "Simply repeating the same quarter last year missed by less, {m.holdout.mae.seasonal:f1}. All of this is a "
                   "test on past quarters, read from a registry copy of {snap.backtest:date}"),
    T("dashboard", "{live.2026Q3.pred.nowcast.total:f1} deliveries, estimated"),
    T("dashboard", "Band of past misses: {live.2026Q3.pred.band.0:f1} to {live.2026Q3.pred.band.1:f1} deliveries"),
    T("dashboard", "{path.2026Q3.n:int} snapshots so far, {path.2026Q3.first:date} to {path.2026Q3.last:date}"),
    T("dashboard", "Against GD's guidance pace, the registry estimate was closer in {m.holdout.tests.guidance.wins:int} of "
                   "{m.holdout.n:int} quarters and further off in {m.holdout.tests.guidance.losses:int}. Its average miss was "
                   "{m.holdout.mae.ratio:f1} against {m.holdout.mae.guidance:f1}. A one-sided sign test gives p = "
                   "{m.holdout.tests.guidance.p_one_sided:f3}; after Holm's correction for {const.n_baselines:word} comparisons "
                   "it is not significant. The quarter-to-quarter differences are positively correlated "
                   "({m.holdout.autocorr_lag1.guidance:f2})"),
    T("dashboard", "Against the same quarter last year, the registry estimate was closer in {m.holdout.tests.seasonal.wins:int} "
                   "of {m.holdout.n:int} quarters and further off in {m.holdout.tests.seasonal.losses:int}. Its average miss "
                   "was {m.holdout.mae.ratio:f1} against {m.holdout.mae.seasonal:f1}. A one-sided sign test gives p = "
                   "{m.holdout.tests.seasonal.p_one_sided:f3}; after Holm's correction for {const.n_baselines:word} comparisons"),
    T("dashboard", "Against last quarter, the registry estimate was closer in {m.holdout.tests.last.wins:int} of "
                   "{m.holdout.n:int} quarters and further off in {m.holdout.tests.last.losses:int}. Its average miss was "
                   "{m.holdout.mae.ratio:f1} against {m.holdout.mae.last:f1}. A one-sided sign test gives p = "
                   "{m.holdout.tests.last.p_one_sided:f3}; after Holm's correction for {const.n_baselines:word} comparisons it "
                   "is not significant. The quarter-to-quarter differences are positively correlated "
                   "({m.holdout.autocorr_lag1.last:f2})"),
    T("dashboard", "at the {snap.newest:date} snapshot: {pipe.total:int} in all"),
    T("dashboard", "while the {const.lags:word} quarters before it stay whole"),
    T("dashboard", "by the last {const.lags:word} quarters' growth"),
    T("dashboard", "Bar chart of {pipe.total:int} jets on Gulfstream's own registration with no delivery event, by model, at "
                   "the {snap.newest:date} snapshot"),
    T("dashboard", "The delivery estimate of {live.2026Q3.pred.nowcast.total:f1} sits below the {gd.2025Q3.total:int} "
                   "deliveries of 2025Q3, and each delivery carries about {est.revenue_per_delivery_usd:usdM} of Aerospace "
                   "revenue, so the delivery-based figure falls. That {est.revenue_per_delivery_usd:usdM} includes services"),
    T("dashboard", "the {m.holdout.n:int} quarters from 2020Q1 to 2026Q2 test it against GD's guidance pace (its full-year "
                   "delivery outlook less the deliveries already reported, spread by each quarter's usual share of the year) "
                   "and {const.n_simple:word} simple rules of thumb"),
    T("dashboard", "Chart of the 2026Q3 estimate by registry snapshot date: latest {live.2026Q3.pred.nowcast.total:f1} "
                   "deliveries with a band of past misses from {live.2026Q3.pred.band.0:f1} to {live.2026Q3.pred.band.1:f1}, "
                   "against GD's guidance pace of {live.2026Q3.score.guidance_pace:f1}"),
    T("dashboard", "against {const.n_models:word} estimates. The registry estimate missed by {m.holdout.mae.ratio:f1} "
                   "deliveries a quarter on average"),
    T("dashboard", "GD's reported deliveries each quarter against {const.n_models:word} estimates"),
    T("dashboard", "Chart of reported deliveries against {const.n_models:word} estimates by quarter"),
    # --- workbook About ---
    T("workbook", "snapshot of {snap.backtest:date} gets a delivery date"),
    T("workbook", "snapshot {snap.backtest:date}."),
    T("workbook", "deliveries over the last {const.lags:word} quarters / registry events over the same {const.lags:word} quarters"),
    T("workbook", "the {m.holdout.n:int} quarters 2020Q1 to 2026Q2 are held out"),
    # --- prereg ---
    T("prereg", "The design window, 2017Q1 to 2019Q4 ({m.design.n:int} quarters), selects E1. The ratio model's design MAE is "
                "{m.design.mae.E1.ratio:any} aircraft under E1 and {m.design.mae.E2.ratio:any} under E2"),
    T("prereg", "Committed on {const.prereg_date:date}"),
]

# ---- templates for the text as rewritten in the fix pass (P6, P7) ----
Q = "2026Q3"
LOCK_LINE = ("locked at {live.Q.pred.nowcast.total:f1} (band {live.Q.pred.band.0:f1} to {live.Q.pred.band.1:f1}) from the "
             "{live.Q.pred.snapshot:date} snapshot, as a timestamped GitHub release, made while the repository was private "
             "(lock-2026Q3) at {live.Q.lock.et_time:time} ET on {live.Q.lock.et_date:date}, sha256 "
             "{live.Q.lock.sha256:hash}. GD reported {live.Q.score.reported.total:int} on {cal.release.Q:date}: the lock "
             "missed by {live.Q.score.ae_total:f1} ({live.Q.score.ape_pct:pct1}), outside the band")
OTHERS = ("Other misses for the quarter: GD's guidance pace ({live.Q.score.guidance_pace:f1}) by "
          "{live.Q.score.guidance_ae:f1}, the raw registry count ({cmp.Q.raw:int}) by {cmp.Q.raw_miss:int}, the same quarter "
          "last year ({cmp.Q.yago:int}) by {cmp.Q.yago_miss:int}, last quarter ({cmp.Q.last:int}) by {cmp.Q.last_miss:int}")
SPLIT = ("comes from 2023 and 2024, when the guidance pace missed by {sv.only_2023_2024.mae.guidance:f1} on average and the "
         "registry estimate by {sv.only_2023_2024.mae.ratio:f1}. In the other {sv.without_2023_2024.n:int} held-out quarters "
         "the guidance pace missed by {sv.without_2023_2024.mae.guidance:f1}, the same quarter last year by "
         "{sv.without_2023_2024.mae.seasonal:f1} and the registry estimate by {sv.without_2023_2024.mae.ratio:f1}")
NEW = [
    # post
    ("post", "My first locked estimate of Gulfstream deliveries missed: I said {live.Q.score.nowcast.total:f1} for 2026Q3, "
             "General Dynamics reported {live.Q.score.reported.total:int}"),
    ("post", "The 2026Q3 miss was {live.Q.score.ae_total:f1} jets ({live.Q.score.ape_pct:pct1}), outside my band of past misses. "
             "A pace I derived from GD's own full-year outlook missed by {live.Q.score.guidance_ae:f1}, and last year's same "
             "quarter ({cmp.Q.yago:int}) by {cmp.Q.yago_miss:int}"),
    ("post", "{const.one:word} quarter is one data point"),
    # README lead and summary
    ("readme", "check it on {m.holdout.n:int} past quarters against a pace built from GD's own guidance and "
               "{const.n_simple:word} simple rules"),
    ("readme", "Live record so far: {const.one:word} locked quarter, a miss outside its band. For 2026Q3 I locked an estimate "
               "of {live.Q.pred.nowcast.total:f1} Gulfstream deliveries (band {live.Q.pred.band.0:f1} to "
               "{live.Q.pred.band.1:f1}) the day before GD reported. GD reported {live.Q.score.reported.total:int}, so the "
               "lock missed by {live.Q.score.ae_total:f1} ({live.Q.score.ape_pct:pct1}), outside the band. GD's guidance pace "
               "missed by {live.Q.score.guidance_ae:f1} and the same quarter last year ({cmp.Q.yago:int}) by "
               "{cmp.Q.yago_miss:int}"),
    ("readme", "Backtest, {m.holdout.n:int} held-out quarters: the registry estimate missed by {m.holdout.mae.ratio:f1} jets a "
               "quarter on average, GD's guidance pace by {m.holdout.mae.guidance:f1} and the same quarter last year by "
               "{m.holdout.mae.seasonal:f1}"),
    ("readme", "GD's reported Gulfstream deliveries by quarter against the {const.n_models:word} estimates"),
    # README results and error analysis
    ("readme", "GD gave the year only as a change from 2020, \"{const.ten:int} fewer aircraft\""),
    ("readme", "on {qp.n:word} calls held inside a held-out quarter GD also said"),
    ("readme", "On {qp.far.call:date} it said \"We now expect to deliver {qp.far.plan:int} aircraft in the third quarter, with a "
               "rapid increase in the fourth quarter deliveries\", when my pace for 2023Q3 says {qp.far.pace:f1}"),
    ("readme,interview", "the baseline misses by {sv.quarter_plans.mae.guidance:f1} on average, not {m.holdout.mae.guidance:f1}, "
                         "and the registry estimate is closer in {sv.quarter_plans.wins:int} of {sv.quarter_plans.of:int} quarters"),
    ("interview", "On {qp.n:word} calls GD also said how many aircraft it planned to deliver"),
    ("readme", "\"a few demonstrators all up about {const.demo11:int} aircraft\""),
    ("readme", "No held-out quarter had fewer than {mid.min_holdout:int} mid-cabin deliveries"),
    ("readme", "\"ought to deliver in the second quarter of next year\", meaning {const.g300_late:year}, with the G300 to follow "
               "around late {const.g300_late:year} or early {const.g300_early:year}"),
    ("note", "{used.old3:int} of the {used.n:int} counted events ({used.old3_pct:pct1}) are airframes at least "
             "{const.old_years:word} years old"),
    ("sensitivity", "on {qp.n:int} calls held inside a held-out quarter GD said how many aircraft it planned to deliver in that "
                    "quarter (2021Q3: {qp.2021Q3.plan:int}, 2021Q4: {qp.2021Q4.plan:int}, 2022Q2: {qp.2022Q2.plan:int}, "
                    "2022Q4: {qp.2022Q4.plan:f1}, 2023Q2: {qp.2023Q2.plan:int}, 2023Q3: {qp.2023Q3.plan:int}"),
    ("readme", "Read as {const.alt2021:int}, the guidance pace misses by {sv.outlook_2021_as_117.mae.guidance:f1} on average, "
               "not {sv.preregistered.mae.guidance:f1}, and the registry estimate is closer in {sv.outlook_2021_as_117.wins:int} "
               "of {sv.outlook_2021_as_117.of:int} quarters"),
    ("readme,interview", SPLIT),
    ("readme", "The 2026Q3 lock read a snapshot taken {lockt.Q.days:int} days after the quarter ended, when the quarter's count "
               "stood at {lockt.Q.count:int}, and it is the same in every daily snapshot since, to {lockt.Q.newest:date}. Its "
               "miss came from the scale, not from late postings: the {const.lags:word} quarters before gave "
               "{lockt.Q.scale:f2} deliveries per registry event, and the quarter itself came in at {lockt.Q.real:f2}"),
    ("readme", LOCK_LINE), ("readme,note", OTHERS),
    ("readme", "With {m.holdout.n:int} quarters one standard error of an autocorrelation is about {const.ac_se:f2}, so only "
               "the one against GD's guidance pace is more than {const.one:word} standard error above zero"),
    ("readme", "The two definitions count the same in {design.same:int} of the {m.design.n:int} design quarters and differ "
               "by {design.gap:word} airframe in 2019Q4, so the choice decided little: under E2 the held-out miss is "
               "{sv.definition_E2.mae.ratio:f2}, against {m.holdout.mae.ratio:f2} under E1"),
    ("readme,interview", "has been closer in each of the last {guid.run:word} quarters"),
    ("readme", "It held GD's count in {m.holdout.band.hits:int} of the {m.holdout.band.n:int} held-out quarters against a "
               "nominal {const.band_nominal_pct:pct0}"),
    # README method, data, limitations
    ("readme", "Either date must fall no later than {const.bound_days:int} days after the airframe's first airworthiness date"),
    ("readme", "And {nobound.airframes:int} of the {nobound.all:int} airframes have no airworthiness date and no year, so no "
               "bound applies to them: they supply {nobound.events:int} of the {used.n:int} counted events"),
    ("readme", "whose {leasing.events:word} registrations in 2020Q4 and 2025Q4 count as deliveries"),
    ("readme", "The scope rule keeps engine-type codes {const.eng_a:int} and {const.eng_b:int}"),
    ("readme", "under engine-type code {const.eng_out:int}, so the {scope.g700_out:int} G700s registered to "
               "Gulfstream under it on {scope.g700_date:date} are outside the count"),
    ("readme", "the rules were committed {const.prereg_gap_min:word} minutes before the held-out scores"),
    ("readme", "GD restated its 2016 delivery counts when it adopted ASC 606 on {const.asc606_date:date} (the "
               "{const.y2016:year} releases had printed green and outfitted counts), so {const.y2016:year} comes from the "
               "restated prior-year columns of the {const.y2017:year} releases"),
    ("readme", "GD deliveries per registry event fell from {delper.2016.total:f2} in {const.y2016:year} to "
               "{delper.2019.total:f2} in {const.y2019:year}, and sat above {const.two_x:int} for mid cabin in "
               "{const.y2016:year} and {const.y2017:year}"),
    ("readme", "In the last {const.recent_n:word} held-out quarters it sat at {cov.min3:f2} to {cov.max3:f2}"),
    ("readme", "{used.old3:int} of the {used.n:int} events counted from 2016Q1 to 2026Q2"),
    ("interview", "{used.old3:int} of the {used.n:int} events I counted"),
    ("readme", "counted from 2016Q1 to 2026Q2 ({used.old3_pct:pct1}) are airframes at least {const.old_years:word} years old, "
               "and {used.noyear:int} more carry no year. In the 2026Q3 lock, {used.lock.Q.old3:int} of the "
               "{used.lock.Q.n:int} events were airframes at least {const.old_years:word} years old by that field. "
               "{used.double:word} airframes are also counted twice, under {const.two_prefix:word} maker-code prefixes: a G150 "
               "in 2016Q2 and again in 2018Q2, and a G280 first registered to a customer in {const.g280_first_reg:year} that "
               "counts again in 2026Q2"),
    ("readme", "The cabin rule files {cabin.misfiled:int} airframes of older mid-cabin types as large"),
    ("readme", "every daily commit since {const.ci_only_since:date} has come from the workflow"),
    ("readme", "runs it {const.cron_runs_word:word} a day and can lock"),
    ("readme", "A GitHub workflow runs the daily job twice a day"),
    # note
    ("note", "Estimate locked from the {live.Q.pred.snapshot:date} registry snapshot; GD reported on {cal.release.Q:date}"),
    ("note", "For 2026Q3 I locked a registry estimate of {live.Q.pred.nowcast.total:f1} Gulfstream deliveries, with a past-miss "
             "band of {live.Q.pred.band.0:f1} to {live.Q.pred.band.1:f1}, as a timestamped GitHub release, made while the "
             "repository was private, at {live.Q.lock.et_time:time} ET on {live.Q.lock.et_date:date}. GD reported "
             "{live.Q.score.reported.total:int} on {cal.release.Q:date}: the lock missed by {live.Q.score.ae_total:f1} "
             "({live.Q.score.ape_pct:pct1}), outside the band"),
    ("note", "At trailing Aerospace revenue per delivery of {est.revenue_per_delivery_usd:usdM}, the locked estimate implied "
             "{est.aerospace_from_nowcast_usd:usdB} of Aerospace revenue for 2026Q3, and scaling last year's quarter by "
             "trailing growth gave {est.segments.Aerospace.drift_usd:usdB}. GD reported {rseg.Q.Aerospace.rev:usdB}, against "
             "{seg.Aerospace.2025Q3.rev:usdB} a year earlier. The {est.revenue_per_delivery_usd:usdM} includes services"),
    ("note", "I wrote this note before GD reported 2026Q3 on {cal.release.Q:date}"),
    ("note", "By the {live.Q.pred.snapshot:date} registry snapshot, {live.Q.pred.events.large:int} large-cabin and "
             "{live.Q.pred.events.mid:int} mid-cabin airframes had a delivery event in 2026Q3's window (after "
             "{live.Q.pred.window_start:date}, through {live.Q.pred.window_end:date}). Over the {const.lags:word} quarters "
             "before, GD reported {live.Q.pred.trailing.reported.large:int} large-cabin and "
             "{live.Q.pred.trailing.reported.mid:int} mid-cabin deliveries against "
             "{live.Q.pred.trailing.registry.large:int} and {live.Q.pred.trailing.registry.mid:int} registry events. "
             "Scaled the same way, the estimate is {live.Q.pred.nowcast.total:f1} ({live.Q.pred.nowcast.large:f1} "
             "large, {live.Q.pred.nowcast.mid:f1} mid), with a past-miss band of {live.Q.pred.band.0:f1} to "
             "{live.Q.pred.band.1:f1}. I locked this estimate as a timestamped GitHub release, made while the repository "
             "was private, at {live.Q.lock.et_time:time} ET on {live.Q.lock.et_date:date}. GD then reported "
             "{live.Q.score.reported.total:int}: the lock missed by {live.Q.score.ae_total:f1} "
             "({live.Q.score.ape_pct:pct1}), outside the band. GD's guidance pace for the quarter had been "
             "{live.Q.score.guidance_pace:f1}, a miss of {live.Q.score.guidance_ae:f1}. The raw count of {cmp.Q.raw:int} "
             "events missed by {cmp.Q.raw_miss:int}; the estimate came out lower because the {const.lags:word} quarters "
             "before gave a scale of {lockt.Q.scale:f2} deliveries per event"),
    ("note", "GD reported {rseg.oe_total:usdB} of operating earnings for the {const.n_segments:word} segments"),
    ("note", "snapshot {snap.backtest:date} for the backtest, and snapshot {live.Q.pred.snapshot:date} for the 2026Q3 lock"),
    ("note", "As of GD's {guid.last:date} call"),
    # interview and resume
    ("interview", "Over those {m.holdout.n:int} quarters my registry estimate was off by {m.holdout.mae.ratio:f1} jets a quarter "
                  "on average, against {m.holdout.mae.guidance:f1} for GD's guidance pace. The difference is not statistically "
                  "distinguishable, and simply repeating the same quarter last year missed by less on average, "
                  "{m.holdout.mae.seasonal:f1}"),
    ("interview", "I fixed the rules on {m.design.n:int} design quarters and committed them before scoring {m.holdout.n:int} "
                  "held-out quarters"),
    ("interview", "The first lock, for 2026Q3, said {live.Q.pred.nowcast.total:f1} with a band of {live.Q.pred.band.0:f1} to "
                  "{live.Q.pred.band.1:f1}. GD reported {live.Q.score.reported.total:int} on {cal.release.Q:date}: a miss of "
                  "{live.Q.score.ae_total:f1}, outside the band, and further off than GD's guidance pace (a miss of "
                  "{live.Q.score.guidance_ae:f1}) or the same quarter last year (a miss of {cmp.Q.yago_miss:int})"),
    ("interview", "The GitHub workflow locked {live.Q.pred.nowcast.total:f1} deliveries, with a band of {live.Q.pred.band.0:f1} "
                  "to {live.Q.pred.band.1:f1}, at {live.Q.lock.et_time:time} ET on {live.Q.lock.et_date:date}, while the "
                  "repository was still private. GD reported {live.Q.score.reported.total:int} the next day. The lock missed "
                  "by {live.Q.score.ae_total:f1}, or {live.Q.score.ape_pct:pct1}, outside the band. GD's guidance pace was "
                  "{live.Q.score.guidance_pace:f1}, a miss of {live.Q.score.guidance_ae:f1}, and the raw registry count for "
                  "the quarter was {cmp.Q.raw:int}, a miss of {cmp.Q.raw_miss:int}. So the registry had the quarter's jets in "
                  "time: the count had settled at {lockt.Q.count:int} by the lock. What missed was my scaling, which took "
                  "{lockt.Q.scale:f2} deliveries per registry event from the {const.lags:word} quarters before when the "
                  "quarter came in at {lockt.Q.real:f2}. {const.one:word} quarter is one data point"),
    ("interview", "scaling FAA registrations missed by {m.holdout.mae.ratio:f1} jets a quarter, repeating the same quarter last "
                  "year missed by {m.holdout.mae.seasonal:f1}, and no test separates my estimate from any baseline. Then the "
                  "first live lock missed by {live.Q.score.ae_total:f1}, outside its band"),
    ("interview", "than tune a rule until it wins on {m.holdout.n:int} quarters"),
    ("interview", "From {const.two_years:word} years. In 2023 and 2024 the guidance pace missed by "
                  "{sv.only_2023_2024.mae.guidance:f1} jets a quarter on average and my estimate by "
                  "{sv.only_2023_2024.mae.ratio:f1}. In the other {sv.without_2023_2024.n:int} held-out quarters the guidance "
                  "pace missed by {sv.without_2023_2024.mae.guidance:f1} and my estimate by {sv.without_2023_2024.mae.ratio:f1}"),
    ("interview", "I counted ({used.old3_pct:pct1}) are airframes at least {const.old_years:word} years old"),
    ("interview", "The date must fall no later than {const.bound_days:int} days after the jet's first airworthiness date"),
    ("interview", "the earlier of {const.two_dates:word} dates"),
    ("interview", "the gap drifted from about {const.two_x:word} deliveries per event in {const.y2016:year} to {cov.2026Q2:f2} in "
                  "2026Q2. So I scale this quarter's count by the last {const.lags:word} quarters' ratio"),
    ("interview", "{const.n_simple:word} smaller surprises"),
    ("resume", "on {m.holdout.n:int} held-out quarters it missed by {m.holdout.mae.ratio:f1} jets a quarter vs "
               "{m.holdout.mae.guidance:f1} for a guidance-based pace and {m.holdout.mae.seasonal:f1} for last year's same quarter"),
    ("resume", "the first lock, 2026Q3, said {live.Q.pred.nowcast.total:f1} and GD reported "
               "{live.Q.score.reported.total:int}: a miss of {live.Q.score.ae_total:f1}, outside its band"),
    # sensitivity.md
    ("sensitivity", "\"So all up, {const.ten:int} fewer aircraft\", after reporting {gdyear.2020:int} deliveries for 2020"),
    ("sensitivity", "Read as {const.alt2021:int}, all {sv.alt_sourced:int} held-out quarters have an outlook"),
    # dashboard
    ("dashboard", "Over {m.holdout.n:int} held-out quarters the registry estimate was off by {m.holdout.mae.ratio:f1} jets a "
                  "quarter on average, when GD delivers about {typical:whole}, against {m.holdout.mae.guidance:f1} for GD's "
                  "guidance pace"),
    ("dashboard", "Scored: missed by {live.Q.score.ae_total:f1}, outside the band"),
    ("dashboard", "{live.Q.pred.nowcast.total:f1} deliveries, locked estimate"),
    ("dashboard", "{path.Q.n:int} snapshots, {path.Q.first:date} to {path.Q.last:date}"),
    ("dashboard", "made while the repository was private, on {live.Q.lock.et_date:date} at {live.Q.lock.et_time:time} ET"),
    ("dashboard", "Before GD reported, the delivery estimate of {live.Q.pred.nowcast.total:f1} sat below the "
                  "{gd.2025Q3.total:int} deliveries of 2025Q3, and each delivery carried about "
                  "{est.revenue_per_delivery_usd:usdM} of Aerospace revenue, so the delivery-based figure fell. GD reported "
                  "{rseg.Q.Aerospace.rev:usdB} of Aerospace revenue. That {est.revenue_per_delivery_usd:usdM} includes services"),
    ("dashboard", "while the {const.lags:word} quarters before it stay whole, so the count falls"),
    # workbook About
    ("workbook", "within {const.bound_days:int} days of first airworthiness"),
]
TEMPLATES += [T(surf, tpl.replace(".Q.", f".{Q}.").replace(".Q:", f".{Q}:")) for surf, tpl in NEW]


def _extra_consts(F):
    S = F["@src"]

    def put(k, v, src):
        F[k], S[k] = v, src

    put("const.one", 1, "count of locked and scored quarters in results/live (state)")
    put("const.two_x", 2, "threshold named in the sentence (deliveries per registry event above 2)")
    put("const.old_years", 3, "the age cut used for the used-jet count (event year minus year_mfr at least 3)")
    put("const.two_prefix", 2, "data/processed/serials.csv (each double-counted serial sits under two mfr_code prefixes)")
    put("const.demo11", 11, "GD's 2022-01-26 call, quoted: 'a few demonstrators all up about 11 aircraft' "
        "(data/raw/sources/calls/2022-01-26-fool.txt)")
    put("const.g300_late", 2027, "report/claims.json pc-g280-final-delivery (the year after the 2026-07-29 call; \"late '27\")")
    put("const.g300_early", 2028, "report/claims.json pc-g280-final-delivery (\"early '28\")")
    put("const.eng_a", 4, "src/gdn/faa.py scope rule (TYPE-ENG 4) and docs/PREREGISTRATION.md section 3 rule 1")
    put("const.eng_b", 5, "src/gdn/faa.py scope rule (TYPE-ENG 5) and docs/PREREGISTRATION.md section 3 rule 1")
    put("const.eng_out", 2, "ACFTREF row 3980222,GULFSTREAM AEROSPACE CORP,GVIII-G700,5,2 in the FAA file of 2026-10-30")
    put("const.two_years", 2, "results/exploratory/sensitivity.json (the variant names 2023 and 2024)")
    put("const.two_dates", 2, "src/gdn/events.py:57 (customer certificate, export cancellation)")
    rc = [F[f"cov.{q}"] for q in ("2025Q4", "2026Q1", "2026Q2")]
    put("cov.min3", min(rc), "results/metrics.json coverage_ratio.by_quarter (lowest of the last three held-out quarters)")
    put("cov.max3", max(rc), "results/metrics.json coverage_ratio.by_quarter (highest of the last three held-out quarters)")
    put("const.n_simple", 2, "src/gdn/model.py BASELINES minus guidance (seasonal, last)")
    put("const.n_segments", 4, "data/processed/segments.csv (distinct segments)")
    put("const.y2016", 2016, "data/processed/gd_deliveries.csv (first year)")
    put("const.y2017", 2017, "ASC 606 adoption year, data/processed/gd_deliveries.csv filed dates")
    put("const.y2019", 2019, "design window end year")
    put("const.asc606_date", "2017-01-01", "GD adopted ASC 606 on 2017-01-01 (GD 2017 Form 10-K; checked in P3.1)")
    put("const.prereg_date", "2026-10-19", "git log --diff-filter=A -- docs/PREREGISTRATION.md (checked in extra_checks)")
    put("const.cron_runs_word", F.get("const.cron_runs"), ".github/workflows/nowcast.yml (cron hours)")
    put("const.export_since", 2022, "middiff.<year>: |registry mid - GD mid| by year, checked in extra_checks")
    c = F["@claims"]
    for cid, cl in c.items():
        nums = re.findall(r"\d+(?:\.\d+)?", cl["text"])
        if cid == "os-margin" and nums:
            put("claimnum.os-margin", float(nums[0]), "report/claims.json:os-margin")
    # the README's split of the five used jets and the two earlier deliveries, read from the audit notes
    au = F.get("audit.used")
    if au is not None:
        put("audit.gv_quarters", 1, "docs/build/AIRFRAME_AUDIT.csv serial 571 note: 2000Q1 against 2000Q2")
        put("audit.g650_quarters", 2, "docs/build/AIRFRAME_AUDIT.csv serial 6270 note: 2017Q3 against 2018Q1")
    for k, v in (("ext.study.xbrl_year", 2018), ("ext.study.q1.backlog", 9.9), ("ext.study.q1.naive", 7.3),
                 ("ext.study.q1.drift", 6.5), ("ext.study.q4.backlog", 9.4), ("ext.study.q4.ttm", 5.8),
                 ("ext.study.q4.ttmdrift", 6.0)):
        put(k, v, "external: the defense backlog study's published figures (checked in P3.3 against its site)")


# ---------- tables ----------
def _model(label):
    return NAME2MODEL.get(label.strip().lower().replace("’", "'"))


def table_rule(b, F):
    """(field key, fmt) for a table cell, by header signature, row label and column header; or None."""
    sig, row, col = b.table, b.row.strip(), b.col.strip()
    lrow, lcol = row.lower(), col.lower()
    if sig.startswith("Model | Average miss | Average"):
        mod = _model(row)
        key = {"average miss": "mae", "average % miss": "mape", "average miss, %": "mape", "bias": "bias",
               "large cabin": "mae_large", "mid cabin": "mae_mid", "without 2020": "mae_ex_2020",
               "excluding 2020": "mae_ex_2020"}.get(lcol)
        if mod and key:
            return f"m.holdout.{key}.{mod}", ("pct1" if key == "mape" else "f1")
    if sig.startswith("Model | Large cabin | Mid cabin"):
        mod = _model(row)
        key = {"large cabin": "mae_large", "mid cabin": "mae_mid"}.get(lcol)
        if mod and key:
            return f"m.holdout.{key}.{mod}", "f1"
    if sig.startswith("Baseline | "):
        base = {"gd's guidance pace": "guidance", "the same quarter last year": "seasonal", "last quarter": "last"}.get(lrow)
        key = {"registry closer": ("tests.%s.wins", "int"), "registry further": ("tests.%s.losses", "int"),
               "quarters better": ("tests.%s.wins", "int"), "quarters worse": ("tests.%s.losses", "int"),
               "ties": ("tests.%s.ties", "int"), "p": ("tests.%s.p_one_sided", "f3"),
               "one-sided p": ("tests.%s.p_one_sided", "f3"), "relative miss": ("rel_mae.%s", "f2"),
               "lag-1 autocorrelation": ("autocorr_lag1.%s", "f2")}.get(lcol)
        if base and key:
            return "m.holdout." + key[0] % base, key[1]
    if sig.startswith("Year | Ratio | Raw | Guidance"):
        y = row[:4]
        mod = _model(col)
        if mod and re.fullmatch(r"\d{4}", y):
            return f"year.{y}.{mod}", "f2"
    if sig.startswith("Days cut |") or b.table == "t-trunc":
        if re.fullmatch(r"\d+", row):
            return f"m.holdout.truncation_mae.{row}", "f1"
    if sig.startswith("Quarter | Estimate | GD reported | Signed error"):
        q = row
        return {"estimate": (f"bt.{q}.ratio.total", "f1"), "gd reported": (f"gd.{q}.total", "int"),
                "signed error": (f"bt.{q}.ratio.signed", "f1"), "registry large": (f"reg.{q}.large", "int"),
                "registry mid": (f"reg.{q}.mid", "int"), "gd large": (f"gd.{q}.large", "int"),
                "gd mid": (f"gd.{q}.mid", "int")}.get(lcol)
    if sig.startswith("Quarter | Capture | Days after end"):
        q = row
        return {"days after end": (f"asof.{q}.days", "int"), "as-of estimate": (f"asof.{q}.estimate", "f1"),
                "gd reported": (f"asof.{q}.reported", "int"), "reported": (f"asof.{q}.reported", "int"),
                "as-of miss": (f"asof.{q}.ae", "f1"), "capture": (f"asof.{q}.capture_iso", "date")}.get(lcol) or \
            ((f"asof.{q}.bt_ae", "f1") if lcol.startswith("miss on the") else
             (f"asof.{q}.band", "band") if lcol == "as-of band" else None)
    # note exhibits
    if sig == "Segment | Revenue | Share of revenue | Operating margin" and row in SEGS:
        return {"revenue": (f"est.segments.{row}.ttm_revenue_usd", "usdB"), "share of revenue": (f"mix.{row}.share_pct", "pct1"),
                "operating margin": (f"mix.{row}.margin_pct", "pct1")}.get(lcol)
    if sig.startswith("Variant | Quarters | Registry estimate"):
        key = next((k[3:-2] for k in F if isinstance(k, str) and k.startswith("sv.") and k.endswith(".n")
                    and F.get("@svlabel", {}).get(k[3:-2]) == row), None)
        if key:
            return {"quarters": (f"sv.{key}.n", "int"), "registry estimate": (f"sv.{key}.mae.ratio", "f2"),
                    "raw count": (f"sv.{key}.mae.raw", "f2"), "guidance pace": (f"sv.{key}.mae.guidance", "f2"),
                    "same quarter last year": (f"sv.{key}.mae.seasonal", "f2"), "last quarter": (f"sv.{key}.mae.last", "f2"),
                    "closer than guidance": (f"sv.{key}.wins", "svwins"), "p": (f"sv.{key}.p", "f3")}.get(lcol)
    if sig.startswith("Segment | 2025Q3 actual | 2026Q3 estimate") or b.table == "t-est":
        r = {"aerospace, from the delivery estimate": "aero_now", "aerospace, delivery estimate": "aero_now",
             "aerospace, drift baseline": "Aerospace", "aerospace, growth rule": "Aerospace",
             "total, with aerospace from the delivery estimate": "total", "total, four segments": "total"}.get(lrow, row)
        c = {"2025q3 actual": ("yago", "usdB"), "year-ago quarter": ("yago", "usdB"), "2026q3 estimate": ("est", "usdB"),
             "estimate": ("est", "usdB"), "change": ("chg", "usdM"), "change, %": ("chgpct", "pct1"),
             "gd reported": ("rep", "usdB"), "estimate less reported": ("miss", "usdM"), "miss, %": ("misspct", "pct1")}.get(lcol)
        if c and f"estx.{r}.{c[0]}" in F:
            return f"estx.{r}.{c[0]}", c[1]
    if sig == "Change | Deliveries | Aerospace revenue":
        k = str(int(row.replace("+", "").replace("−", "-")))
        return {"deliveries": (f"sens.{k}.deliveries", "f1"), "aerospace revenue": (f"sens.{k}.rev", "usdB")}.get(lcol)
    if b.table == "t-sens":
        for k in range(-4, 5):
            if f"{F[f'sens.{k}.deliveries']:.1f}" == row:
                return {"aerospace revenue": (f"sens.{k}.rev", "usdB"),
                        "change on the year-ago quarter": (f"sens.{k}.chg", "usdM")}.get(lcol)
    if sig.startswith("Segment | Backlog, 2026Q2 | Coverage, years") and row in SEGS:
        return {"backlog, 2026q2": (f"backlog.{row}", "usdB"), "coverage, years": (f"est.segments.{row}.coverage_years", "f2"),
                "2026q3 estimate": (f"est.segments.{row}.drift_usd", "usdB"),
                "operating margin": (f"mix.{row}.margin_pct", "pct1")}.get(lcol)
    if sig.startswith("Summary | Design"):
        mod = _model(row)
        if mod:
            if lcol.startswith("design"):
                return (f"m.design.mae.{'none' if mod in ('seasonal', 'last') else F['m.definition']}.{mod}", "f1")
            return f"m.holdout.mae.{mod}", "f1"
    if sig.startswith("Segment | Revenue, 4Q to 2026Q2") and row in SEGS:
        return {"revenue, 4q to 2026q2": (f"est.segments.{row}.ttm_revenue_usd", "usdB"),
                "revenue, 4q to 2025q2": (f"est.segments.{row}.ttm_revenue_prior_usd", "usdB"),
                "drift, 2026q3": (f"est.segments.{row}.drift_usd", "usdB"), "margin, 4q": (f"mix.{row}.margin_pct", "pct1"),
                "backlog": (f"backlog.{row}", "usdB"), "coverage, years": (f"est.segments.{row}.coverage_years", "f2")}.get(lcol)
    if sig == "Derived | Value":
        return {"deliveries, four quarters to 2026q2": ("est.ttm_deliveries", "int"),
                "aerospace revenue per delivery": ("est.revenue_per_delivery_usd", "usdM"),
                "2026q3 delivery estimate": ("est.nowcast_total", "f1"),
                "aerospace revenue from the estimate": ("est.aerospace_from_nowcast_usd", "usdB"),
                "aerospace operating earnings from the estimate": ("est.aerospace_oe_from_nowcast_usd", "usdB"),
                "revenue, all four segments": ("est.revenue_total_usd", "usdB"),
                "segment operating earnings, all four segments": ("est.operating_earnings_total_usd", "usdB")}.get(lrow)
    # dashboard
    if b.table == "live-facts":
        return {"gd's guidance pace": ("live.2026Q3.score.guidance_pace", "f1"), "gd's typical quarter": ("typical", "whole"),
                "same quarter last year": ("gd.2025Q3.total", "int"), "gd reported": ("live.2026Q3.score.reported.total", "int"),
                "miss of the locked estimate": ("live.2026Q3.score.ae_total", "f1")}.get(lrow)
    if b.table == "t-track":
        q = row
        if lcol == "gd reported":
            return f"gd.{q}.total", "int"
        mod = _model(col)
        if mod:
            return f"bt.{q}.{mod}.total", "f1"
    if b.table == "t-path":
        d = row
        m = {"estimate": "nowcast_total", "large-cabin registrations": "events_large",
             "mid-cabin registrations": "events_mid", "band low": "band_low", "band high": "band_high"}
        for k, v in m.items():
            if lcol.startswith(k):
                return f"path.2026Q3.{d}.{v}", ("int" if "events" in v else "f1")
    if b.table == "t-pipe":
        return f"pipex.{row}", "int"
    return None


SPECIAL_CELLS = {
    # dashboard dl rows that carry several typed values
    ("live-facts", "registrations so far"): "{live.2026Q3.latest.events.large:int} large-cabin, "
                                            "{live.2026Q3.latest.events.mid:int} mid-cabin (snapshot "
                                            "{live.2026Q3.latest.snapshot:date})",
    ("live-facts", "quarter window"): "{live.2026Q3.pred.window_open:date} to {live.2026Q3.pred.window_end:date}",
    ("live-facts", "gd reports"): "{cal.release.2026Q3:date}",
    ("live-facts", "gd reported on"): "{cal.release.2026Q3:date}",
    ("live-facts", "registrations in the quarter"): "{live.2026Q3.latest.events.large:int} large-cabin, "
                                                    "{live.2026Q3.latest.events.mid:int} mid-cabin (snapshot "
                                                    "{live.2026Q3.latest.snapshot:date})",
    ("live-facts", "gd's guidance pace"): "{live.2026Q3.score.guidance_pace:f1} deliveries (missed by "
                                          "{live.2026Q3.score.guidance_ae:f1})",
    ("live-facts", "same quarter last year"): "{cmp.2026Q3.yago:int} deliveries (missed by {cmp.2026Q3.yago_miss:int})",
    ("live-facts", "miss of the locked estimate"): "{live.2026Q3.score.ae_total:f1} deliveries "
                                                   "({live.2026Q3.score.ape_pct:pct1}), outside the band",
    ("live-facts", "gd's typical quarter"): "about {typical:whole} deliveries since {const.since2020:year}",
}
TILE = re.compile(r"^(Registry estimate|Raw registry count|GD's guidance pace|Same quarter last year|Last quarter)"
                  r"\s*(\d+\.\d)\s*(?:(\d+\.\d) (more|less) than the registry estimate|this project's estimate)$")


def _bind(text, toks, rx, keys, F, compare, js, q=None):
    """Bind the tokens inside one template's slots. [(tok, field, expected, status, note)], and literal-covered tokens."""
    out, covered = [], []
    for m in rx.finditer(text):
        for gi, (key, fmt) in enumerate(keys, start=1):
            s, e = m.span(gi)
            if q:
                key = key.replace("%Q%", q)
            tok = next((t for t in toks if t.start < e and t.end > s), None)
            if tok is None:
                continue
            exp = F.get(key)
            src = F["@src"].get(key, key)
            if exp is None:
                out.append((tok, key, "", "untraced", "rule names a field the sources do not hold"))
            elif fmt in ("date", "time", "hash", "year"):
                shown = tok.text
                ok = str(exp) == shown or (fmt == "year" and int(float(exp)) == int(tok.value or 0))
                out.append((tok, f"{src} [{key}]", str(exp), "traced" if ok else "mismatch", ""))
            elif fmt == "any":
                ok = repr(float(exp)) == tok.text or f"{exp}" == tok.text
                out.append((tok, f"{src} [{key}]", repr(exp), "traced" if ok else "mismatch", ""))
            else:
                st, want = compare(tok, exp, "word" if fmt == "word" else fmt, js=js)
                out.append((tok, f"{src} [{key}]", want, st, ""))
        covered += [t for t in toks if m.start() <= t.start and t.end <= m.end()]
    return out, covered


def normalize(text):
    text = re.sub(r"\[`?([^\]`]*)`?\]\([^)]*\)", r"\1", text)      # markdown links: keep the text
    text = re.sub(r"`([0-9a-f]{64})`", r"\1", text)                # a bare hash in a code span
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)             # HTML comments (the README's block markers)
    text = text.replace("**", "").replace(" ", " ")
    return " ".join(text.split())


def trace_block(b, F, tokens, compare):
    if "const.one" not in F:
        _extra_consts(F)
    if b.kind == "rowhead":
        return []
    if b.surface == "prereg" and b.section not in ("Chosen definition", "Preregistration"):
        return []
    text = normalize(b.text)
    toks = tokens(text)
    js = b.surface == "dashboard"
    out, done = [], set()

    def add(tok, field, exp, st, note=""):
        if id(tok) not in done:
            done.add(id(tok))
            out.append((tok, field, exp, st, note))

    figs = [t for t in toks if t.kind in ("num", "word")]
    if b.kind == "cell":
        spec = SPECIAL_CELLS.get((b.table, b.row.strip().lower()))
        if spec:
            F.setdefault("const.since2020", 2020)
            F["@src"].setdefault("const.since2020", "holdout window start year")
            rx, keys = compile_tpl(spec)
            res, _ = _bind(text, toks, rx, keys, F, compare, js)
            for r in res:
                add(*r)
        rule = None if spec else table_rule(b, F)
        if rule and rule[1] == "band":
            q = b.row
            if f"asof.{q}.band_low" in F:
                rx, keys = compile_tpl("{asof.%s.band_low:f1} to {asof.%s.band_high:f1}" % (q, q))
                res, _ = _bind(text, toks, rx, keys, F, compare, js)
                for r in res:
                    add(*r)
        elif rule and rule[1] == "svwins":
            k = rule[0][3:-5]
            rx, keys = compile_tpl("{sv.%s.wins:int} of {sv.%s.of:int}" % (k, k))
            res, _ = _bind(text, toks, rx, keys, F, compare, js)
            for r in res:
                add(*r)
        elif rule and rule[1] == "date":
            for t in toks:
                if t.kind in ("id:date", "id:date8"):
                    exp = F.get(rule[0])
                    shown = t.text if "-" in t.text else f"{t.text[:4]}-{t.text[4:6]}-{t.text[6:8]}"
                    add(t, f"{F['@src'].get(rule[0], '')} [{rule[0]}]", exp, "traced" if exp == shown else "mismatch")
        elif rule and len(figs) >= 1:
            key, fmt = rule
            exp, src = F.get(key), F["@src"].get(key, "")
            st, want = compare(figs[0], exp, fmt, js=js) if exp is not None else ("untraced", "")
            add(figs[0], f"{src} [{key}]", want, st, "" if exp is not None else "rule names a field the sources do not hold")
    if b.surface == "dashboard" and b.ident == "tiles":
        m = TILE.match(text)
        if m:
            mod = _model(m.group(1))
            nums = [t for t in figs]
            if not nums:
                return [(None, "", "", "untraced", "tile text carries no separable figure")][:0]
            st, want = compare(nums[0], F[f"m.holdout.mae.{mod}"], "f1", js=True)
            add(nums[0], f"results/metrics.json [m.holdout.mae.{mod}]", want, st)
            if len(nums) > 1:
                st, want = compare(nums[1], F[f"tile.{mod}"], "f1", js=True)
                add(nums[1], f"{F['@src'][f'tile.{mod}']} [tile.{mod}]", want, st)
    q = b.section if re.fullmatch(r"\d{4}Q\d", b.section or "") else None
    covered = []
    for surfaces, rx, keys, tpl in TEMPLATES:
        if b.surface not in surfaces:
            continue
        res, cov = _bind(text, toks, rx, keys, F, compare, js, q)
        for r in res:
            add(*r)
        covered += cov
    # claims: a sentence printed from the claims registry carries that registry's figures
    for cid, cl in F["@claims"].items():
        ct = normalize(cl["text"])
        pos = text.find(ct)
        if pos >= 0:
            for t in toks:
                if pos <= t.start and t.end <= pos + len(ct) and t.kind in ("num", "word", "id:date"):
                    add(t, f"report/claims.json:{cid}", "", "traced", "figure inside a registry claim; the claim is source-checked in P3.3")
            covered += [t for t in toks if pos <= t.start and t.end <= pos + len(ct)]
    # a ratio named in one unit must not carry the other unit's value
    if b.kind == "prose":
        ev_per = re.compile(r"events? per (reported )?deliver", re.I)
        del_per = re.compile(r"deliver(y|ies) per (registry )?(event|registration)", re.I)
        fam_ev = {k: v for k, v in F.items() if isinstance(k, str) and k.startswith("evper.")}
        fam_ev.update({f"1/cov.{k[4:]}": 1 / v for k, v in F.items() if isinstance(k, str) and re.fullmatch(r"cov\.\d{4}Q\d", k)})
        fam_del = {k: v for k, v in F.items() if isinstance(k, str) and re.fullmatch(r"cov\.\d{4}Q\d", k)}
        fam_del["m.holdout.coverage_ratio.mean"] = F["m.holdout.coverage_ratio.mean"]
        for t in toks:
            if id(t) in done or t.kind != "num" or t.unit or t.cur or t.decimals == 0:
                continue
            s0 = text.rfind(". ", 0, t.start) + 1
            e0 = text.find(". ", t.end)
            sent = text[s0:len(text) if e0 < 0 else e0]
            named_ev, named_del = ev_per.search(sent), del_per.search(sent)
            if not (named_ev or named_del) or (named_ev and named_del):
                continue
            own, other = (fam_ev, fam_del) if named_ev else (fam_del, fam_ev)
            unit = "registry events per delivery" if named_ev else "deliveries per registry event"

            def hits(fam):
                return [k for k, v in fam.items() if f"{v:.{t.decimals}f}" == f"{abs(t.value):.{t.decimals}f}"]
            if hits(other) and not hits(own):
                add(t, f"{unit} (family of fields)", "", "mismatch",
                    f"unit swap: the sentence names {unit}, but {t.text} is the value of {hits(other)[0]}, the inverse unit")
    # identifiers
    for t in toks:
        if id(t) in done:
            continue
        if t.kind in ("id:date", "id:datetime"):
            ok = t.text in F["@dates"]
            add(t, "date found in the source set" if ok else "", "", "traced" if ok else "untraced", "class id (date), bound by value")
        elif t.kind == "id:date8":
            iso = f"{t.text[:4]}-{t.text[4:6]}-{t.text[6:8]}"
            ok = any(F.get(k) == t.text for k in F if k.startswith("asof.") and k.endswith(".capture"))
            add(t, "results/exploratory/asof.csv capture" if ok else "", iso, "traced" if ok else "untraced", "class id (date)")
        elif t.kind == "id:hash" and len(t.text) == 64:
            ok = t.text in F["@hashes"]
            add(t, "hash found in the source set" if ok else "", "", "traced" if ok else "untraced", "class id (hash)")
        elif t.kind == "id:accn":
            ok = t.text in F["@accns"]
            add(t, "accession found in the source set" if ok else "", "", "traced" if ok else "untraced", "class id (accession)")
        elif t.kind == "id:time":
            add(t, "", "", "untraced", "clock time outside a live-record template")
        elif t.kind == "id:quarter":
            if not (qidx("2015Q4") <= qidx(t.text) <= qidx("2027Q4")):
                add(t, "", "", "untraced", "quarter label outside the project's range")
        elif t.kind == "num" and t.decimals == 0 and not t.unit and not t.cur and 2000 <= (t.value or 0) <= 2027 \
                and len(t.text) == 4:
            add(t, "calendar year in the project's range", "", "traced", "class id (year), bound by range")
        elif t.kind in ("num", "word"):
            if t in covered and t.kind == "word":
                add(t, "label text of a matched rule", "", "traced", "number word inside a matched template's fixed text")
            else:
                add(t, "", "", "untraced", "no label rule claims this figure")
    return out


# ---------- staleness ----------
TRIGGER = re.compile(r"\block(s|ed|ing)?\b|\bscor(e|ed|es|ing)\b|live (quarter|estimate|test|record)|first (live|real) "
                     r"(test|quarter)|GD reports\b|GD (then )?reported \d|\breports on\b|provisional|release date|"
                     r"build estimate|the day before", re.I)
FUTURE = re.compile(r"will be scored|will show|will be the first|is scored on|is scored when|\blocks on\b|comes on|"
                    r"first real test comes|not yet (locked|scored)|provisional|My build estimate is|"
                    r"GD reports on|It locks|locks the evening|awaits|upcoming", re.I)


def sentences(text):
    text = normalize(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"(\[*0-9])", text)
    return [p.strip() for p in parts if p.strip()]


def _norm_sent(s):
    s = re.sub(r"[0-9a-f]{64}", "H", s)
    s = re.sub(r"\b\d{4}Q[1-4]\b", "QQ", s)
    s = s.replace("sha256", "sha-two-five-six")
    s = re.sub(r"\d{4}-\d{2}-\d{2}", "D", s)
    s = re.sub(r"\d{2}:\d{2}", "TM", s)
    s = re.sub(r"(?<![\w])[-−+]?\$?\d+(?:,\d{3})*(?:\.\d+)?%?", "#", s)
    return s.replace("sha-two-five-six", "sha256")


def live_ok(F):
    """Reviewed sentence patterns about locks and scores, each with the state under which it is true.

    Pattern on the normalized sentence (numbers #, dates D, times TM, hashes H). cond(state) -> bool."""
    st = F["@state"]

    def scored(q):
        return st.get(q, {}).get("scored", False)

    def locked(q):
        return st.get(q, {}).get("locked", False)

    any_locked_scored = any(v["locked"] and v["scored"] for v in st.values())
    n_ls = sum(1 for v in st.values() if v["locked"] and v["scored"])
    G = True  # a general description of the method, true whatever the state
    return [
        # generic method descriptions
        (r"lock each live estimate on GitHub the day before GD reports", G),
        (r"Only the locked quarters test whether (it|the registry) counts (them|deliveries|jets) in time", G),
        (r"only the locked quarters show whether it counts jets in time", G),
        (r"the locked quarters remain the real test", G),
        (r"on the day before GD reports, locks the estimate as a GitHub release whose notes carry the file's sha256", G),
        (r"When GD reports, the run scores the lock against GD's count", G),
        (r"can lock from either run on the release date's eve", G),
        (r"it never downloads a snapshot, reads SEC, locks or scores", G),
        (r"I run it on my Mac once a day until each quarter is scored", G),
        (r"Each live quarter's estimate is locked on GitHub the day before GD reports, and kept whether it hits or misses", G),
        (r"with each quarter's estimate locked on GitHub before the release", G),
        (r"the pipeline locks its estimate as a timestamped GitHub release with the file's sha256 in the notes, and scores it "
         r"against GD's count when the filing lands", G),
        (r"Built a daily job that locks each quarter's estimate on GitHub as a timestamped release carrying its sha256 the day "
         r"before GD reports, and scores it from GD's SEC filing", G),
        (r"The band comes from (misses|errors) measured on a (finished )?registry file.*(live quarter|live lock)", G),
        (r"so it is likely too narrow (live|at a live lock|for a live quarter)", G),
        (r"the past-miss band comes from (misses|errors) measured on a finished registry file", G),
        (r"A live estimate sees only what has posted|while a live estimate sees only what has posted", G),
        (r"as a live estimate (reads them|does)", G),
        (r"Score more locked quarters before claiming anything", G),
        (r"the diamond marks the locked estimate", G),
        (r"A crude stand-in for a live quarter", G),
        (r"^The live quarter$", G),
        (r"^The test that matters is live\.?$", G),
        (r"The live job is make daily", G),
        (r"README.md: Results, Error analysis and Live record|the README's Live record", G),
        (r"^## ?Live record$|^Live record$", G),
        (r"^Live$|^Live\.", G),
        (r"A design window .* chose the event definition .* before I scored the # quarters", G),
        (r"committed .* before the held-out quarters were scored", G),
        (r"committed them before scoring # held-out quarters", G),
        (r"of them can be scored", G),
        (r"GD reports (four|#) segments", G),
        (r"GD reported # large-cabin and # mid-cabin deliveries against # and # registry events", G),
        (r"Scored as each capture would have read it", G),
        (r"The (\d{4}Q\d and \d{4}Q\d|QQ and QQ) need lag quarters", G),
        (r"are held out and scored against seasonal, last-quarter and GD guidance baselines", G),
        (r"Each as-of estimate reads both the quarter's own registry events", G),
        # state sentences
        (r"QQ: locked at # \(band # to #\) from the D snapshot, as a timestamped GitHub release \(lock-QQ\) at TM ET on D, "
         r"sha256 H; GD's guidance pace for the quarter was #\.?$", "Q3LS"),
        (r"GD reported #: the lock missed by #, outside the band", "Q3LS_out"),
        (r"QQ: not locked yet\.?$", "Q4open"),
        (r"Its window runs to D, so the D snapshot counts only part of it and no estimate is shown yet", "Q4open"),
        (r"One locked quarter so far: off by #", "one_ls"),
        (r"I locked an estimate of # Gulfstream deliveries for QQ on GitHub before GD reported, and GD reported #", "Q3LS"),
        (r"One quarter shows how it works live, not whether it works", "one_ls"),
        (r"I locked it as a timestamped GitHub release at TM ET on D", "Q3L_private"),
        (r"I locked this estimate as a timestamped GitHub release at TM ET on D", "Q3L_private"),
        (r"GD reported #, against a guidance pace of #", "Q3LS"),
        (r"GD then reported #", "Q3LS"),
        (r"GD's guidance pace for the quarter had been #", "Q3LS"),
        (r"^QQ · Scored$", "Q3LS"),
        (r"Locked as a timestamped GitHub release; the file's sha256 is in the release notes", "Q3L_private"),
        (r"^GD reported: # deliveries$|^Miss of the locked estimate: # deliveries$", "Q3LS"),
        (r"^# deliveries$|^#$", G),
        (r"The live quarter: QQ", "Q3LS"),
        (r"So I report it as a tracker, not as an edge", G),
        # ---- sentences written in the fix pass ----
        (r"(lock|locks) (each live estimate|it|each estimate) on GitHub the day before GD reports", G),
        (r"so only locked quarters show whether it counts jets in time", G),
        (r"That table is not a model of a live lock", G),
        (r"It is not a model of a live lock, which is made weeks after the quarter ends", G),
        (r"The commit order is all that backs the words .held out. and .preregistered. here", G),
        (r"Only the locked quarters are out of sample in the strict sense", G),
        (r"A lock needs GD's release date, which I add to `config/calendar.json` by hand once GD announces it; a quarter "
         r"with no date there gets no lock", G),
        (r"then each scored live quarter from its own release", G),
        (r"What GD reported by segment for a scored live quarter is in data/processed/segments_reported.csv", G),
        (r"a quarter with no fresh snapshot after its fiscal end goes without a lock", G),
        (r"so after a lock or a score I rebuild it on the Mac with `make pdf`", G),
        (r"I fixed the rules before I scored the held-out quarters", G),
        (r"^What did the locked quarter show\?$", G),
        (r"that locks each estimate as a timestamped GitHub release before GD reports and scores it from GD's SEC filing; "
         r"the first lock, QQ, said # and GD reported #: a miss of #, outside its band", "Q3LS_out"),
        (r"My first locked estimate of Gulfstream deliveries missed: I said # for QQ, General Dynamics reported #", "first_miss"),
        (r"The QQ miss was # jets \(#\), outside my band of past misses", "Q3LS_out"),
        (r"Live record so far: one locked quarter, a miss outside its band", "first_miss"),
        (r"For QQ I locked an estimate of # Gulfstream deliveries \(band # to #\) the day before GD reported", "Q3LS"),
        (r"GD reported #, so the lock missed by # \(#\), outside the band", "Q3LS_out"),
        (r"The QQ lock read a snapshot taken # days after the quarter ended, when the quarter's count stood at #, and it "
         r"is the same in every daily snapshot since, to D", "Q3LS"),
        (r"QQ: locked at # \(band # to #\) from the D snapshot, as a timestamped GitHub release, made while the repository "
         r"was private \(lock-QQ\) at TM ET on D, sha256 H\.?$", "Q3L_private"),
        (r"GD reported # on D: the lock missed by # \(#\), outside the band", "Q3LS_out"),
        (r"No release date is set in `config/calendar.json` yet, so no lock is scheduled", "Q4_no_date"),
        (r"The QQ lock was made by the workflow while this repository was private, so nobody outside could see it before "
         r"GD reported", "Q3_bot_private"),
        (r"In the QQ lock, # of the # events were airframes at least three years old by that field", "Q3LS"),
        (r"Estimate locked from the D registry snapshot; GD reported on D", "Q3LS"),
        (r"For QQ I locked a registry estimate of # Gulfstream deliveries, with a past-miss band of # to #, as a "
         r"timestamped GitHub release, made while the repository was private, at TM ET on D", "Q3L_private"),
        (r"the locked estimate implied #B of Aerospace revenue for QQ", "Q3LS"),
        (r"I wrote this note before GD reported QQ on D", "Q3LS"),
        (r"I locked this estimate as a timestamped GitHub release, made while the repository was private, at TM ET on D",
         "Q3L_private"),
        (r"GD then reported #: the lock missed by # \(#\), outside the band", "Q3LS_out"),
        (r"snapshot D for the backtest, and snapshot D for the QQ lock", "Q3LS"),
        (r"^QQ · Scored: missed by #, outside the band$", "Q3LS_out"),
        (r"^# deliveries, locked estimate$", "Q3LS"),
        (r"Locked as a timestamped GitHub release, made while the repository was private, on D at TM ET; the file's sha256 "
         r"is in the release notes", "Q3L_private"),
        (r"^Miss of the locked estimate: # deliveries \(#\), outside the band$", "Q3LS_out"),
        (r"The first lock, for QQ, said # with a band of # to #", "Q3LS"),
        (r"GD reported # on D: a miss of #, outside the band, and further off than GD's guidance pace \(a miss of #\) or "
         r"the same quarter last year \(a miss of #\)", "Q3LS_out"),
        (r"The first lock was for QQ", "Q3LS"),
        (r"The GitHub workflow locked # deliveries, with a band of # to #, at TM ET on D, while the repository was still "
         r"private", "Q3_bot_private"),
        (r"GD reported # the next day", "Q3LS"),
        (r"The lock missed by #, or #, outside the band", "Q3LS_out"),
        (r"So the registry had the quarter's jets in time: the count had settled at # by the lock", "Q3LS"),
        (r"Then the first live lock missed by #, outside its band", "first_miss"),
        (r"and the first lock fell outside it", "first_miss"),
        (r"docs/prepub/ERRATA\.md records the gap and the amendment to decide before the next lock", G),
        (r"The past-miss band comes from misses measured on one finished registry file, so it may not fit a live lock", G),
        (r"why the test on past quarters is not a test of a live estimate", G),
        (r"The guidance pace has been closer in each of the last (three|four|five|six|seven|eight|#) quarters, the locked "
         r"one included", "guid_closer_live"),
    ], {"Q3LS": locked("2026Q3") and scored("2026Q3"),
        "Q3LS_out": locked("2026Q3") and scored("2026Q3") and F.get("live.2026Q3.score.inside_band") is False,
        "Q4open": not locked("2026Q4") and not scored("2026Q4") and "2026Q4" in st,
        "one_ls": n_ls == 1,
        "first_miss": n_ls == 1 and locked("2026Q3") and scored("2026Q3") and F.get("live.2026Q3.score.inside_band") is False,
        "guid_closer_live": n_ls == 1 and (F.get("live.2026Q3.score.guidance_ae") or 9e9) < (F.get("live.2026Q3.score.ae_total") or 0),
        "Q4_no_date": "2026Q4" in st and not locked("2026Q4") and not scored("2026Q4") and "cal.release.2026Q4" not in F,
        "Q3_bot_private": locked("2026Q3") and not F["@public"] and F.get("@lock_author", {}).get("2026Q3", "").startswith("github-actions"),
        "Q3L_private": locked("2026Q3") and not F["@public"]}


def stale_check(b, F):
    """[(sentence, 'stale', why)] for each sentence about a lock or score that the scored state does not admit."""
    if b.surface == "prereg" or b.kind == "rowhead":
        return []
    out = []
    pats, conds = live_ok(F)
    st = F["@state"]
    text = b.text if b.kind != "cell" else f"{b.row}: {b.text}"
    for s in sentences(text):
        if not TRIGGER.search(s):
            continue
        n = _norm_sent(s)
        qs = re.findall(r"\d{4}Q\d", s)
        fut = FUTURE.search(s)
        if fut:
            # a pending phrase is right only for a quarter that is not yet locked or scored
            open_q = [q for q in qs if q in st and not st[q]["scored"]]
            past_date = [d for d in re.findall(r"\d{4}-\d{2}-\d{2}", s)
                         if any(d <= F.get(f"cal.release.{q}", "") for q in st if st[q]["scored"])]
            if not open_q or past_date:
                out.append((s[:200], "stale", f"pending wording ('{fut.group(0)}') but results/live shows the quarter scored"))
                continue
        hit = None
        for pat, cond in pats:
            if re.search(pat, n, re.I):
                hit = (pat, cond)
                break
        if hit is None:
            out.append((s[:200], "stale", "no reviewed pattern admits this sentence about a lock or score under the state in results/live"))
        elif hit[1] is not True and not conds[hit[1]]:
            out.append((s[:200], "stale", f"reviewed pattern needs state {hit[1]}, which results/live does not show"))
    return out


# ---------- workbook ----------
def trace_workbook_cell(c, F, tokens, compare):
    """[(field, expected, status, note, value, label)] for one workbook cell."""
    if "const.one" not in F:
        _extra_consts(F)
    sheet, coord, row, col, v = c["sheet"], c["coord"], c["row"], c["col"], c["value"]
    label = f"{sheet} | {row} | {col}"
    out = []

    def num(key, scale=1.0):
        exp = F.get(key)
        if exp is None:
            out.append((key, "", "untraced", "rule names a field the sources do not hold", v, label))
            return
        try:
            x = float(v)
        except (TypeError, ValueError):
            out.append((key, repr(exp), "mismatch", "cell does not compute to a number", v, label))
            return
        e = float(exp) / scale
        ok = abs(x - e) <= 1e-9 * max(1.0, abs(e))
        out.append((f"{F['@src'].get(key, '')} [{key}]", repr(e), "traced" if ok else "mismatch", "", repr(x), label))

    if sheet == "About":
        class B:  # a prose block
            pass
        b = B()
        b.surface, b.kind, b.section, b.table, b.row, b.col, b.ident = "workbook", "prose", "", "", "", "", ""
        b.text = re.sub(r"^\d+\. ", "", str(v))  # the method list's own numbering
        for tok, field, exp, st, note in trace_block(b, F, tokens, compare):
            out.append((field, exp, st, note, tok.text, str(v)[:160]))
        return out
    if coord.startswith("A") or (coord[1:] == "1" and coord[0] != "A"):
        return out
    if c.get("formula") is not None and not isinstance(v, (int, float)) and not (sheet == "Live" and isinstance(v, str)):
        out.append(("", "", "mismatch", f"formula {c['formula'][:60]} did not compute to a number ({v!r})", str(v), label))
        return out
    if v is None:
        return out
    live_text = sheet == "Live" and row in ("GD's count against the band", "GD release (SEC accession)")
    if not live_text and (c["col"] is None or isinstance(v, str) and not re.fullmatch(r"-?\d+(\.\d+)?", v)):
        if isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            key = {"Fiscal end": f"gd.{row}.fiscal_end"}.get(col) or ("live.2026Q3.pred.snapshot" if row == "Snapshot" else None)
            exp = F.get(key) if key else None
            out.append((f"{F['@src'].get(key, '')} [{key}]" if key else "", exp or "", "traced" if exp == v else
                        ("mismatch" if key else "untraced"), "", v, label))
        return out
    if sheet == "Quarters":
        q = row
        key = {"Reported large": f"gd.{q}.large", "Reported mid": f"gd.{q}.mid", "Reported total": f"gd.{q}.total",
               "Registry large": f"reg.{q}.large", "Registry mid": f"reg.{q}.mid",
               "Ratio large": f"bt.{q}.ratio.large", "Ratio mid": f"bt.{q}.ratio.mid", "Ratio total": f"bt.{q}.ratio.total",
               "Raw total": f"bt.{q}.raw.total", "Seasonal": f"bt.{q}.seasonal.total", "Last": f"bt.{q}.last.total",
               "AE ratio": f"bt.{q}.ratio.ae", "AE raw": f"bt.{q}.raw.ae", "AE seasonal": f"bt.{q}.seasonal.ae",
               "AE last": f"bt.{q}.last.ae", "Guidance pace": f"bt.{q}.guidance.total",
               "AE guidance": f"bt.{q}.guidance.ae"}.get(col)
        if key:
            num(key)
    elif sheet == "Summary":
        mod = {"MAE ratio": "ratio", "MAE raw": "raw", "MAE seasonal": "seasonal", "MAE last": "last",
               "MAE guidance": "guidance"}.get(row)
        if mod and col == "Design":
            num(f"m.design.mae.{'none' if mod in ('seasonal', 'last') else F['m.definition']}.{mod}")
        elif mod and col == "Holdout":
            num(f"m.holdout.mae.{mod}")
        else:
            out.append(("", "", "untraced", "no label rule for this Summary cell", v, label))
    elif sheet == "Live":
        errs = F["m.band_errors"]
        P = "live.2026Q3.pred."
        key = {"Registry large": P + "events.large", "Registry mid": P + "events.mid",
               "Trailing reported large": P + "trailing.reported.large", "Trailing reported mid": P + "trailing.reported.mid",
               "Trailing registry large": P + "trailing.registry.large", "Trailing registry mid": P + "trailing.registry.mid",
               "Nowcast large": P + "nowcast.large", "Nowcast mid": P + "nowcast.mid", "Nowcast total": P + "nowcast.total",
               "Band low": P + "band.0", "Band high": P + "band.1"}.get(row)
        if key:
            num(key)
        elif row in ("Past-miss P10", "Past-miss P90"):
            F["wb.p10"], F["wb.p90"] = nearest_rank(errs, 0.1), nearest_rank(errs, 0.9)
            F["@src"]["wb.p10"] = F["@src"]["wb.p90"] = "results/metrics.json:band_errors (nearest rank)"
            num("wb.p10" if row.endswith("P10") else "wb.p90")
        else:
            key2 = {"GD reported": "live.2026Q3.score.reported.total", "Miss of the lock": "live.2026Q3.score.ae_total",
                    "Miss, % of reported": "live.2026Q3.score.ape_pct", "Guidance pace": "live.2026Q3.score.guidance_pace",
                    "Guidance pace miss": "live.2026Q3.score.guidance_ae"}.get(row)
            if key2:
                num(key2, 100.0 if row.startswith("Miss, %") else 1.0)     # the sheet holds the share as a fraction
            elif row == "GD's count against the band":
                want = "inside" if F["live.2026Q3.score.inside_band"] else "outside"
                out.append(("results/live/2026Q3_score.json [inside_band]", want, "traced" if v == want else "mismatch",
                            "", str(v), label))
            elif row == "GD release (SEC accession)":
                want = F["live.2026Q3.score.accn"]
                out.append(("results/live/2026Q3_score.json [accn]", want, "traced" if v == want else "mismatch", "",
                            str(v), label))
            elif not isinstance(v, str):
                out.append(("", "", "untraced", "no label rule for this Live cell", v, label))
    elif sheet == "Segments":
        derived = {"TTM deliveries": ("est.ttm_deliveries", 1), "Revenue per delivery": ("est.revenue_per_delivery_usd", 1e6),
                   "Nowcast deliveries": ("est.nowcast_total", 1), "Aerospace from nowcast": ("est.aerospace_from_nowcast_usd", 1e6),
                   "Aerospace operating earnings from nowcast": ("est.aerospace_oe_from_nowcast_usd", 1e6),
                   "Revenue total": ("est.revenue_total_usd", 1e6),
                   "Operating earnings total": ("est.operating_earnings_total_usd", 1e6)}
        if row in derived and coord.startswith("B"):
            num(*derived[row])
        elif re.fullmatch(r"\d{4}Q\d", str(col or "")):
            seg, kind = (row[:-len(" operating earnings")], "oe") if str(row).endswith(" operating earnings") else (row, "rev")
            if seg in SEGS:
                num(f"seg.{seg}.{col}.{kind}", 1e6)
        elif row in SEGS:
            key = {"TTM 2026Q2": (f"est.segments.{row}.ttm_revenue_usd", 1e6),
                   "TTM 2025Q2": (f"est.segments.{row}.ttm_revenue_prior_usd", 1e6),
                   "Drift 2026Q3": (f"est.segments.{row}.drift_usd", 1e6), "TTM margin": (f"est.segments.{row}.ttm_margin", 1),
                   "Backlog 2026Q2": (f"backlog.{row}", 1e6), "Coverage (years)": (f"est.segments.{row}.coverage_years", 1)}.get(col)
            if key:
                num(*key)
        elif coord.startswith("B"):
            key = {"TTM deliveries": ("est.ttm_deliveries", 1), "Revenue per delivery": ("est.revenue_per_delivery_usd", 1e6),
                   "Nowcast deliveries": ("est.nowcast_total", 1), "Aerospace from nowcast": ("est.aerospace_from_nowcast_usd", 1e6),
                   "Aerospace operating earnings from nowcast": ("est.aerospace_oe_from_nowcast_usd", 1e6),
                   "Revenue total": ("est.revenue_total_usd", 1e6),
                   "Operating earnings total": ("est.operating_earnings_total_usd", 1e6)}.get(row)
            if key:
                num(*key)
            elif not isinstance(v, str):
                out.append(("", "", "untraced", "no label rule for this Segments cell", v, label))
    elif sheet == "Sensitivity":
        try:
            k = int(float(c["row"]))
        except (TypeError, ValueError):
            return out
        key = {"Deliveries": f"sens.{k}.deliveries", "Aerospace revenue": f"sens.{k}.rev"}.get(col)
        if key:
            num(key, 1e6 if col == "Aerospace revenue" else 1)
    if not out and (c.get("formula") is not None or isinstance(v, (int, float))):
        # never skip a figure in silence: a number or formula no rule names is untraced
        out.append(("", "", "untraced", "no label rule for this cell", v, label))
    return out


# ---------- charts, PDF, extras ----------
def trace_chart_row(r, F):
    """A hand-listed number from a chart image: file,value,label,field,fmt."""
    if "const.one" not in F:
        _extra_consts(F)
    key, fmt = r["field"], r["fmt"]
    if key.startswith("="):
        return key[1:], "", "traced", r.get("note", "")
    exp = F.get(key)
    if exp is None:
        return key, "", "untraced", "listed by hand; the sources hold no such field"
    if fmt in ("date", "str"):
        return f"{F['@src'].get(key, '')} [{key}]", str(exp), "traced" if str(exp) == r["value"] else "stale", r.get("note", "")
    d = len(r["value"].split(".")[1]) if "." in r["value"] else 0
    want = f"{float(exp):.{d}f}" if d else str(int(float(f"{float(exp):.0f}")))
    return f"{F['@src'].get(key, '')} [{key}]", want, "traced" if want == r["value"] else "stale", r.get("note", "")


def pdf_normalize(t):
    t = t.replace("­", "").replace("−", "-")
    t = " ".join(t.split())
    t = re.sub(r"\b(8|10)-\s+([KQ])\b", r"\1-\2", t)   # a form name broken across lines
    return re.sub(r"(\d)-\s+(\d)", r"\1-\2", t)          # a date or an accession number broken across lines


def pdf_input_hash(root):
    return hashlib.sha256((Path(root) / "report/note.html").read_bytes()).hexdigest()


def extra_checks(root, F):
    """Whole-file checks that are not a figure in a sentence."""
    root = Path(root)
    out = []
    # the export limitation's "within a few jets" since 2022
    diffs = {y: F[f"middiff.{y}"] for y in range(2022, 2026) if f"middiff.{y}" in F}
    worst = max(abs(v) for v in diffs.values())
    out.append(("readme", "README.md (Limitations, Export)", "a few", "registry yearly mid-cabin count within a few jets of GD's "
                "since 2022", "registry_quarterly.csv minus gd_deliveries.csv, mid cabin, by full year " + json.dumps(diffs),
                f"largest gap {worst}", "traced" if worst <= 5 else "mismatch", "a few is read as five or fewer"))
    # the README's hero image and the committed charts must not predate the live state
    build = root / "docs/build/README.md"
    logs = sorted(p.name for p in (root / "docs/build").glob("*") if p.is_file() and p.suffix in (".md", ".csv", ".json"))
    ok = build.exists() and "as of its date" in build.read_text()
    out.append(("build-notes", "docs/build/ (%d files)" % len(logs), "", "dated build logs from v1; figures in them are as of "
                "their date", "docs/build/README.md notice", "", "traced" if ok else "stale",
                "" if ok else "no notice says these logs are dated and not updated"))
    return out
