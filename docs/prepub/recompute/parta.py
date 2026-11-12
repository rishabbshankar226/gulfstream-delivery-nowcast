#!/usr/bin/env python3
"""Independent recompute, Part A: every figure from the processed files alone.

Usage:
  python3 parta.py <data_folder> [--guidance FILE] [--prediction FILE]
                   [--q3-reported LARGE,MID]

<data_folder> holds gd_deliveries.csv and registry_quarterly.csv.
Standard library only. Arithmetic is exact (fractions.Fraction); figures are
converted to float only when printed, to 6 decimals. Nothing is rounded before
that. No module of the audited repository is imported.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys
from fractions import Fraction as F

CABINS = ("large", "mid")
DEFS = ("E1", "E2")
DESIGN = ("2017Q1", "2019Q4")
HOLDOUT = ("2020Q1", "2026Q2")
DRIFT_BASE = ("2017Q1", "2025Q2")
DRIFT_WATCH = ("2025Q3", "2026Q2")


def qidx(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


def qlab(i):
    return "%dQ%d" % (i // 4, i % 4 + 1)


def qrange(a, b):
    return [qlab(i) for i in range(qidx(a), qidx(b) + 1)]


def lag(q, k):
    return qlab(qidx(q) - k)


def f6(x):
    if x is None:
        return "null"
    return "%.6f" % float(x)


def out(key, val):
    print("%s = %s" % (key, val))


def head(title):
    print()
    print("## " + title)


# ---------------------------------------------------------------- loading
def load(folder):
    Y, N = {}, {}
    with open(os.path.join(folder, "gd_deliveries.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            lg, md, tt = int(r["large"]), int(r["mid"]), int(r["total"])
            Y[r["quarter"]] = {"large": F(lg), "mid": F(md), "total": F(tt),
                               "fiscal_end": r["fiscal_end"],
                               "sum_ok": (lg + md == tt)}
    with open(os.path.join(folder, "registry_quarterly.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            N[r["quarter"]] = {
                "E1": {"large": F(int(r["e1_large"])), "mid": F(int(r["e1_mid"]))},
                "E2": {"large": F(int(r["e2_large"])), "mid": F(int(r["e2_mid"]))},
                "window_start": r["window_start"], "window_end": r["window_end"]}
    for q in N:
        for d in DEFS:
            N[q][d]["total"] = N[q][d]["large"] + N[q][d]["mid"]
    return Y, N


def load_guidance(path):
    rows = []
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            o = r["outlook"].strip()
            rows.append({"call_date": r["call_date"].strip(),
                         "year": int(r["year"]),
                         "outlook": (F(o) if o != "" else None)})
    return rows


# ---------------------------------------------------------------- models
def m_seasonal(Y, q):
    p = lag(q, 4)
    if p not in Y:
        return None
    return {c: Y[p][c] for c in CABINS + ("total",)}


def m_last(Y, q):
    p = lag(q, 1)
    if p not in Y:
        return None
    return {c: Y[p][c] for c in CABINS + ("total",)}


def m_raw(N, q, d):
    if q not in N:
        return None
    return {"large": N[q][d]["large"], "mid": N[q][d]["mid"],
            "total": N[q][d]["large"] + N[q][d]["mid"]}


def m_ratio(Y, N, q, d, n_now=None):
    """N(q) x sum Y(q-1..q-4) / sum N(q-1..q-4), per cabin; trailing mean of Y
    when the four N sum to zero. n_now overrides the quarter's own count."""
    lags = [lag(q, k) for k in (1, 2, 3, 4)]
    if any(l not in Y or l not in N for l in lags):
        return None
    if n_now is None:
        if q not in N:
            return None
        n_now = {c: N[q][d][c] for c in CABINS}
    r = {}
    for c in CABINS:
        sy = sum(Y[l][c] for l in lags)
        sn = sum(N[l][d][c] for l in lags)
        r[c] = (sy / 4) if sn == 0 else n_now[c] * sy / sn
    r["total"] = r["large"] + r["mid"]
    return r


def pick_outlook(G, year, fiscal_end, reading):
    """Reading A: the latest call on or before the fiscal end, among the calls
    that stated a number for the year (a no-number call is skipped and the
    earlier number carries forward).
    Reading B: the latest call on or before the fiscal end; when that call
    stated no number, the quarter has no outlook."""
    calls = [g for g in G if g["year"] == year and g["call_date"] <= fiscal_end]
    if reading == "A":
        calls = [g for g in calls if g["outlook"] is not None]
    if not calls:
        return None
    best = max(calls, key=lambda g: g["call_date"])
    if best["outlook"] is None:
        return None
    return best


