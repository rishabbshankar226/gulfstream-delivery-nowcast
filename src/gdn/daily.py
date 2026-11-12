"""`make daily` and `make daily-core` (§3.11).

Pull, download the snapshot, write the latest nowcast, path row and daily airframe table, lock when
§3.6 says so, score any released quarter, then (not for daily-core) rebuild the estimates, the
workbook, the note, the site data, the README's Live record and the post. Only the paths below are
staged; the run refuses to start when any other tracked file has uncommitted changes."""
import csv
import fcntl
import importlib
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path

from . import faa, live, sec
from .gitops import GitError, Ops
from .files import csv_text

LIVE_PATHS = ["data/snapshots", "results/live", "data/sec_manifest.json"]
REBUILD_PATHS = ["results/estimates.json", "output/gd_gulfstream_model.xlsx",
                 "output/gd_gulfstream_model.inputs.sha256", "report/note.html", "site/data.json", "README.md",
                 "docs/LINKEDIN_POST.md", "output/GD_research_note.pdf", "site/GD_research_note.pdf",
                 "output/GD_research_note.inputs.sha256"]
LOCK_PATHS = ["predictions"]
ALLOWED = LIVE_PATHS + REBUILD_PATHS + LOCK_PATHS
GENERATED = REBUILD_PATHS  # files `make all` writes that a daily run also rewrites


def _under(path, prefixes):
    return any(path == p or path.startswith(p.rstrip("/") + "/") for p in prefixes)


def _stage(mod, fn, **kw):
    if importlib.util.find_spec(f"gdn.{mod}") is None:
        print(f"skip {mod}: not written yet")
        return None
    return getattr(importlib.import_module(f"gdn.{mod}"), fn)(**kw)


def rebuild(root, pdf=True):
    _stage("estimates", "run", root=root)
    _stage("workbook", "run", root=root)
    _stage("note", "run", root=root)
    if pdf and sys.platform == "darwin" and not os.environ.get("CI"):
        _stage("note", "run_pdf", root=root)
    _stage("site_data", "run", root=root)
    _stage("report", "run", root=root)


def merge_manifests(ours, theirs):
    """Union of snapshot entries, refusing disagreement about the same date or backtest."""
    a, b = json.loads(ours), json.loads(theirs)
    if a.get("backtest") and b.get("backtest") and a["backtest"] != b["backtest"]:
        raise ValueError("backtest conflict: the two machines name different immutable snapshots")
    snaps = dict(a.get("snapshots", {}))
    def content(entry):
        # Two machines that download the same zip record different times for it; only the bytes matter.
        return {k: v for k, v in entry.items() if k != "downloaded_utc"}

    for date, entry in b.get("snapshots", {}).items():
        if date in snaps and content(snaps[date]) != content(entry):
            raise ValueError(f"snapshot conflict for {date}: resolve its manifest and files together")
    snaps.update(b.get("snapshots", {}))
    return json.dumps({"backtest": b.get("backtest") or a.get("backtest"),
                       "snapshots": dict(sorted(snaps.items()))}, indent=2) + "\n"


def merge_paths(ours, theirs):
    """Keep both machines' dated observations, preferring upstream on the same date.

    update_latest recomputes the newest observation after the merge from the merged daily table.
    """
    rows = {}
    for text in (ours, theirs):
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames != live.PATH_COLS:
            raise ValueError("path conflict: unexpected CSV header")
        for row in reader:
            if not row.get("date") or None in row or any(v is None for v in row.values()):
                raise ValueError("path conflict: malformed CSV row")
            rows[row["date"]] = row
    return csv_text(live.PATH_COLS, [rows[d] for d in sorted(rows)])


def run(now=None, offline=False, core=False, root="."):
    root = Path(root)
    lock_file = root / ".build/daily.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    held = open(lock_file, "w")
    try:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another daily run holds .build/daily.lock; this one stops")
        return 0
    try:
        return _run(now, offline, core, root)
    finally:
        fcntl.flock(held, fcntl.LOCK_UN)
        held.close()


