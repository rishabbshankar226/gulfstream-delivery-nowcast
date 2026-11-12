"""report/note.html (§3.9), printed to output/GD_research_note.pdf with headless Chrome and copied to site/.

Prose comes from two places only: templates over the results files, and report/claims.json entries,
each cited as <sup data-claim="id">."""
import html
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import claims as claims_mod
from . import live, model
from .estimates import DEFENSE, LABEL, SEGMENTS, basis_path
from .report import comparators, lock_old_events, lock_words, readings_footnote
from .fiscal import Calendar, qrange, shift
from .files import read_csv, read_json, sha256, write_text

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TITLE = "General Dynamics (GD): Gulfstream delivery tracker"
DISCLAIMER = ("Student research project. Not investment advice. No rating or price target. Not affiliated with General "
              "Dynamics or Gulfstream.")
FRAMING = ("The backtest reads a registry copy from {snap}, which had months or years to fill in. It shows how well "
           "the registry tracks Gulfstream deliveries after the fact. Only the locked quarters test whether it "
           "counts them in time.")
NAMES = {"ratio": "Registry estimate (ratio)", "raw": "Raw registry count", "guidance": "GD guidance pace",
         "seasonal": "Same quarter last year", "last": "Last quarter"}
BASE_NAMES = {"guidance": "GD's guidance pace", "seasonal": "the same quarter last year", "last": "last quarter"}
STUDY_URL = "https://rishabbshankar226.github.io/Defense-Backlog-forecast/"
PRODUCT_IDS = ["pc-g500-g600-entry-into-service", "pc-g700-first-deliveries", "pc-g800-certification",
               "pc-g800-first-deliveries", "pc-g650-end-of-production", "pc-g280-mid-cabin", "pc-g280-iai",
               "pc-g300-replaces-g280", "pc-g280-final-delivery", "pc-g400-timing-update"]
REPO_URL = "https://github.com/rishabbshankar226/gulfstream-delivery-nowcast"


def edgar(accn):
    """An accession as its EDGAR folder URL."""
    return f"https://sec.gov/Archives/edgar/data/40533/{accn.replace('-', '')}"


def esc(s):
    return html.escape(str(s), quote=False)


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def bn(usd):
    return f"${usd / 1e9:.1f}B"


def mn(usd):
    return f"{'-' if usd < 0 else ''}${abs(usd) / 1e6:,.0f}M"


def cap(s):
    return s[:1].upper() + s[1:]


def pct(x, d=1):
    return f"{x:.{d}f}%"


def disclosure(root):
    p = Path.home() / ".gdn_disclosure"
    if p.exists() and p.read_text().strip():
        return p.read_text().strip()
    old = Path(root) / "report/note.html"
    if old.exists():
        m = re.search(r'<p id="disclosure">(.*?)</p>', old.read_text(), re.S)
        if m:
            return html.unescape(m.group(1)).strip()
    raise SystemExit("No ~/.gdn_disclosure and no earlier note to carry the sentence from.")


def headline_sentence(m):
    """§3.4's headline rule, worded for the note."""
    h = m["holdout"]
    lead = "guidance" if h["guidance"]["headline"] else "seasonal"
    beats = [b for b in ("guidance", "seasonal", "last") if h["tests"][b]["holm_reject"] and h["rel_mae"][b] < 1]
    if beats:
        names = ", ".join(BASE_NAMES[b] for b in beats)
        return (f"Over 26 held-out quarters the registry count beat {names}: it was off by {f1(h['mae']['ratio'])} "
                f"jets a quarter on average, against {f1(h['mae'][beats[0]])} for {BASE_NAMES[beats[0]]}.")
    return (f"Over 26 held-out quarters the registry count was off by {f1(h['mae']['ratio'])} jets a quarter on "
            f"average, against {f1(h['mae'][lead])} for {BASE_NAMES[lead]}. The difference is not statistically "
            f"distinguishable.")


def low_line(m):
    """A sentence naming a simple rule that missed by less on average than the registry estimate, if one did."""
    h = m["holdout"]
    low = min(("seasonal", "last"), key=lambda b: h["mae"][b])
    if h["mae"][low] < h["mae"]["ratio"]:
        return f" Simply repeating {BASE_NAMES[low]} missed by less on average, {f1(h['mae'][low])}."
    return ""


def drift_line(h):
    """The coverage ratio's recent quarters when they all sit below its mean, which the one-sided flag cannot see."""
    cr = h["coverage_ratio"]
    recent = [cr["by_quarter"][q] for q in ("2025Q4", "2026Q1", "2026Q2") if q in cr["by_quarter"]]
    if len(recent) == 3 and all(x < cr["mean"] for x in recent):
        return (f" The drift runs the other way: the last three held-out quarters sit at {', '.join(f2(x) for x in recent)} "
                f"against a mean of {f2(cr['mean'])}, so the registry is counting more events per delivery than "
                "usual, which the ratio's trailing scale absorbs only with a lag.")
    return ""


class Cites:
    """Claims are cited by id; the visible marker numbers each distinct source, listed once."""

    def __init__(self, cl):
        self.by_id = {c["id"]: c for c in cl}
        self.order = []
        self.sources = []

    def has(self, cid):
        return cid in self.by_id

    def sup(self, cid):
        if cid not in self.order:
            self.order.append(cid)
        c = self.by_id[cid]
        key = (c["source_type"], c["url_or_accn"])
        if key not in self.sources:
            self.sources.append(key)
        return f'<sup data-claim="{cid}" data-n="{self.sources.index(key) + 1}"></sup>'

    def say(self, cid):
        """The claim's sentence with its citation, or '' when the registry lacks it."""
        c = self.by_id.get(cid)
        return f"{esc(c['text'])}{self.sup(cid)}" if c else ""

    def prefix(self, pre):
        return [cid for cid in sorted(self.by_id) if cid.startswith(pre)]


