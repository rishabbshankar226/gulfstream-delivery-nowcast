"""results/estimates.json (§3.7): 2026Q3 segment estimates from the 2026Q2 origin."""
from pathlib import Path

from .fiscal import qrange
from .files import read_csv, read_json, sha256, write_json

ORIGIN, TARGET = "2026Q2", "2026Q3"
SEGMENTS = ("Aerospace", "Marine Systems", "Combat Systems", "Technologies")
DEFENSE = SEGMENTS[1:]
TTM = qrange("2025Q3", "2026Q2")
TTM_PRIOR = qrange("2024Q3", "2025Q2")
LABEL = ("the delivery estimate × trailing Aerospace revenue per delivery, services included: "
         "a mechanical estimate")


def basis_path(root):
    root = Path(root)
    p = root / "predictions" / f"{TARGET}.json"
    return p if p.exists() else root / "results/live" / f"{TARGET}_build.json"


def compute(root="."):
    root = Path(root)
    seg = {}
    for r in read_csv(root / "data/processed/segments.csv"):
        seg.setdefault(r["segment"], {})[r["quarter"]] = (int(r["revenue_usd"]), int(r["operating_earnings_usd"]))
    backlog = {r["segment"]: int(r["total_backlog_usd"]) for r in read_csv(root / "data/processed/backlog_2026Q2.csv")}
    rep = {r["quarter"]: int(r["total"]) for r in read_csv(root / "data/processed/gd_deliveries.csv")}
    bp = basis_path(root)
    basis = read_json(bp)
    out_seg = {}
    for s in SEGMENTS:
        ttm = sum(seg[s][q][0] for q in TTM)
        prior = sum(seg[s][q][0] for q in TTM_PRIOR)
        oe = sum(seg[s][q][1] for q in TTM)
        out_seg[s] = {"ttm_revenue_usd": ttm, "ttm_revenue_prior_usd": prior,
                      "drift_usd": seg[s]["2025Q3"][0] * ttm / prior, "ttm_margin": oe / ttm,
                      "backlog_usd": backlog[s], "coverage_years": backlog[s] / ttm}
    ttm_del = sum(rep[q] for q in TTM)
    rpd = out_seg["Aerospace"]["ttm_revenue_usd"] / ttm_del
    total = basis["nowcast"]["total"]
    aero = total * rpd
    aero_oe = aero * out_seg["Aerospace"]["ttm_margin"]
    return {
        "origin": ORIGIN, "target": TARGET,
        "basis": {"path": str(bp.relative_to(root)), "sha256": sha256(bp.read_bytes())},
        "segments": out_seg,
        "ttm_deliveries": ttm_del,
        "revenue_per_delivery_usd": rpd,
        "nowcast_total": total,
        "aerospace_from_nowcast_usd": aero,
        "aerospace_oe_from_nowcast_usd": aero_oe,
        "revenue_total_usd": aero + sum(out_seg[s]["drift_usd"] for s in DEFENSE),
        "operating_earnings_total_usd": aero_oe + sum(out_seg[s]["drift_usd"] * out_seg[s]["ttm_margin"]
                                                      for s in DEFENSE),
        "sensitivity": [{"deliveries_change": k, "deliveries": total + k, "aerospace_revenue_usd": (total + k) * rpd}
                        for k in range(-4, 5)],
    }


def run(root="."):
    root = Path(root)
    if not basis_path(root).exists():
        print("skip estimates: no build nowcast or prediction yet")
        return 0
    e = compute(root)
    write_json(root / "results/estimates.json", e)
    print(f"estimates from {e['basis']['path']}: Aerospace ${e['aerospace_from_nowcast_usd'] / 1e9:.1f}B "
          f"from {e['nowcast_total']:.1f} deliveries")
    return 0