def _run(now, offline, core, root):
    wall = now is None
    failed = 0  # a step that failed but let the run go on; the run still exits 1 so the failure shows
    now = live.parse_now(now)
    ops = Ops(root)
    if ops.merging():
        # An earlier run died mid-merge: never carry its conflicted files over.
        ops.abort_merge()
        print("aborted a merge an earlier run left unfinished")
    dirty = [p for p in ops.dirty_tracked() if not _under(p, ALLOWED)]
    if dirty:
        print(f"Refusing to run: uncommitted changes outside the daily job's paths: {dirty[:8]}")
        return 2
    if ops.dirty_tracked():
        ops.commit(ALLOWED, "Carry over uncommitted daily outputs")

    def on_conflict(paths):
        if any(p.startswith("results/live/") and p.endswith(("_lock.json", "_score.json", "_build.json"))
               for p in paths):
            print("Conflicting immutable live records require manual review")
            return False
        if all(_under(p, LIVE_PATHS) or _under(p, GENERATED) for p in paths):
            man = "data/snapshots/MANIFEST.json"
            merged = {}
            try:
                for p in paths:
                    merge = merge_manifests if p == man else (
                        merge_paths if p.startswith("results/live/") and p.endswith("_path.csv") else None)
                    if merge:
                        ours, theirs = ops.stage_version(p, 2), ops.stage_version(p, 3)
                        if ours is None or theirs is None:
                            raise ValueError(f"delete/modify conflict in {p}")
                        merged[p] = merge(ours, theirs)
            except ValueError as e:
                print(f"Cannot safely merge daily outputs: {e}")
                return False
            for p, text in merged.items():
                (root / p).write_text(text)
                ops.add(p)
            paths = [p for p in paths if p not in merged]
            ops.take_theirs(paths)
            ops.finish_merge()
            live.update_latest(root, now)
            if not core and any(_under(p, GENERATED) for p in paths):
                rebuild(root, pdf=False)
            ops.commit(LIVE_PATHS + REBUILD_PATHS, "Rebuild after merging upstream daily outputs")
            return True
        return False

    try:
        conflicted = ops.pull()
        if conflicted and not on_conflict(conflicted):
            ops.abort_merge()
            print(f"Merge conflict in hand-written files {conflicted}; resolve by hand.")
            return 2
    except GitError as e:
        print(f"git pull failed: {e}")
    if not offline:
        print(sec.probe())
    date = None
    try:
        # A bad zip or a changed FAA header must not cost the lock, which reads the newest stored subset.
        date = None if offline else faa.download(root, now)
        if date:
            live.ingest(root, date)
        live.update_latest(root, now)
    except Exception as e:  # noqa: BLE001
        print(f"snapshot step failed: {type(e).__name__}: {e}; carrying on to the lock")
        failed = 1
    ops.commit(LIVE_PATHS, f"Daily snapshot {date}" if date else "Daily nowcast without a new snapshot")

    def push_outputs():
        ops.commit(LIVE_PATHS, "Daily outputs before the lock")
        live.push_with_merge(ops, on_conflict=on_conflict)

    try:
        rc = live.run_lock(now, offline, root=root, ops=ops, before_prediction=push_outputs,
                           on_conflict=on_conflict, wall=wall)
    except Exception as e:  # noqa: BLE001
        print(f"lock step failed: {type(e).__name__}: {e}")
        rc = 1
    before = set(live.scores(root))
    try:
        failed = live.run_score(now, offline, root=root) or failed
    except Exception as e:  # noqa: BLE001
        print(f"score step failed: {type(e).__name__}: {e}")
        failed = 1
    if set(live.scores(root)) != before:
        live.update_latest(root, now)
        ops.commit(LIVE_PATHS, "Score the released quarter")
        try:
            live.push_with_merge(ops, on_conflict=on_conflict)
        except GitError as e:
            print(f"push of the score failed: {e}")
    if not core:
        try:
            rebuild(root)
        except Exception as e:  # noqa: BLE001  a rebuild error must not stop the live files reaching GitHub
            print(f"rebuild failed: {type(e).__name__}: {e}")
            rc = rc or 1
    ops.commit(LIVE_PATHS + REBUILD_PATHS, "Daily update" + (f" {date}" if date else ""))
    try:
        if not live.push_with_merge(ops, on_conflict=on_conflict):
            print("push failed three times; the commits stay local for the next run")
            return 1
    except GitError as e:
        print(f"push failed: {e}")
        return 1
    return rc or failed
