"""P2.2: compare every figure in the independent recompute with the repository's own.

    .venv/bin/python tools/prepub/recompute_diff.py > docs/prepub/RECOMPUTE_DIFF.md

The recompute file (docs/prepub/reviews/recompute.txt) prints 6 decimals, so a figure matches when the
repository's value, printed to 6 decimals, is the same text. Every public surface shows fewer decimals than that.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
rec = {}
for ln in (ROOT / "docs/prepub/reviews/recompute.txt").read_text().splitlines():
    m = re.match(r"^([A-Za-z0-9_.\-/]+) = (.*)$", ln)
    if m:
        rec[m.group(1)] = m.group(2).strip()

M = json.loads((ROOT / "results/metrics.json").read_text())
H, D = M["holdout"], M["design"]
score = json.loads((ROOT / "results/live/2026Q3_score.json").read_text())
pred = json.loads((ROOT / "predictions/2026Q3.json").read_text())
bt = {}
for name in ("design", "holdout"):
    for r in csv.DictReader((ROOT / f"results/{name}.csv").open()):
        bt[(r["quarter"], r["definition"], r["model"])] = r
gd = {r["quarter"]: r for r in csv.DictReader((ROOT / "data/processed/gd_deliveries.csv").open())}
reg = {r["quarter"]: r for r in csv.DictReader((ROOT / "data/processed/registry_quarterly.csv").open())}


def q_range(a, b):
    def idx(q):
        return int(q[:4]) * 4 + int(q[5]) - 1
    return [f"{i // 4}Q{i % 4 + 1}" for i in range(idx(a), idx(b) + 1)]


HOLD = q_range("2020Q1", "2026Q2")
pairs = []   # (group, label, recomputed text, repository value)


def add(group, key, repo):
    if key in rec:
        pairs.append((group, key, rec[key], repo))
    else:
        pairs.append((group, key, None, repo))


# 1. ratio per quarter (the repository holds E1 for 2017Q1 to 2026Q2 and E2 for the design window)
for (q, d, mod), r in bt.items():
    if mod == "ratio":
        for c in ("large", "mid", "total"):
            add("1 ratio estimate per quarter", f"ratio.{d}.{q}.{c}", float(r[c]))
# 2. design
add("2 design window", "design.n", D["n"])
add("2 design window", "design.mae.seasonal", D["mae"]["none"]["seasonal"])
add("2 design window", "design.mae.last", D["mae"]["none"]["last"])
for e in ("E1", "E2"):
    for mod in ("raw", "ratio"):
        add("2 design window", f"design.mae.{mod}.{e}", D["mae"][e][mod])
add("2 design window", "design.chosen_definition", M["definition"])
# 3. holdout summary
add("3 held-out summary", "holdout.n", H["n"])
for mod in ("ratio", "raw", "guidance", "seasonal", "last"):
    add("3 held-out summary", f"holdout.mae.{mod}", H["mae"][mod])
    add("3 held-out summary", f"holdout.mape_pct.{mod}", H["mape"][mod])
    add("3 held-out summary", f"holdout.bias.{mod}", H["bias"][mod])
    add("3 held-out summary", f"holdout.mae_large.{mod}", H["mae_large"][mod])
    add("3 held-out summary", f"holdout.mae_mid.{mod}", H["mae_mid"][mod])
    add("3 held-out summary", f"holdout.mae_ex_2020.{mod}", H["mae_ex_2020"][mod])
# 4. by year (the README prints these from results/holdout.csv)
for y in range(2020, 2027):
    for mod in ("ratio", "raw", "guidance", "seasonal", "last"):
        xs = [float(r["ae"]) for (q, d, m_), r in bt.items() if m_ == mod and q.startswith(str(y)) and q in HOLD
              and d in ("none", M["definition"])]
        add("4 held-out MAE by year", f"holdout.year.{y}.mae.{mod}", sum(xs) / len(xs))
# 5. tests
for b in ("guidance", "seasonal", "last"):
    t = H["tests"][b]
    for k in ("wins", "losses", "ties", "p_one_sided"):
        add("5 sign tests and Holm", f"tests.{b}.{k}", t[k])
    add("5 sign tests and Holm", f"tests.{b}.holm_reject", "true" if t["holm_reject"] else "false")
    for cand in (f"rel_mae.{b}", f"tests.{b}.rel_mae", f"relative_mae.{b}", f"tests.{b}.relative_mae"):
        if cand in rec:
            add("5 sign tests and Holm", cand, H["rel_mae"][b])
# 6. autocorrelation
for b in ("guidance", "seasonal", "last"):
    add("6 lag-1 autocorrelation", f"autocorr_lag1.{b}", H["autocorr_lag1"][b])
# 7. guidance pace
for q in HOLD:
    r = bt[(q, "none", "guidance")]
    for c in ("large", "mid", "total"):
        add("7 guidance pace per quarter", f"guidance.{q}.{c}", float(r[c]))
add("7 guidance pace per quarter", "guidance.2026Q3.total", score["guidance_pace"])
add("7 guidance pace per quarter", "guidance.sourced_quarters", H["guidance"]["sourced"])
add("7 guidance pace per quarter", "guidance.fallback_quarters", ",".join(H["guidance"]["fallback_quarters"]))
add("7 guidance pace per quarter", "guidance.mae_sourced.guidance", H["guidance"]["mae_sourced"])
src_q = [q for q in HOLD if q not in H["guidance"]["fallback_quarters"]]
for mod, d in (("ratio", M["definition"]), ("seasonal", "none")):
    add("7 guidance pace per quarter", f"guidance.mae_sourced.{mod}",
        sum(float(bt[(q, d, mod)]["ae"]) for q in src_q) / len(src_q))
# 8. band
for r in H["band"]["by_quarter"]:
    add("8 past-miss band", f"band.{r['quarter']}.low", r["low"])
    add("8 past-miss band", f"band.{r['quarter']}.high", r["high"])
    add("8 past-miss band", f"band.{r['quarter']}.hit", "hit" if r["hit"] else "miss")
add("8 past-miss band", "band.hits", H["band"]["hits"])
add("8 past-miss band", "band.n", H["band"]["n"])
add("8 past-miss band", "band.coverage_pct", H["band"]["coverage_pct"])
add("8 past-miss band", "band.cp95_low_pct", H["band"]["cp95_pct"][0])
add("8 past-miss band", "band.cp95_high_pct", H["band"]["cp95_pct"][1])
for q, e in zip(q_range("2017Q1", "2026Q2"), M["band_errors"]):
    add("8 past-miss band", f"band_errors.{q}", e)
# 9. deliveries per registry event
for q, v in H["coverage_ratio"]["by_quarter"].items():
    add("9 deliveries per registry event", f"coverage_ratio.{q}", v)
add("9 deliveries per registry event", "coverage_ratio.mean", H["coverage_ratio"]["mean"])
add("9 deliveries per registry event", "coverage_ratio.sd_sample", H["coverage_ratio"]["sd"])
add("9 deliveries per registry event", "coverage_ratio.flags_above_mean_plus_2sd",
    ",".join(H["coverage_ratio"]["flags"]) or "none")
e = M["definition"].lower()
for y in range(2016, 2027):
    qs = [q for q in gd if q.startswith(str(y))]
    ev = sum(int(reg[q][f"{e}_large"]) + int(reg[q][f"{e}_mid"]) for q in qs)
    add("9 deliveries per registry event", f"events_per_delivery.{y}.total", ev / sum(int(gd[q]["total"]) for q in qs))
    add("9 deliveries per registry event", f"events_per_delivery.{y}.mid",
        sum(int(reg[q][f"{e}_mid"]) for q in qs) / sum(int(gd[q]["mid"]) for q in qs))
# 10. five largest misses (quarter order and estimate)
top = sorted(HOLD, key=lambda q: -float(bt[(q, M["definition"], "ratio")]["ae"]))[:5]
for i, q in enumerate(top, start=1):
    r = bt[(q, M["definition"], "ratio")]
    got = rec.get(f"top_miss.{i}", "")
    mm = re.match(r"(\d{4}Q\d) estimate=([\d.]+)", got)
    pairs.append(("10 five largest misses", f"top_miss.{i} quarter", mm.group(1) if mm else None, q))
    pairs.append(("10 five largest misses", f"top_miss.{i} estimate", mm.group(2) if mm else None, float(r["total"])))
# 11. the 2026Q3 score
add("11 the 2026Q3 score", "score.reported.total", score["reported"]["total"])
add("11 the 2026Q3 score", "score.reported.large", score["reported"]["large"])
add("11 the 2026Q3 score", "score.reported.mid", score["reported"]["mid"])
add("11 the 2026Q3 score", "score.locked.total", score["nowcast"]["total"])
add("11 the 2026Q3 score", "score.locked.large", score["nowcast"]["large"])
add("11 the 2026Q3 score", "score.locked.mid", score["nowcast"]["mid"])
add("11 the 2026Q3 score", "score.ae_total", score["ae_total"])
add("11 the 2026Q3 score", "score.ape_pct", score["ape_pct"])
add("11 the 2026Q3 score", "score.inside_band", "true" if score["inside_band"] else "false")
add("11 the 2026Q3 score", "score.band_low", pred["band"][0])
add("11 the 2026Q3 score", "score.band_high", pred["band"][1])
add("11 the 2026Q3 score", "score.prediction_sha256", json.loads((ROOT / "results/live/2026Q3_lock.json").read_text())["sha256"])
for cand, repo in (("score.guidance_pace", score["guidance_pace"]), ("score.guidance_pace.total", score["guidance_pace"]),
                   ("score.guidance_ae", score["guidance_ae"]), ("score.guidance_pace.abs_error", score["guidance_ae"])):
    if cand in rec:
        add("11 the 2026Q3 score", cand, repo)
# 12. GD averages
add("12 GD averages", "gd.mean_quarterly_deliveries_2020Q1_2026Q2", sum(int(gd[q]["total"]) for q in HOLD) / len(HOLD))
add("12 GD averages", "gd.2025Q3.total", int(gd["2025Q3"]["total"]))
# 16. truncation (an extra the recompute ran from its own airframe table)
for d in ("0", "30", "60", "90"):
    add("16 truncation table (extra)", f"b16.truncation_mae.{d}", H["truncation_mae"][d])


def same(got, repo):
    if got is None:
        return None
    if isinstance(repo, str):
        return got.split()[0] == repo or got == repo
    if isinstance(repo, bool):
        return got == ("true" if repo else "false")
    try:
        return f"{float(got.split()[0]):.6f}" == f"{float(repo):.6f}"
    except ValueError:
        return False


groups, bad, missing = {}, [], []
for g, key, got, repo in pairs:
    ok = same(got, repo)
    n, good = groups.get(g, (0, 0))
    groups[g] = (n + (ok is not None), good + bool(ok))
    if ok is False:
        bad.append((g, key, got, repo))
    elif ok is None:
        missing.append((g, key, repo))

print("# Recompute against the repository (P2.2)\n")
print("The independent recompute is `docs/prepub/reviews/recompute.txt`, written by a subagent that read only the "
      "processed inputs, the stored registry subsets, the locked prediction, the preregistration and the README's "
      "Method text. It is copied here unchanged. This file is written by `tools/prepub/recompute_diff.py`.\n")
print("A figure is `match` when the repository's value, printed to 6 decimals, equals the recomputed text. Every "
      "public surface shows at most 3 decimals, so a match at 6 is a match at the displayed precision.\n")
print("| Figure group | Compared | Match | Result |")
print("|---|---|---|---|")
for g in sorted(groups, key=lambda s: int(s.split()[0])):
    n, good = groups[g]
    print(f"| {g} | {n} | {good} | {'match' if n == good else 'DIFFERENCE, see below'} |")
tot = sum(n for n, _ in groups.values())
print(f"\nTotal: {tot} figures compared, {sum(g for _, g in groups.values())} match, {len(bad)} differ.\n")
if bad:
    print("## Differences\n")
    for g, key, got, repo in bad:
        print(f"- `{key}`: recomputed `{got}`, repository `{repo}`")
print("\n## Repository figures the recompute file has no key for\n")
if missing:
    for g, key, repo in missing:
        print(f"- `{key}` ({g}): repository `{repo}`")
else:
    print("None.")
