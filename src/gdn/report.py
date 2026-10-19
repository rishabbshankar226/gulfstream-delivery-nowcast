"""README.md's ## Results, ## Error analysis and ## Live record, and docs/LINKEDIN_POST.md, from the results files.

Only the text between each of those headings and the next is replaced, so a second run changes nothing."""
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
        f"**{headline(m)}**", "",
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
              f"{f1(g['mae_sourced'])} aircraft on average.", "",
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
        "Average miss by cabin, aircraft:", "",
        md_table(["Model", "Large cabin", "Mid cabin"], crows), "",
        f"GD deliveries per registry event averaged {f2(cr['mean'])} from 2017Q1 to 2025Q2. "
        + "The preregistered flag looks for quarters from 2025Q3 to 2026Q2 above the mean plus two standard "
        "deviations, where the registry would be counting fewer events per delivery than usual"
        + (f"; it flags {', '.join(cr['flags'])}." if cr["flags"] else "; none is.") + drift, "",
        "The truncation test cuts each held-out quarter's own registry events a set number of days before the "
        "quarter ends, with its four lags left whole. It stands in, crudely, for a registry that has not finished "
        "posting:", "",
        md_table(["Days cut", "Average miss, aircraft"], [[d, f1(tr[d])] for d in ("0", "30", "60", "90")]), "",
        f"Five quarters drive much of the average: {', '.join(top[:-1])} and {top[-1]}. No filing or call states why "
        "the registry count differed from GD's count in any of them. The full write-up is in "
        "[results/error_analysis.md](results/error_analysis.md).", "",
        table,
    ]
    return "\n".join(lines)


def live_record(root):
    root = Path(root)
    cfg = read_json(root / "config/calendar.json")
    word = "public lock" if cfg.get("public") else "timestamped GitHub release"
    cal, Y, calls = Calendar.load(root), live.reported_history(root), model.load_guidance(root)
    lv = root / "results/live"
    qs = sorted({p.name[:6] for p in lv.glob("*_build.json")} | {p.name[:6] for p in lv.glob("*_latest.json")}
                | {p.name[:6] for p in (root / "predictions").glob("*.json")}, key=qidx)
    out = []
    for q in qs:
        rel = cfg.get("releases", {}).get(q)
        lock = read_json(lv / f"{q}_lock.json") if (lv / f"{q}_lock.json").exists() else None
        score = read_json(lv / f"{q}_score.json") if (lv / f"{q}_score.json").exists() else None
        pred_p = root / "predictions" / f"{q}.json"
        pace = model.guidance_pace(q, Y, calls, cal)
        pace_s = (f"; GD's guidance pace for the quarter was {f1(score['guidance_pace'])}"
                  if score and score.get("guidance_pace") is not None else "")
        if lock and pred_p.exists():
            p = read_json(pred_p)
            t = live.parse_now(lock["published_at"]).astimezone(live.ET)
            line = (f"- **{q}**: locked at {f1(p['nowcast']['total'])} (band {f1(p['band'][0])} to "
                    f"{f1(p['band'][1])}) from the {p['snapshot']} snapshot, as a {word} "
                    f"([`{lock['tag']}`]({REPO}/releases/tag/{lock['tag']})) at {t.strftime('%H:%M')} ET on "
                    f"{t.strftime('%Y-%m-%d')}, sha256 `{lock['sha256']}`{pace_s}.")
            if score:
                line += (f" GD reported {score['reported']['total']}: the lock missed by {f1(score['ae_total'])}"
                         f"{', inside' if score['inside_band'] else ', outside'} the band.")
            elif rel:
                line += f" GD reports on {rel}."
        elif score:
            line = f"- **{q}**: no lock (the quarter missed its window). GD reported {score['reported']['total']}."
        else:
            lp = lv / f"{q}_latest.json"
            p = read_json(lp) if lp.exists() else read_json(lv / f"{q}_build.json")
            line = (f"- **{q}**: not locked yet. The latest estimate is {f1(p['nowcast']['total'])} (band "
                    f"{f1(p['band'][0])} to {f1(p['band'][1])}) from the {p['snapshot']} snapshot{pace_s}."
                    + (f" It locks on {eve_of(rel)}, the day before GD reports on {rel}." if rel else ""))
        out.append(line)
    return "\n".join(out) if out else "No live quarter yet."


def eve_of(rel):
    return (live.dt.date.fromisoformat(rel) - live.dt.timedelta(days=1)).isoformat()


def replace_section(md, head, body):
    pat = re.compile(rf"^{re.escape(head)}[ \t]*\n.*?(?=^## |\Z)", re.M | re.S)
    if not pat.search(md):
        raise SystemExit(f"README.md has no {head} section")
    return pat.sub(lambda m: f"{head}\n\n{body.strip()}\n\n", md, count=1)


def low_line(m):
    """A sentence naming a simple baseline that missed by less than the registry estimate, if one did."""
    h = m["holdout"]
    low = min(("seasonal", "last"), key=lambda b: h["mae"][b])
    if h["mae"][low] < h["mae"]["ratio"]:
        return f" Simply repeating {BASE[low]} missed by less on average, {f1(h['mae'][low])}."
    return ""


def post(root):
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    h = m["holdout"]
    cfg = read_json(root / "config/calendar.json")
    scores = live.scores(root)
    locked = {q: s for q, s in scores.items() if s.get("locked")}
    lines = []
    if locked:
        q = sorted(locked, key=qidx)[-1]
        s = locked[q]
        n = len(locked)
        lines.append(f"{'One locked quarter' if n == 1 else f'{n} locked quarters'} so far: off by "
                     f"{f1(s['ae_total'])}. I locked an estimate of {f1(s['nowcast']['total'])} Gulfstream deliveries "
                     f"for {q} on GitHub before GD reported, and GD reported {s['reported']['total']}. One quarter "
                     "shows how it works live, not whether it works.")
    else:
        rel = cfg.get("releases", {}).get("2026Q3")
        lines.append("How closely do FAA aircraft registrations track the Gulfstream deliveries General Dynamics "
                     "reports? I built a tracker to find out. Its first real test comes on " + (rel or "the next release")
                     + ", when GD reports 2026Q3 and I score the estimate I lock on GitHub the day before.")
    lines += ["",
              "How I tested it: I counted each Gulfstream jet's first customer registration or export in a registry "
              "copy, scaled the count by the last four quarters, and checked it on 26 past quarters held out from setting "
              "the rules, "
              "against GD's own guidance pace and two simple baselines.", "",
              headline(m) + low_line(m) + " That test reads a registry that had years to fill in, so only the "
              "locked quarters show whether it counts jets in time.", "",
              f"Dashboard: {DASH}", f"Code, data and the research note: {REPO}", "",
              "What public data would you add to sharpen a delivery estimate like this?", "",
              "#GeneralDynamics #EquityResearch #Python"]
    return "\n".join(lines) + "\n"


def run(root="."):
    root = Path(root)
    readme = root / "README.md"
    if readme.exists():
        md = readme.read_text()
        md = replace_section(md, "## Results", results(root))
        md = replace_section(md, "## Error analysis", error_analysis(root))
        md = replace_section(md, "## Live record", live_record(root))
        write_text(readme, md)
        print("README.md: Results, Error analysis and Live record rewritten")
    else:
        print("skip README: no README.md yet")
    p = post(root)
    if len(p) > 1500:
        raise SystemExit(f"LinkedIn post is {len(p)} characters, over 1,500")
    write_text(root / "docs/LINKEDIN_POST.md", p)
    print(f"docs/LINKEDIN_POST.md: {len(p)} characters")
    return 0
