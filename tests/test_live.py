"""The lock's timing and steps (§3.6) with fixed clocks and a fake git/gh, and the score."""
import datetime as dt
import json
import shutil
from pathlib import Path

import pytest

from conftest import FIXTURES, ROOT
from gdn import events, faa, live
from gdn.files import write_json

ET = live.ET


def at(s):
    """An ET wall-clock time as aware UTC."""
    return dt.datetime.fromisoformat(s).replace(tzinfo=ET).astimezone(dt.timezone.utc)


class FakeOps:
    """Stands in for gitops.Ops: records commits, pushes and releases."""

    def __init__(self, root, clock, reject_pushes=0, release=None):
        self.root, self.clock, self.rejects = Path(root), clock, reject_pushes
        self.released, self.creates, self.commits, self.pushes, self.resets = release, [], [], 0, 0
        self.tracked_files = set()

    def pull(self):
        return []

    def release_view(self, tag):
        return self.released

    def ahead(self):
        return 0

    def tracked(self, p):
        return Path(p) in self.tracked_files

    def first_commit(self, p):
        return "c-first"

    def commit_only(self, p, msg):
        self.commits.append(("only", Path(p).name, msg))
        self.tracked_files.add(Path(p))
        return f"c{len(self.commits)}"

    def commit(self, paths, msg):
        self.commits.append(("commit", msg))
        return True

    def push(self):
        if self.rejects:
            self.rejects -= 1
            return False
        self.pushes += 1
        return True

    def reset_to_upstream(self):
        self.resets += 1
        for p in list(self.tracked_files):
            p.unlink(missing_ok=True)
            self.tracked_files.discard(p)

    def release_create(self, tag, target, title, notes):
        self.creates.append((tag, target, title, notes))
        self.released = {"tagName": tag, "publishedAt": live.stamp(self.clock)}

    def fetch_tag(self, tag):
        pass

    def tag_commit(self, tag):
        return self.creates[-1][1] if self.creates else "c-first"

    def abort_merge(self):
        pass


@pytest.fixture
def repo(tmp_path):
    """A small tree: GD's reported series, a metrics file, the calendar, and fixture snapshots."""
    (tmp_path / "data/processed").mkdir(parents=True)
    shutil.copy(ROOT / "data/processed/gd_deliveries.csv", tmp_path / "data/processed/gd_deliveries.csv")
    write_json(tmp_path / "config/calendar.json", {"releases": {"2026Q3": "2026-10-30"}, "fiscal_ends": {},
                                                   "public": False})
    write_json(tmp_path / "results/metrics.json", {"definition": "E1", "band_errors": [float(x) for x in
                                                                                      range(-10, 10)]})
    texts = {k: (FIXTURES / "faa" / f"{k}.txt").read_bytes().decode("utf-8") for k in faa.FILES}
    sub = faa.subset(texts)
    z = tmp_path / "zip.zip"
    z.write_bytes(b"PK")
    rows = events.airframes(sub)
    for date in ("2026-10-27", "2026-10-28", "2026-10-29"):
        faa.store_subset(tmp_path, date, sub, z, backtest=(date == "2026-10-27"))
    for date in ("2026-10-27", "2026-10-28"):
        live.write_table(tmp_path, date, rows)
    return tmp_path


def lock(repo, when, snapshots=("2026-10-28",), **kw):
    for s in snapshots:
        live.write_table(repo, s, events.read_serials_rows([]) or [])
    ops = FakeOps(repo, at(when), **kw)
    rc = live.run_lock(at(when), root=repo, ops=ops, log=lambda *a: None)
    return rc, ops


def test_lock_due_rule():
    rel = "2026-10-30"
    assert not live.lock_due(at("2026-10-28T23:00"), rel, "2026-10-28")
    assert not live.lock_due(at("2026-10-29T18:59"), rel, "2026-10-28")
    assert live.lock_due(at("2026-10-29T08:00"), rel, "2026-10-29")
    assert live.lock_due(at("2026-10-29T19:00"), rel, "2026-10-28")
    assert live.lock_due(at("2026-10-29T23:59"), rel, "2026-10-28")
    assert not live.lock_due(at("2026-10-30T00:00"), rel, "2026-10-29")


def test_no_lock_before_the_eve(repo):
    rc, ops = lock(repo, "2026-10-28T20:00")
    assert rc == 0 and not ops.creates and not (repo / "predictions/2026Q3.json").exists()


