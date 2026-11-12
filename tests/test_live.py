"""The lock's timing and steps (§3.6) with fixed clocks and a fake git/gh, and the score."""
import datetime as dt
import json
import shutil
from pathlib import Path

import pytest

from conftest import FIXTURES, ROOT
from gdn import events, faa, live
from gdn.files import write_json
from gdn.gitops import GitError, Ops

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

    def file_at_ref(self, ref, path):
        return (self.root / path).read_bytes()

    def abort_merge(self):
        pass


class LocalReleaseOps(Ops):
    """Real local Git objects, with only remote and GitHub operations replaced."""

    def __init__(self, root, clock):
        super().__init__(root, log=lambda *a: None)
        self.clock, self.released = clock, None
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")

    def pull(self):
        return []

    def push(self):
        return True

    def release_view(self, tag):
        return self.released

    def release_create(self, tag, target, title, notes):
        self.git("tag", tag, target)
        self.released = {"tagName": tag, "publishedAt": live.stamp(self.clock)}

    def fetch_tag(self, tag):
        pass


def test_lock_works_with_a_relative_repository_root(repo, monkeypatch):
    when = at("2026-10-29T19:00")
    ops = LocalReleaseOps(repo, when)
    ops.commit(["data", "config", "results"], "fixture inputs")
    monkeypatch.chdir(repo.parent)
    assert live.run_lock(when, root=repo.name, ops=ops, log=lambda *a: None) == 0
    assert (repo / "results/live/2026Q3_lock.json").exists()


def test_lock_record_refuses_prediction_that_differs_from_the_release_tag(repo):
    when = at("2026-10-29T19:00")
    ops = LocalReleaseOps(repo, when)
    p = live.prediction_path(repo, "2026Q3")
    write_json(p, {"quarter": "2026Q3", "nowcast": {"total": 30}})
    target = ops.commit_only(p, "original prediction")
    ops.release_create("lock-2026Q3", target, "lock", "")
    write_json(p, {"quarter": "2026Q3", "nowcast": {"total": 999}})
    with pytest.raises(GitError, match="prediction.*tag"):
        live.write_lock_json(repo, "2026Q3", ops)
    assert not live.lock_json_path(repo, "2026Q3").exists()


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


@pytest.mark.parametrize("state", ["new", "recover", "exists", "recorded"])
def test_a_lock_record_that_cannot_be_pushed_fails_the_run(repo, state):
    when = at("2026-10-29T19:00")

    class RejectRecord(FakeOps):
        def push(self):
            return not (repo / "results/live/2026Q3_lock.json").exists()

    ops = RejectRecord(repo, when)
    if state in ("recover", "recorded"):
        lock(repo, "2026-10-29T19:00")
        if state == "recover":
            (repo / "results/live/2026Q3_lock.json").unlink()
        else:
            ops.ahead = lambda: 1
        ops.released = {"tagName": "lock-2026Q3", "publishedAt": live.stamp(when)}
    elif state == "exists":
        original = ops.release_view
        views = []

        def created_between_pulls(tag):
            views.append(tag)
            if len(views) > 1:
                ops.released = {"tagName": tag, "publishedAt": live.stamp(when)}
            return original(tag)

        write_json(repo / "predictions/2026Q3.json", {"quarter": "2026Q3", "snapshot": "2026-10-29"})
        ops.release_view = created_between_pulls
    assert live.run_lock(when, root=repo, ops=ops, log=lambda *a: None) == 1


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


class ConflictOnce(FakeOps):
    """The first pulls come back conflicted, as when the other machine pushed live files mid-run."""

    def __init__(self, *a, conflicts=2, **kw):
        super().__init__(*a, **kw)
        self.pulls, self.aborts, self.conflicts = 0, 0, conflicts

    def pull(self):
        self.pulls += 1
        return ["results/live/2026Q3_latest.json"] if self.pulls <= self.conflicts else []

    def abort_merge(self):
        self.aborts += 1


def test_conflicted_pull_aborts_and_retries(repo):
    ops = ConflictOnce(repo, at("2026-10-29T19:30"))
    rc = live.run_lock(at("2026-10-29T19:30"), root=repo, ops=ops, log=lambda *a: None)
    # The opening pull and the first attempt's pull both conflict; both merges are aborted and attempt 2 locks.
    assert rc == 0 and ops.aborts == 2 and len(ops.creates) == 1


