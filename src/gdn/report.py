"""README.md's live summary, ## Results, ## Error analysis and ## Live record, and docs/LINKEDIN_POST.md, from the
results files.

Only the text between each of those headings and the next (and between the live-summary markers) is replaced, so a
second run changes nothing."""
import re
from pathlib import Path

from . import live, model
from .fiscal import Calendar, qidx
from .files import read_csv, read_json, write_text

NAMES = {"ratio": "Registry estimate (ratio)", "raw": "Raw registry count", "guidance": "GD guidance pace",
         "seasonal": "Same quarter last year", "last": "Last quarter"}
BASE = {"guidance": "GD's guidance pace", "seasonal": "the same quarter last year", "last": "last quarter"}
DASH = "https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/"
REPO = "https://github.com/rishabbshankar226/gulfstream-delivery-nowcast"


def f1(x):
    return f"{x:.1f}"


def f2(x):
    return f"{x:.2f}"


def framing(snap):
    return (f"The backtest reads a registry copy from {snap}, which had months or years to fill in. It shows how "
            "well the registry tracks Gulfstream deliveries after the fact. Only the locked quarters test whether it "
            "counts them in time.")


def headline(m):
    h = m["holdout"]
    lead = "guidance" if h["guidance"]["headline"] else "seasonal"
    beats = [b for b in ("guidance", "seasonal", "last") if h["tests"][b]["holm_reject"] and h["rel_mae"][b] < 1]
    if beats:
        return (f"Over 26 held-out quarters the registry count beat {' and '.join(BASE[b] for b in beats)}: it was "
                f"off by {f1(h['mae']['ratio'])} jets a quarter on average, against {f1(h['mae'][beats[0]])} for "
                f"{BASE[beats[0]]}.")
    return (f"Over 26 held-out quarters the registry count was off by {f1(h['mae']['ratio'])} jets a quarter on "
            f"average, against {f1(h['mae'][lead])} for {BASE[lead]}. The difference is not statistically "
            "distinguishable.")


CLARIFY = ("In that sentence the registry count is the scaled registry estimate, the table's first row, not the raw "
           "registry count in its second. GD's guidance pace is my construction, not a figure GD publishes: GD's "
           "full-year delivery outlook, less the deliveries already reported, spread over the remaining quarters by "
           "their usual share of the year.")
PRIVATE = "timestamped GitHub release, made while the repository was private"
SUMMARY_MARKS = ("<!-- live-summary:start -->", "<!-- live-summary:end -->")
DISCLAIMER = "Student project, not investment advice. I am not affiliated with General Dynamics or Gulfstream."


def lock_words(cfg, published_at):
    """How to name one lock. A lock is public only when the repository was already public on the day its release
    was published: `public` is true and `public_since` (an ISO date the owner sets) is on or before that day.
    Every earlier lock stays what it was, a timestamped release nobody outside could see."""
    since = cfg.get("public_since")
    if cfg.get("public") and since and published_at[:10] >= since:
        return "public GitHub release"
    return PRIVATE


def pct1(x):
    return f"{x:.1f}%"


def whole(x):
    return f"{x:.0f}"


def comparators(root, q, score, pred):
    """The other four misses for a scored quarter: guidance pace, raw registry count, same quarter last year,
    last quarter. Each is (label, value text, miss text)."""
    Y = live.reported_history(root)
    actual = score["reported"]["total"]
    out = []
    if score.get("guidance_pace") is not None:
        out.append(("GD's guidance pace", f1(score["guidance_pace"]), f1(score["guidance_ae"])))
    if pred:
        raw = pred["events"]["large"] + pred["events"]["mid"]
        out.append(("the raw registry count", str(raw), str(abs(raw - actual))))
    for label, k in (("the same quarter last year", -4), ("last quarter", -1)):
        prev = Y.get(live.shift(q, k))
        if prev:
            out.append((label, str(prev["total"]), str(abs(prev["total"] - actual))))
    return out


def locked_scores(root):
    """[(quarter, score, prediction, lock)] for every quarter that was locked and then scored, in order."""
    root = Path(root)
    out = []
    for q, s in sorted(live.scores(root).items(), key=lambda kv: qidx(kv[0])):
        lp, pp = root / "results/live" / f"{q}_lock.json", root / "predictions" / f"{q}.json"
        if s.get("locked") and lp.exists() and pp.exists():
            out.append((q, s, read_json(pp), read_json(lp)))
    return out


