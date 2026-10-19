"""The estimates basis, the workbook's rebuild rule and format, and the offline backtest subset (§3.7, §3.8,
§3.11), on copies of the tracked inputs."""
import json
import shutil

from openpyxl import load_workbook

from conftest import FIXTURES, ROOT
from gdn import data, estimates, faa, workbook
from gdn.files import sha256, write_json

INPUTS = ["data/processed", "results/metrics.json", "results/live/2026Q3_build.json", "data/snapshots/MANIFEST.json",
          "config/calendar.json", "data/guidance.csv"]


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