def shares(Y, year, pooled=True):
    """w_j for j=1..4 over years year-3..year-1. pooled: sum over the three
    years of quarter j, over the three-year total. Not pooled: the mean of the
    three within-year shares."""
    yrs = [year - 3, year - 2, year - 1]
    need = ["%dQ%d" % (y, j) for y in yrs for j in (1, 2, 3, 4)]
    if any(n not in Y for n in need):
        return None
    if pooled:
        tot = sum(Y[n]["total"] for n in need)
        return [sum(Y["%dQ%d" % (y, j)]["total"] for y in yrs) / tot
                for j in (1, 2, 3, 4)]
    w = []
    for j in (1, 2, 3, 4):
        s = F(0)
        for y in yrs:
            yt = sum(Y["%dQ%d" % (y, i)]["total"] for i in (1, 2, 3, 4))
            s += Y["%dQ%d" % (y, j)]["total"] / yt
        w.append(s / 3)
    return w


def m_guidance(Y, G, q, fiscal_end, reading="A", pooled=True):
    """Returns (estimate dict, info dict). Falls back to seasonal with no
    numeric outlook."""
    year, k = int(q[:4]), int(q[5])
    call = pick_outlook(G, year, fiscal_end, reading)
    if call is None:
        s = m_seasonal(Y, q)
        return s, {"sourced": False, "outlook": None, "call_date": None}
    w = shares(Y, year, pooled)
    ytd = sum(Y["%dQ%d" % (year, j)]["total"] for j in range(1, k))
    rem = call["outlook"] - ytd
    if rem < 0:
        rem = F(0)
    total = rem * w[k - 1] / sum(w[k - 1:])
    lags = [lag(q, i) for i in (1, 2, 3, 4)]
    share_large = sum(Y[l]["large"] for l in lags) / sum(Y[l]["total"] for l in lags)
    large = total * share_large
    est = {"large": large, "mid": total - large, "total": total}
    return est, {"sourced": True, "outlook": call["outlook"],
                 "call_date": call["call_date"], "ytd": ytd,
                 "w_k_over_rest": w[k - 1] / sum(w[k - 1:]),
                 "share_large": share_large}


# ---------------------------------------------------------------- stats
def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def mae(Y, est, qs, cab="total"):
    return mean(abs(est[q][cab] - Y[q][cab]) for q in qs)


def sign_test(ae_r, ae_b, qs):
    w = sum(1 for q in qs if ae_r[q] < ae_b[q])
    l = sum(1 for q in qs if ae_r[q] > ae_b[q])
    t = sum(1 for q in qs if ae_r[q] == ae_b[q])
    n = w + l
    p = F(sum(math.comb(n, k) for k in range(w, n + 1)), 2 ** n)
    return w, l, t, p