def live_summary(root):
    """The README's first lines after the lead: the live record so far, then the backtest in one sentence."""
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    h = m["holdout"]
    ls = locked_scores(root)
    scores = live.scores(root)
    if ls:
        q, s, p, lock = ls[-1]
        hits = sum(1 for _, x, _, _ in ls if x["inside_band"])
        head = ("one locked quarter, a miss outside its band" if len(ls) == 1 and not s["inside_band"] else
                "one locked quarter, inside its band" if len(ls) == 1 else
                f"{len(ls)} locked quarters, {hits} inside the band")
        cmp_ = comparators(root, q, s, p)
        pace = next((c for c in cmp_ if c[0] == "GD's guidance pace"), None)
        yago = next((c for c in cmp_ if c[0] == "the same quarter last year"), None)
        line = (f"**Live record so far: {head}.** For {q} I locked an estimate of {f1(p['nowcast']['total'])} "
                f"Gulfstream deliveries (band {f1(p['band'][0])} to {f1(p['band'][1])}) the day before GD reported. GD "
                f"reported {s['reported']['total']}, so the lock missed by {f1(s['ae_total'])} ({pct1(s['ape_pct'])}), "
                f"{'inside' if s['inside_band'] else 'outside'} the band.")
        if pace and yago:
            line += (f" GD's guidance pace missed by {pace[2]} and the same quarter last year ({yago[1]}) by {yago[2]}.")
    elif scores:
        q = sorted(scores, key=qidx)[0]
        line = (f"**Live record so far: no locked quarter.** {q} missed its lock window, so there is no locked "
                "estimate to score yet.")
    else:
        line = "**Live record so far: no locked quarter yet.** The first lock comes the day before GD next reports."
    low = min(("seasonal", "last"), key=lambda b: h["mae"][b])
    back = (f"**Backtest, {h['n']} held-out quarters:** the registry estimate missed by {f1(h['mae']['ratio'])} jets a "
            f"quarter on average, GD's guidance pace by {f1(h['mae']['guidance'])} and {BASE[low]} by "
            f"{f1(h['mae'][low])}.")
    if h["mae"][low] < h["mae"]["ratio"]:
        back += f" Simply repeating {BASE[low]} missed by least."
    if not any(t["holm_reject"] for t in h["tests"].values()):
        back += " No test finds the registry estimate better than a baseline."
    back += " The backtest reads a registry copy that had months or years to fill in."
    return line + "\n\n" + back


def split_sentence(root):
    """Where the registry estimate's lower average miss than the guidance pace comes from, when a few years
    carry it: those years against all the other held-out quarters."""
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    chosen = m["definition"]
    ae = {}
    for r in read_csv(root / "results/holdout.csv"):
        if r["definition"] in ("none", chosen):
            ae.setdefault(r["quarter"], {})[r["model"]] = float(r["ae"])
    years = sorted({q[:4] for q in ae})

    def mean(qs, model):
        return sum(ae[q][model] for q in qs) / len(qs)

    won = [y for y in years if mean([q for q in ae if q[:4] == y], "ratio") < mean([q for q in ae if q[:4] == y], "guidance")]
    inside, rest = [q for q in ae if q[:4] in won], [q for q in ae if q[:4] not in won]
    if not won or not rest or len(won) > len(years) / 2 or mean(rest, "ratio") <= mean(rest, "guidance"):
        return ""
    return (f"The registry estimate's lower average miss than the guidance pace comes from {' and '.join(won)}, when "
            f"the guidance pace missed by {f1(mean(inside, 'guidance'))} on average and the registry estimate by "
            f"{f1(mean(inside, 'ratio'))}. In the other {len(rest)} held-out quarters the guidance pace missed by "
            f"{f1(mean(rest, 'guidance'))}, the same quarter last year by {f1(mean(rest, 'seasonal'))} and the registry "
            f"estimate by {f1(mean(rest, 'ratio'))}.")


