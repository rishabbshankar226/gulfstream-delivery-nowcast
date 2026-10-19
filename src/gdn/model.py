"""The models of §3.4. Phase 2 writes the design window only."""
from pathlib import Path

from .fiscal import DESIGN, qrange, shift
from .files import read_csv, write_csv

BT_COLS = ["quarter", "window", "definition", "model", "large", "mid", "total", "actual", "ae", "ape_pct"]
CABINS = ("large", "mid")
DEFS = ("E1", "E2")


def load_reported(root="."):
    return {r["quarter"]: {"large": int(r["large"]), "mid": int(r["mid"]), "total": int(r["total"])}
            for r in read_csv(Path(root) / "data/processed/gd_deliveries.csv")}


def load_registry(root="."):
    out = {}
    for r in read_csv(Path(root) / "data/processed/registry_quarterly.csv"):
        out[r["quarter"]] = {e: {c: int(r[f"{e.lower()}_{c}"]) for c in CABINS} for e in DEFS}
    return out


def ratio(nq, n_lags, y_lags):
    """N(q) x sum of the four reported lags / sum of the four registry lags; the trailing mean of Y when
    the four registry lags sum to zero."""
    den = sum(n_lags)
    if den == 0:
        return sum(y_lags) / len(y_lags)
    return nq * sum(y_lags) / den


def forecast(q, model, Y, N=None, definition=None):
    """{"large", "mid"} for one quarter under seasonal, last, raw or ratio."""
    out = {}
    for c in CABINS:
        if model == "seasonal":
            out[c] = Y[shift(q, -4)][c]
        elif model == "last":
            out[c] = Y[shift(q, -1)][c]
        elif model == "raw":
            out[c] = N[q][definition][c]
        elif model == "ratio":
            lags = [shift(q, -k) for k in range(1, 5)]
            out[c] = ratio(N[q][definition][c], [N[x][definition][c] for x in lags], [Y[x][c] for x in lags])
        else:
            raise ValueError(model)
    return out


def row(q, window, definition, model, f, Y):
    total = f["large"] + f["mid"]
    actual = Y[q]["total"]
    ae = abs(total - actual)
    return {"quarter": q, "window": window, "definition": definition, "model": model, "large": f["large"],
            "mid": f["mid"], "total": total, "actual": actual, "ae": ae, "ape_pct": ae / actual * 100}


def design_rows(Y, N):
    rows = []
    for q in qrange(*DESIGN):
        for m in ("seasonal", "last"):
            rows.append(row(q, "design", "none", m, forecast(q, m, Y), Y))
        for e in DEFS:
            for m in ("raw", "ratio"):
                rows.append(row(q, "design", e, m, forecast(q, m, Y, N, e), Y))
    return rows


def mae(rows, model, definition):
    xs = [r["ae"] for r in rows if r["model"] == model and r["definition"] == definition]
    return sum(xs) / len(xs)


def choose(rows):
    """The definition with the lower design MAE of ratio; E1 on a tie."""
    m1, m2 = mae(rows, "ratio", "E1"), mae(rows, "ratio", "E2")
    return ("E2" if m2 < m1 else "E1"), m1, m2


def run_design(root="."):
    root = Path(root)
    Y, N = load_reported(root), load_registry(root)
    rows = design_rows(Y, N)
    write_csv(root / "results/design.csv", BT_COLS, rows)
    chosen, m1, m2 = choose(rows)
    for m, d in (("seasonal", "none"), ("last", "none"), ("raw", "E1"), ("ratio", "E1"), ("raw", "E2"),
                 ("ratio", "E2")):
        print(f"design MAE {m:8s} {d:4s} {mae(rows, m, d):.4f}")
    print(f"chosen definition {chosen} (ratio MAE E1 {m1!r}, E2 {m2!r})")
    return 0


# ---------- holdout (run only after the preregistration commit) ----------
import datetime as dt  # noqa: E402

from . import events, stats  # noqa: E402
from .fiscal import HOLDOUT, START, Calendar, qidx  # noqa: E402
from .files import read_json, write_json  # noqa: E402

GUIDE_COLS = ["call_date", "year", "outlook", "quote", "speaker", "url"]
HOLDOUT_MODELS = ("seasonal", "last", "guidance", "raw", "ratio")
BASELINES = ("guidance", "seasonal", "last")


def load_guidance(root="."):
    return [{"call_date": r["call_date"], "year": int(r["year"]),
             "outlook": float(r["outlook"]) if r["outlook"].strip() else None}
            for r in read_csv(Path(root) / "data/guidance.csv")]


