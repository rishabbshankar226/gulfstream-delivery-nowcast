"""The estimates basis, the workbook's rebuild rule and format, and the offline backtest subset (§3.7, §3.8,
§3.11), on copies of the tracked inputs."""
import json
import shutil

from openpyxl import load_workbook

from conftest import FIXTURES, ROOT
from gdn import data, estimates, faa, workbook
from gdn.files import sha256, write_json

INPUTS = ["data/processed", "results/metrics.json", "results/holdout.csv", "results/live/2026Q3_build.json",
          "data/snapshots/MANIFEST.json", "config/calendar.json", "data/guidance.csv"]


def tree(tmp_path):
    for rel in INPUTS:
        src, dst = ROOT / rel, tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if src.is_dir() else shutil.copy)(src, dst)
    return tmp_path


def test_estimates_switch_to_the_locked_prediction(tmp_path):
    root = tree(tmp_path)
    assert estimates.compute(root)["basis"]["path"] == "results/live/2026Q3_build.json"
    pred = json.loads((root / "results/live/2026Q3_build.json").read_text())
    pred["nowcast"]["total"] = 40.0
    write_json(root / "predictions/2026Q3.json", pred)
    e = estimates.compute(root)
    assert e["basis"] == {"path": "predictions/2026Q3.json",
                          "sha256": sha256((root / "predictions/2026Q3.json").read_bytes())}
    assert e["nowcast_total"] == 40.0 and e["aerospace_from_nowcast_usd"] == 40.0 * e["revenue_per_delivery_usd"]


def test_workbook_is_kept_until_an_input_changes(tmp_path, capsys):
    root = tree(tmp_path)
    workbook.run(root)
    first = (root / workbook.OUT).read_bytes()
    workbook.run(root)
    assert "inputs unchanged; kept" in capsys.readouterr().out
    assert (root / workbook.OUT).read_bytes() == first
    m = json.loads((root / "results/metrics.json").read_text())
    m["note"] = "changed"
    write_json(root / "results/metrics.json", m)
    workbook.run(root)
    assert "wrote" in capsys.readouterr().out


def test_revenue_per_delivery_is_formatted_as_dollars(tmp_path):
    root = tree(tmp_path)
    workbook.build(root)
    ws = load_workbook(root / workbook.OUT)["Segments"]
    row = next(r for r in ws.iter_rows() if r[0].value == "Revenue per delivery")
    assert row[1].number_format == "#,##0"


def test_offline_data_reads_the_tracked_backtest_subset(tmp_path):
    texts = {k: (FIXTURES / "faa" / f"{k}.txt").read_bytes().decode("utf-8") for k in faa.FILES}
    z = faa.zip_path(tmp_path, "2030-01-02")
    z.parent.mkdir(parents=True)
    z.write_bytes(b"PK first")
    faa.store_subset(tmp_path, "2030-01-02", faa.subset(texts), z, backtest=True)
    stored = {p.name: p.read_bytes() for p in (tmp_path / "data/snapshots/2030-01-02").iterdir()}
    # A different zip under the same name: neither an offline nor a networked build may re-store from it.
    z.write_bytes(b"PK replaced")
    for network in (False, True):
        date, sub = data.build_faa(tmp_path, network=network, log=lambda *a: None)
        assert date == "2030-01-02" and sub == faa.read_subset(tmp_path, date)
    assert {p.name: p.read_bytes() for p in (tmp_path / "data/snapshots/2030-01-02").iterdir()} == stored


def test_the_path_chart_keeps_a_scored_quarter_until_the_next_lock(tmp_path):
    from gdn.charts import featured_path
    lv = tmp_path / "results/live"
    lv.mkdir(parents=True)
    paths = [lv / "2026Q3_path.csv", lv / "2026Q4_path.csv"]
    for p in paths:
        p.write_text("date\n")
    assert featured_path(paths) == paths[1]
    (lv / "2026Q3_score.json").write_text("{}\n")
    assert featured_path(paths) == paths[0]
    (lv / "2026Q4_lock.json").write_text("{}\n")
    assert featured_path(paths) == paths[1]


def test_workbook_digest_covers_every_input_but_new_snapshot_entries(tmp_path):
    root = tree(tmp_path)
    base = workbook.input_digest(root)
    man = json.loads((root / "data/snapshots/MANIFEST.json").read_text())
    man["snapshots"]["2026-10-29"] = {"zip_sha256": "0" * 64}
    write_json(root / "data/snapshots/MANIFEST.json", man)
    assert workbook.input_digest(root) == base  # a lock-window snapshot changes nothing the workbook shows
    for rel in ("data/processed/backlog_2026Q2.csv", "data/processed/gd_deliveries.csv",
                "data/processed/registry_quarterly.csv"):
        p = root / rel
        old = p.read_bytes()
        p.write_bytes(old + b"\n")
        assert workbook.input_digest(root) != base, rel
        p.write_bytes(old)
    man["backtest"] = "2026-10-20"
    write_json(root / "data/snapshots/MANIFEST.json", man)
    assert workbook.input_digest(root) != base
    man["backtest"] = json.loads((ROOT / "data/snapshots/MANIFEST.json").read_text())["backtest"]
    write_json(root / "data/snapshots/MANIFEST.json", man)
    assert workbook.input_digest(root) == base
    write_json(root / "results/live/2026Q3_score.json", {"quarter": "2026Q3"})
    assert workbook.input_digest(root) != base


def test_the_workbook_carries_the_guidance_baseline_and_the_live_result(tmp_path):
    # BUYSIDE-17. The About sheet says the held-out quarters are scored against GD's guidance, so the sheets must
    # hold it; and once GD has reported the live quarter, the Live sheet states the miss and the band outcome.
    root = tree(tmp_path)
    shutil.copy(ROOT / "predictions/2026Q3.json", (root / "predictions").mkdir() or root / "predictions/2026Q3.json")
    shutil.copy(ROOT / "results/live/2026Q3_score.json", root / "results/live/2026Q3_score.json")
    workbook.build(root)
    wb = load_workbook(root / workbook.OUT)
    q = wb["Quarters"]
    head = [c.value for c in q[1]]
    assert head[:18] == workbook.HEAD and head[18:20] == ["Guidance pace", "AE guidance"]
    assert q["S18"].value is not None and q["T18"].value == "=ABS(S18-E18)" and q["S6"].value is None
    s = wb["Summary"]
    assert [s.cell(r, 1).value for r in range(2, 7)] == ["MAE ratio", "MAE raw", "MAE seasonal", "MAE last",
                                                           "MAE guidance"]
    assert s["C6"].value == "=AVERAGE(Quarters!T18:T43)"
    live = {r[0].value: r[1].value for r in wb["Live"].iter_rows(min_row=16, max_row=22)}
    assert live["GD reported"] == 40 and live["Miss of the lock"] == "=ABS(B11-B16)"
    assert "outside" in live["GD's count against the band"] and live["Guidance pace miss"] == "=ABS(B20-B16)"
    about = " ".join(str(r[0].value) for r in wb["About"].iter_rows() if r[0].value)
    assert "Not investment advice" in about and "365 days" in about