def reading_2021(root):
    """The one reading of a call that moves a headline figure: GD's January 2021 statement, from the sensitivity file."""
    p = Path(root) / "results/exploratory/sensitivity.json"
    if not p.exists():
        return ""
    v = {x["key"]: x for x in read_json(p)["variants"]}
    a, b = v.get("outlook_2021_as_117"), v.get("preregistered")
    if not a or not b:
        return ""
    t = a["ratio_vs_guidance"]
    return (" One reading matters here. On its 2021-01-27 call GD gave the year only as a change from 2020, \"10 fewer "
            "aircraft\", and the preregistered rule reads a change only when its base figure is in the same sentence, "
            f"so it reads no number. Read as 117, the guidance pace misses by {f1(a['mae']['guidance'])} on average, "
            f"not {f1(b['mae']['guidance'])}, and the registry estimate is closer in {t['wins']} of {a['n']} quarters. "
            "That and the other variants I tried afterwards are in "
            "[results/exploratory/sensitivity.md](results/exploratory/sensitivity.md).")


def lock_timing(root):
    """Why the truncation table is not a model of a live lock: how long after the quarter's end the latest lock was
    made, the quarter's count then, and the same count in the newest daily table."""
    root = Path(root)
    ls = locked_scores(root)
    if not ls:
        return ""
    q, s, p, lock = ls[-1]
    days = (live.dt.date.fromisoformat(p["snapshot"]) - live.dt.date.fromisoformat(p["window_end"])).days
    at_lock = p["events"]["large"] + p["events"]["mid"]
    dates = live.table_dates(root)
    if not dates:
        return ""
    chosen = read_json(root / "results/metrics.json")["definition"]

    def count(date):
        rows = live.read_table(root, date)
        return sum(live.events.count(rows, chosen, c, p["window_start"], p["window_end"]) for c in live.CABINS)

    later = [count(d) for d in dates if d > p["snapshot"]]
    if not later:
        since = "the newest snapshot there is"
    elif all(n == at_lock for n in later):
        since = f"and it is the same in every daily snapshot since, to {dates[-1]}"
    else:
        since = f"and it stands at {later[-1]} in the {dates[-1]} snapshot"
    scale = (p["trailing"]["reported"]["large"] + p["trailing"]["reported"]["mid"]) / \
        (p["trailing"]["registry"]["large"] + p["trailing"]["registry"]["mid"])
    real = s["reported"]["total"] / at_lock
    return (f"That table is not a model of a live lock. The {q} lock read a snapshot taken {days} days after the "
            f"quarter ended, when the quarter's count stood at {at_lock}, {since}. Its miss came from the scale, not "
            f"from late postings: the four quarters before gave {f2(scale)} deliveries per registry event, and the "
            f"quarter itself came in at {f2(real)}.")


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def results(root):
    m = read_json(Path(root) / "results/metrics.json")
    h, d = m["holdout"], m["design"]
    snap = read_json(Path(root) / "data/snapshots/MANIFEST.json")["backtest"]
    rows = [[NAMES[x], f1(h["mae"][x]), f1(h["mape"][x]) + "%", f1(h["bias"][x]), f1(h["mae_large"][x]),
             f1(h["mae_mid"][x]), f1(h["mae_ex_2020"][x])] for x in ("ratio", "raw", "guidance", "seasonal", "last")]
    tests = []
    for b in ("guidance", "seasonal", "last"):
        t = h["tests"][b]
        ac = h["autocorr_lag1"][b]
        tests.append([BASE[b].capitalize() if b != "guidance" else "GD's guidance pace", t["wins"], t["losses"],
                      t["ties"], f"{t['p_one_sided']:.3f}", "rejects" if t["holm_reject"] else "does not reject",
                      f2(h["rel_mae"][b]), f2(ac) if ac is not None else "n/a"])
    positive = [BASE[b] for b in ("guidance", "seasonal", "last") if (h["autocorr_lag1"][b] or 0) > 0]
    g, band = h["guidance"], h["band"]
    lines = [
        framing(snap), "",
        f"**{headline(m)}{low_line(m)}**", "",
        CLARIFY, "",
        "Average miss in aircraft over the 26 held-out quarters, 2020Q1 to 2026Q2:", "",
        md_table(["Model", "Average miss", "Average % miss", "Bias", "Large cabin", "Mid cabin", "Without 2020"], rows),
        "", "Bias is the average of the estimate minus GD's count.", "",
        "One-sided exact sign tests that the registry estimate's miss is smaller than each baseline's, with Holm's "
        "correction across the three:", "",
        md_table(["Baseline", "Registry closer", "Registry further", "Ties", "p", "Holm", "Relative miss",
                  "Lag-1 autocorrelation"], tests),
        "",
        "Relative miss is the registry estimate's average miss divided by the baseline's.",
    ]
    if positive:
        lines += ["", f"The quarter-to-quarter differences against {' and '.join(positive)} are positively "
                      "autocorrelated, so the sign test, which treats quarters as independent, overstates how much "
                      "evidence those quarters carry."]
    lines += ["",
              f"GD stated a numeric delivery outlook covering {g['sourced']} of the 26 held-out quarters, so GD's "
              f"guidance pace is the baseline named first. The other {len(g['fallback_quarters'])} quarters "
              f"({', '.join(g['fallback_quarters'])}) fall back to the same quarter last year, because no 2021 call "
              f"stated a full-year number. On the {g['sourced']} sourced quarters the guidance pace missed by "
              f"{f1(g['mae_sourced'])} aircraft on average." + reading_2021(root), "",
              f"The past-miss band, built from each quarter's earlier misses only, held GD's count in {band['hits']} "
              f"of {band['n']} held-out quarters ({f1(band['coverage_pct'])}%, against a nominal 80%; exact 95% interval "
              f"{f1(band['cp95_pct'][0])}% to {f1(band['cp95_pct'][1])}%).", "",
              f"The design window, 2017Q1 to 2019Q4 (12 quarters), chose **{m['definition']}**: the ratio model's "
              f"average miss was {f2(d['mae']['E1']['ratio'])} under E1 and {f2(d['mae']['E2']['ratio'])} under E2. "
              f"In that window the same quarter last year missed by {f2(d['mae']['none']['seasonal'])} and last "
              f"quarter by {f2(d['mae']['none']['last'])}."]
    return "\n".join(lines)