def test_wall_clock_stops_a_late_lock(repo, monkeypatch):
    # The run started at 19:00 ET by its own clock, but the real clock already reads 23:55 ET.
    monkeypatch.setattr(live, "utcnow", lambda: at("2026-10-29T23:55"))
    ops = FakeOps(repo, at("2026-10-29T19:00"))
    rc = live.run_lock(at("2026-10-29T19:00"), root=repo, ops=ops, log=lambda *a: None, wall=True)
    assert rc == 1 and not ops.creates and not (repo / "predictions/2026Q3.json").exists()


def test_commit_refuses_conflict_markers(tmp_path):
    import subprocess
    from gdn.gitops import GitError, Ops
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for k, v in (("user.name", "t"), ("user.email", "t@example.invalid")):
        subprocess.run(["git", "-C", str(tmp_path), "config", k, v], check=True)
    f = tmp_path / "results/live/x.json"
    f.parent.mkdir(parents=True)
    f.write_text("{\n<<<<<<< HEAD\n  \"a\": 1\n=======\n  \"a\": 2\n>>>>>>> theirs\n}\n")
    with pytest.raises(GitError, match="conflict markers"):
        Ops(tmp_path, log=lambda *a: None).commit(["results"], "x")


def test_daily_runs_one_at_a_time(tmp_path, capsys):
    import fcntl
    from gdn import daily
    (tmp_path / ".build").mkdir()
    with open(tmp_path / ".build/daily.lock", "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert daily.run(root=tmp_path, offline=True) == 0
    assert "holds .build/daily.lock" in capsys.readouterr().out


def test_manifest_merge_keeps_both_sides():
    from gdn import daily
    ours = json.dumps({"backtest": "2026-10-19", "snapshots": {"2026-10-19": {"z": 1}, "2026-10-28": {"z": 2}}})
    theirs = json.dumps({"backtest": "2026-10-19", "snapshots": {"2026-10-19": {"z": 1}, "2026-10-29": {"z": 3}}})
    merged = json.loads(daily.merge_manifests(ours, theirs))
    assert sorted(merged["snapshots"]) == ["2026-10-19", "2026-10-28", "2026-10-29"]


class SlowPush(FakeOps):
    """The prediction's push takes the real clock to within minutes of midnight ET."""

    def __init__(self, *a, box, late, **kw):
        super().__init__(*a, **kw)
        self.box, self.late = box, late

    def push(self):
        self.box[0] = self.late
        return super().push()


def test_clock_crossing_the_margin_during_the_push_stops_the_release(repo, monkeypatch):
    box = [at("2026-10-29T19:20")]
    monkeypatch.setattr(live, "utcnow", lambda: box[0])
    ops = SlowPush(repo, at("2026-10-29T19:00"), box=box, late=at("2026-10-29T23:55"))
    rc = live.run_lock(at("2026-10-29T19:00"), root=repo, ops=ops, log=lambda *a: None, wall=True)
    assert rc == 1 and not ops.creates
    # The committed prediction carries the time it was computed, not the time the run started.
    assert json.loads((repo / "predictions/2026Q3.json").read_text())["made_utc"] == "2026-10-29T23:20:00Z"


class CreatedElsewhere(FakeOps):
    """gh release create fails because the other machine created the release a moment earlier."""

    def release_create(self, tag, target, title, notes):
        from gdn.gitops import GitError
        self.released = {"tagName": tag, "publishedAt": "2026-10-29T23:01:00Z"}
        raise GitError("gh release create failed: a release with the same tag name already exists")


def test_a_release_created_by_another_run_is_recorded(repo):
    ops = CreatedElsewhere(repo, at("2026-10-29T19:00"))
    rc = live.run_lock(at("2026-10-29T19:00"), root=repo, ops=ops, log=lambda *a: None)
    lock_obj = json.loads((repo / "results/live/2026Q3_lock.json").read_text())
    assert rc == 0 and lock_obj["published_at"] == "2026-10-29T23:01:00Z"


def fixture_zip(path, drop_master_row=False):
    import zipfile
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as z:
        for k in faa.FILES:
            text = (FIXTURES / "faa" / f"{k}.txt").read_bytes().decode("utf-8")
            if drop_master_row and k == "MASTER":
                lines = text.splitlines(keepends=True)
                text = "".join(lines[:1] + lines[2:])
            z.writestr(f"{k}.txt", text)


def test_ingest_stores_the_subset_only_in_the_lock_window(repo):
    for date in ("2026-10-22", "2026-10-23", "2026-10-30"):
        fixture_zip(faa.zip_path(repo, date))
        live.ingest(repo, date, log=lambda *a: None)
        assert live.table_path(repo, date).exists()
    stored = set(faa.manifest(repo)["snapshots"])
    # Seven days before 2026-10-30 is 2026-10-23; the release date itself is outside the window.
    assert "2026-10-23" in stored and "2026-10-22" not in stored and "2026-10-30" not in stored


def test_ingest_keeps_a_subset_that_a_prediction_names(repo):
    date = "2026-10-24"
    fixture_zip(faa.zip_path(repo, date))
    live.ingest(repo, date, log=lambda *a: None)
    before = {p.name: p.read_bytes() for p in (repo / "data/snapshots" / date).iterdir()}
    entry = faa.manifest(repo)["snapshots"][date]
    write_json(repo / "predictions/2026Q3.json", {"quarter": "2026Q3", "snapshot": date})
    fixture_zip(faa.zip_path(repo, date), drop_master_row=True)
    live.ingest(repo, date, log=lambda *a: None)
    assert {p.name: p.read_bytes() for p in (repo / "data/snapshots" / date).iterdir()} == before
    assert faa.manifest(repo)["snapshots"][date] == entry


def test_path_rows_one_per_date(repo):
    now = at("2026-10-28T09:00")
    live.update_latest(repo, now, log=lambda *a: None)
    live.update_latest(repo, now, log=lambda *a: None)
    path = repo / "results/live/2026Q3_path.csv"
    assert [r.split(",")[0] for r in path.read_text().splitlines()[1:]] == ["2026-10-28"]
    live.write_table(repo, "2026-10-29", live.read_table(repo, "2026-10-28"))
    live.update_latest(repo, at("2026-10-29T09:00"), log=lambda *a: None)
    assert [r.split(",")[0] for r in path.read_text().splitlines()[1:]] == ["2026-10-28", "2026-10-29"]


def test_build_file_is_written_once(repo):
    live.write_build(repo, now=at("2026-10-27T09:00"))
    p = repo / "results/live/2026Q3_build.json"
    first = p.read_bytes()
    live.write_build(repo, now=at("2026-10-28T09:00"))
    assert p.read_bytes() == first


def score_file(repo, q, total, nowcast=None):
    write_json(repo / f"results/live/{q}_score.json",
               {"quarter": q, "reported": {"large": total - 6, "mid": 6, "total": total}, "accn": "x",
                "locked": nowcast is not None, "nowcast": {"total": nowcast} if nowcast is not None else None})


def test_a_score_moves_the_live_quarter_and_joins_the_history(repo):
    assert live.live_quarter(repo) == "2026Q3"
    score_file(repo, "2026Q3", 40, nowcast=37.5)
    assert live.live_quarter(repo) == "2026Q4"
    assert live.reported_history(repo)["2026Q3"] == {"large": 34, "mid": 6, "total": 40}
    # The locked error (37.5 - 40) joins the band's errors after the design and holdout ones.
    assert live.band_errors(repo)[-1] == -2.5 and len(live.band_errors(repo)) == 21


def test_a_live_quarter_without_a_fiscal_end_is_logged_not_raised(repo):
    score_file(repo, "2026Q3", 40)
    score_file(repo, "2026Q4", 45)
    msgs = []
    assert live.live_quarter(repo) == "2027Q1"
    assert live.update_latest(repo, at("2027-02-01T09:00"), log=msgs.append) is None
    assert any("fiscal end" in m for m in msgs)


class FakeSEC:
    body = ""

    def __init__(self, root, network=True):
        pass

    def filings(self, refresh=True):
        return []

    def exhibit_991(self, accn):
        return "ex99.htm", self.body

    def save_manifest(self):
        pass


@pytest.mark.parametrize("fixture,scored", [("with_sentence.htm", True), (None, False)])
def test_the_score_waits_for_the_8k_not_the_calendar(repo, monkeypatch, fixture, scored):
    from gdn import sec
    (repo / "data/guidance.csv").write_text(
        "call_date,year,outlook,quote,speaker,url\n2026-07-29,2026,160,about 160,CFO,u\n")
    # An 8-K whose exhibit has no delivery table is logged and left unscored, not raised.
    FakeSEC.body = (FIXTURES / "releases" / fixture).read_bytes() if fixture else b"<p>Other news</p>"
    monkeypatch.setattr(sec, "Client", FakeSEC)
    monkeypatch.setattr(sec, "results_8k", lambda filings, end: {"accn": "0000040533-26-000099"})
    # 2026-10-20: after the quarter's end (2026-10-04), ten days before the calendar's release date.
    rc = live.run_score(at("2026-10-20T09:00"), root=repo, log=lambda *a: None)
    assert (repo / "results/live/2026Q3_score.json").exists() is scored and rc == (0 if scored else 1)


class PullBringsAScore(FakeOps):
    """The pull brings the other machine's score for 2026Q3, so there is nothing left to lock."""

    def pull(self):
        score_file(self.root, "2026Q3", 40)
        return []


def test_the_lock_pulls_before_it_reads_local_state(repo):
    ops = PullBringsAScore(repo, at("2026-10-29T19:30"))
    assert live.run_lock(at("2026-10-29T19:30"), root=repo, ops=ops, log=lambda *a: None) == 0
    assert ops.creates == [] and not (repo / "predictions/2026Q3.json").exists()


def test_a_real_gdn_lock_checks_the_wall_clock(monkeypatch):
    from gdn import __main__ as cli
    seen = []
    monkeypatch.setattr(live, "run_lock", lambda **kw: seen.append(kw["wall"]) or 0)
    cli.main(["lock"])
    cli.main(["lock", "--now", "2026-10-29T23:05:00Z"])
    assert seen == [True, False]


def test_a_prediction_left_without_a_release_is_logged_as_missed(repo):
    write_json(repo / "predictions/2026Q3.json", {"quarter": "2026Q3", "snapshot": "2026-10-29"})
    msgs = []
    ops = FakeOps(repo, at("2026-10-30T07:00"))
    assert live.run_lock(at("2026-10-30T07:00"), root=repo, ops=ops, log=msgs.append) == 0
    assert ops.creates == [] and any("committed but no release was made" in m for m in msgs)


def test_no_lock_from_a_subset_that_predates_the_quarter_end(repo):
    # F017. Every download in the lock window failed, so the newest stored subset is an old one, dated before
    # 2026Q3 ended (2026-10-04). A lock from it would publish a partial count as the quarter's estimate.
    man = faa.manifest(repo)
    shutil.copytree(repo / "data/snapshots/2026-10-27", repo / "data/snapshots/2026-09-20")
    faa.save_manifest(repo, {"backtest": "2026-09-20", "snapshots": {"2026-09-20": man["snapshots"]["2026-10-27"]}})
    live.write_table(repo, "2026-10-28", [])
    msgs = []
    ops = FakeOps(repo, at("2026-10-29T19:00"))
    rc = live.run_lock(at("2026-10-29T19:00"), root=repo, ops=ops, log=msgs.append)
    assert rc == 1 and not ops.creates and not (repo / "predictions/2026Q3.json").exists()
    assert any("fiscal end" in m for m in msgs)


@pytest.mark.parametrize("accepted,scored", [("2026-10-30T12:09:27.000Z", True), ("2026-10-29T12:00:00.000Z", False)])
def test_a_lock_published_after_the_filing_is_not_scored(repo, monkeypatch, accepted, scored):
    # F018. The release date in config/calendar.json is typed by hand. If it is a day late, the lock is published
    # after GD has reported. SEC's acceptance time of the 8-K is the check: such a lock is never scored as a lock.
    from gdn import sec
    (repo / "data/guidance.csv").write_text(
        "call_date,year,outlook,quote,speaker,url\n2026-07-29,2026,160,about 160,CFO,u\n")
    lock(repo, "2026-10-29T19:00")          # published at 2026-10-29T23:00:00Z
    FakeSEC.body = (FIXTURES / "releases" / "with_sentence.htm").read_bytes()
    monkeypatch.setattr(sec, "Client", FakeSEC)
    monkeypatch.setattr(sec, "results_8k", lambda filings, end: {"accn": "0000040533-26-000099", "accepted": accepted})
    msgs = []
    rc = live.run_score(at("2026-10-31T09:00"), root=repo, log=msgs.append)
    assert (repo / "results/live/2026Q3_score.json").exists() is scored and rc == (0 if scored else 1)
    assert scored or any("not before" in m for m in msgs)
