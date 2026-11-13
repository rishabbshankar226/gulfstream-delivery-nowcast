"""Fixes from round 4 of the pre-publication audit (docs/prepub/ROUND4_VERDICT.md), each checked against the files it
is built from. Figures are recomputed here from data, results or the snapshot tables, never copied from the text."""
import csv
import gzip
import io
import json
import re
import subprocess
from html import unescape

import pytest
from openpyxl import load_workbook

from conftest import FIXTURES, ROOT
from gdn import charts, events, faa, note, report, workbook
from gdn.files import write_json


@pytest.fixture
def clone(tmp_path):
    root = tmp_path / "repo"
    subprocess.run(["git", "clone", "-q", str(ROOT), str(root)], check=True)
    return root


def plain(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))


def metrics():
    return json.loads((ROOT / "results/metrics.json").read_text())


def test_the_note_states_why_gd_left_the_defense_study_as_the_filings_allow(clone):
    # F109. GD's 10-Ks for FY2023 to FY2025 carry an undimensioned backlog fact, so "stopped tagging backlog in XBRL in
    # 2018" is false. What holds: no quarterly figure after 2018Q3 in the company-facts data.
    note.build(clone)
    t = plain((clone / "report/note.html").read_text())
    assert "stopped tagging backlog" not in t
    assert "holds no quarterly GD backlog after 2018Q3" in t


def test_the_notes_first_page_glosses_its_terms_and_says_where_the_edge_comes_from(clone):
    # F114, F116. Key point 1 keeps the preregistered sentence, then says the pace is mine and that the registry
    # estimate's lead over it comes from two years.
    note.build(clone)
    html = (clone / "report/note.html").read_text()
    kp = plain(html[html.index('<div class="keypoints">'):html.index("</ol></div>")])
    assert "GD's guidance pace is my construction from GD's full-year outlook" in kp
    split = report.split_sentence(clone)
    assert split and split[:60] in kp
    assert "comes from 2023 and 2024" in kp


def test_the_band_is_shown_with_its_coverage_in_the_note_and_the_workbook(clone):
    # F113. Wherever the band is shown, its coverage on the held-out quarters is beside it.
    b = metrics()["holdout"]["band"]
    phrase = f"held GD's count in {b['hits']} of {b['n']} held-out quarters against a nominal 80%"
    note.build(clone)
    kp = plain((clone / "report/note.html").read_text())
    assert kp.count(phrase) >= 2                       # key point 2 and the locked-quarter paragraph
    workbook.build(clone)
    ws = load_workbook(clone / "output/gd_gulfstream_model.xlsx")["Live"]
    assert f"held GD's count in {b['hits']} of {b['n']} held-out quarters, against a nominal 80%" in ws["C14"].value


def test_the_workbook_summary_does_not_say_a_baseline_beat_the_estimate(clone):
    # F123. "Beat" is kept for a Holm rejection (PREREGISTRATION.md, headline rule). None rejects.
    assert not any(metrics()["holdout"]["tests"][b]["holm_reject"] for b in ("guidance", "seasonal", "last"))
    workbook.build(clone)
    a9 = load_workbook(clone / "output/gd_gulfstream_model.xlsx")["Summary"]["A9"].value
    assert "beat" not in a9 and "missed by less on average" in a9


def test_gds_stated_shape_of_the_year_and_the_even_split_sit_beside_the_pace(clone):
    # F115. GD said on its 2026-04-29 call that Q3 and Q4 would be its highest; the pace split the year by an older
    # pattern. Found from data/guidance.csv, not typed in.
    rows = [r for r in csv.DictReader((ROOT / "data/guidance.csv").open())
            if r["call_date"].startswith("2026") and "third" in r["quote"].lower() and "highest" in r["quote"].lower()]
    assert rows
    assert note.stated_shape(clone, "2026Q3") == (f" On its {rows[-1]['call_date']} call GD said the third quarter "
                                                  "would be among the year's highest.")
    assert note.stated_shape(clone, "2026Q1") == ""
    note.build(clone)
    t = plain((clone / "report/note.html").read_text())
    assert note.stated_shape(clone, "2026Q3").strip() in t
    assert "an even split would have said" in t


def test_the_note_does_not_say_it_reads_every_gulfstream_jet(clone):
    # F119. The scope rule leaves one G700 type code out (README, Limitations), so "every Gulfstream jet" is wrong.
    note.build(clone)
    t = plain((clone / "report/note.html").read_text())
    assert "every Gulfstream jet in the FAA" not in t
    assert "every Gulfstream jet type my scope rule keeps" in t
    assert "Scope and holder:" in t


def test_the_notes_risks_carry_the_mid_cabin_supplier_delay(clone):
    # F122. GD's 2026Q2 10-Q states a delay at its Israel-based mid-cabin airframe supplier; the note's mid-cabin
    # count rests on the G280 alone.
    claims = json.loads((ROOT / "docs/build/claims_risks.json").read_text())
    c = next(x for x in claims if x["id"] == "risk-midcabin-supplier-delay")
    assert c["url_or_accn"] == "0000040533-26-000032" and len(c["quote"].split()) < 25
    # report/claims.json is built where the cached sources are (data/raw/, untracked); the clone reads the tracked one.
    assert any(x["id"] == c["id"] for x in json.loads((clone / "report/claims.json").read_text()))
    note.build(clone)
    html = (clone / "report/note.html").read_text()
    risks = plain(html[html.index("<h2>Risks</h2>"):html.index("<h2>Limitations of the method</h2>")])
    assert "Israel-based supplier of mid-cabin airframes" in risks