def outlook_for(q, calls, cal):
    """G: the outlook for q's year from the latest call on or before q's fiscal end that stated a number."""
    end = cal.end(q)
    hits = [c for c in calls if c["year"] == int(q[:4]) and end and c["call_date"] <= end and c["outlook"] is not None]
    return max(hits, key=lambda c: c["call_date"])["outlook"] if hits else None


def guidance_pace(q, Y, calls, cal):
    """§3.4's guidance model, or None when no numeric outlook covers the quarter."""
    g = outlook_for(q, calls, cal)
    if g is None:
        return None
    t, k = int(q[:4]), int(q[5])
    years = range(t - 3, t)
    pooled = sum(Y[f"{y}Q{j}"]["total"] for y in years for j in range(1, 5))
    w = {j: sum(Y[f"{y}Q{j}"]["total"] for y in years) / pooled for j in range(1, 5)}
    ytd = sum(Y[f"{t}Q{j}"]["total"] for j in range(1, k))
    total = max(0.0, g - ytd) * w[k] / sum(w[j] for j in range(k, 5))
    lags = [shift(q, -i) for i in range(1, 5)]
    share = sum(Y[x]["large"] for x in lags) / sum(Y[x]["total"] for x in lags)
    large = total * share
    return {"large": large, "mid": total - large, "total": total, "outlook": g}


def guidance_forecast(q, Y, calls, cal):
    p = guidance_pace(q, Y, calls, cal)
    return ({"large": p["large"], "mid": p["mid"]}, True) if p else (forecast(q, "seasonal", Y), False)


def holdout_rows(Y, N, chosen, calls, cal):
    rows = []
    for q in qrange(*HOLDOUT):
        for m in ("seasonal", "last"):
            rows.append(row(q, "holdout", "none", m, forecast(q, m, Y), Y))
        rows.append(row(q, "holdout", "none", "guidance", guidance_forecast(q, Y, calls, cal)[0], Y))
        for m in ("raw", "ratio"):
            rows.append(row(q, "holdout", chosen, m, forecast(q, m, Y, N, chosen), Y))
    return rows


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def signed_errors(Y, N, chosen, quarters):
    out = []
    for q in quarters:
        f = forecast(q, "ratio", Y, N, chosen)
        out.append(f["large"] + f["mid"] - Y[q]["total"])
    return out


def truncated_mae(rows_air, Y, N, chosen, cal, d):
    """Ratio's holdout MAE with each quarter's own count cut d days before its end, lags whole."""
    aes = []
    for q in qrange(*HOLDOUT):
        lo, hi = cal.window(q)
        cut = (dt.date.fromisoformat(hi) - dt.timedelta(days=d)).isoformat()
        nq = {c: events.count(rows_air, chosen, c, lo, hi, cutoff=cut) for c in CABINS}
        lags = [shift(q, -k) for k in range(1, 5)]
        tot = sum(ratio(nq[c], [N[x][chosen][c] for x in lags], [Y[x][c] for x in lags]) for c in CABINS)
        aes.append(abs(tot - Y[q]["total"]))
    return _mean(aes)


def coverage_drift(Y, N, chosen):
    by = {}
    for q in qrange(START, HOLDOUT[1]):
        reg = N[q][chosen]["large"] + N[q][chosen]["mid"]
        if reg:
            by[q] = Y[q]["total"] / reg
    base = [by[q] for q in qrange("2017Q1", "2025Q2") if q in by]
    m = sum(base) / len(base)
    sd = (sum((x - m) ** 2 for x in base) / (len(base) - 1)) ** 0.5
    flags = [q for q in qrange("2025Q3", HOLDOUT[1]) if q in by and by[q] > m + 2 * sd]
    return {"by_quarter": by, "mean": m, "sd": sd, "flags": flags}