def test_eve_with_same_day_snapshot_locks(repo):
    live.write_table(repo, "2026-10-29", [])
    rc, ops = lock(repo, "2026-10-29T08:30", snapshots=())
    assert rc == 0 and len(ops.creates) == 1
    pred = json.loads((repo / "predictions/2026Q3.json").read_text())
    assert pred["snapshot"] == "2026-10-29"           # the newest stored subset
    tag, target, title, notes = ops.creates[0]
    assert (tag, title) == ("lock-2026Q3", "Locked nowcast 2026Q3")
    lk = json.loads((repo / "results/live/2026Q3_lock.json").read_text())
    assert notes == f"sha256 {lk['sha256']}" and lk["commit"] == target
    assert lk["published_at"] == "2026-10-29T12:30:00Z"


def test_eve_before_seven_pm_with_older_snapshot_waits(repo):
    rc, ops = lock(repo, "2026-10-29T18:59")
    assert not ops.creates and not (repo / "predictions/2026Q3.json").exists()


def test_eve_at_seven_pm_with_older_snapshot_locks(repo):
    rc, ops = lock(repo, "2026-10-29T19:00")
    assert rc == 0 and len(ops.creates) == 1


def test_no_lock_on_the_release_date(repo):
    rc, ops = lock(repo, "2026-10-30T00:00", snapshots=("2026-10-29",))
    assert not ops.creates and not (repo / "predictions/2026Q3.json").exists()


def test_no_second_lock(repo):
    rc, ops = lock(repo, "2026-10-29T19:00")
    first = (repo / "predictions/2026Q3.json").read_bytes()
    ops2 = FakeOps(repo, at("2026-10-29T21:00"), release=ops.released)
    live.run_lock(at("2026-10-29T21:00"), root=repo, ops=ops2, log=lambda *a: None)
    assert not ops2.creates and (repo / "predictions/2026Q3.json").read_bytes() == first


def test_rejected_push_resets_and_retries(repo):
    rc, ops = lock(repo, "2026-10-29T19:30", reject_pushes=1)
    assert rc == 0 and ops.resets == 1 and len(ops.creates) == 1
    assert sum(1 for c in ops.commits if c[0] == "only") == 2


def test_three_rejected_pushes_give_up(repo):
    rc, ops = lock(repo, "2026-10-29T19:30", reject_pushes=9)
    assert rc == 1 and not ops.creates and ops.resets == 3


def test_release_without_lock_json_is_recorded(repo):
    rc, ops = lock(repo, "2026-10-29T19:00")
    (repo / "results/live/2026Q3_lock.json").unlink()
    ops2 = FakeOps(repo, at("2026-10-30T07:00"), release=ops.released)
    ops2.creates = list(ops.creates)
    live.run_lock(at("2026-10-30T07:00"), root=repo, ops=ops2, log=lambda *a: None)
    assert (repo / "results/live/2026Q3_lock.json").exists() and len(ops2.creates) == 1


def test_score_with_and_without_lock(repo):
    (repo / "data/guidance.csv").write_text(
        "call_date,year,outlook,quote,speaker,url\n2026-07-29,2026,160,about 160,CFO,u\n")
    d = {"large": 34, "mid": 6, "total": 40}
    s = live.score_quarter(repo, "2026Q3", d, "0000040533-26-000099")
    assert s["locked"] is False and s["nowcast"] is None and s["ae_total"] is None and s["inside_band"] is None
    assert s["guidance_pace"] is not None and s["guidance_ae"] == abs(s["guidance_pace"] - 40)
    lock(repo, "2026-10-29T19:00")
    s = live.score_quarter(repo, "2026Q3", d, "0000040533-26-000099")
    pred = json.loads((repo / "predictions/2026Q3.json").read_text())
    assert s["locked"] is True and s["nowcast"] == pred["nowcast"]
    assert s["ae_total"] == abs(pred["nowcast"]["total"] - 40)
    assert s["inside_band"] == (pred["band"][0] <= 40 <= pred["band"][1])


def test_existing_release_blocks_a_new_lock(repo):
    # Another machine already created the release; this clone has neither the prediction nor the lock record.
    ops = FakeOps(repo, at("2026-10-29T19:30"), release={"tagName": "lock-2026Q3", "publishedAt": "2026-10-29T23:05:00Z"})
    live.run_lock(at("2026-10-29T19:30"), root=repo, ops=ops, log=lambda *a: None)
    assert ops.creates == [] and not (repo / "predictions/2026Q3.json").exists()
