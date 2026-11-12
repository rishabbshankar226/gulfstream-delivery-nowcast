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
        return self.stages.get((path, stage), self.stages.get(stage))

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
    path = "results/live/2026Q3_path.csv"
    from gdn.files import csv_text
    path_text = csv_text(live.PATH_COLS, [])
    (tmp_path / path).parent.mkdir(parents=True)
    ops = DailyOps(conflicts=[[MAN, path]], stages={(MAN, 2): ours, (MAN, 3): theirs,
                                                   (path, 2): path_text, (path, 3): path_text})
    rc, ops, _ = run(ops)
    merged = json.loads((tmp_path / MAN).read_text())
    assert sorted(merged["snapshots"]) == ["2026-10-19", "2026-10-28", "2026-10-29"]
    assert ("add", MAN) in ops.calls and ("add", path) in ops.calls
    assert "finish" in ops.calls and rc == 0


def test_a_conflicted_path_keeps_both_machines_history(run, tmp_path):
    from gdn.files import csv_text, read_csv
    path = "results/live/2026Q3_path.csv"
    (tmp_path / path).parent.mkdir(parents=True)
    ours = csv_text(live.PATH_COLS, [{"date": "2026-10-27", "nowcast_total": 30},
                                      {"date": "2026-10-28", "nowcast_total": 31}])
    theirs = csv_text(live.PATH_COLS, [{"date": "2026-10-28", "nowcast_total": 32},
                                        {"date": "2026-10-29", "nowcast_total": 33}])
    (tmp_path / path).write_text(theirs)
    ops = DailyOps(conflicts=[[path]], stages={(path, 2): ours, (path, 3): theirs})
    rc, ops, _ = run(ops)
    rows = read_csv(tmp_path / path)
    assert [r["date"] for r in rows] == ["2026-10-27", "2026-10-28", "2026-10-29"]
    assert rows[1]["nowcast_total"] == "32"
    assert ("add", path) in ops.calls and "finish" in ops.calls and rc == 0


@pytest.mark.parametrize("field", ["backtest", "snapshots"])
def test_a_manifest_merge_refuses_different_immutable_inputs(field):
    ours = {"backtest": "2026-10-19", "snapshots": {"2026-10-19": {"zip_sha256": "aaa"}}}
    theirs = json.loads(json.dumps(ours))
    if field == "backtest":
        theirs[field] = "2026-10-20"
    else:
        theirs[field]["2026-10-19"]["zip_sha256"] = "bbb"
    with pytest.raises(ValueError, match="conflict"):
        daily.merge_manifests(json.dumps(ours), json.dumps(theirs))


def test_a_manifest_collision_aborts_before_finishing_the_merge(run, tmp_path):
    (tmp_path / "data/snapshots").mkdir(parents=True)
    ours = json.dumps({"backtest": "2026-10-19", "snapshots": {"2026-10-19": {"zip_sha256": "aaa"}}})
    theirs = json.dumps({"backtest": "2026-10-19", "snapshots": {"2026-10-19": {"zip_sha256": "bbb"}}})
    rc, ops, events = run(DailyOps(conflicts=[[MAN]], stages={2: ours, 3: theirs}))
    assert rc == 2 and "abort" in ops.calls and "finish" not in ops.calls and events == []


@pytest.mark.parametrize("suffix", ["lock", "score", "build"])
def test_immutable_live_records_are_not_resolved_by_taking_upstream(run, suffix):
    rc, ops, events = run(DailyOps(conflicts=[[f"results/live/2026Q3_{suffix}.json"]]))
    assert rc == 2 and "abort" in ops.calls and "finish" not in ops.calls and events == []


def test_daily_merges_diverged_path_history_in_real_git(tmp_path, monkeypatch):
    from gdn.files import csv_text, read_csv
    from gdn.gitops import Ops
    remote, first, second = (tmp_path / n for n in ("remote", "first", "second"))
    Ops(tmp_path).git("init", "--bare", "-q", str(remote))
    Ops(tmp_path).git("clone", "-q", str(remote), str(first))
    a = Ops(first)
    a.git("config", "user.name", "Test")
    a.git("config", "user.email", "test@example.invalid")
    path = "results/live/2026Q3_path.csv"
    (first / path).parent.mkdir(parents=True)
    base = {"date": "2026-10-27", "nowcast_total": 30}
    (first / path).write_text(csv_text(live.PATH_COLS, [base]))
    a.commit([path], "base")
    a.git("push", "-u", "origin", "HEAD")
    Ops(tmp_path).git("clone", "-q", str(remote), str(second))
    b = Ops(second)
    b.git("config", "user.name", "Test")
    b.git("config", "user.email", "test@example.invalid")
    (first / path).write_text(csv_text(live.PATH_COLS, [base, {"date": "2026-10-28", "nowcast_total": 31}]))
    a.commit([path], "local observation")
    (second / path).write_text(csv_text(live.PATH_COLS, [base, {"date": "2026-10-29", "nowcast_total": 32}]))
    b.commit([path], "upstream observation")
    assert b.push()
    monkeypatch.setattr(live, "update_latest", lambda *a, **k: None)
    monkeypatch.setattr(live, "run_lock", lambda *a, **k: 0)
    monkeypatch.setattr(live, "run_score", lambda *a, **k: 0)
    assert daily.run(now="2026-10-29T23:05:00Z", offline=True, core=True, root=first) == 0
    assert [r["date"] for r in read_csv(first / path)] == ["2026-10-27", "2026-10-28", "2026-10-29"]
    assert not a.merging() and not a.dirty_tracked() and a.ahead() == 0
    assert "2026-10-28" in a.git("show", f"origin/{a.git('branch', '--show-current').stdout.strip()}:{path}").stdout


def test_a_manifest_merge_accepts_the_same_zip_downloaded_at_two_times():
    # F014. Two machines that download the same file on the same date record different download times.
    # That is not a conflict: the zip and its subset hashes agree.
    e = {"zip_sha256": "aaa", "zip_bytes": 5, "files": {"MASTER.txt.gz": "h1"}}
    ours = {"backtest": "2026-10-19", "snapshots": {"2026-10-28": dict(e, downloaded_utc="2026-10-28T10:43:00Z")}}
    theirs = {"backtest": "2026-10-19", "snapshots": {"2026-10-28": dict(e, downloaded_utc="2026-10-28T06:20:00Z")}}
    merged = json.loads(daily.merge_manifests(json.dumps(ours), json.dumps(theirs)))
    assert merged["snapshots"]["2026-10-28"]["downloaded_utc"] == "2026-10-28T06:20:00Z"


def test_the_daily_rebuild_redraws_the_charts(monkeypatch, tmp_path):
    # F001. The charts carry the locked estimate and GD's count; before this fix only `make all` drew them, so the
    # tracked chart stayed at its 2026-10-19 state through the lock and the score.
    calls = []
    monkeypatch.setattr(daily, "_stage", lambda mod, fn, **kw: calls.append((mod, fn)))
    daily.rebuild(tmp_path, pdf=False)
    assert ("charts", "run") in calls
    assert calls.index(("charts", "run")) < calls.index(("note", "run"))     # the note embeds two of them
    assert "output/charts" in daily.REBUILD_PATHS
