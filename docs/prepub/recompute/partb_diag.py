#!/usr/bin/env python3
"""Diagnostics on my own Part B airframe tables (not in the brief's list).

Usage: python3 partb_diag.py <snapshots_dir> <backtest_date> <lock_date>
                             <processed_folder> <prediction_json>
"""
import collections
import datetime as dt
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parta as A
import partb as B

out, head = B.out, B.head


def main():
    snaps, back, lock, processed, predfile = sys.argv[1:6]
    Y, Nproc = A.load(processed)
    with open(predfile, "rb") as fh:
        pj = json.loads(fh.read().decode("utf-8"))
    W = B.load_windows(processed)
    q3 = (pj["quarter"], dt.date.fromisoformat(pj["window_start"]), dt.date.fromisoformat(pj["window_end"]))
    lo_d, hi_d = W[0][1], W[-1][2]
    codes, air, st = B.build(os.path.join(snaps, back))
    codes2, air2, st2 = B.build(os.path.join(snaps, lock))

    def quarter_of(d, WW):
        for q, s, e in WW:
            if s < d <= e:
                return q
        return None

    head("17. Extra, not in the list: E1 events of airframes with no bound (no airworthiness date and no year), backtest snapshot")
    nb = [a for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d and a["bound"] is None]
    out("b17.e1_events_2016Q1_2026Q2", sum(1 for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d))
    out("b17.e1_events_no_bound", len(nb))
    out("b17.e1_events_no_bound.by_source", dict(collections.Counter(a["e1_source"] for a in nb)))
    out("b17.e1_events_no_bound.by_cabin", dict(collections.Counter(a["cabin"] for a in nb)))
    bm = collections.Counter(a["model"] for a in nb)
    for m, n in sorted(bm.items(), key=lambda kv: (-kv[1], kv[0])):
        out("b17.e1_events_no_bound.model.%s" % m.replace(" ", "_"), n)
    byq = collections.Counter(quarter_of(a["e1"], W) for a in nb)
    for yr in range(2016, 2027):
        qs = [q for q, _, _ in W if q[:4] == str(yr)]
        out("b17.e1_events_no_bound.year.%d" % yr, "%d (%s)" % (
            sum(byq[q] for q in qs), " ".join("%s=%d" % (q, byq[q]) for q in qs)))
    # every model: events in window, by whether a bound exists and by source
    for (code0, model) in sorted(set((a["code0"], a["model"]) for a in air.values())):
        ev = [a for a in air.values() if a["code0"] == code0 and a["e1"] and lo_d < a["e1"] <= hi_d]
        if not ev:
            continue
        yrs = sorted(a["e1"].year for a in ev)
        out("b17.model_events.%s" % code0, "model=%s | e1_events=%d | no_bound=%d | from_export_cancel=%d | first_event_year=%d | last_event_year=%d" % (
            model, len(ev), sum(1 for a in ev if a["bound"] is None),
            sum(1 for a in ev if a["e1_source"] == "export_cancel"), yrs[0], yrs[-1]))

    head("18. Extra, not in the list: every E1 event of %s in the lock snapshot %s" % (pj["quarter"], lock))
    evs = sorted((a for a in air2.values() if a["e1"] and q3[1] < a["e1"] <= q3[2]),
                 key=lambda a: (a["e1"], a["mfr_code"], a["serial"]))
    for i, a in enumerate(evs, 1):
        out("b18.event.%02d" % i, "e1=%s | cabin=%s | model=%s | key=%s-%s | source=%s | first_airworthiness=%s | year_mfr=%s | bound=%s | records=%d" % (
            a["e1"], a["cabin"], a["model"], a["mfr_code"], a["serial"], a["e1_source"],
            a["first_airworthiness"], a["year_mfr"], a["bound"], a["n_records"]))
    out("b18.events", len(evs))
    out("b18.events_no_bound", sum(1 for a in evs if a["bound"] is None))
    out("b18.events_no_bound.large", sum(1 for a in evs if a["bound"] is None and a["cabin"] == "large"))
    out("b18.events_no_bound.mid", sum(1 for a in evs if a["bound"] is None and a["cabin"] == "mid"))
    out("b18.events_with_bound.large", sum(1 for a in evs if a["bound"] is not None and a["cabin"] == "large"))
    out("b18.events_with_bound.mid", sum(1 for a in evs if a["bound"] is not None and a["cabin"] == "mid"))

    head("19. Extra, not in the list: the same serial counted under two maker prefixes (backtest snapshot)")
    for pfx, serial in (("450", "2009"), ("398", "2009"), ("450", "322"), ("398", "322")):
        a = air.get((pfx, serial))
        if a is None:
            continue
        out("b19.airframe.%s-%s" % (pfx, serial), "model=%s | cabin=%s | records=%d | first_airworthiness=%s | year_mfr=%s | bound=%s | customer_cert=%s | export_cancel=%s | e1=%s | e1_quarter=%s" % (
            a["model"], a["cabin"], a["n_records"], a["first_airworthiness"], a["year_mfr"], a["bound"],
            a["customer_cert"], a["export_cancel"], a["e1"], quarter_of(a["e1"], W) if a["e1"] else None))

    head("21. Extra, not in the list: E1 events by the airframe's age at the event (event year minus year_mfr), backtest snapshot")
    def age_class(a):
        if a["year_mfr"] is None:
            return "year_unknown"
        return "old_3plus_years" if a["e1"].year - a["year_mfr"] >= 3 else "new_0_to_2_years"
    ev = [a for a in air.values() if a["e1"] and lo_d < a["e1"] <= hi_d]
    out("b21.e1_events", len(ev))
    for cls in ("new_0_to_2_years", "old_3plus_years", "year_unknown"):
        out("b21.e1_events.%s" % cls, "%d (large=%d mid=%d)" % (
            sum(1 for a in ev if age_class(a) == cls),
            sum(1 for a in ev if age_class(a) == cls and a["cabin"] == "large"),
            sum(1 for a in ev if age_class(a) == cls and a["cabin"] == "mid")))
    out("b21.e1_events.old_3plus_years_share_pct", A.f6(100.0 * sum(1 for a in ev if age_class(a) == "old_3plus_years") / len(ev)))
    out("b21.e1_events.year_unknown_share_pct", A.f6(100.0 * sum(1 for a in ev if age_class(a) == "year_unknown") / len(ev)))
    out("b21.e1_events.new_0_to_2_years_share_pct", A.f6(100.0 * sum(1 for a in ev if age_class(a) == "new_0_to_2_years") / len(ev)))
    for yr in range(2016, 2027):
        qs = set(q for q, _, _ in W if q[:4] == str(yr))
        evy = [a for a in ev if quarter_of(a["e1"], W) in qs]
        rep = sum(int(Y[q]["total"]) for q in qs)
        n_new = sum(1 for a in evy if age_class(a) == "new_0_to_2_years")
        n_old = sum(1 for a in evy if age_class(a) == "old_3plus_years")
        n_unk = sum(1 for a in evy if age_class(a) == "year_unknown")
        out("b21.fiscal_year.%d" % yr, "events=%d new_0_to_2_years=%d old_3plus_years=%d year_unknown=%d gd_reported=%d" % (
            len(evy), n_new, n_old, n_unk, rep))
    oldm = collections.Counter(a["model"] for a in ev if age_class(a) == "old_3plus_years")
    for m, n in sorted(oldm.items(), key=lambda kv: (-kv[1], kv[0])):
        out("b21.old_3plus_years.model.%s" % m.replace(" ", "_"), n)
    evl = [a for a in air2.values() if a["e1"] and q3[1] < a["e1"] <= q3[2]]
    for cls in ("new_0_to_2_years", "old_3plus_years", "year_unknown"):
        out("b21.lock_quarter_%s.%s" % (pj["quarter"], cls), "%d (large=%d mid=%d)" % (
            sum(1 for a in evl if age_class(a) == cls),
            sum(1 for a in evl if age_class(a) == cls and a["cabin"] == "large"),
            sum(1 for a in evl if age_class(a) == cls and a["cabin"] == "mid")))
    for a in sorted(evl, key=lambda a: a["e1"]):
        if age_class(a) == "old_3plus_years":
            out("b21.lock_quarter_old.%s-%s" % (a["mfr_code"], a["serial"]), "model=%s year_mfr=%s first_airworthiness=%s e1=%s cabin=%s" % (
                a["model"], a["year_mfr"], a["first_airworthiness"], a["e1"], a["cabin"]))

    head("22. Extra to item 15: records under codes whose model name is a mid-cabin type but whose maker is not IAI/ISRAEL")
    import gzip, csv
    for code in ("3980202", "3980211", "3980213", "3980304", "3980401", "3980403", "3980404"):
        if code not in codes:
            continue
        hit = [a for a in air.values() if a["code0"] == code]
        out("b22.code.%s" % code, "mfr=%s | model=%s | cabin_by_rule=%s | airframes_with_this_first_code=%d" % (
            codes[code]["mfr"], codes[code]["model"], codes[code]["cabin"], len(hit)))
    for fn in ("MASTER", "DEREG"):
        _, rows, _ = B.read_table(os.path.join(snaps, back, fn + ".txt.gz"))
        cnt = collections.Counter(r["MFRMDLCODE"] for r in rows)
        out("b22.records_in_%s" % fn, " ".join("%s=%d" % (c, cnt.get(c, 0)) for c in (
            "3980202", "3980211", "3980213", "3980304", "3980401", "3980403", "3980404")))

    head("23. README reading of the bound (one calendar year) against the preregistration's (365 days), backtest snapshot")
    def alt_bound(a):
        fa = a["first_airworthiness"]
        if fa is not None:
            try:
                return fa.replace(year=fa.year + 1)
            except ValueError:
                return dt.date(fa.year + 1, 3, 1)
        return a["bound"]
    changed, cells = 0, collections.Counter()
    for a in air.values():
        b = alt_bound(a)
        for dn, ins in (("E1", (a["customer_cert"], a["export_cancel"])), ("E2", (a["customer_cert"], a["gulfstream_cancel"]))):
            v = [x for x in ins if x is not None and (b is None or x <= b)]
            alt = min(v) if v else None
            if alt != a[dn.lower()]:
                changed += 1
                for x in (alt, a[dn.lower()]):
                    if x is not None and quarter_of(x, W):
                        cells[(quarter_of(x, W), dn, a["cabin"])] += 1
                out("b23.changed.%s-%s.%s" % (a["mfr_code"], a["serial"], dn), "365_days=%s calendar_year=%s first_airworthiness=%s" % (
                    a[dn.lower()], alt, a["first_airworthiness"]))
    out("b23.airframe_definition_pairs_that_change", changed)
    out("b23.quarter_cells_2016Q1_2026Q2_touched", len(cells))
    for k in sorted(cells):
        out("b23.cell_touched.%s.%s.%s" % k, cells[k])
    # effect on the figures: rebuild the counts under the calendar-year bound
    from fractions import Fraction as F
    Nalt = {}
    for q, s, e in W:
        Nalt[q] = {"E1": {"large": F(0), "mid": F(0)}, "E2": {"large": F(0), "mid": F(0)}}
    for a in air.values():
        b = alt_bound(a)
        for dn, ins in (("E1", (a["customer_cert"], a["export_cancel"])), ("E2", (a["customer_cert"], a["gulfstream_cancel"]))):
            v = [x for x in ins if x is not None and (b is None or x <= b)]
            if v and quarter_of(min(v), W):
                Nalt[quarter_of(min(v), W)][dn][a["cabin"]] += 1
    dq, hq = A.qrange(*A.DESIGN), A.qrange(*A.HOLDOUT)
    for dn in ("E1", "E2"):
        R = {q: A.m_ratio(Y, Nalt, q, dn) for q in dq}
        out("b23.design_mae_ratio.%s.calendar_year_bound" % dn, A.f6(A.mae(Y, R, dq)))
        R0 = {q: A.m_ratio(Y, Nproc, q, dn) for q in dq}
        out("b23.design_mae_ratio.%s.365_day_bound" % dn, A.f6(A.mae(Y, R0, dq)))
    for tag, Nsrc in (("calendar_year_bound", Nalt), ("365_day_bound", Nproc)):
        R = {q: A.m_ratio(Y, Nsrc, q, "E1") for q in dq + hq}
        err = {q: R[q]["total"] - Y[q]["total"] for q in dq + hq}
        hits = 0
        for q in hq:
            prior = [err[p] for p in dq + hq if A.qidx(p) < A.qidx(q)]
            lo, hi = A.band_for(prior, R[q]["total"])[:2]
            hits += 1 if lo <= Y[q]["total"] <= hi else 0
        out("b23.holdout_mae_ratio_E1.%s" % tag, A.f6(A.mae(Y, R, hq)))
        out("b23.band_hits.%s" % tag, hits)

    head("20. Extra, not in the list: airframes whose E1 changed between the two snapshots")
    # airframes whose E1 changed or vanished between the snapshots
    for key in sorted(set(air) | set(air2)):
        a, b = air.get(key), air2.get(key)
        e_a = a["e1"] if a else None
        e_b = b["e1"] if b else None
        if e_a != e_b:
            ref = a or b
            in_a = e_a is not None and lo_d < e_a <= q3[2]
            in_b = e_b is not None and lo_d < e_b <= q3[2]
            if in_a or in_b:
                out("b20.e1_changed.%s-%s" % key, "model=%s | %s: e1=%s customer_cert=%s | %s: e1=%s customer_cert=%s bound=%s" % (
                    ref["model"], back, e_a, a["customer_cert"] if a else None,
                    lock, e_b, b["customer_cert"] if b else None, b["bound"] if b else None))


if __name__ == "__main__":
    main()