def error_analysis(root):
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    h, chosen = m["holdout"], m["definition"]
    by = {}
    for r in read_csv(root / "results/holdout.csv"):
        if r["definition"] in ("none", chosen):
            by.setdefault(r["quarter"][:4], {}).setdefault(r["model"], []).append(float(r["ae"]))
    # Two decimals: each year's mean of four integer misses often ends in 5, which one decimal would round to even.
    yrows = [[y + (", first half" if len(v["ratio"]) == 2 else "")]
             + [f2(sum(v[x]) / len(v[x])) for x in ("ratio", "raw", "guidance", "seasonal", "last")]
             for y, v in sorted(by.items())]
    crows = [[NAMES[x], f1(h["mae_large"][x]), f1(h["mae_mid"][x])] for x in ("ratio", "raw", "guidance", "seasonal",
                                                                             "last")]
    cr = h["coverage_ratio"]
    recent = [cr["by_quarter"][q] for q in ("2025Q4", "2026Q1", "2026Q2") if q in cr["by_quarter"]]
    drift = (f" The drift runs the other way: the last three quarters sit at {', '.join(f2(x) for x in recent)} "
             f"against the {f2(cr['mean'])} mean, so the registry is counting more events per delivery than usual, "
             "which the ratio's trailing scale absorbs only with a lag."
             if len(recent) == 3 and all(x < cr["mean"] for x in recent) else "")
    tr = h["truncation_mae"]
    ea = (root / "results/error_analysis.md").read_text()
    table = re.search(r"(\| Quarter \|.*?)\n\n", ea, re.S).group(1)
    top = re.findall(r"^\| (\d{4}Q\d) \|", table, re.M)
    lines = [
        "Average miss by year, aircraft:", "",
        md_table(["Year", "Ratio", "Raw", "Guidance", "Same quarter last year", "Last quarter"], yrows), "",
        *([split_sentence(root), ""] if split_sentence(root) else []),
        "Average miss by cabin, aircraft:", "",
        md_table(["Model", "Large cabin", "Mid cabin"], crows), "",
        f"GD deliveries per registry event averaged {f2(cr['mean'])} from 2017Q1 to 2025Q2. "
        + "The preregistered flag looks for quarters from 2025Q3 to 2026Q2 above the mean plus two standard "
        "deviations, where the registry would be counting fewer events per delivery than usual"
        + (f"; it flags {', '.join(cr['flags'])}." if cr["flags"] else "; none is.") + drift, "",
        "The truncation test cuts each held-out quarter's own registry events a set number of days before the "
        "quarter ends, with its four lags left whole. It stands in, crudely, for a registry that has not finished "
        "posting, and shows how fast the miss grows when a quarter's registrations post late:", "",
        md_table(["Days cut", "Average miss, aircraft"], [[d, f1(tr[d])] for d in ("0", "30", "60", "90")]), "",
        *([lock_timing(root), ""] if lock_timing(root) else []),
        f"Five quarters drive much of the average: {', '.join(top[:-1])} and {top[-1]}. No filing or call states why "
        "the registry count differed from GD's count in any of them. The full write-up is in "
        "[results/error_analysis.md](results/error_analysis.md).", "",
        table,
    ]
    return "\n".join(lines)


