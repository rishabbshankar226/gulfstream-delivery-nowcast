"""The preregistered as-of study (Phase 9): score ratio on Wayback captures taken 20 to 30 days after fiscal ends.

Usage: .venv/bin/python tools/asof.py   (downloads captures into data/raw/wayback/, out of git)
Writes results/exploratory/asof.csv and results/exploratory/asof.md."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gdn import events, faa, model  # noqa: E402
from gdn.files import read_csv, read_json, write_csv, write_text  # noqa: E402
from gdn.fiscal import Calendar, qrange, shift  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
COLS = ["quarter", "fiscal_end", "capture", "days_after_end", "events_large", "events_mid", "trailing_registry_large",
        "trailing_registry_mid", "estimate", "reported", "ae", "backtest_estimate", "backtest_ae", "band_low",
        "band_high", "inside_band", "note"]


def captures():
    p = ROOT / "data/raw/wayback/cdx.json"
    if not p.exists():
        url = "https://web.archive.org/cdx/search/cdx?url=registry.faa.gov/database/ReleasableAircraft.zip&output=json"
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sS", "--max-time", "120", "-A", UA, "-o", str(p), url], check=True)
    d = json.loads(p.read_text())
    return [dict(zip(d[0], r)) for r in d[1:] if r[4] == "200"]


def listed(xs):
    return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else "".join(xs)


def main():
    cal = Calendar.load(ROOT)
    Y = model.load_reported(ROOT)
    chosen = read_json(ROOT / "results/metrics.json")["definition"]
    hold = {r["quarter"]: float(r["total"]) for r in read_csv(ROOT / "results/holdout.csv")
            if r["model"] == "ratio"}
    hold.update({r["quarter"]: float(r["total"]) for r in read_csv(ROOT / "results/design.csv")
                 if r["model"] == "ratio" and r["definition"] == chosen})
    bands = {b["quarter"]: b for b in read_json(ROOT / "results/metrics.json")["holdout"]["band"]["by_quarter"]}
    caps = captures()
    best = {}
    for q in qrange("2016Q1", "2026Q2"):
        end = dt.date.fromisoformat(cal.end(q))
        for c in caps:
            lag = (dt.datetime.strptime(c["timestamp"], "%Y%m%d%H%M%S").date() - end).days
            if 20 <= lag <= 30 and (q not in best or abs(lag - 25) < abs(best[q][1] - 25)):
                best[q] = (c["timestamp"], lag)
    rows = []
    for q, (ts, lag) in sorted(best.items()):
        lags = [shift(q, -k) for k in range(1, 5)]
        base = {"quarter": q, "fiscal_end": cal.end(q), "capture": ts, "days_after_end": lag}
        if not all(x in Y for x in lags):
            rows.append(dict(base, note="not scored: a lag quarter precedes the reported series"))
            continue
        z = ROOT / "data/raw/wayback" / f"ReleasableAircraft-{ts}.zip"
        if not faa.is_zip(z):
            url = f"https://web.archive.org/web/{ts}id_/http://registry.faa.gov/database/ReleasableAircraft.zip"
            subprocess.run(["curl", "-sSL", "--max-time", "900", "--retry", "2", "-A", UA, "-o", str(z), url])
        if not faa.is_zip(z):
            rows.append(dict(base, note="capture did not download"))
            continue
        try:
            sub = faa.subset(faa.zip_texts(z))
        except (faa.MissingColumn, KeyError) as e:
            rows.append(dict(base, note=f"capture lacks a field: {e}"))
            continue
        air = events.airframes(sub)
        ev = {c: events.count(air, chosen, c, *cal.window(q)) for c in ("large", "mid")}
        nl = {c: [events.count(air, chosen, c, *cal.window(x)) for x in lags] for c in ("large", "mid")}
        est = sum(model.ratio(ev[c], nl[c], [Y[x][c] for x in lags]) for c in ("large", "mid"))
        rep = Y[q]["total"]
        band = {}
        if q in bands and q in hold:
            # The same past-miss band widths as the backtest, centred on the as-of estimate.
            lo, hi = est - (hold[q] - bands[q]["low"]), est + (bands[q]["high"] - hold[q])
            band = {"band_low": lo, "band_high": hi, "inside_band": lo <= rep <= hi}
        rows.append(dict(base, **band, events_large=ev["large"], events_mid=ev["mid"], trailing_registry_large=sum(nl["large"]),
                         trailing_registry_mid=sum(nl["mid"]), estimate=est, reported=rep, ae=abs(est - rep),
                         backtest_estimate=hold.get(q), backtest_ae=abs(hold[q] - rep) if q in hold else None,
                         note=""))
        print(q, ts, f"{est:.1f} against {rep}; the 2026-10-19 copy gave {hold.get(q)}")
    write_csv(ROOT / "results/exploratory/asof.csv", COLS, rows)
    scored = [r for r in rows if r.get("estimate") is not None]
    lower = [r["quarter"] for r in scored if r["backtest_estimate"] is not None and r["estimate"] < r["backtest_estimate"]]
    higher = [r for r in scored if r["backtest_estimate"] is not None and r["estimate"] >= r["backtest_estimate"]]
    both_low = all(r["estimate"] < r["reported"] and r["backtest_estimate"] < r["reported"] for r in higher)
    higher = [r["quarter"] for r in higher]
    line = (f"Wayback captures exist: {len(caps)} successful captures of ReleasableAircraft.zip; {len(best)} quarters have "
            f"one taken 20 to 30 days after the fiscal end, and {len(scored)} of them can be scored.")
    text = ["# As-of study (preregistered secondary analysis)", "", line, ""]
    if scored:
        text += ["| Quarter | Capture | Days after end | As-of estimate | Reported | As-of miss | Miss on the 2026-10-19 copy | As-of band | Inside |",
                 "|---|---|---|---|---|---|---|---|---|"]
        for r in scored:
            band = (f"{r['band_low']:.1f} to {r['band_high']:.1f}", "yes" if r["inside_band"] else "no") \
                if r.get("band_low") is not None else ("n/a (design quarter)", "")
            text.append(f"| {r['quarter']} | {r['capture'][:8]} | {r['days_after_end']} | {r['estimate']:.1f} | "
                        f"{r['reported']} | {r['ae']:.1f} | {r['backtest_ae']:.1f} | {band[0]} | {band[1]} |")
        text += ["", "Each as-of estimate reads both the quarter's own registry events and its four lag quarters from "
                     "the same archived copy, as a live estimate does. The truncation table in the README cuts only the "
                     "quarter's own events and keeps the lags whole. The archived copies held more lag-quarter events than the "
                     "2026-10-19 copy, since a later file loses a first owner's date when a jet is resold or "
                     f"re-registered. In {listed(lower) or 'none'} the as-of estimate came out lower than the "
                     "2026-10-19 copy's and, given the ratio's upward bias, closer"
                     + (f"; in {listed(higher)} it came out higher" + (", and both copies missed low" if both_low
                        else "") if higher else "") + ". Four quarters are too "
                     "few to conclude anything; the locked quarters remain the real test."]
    write_text(ROOT / "results/exploratory/asof.md", "\n".join(text) + "\n")
    print(line)


if __name__ == "__main__":
    main()
