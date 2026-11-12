"""What the README, the post and the note say once GD has reported, on a clone with a made-up score.

Each test starts from a clone put back to the state before any lock or score (the tracked tree now holds the real
2026Q3 lock and score), writes the lock and score files a release day would, and rebuilds the text from them."""
import json
import re
import subprocess
from html import unescape

import pytest

from conftest import ROOT
from gdn import live, note, report
from gdn.files import write_json


@pytest.fixture
def scored(tmp_path):
    """A clone where 2026Q3 is scored and 2026Q4's first files exist; `lock` adds the lock first."""
    root = tmp_path / "repo"
    subprocess.run(["git", "clone", "-q", str(ROOT), str(root)], check=True)
    # Back to the day before the first lock: no prediction, lock or score, and no later quarter's files.
    for rel in ("predictions/2026Q3.json", "results/live/2026Q3_lock.json", "results/live/2026Q3_score.json",
                "results/live/2026Q4_latest.json", "results/live/2026Q4_path.csv",
                "data/processed/segments_reported.csv"):
        (root / rel).unlink(missing_ok=True)

    def make(lock, public=None):
        latest = json.loads((root / "results/live/2026Q3_latest.json").read_text())
        if public:
            cfg = json.loads((root / "config/calendar.json").read_text())
            cfg.update(public)
            write_json(root / "config/calendar.json", cfg)
        if lock:
            write_json(root / "predictions/2026Q3.json", latest)
            write_json(root / "results/live/2026Q3_lock.json", {"tag": "lock-2026Q3", "published_at":
                       "2026-10-29T23:20:00Z", "sha256": "0" * 64, "commit": "0" * 40})
        s = live.score_quarter(root, "2026Q3", {"large": 30, "mid": 5, "total": 35}, "0000040533-26-000040")
        write_json(root / "results/live/2026Q3_score.json", s)
        live.update_latest(root, live.parse_now("2026-10-30T15:00:00Z"), log=lambda *a: None)
        return root
    return make


def plain(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))


@pytest.mark.parametrize("lock", [True, False])
def test_an_open_quarter_shows_no_partial_estimate(scored, lock):
    # The run that scores 2026Q3 starts 2026Q4 from a snapshot early in its window; its count so far is not an
    # estimate of the quarter, and its band can run below zero.
    rec = report.live_record(scored(lock))
    q4 = next(ln for ln in rec.splitlines() if ln.startswith("- **2026Q4**"))
    assert "latest estimate" not in q4 and "band" not in q4
    assert "2026-12-31" in q4


def test_a_missed_lock_is_said_in_the_post_and_the_note(scored):
    root = scored(False)
    post = report.post(root)
    assert "comes on 2026-10-30" not in post and "missed its lock window" in post
    note.build(root)
    t = plain((root / "report/note.html").read_text())
    assert "the locked estimate replaces it" not in t
    assert t.count("missed its lock window") >= 2


def test_a_locked_and_scored_quarter_keeps_its_text(scored):
    root = scored(True)
    latest = json.loads((root / "results/live/2026Q3_latest.json").read_text())["nowcast"]["total"]
    miss = f"{abs(latest - 35):.1f}"
    post = report.post(root)
    assert post.startswith(f"My first locked estimate of Gulfstream deliveries landed inside its band: I said "
                           f"{latest:.1f} for 2026Q3, General Dynamics reported 35.")
    assert f"The 2026Q3 miss was {miss}, inside my 80% band" in post
    note.build(root)
    t = plain((root / "report/note.html").read_text())
    assert "at 19:20 ET on 2026-10-29" in t and "GD reported 35" in t and f"missed by {miss}" in t
    assert "missed its lock window" not in t


def test_the_live_record_sets_the_lock_beside_the_other_misses(scored):
    # BUYSIDE-7: the lock's miss alone says little; the README gives the four comparators for the quarter.
    root = scored(True)
    rec = report.live_record(root)
    q3 = next(ln for ln in rec.splitlines() if ln.startswith("- **2026Q3**"))
    assert "GD reported 35 on 2026-10-30" in q3 and "Other misses for the quarter:" in q3
    for label in ("GD's guidance pace", "the raw registry count", "the same quarter last year", "last quarter"):
        assert label in q3
    assert "(39) by 4" in q3 and "(41) by 6" in q3          # 2025Q3 delivered 39, 2026Q2 delivered 41


@pytest.mark.parametrize("public,words", [
    (None, "made while the repository was private"),
    ({"public": True}, "made while the repository was private"),
    ({"public": True, "public_since": "2026-11-15"}, "made while the repository was private"),
    ({"public": True, "public_since": "2026-10-01"}, "public GitHub release"),
])
def test_a_lock_is_called_public_only_if_the_repository_was_public_that_day(scored, public, words):
    # F005. Setting "public": true must not relabel a lock that nobody outside could see when it was made.
    root = scored(True, public)
    q3 = next(ln for ln in report.live_record(root).splitlines() if ln.startswith("- **2026Q3**"))
    assert words in q3
    assert ("public GitHub release" in q3) == (words == "public GitHub release")
    note.build(root)
    t = plain((root / "report/note.html").read_text())
    assert words in t and "public lock" not in t


def test_the_post_counts_its_locked_quarters(scored):
    # F020. "My first locked estimate" and "One locked quarter is one data point" are true for one quarter only.
    root = scored(True)
    one = report.post(root)
    assert "My first locked estimate" in one and "One quarter is one data point." in one
    pred = json.loads((root / "predictions/2026Q3.json").read_text())
    pred["quarter"] = "2026Q4"
    write_json(root / "predictions/2026Q4.json", pred)
    write_json(root / "results/live/2026Q4_lock.json", {"tag": "lock-2026Q4", "published_at": "2027-01-26T23:20:00Z",
                                                         "sha256": "0" * 64, "commit": "0" * 40})
    s = json.loads((root / "results/live/2026Q3_score.json").read_text())
    s["quarter"] = "2026Q4"
    write_json(root / "results/live/2026Q4_score.json", s)
    two = report.post(root)
    assert two.startswith("2 locked estimates of Gulfstream deliveries so far")
    assert "My first locked estimate" not in two and "One quarter is one data point" not in two


def test_the_post_is_short_and_carries_its_disclaimer(scored):
    for lock in (True, False):
        p = report.post(scored(lock))
        assert len(p) <= report.POST_MAX, len(p)
        assert report.DISCLAIMER in p and "not investment advice" in p
        assert "rules set minutes before scoring" in p and "missed by less on average" in p
        assert "had months or years to fill in" in p and "#GeneralDynamics" not in p and "$GD" not in p


def test_the_readme_summary_block_is_rewritten_between_its_markers(scored):
    root = scored(True)
    readme = root / "README.md"
    md = readme.read_text()
    a, b = report.SUMMARY_MARKS
    assert a in md and b in md
    readme.write_text(md.replace(md[md.index(a):md.index(b) + len(b)], f"{a}\nstale text\n{b}"))
    report.run(root)
    out = readme.read_text()
    block = out[out.index(a):out.index(b)]
    assert "stale text" not in block and "Live record so far: one locked quarter" in block
    assert "GD reported 35" in block and "Backtest, 26 held-out quarters" in block
    # and the first screen names the baseline that won
    assert "missed by least" in block
