"""output/charts/*.png at 1600 x 900: one style per model throughout, axis titles with units, a source line.

Colours are the backlog dashboard's: one ink, one blue accent, warm greys. Models other than ratio
are told apart by dash pattern as well as tone, and every chart carries a legend."""
import csv
import datetime as dt
import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import stats  # noqa: E402
from .fiscal import qidx, qrange  # noqa: E402
from .files import read_csv, read_json  # noqa: E402

INK, ACCENT, ACCENT_2 = "#1c1a17", "#1d3f6e", "#6d8db8"
GREY_D, GREY_M, GREY_L = "#47423c", "#77716a", "#a39c90"
GRID, AXIS, PAPER, MUTED = "#e3e0da", "#847e74", "#ffffff", "#5f5a52"
STYLE = {
    "reported": dict(color=INK, lw=3.4, ls="-"),
    "ratio": dict(color=ACCENT, lw=2.6, ls="-"),
    "raw": dict(color=ACCENT_2, lw=2.0, ls=(0, (6, 3))),
    "guidance": dict(color=GREY_D, lw=2.0, ls=(0, (9, 3, 2, 3))),
    "seasonal": dict(color=GREY_M, lw=2.0, ls=(0, (4, 3))),
    "last": dict(color=GREY_L, lw=2.2, ls=(0, (1.5, 2.5))),
}
NAMES = {"reported": "GD reported", "ratio": "Registry estimate (ratio)", "raw": "Raw registry count",
         "guidance": "Pace built from GD's outlook", "seasonal": "Same quarter last year", "last": "Last quarter"}
QS = qrange("2016Q1", "2026Q2")
SOURCE = ("Source: GD earnings releases on SEC EDGAR; FAA aircraft registry snapshot {snap}; GD earnings calls; "
          "author's calculations. Rishabb Shankar, rshankar.dev")

plt.rcParams.update({
    "font.size": 17, "axes.titlesize": 22, "axes.labelsize": 17, "legend.fontsize": 15,
    "xtick.labelsize": 15, "ytick.labelsize": 15, "axes.edgecolor": AXIS, "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "svg.hashsalt": "gdn", "path.simplify": False,
})


def _fig():
    fig = plt.figure(figsize=(16, 9), dpi=100)
    return fig, fig.add_axes([0.075, 0.15, 0.9, 0.66])


def _finish(fig, ax, title, ylabel, snap, xlabel="Fiscal quarter", source=None):
    fig.text(0.075, 0.935, title, fontsize=22, fontweight="bold", va="center")
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.yaxis.grid(True, color=GRID, lw=1)
    ax.set_axisbelow(True)
    fig.text(0.075, 0.025, source or SOURCE.format(snap=snap), fontsize=13, color=MUTED)


def _quarter_axis(ax, qs):
    ticks = [i for i, q in enumerate(qs) if q.endswith("Q1")]
    ax.set_xticks(ticks, [qs[i][:4] for i in ticks])
    ax.set_xlim(-0.6, len(qs) - 0.4)


def _save(fig, root, name):
    p = Path(root) / "output/charts" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, metadata={"Software": None})
    plt.close(fig)
    data = buf.getvalue()
    if not p.exists() or p.read_bytes() != data:
        p.write_bytes(data)
    print(f"wrote {p.relative_to(root)}")


def series(root):
    """{model: {quarter: total}} from design.csv and holdout.csv under the chosen definition."""
    chosen = read_json(Path(root) / "results/metrics.json")["definition"]
    out = {m: {} for m in ("ratio", "raw", "guidance", "seasonal", "last")}
    for f in ("results/design.csv", "results/holdout.csv"):
        for r in read_csv(Path(root) / f):
            if r["definition"] in ("none", chosen):
                out[r["model"]][r["quarter"]] = float(r["total"])
    return out


LOCKED = "Locked, with band"


def locked_points(root):
    """F117. [(quarter, locked estimate, (band low, band high), GD's count)] for each quarter that was locked and then
    scored, in order. The track chart draws them after the backtest, so the image a reader sees first shows the live
    record too. A quarter that missed its lock window, or is locked but not yet scored, has no point."""
    from . import live
    root = Path(root)
    out = []
    for q, s in sorted(live.scores(root).items(), key=lambda kv: qidx(kv[0])):
        p = root / "predictions" / f"{q}.json"
        if s.get("locked") and s.get("nowcast") and p.exists() and qidx(q) > qidx(QS[-1]):
            lo, hi = read_json(p)["band"]
            out.append((q, s["nowcast"]["total"], (lo, hi), s["reported"]["total"]))
    return out


