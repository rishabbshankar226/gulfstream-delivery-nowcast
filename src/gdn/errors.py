"""results/error_analysis.md: the ratio model's five largest holdout misses, from the results files.

A cause appears only where a filing or GD's call states one. The statements below are GD's own words
about the quarter's deliveries, quoted from the cached release or transcript; none of them explains
the gap between the registry and GD's count, and the file says so."""
from pathlib import Path

from .files import read_csv, read_json, write_text

# quarter: [(source, where, quote)] — GD's statements about the quarter's deliveries.
STATEMENTS = {
    "2020Q2": [("GD's 2020Q2 earnings release", "accession 0000040533-20-000055",
                "The company delivered 32 aircraft during the quarter, up from 23 last quarter, despite continued "
                "pandemic-related challenges to making international deliveries.")],
    "2021Q2": [("GD's 2021-04-28 earnings call (Phebe Novakovic)",
                "https://www.fool.com/earnings/call-transcripts/2021/04/28/general-dynamics-gd-q1-2021-earnings-call-transcri/",
                "Looking forward, we expect the second quarter to be our most challenging from a delivery perspective.")],
}


def fmt(x):
    return f"{x:.1f}"


def run(root="."):
    root = Path(root)
    m = read_json(root / "results/metrics.json")
    chosen = m["definition"].lower()
    hold = [r for r in read_csv(root / "results/holdout.csv") if r["model"] == "ratio"]
    reg = {r["quarter"]: r for r in read_csv(root / "data/processed/registry_quarterly.csv")}
    rep = {r["quarter"]: r for r in read_csv(root / "data/processed/gd_deliveries.csv")}
    snap = read_json(root / "data/snapshots/MANIFEST.json")["backtest"]
    top = sorted(hold, key=lambda r: (-float(r["ae"]), r["quarter"]))[:5]
    lines = ["# Error analysis: the five largest held-out misses", "",
             f"The backtest reads a registry copy from {snap}, which had months or years to fill in. It shows how "
             "well the registry tracks Gulfstream deliveries after the fact. Only the locked quarters test whether "
             "it counts them in time.", "",
             f"Ratio model under {m['definition']}, the five held-out quarters with the largest absolute miss. "
             "Registry events are the airframes whose event date falls in the quarter's window.", "",
             "| Quarter | Estimate | GD reported | Signed error | Registry large | Registry mid | GD large | GD mid |",
             "|---|---|---|---|---|---|---|---|"]
    for r in top:
        q = r["quarter"]
        est, act = float(r["total"]), int(r["actual"])
        lines.append(f"| {q} | {fmt(est)} | {act} | {fmt(est - act)} | {reg[q][chosen + '_large']} | "
                     f"{reg[q][chosen + '_mid']} | {rep[q]['large']} | {rep[q]['mid']} |")
    lines.append("")
    for r in top:
        q = r["quarter"]
        est, act = float(r["total"]), int(r["actual"])
        n = int(reg[q][chosen + "_large"]) + int(reg[q][chosen + "_mid"])
        side = "above" if est > act else "below"
        lines.append(f"## {q}")
        lines.append("")
        lines.append(f"The registry counted {n} airframes in the window against {act} GD deliveries, and the "
                     f"estimate of {fmt(est)} came out {fmt(abs(est - act))} {side} GD's count "
                     f"(release accession {rep[q]['accn']}).")
        for src, where, quote in STATEMENTS.get(q, []):
            lines.append("")
            lines.append(f"What GD said about the quarter, in {src} ({where}): \"{quote}\"")
        lines.append("")
        lines.append("No filing or call states why the registry count differed from GD's count in this quarter, "
                     "so none is given here.")
        lines.append("")
    write_text(root / "results/error_analysis.md", "\n".join(lines).rstrip("\n") + "\n")
    print("results/error_analysis.md:", ", ".join(r["quarter"] for r in top))
    return 0
