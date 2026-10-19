"""Airframes, their delivery events E1 and E2, quarterly counts and the pipeline (§3.3)."""
import datetime as dt
import gzip
import re

from .faa import parse_date, read_table, scope
from .files import csv_text

SERIAL_COLS = ["mfr_code", "serial", "model", "cabin", "held_by_gulfstream", "first_airworthiness", "year_mfr",
               "bound", "customer_cert", "gulfstream_cancel", "export_cancel", "export_country", "e1", "e2"]
REG_COLS = ["quarter", "window_start", "window_end", "e1_large", "e1_mid", "e2_large", "e2_mid"]


def gulfstream_held(name):
    return name.strip().upper().startswith("GULFSTREAM AEROSPACE")


def _min(xs):
    xs = [x for x in xs if x]
    return min(xs) if xs else None


def airframes(sub):
    """One row per airframe: maker-code prefix plus upper-cased serial, sorted."""
    codes = scope(read_table(sub["ACFTREF"], "ACFTREF"))
    recs = {}
    for kind in ("MASTER", "DEREG"):
        for r in read_table(sub[kind], kind):
            code = r["MFRMDLCODE"]
            if code not in codes or not r["SERIALNUMBER"]:
                continue
            recs.setdefault((code[:3], r["SERIALNUMBER"].upper()), []).append((kind, code, r))
    out = []
    for key in sorted(recs):
        rs = recs[key]
        code = min(c for _, c, _ in rs)
        cust = _min(parse_date(r["CERTISSUEDATE"]) for _, _, r in rs if not gulfstream_held(r["NAME"]))
        gcan = _min(parse_date(r["CANCELDATE"]) for k, _, r in rs if k == "DEREG" and gulfstream_held(r["NAME"]))
        exports = sorted((parse_date(r["CANCELDATE"]), r["EXPCOUNTRY"]) for k, _, r in rs
                         if k == "DEREG" and gulfstream_held(r["NAME"]) and r["EXPCOUNTRY"]
                         and parse_date(r["CANCELDATE"]))
        exp_date, exp_country = exports[0] if exports else (None, "")
        held = any(k == "MASTER" and gulfstream_held(r["NAME"]) for k, _, r in rs)
        air = _min(parse_date(r["AIRWORTHDATE"]) for _, _, r in rs)
        years = [int(r["YEARMFR"]) for _, _, r in rs if re.fullmatch(r"(19|20)\d\d", r["YEARMFR"])]
        year = min(years) if years else None
        if air:
            bound = (dt.date.fromisoformat(air) + dt.timedelta(days=365)).isoformat()
        elif year:
            bound = f"{year + 1}-12-31"
        else:
            bound = None

        def ok(x):
            return x and (bound is None or x <= bound)

        e1 = _min(x for x in (cust, exp_date) if ok(x))
        e2 = _min(x for x in (cust, gcan) if ok(x))
        out.append({"mfr_code": key[0], "serial": key[1], "model": codes[code]["model"],
                    "cabin": codes[code]["cabin"], "held_by_gulfstream": int(held), "first_airworthiness": air,
                    "year_mfr": str(year) if year else None, "bound": bound, "customer_cert": cust,
                    "gulfstream_cancel": gcan, "export_cancel": exp_date, "export_country": exp_country,
                    "e1": e1, "e2": e2})
    return out


def serials_text(rows):
    return csv_text(SERIAL_COLS, rows)


def serials_gz(rows):
    return gzip.compress(serials_text(rows).encode("utf-8"), mtime=0)


def read_serials_rows(dict_rows):
    """Rows read back from a serials CSV, blanks as None."""
    out = []
    for r in dict_rows:
        r = {k: (v if v != "" else None) for k, v in r.items()}
        r["held_by_gulfstream"] = int(r["held_by_gulfstream"] or 0)
        r["export_country"] = r["export_country"] or ""
        out.append(r)
    return out


def count(rows, definition, cabin, lo, hi, cutoff=None):
    """Airframes of one cabin whose event falls after lo, through hi (and on or before cutoff)."""
    key = definition.lower()
    top = hi if cutoff is None else min(hi, cutoff)
    return sum(1 for r in rows if r["cabin"] == cabin and r[key] and lo < r[key] <= top)


def quarterly(rows, quarters, cal):
    out = []
    for q in quarters:
        lo, hi = cal.window(q)
        rec = {"quarter": q, "window_start": lo, "window_end": hi}
        for e in ("E1", "E2"):
            for c in ("large", "mid"):
                rec[f"{e.lower()}_{c}"] = count(rows, e, c, lo, hi)
        out.append(rec)
    return out


def pipeline(rows):
    """Airframes held by Gulfstream with neither event, by model."""
    out = {}
    for r in rows:
        if r["held_by_gulfstream"] and not r["e1"] and not r["e2"]:
            out[r["model"]] = out.get(r["model"], 0) + 1
    return dict(sorted(out.items()))