def track_quarters(root):
    """The track chart's x axis: the backtest quarters, then every quarter through the last scored lock."""
    pts = locked_points(root)
    return QS + (qrange(QS[-1], pts[-1][0])[1:] if pts else [])


def track_record(root, snap):
    rep = {r["quarter"]: int(r["total"]) for r in read_csv(Path(root) / "data/processed/gd_deliveries.csv")}
    pts = locked_points(root)
    qs = track_quarters(root)
    rep.update({q: n for q, _, _, n in pts})
    s = series(root)
    fig, ax = _fig()
    ax.axvspan(QS.index("2017Q1") - 0.5, QS.index("2019Q4") + 0.5, color="#423e38", alpha=0.07, lw=0)
    ax.text(QS.index("2017Q1") - 0.3, 3, "Design window", fontsize=15, color=MUTED)
    ax.text(QS.index("2020Q1") + 0.2, 3, "Held-out quarters", fontsize=15, color=MUTED)
    for m in ("last", "seasonal", "guidance", "raw", "ratio"):
        xs = [QS.index(q) for q in QS if q in s[m]]
        ax.plot(xs, [s[m][QS[i]] for i in xs], label=NAMES[m], **STYLE[m])
    xr = [i for i, q in enumerate(qs) if q in rep]
    ax.plot(xr, [rep[qs[i]] for i in xr], label=NAMES["reported"], **STYLE["reported"])
    top = max(max(rep.values()), max(max(v.values()) for v in s.values()))
    if pts:
        ax.axvspan(len(QS) - 0.5, len(qs) - 0.5, color=ACCENT, alpha=0.08, lw=0)
        ax.text(len(qs) - 0.55, 3, "Locked", fontsize=15, color=MUTED, ha="right")
        for i, (q, est, (lo, hi), _) in enumerate(pts):
            ax.errorbar([qs.index(q)], [est], yerr=[[est - lo], [hi - est]], fmt="D", color=ACCENT, ms=12,
                        capsize=7, lw=2.4, mfc=ACCENT, mec=INK, label=LOCKED if i == 0 else None, zorder=5)
        top = max(top, max(hi for _, _, (_, hi), _ in pts))
    _quarter_axis(ax, qs)
    ax.set_ylim(0, top * 1.12)
    h, lab = ax.get_legend_handles_labels()
    keys = ("reported", "ratio", "raw", "guidance", "seasonal", "last")
    order = [lab.index(NAMES[m]) for m in keys] + ([lab.index(LOCKED)] if pts else [])
    ax.legend([h[i] for i in order], [lab[i] for i in order], loc="lower left", bbox_to_anchor=(0, 1.0),
              ncol=4 if pts else 3, frameon=False, handlelength=3.2 if not pts else 2.6,
              columnspacing=2.0 if not pts else 1.2)
    title = ("GD's Gulfstream deliveries against five backtest estimates and the live lock" if pts
             else "Gulfstream deliveries by quarter: GD's count against five estimates")
    _finish(fig, ax, title, "Aircraft delivered per quarter", snap)
    _save(fig, root, "track_record.png")


def coverage(root, snap):
    m = read_json(Path(root) / "results/metrics.json")
    cr = m["holdout"]["coverage_ratio"]
    by = cr["by_quarter"]
    fig, ax = _fig()
    xs = [QS.index(q) for q in QS if q in by]
    ax.plot(xs, [by[QS[i]] for i in xs], color=ACCENT, lw=2.6, marker="o", ms=7, label="GD deliveries / registry events")
    ax.axhline(cr["mean"], color=GREY_M, lw=2, ls=(0, (6, 3)), label=f"Mean, 2017Q1 to 2025Q2")
    ax.axhline(cr["mean"] + 2 * cr["sd"], color=GREY_D, lw=2, ls=(0, (1.5, 2.5)), label="Mean plus two standard deviations")
    for q in cr["flags"]:
        ax.plot([QS.index(q)], [by[q]], marker="o", ms=14, mfc="none", mec=INK, mew=2)
    _quarter_axis(ax, QS)
    ax.set_ylim(0, max(by.values()) * 1.25)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, ncol=3, handlelength=3.2)
    _finish(fig, ax, "How many GD deliveries each registry event stands for, by quarter",
            "GD deliveries per registry event (ratio)", snap)
    _save(fig, root, "coverage.png")


