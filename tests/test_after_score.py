"""What the README, the post and the note say once GD has reported, on a clone with a made-up score.

The live quarter's text only changes after a score, which no tracked file holds yet, so each test writes the
lock and score files a release day would and rebuilds the text from them."""
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

    def make(lock):
        latest = json.loads((root / "results/live/2026Q3_latest.json").read_text())
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
    assert report.post(root).startswith("One locked quarter so far: off by 3.9.")
    note.build(root)
    t = plain((root / "report/note.html").read_text())
    assert "I locked it as a timestamped GitHub release at 19:20 ET on 2026-10-29. GD reported 35" in t
    assert "missed its lock window" not in t