def live_record(root):
    root = Path(root)
    cfg = read_json(root / "config/calendar.json")
    lv = root / "results/live"
    qs = sorted({p.name[:6] for p in lv.glob("*_build.json")} | {p.name[:6] for p in lv.glob("*_latest.json")}
                | {p.name[:6] for p in (root / "predictions").glob("*.json")}, key=qidx)
    out = []
    for q in qs:
        rel = cfg.get("releases", {}).get(q)
        lock = read_json(lv / f"{q}_lock.json") if (lv / f"{q}_lock.json").exists() else None
        score = read_json(lv / f"{q}_score.json") if (lv / f"{q}_score.json").exists() else None
        pred_p = root / "predictions" / f"{q}.json"
        pace_s = (f"; GD's guidance pace for the quarter was {f1(score['guidance_pace'])}"
                  if score and score.get("guidance_pace") is not None else "")
        if lock and pred_p.exists():
            p = read_json(pred_p)
            t = live.parse_now(lock["published_at"]).astimezone(live.ET)
            line = (f"- **{q}**: locked at {f1(p['nowcast']['total'])} (band {f1(p['band'][0])} to "
                    f"{f1(p['band'][1])}) from the {p['snapshot']} snapshot, as a {lock_words(cfg, lock['published_at'])} "
                    f"([`{lock['tag']}`]({REPO}/releases/tag/{lock['tag']})) at {t.strftime('%H:%M')} ET on "
                    f"{t.strftime('%Y-%m-%d')}, sha256 `{lock['sha256']}`.")
            if score and score.get("locked"):
                line += (f" GD reported {score['reported']['total']}{' on ' + rel if rel else ''}: the lock missed by "
                         f"{f1(score['ae_total'])} ({pct1(score['ape_pct'])}), "
                         f"{'inside' if score['inside_band'] else 'outside'} the band.")
                cmp_ = comparators(root, q, score, p)
                if cmp_:
                    line += (" Other misses for the quarter: "
                             + ", ".join(f"{lab} ({val}) by {miss}" for lab, val, miss in cmp_) + ".")
            elif rel:
                line += f" GD reports on {rel}."
        elif score:
            line = f"- **{q}**: no lock (the quarter missed its window). GD reported {score['reported']['total']}."
        else:
            lp = lv / f"{q}_latest.json"
            p = read_json(lp) if lp.exists() else read_json(lv / f"{q}_build.json")
            if p["snapshot"] < p["window_end"]:
                # The quarter is still open: its count so far is not an estimate of the quarter.
                line = (f"- **{q}**: not locked yet. Its window runs to {p['window_end']}, so the {p['snapshot']} "
                        "snapshot counts only part of it and no estimate is shown yet.")
            else:
                line = (f"- **{q}**: not locked yet. The latest estimate is {f1(p['nowcast']['total'])} (band "
                        f"{f1(p['band'][0])} to {f1(p['band'][1])}) from the {p['snapshot']} snapshot{pace_s}.")
            line += (f" It locks on {eve_of(rel)}, the day before GD reports on {rel}." if rel else
                     " No release date is set in `config/calendar.json` yet, so no lock is scheduled.")
        out.append(line)
    return "\n".join(out) if out else "No live quarter yet."


def eve_of(rel):
    return (live.dt.date.fromisoformat(rel) - live.dt.timedelta(days=1)).isoformat()


def replace_section(md, head, body):
    pat = re.compile(rf"^{re.escape(head)}[ \t]*\n.*?(?=^## |\Z)", re.M | re.S)
    if not pat.search(md):
        raise SystemExit(f"README.md has no {head} section")
    return pat.sub(lambda m: f"{head}\n\n{body.strip()}\n\n", md, count=1)


POST_MAX = 1300


def replace_block(md, start, end, body):
    """Replace the text between two marker lines, keeping the markers."""
    pat = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.S)
    if not pat.search(md):
        raise SystemExit(f"README.md has no {start} ... {end} block")
    return pat.sub(lambda m: f"{start}\n{body.strip()}\n{end}", md, count=1)