def signed_errors(root, snap):
    m = read_json(Path(root) / "results/metrics.json")
    qs = qrange("2017Q1", "2026Q2")
    errs = m["band_errors"]
    band = {b["quarter"]: b for b in m["holdout"]["band"]["by_quarter"]}
    ratio = series(root)["ratio"]
    fig, ax = _fig()
    lo_band, hi_band, xb = [], [], []
    for i, q in enumerate(qs):
        if q in band:
            xb.append(i)
            lo_band.append(ratio[q] - band[q]["high"])       # P10 in error space
            hi_band.append(ratio[q] - band[q]["low"])        # P90 in error space
    ax.fill_between(xb, lo_band, hi_band, step="mid", color=ACCENT, alpha=0.13, lw=0,
                    label="Past-miss band (P10 to P90 of earlier misses)")
    colors = [GREY_M if qidx(q) <= qidx("2019Q4") else ACCENT for q in qs]
    ax.bar(range(len(qs)), errs, width=0.72, color=colors)
    from matplotlib.patches import Patch
    handles = [Patch(color=ACCENT, alpha=0.13, label="Past-miss band (P10 to P90 of earlier misses)"),
               Patch(color=GREY_M, label="Design window miss"), Patch(color=ACCENT, label="Held-out miss")]
    ax.axhline(0, color=INK, lw=1.4)
    ticks = [i for i, q in enumerate(qs) if q.endswith("Q1")]
    ax.set_xticks(ticks, [qs[i][:4] for i in ticks])
    ax.set_xlim(-0.6, len(qs) - 0.4)
    top = max(abs(min(errs + lo_band)), max(errs + hi_band)) * 1.2
    ax.set_ylim(-top, top)
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, ncol=3)
    _finish(fig, ax, "The registry estimate's miss by quarter, with the band built from earlier misses",
            "Estimate minus GD's count (aircraft)", snap)
    _save(fig, root, "signed_errors.png")


def featured_path(paths):
    """The newest quarter's path with a lock or a score, so a scored quarter stays up until the next one locks;
    else the newest. `paths` is in quarter order. site/app.js `current()` picks the same quarter."""
    for p in reversed(paths):
        q = p.name.split("_")[0]
        if (p.parent / f"{q}_lock.json").exists() or (p.parent / f"{q}_score.json").exists():
            return p
    return paths[-1]


def nowcast_path(root, snap):
    import matplotlib.dates as mdates
    from . import live, model
    from .fiscal import Calendar
    lv = Path(root) / "results/live"
    paths = sorted(lv.glob("*_path.csv"), key=lambda x: qidx(x.name[:6]))
    fig, ax = _fig()
    if not paths:
        ax.text(0.5, 0.5, "No live quarter yet", transform=ax.transAxes, ha="center")
        _finish(fig, ax, "The live estimate by snapshot date", "Estimated deliveries (aircraft)", snap, "Snapshot date")
        _save(fig, root, "nowcast_path.png")
        return
    p = featured_path(paths)
    q = p.name.split("_")[0]
    rows = read_csv(p)
    latest = read_json(lv / f"{q}_latest.json")
    below = latest["nowcast"]["total"] - latest["band"][0]
    above = latest["band"][1] - latest["nowcast"]["total"]
    dates = [dt.date.fromisoformat(r["date"]) for r in rows]
    tot = [float(r["nowcast_total"]) for r in rows]
    rel = live.config(root).get("releases", {}).get(q)
    if len(dates) > 1:
        ax.fill_between(dates, [x - below for x in tot], [x + above for x in tot], color=ACCENT, alpha=0.13, lw=0)
    ax.errorbar(dates, tot, yerr=[[below] * len(tot), [above] * len(tot)], color=ACCENT, lw=2.6, marker="o",
                ms=8, capsize=6, elinewidth=1.6, ecolor=ACCENT_2, label=f"{q} estimate, with its past-miss band")
    pace = model.guidance_pace(q, live.reported_history(root), model.load_guidance(root), Calendar.load(root))
    if pace:
        ax.axhline(pace["total"], color=GREY_D, lw=2, ls=(0, (9, 3, 2, 3)), label="Pace built from GD's outlook, for the quarter")
    pred_p = Path(root) / "predictions" / f"{q}.json"
    if (lv / f"{q}_lock.json").exists() and pred_p.exists():
        pr = read_json(pred_p)
        ax.plot([dt.date.fromisoformat(pr["snapshot"])], [pr["nowcast"]["total"]], marker="D", ms=14, color=INK,
                ls="none", label="Locked estimate")
    if (lv / f"{q}_score.json").exists():
        ax.axhline(read_json(lv / f"{q}_score.json")["reported"]["total"], color=INK, lw=3.2, label="GD reported")
    left = dates[0] - dt.timedelta(days=2)
    right = max(dates[-1], dt.date.fromisoformat(rel) if rel else dates[-1]) + dt.timedelta(days=2)
    if rel:
        ax.axvline(dt.date.fromisoformat(rel), color=AXIS, lw=1.4, ls=(0, (2, 2)))
        said = "GD reported" if (lv / f"{q}_score.json").exists() else "GD reports"
        ax.text(dt.date.fromisoformat(rel), 2, f" {said} {rel}", fontsize=15, color=MUTED, ha="right")
    ax.set_xlim(left, right)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    top = max([x + above for x in tot] + ([pace["total"]] if pace else []))
    ax.set_ylim(0, top * 1.2)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, ncol=3)
    # This chart plots one point per daily snapshot, so its source line names those, not the backtest snapshot.
    source = (f"Source: GD earnings releases (SEC); FAA registry snapshots {rows[0]['date']} to "
              f"{rows[-1]['date']}; GD earnings calls; author's calculations. Rishabb Shankar, rshankar.dev")
    _finish(fig, ax, f"The {q} estimate by registry snapshot date", "Estimated deliveries (aircraft)", snap,
            "Snapshot date", source=source)
    _save(fig, root, "nowcast_path.png")