def table(head, rows, cls=""):
    th = "".join(f"<th>{esc(h)}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def by_year(root, chosen):
    """{year: {model: [absolute errors]}} over the held-out quarters."""
    rows = read_csv(Path(root) / "results/holdout.csv")
    out = {}
    for r in rows:
        if r["definition"] in ("none", chosen):
            out.setdefault(r["quarter"][:4], {}).setdefault(r["model"], []).append(float(r["ae"]))
    return dict(sorted(out.items()))


def live_state(root, q):
    lv = Path(root) / "results/live"
    pred_p = Path(root) / "predictions" / f"{q}.json"
    lock = read_json(lv / f"{q}_lock.json") if (lv / f"{q}_lock.json").exists() else None
    score = read_json(lv / f"{q}_score.json") if (lv / f"{q}_score.json").exists() else None
    pred = read_json(pred_p) if (lock and pred_p.exists()) else read_json(basis_path(root))
    return pred, lock, score


def et_time(iso):
    t = live.parse_now(iso).astimezone(live.ET)
    return t.strftime("%Y-%m-%d"), t.strftime("%H:%M")


CSS = """
@font-face { font-family: "IBM Plex Sans Var"; src: url(../site/fonts/ibm-plex-sans-wght.woff2) format("woff2");
  font-weight: 100 700; font-style: normal; }
@page { size: Letter; margin: 0.6in 0.6in 0.8in;
  @bottom-center { content: "PAGEFOOT"; font: 400 7.2pt "IBM Plex Sans Var", "Helvetica Neue", Arial, sans-serif;
    color: #5f5a52; } }
:root { --ink: #1c1a17; --ink-3: #423e38; --muted: #5f5a52; --line: #c4bfb6; --line-soft: #dedad3;
  --accent: #1d3f6e; --wash: #f1efeb; --surface: #fbfaf8; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: var(--ink); background: #ffffff; font: 400 9.3pt/1.4 "IBM Plex Sans Var", "Helvetica Neue",
  Arial, sans-serif; font-variant-numeric: tabular-nums; }
h1 { font-size: 21pt; line-height: 1.15; margin: 0 0 4pt; font-weight: 600; }
h2 { font-size: 12.5pt; margin: 14pt 0 5pt; padding-top: 5pt; border-top: 1.5pt solid var(--ink); font-weight: 600; }
h3 { font-size: 10pt; margin: 9pt 0 3pt; font-weight: 600; }
p { margin: 0 0 6pt; }
sup { font-size: 6.5pt; color: var(--accent); }
sup[data-n]::after { content: attr(data-n); }
ol.claims li::marker { color: var(--accent); }
a { color: var(--accent); }
.byline { color: var(--muted); margin-bottom: 12pt; }
.keypoints { border-top: 1.5pt solid var(--ink); border-bottom: 1pt solid var(--line); padding: 8pt 0 4pt;
  margin: 10pt 0 12pt; }
.keypoints li { margin-bottom: 5pt; }
.keypoints ol { margin: 0; padding-left: 16pt; }
.disclaimer { font-size: 8.4pt; color: var(--muted); border: 1pt solid var(--line); padding: 6pt 8pt; margin-top: 10pt; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0 6pt; font-size: 8.1pt; page-break-inside: avoid; }
th { text-align: right; font-weight: 600; border-bottom: 1pt solid var(--ink); padding: 3pt 5pt; vertical-align: bottom; }
td { text-align: right; padding: 2pt 5pt; border-bottom: 0.5pt solid var(--line-soft); }
th:first-child, td:first-child { text-align: left; }
tr.emph td { font-weight: 600; }
.exhibit { page-break-inside: avoid; margin: 6pt 0 10pt; }
.exhibit .cap { font-size: 8.4pt; font-weight: 600; margin-bottom: 2pt; }
.exhibit .src { font-size: 7.4pt; color: var(--muted); margin-top: 2pt; }
.exhibit img { width: 100%; display: block; border: 0.5pt solid var(--line-soft); }
.callout { background: var(--wash); border-left: 3pt solid var(--accent); padding: 7pt 9pt; margin: 6pt 0 10pt;
  page-break-inside: avoid; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; }
.small { font-size: 8.4pt; color: var(--ink-3); }
.pb { page-break-before: always; }
ol.sources { font-size: 7.4pt; padding-left: 14pt; }
ul.tight { margin: 2pt 0 6pt; padding-left: 13pt; } ul.tight li { margin-bottom: 2pt; }
.exhibit img { width: auto; max-width: 100%; max-height: 3.3in; margin: 0 auto; border: 0; }
.urls { columns: 2; column-gap: 12pt; font-size: 6.2pt; line-height: 1.35; color: var(--ink-3); margin-top: 2pt; }
.urls span { display: block; }
h2, h3, .exhibit .cap { break-after: avoid; page-break-after: avoid; }
.keep { break-inside: avoid; page-break-inside: avoid; }
.exhibit.split { break-inside: auto; page-break-inside: auto; }
ol.sources li { margin-bottom: 2pt; word-break: break-word; }
"""


def _watch(add, C, Y, seg, btb):
    """What the street watches on the print: printed only while the release is still ahead."""
    add("<h2>What the street watches on the print</h2>")
    ytd = sum(Y[x]["total"] for x in qrange("2026Q1", "2026Q2"))
    aero_m = seg["Aerospace"]["2026Q2"][1] / seg["Aerospace"]["2026Q2"][0] * 100
    h1_m = sum(seg["Aerospace"][x][1] for x in ("2026Q1", "2026Q2")) / sum(
        seg["Aerospace"][x][0] for x in ("2026Q1", "2026Q2")) * 100
    marine = [pct(seg["Marine Systems"][x][1] / seg["Marine Systems"][x][0] * 100) for x in qrange("2025Q3", "2026Q2")]
    items = [f"Deliveries against the outlook: GD delivered {ytd} jets in the first half of 2026, against an outlook "
             "of about 160 for the year." + (C.sup("os-del") if C.has("os-del") else ""),
             f"The Aerospace margin: {pct(aero_m)} in 2026Q2 and {pct(h1_m)} for the first half, against the "
             "14.7% GD guided for 2026." + (C.sup("os-margin") if C.has("os-margin") else "")
             + "".join(" " + C.say(c) for c in C.prefix("os-aero-margin")),
             f"Book-to-bill: {btb.get('aerospace', 0):.1f} for Aerospace and {btb.get('defense', 0):.1f} for the "
             "defense segments in 2026Q2.",
             "Marine Systems margins, 2025Q3 to 2026Q2: " + ", ".join(marine) + "."
             + "".join(" " + C.say(c) for c in C.prefix("os-marine")),
             "The G280: " + " ".join(C.say(c) for c in ("os-upside", "pc-g280-israel-supplier") if C.has(c))]
    add("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")


def build(root="."):
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    h = m["holdout"]
    est = read_json(root / "results/estimates.json")
    cfg = read_json(root / "config/calendar.json")
    snap = read_json(root / "data/snapshots/MANIFEST.json")["backtest"]
    chosen = m["definition"]
    cal = Calendar.load(root)
    Y = live.reported_history(root)
    calls = model.load_guidance(root)
    C = Cites(claims_mod.load(root))
    dels = {r["quarter"]: r for r in read_csv(root / "data/processed/gd_deliveries.csv")}
    seg = {}
    for r in read_csv(root / "data/processed/segments.csv"):
        seg.setdefault(r["segment"], {})[r["quarter"]] = (int(r["revenue_usd"]), int(r["operating_earnings_usd"]))
    btb = {r["group"]: float(r["ratio"]) for r in read_csv(root / "data/processed/book_to_bill.csv")}
    q = est["target"]
    pred, lock, score = live_state(root, q)
    pace = model.guidance_pace(q, Y, calls, cal)
    rel = cfg.get("releases", {}).get(q)
    S = est["segments"]
    total_ttm = sum(S[s]["ttm_revenue_usd"] for s in SEGMENTS)
    aero_drift = S["Aerospace"]["drift_usd"]

    foot = f"{DISCLAIMER} {disclosure(root)}".replace("\\", "").replace('"', "'")
    parts = [f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>{esc(TITLE)}</title>",
             f"<style>{CSS.replace('PAGEFOOT', foot)}</style></head><body>"]
    add = parts.append

    # 1. Cover
    add(f"<h1>{esc(TITLE)}</h1>")
    scored_lock = bool(score and score.get("locked") and lock)
    rseg = live.reported_segments(root).get(q) if score else None
    if scored_lock:
        dated = (f"Estimate locked from the {pred['snapshot']} registry snapshot; GD reported on {rel}." if rel else
                 f"Estimate locked from the {pred['snapshot']} registry snapshot; GD has since reported.")
    else:
        dated = f"Data as of {pred['snapshot']}."
    add(f'<p class="byline">{dated} Rishabb Shankar, <a href="https://rshankar.dev">'
        f"rshankar.dev</a>. Model, data and code: <a href=\"{REPO_URL}\">{REPO_URL}</a></p>")
    yago_q = shift(q, -4)
    live_point = (f"My registry estimate for {q} is {f1(pred['nowcast']['total'])} Gulfstream deliveries, with a "
                  f"past-miss band of {f1(pred['band'][0])} to {f1(pred['band'][1])}, against "
                  f"{Y[yago_q]['total']} delivered in {yago_q}.")
    t_year, k_q = int(q[:4]), int(q[5])
    outlook = model.outlook_for(q, calls, cal)
    if k_q == 3 and outlook and not score:
        ytd = sum(Y[f"{t_year}Q{j}"]["total"] for j in (1, 2))
        best = max(Y[x]["total"] for x in Y)
        if outlook - ytd - pred["nowcast"]["total"] > best:
            live_point += (f" With {ytd} delivered in the first half, reaching GD's outlook of about {outlook:.0f} "
                           f"would then take a fourth quarter above {best}, GD's best quarter since 2016.")
    # The release-date claim is cited only while the release is still ahead (F019): citing it here whatever the
    # state kept an uncited claim in report/claims.json after a score.
    rel_cite = C.sup("os-release-date") if (C.has("os-release-date") and rel and not score) else ""
    if scored_lock:
        d, t = et_time(lock["published_at"])
        band = "inside" if score["inside_band"] else "outside"
        live_point = (f"For {q} I locked a registry estimate of {f1(pred['nowcast']['total'])} Gulfstream deliveries, "
                      f"with a past-miss band of {f1(pred['band'][0])} to {f1(pred['band'][1])}, as a "
                      f"{lock_words(cfg, lock['published_at'])}, at {t} ET on {d}. GD reported "
                      f"{score['reported']['total']}{' on ' + rel if rel else ''}: the lock missed by "
                      f"{f1(score['ae_total'])} ({score['ape_pct']:.0f}%), {band} the band.")
        cmp_ = comparators(root, q, score, pred)
        if cmp_:
            live_point += (" Other misses for the quarter: "
                           + ", ".join(f"{lab} ({val}) by {miss}" for lab, val, miss in cmp_) + ".")
            live_point += old_events_line(root, pred)
    elif lock:
        d, t = et_time(lock["published_at"])
        live_point += f" I locked it as a {lock_words(cfg, lock['published_at'])}, at {t} ET on {d}."
    elif score:
        live_point += " The quarter missed its lock window, so this estimate was never locked."
        live_point += f" GD reported {score['reported']['total']}"
        if score.get("guidance_pace") is not None:
            live_point += f", against a guidance pace of {f1(score['guidance_pace'])}"
        live_point += "."
    add('<div class="keypoints"><ol>')
    add(f"<li>{esc(headline_sentence(m))}{esc(low_line(m))} {esc(FRAMING.format(snap=snap))}</li>")
    add(f"<li>{esc(live_point)}" + (f" GD expects to report on {rel}.{rel_cite}" if rel and not score else "") + "</li>")
    if rseg:
        add(f"<li>At trailing Aerospace revenue per delivery of {mn(est['revenue_per_delivery_usd'])}, the locked "
            f"estimate implied {bn(est['aerospace_from_nowcast_usd'])} of Aerospace revenue for {q}, and scaling last "
            f"year's quarter by trailing growth gave {bn(aero_drift)}. GD reported {bn(rseg['Aerospace'][0])}, against "
            f"{bn(seg['Aerospace']['2025Q3'][0])} a year earlier. The {mn(est['revenue_per_delivery_usd'])} includes "
            "services and Jet Aviation revenue, which a delivery count does not measure. The delivery-based figure is "
            f"{esc(LABEL)}, and it carried the delivery miss into revenue.</li>")
    else:
        add(f"<li>At trailing Aerospace revenue per delivery of {mn(est['revenue_per_delivery_usd'])}, that estimate "
            f"implies {bn(est['aerospace_from_nowcast_usd'])} of Aerospace revenue for {q}, against "
            f"{bn(seg['Aerospace']['2025Q3'][0])} a year earlier; scaling last year's quarter by trailing growth gives "
            f"{bn(aero_drift)} instead. The {mn(est['revenue_per_delivery_usd'])} includes services and Jet Aviation "
            f"revenue, which a delivery count does not measure. This is {esc(LABEL)}.</li>")
    add("</ol></div>")
    if score:
        add('<div class="callout"><p>I made the estimates in this note before GD reported ' + esc(q)
            + (f" on {rel}" if rel else "")
            + ". The key points above, the locked-quarter paragraph and Exhibit 8 now carry what GD reported, and I "
              "have revised other wording since. The estimates in the sections marked \"before the release\" and in "
              "Exhibit 9, Exhibit 10 and Exhibit 11 are unchanged, so each can be read against the result.</p></div>")
    add(f'<div class="disclaimer"><p>{esc(DISCLAIMER)}</p><p id="disclosure">{esc(disclosure(root))}</p></div>')

    # 2. Business overview
    add("<h2>Business overview</h2>")
    mix_rows = []
    for s in SEGMENTS:
        mix_rows.append([esc(s), bn(S[s]["ttm_revenue_usd"]), pct(S[s]["ttm_revenue_usd"] / total_ttm * 100),
                         pct(S[s]["ttm_margin"] * 100)])
    add(f'<div class="exhibit"><div class="cap">Exhibit 1. Segment revenue and operating margin, four quarters '
        f"to 2026Q2</div>{table(['Segment', 'Revenue', 'Share of revenue', 'Operating margin'], mix_rows)}"
        f'<div class="src">Source: GD earnings releases, 2025Q3 to 2026Q2. Segment figures exclude Corporate.</div></div>')
    bo = " ".join(C.say(cid) for cid in C.prefix("bo-"))
    add(f"<p>GD reports four segments. Over the four quarters to 2026Q2, Aerospace, the segment that holds "
        f"Gulfstream, earned {bn(S['Aerospace']['ttm_revenue_usd'])} of revenue, "
        f"{pct(S['Aerospace']['ttm_revenue_usd'] / total_ttm * 100)} of the four segments' total, at a "
        f"{pct(S['Aerospace']['ttm_margin'] * 100)} operating margin. {bo}</p>")

    # 3. Product cycle
    pcs = [cid for cid in PRODUCT_IDS if C.has(cid)]
    if pcs:
        add("<h2>Gulfstream's product cycle</h2>")
        add('<ul class="tight">' + "".join(f"<li>{C.say(cid)}</li>" for cid in pcs) + "</ul>")

    # 4. The tracker
    add('<h2>The tracker</h2>')
    add("<p>I read every Gulfstream jet in the FAA's aircraft registry, including the G280, which the registry "
        "files under its builder, IAI. For each airframe I take the first sign that it reached a customer: a "
        "customer's registration certificate or the cancellation of Gulfstream's own registration for export, "
        "whichever comes first, no later than a year after the jet's first airworthiness date. I count those events in each "
        "of GD's fiscal quarters, by cabin, and scale the count by how many deliveries GD reported per registry "
        "event over the four quarters before. That scaled count is the estimate. A design window from 2017Q1 to "
        f"2019Q4 chose the event definition ({chosen}) before I scored the 26 quarters from 2020Q1 to 2026Q2. "
        "GD's guidance pace, the main comparison, is GD's latest full-year delivery outlook less the deliveries "
        "already reported that year, spread over the remaining quarters by their usual share of the year; where no "
        "call gave a number, it falls back to the same quarter last year.</p>")
    add(f'<div class="callout"><p>{esc(FRAMING.format(snap=snap))}</p><p><strong>{esc(headline_sentence(m))}'
        f"</strong>{esc(low_line(m))} In that sentence the registry count is the registry estimate, the first row "
        "of the exhibit below, not the raw registry count in its second. GD's guidance pace is my construction from "
        "GD's full-year outlook, not a figure GD publishes.</p></div>")
    hrows = []
    for mm in ("ratio", "raw", "guidance", "seasonal", "last"):
        hrows.append([esc(NAMES[mm]), f1(h["mae"][mm]), pct(h["mape"][mm]), f1(h["bias"][mm]),
                      f1(h["mae_large"][mm]), f1(h["mae_mid"][mm]), f1(h["mae_ex_2020"][mm])])
    add(f'<div class="exhibit"><div class="cap">Exhibit 2. Average miss on the 26 held-out quarters, aircraft</div>'
        + table(["Model", "Average miss", "Average miss, %", "Bias", "Large cabin", "Mid cabin", "Excluding 2020"],
                hrows) + '<div class="src">Bias is the average of estimate minus GD\'s count. Source: '
        "results/metrics.json.</div></div>")
    trows = []
    for b in ("guidance", "seasonal", "last"):
        t = h["tests"][b]
        ac = h["autocorr_lag1"][b]
        trows.append([esc(cap(BASE_NAMES[b])), str(t["wins"]), str(t["losses"]), str(t["ties"]),
                      f"{t['p_one_sided']:.3f}", "rejected" if t["holm_reject"] else "not rejected",
                      f2(h["rel_mae"][b]), f2(ac) if ac is not None else "n/a"])
    add('<div class="exhibit"><div class="cap">Exhibit 3. Sign tests of the registry estimate against each '
        "baseline, Holm-corrected</div>"
        + table(["Baseline", "Quarters better", "Quarters worse", "Ties", "One-sided p", "Holm", "Relative miss",
                 "Lag-1 autocorrelation"], trows)
        + '<div class="src">Relative miss is the registry estimate\'s average miss over the baseline\'s. A positive '
          "autocorrelation of the quarterly differences weakens the sign test.</div></div>")
    g = h["guidance"]
    on_sourced = {mm: [float(r["ae"]) for r in read_csv(root / "results/holdout.csv")
                       if r["model"] == mm and r["definition"] in ("none", chosen)
                       and r["quarter"] not in g["fallback_quarters"]] for mm in ("ratio", "seasonal")}
    add(f"<p>GD stated a numeric delivery outlook covering {g['sourced']} of the 26 held-out quarters; the other "
        f"{len(g['fallback_quarters'])}, all in 2021, fall back to the same quarter last year. On those "
        f"{g['sourced']} quarters GD's guidance pace missed by {f1(g['mae_sourced'])} aircraft on average, against "
        f"{f1(sum(on_sourced['ratio']) / len(on_sourced['ratio']))} for the registry estimate and "
        f"{f1(sum(on_sourced['seasonal']) / len(on_sourced['seasonal']))} for the same quarter last year. The "
        f"registry estimate's past-miss band held GD's count in {h['band']['hits']} of 26 held-out quarters "
        f"({pct(h['band']['coverage_pct'])}, against a nominal 80%; 95% interval {pct(h['band']['cp95_pct'][0])} to "
        f"{pct(h['band']['cp95_pct'][1])}).</p>")
    add(f'<div class="exhibit"><div class="cap">Exhibit 4. GD\'s reported deliveries against the five estimates'
        f'</div><img src="../output/charts/track_record.png" alt="Line chart of GD\'s reported Gulfstream '
        f'deliveries by quarter from 2016Q1 to 2026Q2 against the five estimates"></div>')
    ea = read_csv(root / "results/holdout.csv")
    ratio_rows = sorted([r for r in ea if r["model"] == "ratio"], key=lambda r: -float(r["ae"]))[:5]
    yrs = by_year(root, chosen)
    add("<h3>Where it missed</h3>")
    add("<p>The five largest misses were " + ", ".join(
        f"{r['quarter']} ({f1(float(r['total']))} against {r['actual']})" for r in ratio_rows)
        + ". No filing or call states why the registry count differed from GD's count in those quarters. "
          "The truncation test below cuts each quarter's own registry events a set number of days before the "
          "quarter ends, a crude stand-in for a registry that has not finished posting. Archived registry copies "
          "taken a few weeks after four past quarter ends missed by less than the finished copy did. They held more "
          "events for the same past quarters than today's file, which loses a first owner's date when a jet is "
          "resold or re-registered, so a later file is not simply a more complete one. Four quarters prove nothing "
          "either way.</p>")
    yr_rows = [[y + (", first half" if len(v["ratio"]) == 2 else "")] + [f2(sum(v[mm]) / len(v[mm])) for mm in
               ("ratio", "raw", "guidance", "seasonal", "last")] for y, v in yrs.items()]
    tr = h["truncation_mae"]
    add('<div class="two"><div class="exhibit"><div class="cap">Exhibit 5. Average miss by year, aircraft</div>'
        + table(["Year", "Ratio", "Raw", "Guidance", "Seasonal", "Last"], yr_rows)
        + '<div class="src">No 2021 call gave a full-year figure that the preregistered rule reads, so guidance in '
          "2021 is the same quarter last year." + esc(readings_footnote(root)) + "</div>"
        + '</div><div class="exhibit"><div class="cap">Exhibit 6. Registry estimate\'s average miss with each '
          "quarter's events cut early</div>"
        + table(["Days cut", "Average miss"], [[d, f1(tr[d])] for d in ("0", "30", "60", "90")])
        + f"<p class=\"small\">Coverage drift: the preregistered flag looks for quarters from 2025Q3 to 2026Q2 "
          f"above the mean plus two standard deviations of GD deliveries per registry event"
        + (f"; it flags {', '.join(h['coverage_ratio']['flags'])}." if h["coverage_ratio"]["flags"] else
           "; none is.") + drift_line(h)
        + "</p></div></div>")
    add('<div class="exhibit"><div class="cap">Exhibit 7. The registry estimate\'s miss by quarter and the band '
        'built from earlier misses</div><img src="../output/charts/signed_errors.png" alt="Bar chart of the '
        'registry estimate minus GD\'s count by quarter, with the past-miss band"></div>')
    add(f"<h3>The {'locked' if scored_lock else 'live'} quarter: {q}</h3>")
    ev, tr_ = pred["events"], pred["trailing"]
    body = (f"By the {pred['snapshot']} registry snapshot, {ev['large']} large-cabin and {ev['mid']} mid-cabin "
            f"airframes had a delivery event in {q}'s window (after {pred['window_start']}, through {pred['window_end']}). Over "
            f"the four quarters before, GD reported {tr_['reported']['large']} large-cabin and "
            f"{tr_['reported']['mid']} mid-cabin deliveries against {tr_['registry']['large']} and "
            f"{tr_['registry']['mid']} registry events. Scaled the same way, the estimate is "
            f"{f1(pred['nowcast']['total'])} ({f1(pred['nowcast']['large'])} large, {f1(pred['nowcast']['mid'])} mid), "
            f"with a past-miss band of {f1(pred['band'][0])} to {f1(pred['band'][1])}.")
    if lock:
        d, t = et_time(lock["published_at"])
        body += f" I locked this estimate as a {lock_words(cfg, lock['published_at'])}, at {t} ET on {d}."
    elif score:
        body += " This is the build estimate: the quarter missed its lock window, so it was never locked."
    else:
        eve = (live.parse_now(rel + "T12:00:00Z") - live.dt.timedelta(days=1)).date().isoformat() if rel else None
        body += (" This is the build estimate; the locked estimate replaces it"
                 + (f" on {eve}, the day before GD's {rel} release." if rel else " before the release."))
        age = (live.dt.date.fromisoformat(pred["snapshot"]) - live.dt.date.fromisoformat(pred["window_end"])).days
        if age < 20:
            body += (" This snapshot came sooner after the quarter's end than any archived copy the as-of study "
                     "scored, so more of the quarter's registrations may still be missing.")
    if scored_lock:
        band = "inside" if score["inside_band"] else "outside"
        body += (f" GD then reported {score['reported']['total']}: the lock missed by {f1(score['ae_total'])} "
                 f"({score['ape_pct']:.0f}%), {band} the band.")
        if score.get("guidance_pace") is not None:
            body += (f" GD's guidance pace for the quarter had been {f1(score['guidance_pace'])}, a miss of "
                     f"{f1(score['guidance_ae'])}.")
        raw = pred["events"]["large"] + pred["events"]["mid"]
        scale = (tr_["reported"]["large"] + tr_["reported"]["mid"]) / (tr_["registry"]["large"] + tr_["registry"]["mid"])
        body += (f" The raw count of {raw} events missed by {abs(raw - score['reported']['total'])}; the estimate "
                 f"came out lower because the four quarters before gave a scale of {f2(scale)} deliveries per event."
                 + old_events_line(root, pred))
    elif score:
        body += f" GD then reported {score['reported']['total']}."
        if score.get("guidance_pace") is not None:
            body += f" GD's guidance pace for the quarter had been {f1(score['guidance_pace'])}."
    add(f"<p>{esc(body)} The band comes from errors measured on a registry file that had months or years to fill in, so "
        "it may not fit a live lock.</p>")

    # 5. Backlog, book-to-bill, estimates
    before = ", before the release" if score else ""
    add(f'<h2>Backlog, book-to-bill and the 2026Q3 estimates{before}</h2>')
    add(f"<p>Aerospace ended 2026Q2 with {bn(S['Aerospace']['backlog_usd'])} of backlog, "
        f"{f2(S['Aerospace']['coverage_years'])} years of its trailing revenue. "
        + (C.say("os-btb") if C.has("os-btb") else
           f"Book-to-bill in 2026Q2 was {btb.get('aerospace', 0):.1f} for Aerospace.") + "</p>")
    erows = []
    a_tot = sum(seg[s]["2025Q3"][0] for s in SEGMENTS)

    def erow(name, a, e, r):
        """Year-ago actual, the estimate, and either its change on the year or, once GD has reported, the miss."""
        if r is None:
            return [esc(name), bn(a), bn(e), mn(e - a), pct((e - a) / a * 100)]
        return [esc(name), bn(a), bn(e), bn(r), mn(e - r), pct((e - r) / r * 100)]

    for s in SEGMENTS:
        e = est["aerospace_from_nowcast_usd"] if s == "Aerospace" else S[s]["drift_usd"]
        erows.append(erow(s + (", from the delivery estimate" if s == "Aerospace" else ""), seg[s]["2025Q3"][0], e,
                          rseg[s][0] if rseg else None))
    erows.insert(1, erow("Aerospace, drift baseline", seg["Aerospace"]["2025Q3"][0], aero_drift,
                         rseg["Aerospace"][0] if rseg else None))
    erows.append(erow("Total, with Aerospace from the delivery estimate", a_tot, est["revenue_total_usd"],
                      sum(rseg[s][0] for s in SEGMENTS) if rseg else None))
    if rseg:
        cap8 = "Exhibit 8. 2026Q3 revenue by segment: the estimates made before the release, and what GD reported"
        head8 = ["Segment", "2025Q3 actual", "2026Q3 estimate", "GD reported", "Estimate less reported", "Miss, %"]
        tail8 = (f" GD reported {bn(sum(rseg[s][1] for s in SEGMENTS))} of operating earnings for the four segments "
                 f"(release {esc(rseg['accn'])}).")
    else:
        cap8, tail8 = "Exhibit 8. 2026Q3 revenue estimates by segment", ""
        head8 = ["Segment", "2025Q3 actual", "2026Q3 estimate", "Change", "Change, %"]
    add(f'<div class="exhibit"><div class="cap">{cap8}</div>'
        + table(head8, erows)
        + f'<div class="src">Aerospace from the delivery estimate is {esc(LABEL)}. Aerospace revenue carries '
          "services and Jet Aviation. The drift baseline and the defense "
          "segments use the same quarter last year scaled by trailing growth. Segment operating earnings at "
          f"trailing margins: {bn(est['operating_earnings_total_usd'])}, Corporate excluded.{tail8}</div></div>")
    srows = [[f"{x['deliveries_change']:+d}", f1(x["deliveries"]), bn(x["aerospace_revenue_usd"])]
             for x in est["sensitivity"]]
    out_bits = [C.say(c) for c in ("os-del", "os-rev", "os-margin") if C.has(c)]
    add('<div class="two"><div class="exhibit"><div class="cap">Exhibit 9. Aerospace revenue for each delivery '
        "count: deliveries times trailing revenue per delivery, a mechanical figure"
        + (", made before the release" if score else "") + "</div>" + table(["Change", "Deliveries", "Aerospace revenue"], srows) + "</div><div>"
        + ("<h3>GD's outlook for 2026, before the release</h3><p>As of GD's 2026-07-29 call: " if score else
           "<h3>GD's own outlook for 2026</h3><p>") + " ".join(out_bits)
        + "</p></div></div>")

    # 6. Defense segments
    add(f"<h2>The defense segments{before}</h2>")
    drows = [[esc(s), bn(S[s]["backlog_usd"]), f2(S[s]["coverage_years"]), bn(S[s]["drift_usd"]),
              pct(S[s]["ttm_margin"] * 100)] for s in DEFENSE]
    add('<div class="exhibit"><div class="cap">Exhibit 10. Defense backlog in years of trailing revenue, and the '
        "2026Q3 baseline" + (", made before the release" if score else "") + "</div>"
        + table(["Segment", "Backlog, 2026Q2", "Coverage, years", "2026Q3 estimate", "Operating margin"], drows)
        + ('<div class="src">Backlog is as of 2026Q2, the last quarter before these estimates were made. GD\'s 2026Q3 '
           "release (accession 0000040533-26-000036, Exhibit H) reports Marine Systems backlog of $146.9B, so this "
           "table is not current.</div>" if score else "") + "</div>")
    add("<p>For the defense segments I use my defense backlog study's best next-quarter baseline. That study "
        "tested five other defense primes; GD was left out because it stopped tagging backlog in XBRL in 2018. Pooled "
        "across those five, the next-quarter error was 9.9% for a backlog model, 7.3% for the seasonal naive and 6.5% "
        "for the seasonal naive with drift; four quarters out it was 9.4% for backlog, 5.8% for trailing revenue and "
        "6.0% for trailing revenue with drift. So the 2026Q3 defense figures above are the seasonal naive with drift, "
        "and backlog appears as coverage beside them. Applying that study to GD is an assumption: it did not test GD. "
        f'The study is at <a href="{STUDY_URL}">{STUDY_URL}</a>; these percentages are from its published data file '
        "as of 2026-10-13.</p>")

    # 7. What the street watches: a preview of the print, so it is dropped once GD has reported
    if not score:
        _watch(add, C, Y, seg, btb)

    # 8. Risks
    risks = C.prefix("risk-")
    if risks:
        add("<h2>Risks</h2><p>The risks closest to this tracker are Gulfstream's own, and the product cycle section "
            "cites them: the planned production break between the last G280 and the G300, and the timing of the "
            "G400. Below are GD's general risk factors, as its filings state them; the limits of my method follow "
            "separately.</p>")
        add('<ul class="tight">' + "".join(f"<li>{C.say(cid)}</li>" for cid in risks) + "</ul>")

    # 9. Limitations
    add("<h2>Limitations of the method</h2><ul>")
    for li in limitations(root):
        add(f"<li>{li}</li>")
    add("</ul>")

    # 10. Model page
    add('<h2>Model page</h2>')
    dm = m["design"]["mae"]
    srow = [["Average miss, ratio", f1(dm[chosen]["ratio"]), f1(h["mae"]["ratio"])],
            ["Average miss, raw", f1(dm[chosen]["raw"]), f1(h["mae"]["raw"])],
            ["Average miss, same quarter last year", f1(dm["none"]["seasonal"]), f1(h["mae"]["seasonal"])],
            ["Average miss, last quarter", f1(dm["none"]["last"]), f1(h["mae"]["last"])]]
    seg_rows = [[esc(s), bn(S[s]["ttm_revenue_usd"]), bn(S[s]["ttm_revenue_prior_usd"]), bn(S[s]["drift_usd"]),
                 pct(S[s]["ttm_margin"] * 100), bn(S[s]["backlog_usd"]), f2(S[s]["coverage_years"])] for s in SEGMENTS]
    derived = [["Deliveries, four quarters to 2026Q2", str(est["ttm_deliveries"])],
               ["Aerospace revenue per delivery", mn(est["revenue_per_delivery_usd"])],
               [f"{q} delivery estimate", f1(est["nowcast_total"])],
               ["Aerospace revenue from the estimate", bn(est["aerospace_from_nowcast_usd"])],
               ["Aerospace operating earnings from the estimate", bn(est["aerospace_oe_from_nowcast_usd"])],
               ["Revenue, all four segments", bn(est["revenue_total_usd"])],
               ["Segment operating earnings, all four segments", bn(est["operating_earnings_total_usd"])]]
    add('<div class="exhibit split"><div class="cap">Exhibit 11. The workbook\'s Summary and Segments sheets</div>'
        + table(["Summary", "Design (12 quarters)", "Held out (26 quarters)"], srow)
        + table(["Segment", "Revenue, 4Q to 2026Q2", "Revenue, 4Q to 2025Q2", "Drift, 2026Q3", "Margin, 4Q",
                 "Backlog", "Coverage, years"], seg_rows)
        + table(["Derived", "Value"], derived)
        + '<div class="src">The rows "from the estimate" are mechanical: the delivery estimate times trailing '
          'Aerospace revenue per delivery, services included. '
        + ("The 2026Q3 figures here are the estimates made before the release; Exhibit 8 has what GD reported. "
           if score else "") + 'From output/gd_gulfstream_model.xlsx, where every figure above is a live formula over '
          "typed inputs.</div></div>")

    # 11. Sources
    add("<h2>Sources</h2><p class=\"small\">Numbered sources are the ones the superscripts cite.</p>"
        '<ol class="sources">')
    forms = {"0000040533-26-000006": "GD Form 10-K for 2025", "0000040533-25-000008": "GD Form 10-K for 2024",
             "0000040533-25-000014": "GD Form 10-Q for 2025Q1", "0000040533-25-000045": "GD Form 10-Q for 2025Q3",
             "0000040533-26-000029": "GD Form 8-K, Exhibit 99.1, 2026Q2 results",
             "0000040533-26-000032": "GD Form 10-Q for 2026Q2"}
    kinds = {"filing": "GD SEC filing", "call": "GD earnings call transcript",
             "press": "Gulfstream press release", "faa": "FAA"}
    for kind, where in C.sources:
        got = next(C.by_id[c]["retrieved_on"] for c in C.order
                   if (C.by_id[c]["source_type"], C.by_id[c]["url_or_accn"]) == (kind, where))
        link = edgar(where) if kind == "filing" else where
        label = forms.get(where, kinds.get(kind, kind)) if kind == "filing" else kinds.get(kind, kind)
        add(f"<li>{label}, {esc(link)} , retrieved {got}.</li>")
    accns = sorted({r["accn"] for r in dels.values()} | {r["accn"] for r in read_csv(root / "data/processed/segments.csv")}
                   | {x["accn"] for x in live.scores(root).values()})
    add("<li>GD earnings releases, Exhibit 99.1 to each results 8-K, in these SEC EDGAR folders:"
        '<div class="urls">' + "".join(f"<span>{esc(edgar(a))} </span>" for a in accns) + "</div></li>")
    # No date here that moves every day: the note then changes only at a lock or a score, and the PDF, which only
    # a Mac can print, stays in step with it (F008).
    add(f"<li>FAA Releasable Aircraft database, ReleasableAircraft.zip (ACFTREF, MASTER and DEREG), snapshot "
        f"{snap} for the backtest" + (f", and snapshot {pred['snapshot']} for the {q} lock" if lock else "") + ".</li>")
    cd = sorted(r["call_date"] for r in read_csv(root / "data/guidance.csv"))
    add(f"<li>GD earnings calls from {cd[0]} to {cd[-1]}, for the guidance outlooks in data/guidance.csv.</li>")
    add(f'<li>Repository: <a href="{REPO_URL}">{REPO_URL}</a></li></ol>')
    add("</body></html>")
    text = "\n".join(parts) + "\n"
    write_text(root / "report/note.html", text)
    pool = claims_mod.load(root)
    if {c["id"] for c in pool} != set(C.order):
        kept = [c for c in pool if c["id"] in set(C.order)]
        import json
        write_text(root / "report/claims.json", json.dumps(kept, indent=2, ensure_ascii=False) + "\n")
    return text


def old_events_line(root, pred):
    """What the lock's raw count held: how many of its events sat on airframes at least three years old."""
    old = lock_old_events(root, pred)
    if not old:
        return ""
    return (f" Of the {old[1]} events in the raw count, {old[0]} were airframes at least three years old by the "
            "registry's year of manufacture, so the raw count is not a count of new jets.")


def used_share(root):
    """How many counted events sit on airframes at least three years old by the registry's year of manufacture."""
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    e = m["definition"].lower()
    reg = read_csv(root / "data/processed/registry_quarterly.csv")
    lo, hi = min(r["window_start"] for r in reg), max(r["window_end"] for r in reg)
    ev = [r for r in read_csv(root / "data/processed/serials.csv") if r[e] and lo < r[e] <= hi]
    old = [r for r in ev if r["year_mfr"] and int(r[e][:4]) - int(r["year_mfr"]) >= 3]
    if not ev:
        return ""
    return (f" It is not rare: by the registry's own year of manufacture, {len(old):,} of the {len(ev):,} counted events "
            f"({len(old) / len(ev) * 100:.1f}%) are airframes at least three years old.")


def limitations(root):
    """The seven limitations from DECISIONS.md's README list, in plain words."""
    return [
        "Exports: a jet exported to a foreign registry without a US registration leaves no US record, "
        "so the registry never sees that delivery. Since 2022 the registry's yearly mid-cabin count has stayed within "
        "a few jets of GD's, so G280 exports do not look like a large gap now.",
        "Processing: registry processing can lag by months. The backtest reads events by their stamped date in a "
        "file that had months or years to fill in, while a live estimate sees only what has posted.",
        "Military: military and special-mission airframes may never reach the civil registry.",
        "Handover: GD counts a delivery at its own handover, which a registration or cancellation date only "
        "approximates, so an event can land in the next or previous quarter.",
        "Coverage: the ratio assumes the registry's coverage of GD's count holds steady from year to year. It "
        "drifted: the registry keeps only an airframe's current certificate, so a resold or renewed jet loses its "
        "first owner's date.",
        "Used jets: a used jet that re-entered the US registry with a fresh airworthiness date, one with no "
        "airworthiness date or year of manufacture, or one whose maker code changed, "
        "can read as a new delivery." + used_share(root),
        "Mid-cabin gap: the mid-cabin count rests on the G280 alone, and GD has said G280 deliveries end in 2027 with a "
        "production break before the G300 (product cycle, above). The method is untested in a quarter with few or no "
        "mid-cabin deliveries.",
        "Band: the past-miss band comes from errors measured on a finished registry file, so it may not fit a live lock.",
        "Audit: in 10 of 30 airframes checked against outside sources (33.3%), the source disagreed with the registry "
        "reading or could not confirm it: five were used jets read as new deliveries, two had an earlier stated "
        "delivery, and three could not be confirmed. All but one source was a registry mirror or aircraft-history "
        "site, and every event the audit could date fell between 2000 and 2019, so it says little about recent quarters.",
    ]


def run(root="."):
    root = Path(root)
    if not (root / "results/estimates.json").exists():
        print("skip note: no estimates yet")
        return 0
    build(root)
    print("wrote report/note.html")
    return 0


def run_pdf(root="."):
    """Print the note with headless Chrome when its HTML changed, then copy it to site/."""
    root = Path(root)
    src = root / "report/note.html"
    pdf, copy = root / "output/GD_research_note.pdf", root / "site/GD_research_note.pdf"
    stamp = root / "output/GD_research_note.inputs.sha256"
    digest = sha256(src.read_bytes()) + "  report/note.html\n"
    if pdf.exists() and copy.exists() and stamp.exists() and stamp.read_text() == digest:
        print("note unchanged; PDF kept")
        return 0
    if not Path(CHROME).exists():
        print("skip PDF: no Chrome")
        return 0
    pdf.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--no-pdf-header-footer", "--disable-gpu",
                    f"--print-to-pdf={pdf.resolve()}", src.resolve().as_uri()], capture_output=True, timeout=180)
    copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, copy)
    write_text(stamp, digest)
    pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))
    print(f"wrote {pdf.relative_to(root)} ({pages} pages) and {copy.relative_to(root)}")
    return 0
