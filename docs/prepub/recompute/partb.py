#!/usr/bin/env python3
"""Independent recompute, Part B: airframe table and counts from the stored
FAA registry subsets, by docs/PREREGISTRATION.md section 3.3.

Usage:
  python3 partb.py <snapshots_dir> <backtest_date> <lock_date>
                   <processed_folder> <prediction_json>

Standard library only. No module of the audited repository is imported.
"""
import collections
import csv
import datetime as dt
import gzip
import json
import math
import os
import re
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parta as A  # my own Part A helpers (same scratch folder)

CABINS = ("large", "mid")
MID_PATTERNS = ("G280", "G150", "G200", "G100")
# model names that are mid-cabin types (G100/Astra, G150, G200/Galaxy, G280)
# whatever the preregistered rule says. Hand list, from the ACFTREF rows.
MID_TYPE_BY_NAME = re.compile(r"(^|[^0-9])(100|150|200|280)([^0-9]|$)|GALAXY|ASTRA")


def f6(x):
    return A.f6(x)


def out(k, v):
    print("%s = %s" % (k, v))


def head(t):
    print()
    print("## " + t)


def norm_header(h):
    return re.sub(r"[^A-Z0-9]", "", h.replace("﻿", "").upper())


def read_table(path):
    """Header + rows as dicts keyed by the normalized header. csv split; the
    fixed-width fallback of section 3.3 is counted, never needed (see output)."""
    raw = gzip.open(path, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    lines = text.split("\n")
    hdr_line = lines[0].rstrip("\r")
    hcells = next(csv.reader([hdr_line]))
    names = [norm_header(h) for h in hcells]
    rows, mismatch = [], 0
    for ln in lines[1:]:
        ln = ln.rstrip("\r")
        if ln.strip() == "":
            continue
        cells = next(csv.reader([ln]))
        if len(cells) != len(hcells):
            mismatch += 1
            continue
        rows.append({names[i]: cells[i].strip() for i in range(len(names)) if names[i] != ""})
    return names, rows, mismatch


BAD_DATES = collections.Counter()


def parse_date(s, field=""):
    s = (s or "").strip()
    if s == "":
        return None
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", s)
    if not m:
        m2 = re.fullmatch(r"(\d{4})([/-])(\d{2})\2(\d{2})", s)
        if m2:
            y, mo, d = int(m2.group(1)), int(m2.group(3)), int(m2.group(4))
        else:
            BAD_DATES[field] += 1
            return None
    else:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return dt.date(y, mo, d)
    except ValueError:
        BAD_DATES[field] += 1
        return None


def build(snapdir):
    st = {}
    _, acft, mm_a = read_table(os.path.join(snapdir, "ACFTREF.txt.gz"))
    mnames, master, mm_m = read_table(os.path.join(snapdir, "MASTER.txt.gz"))
    dnames, dereg, mm_d = read_table(os.path.join(snapdir, "DEREG.txt.gz"))
    st["field_count_mismatch_lines"] = mm_a + mm_m + mm_d
    st["acftref_rows"], st["master_rows"], st["dereg_rows"] = len(acft), len(master), len(dereg)
    st["master_has_yearmfr"] = "YEARMFR" in mnames
    st["dereg_has_yearmfr"] = "YEARMFR" in dnames
    codes = {}
    out_of_scope = []
    for r in acft:
        mfr, model, te = r["MFR"].upper(), r["MODEL"].upper(), r["TYPEENG"]
        in_scope = ("GULFSTREAM" in mfr or "GULFSTREAM" in model) and te in ("4", "5")
        if not in_scope:
            out_of_scope.append(r["CODE"])
            continue
        mid = any(p in model for p in MID_PATTERNS) or mfr.startswith("IAI") or mfr.startswith("ISRAEL")
        codes[r["CODE"]] = {"mfr": mfr, "model": model, "typeeng": te,
                            "cabin": "mid" if mid else "large"}
    st["acftref_in_scope_codes"] = len(codes)
    st["acftref_out_of_scope_codes_in_subset"] = ",".join(out_of_scope) or "none"

    recs = collections.defaultdict(list)
    st["master_blank_serial"] = st["dereg_blank_serial"] = 0
    st["master_out_of_scope_rows"] = st["dereg_out_of_scope_rows"] = 0
    for src, rows in (("MASTER", master), ("DEREG", dereg)):
        for r in rows:
            serial = r["SERIALNUMBER"]
            if serial == "":
                st[src.lower() + "_blank_serial"] += 1
                continue
            code = r["MFRMDLCODE"]
            if code not in codes:
                st[src.lower() + "_out_of_scope_rows"] += 1
                continue
            key = (code[:3], serial.upper())
            ym = r.get("YEARMFR", "")
            recs[key].append({
                "src": src, "code": code, "name": r["NAME"], "n": r["NNUMBER"],
                "held": r["NAME"].startswith("GULFSTREAM AEROSPACE"),
                "cert": parse_date(r["CERTISSUEDATE"], src + ".CERTISSUEDATE"),
                "aw": parse_date(r["AIRWORTHDATE"], src + ".AIRWORTHDATE"),
                "year": int(ym) if re.fullmatch(r"\d{4}", ym) and 1900 <= int(ym) <= 2099 else None,
                "cancel": parse_date(r.get("CANCELDATE", ""), src + ".CANCELDATE") if src == "DEREG" else None,
                "exp": r.get("EXPCOUNTRY", "") if src == "DEREG" else ""})
    air = {}
    for key, rs in recs.items():
        a = {"mfr_code": key[0], "serial": key[1], "n_records": len(rs)}
        cust = [r["cert"] for r in rs if not r["held"] and r["cert"]]
        a["customer_cert"] = min(cust) if cust else None
        gc = [r["cancel"] for r in rs if r["held"] and r["src"] == "DEREG" and r["cancel"]]
        a["gulfstream_cancel"] = min(gc) if gc else None
        ex = [(r["cancel"], r["exp"]) for r in rs
              if r["held"] and r["src"] == "DEREG" and r["cancel"] and r["exp"] != ""]
        if ex:
            a["export_cancel"], a["export_country"] = min(ex)
        else:
            a["export_cancel"], a["export_country"] = None, ""
        a["held_by_gulfstream"] = 1 if any(r["held"] and r["src"] == "MASTER" for r in rs) else 0
        code0 = min(r["code"] for r in rs)
        a["code0"] = code0
        a["n_codes"] = len(set(r["code"] for r in rs))
        a["model"], a["cabin"], a["mfr"] = codes[code0]["model"], codes[code0]["cabin"], codes[code0]["mfr"]
        aws = [r["aw"] for r in rs if r["aw"]]
        a["first_airworthiness"] = min(aws) if aws else None
        yrs = [r["year"] for r in rs if r["year"]]
        a["year_mfr"] = min(yrs) if yrs else None
        if a["first_airworthiness"]:
            a["bound"] = a["first_airworthiness"] + dt.timedelta(days=365)
        elif a["year_mfr"]:
            a["bound"] = dt.date(a["year_mfr"] + 1, 12, 31)
        else:
            a["bound"] = None
        b = a["bound"]

        def earliest(vals):
            v = [x for x in vals if x is not None and (b is None or x <= b)]
            return min(v) if v else None
        a["e1"] = earliest([a["customer_cert"], a["export_cancel"]])
        a["e2"] = earliest([a["customer_cert"], a["gulfstream_cancel"]])
        a["e1_source"] = None
        if a["e1"] is not None:
            a["e1_source"] = "customer_cert" if a["customer_cert"] == a["e1"] else "export_cancel"
        a["names"] = sorted(set(r["name"] for r in rs))
        air[key] = a
    return codes, air, st


def load_windows(processed, extra=None):
    W = []
    with open(os.path.join(processed, "registry_quarterly.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            W.append((r["quarter"], dt.date.fromisoformat(r["window_start"]),
                      dt.date.fromisoformat(r["window_end"])))
    if extra:
        W.append(extra)
    return W


def count(air, defn, W, cut_days=0):
    """{quarter: {large, mid}} of airframes whose event date is after
    window_start, through window_end (minus cut_days)."""
    k = defn.lower()
    res = {q: {"large": 0, "mid": 0} for q, _, _ in W}
    for a in air.values():
        d = a[k]
        if d is None:
            continue
        for q, s, e in W:
            if s < d <= e - dt.timedelta(days=cut_days):
                res[q][a["cabin"]] += 1
                break
    return res


def to_N(counts_by_def):
    """Part A registry structure from {defn: {q: {large, mid}}}."""
    N = {}
    for d, cq in counts_by_def.items():
        for q, v in cq.items():
            N.setdefault(q, {})[d] = {"large": F(v["large"]), "mid": F(v["mid"]),
                                      "total": F(v["large"] + v["mid"])}
    return N


def main():
    snaps, back, lock, processed, predfile = sys.argv[1:6]
    Y, Nproc = A.load(processed)
    with open(predfile, "rb") as fh:
        pj = json.loads(fh.read().decode("utf-8"))
    W = load_windows(processed)
    q3 = (pj["quarter"], dt.date.fromisoformat(pj["window_start"]), dt.date.fromisoformat(pj["window_end"]))
    W3 = W + [q3]
    wq = [q for q, _, _ in W]
    lo_d, hi_d = W[0][1], W[-1][2]

    # ------------------------------------------------------------ item 13
    codes, air, st = build(os.path.join(snaps, back))
    head("13. Backtest snapshot %s: airframe table and counts" % back)
    for k in sorted(st):
        out("b13.parse.%s" % k, st[k])
    out("b13.parse.unparseable_nonblank_dates", dict(BAD_DATES) or "none")
    out("b13.airframes", len(air))
    out("b13.airframes.large", sum(1 for a in air.values() if a["cabin"] == "large"))
    out("b13.airframes.mid", sum(1 for a in air.values() if a["cabin"] == "mid"))
    out("b13.airframes.with_e1", sum(1 for a in air.values() if a["e1"]))
    out("b13.airframes.with_e2", sum(1 for a in air.values() if a["e2"]))
    out("b13.airframes.with_e1.large", sum(1 for a in air.values() if a["e1"] and a["cabin"] == "large"))
    out("b13.airframes.with_e1.mid", sum(1 for a in air.values() if a["e1"] and a["cabin"] == "mid"))
    out("b13.airframes.with_e1_in_2016Q1_2026Q2", sum(1 for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d))
    out("b13.airframes.with_e2_in_2016Q1_2026Q2", sum(1 for a in air.values() if a["e2"] and lo_d < a["e2"] <= hi_d))
    out("b13.airframes.e1_differs_from_e2", sum(1 for a in air.values() if a["e1"] != a["e2"]))
    out("b13.airframes.held_by_gulfstream", sum(a["held_by_gulfstream"] for a in air.values()))
    out("b13.airframes.held_by_gulfstream_with_neither_event",
        sum(1 for a in air.values() if a["held_by_gulfstream"] and not a["e1"] and not a["e2"]))
    out("b13.airframes.with_bound", sum(1 for a in air.values() if a["bound"]))
    out("b13.airframes.bound_from_year_mfr_only", sum(1 for a in air.values() if a["bound"] and not a["first_airworthiness"]))
    out("b13.airframes.no_bound", sum(1 for a in air.values() if not a["bound"]))
    out("b13.airframes.customer_cert_dropped_by_bound",
        sum(1 for a in air.values() if a["customer_cert"] and a["bound"] and a["customer_cert"] > a["bound"]))
    out("b13.airframes.more_than_one_code", sum(1 for a in air.values() if a["n_codes"] > 1))
    C = {d: count(air, d, W) for d in ("E1", "E2")}
    ndiff = 0
    for q in wq:
        for d in ("E1", "E2"):
            for c in CABINS:
                mine, theirs = C[d][q][c], int(Nproc[q][d][c])
                if mine != theirs:
                    ndiff += 1
                    out("b13.diff.%s.%s.%s" % (q, d, c), "mine=%d theirs=%d" % (mine, theirs))
    out("b13.cells_compared", len(wq) * 4)
    out("b13.cells_that_differ", ndiff)
    for q in wq:
        out("b13.count.%s" % q, "e1_large=%d e1_mid=%d e2_large=%d e2_mid=%d" % (
            C["E1"][q]["large"], C["E1"][q]["mid"], C["E2"][q]["large"], C["E2"][q]["mid"]))
    for d in ("E1", "E2"):
        out("b13.sum_2016Q1_2026Q2.%s" % d, "large=%d mid=%d" % (
            sum(C[d][q]["large"] for q in wq), sum(C[d][q]["mid"] for q in wq)))
    src = collections.Counter(a["e1_source"] for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d)
    out("b13.e1_in_window_by_source", dict(src))
    nb = [a for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d and not a["first_airworthiness"]]
    out("b13.e1_in_window_with_no_airworthiness_date", len(nb))
    nb2 = [a for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d and not a["bound"]]
    out("b13.e1_in_window_with_no_bound_at_all", len(nb2))

    # ------------------------------------------------------------ item 15
    head("15. Models in the backtest airframe table")
    inwin = lambda x: x is not None and lo_d < x <= hi_d
    by = collections.defaultdict(list)
    for a in air.values():
        by[(a["code0"], a["mfr"], a["model"], a["cabin"])].append(a)
    flagged = []
    for (code0, mfr, model, cabin), lst in sorted(by.items()):
        midname = bool(MID_TYPE_BY_NAME.search(model)) or mfr.startswith("IAI") or mfr.startswith("ISRAEL")
        tag = "LARGE_BY_RULE_BUT_MID_TYPE_BY_NAME" if (cabin == "large" and midname) else "-"
        n1 = sum(1 for a in lst if inwin(a["e1"]))
        n2 = sum(1 for a in lst if inwin(a["e2"]))
        out("b15.model.%s" % code0, "mfr=%s | model=%s | cabin_by_rule=%s | airframes=%d | e1_in_2016Q1_2026Q2=%d | e2_in_2016Q1_2026Q2=%d | %s" % (
            mfr, model, cabin, len(lst), n1, n2, tag))
        if tag != "-":
            flagged.append((code0, mfr, model, lst, n1, n2))
    out("b15.flagged_models", len(flagged))
    out("b15.flagged_airframes", sum(len(x[3]) for x in flagged))
    out("b15.flagged_airframes_with_e1_in_2016Q1_2026Q2", sum(x[4] for x in flagged))
    out("b15.flagged_airframes_with_e2_in_2016Q1_2026Q2", sum(x[5] for x in flagged))
    for code0, mfr, model, lst, n1, n2 in flagged:
        for a in lst:
            if inwin(a["e1"]) or inwin(a["e2"]):
                out("b15.flagged_event.%s.%s" % (code0, a["serial"]), "model=%s e1=%s e2=%s first_airworthiness=%s year_mfr=%s bound=%s" % (
                    model, a["e1"], a["e2"], a["first_airworthiness"], a["year_mfr"], a["bound"]))
    codes_unused = sorted(set(codes) - set(a["code0"] for a in air.values()))
    out("b15.in_scope_codes_that_are_no_airframes_first_code", ",".join(codes_unused) or "none")

    # diagnostics: the same serial under two three-character maker prefixes
    head("15x. Diagnostics outside the list (backtest snapshot)")
    bys = collections.defaultdict(list)
    for (pfx, serial), a in air.items():
        bys[serial].append(a)
    dup_same_type, dup_both_events = 0, 0
    for serial, lst in sorted(bys.items()):
        if len(lst) < 2:
            continue
        fam = lambda a: re.sub(r"[^0-9]", "", a["model"].split("(")[-1])[-3:]
        both = [a for a in lst if inwin(a["e1"])]
        fams = set(fam(a) for a in lst)
        if len(fams) < len(lst):
            dup_same_type += 1
            if len(both) >= 2:
                dup_both_events += 1
            out("b15x.serial_under_two_prefixes.%s" % serial, " ; ".join(
                "%s %s cabin=%s e1=%s e2=%s" % (a["mfr_code"], a["model"], a["cabin"], a["e1"], a["e2"]) for a in lst))
    out("b15x.serials_under_two_prefixes_with_same_type_digits", dup_same_type)
    out("b15x.of_which_both_airframes_have_e1_in_2016Q1_2026Q2", dup_both_events)
    out("b15x.serials_under_more_than_one_prefix_any_type", sum(1 for l in bys.values() if len(l) > 1))
    anyboth = sorted(s for s, l in bys.items() if sum(1 for a in l if inwin(a["e1"])) >= 2)
    out("b15x.serials_with_e1_in_window_under_two_prefixes_any_type", len(anyboth))
    for s in anyboth:
        out("b15x.two_events_same_serial.%s" % s, " ; ".join(
            "%s %s e1=%s" % (a["mfr_code"], a["model"], a["e1"]) for a in bys[s] if inwin(a["e1"])))
    names = collections.Counter()
    for a in air.values():
        for n in a["names"]:
            if "GULFSTREAM" in n and not n.startswith("GULFSTREAM AEROSPACE"):
                names[n] += 1
    out("b15x.owner_names_containing_GULFSTREAM_not_starting_GULFSTREAM_AEROSPACE", len(names))
    for n, c in names.most_common(12):
        out("b15x.owner_name.%s" % n.replace(" ", "_"), c)
    gh = collections.Counter()
    for a in air.values():
        for n in a["names"]:
            if n.startswith("GULFSTREAM AEROSPACE"):
                gh[n] += 1
    for n, c in gh.most_common(8):
        out("b15x.gulfstream_held_name.%s" % n.replace(" ", "_"), c)
    blank = sum(1 for a in air.values() if inwin(a["e1"]) and "" in a["names"])
    out("b15x.e1_in_window_airframes_with_a_blank_name_record", blank)
    for yr in range(2016, 2027):
        ev = [a for a in air.values() if inwin(a["e1"]) and a["e1"].year == yr]
        cs = sum(1 for a in ev if a["e1_source"] == "customer_cert")
        out("b15x.e1_by_event_calendar_year.%d" % yr, "events=%d from_customer_cert=%d from_export_cancel=%d" % (len(ev), cs, len(ev) - cs))

    # ------------------------------------------------------------ item 16 (extra)
    head("16. Extra, not in the list: truncation table from my backtest airframe table (E1)")
    hq = A.qrange(*A.HOLDOUT)
    Nb = to_N(C)
    for cut in (0, 30, 60, 90):
        Ct = count(air, "E1", W, cut)
        est = {}
        for q in hq:
            est[q] = A.m_ratio(Y, Nb, q, "E1", n_now={c: F(Ct[q][c]) for c in CABINS})
        out("b16.truncation_mae.%d" % cut, f6(A.mae(Y, est, hq)))
        out("b16.truncation_events_kept_holdout.%d" % cut, sum(Ct[q]["large"] + Ct[q]["mid"] for q in hq))
    R = {q: A.m_ratio(Y, Nb, q, "E1") for q in A.qrange("2017Q1", "2026Q2")}
    out("b16.holdout_mae_ratio_from_my_counts", f6(A.mae(Y, R, hq)))
    out("b16.design_mae_ratio_E1_from_my_counts", f6(A.mae(Y, R, A.qrange(*A.DESIGN))))
    R2 = {q: A.m_ratio(Y, Nb, q, "E2") for q in A.qrange("2017Q1", "2019Q4")}
    out("b16.design_mae_ratio_E2_from_my_counts", f6(A.mae(Y, R2, A.qrange(*A.DESIGN))))

    # ------------------------------------------------------------ item 14
    BAD_DATES.clear()
    codes2, air2, st2 = build(os.path.join(snaps, lock))
    head("14. Lock snapshot %s: rebuild of the %s prediction" % (lock, pj["quarter"]))
    for k in sorted(st2):
        out("b14.parse.%s" % k, st2[k])
    out("b14.parse.unparseable_nonblank_dates", dict(BAD_DATES) or "none")
    out("b14.airframes", len(air2))
    out("b14.airframes.with_e1", sum(1 for a in air2.values() if a["e1"]))
    out("b14.new_in_scope_codes_vs_backtest", ",".join(
        "%s(%s|%s)" % (c, codes2[c]["mfr"], codes2[c]["model"]) for c in sorted(set(codes2) - set(codes))) or "none")
    C2 = {d: count(air2, d, W3) for d in ("E1", "E2")}
    C1 = {d: count(air, d, W3) for d in ("E1", "E2")}
    Q = pj["quarter"]
    dfn = pj["definition"]
    lags = [A.lag(Q, k) for k in (1, 2, 3, 4)]
    ev = C2[dfn][Q]
    trn = {c: sum(C2[dfn][l][c] for l in lags) for c in CABINS}
    trr = {c: int(sum(Y[l][c] for l in lags)) for c in CABINS}
    est = {c: F(ev[c]) * trr[c] / trn[c] for c in CABINS}
    tot = est["large"] + est["mid"]

    def cmp(key, mine, theirs, isfloat=False):
        if isfloat:
            same = abs(float(mine) - float(theirs)) < 5e-10
            out(key, "mine=%s theirs=%s %s (abs difference %.3e)" % (
                f6(mine), f6(theirs), "match" if same else "DIFFERENT", abs(float(mine) - float(theirs))))
        else:
            out(key, "mine=%s theirs=%s %s" % (mine, theirs, "match" if mine == theirs else "DIFFERENT"))
    cmp("b14.window_start", str(q3[1]), pj["window_start"])
    cmp("b14.window_end", str(q3[2]), pj["window_end"])
    out("b14.window_start_equals_2026Q2_fiscal_end", "true" if str(q3[1]) == Y[lags[0]]["fiscal_end"] else "false")
    cmp("b14.events.large", ev["large"], pj["events"]["large"])
    cmp("b14.events.mid", ev["mid"], pj["events"]["mid"])
    cmp("b14.trailing.registry.large", trn["large"], pj["trailing"]["registry"]["large"])
    cmp("b14.trailing.registry.mid", trn["mid"], pj["trailing"]["registry"]["mid"])
    cmp("b14.trailing.reported.large", trr["large"], pj["trailing"]["reported"]["large"])
    cmp("b14.trailing.reported.mid", trr["mid"], pj["trailing"]["reported"]["mid"])
    cmp("b14.nowcast.large", est["large"], pj["nowcast"]["large"], True)
    cmp("b14.nowcast.mid", est["mid"], pj["nowcast"]["mid"], True)
    cmp("b14.nowcast.total", tot, pj["nowcast"]["total"], True)
    out("b14.events.E2_for_reference", "large=%d mid=%d" % (C2["E2"][Q]["large"], C2["E2"][Q]["mid"]))
    out("b14.events_from_backtest_snapshot_%s_for_reference" % back, "large=%d mid=%d" % (C1[dfn][Q]["large"], C1[dfn][Q]["mid"]))
    # band: every signed error 2017Q1..2026Q2, three sources of the past counts
    bq = A.qrange("2017Q1", "2026Q2")
    for tag, Nsrc in (("lock_snapshot_counts", to_N({d: {q: C2[d][q] for q in wq} for d in C2})),
                      ("backtest_snapshot_counts_my_rebuild", to_N({d: {q: C1[d][q] for q in wq} for d in C1})),
                      ("processed_file_counts", Nproc)):
        errs = []
        for q in bq:
            r = A.m_ratio(Y, Nsrc, q, dfn)
            errs.append(r["total"] - Y[q]["total"])
        lo, hi, p10, p90, pos10, pos90, n = A.band_for(errs, tot)
        out("b14.band.%s" % tag, "n=%d p10_position=%d p90_position=%d p10=%s p90=%s low=%s high=%s" % (
            n, pos10, pos90, f6(p10), f6(p90), f6(lo), f6(hi)))
        cmp("b14.band.%s.low" % tag, lo, pj["band"][0], True)
        cmp("b14.band.%s.high" % tag, hi, pj["band"][1], True)
    # drift of past-quarter counts between the two snapshots
    nd = 0
    for q in wq:
        for d in ("E1", "E2"):
            for c in CABINS:
                if C1[d][q][c] != C2[d][q][c]:
                    nd += 1
                    out("b14.count_changed_between_snapshots.%s.%s.%s" % (q, d, c),
                        "%s=%d %s=%d" % (back, C1[d][q][c], lock, C2[d][q][c]))
    out("b14.past_quarter_cells_changed_between_snapshots", nd)
    # the quarter's own events by posting lag, lock snapshot
    evs = sorted((a["e1"], a["cabin"], a["mfr_code"], a["serial"], a["model"], a["e1_source"])
                 for a in air2.values() if a["e1"] and q3[1] < a["e1"] <= q3[2])
    out("b14.events.first_date", evs[0][0] if evs else "none")
    out("b14.events.last_date", evs[-1][0] if evs else "none")
    bym = collections.Counter((e[4], e[1]) for e in evs)
    for (model, cabin), n in sorted(bym.items()):
        out("b14.events.by_model.%s" % model.replace(" ", "_"), "%d (%s)" % (n, cabin))
    out("b14.events.by_source", dict(collections.Counter(e[5] for e in evs)))
    pipeline = collections.Counter(a["model"] for a in air2.values()
                                   if a["held_by_gulfstream"] and not a["e1"] and not a["e2"])
    out("b14.pipeline_held_by_gulfstream_with_neither_event", sum(pipeline.values()))
    for m, n in sorted(pipeline.items()):
        out("b14.pipeline.%s" % m.replace(" ", "_"), n)


if __name__ == "__main__":
    main()