CHARTS = ("track_record.png", "coverage.png", "signed_errors.png", "nowcast_path.png")
STAMP = "output/charts/inputs.sha256"


def input_digest(root):
    """One line per input the four charts read, so the daily job redraws them only when one changes (a lock, a
    score, a new path row for the featured quarter) and a PNG is not rewritten for nothing."""
    from .files import sha256
    root = Path(root)
    lv = root / "results/live"
    files = [root / "results/design.csv", root / "results/holdout.csv", root / "results/metrics.json",
             root / "data/processed/gd_deliveries.csv", root / "data/processed/registry_quarterly.csv",
             root / "data/guidance.csv", root / "config/calendar.json", root / "data/snapshots/MANIFEST.json"]
    paths = sorted(lv.glob("*_path.csv"), key=lambda x: qidx(x.name[:6]))
    if paths:
        q = featured_path(paths).name.split("_")[0]
        files += [lv / f"{q}_path.csv", lv / f"{q}_latest.json", lv / f"{q}_lock.json", lv / f"{q}_score.json",
                  root / "predictions" / f"{q}.json"]
    files += sorted(lv.glob("*_score.json"))
    files += [root / "predictions" / f"{p.name[:6]}.json" for p in sorted(lv.glob("*_score.json"))]
    lines = [f"{sha256(p.read_bytes())}  {p.relative_to(root)}" for p in dict.fromkeys(files) if p.exists()]
    lines.append(f"{sha256(Path(__file__).read_bytes())}  src/gdn/charts.py")
    return "\n".join(lines) + "\n"


PREVIEW = "site/preview.png"


def _preview(root):
    """The dashboard's link-preview image (og:image): a copy of the track-record chart, kept under site/ so Pages
    serves it and redrawn whenever the chart is."""
    src, dst = Path(root) / "output/charts/track_record.png", Path(root) / PREVIEW
    if src.exists() and (not dst.exists() or dst.read_bytes() != src.read_bytes()):
        dst.write_bytes(src.read_bytes())


def run(root=".", force=False):
    from .files import write_text
    root = Path(root)
    digest = input_digest(root)
    stamp = root / STAMP
    if not force and stamp.exists() and stamp.read_text() == digest and \
            all((root / "output/charts" / n).exists() for n in CHARTS):
        print("chart inputs unchanged; kept")
        _preview(root)
        return 0
    snap = read_json(root / "data/snapshots/MANIFEST.json")["backtest"]
    track_record(root, snap)
    coverage(root, snap)
    signed_errors(root, snap)
    nowcast_path(root, snap)
    write_text(stamp, digest)
    _preview(root)
    return 0
