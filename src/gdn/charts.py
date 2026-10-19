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
         "guidance": "GD guidance pace", "seasonal": "Same quarter last year", "last": "Last quarter"}
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


def _finish(fig, ax, title, ylabel, snap, xlabel="Fiscal quarter"):
    fig.text(0.075, 0.935, title, fontsize=22, fontweight="bold", va="center")
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.yaxis.grid(True, color=GRID, lw=1)
    ax.set_axisbelow(True)
    fig.text(0.075, 0.025, SOURCE.format(snap=snap), fontsize=13, color=MUTED)


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


def track_record(root, snap):
    rep = {r["quarter"]: int(r["total"]) for r in read_csv(Path(root) / "data/processed/gd_deliveries.csv")}
    s = series(root)
    fig, ax = _fig()
    ax.axvspan(QS.index("2017Q1") - 0.5, QS.index("2019Q4") + 0.5, color="#423e38", alpha=0.07, lw=0)
    ax.text(QS.index("2017Q1") - 0.3, 3, "Design window", fontsize=15, color=MUTED)
    ax.text(QS.index("2020Q1") + 0.2, 3, "Held-out quarters", fontsize=15, color=MUTED)
    for m in ("last", "seasonal", "guidance", "raw", "ratio"):
        xs = [QS.index(q) for q in QS if q in s[m]]
        ax.plot(xs, [s[m][QS[i]] for i in xs], label=NAMES[m], **STYLE[m])
    ax.plot(range(len(QS)), [rep[q] for q in QS], label=NAMES["reported"], **STYLE["reported"])
    _quarter_axis(ax, QS)
    ax.set_ylim(0, max(max(rep.values()), max(max(v.values()) for v in s.values())) * 1.12)
    h, lab = ax.get_legend_handles_labels()
    order = [lab.index(NAMES[m]) for m in ("reported", "ratio", "raw", "guidance", "seasonal", "last")]
    ax.legend([h[i] for i in order], [lab[i] for i in order], loc="lower left", bbox_to_anchor=(0, 1.0),
              ncol=3, frameon=False, handlelength=3.2)
    _finish(fig, ax, "Gulfstream deliveries by quarter: GD's count against five estimates",
            "Aircraft delivered per quarter", snap)
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
    p = paths[-1]
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
        ax.axhline(pace["total"], color=GREY_D, lw=2, ls=(0, (9, 3, 2, 3)), label="GD guidance pace for the quarter")
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
        ax.text(dt.date.fromisoformat(rel), 2, f" GD reports {rel}", fontsize=15, color=MUTED, ha="right")
    ax.set_xlim(left, right)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    top = max([x + above for x in tot] + ([pace["total"]] if pace else []))
    ax.set_ylim(0, top * 1.2)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, ncol=3)
    _finish(fig, ax, f"The {q} estimate by registry snapshot date", "Estimated deliveries (aircraft)", snap,
            "Snapshot date")
    _save(fig, root, "nowcast_path.png")


def run(root="."):
    snap = read_json(Path(root) / "data/snapshots/MANIFEST.json")["backtest"]
    track_record(root, snap)
    coverage(root, snap)
    signed_errors(root, snap)
    nowcast_path(root, snap)
    return 0
