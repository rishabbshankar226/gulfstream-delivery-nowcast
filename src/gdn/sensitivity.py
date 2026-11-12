"""results/exploratory/sensitivity.json and .md: the held-out comparison under other readings and windows.

Everything here was tried after the held-out results were seen, so by the preregistration it is exploratory and
changes no headline figure. It answers the questions a reader asks of the headline: what if GD's January 2021
statement is read as a number, what if 2020 is dropped, what if the years the guidance pace missed most are
dropped, and what the other event definition gives."""
from pathlib import Path

from . import model, stats
from .fiscal import HOLDOUT, Calendar, qrange
from .files import write_json, write_text

MODELS = ("ratio", "raw", "guidance", "seasonal", "last")
ALT_2021 = {"call_date": "2021-01-27", "year": 2021, "outlook": 117.0}   # "10 fewer aircraft" than 2020's 127


def _summary(ae, quarters):
    """MAE per model over a set of quarters, and the sign test of ratio against the guidance pace on them."""
    out = {"n": len(quarters), "mae": {m: sum(ae[q][m] for q in quarters) / len(quarters) for m in MODELS}}
    w, lo, t, p = stats.sign_test([ae[q]["guidance"] for q in quarters], [ae[q]["ratio"] for q in quarters])
    out["ratio_vs_guidance"] = {"wins": w, "losses": lo, "ties": t, "p_one_sided": p}
    w, lo, t, p = stats.sign_test([ae[q]["seasonal"] for q in quarters], [ae[q]["ratio"] for q in quarters])
    out["ratio_vs_seasonal"] = {"wins": w, "losses": lo, "ties": t, "p_one_sided": p}
    return out


def _ae(rows):
    out = {}
    for r in rows:
        out.setdefault(r["quarter"], {})[r["model"]] = r["ae"]
    return out


def compute(root="."):
    root = Path(root)
    Y, N = model.load_reported(root), model.load_registry(root)
    chosen = model.choose(model.design_rows(Y, N))[0]
    other = "E2" if chosen == "E1" else "E1"
    calls, cal = model.load_guidance(root), Calendar.load(root)
    qs = qrange(*HOLDOUT)
    base = _ae(model.holdout_rows(Y, N, chosen, calls, cal))
    alt_calls = [dict(c, outlook=ALT_2021["outlook"]) if c["call_date"] == ALT_2021["call_date"] else c for c in calls]
    alt = _ae(model.holdout_rows(Y, N, chosen, alt_calls, cal))
    e2 = _ae(model.holdout_rows(Y, N, other, calls, cal))
    sourced_alt = [q for q in qs if model.outlook_for(q, alt_calls, cal) is not None]
    variants = [
        ("preregistered", "The preregistered comparison: all 26 held-out quarters", base, qs),
        ("outlook_2021_as_117", "GD's January 2021 statement (\"10 fewer aircraft\" than 2020's 127) read as an "
                                "outlook of 117", alt, qs),
        ("without_2020", "Without the four quarters of 2020", base, [q for q in qs if not q.startswith("2020")]),
        ("without_2023_2024", "Without 2023 and 2024, the two years the guidance pace missed by most", base,
         [q for q in qs if q[:4] not in ("2023", "2024")]),
        ("without_2023Q1_2024Q1", "Without 2023Q1 to 2024Q1, the five quarters before G700 deliveries began", base,
         [q for q in qs if not ("2023Q1" <= q <= "2024Q1")]),
        ("only_2023_2024", "Only 2023 and 2024", base, [q for q in qs if q[:4] in ("2023", "2024")]),
        (f"definition_{other}", f"The other event definition, {other}, in place of {chosen}", e2, qs),
    ]
    out = {"note": "Exploratory: tried after the held-out results were seen. None of it changes the headline.",
           "chosen_definition": chosen, "sourced_quarters_with_2021_as_117": len(sourced_alt), "variants": []}
    for key, label, ae, quarters in variants:
        s = _summary(ae, quarters)
        out["variants"].append(dict(key=key, label=label, **s))
    return out


def run(root="."):
    root = Path(root)
    if not (root / "results/holdout.csv").exists():
        print("skip sensitivity: no holdout yet")
        return 0
    s = compute(root)
    write_json(root / "results/exploratory/sensitivity.json", s)
    lines = ["# Sensitivity of the held-out comparison (exploratory)", "",
             "Tried after the held-out results were seen. By the preregistration none of this changes the headline; "
             "it shows how far the comparison moves under another reading or another window.", "",
             "Average miss in aircraft. \"Closer\" counts the quarters where the registry estimate missed by less than "
             "the guidance pace; p is the one-sided exact sign test.", "",
             "| Variant | Quarters | Registry estimate | Raw count | Guidance pace | Same quarter last year | Last quarter "
             "| Closer than guidance | p |", "|---|---|---|---|---|---|---|---|---|"]
    for v in s["variants"]:
        t = v["ratio_vs_guidance"]
        lines.append(f"| {v['label']} | {v['n']} | " + " | ".join(f"{v['mae'][m]:.2f}" for m in MODELS)
                     + f" | {t['wins']} of {t['wins'] + t['losses'] + t['ties']} | {t['p_one_sided']:.3f} |")
    lines += ["", "The January 2021 reading: on its 2021-01-27 call GD gave the year only as a change from 2020 "
              "(\"So all up, 10 fewer aircraft\", after reporting 127 deliveries for 2020). The preregistered rule reads a "
              "change only when its base figure is in the same sentence, so the outlook is blank and 2021 falls back "
              f"to the same quarter last year. Read as 117, all {s['sourced_quarters_with_2021_as_117']} held-out "
              "quarters have an outlook."]
    write_text(root / "results/exploratory/sensitivity.md", "\n".join(lines) + "\n")
    print("wrote results/exploratory/sensitivity.json and .md")
    return 0