def _texts_with(extra):
    """The shared FAA fixture texts, with MASTER rows added in memory only."""
    t = {k: (FIXTURES / "faa" / f"{k}.txt").read_bytes().decode("utf-8", errors="replace") for k in faa.FILES}
    t["MASTER"] = t["MASTER"].rstrip("\n") + "\n" + "\n".join(extra) + "\n"
    return t


def test_an_airframe_with_neither_date_counts_and_one_past_its_year_bound_drops():
    # F125. With no airworthiness date and no year of manufacture the bound is None and any certificate counts; with
    # a year only, the bound is the end of the next year. Two airframes built here, not in the shared fixture.
    neither = "N280NA  ,2201         ,4500314     ,        ,NEITHER DATE HOLDINGS    ,20240601       ,              ,"
    yearonly = "N280YB  ,2202         ,4500314     ,2016    ,YEAR ONLY HOLDINGS       ,20240601       ,              ,"
    rows = {(r["mfr_code"], r["serial"]): r for r in events.airframes(faa.subset(_texts_with([neither, yearonly])))}
    a, b = rows[("450", "2201")], rows[("450", "2202")]
    assert a["bound"] is None and a["e1"] == "2024-06-01" and a["e2"] == "2024-06-01"
    assert b["bound"] == "2017-12-31" and b["e1"] is None and b["e2"] is None


def test_the_locks_old_airframe_count_rebuilds_from_its_snapshot_table():
    # F127. "Of the 42 events in the raw count, 5 were airframes at least three years old": rebuilt here from the
    # snapshot table the lock read, and the 42 checked against the locked prediction's own counts.
    p = json.loads((ROOT / "predictions/2026Q3.json").read_text())
    t = ROOT / f"data/snapshots/daily/{p['snapshot']}.serials.csv.gz"
    rows = list(csv.DictReader(io.StringIO(gzip.decompress(t.read_bytes()).decode())))
    e = p["definition"].lower()
    ev = [r for r in rows if r.get(e) and p["window_start"] < r[e] <= p["window_end"]]
    old = [r for r in ev if r["year_mfr"] and int(r[e][:4]) - int(r["year_mfr"]) >= 3]
    assert len(ev) == p["events"]["large"] + p["events"]["mid"]
    assert note.old_events_line(ROOT, p) == (f" Of the {len(ev)} events in the raw count, {len(old)} were airframes at "
                                             "least three years old by the registry's year of manufacture, so the raw "
                                             "count is not a count of new jets.")


def test_the_counted_events_used_jet_share_rebuilds_from_the_serials_table():
    # F127. "246 of the 1,251 counted events": rebuilt here from data/processed/serials.csv and the quarter windows.
    e = metrics()["definition"].lower()
    reg = list(csv.DictReader((ROOT / "data/processed/registry_quarterly.csv").open()))
    lo, hi = min(r["window_start"] for r in reg), max(r["window_end"] for r in reg)
    ev = [r for r in csv.DictReader((ROOT / "data/processed/serials.csv").open()) if r[e] and lo < r[e] <= hi]
    old = [r for r in ev if r["year_mfr"] and int(r[e][:4]) - int(r["year_mfr"]) >= 3]
    assert f"{len(old):,} of the {len(ev):,} counted events ({len(old) / len(ev) * 100:.1f}%)" in note.used_share(ROOT)


def _scores(root, quarters):
    for q, locked in quarters:
        s = {"quarter": q, "reported": {"large": 30, "mid": 5, "total": 35}, "accn": "x", "locked": locked,
             "nowcast": {"total": 30.0} if locked else None, "ae_total": 5.0, "inside_band": True}
        write_json(root / f"results/live/{q}_score.json", s)
        if locked:
            write_json(root / f"predictions/{q}.json", {"quarter": q, "band": [20.0, 40.0]})


@pytest.mark.parametrize("state,expect", [
    ([], []),                                             # nothing scored yet
    ([("2026Q3", False)], []),                            # scored, but the quarter missed its lock window
    ([("2026Q3", True)], ["2026Q3"]),                     # one lock, scored
    ([("2026Q3", True), ("2026Q4", True)], ["2026Q3", "2026Q4"]),
    ([("2026Q3", True), ("2026Q4", False), ("2027Q1", True)], ["2026Q3", "2027Q1"]),
])
def test_the_track_chart_draws_each_scored_lock_after_the_backtest(tmp_path, state, expect):
    # F117. The README's first image and the post's link card show the live record, in every state the daily job can
    # meet, and a locked quarter that is not yet scored draws nothing.
    (tmp_path / "results/live").mkdir(parents=True)
    (tmp_path / "predictions").mkdir()
    _scores(tmp_path, state)
    if not state:
        write_json(tmp_path / "predictions/2026Q4.json", {"quarter": "2026Q4", "band": [1.0, 2.0]})  # locked, unscored
    pts = charts.locked_points(tmp_path)
    assert [q for q, *_ in pts] == expect
    qs = charts.track_quarters(tmp_path)
    assert qs[:len(charts.QS)] == charts.QS and (qs[-1] == expect[-1] if expect else qs == charts.QS)


def test_the_readmes_first_screen_says_whose_pace_it_is():
    # F130 (COLDREAD-1). The live summary and the backtest line sit above the README's definition of the pace, so they
    # name it as mine. The preregistered headline sentence further down keeps its own wording, glossed after it.
    s = report.live_summary(ROOT)
    assert "GD's guidance pace missed by" not in s and "GD's guidance pace by" not in s
    assert "my pace from GD's outlook by" in s