def holm(pvals, alpha=F(5, 100)):
    """Step-down: sort ascending, compare p(i) with alpha/(m-i+1), stop at the
    first failure. Returns {name: (reject, threshold, adjusted p)}."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    res, stopped, run = {}, False, F(0)
    for i, (name, p) in enumerate(items):
        thr = alpha / (m - i)
        adj = min(F(1), (m - i) * p)
        run = max(run, adj)
        if not stopped and p <= thr:
            res[name] = (True, thr, run)
        else:
            stopped = True
            res[name] = (False, thr, run)
    return res


def autocorr1(D):
    n = len(D)
    if n < 3:
        return None
    m = sum(D) / n
    den = sum((d - m) ** 2 for d in D)
    if den == 0:
        return None
    num = sum((D[t] - m) * (D[t - 1] - m) for t in range(1, n))
    return num / den


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def bisect(fn, lo=0.0, hi=1.0):
    """Root of fn on [lo, hi]; fn(lo) and fn(hi) have opposite signs."""
    flo = fn(lo)
    for _ in range(200):
        mid = (lo + hi) / 2
        fm = fn(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, conf=0.95):
    a = (1 - conf) / 2
    lo = 0.0 if k == 0 else bisect(lambda p: (1 - binom_cdf(k - 1, n, p)) - a)
    hi = 1.0 if k == n else bisect(lambda p: binom_cdf(k, n, p) - a)
    return lo, hi


def nearest_rank(sorted_vals, p_num, p_den, float_ceil=False):
    """Element at position ceil(p x n), 1-based. Exact integer ceiling by
    default; float_ceil uses math.ceil(float(p) * n), which is what a naive
    implementation would do and can land one position higher."""
    n = len(sorted_vals)
    if float_ceil:
        pos = math.ceil((p_num / p_den) * n)
    else:
        pos = -((-p_num * n) // p_den)
    pos = max(1, min(n, pos))
    return sorted_vals[pos - 1], pos


def band_for(prior_errors, total, float_ceil=False):
    s = sorted(prior_errors)
    p10, pos10 = nearest_rank(s, 1, 10, float_ceil)
    p90, pos90 = nearest_rank(s, 9, 10, float_ceil)
    return total - p90, total - p10, p10, p90, pos10, pos90, len(s)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--guidance")
    ap.add_argument("--prediction")
    ap.add_argument("--q3-reported", default=None,
                    help="LARGE,MID reported by GD for the predicted quarter")
    a = ap.parse_args()

    Y, N = load(a.folder)
    G = load_guidance(a.guidance) if a.guidance else None
    allq = sorted(set(Y) & set(N), key=qidx)

    head("0. Inputs")
    out("input.folder", a.folder)
    out("input.gd_quarters", "%d (%s to %s)" % (len(Y), min(Y, key=qidx), max(Y, key=qidx)))
    out("input.registry_quarters", "%d (%s to %s)" % (len(N), min(N, key=qidx), max(N, key=qidx)))
    out("input.gd_rows_where_large_plus_mid_differs_from_total",
        ",".join(q for q in sorted(Y, key=qidx) if not Y[q]["sum_ok"]) or "none")
    bad = [q for q in allq if N[q]["window_end"] != Y[q]["fiscal_end"]]
    out("input.quarters_where_window_end_differs_from_fiscal_end", ",".join(bad) or "none")
    bad = [q for q in allq if lag(q, 1) in Y and N[q]["window_start"] != Y[lag(q, 1)]["fiscal_end"]]
    out("input.quarters_where_window_start_differs_from_prior_fiscal_end", ",".join(bad) or "none")
    out("input.guidance_rows", len(G) if G is not None else "no guidance file: guidance model skipped")

    # ratio under both definitions, every computable quarter
    R = {d: {} for d in DEFS}
    for d in DEFS:
        for q in allq:
            r = m_ratio(Y, N, q, d)
            if r is not None:
                R[d][q] = r
    comp = sorted(R["E1"], key=qidx)

    head("1. Ratio estimate, every computable quarter, E1 and E2")
    for d in DEFS:
        for q in comp:
            r = R[d][q]
            out("ratio.%s.%s.large" % (d, q), f6(r["large"]))
            out("ratio.%s.%s.mid" % (d, q), f6(r["mid"]))
            out("ratio.%s.%s.total" % (d, q), f6(r["total"]))

    head("1b. Ratio total, GD count and absolute error, every computable quarter (the toy check reads this block)")
    for d in DEFS:
        for q in comp:
            out("check.%s.%s.ratio_total" % (d, q), f6(R[d][q]["total"]))
            out("check.%s.%s.reported_total" % (d, q), f6(Y[q]["total"]))
            out("check.%s.%s.abs_error" % (d, q), f6(abs(R[d][q]["total"] - Y[q]["total"])))
        out("check.%s.n_quarters" % d, len(comp))
        out("check.%s.quarters" % d, "%s to %s" % (comp[0], comp[-1]) if comp else "none")
        out("check.%s.mae_all_computable" % d, f6(mae(Y, R[d], comp)))

    # ------------------------------------------------------------ design
    dq = [q for q in qrange(*DESIGN) if q in R["E1"]]
    chosen = "E1"
    head("2. Design window %s to %s" % DESIGN)
    if len(dq) != len(qrange(*DESIGN)):
        out("design.status", "skipped: window not in the data (%d of %d quarters)" % (len(dq), len(qrange(*DESIGN))))
        dq = []
    else:
        S = {q: m_seasonal(Y, q) for q in dq}
        L = {q: m_last(Y, q) for q in dq}
        out("design.n", len(dq))
        out("design.mae.seasonal", f6(mae(Y, S, dq)))
        out("design.mae.last", f6(mae(Y, L, dq)))
        dm = {}
        for d in DEFS:
            RAW = {q: m_raw(N, q, d) for q in dq}
            out("design.mae.raw.%s" % d, f6(mae(Y, RAW, dq)))
            dm[d] = mae(Y, R[d], dq)
            out("design.mae.ratio.%s" % d, f6(dm[d]))
        chosen = "E1" if dm["E1"] <= dm["E2"] else "E2"
        out("design.mae.ratio.E1_minus_E2", f6(dm["E1"] - dm["E2"]))
        out("design.chosen_definition", chosen)
        out("design.rule", "lower design MAE of ratio, E1 on a tie")
        diff = [q for q in qrange("2016Q1", "2019Q4") if q in N and
                (N[q]["E1"]["large"] != N[q]["E2"]["large"] or N[q]["E1"]["mid"] != N[q]["E2"]["mid"])]
        out("design.quarters_2016Q1_2019Q4_where_E1_and_E2_counts_differ", ",".join(diff) or "none")

    # ------------------------------------------------------------ holdout
    hq = [q for q in qrange(*HOLDOUT) if q in R[chosen]]
    if len(hq) != len(qrange(*HOLDOUT)):
        head("3-12. Holdout")
        out("holdout.status", "skipped: window not in the data (%d of %d quarters)" % (len(hq), len(qrange(*HOLDOUT))))
        return
    d = chosen
    M = {"ratio": {q: R[d][q] for q in hq},
         "raw": {q: m_raw(N, q, d) for q in hq},
         "seasonal": {q: m_seasonal(Y, q) for q in hq},
         "last": {q: m_last(Y, q) for q in hq}}
    GI = {}
    variants = {}
    if G is not None:
        for reading in ("A", "B"):
            est, info = {}, {}
            for q in hq:
                est[q], info[q] = m_guidance(Y, G, q, Y[q]["fiscal_end"], reading, True)
            variants[reading] = (est, info)
        est, info = {}, {}
        for q in hq:
            est[q], info[q] = m_guidance(Y, G, q, Y[q]["fiscal_end"], "A", False)
        variants["A_meanshare"] = (est, info)
        M["guidance"] = variants["A"][0]
        GI = variants["A"][1]
        M["guidance_readingB"] = variants["B"][0]
    order = ["ratio", "raw"] + (["guidance"] if G is not None else []) + ["seasonal", "last"]
    extra = ["guidance_readingB"] if G is not None else []
    AE = {m: {q: abs(M[m][q]["total"] - Y[q]["total"]) for q in hq} for m in M}
    ex2020 = [q for q in hq if q[:4] != "2020"]

    head("3. Holdout %s to %s, definition %s, five models" % (HOLDOUT[0], HOLDOUT[1], d))
    out("holdout.n", len(hq))
    out("holdout.definition", d)
    out("holdout.n_ex_2020", len(ex2020))
    for m in order + extra:
        out("holdout.mae.%s" % m, f6(mae(Y, M[m], hq)))
        out("holdout.mape_pct.%s" % m, f6(mean(AE[m][q] / Y[q]["total"] * 100 for q in hq)))
        out("holdout.wape_pct_sumAE_over_sumActual.%s" % m,
            f6(sum(AE[m][q] for q in hq) / sum(Y[q]["total"] for q in hq) * 100))
        out("holdout.bias.%s" % m, f6(mean(M[m][q]["total"] - Y[q]["total"] for q in hq)))
        out("holdout.mae_large.%s" % m, f6(mae(Y, M[m], hq, "large")))
        out("holdout.mae_mid.%s" % m, f6(mae(Y, M[m], hq, "mid")))
        out("holdout.mae_ex_2020.%s" % m, f6(mae(Y, M[m], ex2020)))
    for q in hq:
        out("holdout.by_quarter.%s" % q, "reported=%s ratio=%s raw=%s %sseasonal=%s last=%s" % (
            f6(Y[q]["total"]), f6(M["ratio"][q]["total"]), f6(M["raw"][q]["total"]),
            ("guidance=%s " % f6(M["guidance"][q]["total"])) if G is not None else "",
            f6(M["seasonal"][q]["total"]), f6(M["last"][q]["total"])))

    head("4. Holdout MAE by calendar year")
    for yr in sorted(set(q[:4] for q in hq)):
        qs = [q for q in hq if q[:4] == yr]
        out("holdout.year.%s.n" % yr, len(qs))
        for m in order + extra:
            out("holdout.year.%s.mae.%s" % (yr, m), f6(mae(Y, M[m], qs)))

    head("5. Exact one-sided sign tests (ratio AE lower than the baseline's), Holm at 0.05")
    baselines = (["guidance"] if G is not None else []) + ["seasonal", "last"]

    def test_block(tag, bl_map, qs_map):
        pv = {}
        for b in bl_map:
            w, l, t, p = sign_test(AE["ratio"], AE[bl_map[b]], qs_map[b])
            pv[b] = p
            out("%s.%s.n_quarters" % (tag, b), len(qs_map[b]))
            out("%s.%s.wins" % (tag, b), w)
            out("%s.%s.losses" % (tag, b), l)
            out("%s.%s.ties" % (tag, b), t)
            out("%s.%s.p_one_sided" % (tag, b), f6(p))
            out("%s.%s.p_one_sided_full" % (tag, b), repr(float(p)))
        hres = holm(pv)
        for b in bl_map:
            rej, thr, adj = hres[b]
            out("%s.%s.holm_threshold" % (tag, b), f6(thr))
            out("%s.%s.holm_adjusted_p" % (tag, b), f6(adj))
            out("%s.%s.holm_reject" % (tag, b), "true" if rej else "false")
        for b in bl_map:
            qs = qs_map[b]
            mr, mb = mae(Y, M["ratio"], qs), mae(Y, M[bl_map[b]], qs)
            out("%s.%s.rel_mae" % (tag, b), f6(mr / mb) if mb != 0 else "null")
        return pv

    test_block("tests", {b: b for b in baselines}, {b: hq for b in baselines})
    out("tests.win_rate_vs_seasonal_pct",
        f6(F(sum(1 for q in hq if AE["ratio"][q] < AE["seasonal"][q]) * 100, len(hq))))

    # float cross-check of the win/loss/tie counts (two operation orders)
    for tag, fn in (("n_times_sy_over_sn", lambda n, sy, sn: n * (sy / sn)),
                    ("n_times_sy_then_over_sn", lambda n, sy, sn: (n * sy) / sn)):
        aef = {}
        for q in hq:
            tot = 0.0
            for c in CABINS:
                lags = [lag(q, k) for k in (1, 2, 3, 4)]
                sy = float(sum(Y[l][c] for l in lags))
                sn = float(sum(N[l][d][c] for l in lags))
                tot += (sy / 4.0) if sn == 0 else fn(float(N[q][d][c]), sy, sn)
            aef[q] = abs(tot - float(Y[q]["total"]))
        for b in baselines:
            bf = {q: float(AE[b][q]) for q in hq}
            w = sum(1 for q in hq if aef[q] < bf[q])
            l = sum(1 for q in hq if aef[q] > bf[q])
            t = sum(1 for q in hq if aef[q] == bf[q])
            out("tests.floatcheck.%s.%s.wins_losses_ties" % (tag, b), "%d,%d,%d" % (w, l, t))

    if G is not None:
        src = [q for q in hq if GI[q]["sourced"]]
        infoB = variants["B"][1]
        srcB = [q for q in hq if infoB[q]["sourced"]]
        print("# variant: guidance test over the sourced quarters only (reading A)")
        test_block("tests_variant_sourced_only", {b: b for b in baselines},
                   {"guidance": src, "seasonal": hq, "last": hq})
        print("# variant: guidance by reading B, all 26 quarters with fallback")
        test_block("tests_variant_readingB", {"guidance": "guidance_readingB", "seasonal": "seasonal", "last": "last"},
                   {b: hq for b in baselines})
        print("# variant: guidance by reading B, its sourced quarters only")
        test_block("tests_variant_readingB_sourced_only",
                   {"guidance": "guidance_readingB", "seasonal": "seasonal", "last": "last"},
                   {"guidance": srcB, "seasonal": hq, "last": hq})

    head("6. Lag-1 autocorrelation of D = AE(baseline) - AE(ratio), quarter order")
    for b in baselines:
        D = [AE[b][q] - AE["ratio"][q] for q in hq]
        out("autocorr_lag1.%s" % b, f6(autocorr1(D)))
        out("autocorr_lag1.%s.mean_D" % b, f6(mean(D)))
    if G is not None:
        D = [AE["guidance"][q] - AE["ratio"][q] for q in src]
        out("autocorr_lag1.guidance_sourced_quarters_only_n%d" % len(src), f6(autocorr1(D)))
        D = [AE["guidance_readingB"][q] - AE["ratio"][q] for q in hq]
        out("autocorr_lag1.guidance_readingB", f6(autocorr1(D)))

    head("7. Guidance pace")
    pace_q3 = None
    if G is None:
        out("guidance.status", "skipped: no guidance file")
    else:
        for q in hq:
            i = GI[q]
            out("guidance.%s.source" % q, "outlook" if i["sourced"] else "fallback_seasonal")
            out("guidance.%s.outlook_used" % q, f6(i["outlook"]) if i["sourced"] else "none")
            out("guidance.%s.call_date" % q, i["call_date"] if i["sourced"] else "none")
            if i["sourced"]:
                out("guidance.%s.ytd_reported" % q, f6(i["ytd"]))
                out("guidance.%s.share_of_remaining" % q, f6(i["w_k_over_rest"]))
                out("guidance.%s.large_share" % q, f6(i["share_large"]))
            out("guidance.%s.large" % q, f6(M["guidance"][q]["large"]))
            out("guidance.%s.mid" % q, f6(M["guidance"][q]["mid"]))
            out("guidance.%s.total" % q, f6(M["guidance"][q]["total"]))
            out("guidance.%s.reported_total" % q, f6(Y[q]["total"]))
            out("guidance.%s.abs_error" % q, f6(AE["guidance"][q]))
        fb = [q for q in hq if not GI[q]["sourced"]]
        out("guidance.sourced_quarters", len(src))
        out("guidance.fallback_quarters", ",".join(fb) or "none")
        out("guidance.fallback_to", "seasonal (same quarter last year)")
        out("guidance.headline_baseline_is_guidance_at_22_or_more", "true" if len(src) >= 22 else "false")
        out("guidance.mae_sourced.guidance", f6(mae(Y, M["guidance"], src)))
        out("guidance.mae_sourced.ratio", f6(mae(Y, M["ratio"], src)))
        out("guidance.mae_sourced.seasonal", f6(mae(Y, M["seasonal"], src)))
        out("guidance.mae_sourced.last", f6(mae(Y, M["last"], src)))
        out("guidance.mae_sourced.raw", f6(mae(Y, M["raw"], src)))
        print("# reading B (the latest call must itself state the number)")
        fbB = [q for q in hq if not infoB[q]["sourced"]]
        out("guidance_readingB.sourced_quarters", len(srcB))
        out("guidance_readingB.fallback_quarters", ",".join(fbB) or "none")
        out("guidance_readingB.headline_baseline_is_guidance_at_22_or_more", "true" if len(srcB) >= 22 else "false")
        out("guidance_readingB.mae_all26_with_fallback", f6(mae(Y, M["guidance_readingB"], hq)))
        out("guidance_readingB.mae_sourced.guidance", f6(mae(Y, M["guidance_readingB"], srcB)))
        out("guidance_readingB.mae_sourced.ratio", f6(mae(Y, M["ratio"], srcB)))
        out("guidance_readingB.mae_sourced.seasonal", f6(mae(Y, M["seasonal"], srcB)))
        print("# variant: reading A with w_j as the mean of three within-year shares instead of pooled")
        ms = variants["A_meanshare"][0]
        out("guidance_meanshare.mae_all26_with_fallback", f6(mae(Y, ms, hq)))
        out("guidance_meanshare.mae_sourced", f6(mae(Y, ms, src)))
        out("guidance_meanshare.max_abs_difference_in_total_vs_pooled",
            f6(max(abs(ms[q]["total"] - M["guidance"][q]["total"]) for q in hq)))
        # the live quarter after the last reported one
        nq = qlab(qidx(max(Y, key=qidx)) + 1)
        fe = None
        if a.prediction:
            with open(a.prediction, "rb") as fh:
                pj = json.loads(fh.read().decode("utf-8"))
            if pj.get("quarter") == nq:
                fe = pj.get("window_end")
        if fe is None and nq == "2026Q3":
            fe = "2026-10-04"
        if fe is not None:
            for reading in ("A", "B"):
                est, info = m_guidance(Y, G, nq, fe, reading, True)
                t = "guidance.%s" % nq if reading == "A" else "guidance_readingB.%s" % nq
                out(t + ".fiscal_end_used", fe)
                out(t + ".source", "outlook" if info["sourced"] else "fallback_seasonal")
                out(t + ".outlook_used", f6(info["outlook"]) if info["sourced"] else "none")
                out(t + ".call_date", info["call_date"] if info["sourced"] else "none")
                if info["sourced"]:
                    out(t + ".ytd_reported", f6(info["ytd"]))
                    out(t + ".share_of_remaining", f6(info["w_k_over_rest"]))
                    out(t + ".large_share", f6(info["share_large"]))
                out(t + ".large", f6(est["large"]))
                out(t + ".mid", f6(est["mid"]))
                out(t + ".total", f6(est["total"]))
                if reading == "A":
                    pace_q3 = (nq, est, info)

    head("8. Past-miss band, holdout quarters")
    bq = [q for q in comp if qidx(q) >= qidx("2017Q1")]
    err = {q: R[d][q]["total"] - Y[q]["total"] for q in bq}
    for variant, fc in (("band", False), ("band_floatceil", True)):
        hits = 0
        if fc:
            print("# variant: position computed as math.ceil(float(p) * n) instead of the exact ceiling")
        for q in hq:
            prior = [err[p] for p in bq if qidx(p) < qidx(q)]
            lo, hi, p10, p90, pos10, pos90, n = band_for(prior, R[d][q]["total"], fc)
            hit = lo <= Y[q]["total"] <= hi
            hits += 1 if hit else 0
            if not fc:
                out("%s.%s.n_prior_errors" % (variant, q), n)
                out("%s.%s.p10_position" % (variant, q), pos10)
                out("%s.%s.p90_position" % (variant, q), pos90)
                out("%s.%s.p10" % (variant, q), f6(p10))
                out("%s.%s.p90" % (variant, q), f6(p90))
                out("%s.%s.low" % (variant, q), f6(lo))
                out("%s.%s.high" % (variant, q), f6(hi))
                out("%s.%s.reported" % (variant, q), f6(Y[q]["total"]))
                out("%s.%s.hit" % (variant, q), "hit" if hit else "miss")
            else:
                lo0, hi0, _, _, e10, e90, _ = band_for(prior, R[d][q]["total"], False)
                if (pos10, pos90) != (e10, e90):
                    out("%s.%s.differs" % (variant, q),
                        "n=%d p10_position=%d (exact %d) p90_position=%d (exact %d) low=%s high=%s hit=%s" % (
                            n, pos10, e10, pos90, e90, f6(lo), f6(hi), "hit" if hit else "miss"))
        out("%s.hits" % variant, hits)
        out("%s.n" % variant, len(hq))
        out("%s.coverage_pct" % variant, f6(F(hits * 100, len(hq))))
        lo, hi = clopper_pearson(hits, len(hq))
        out("%s.cp95_low_pct" % variant, f6(lo * 100))
        out("%s.cp95_high_pct" % variant, f6(hi * 100))
    out("band.nominal_coverage_pct_P10_to_P90", f6(80))
    out("band.misses_above_band", ",".join(q for q in hq if Y[q]["total"] > band_for(
        [err[p] for p in bq if qidx(p) < qidx(q)], R[d][q]["total"])[1]) or "none")
    out("band.misses_below_band", ",".join(q for q in hq if Y[q]["total"] < band_for(
        [err[p] for p in bq if qidx(p) < qidx(q)], R[d][q]["total"])[0]) or "none")
    for q in bq:
        out("band_errors.%s" % q, f6(err[q]))

    head("9. Deliveries per registry event (reported total / registry total, %s)" % d)
    C = {}
    for q in allq:
        nt = N[q][d]["large"] + N[q][d]["mid"]
        if nt != 0:
            C[q] = Y[q]["total"] / nt
        out("coverage_ratio.%s" % q, f6(C.get(q)))
    base = [C[q] for q in qrange(*DRIFT_BASE) if q in C]
    mu = sum(base) / len(base)
    var = sum((x - mu) ** 2 for x in base) / (len(base) - 1)
    sd = math.sqrt(var)
    out("coverage_ratio.base_window", "%s to %s" % DRIFT_BASE)
    out("coverage_ratio.base_n", len(base))
    out("coverage_ratio.mean", f6(mu))
    out("coverage_ratio.sd_sample", f6(sd))
    out("coverage_ratio.sd_population_for_reference", f6(math.sqrt(float(var) * (len(base) - 1) / len(base))))
    thr = float(mu) + 2 * sd
    out("coverage_ratio.mean_plus_2sd", f6(thr))
    out("coverage_ratio.mean_minus_2sd", f6(float(mu) - 2 * sd))
    flags = [q for q in qrange(*DRIFT_WATCH) if q in C and float(C[q]) > thr]
    for q in qrange(*DRIFT_WATCH):
        if q in C:
            out("coverage_ratio.watch.%s" % q, "%s above_mean_plus_2sd=%s below_mean_minus_2sd=%s z=%s" % (
                f6(C[q]), "true" if float(C[q]) > thr else "false",
                "true" if float(C[q]) < float(mu) - 2 * sd else "false",
                f6((float(C[q]) - float(mu)) / sd)))
    out("coverage_ratio.flags_above_mean_plus_2sd", ",".join(flags) or "none")
    print("# inverse: registry events per delivery by calendar year (pooled: sum of events / sum of deliveries)")
    for yr in sorted(set(q[:4] for q in allq)):
        qs = [q for q in allq if q[:4] == yr]
        sy = sum(Y[q]["total"] for q in qs)
        sn = sum(N[q][d]["large"] + N[q][d]["mid"] for q in qs)
        sym = sum(Y[q]["mid"] for q in qs)
        snm = sum(N[q][d]["mid"] for q in qs)
        syl = sum(Y[q]["large"] for q in qs)
        snl = sum(N[q][d]["large"] for q in qs)
        out("events_per_delivery.%s.n_quarters" % yr, len(qs))
        out("events_per_delivery.%s.total" % yr, f6(sn / sy))
        out("events_per_delivery.%s.mid" % yr, f6(snm / sym) if sym != 0 else "null")
        out("events_per_delivery.%s.large" % yr, f6(snl / syl) if syl != 0 else "null")
        out("events_per_delivery.%s.sums" % yr, "events_total=%d deliveries_total=%d events_mid=%d deliveries_mid=%d" % (sn, sy, snm, sym))
        out("events_per_delivery_mean_of_quarters.%s.total" % yr,
            f6(mean((N[q][d]["large"] + N[q][d]["mid"]) / Y[q]["total"] for q in qs)))
        out("events_per_delivery_mean_of_quarters.%s.mid" % yr,
            f6(mean(N[q][d]["mid"] / Y[q]["mid"] for q in qs)) if all(Y[q]["mid"] != 0 for q in qs) else "null")

    head("10. Five holdout quarters with the largest absolute error of ratio")
    top = sorted(hq, key=lambda q: (-AE["ratio"][q], qidx(q)))[:5]
    for i, q in enumerate(top, 1):
        out("top_miss.%d" % i, "%s estimate=%s reported=%s signed_error=%s abs_error=%s" % (
            q, f6(M["ratio"][q]["total"]), f6(Y[q]["total"]),
            f6(M["ratio"][q]["total"] - Y[q]["total"]), f6(AE["ratio"][q])))
    sixth = sorted(hq, key=lambda q: (-AE["ratio"][q], qidx(q)))[5]
    out("top_miss.6_for_reference", "%s abs_error=%s" % (sixth, f6(AE["ratio"][sixth])))

    head("11. 2026Q3 score")
    if not a.prediction or not a.q3_reported:
        out("score.status", "skipped: no prediction file or reported count given")
    else:
        with open(a.prediction, "rb") as fh:
            raw = fh.read()
        pj = json.loads(raw.decode("utf-8"))
        lg, md = [int(x) for x in a.q3_reported.split(",")]
        rep = lg + md
        tot = F(repr(pj["nowcast"]["total"]))
        plg, pmd = F(repr(pj["nowcast"]["large"])), F(repr(pj["nowcast"]["mid"]))
        blo, bhi = F(repr(pj["band"][0])), F(repr(pj["band"][1]))
        out("score.quarter", pj["quarter"])
        out("score.prediction_sha256", hashlib.sha256(raw).hexdigest())
        out("score.prediction_bytes", len(raw))
        out("score.prediction_has_crlf", "true" if b"\r" in raw else "false")
        out("score.prediction_ends_with_newline", "true" if raw.endswith(b"\n") else "false")
        out("score.snapshot", pj["snapshot"])
        out("score.definition", pj["definition"])
        out("score.made_utc", pj["made_utc"])
        out("score.reported.large", lg)
        out("score.reported.mid", md)
        out("score.reported.total", rep)
        out("score.locked.large", f6(plg))
        out("score.locked.mid", f6(pmd))
        out("score.locked.total", f6(tot))
        out("score.locked.large_plus_mid_minus_total", f6(plg + pmd - tot))
        out("score.signed_error_total", f6(tot - rep))
        out("score.ae_total", f6(abs(tot - rep)))
        out("score.ape_pct", f6(abs(tot - rep) / rep * 100))
        out("score.ae_large", f6(abs(plg - lg)))
        out("score.ae_mid", f6(abs(pmd - md)))
        out("score.band_low", f6(blo))
        out("score.band_high", f6(bhi))
        out("score.inside_band", "true" if blo <= rep <= bhi else "false")
        out("score.reported_minus_band_high", f6(rep - bhi))
        # the lock's own arithmetic, from its stored events and trailing sums
        ev, tr = pj["events"], pj["trailing"]
        rl = F(ev["large"]) * tr["reported"]["large"] / tr["registry"]["large"]
        rm = F(ev["mid"]) * tr["reported"]["mid"] / tr["registry"]["mid"]
        out("score.lock_arithmetic.large_from_its_events_and_trailing", f6(rl))
        out("score.lock_arithmetic.mid_from_its_events_and_trailing", f6(rm))
        out("score.lock_arithmetic.total_from_its_events_and_trailing", f6(rl + rm))
        lags = [lag(pj["quarter"], k) for k in (1, 2, 3, 4)]
        if all(l in Y for l in lags):
            out("score.trailing_reported_large_from_gd_file", f6(sum(Y[l]["large"] for l in lags)))
            out("score.trailing_reported_mid_from_gd_file", f6(sum(Y[l]["mid"] for l in lags)))
            out("score.trailing_registry_large_from_processed_file_backtest_snapshot",
                f6(sum(N[l][d]["large"] for l in lags)))
            out("score.trailing_registry_mid_from_processed_file_backtest_snapshot",
                f6(sum(N[l][d]["mid"] for l in lags)))
            out("score.seasonal_total", f6(Y[lag(pj["quarter"], 4)]["total"]))
            out("score.seasonal_ae", f6(abs(Y[lag(pj["quarter"], 4)]["total"] - rep)))
            out("score.last_total", f6(Y[lag(pj["quarter"], 1)]["total"]))
            out("score.last_ae", f6(abs(Y[lag(pj["quarter"], 1)]["total"] - rep)))
            out("score.raw_events_total_in_lock", ev["large"] + ev["mid"])
            out("score.raw_ae", abs(ev["large"] + ev["mid"] - rep))
        if pace_q3 is not None and pace_q3[0] == pj["quarter"]:
            est = pace_q3[1]
            out("score.guidance_pace.large", f6(est["large"]))
            out("score.guidance_pace.mid", f6(est["mid"]))
            out("score.guidance_pace.total", f6(est["total"]))
            out("score.guidance_ae", f6(abs(est["total"] - rep)))
        # live band from the processed file's errors (backtest snapshot)
        allerr = [err[q] for q in bq]
        for variant, fc in (("exact_ceiling", False), ("float_ceiling", True)):
            lo, hi, p10, p90, pos10, pos90, n = band_for(allerr, tot, fc)
            out("score.band_rebuilt_from_processed_errors.%s" % variant,
                "n=%d p10_position=%d p90_position=%d p10=%s p90=%s low=%s high=%s" % (
                    n, pos10, pos90, f6(p10), f6(p90), f6(lo), f6(hi)))

    head("12. GD averages")
    out("gd.mean_quarterly_deliveries_%s_%s" % HOLDOUT, f6(mean(Y[q]["total"] for q in hq)))
    out("gd.sum_deliveries_%s_%s" % HOLDOUT, f6(sum(Y[q]["total"] for q in hq)))
    out("gd.mean_quarterly_large_%s_%s" % HOLDOUT, f6(mean(Y[q]["large"] for q in hq)))
    out("gd.mean_quarterly_mid_%s_%s" % HOLDOUT, f6(mean(Y[q]["mid"] for q in hq)))
    if "2025Q3" in Y:
        out("gd.2025Q3.large", f6(Y["2025Q3"]["large"]))
        out("gd.2025Q3.mid", f6(Y["2025Q3"]["mid"]))
        out("gd.2025Q3.total", f6(Y["2025Q3"]["total"]))
    for yr in sorted(set(q[:4] for q in Y)):
        qs = [q for q in Y if q[:4] == yr]
        out("gd.year_total.%s" % yr, "%d (%d quarters)" % (sum(Y[q]["total"] for q in qs), len(qs)))


if __name__ == "__main__":
    main()
