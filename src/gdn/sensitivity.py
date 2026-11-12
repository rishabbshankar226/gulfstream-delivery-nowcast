"""results/exploratory/sensitivity.json and .md: the held-out comparison under other readings and windows.

Everything here was tried after the held-out results were seen, so by the preregistration it is exploratory and
changes no headline figure. It answers the questions a reader asks of the headline: what if GD's January 2021
statement is read as a number, what if 2020 is dropped, what if the years the guidance pace missed most are
dropped, what the other event definition gives, and what the baseline scores when GD's own stated plan for a quarter
stands in for my pace."""
from pathlib import Path

from . import model, stats
from .fiscal import HOLDOUT, Calendar, qrange
from .files import read_csv, write_json, write_text

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


def load_quarter_plans(root, cal):
    """data/quarter_plans.csv: the total deliveries GD said it planned for a quarter, on a call held inside that
    quarter. A range is stored at its midpoint. A plan stated after the quarter's fiscal end is refused."""
    p = Path(root) / "data/quarter_plans.csv"
    out = {}
    for r in (read_csv(p) if p.exists() else []):
        end = cal.end(r["quarter"])
        if not end or r["call_date"] > end:
            raise ValueError(f"quarter plan for {r['quarter']} dated {r['call_date']} is not before its fiscal end")
        out[r["quarter"]] = float(r["plan"])
    return out


def _with_plans(ae, plans, Y):
    """The same misses with the guidance pace replaced, where GD stated a plan, by the miss of that plan."""
    return {q: dict(m, guidance=abs(plans[q] - Y[q]["total"])) if q in plans else m for q, m in ae.items()}


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
    plans = {q: v for q, v in load_quarter_plans(root, cal).items() if q in qs}
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
    if plans:
        variants += [
            ("quarter_plans", f"GD's stated plan for the quarter in place of the guidance pace, in the {len(plans)} "
                              "quarters where a call gave one", _with_plans(base, plans, Y), qs),
            ("quarter_plans_and_2021_as_117", "Both: GD's stated quarter plans, and the January 2021 statement read "
                                              "as 117", _with_plans(alt, plans, Y), qs),
        ]
    out = {"note": "Exploratory: tried after the held-out results were seen. None of it changes the headline.",
           "chosen_definition": chosen, "sourced_quarters_with_2021_as_117": len(sourced_alt),
           "quarter_plans": plans, "variants": []}
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
    if s["quarter_plans"]:
        lines += ["", "GD's stated quarter plans: on " + str(len(s["quarter_plans"])) + " calls held inside a held-out "
                  "quarter GD said how many aircraft it planned to deliver in that quarter ("
                  + ", ".join(f"{q}: {v:g}" for q, v in sorted(s["quarter_plans"].items()))
                  + "; a range is taken at its midpoint). The quotes and links are in `data/quarter_plans.csv`. The "
                  "preregistered guidance pace reads only full-year outlooks, so it does not use them. In the rows "
                  "above that name these plans, the baseline is the plan itself in those quarters and the guidance "
                  "pace in the rest."]
    write_text(root / "results/exploratory/sensitivity.md", "\n".join(lines) + "\n")
    print("wrote results/exploratory/sensitivity.json and .md")
    return 0