def holdout_metrics(design, hold, Y, N, chosen, calls, cal, rows_air):
    qs = qrange(*HOLDOUT)

    def model_rows(m):
        return [r for r in hold if r["model"] == m]

    def ae_of(m):
        return [r["ae"] for r in model_rows(m)]

    out = {"n": len(qs)}
    out["mae"] = {m: _mean(ae_of(m)) for m in HOLDOUT_MODELS}
    out["mape"] = {m: _mean([r["ape_pct"] for r in model_rows(m)]) for m in HOLDOUT_MODELS}
    out["bias"] = {m: _mean([r["total"] - r["actual"] for r in model_rows(m)]) for m in HOLDOUT_MODELS}
    out["mae_large"] = {m: _mean([abs(r["large"] - Y[r["quarter"]]["large"]) for r in model_rows(m)])
                        for m in HOLDOUT_MODELS}
    out["mae_mid"] = {m: _mean([abs(r["mid"] - Y[r["quarter"]]["mid"]) for r in model_rows(m)])
                      for m in HOLDOUT_MODELS}
    out["mae_ex_2020"] = {m: _mean([r["ae"] for r in model_rows(m) if not r["quarter"].startswith("2020")])
                          for m in HOLDOUT_MODELS}
    ratio_ae = ae_of("ratio")
    out["win_rate_vs_seasonal"] = sum(1 for a, b in zip(ratio_ae, ae_of("seasonal")) if a < b) / len(qs) * 100
    tests = {}
    for b in BASELINES:
        w, lo, t, p = stats.sign_test(ae_of(b), ratio_ae)
        tests[b] = {"wins": w, "losses": lo, "ties": t, "p_one_sided": p}
    rej = stats.holm({b: tests[b]["p_one_sided"] for b in BASELINES})
    for b in BASELINES:
        tests[b]["holm_reject"] = rej[b]
    out["tests"] = tests
    out["rel_mae"] = {b: out["mae"]["ratio"] / out["mae"][b] for b in BASELINES}
    out["autocorr_lag1"] = {b: stats.lag1([x - y for x, y in zip(ae_of(b), ratio_ae)]) for b in BASELINES}
    sourced = [q for q in qs if outlook_for(q, calls, cal) is not None]
    g_rows = {r["quarter"]: r for r in model_rows("guidance")}
    out["guidance"] = {"sourced": len(sourced), "fallback_quarters": [q for q in qs if q not in sourced],
                       "mae_sourced": _mean([g_rows[q]["ae"] for q in sourced]), "headline": len(sourced) >= 22}
    past = signed_errors(Y, N, chosen, qrange("2017Q1", "2019Q4"))
    by_q, hits = [], 0
    r_rows = {r["quarter"]: r for r in model_rows("ratio")}
    for q in qs:
        tot = r_rows[q]["total"]
        low, high = tot - stats.nearest_rank(past, 0.9), tot - stats.nearest_rank(past, 0.1)
        hit = low <= Y[q]["total"] <= high
        hits += hit
        by_q.append({"quarter": q, "low": low, "high": high, "hit": hit})
        past.append(tot - Y[q]["total"])
    lo, hi = stats.clopper_pearson(hits, len(qs))
    out["band"] = {"hits": hits, "n": len(qs), "coverage_pct": hits / len(qs) * 100,
                   "cp95_pct": [lo * 100, hi * 100], "by_quarter": by_q}
    out["truncation_mae"] = {str(d): truncated_mae(rows_air, Y, N, chosen, cal, d) for d in (0, 30, 60, 90)}
    out["coverage_ratio"] = coverage_drift(Y, N, chosen)
    return out


def design_metrics(design):
    return {"n": len({r["quarter"] for r in design}),
            "mae": {"none": {"seasonal": mae(design, "seasonal", "none"), "last": mae(design, "last", "none")},
                    "E1": {"raw": mae(design, "raw", "E1"), "ratio": mae(design, "ratio", "E1")},
                    "E2": {"raw": mae(design, "raw", "E2"), "ratio": mae(design, "ratio", "E2")}}}


def run_holdout(root="."):
    root = Path(root)
    if not (root / "docs/PREREGISTRATION.md").exists():
        raise SystemExit("No preregistration: the holdout runs only after docs/PREREGISTRATION.md is committed.")
    Y, N = load_reported(root), load_registry(root)
    design = design_rows(Y, N)
    chosen = choose(design)[0]
    calls, cal = load_guidance(root), Calendar.load(root)
    rows_air = events.read_serials_rows(read_csv(root / "data/processed/serials.csv"))
    hold = holdout_rows(Y, N, chosen, calls, cal)
    write_csv(root / "results/holdout.csv", BT_COLS, hold)
    band_errors = signed_errors(Y, N, chosen, qrange("2017Q1", HOLDOUT[1]))
    metrics = {"definition": chosen, "design": design_metrics(design),
               "holdout": holdout_metrics(design, hold, Y, N, chosen, calls, cal, rows_air),
               "band_errors": band_errors}
    write_json(root / "results/metrics.json", metrics)
    h = metrics["holdout"]
    print("holdout MAE", {m: round(v, 3) for m, v in h["mae"].items()})
    print("tests", {b: (t["wins"], t["losses"], t["ties"], round(t["p_one_sided"], 4), t["holm_reject"])
                    for b, t in h["tests"].items()})
    print("guidance sourced", h["guidance"]["sourced"], "band", h["band"]["hits"], "of", h["band"]["n"])
    return 0