def low_line(m):
    """A sentence naming a simple baseline that missed by less than the registry estimate, if one did."""
    h = m["holdout"]
    low = min(("seasonal", "last"), key=lambda b: h["mae"][b])
    if h["mae"][low] < h["mae"]["ratio"]:
        return f" Simply repeating {BASE[low]} missed by less on average, {f1(h['mae'][low])}."
    return ""


def post(root):
    """docs/LINKEDIN_POST.md. The first two lines carry the live result and what the project is; the post names the
    baseline that beat the model, says the backtest reads a finished registry, and ends with one disclaimer line."""
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    h = m["holdout"]
    scores = live.scores(root)
    ls = locked_scores(root)
    what = ("I built a tracker that scales FAA aircraft registrations into an estimate of the Gulfstream jets General "
            "Dynamics (GD) reports each quarter, and locks it on GitHub the day before GD reports.")
    lines = []
    if ls:
        q, s, p, lock = ls[-1]
        cmp_ = comparators(root, q, s, p)
        pace = next((c for c in cmp_ if c[0] == "GD's guidance pace"), None)
        yago = next((c for c in cmp_ if c[0] == "the same quarter last year"), None)
        band = "inside" if s["inside_band"] else "outside"
        if len(ls) == 1:
            verb = "missed" if not s["inside_band"] else "landed inside its band"
            lines.append(f"My first locked estimate of Gulfstream deliveries {verb}: I said "
                         f"{f1(s['nowcast']['total'])} for {q}, General Dynamics reported {s['reported']['total']}.")
        else:
            hits = sum(1 for _, x, _, _ in ls if x["inside_band"])
            avg = sum(x["ae_total"] for _, x, _, _ in ls) / len(ls)
            lines.append(f"{len(ls)} locked estimates of Gulfstream deliveries so far: off by {f1(avg)} jets on "
                         f"average, {hits} of {len(ls)} inside the band. The latest, {q}: I said "
                         f"{f1(s['nowcast']['total'])}, General Dynamics reported {s['reported']['total']}.")
        lines += [what, ""]
        detail = (f"The {q} miss was {f1(s['ae_total'])} jets ({pct1(s['ape_pct'])}), {band} my band of past "
                  "misses.")
        if pace and yago:
            detail += (f" A pace I derived from GD's own full-year outlook missed by {pace[2]}, and last year's same "
                       f"quarter ({yago[1]}) by {yago[2]}.")
        if lock_words(read_json(root / "config/calendar.json"), lock["published_at"]) == PRIVATE:
            detail += " The repository was private then; the timestamp is GitHub's."
        lines += [detail, ""]
    elif scores:
        q = sorted(scores, key=qidx)[0]
        lines += [f"My Gulfstream delivery tracker's first live test, {q}, missed its lock window, so there is no locked "
                  "estimate to score yet.", what, ""]
    else:
        lines += ["How closely do FAA aircraft registrations track the Gulfstream deliveries General Dynamics reports?",
                  what, ""]
    one = (" One quarter is one data point." if len(ls) == 1 else "")
    lines += ["The backtest, on quarters held out from setting the rules: "
              + headline(m) + low_line(m) + " That test reads a registry copy that had years to fill in, so only "
              "locked quarters show whether it counts jets in time." + one, "",
              f"Dashboard: {DASH}", f"Code and data: {REPO}", "",
              DISCLAIMER, "",
              "#EquityResearch #Aerospace"]
    return "\n".join(lines) + "\n"


def run(root="."):
    root = Path(root)
    readme = root / "README.md"
    if readme.exists():
        md = readme.read_text()
        md = replace_section(md, "## Results", results(root))
        md = replace_section(md, "## Error analysis", error_analysis(root))
        md = replace_section(md, "## Live record", live_record(root))
        md = replace_block(md, *SUMMARY_MARKS, live_summary(root))
        write_text(readme, md)
        print("README.md: live summary, Results, Error analysis and Live record rewritten")
    else:
        print("skip README: no README.md yet")
    p = post(root)
    if len(p) > POST_MAX:
        raise SystemExit(f"LinkedIn post is {len(p)} characters, over {POST_MAX}")
    write_text(root / "docs/LINKEDIN_POST.md", p)
    print(f"docs/LINKEDIN_POST.md: {len(p)} characters")
    return 0
