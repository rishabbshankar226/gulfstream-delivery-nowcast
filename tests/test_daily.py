"""`daily.run`'s order of steps and its failure handling (§3.11), with a fake git layer and the snapshot, lock,
score and rebuild steps replaced by recorders."""
import json
import zipfile

import pytest

from gdn import daily, faa, live

MAN = "data/snapshots/MANIFEST.json"


class DailyOps:
    """Stands in for gitops.Ops inside daily.run and records every call in order."""

    def __init__(self, merging=False, conflicts=(), stages=None):
        self.calls, self._merging, self._conflicts, self.stages = [], merging, list(conflicts), stages or {}

    def merging(self):
        return self._merging

    def abort_merge(self):
        self.calls.append("abort")
        self._merging = False

    def dirty_tracked(self):
        return []

    def pull(self):
        self.calls.append("pull")
        return self._conflicts.pop(0) if self._conflicts else []

    def commit(self, paths, msg):
        self.calls.append(("commit", msg))
        return True

    def push(self):
        self.calls.append("push")
        return True

    def stage_version(self, path, stage):
        return self.stages.get(stage)

    def add(self, path):
        self.calls.append(("add", str(path)))

    def take_theirs(self, paths):
        self.calls.append(("theirs", tuple(paths)))

    def finish_merge(self):
        self.calls.append("finish")


@pytest.fixture
def run(tmp_path, monkeypatch):
    """daily.run on an empty tree; returns (rc, ops, events) with the given step behaviours."""
    def go(ops=None, offline=True, core=True, download=None, lock=None, score=None):
        ops = ops or DailyOps()
        events = []
        monkeypatch.setattr(daily, "Ops", lambda root, *a, **k: ops)
        monkeypatch.setattr(daily.sec, "probe", lambda: "probe")
        monkeypatch.setattr(live, "update_latest", lambda *a, **k: None)
        monkeypatch.setattr(faa, "download", download or (lambda root, now: None))
        monkeypatch.setattr(live, "run_lock", lock or (lambda *a, **k: events.append("lock") or 0))
        monkeypatch.setattr(live, "run_score", score or (lambda *a, **k: 0))
        monkeypatch.setattr(daily, "rebuild", lambda root, pdf=True: ops.calls.append("rebuild"))
        rc = daily.run(now="2026-10-29T23:05:00Z", offline=offline, core=core, root=tmp_path)
        return rc, ops, events
    return go


def test_a_merge_left_by_an_earlier_run_is_aborted_first(run):
    rc, ops, _ = run(DailyOps(merging=True))
    assert ops.calls[0] == "abort" and rc == 0


def test_a_snapshot_failure_still_reaches_the_lock_and_fails_the_run(run):
    def bad_zip(root, now):
        raise zipfile.BadZipFile("File is not a zip file")
    rc, ops, events = run(offline=False, download=bad_zip)
    assert events == ["lock"] and ops.calls[-1] == "push" and rc == 1


def test_a_lock_failure_still_commits_and_pushes(run):
    def broken(*a, **k):
        raise RuntimeError("gh release view failed")
    rc, ops, _ = run(lock=broken)
    assert ("commit", "Daily update") in ops.calls and ops.calls[-1] == "push" and rc == 1


def test_the_score_is_pushed_before_the_rebuild(run, tmp_path):
    def score(now, offline, root):
        (root / "results/live").mkdir(parents=True, exist_ok=True)
        (root / "results/live/2026Q3_score.json").write_text("{}")
        return 0
    rc, ops, _ = run(core=False, score=score)
    c = ops.calls
    i = c.index(("commit", "Score the released quarter"))
    assert "push" in c[i:c.index("rebuild")] and rc == 0


def test_an_unparsable_results_8k_fails_the_run(run):
    rc, ops, _ = run(score=lambda *a, **k: 1)
    assert ops.calls[-1] == "push" and rc == 1


def test_a_conflicted_manifest_keeps_both_machines_dates(run, tmp_path):
    (tmp_path / "data/snapshots").mkdir(parents=True)
    ours = json.dumps({"backtest": "2026-10-19", "snapshots": {"2026-10-19": {}, "2026-10-28": {}}})
    theirs = json.dumps({"backtest": "2026-10-19", "snapshots": {"2026-10-19": {}, "2026-10-29": {}}})
    ops = DailyOps(conflicts=[[MAN, "results/live/2026Q3_path.csv"]], stages={2: ours, 3: theirs})
    rc, ops, _ = run(ops)
    merged = json.loads((tmp_path / MAN).read_text())
    assert sorted(merged["snapshots"]) == ["2026-10-19", "2026-10-28", "2026-10-29"]
    assert ("add", MAN) in ops.calls and ("theirs", ("results/live/2026Q3_path.csv",)) in ops.calls
    assert "finish" in ops.calls and rc == 0
