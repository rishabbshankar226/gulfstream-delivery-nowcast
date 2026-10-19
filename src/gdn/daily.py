"""`make daily` and `make daily-core` (§3.11).

Pull, download the snapshot, write the latest nowcast, path row and daily airframe table, lock when
§3.6 says so, score any released quarter, then (not for daily-core) rebuild the estimates, the
workbook, the note, the site data, the README's Live record and the post. Only the paths below are
staged; the run refuses to start when any other tracked file has uncommitted changes."""
import importlib
import importlib.util
import os
import shutil
import sys
from pathlib import Path

from . import faa, live
from .gitops import GitError, Ops

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


def run(now=None, offline=False, core=False, root="."):
    root = Path(root)
    now = live.parse_now(now)
    ops = Ops(root)
    dirty = [p for p in ops.dirty_tracked() if not _under(p, ALLOWED)]
    if dirty:
        print(f"Refusing to run: uncommitted changes outside the daily job's paths: {dirty[:8]}")
        return 2
    if ops.dirty_tracked():
        ops.commit(ALLOWED, "Carry over uncommitted daily outputs")

    def on_conflict(paths):
        if all(_under(p, LIVE_PATHS) or _under(p, GENERATED) for p in paths):
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
    date = None if offline else faa.download(root, now)
    if date:
        live.ingest(root, date)
    live.update_latest(root, now)
    ops.commit(LIVE_PATHS, f"Daily snapshot {date}" if date else "Daily nowcast without a new snapshot")

    def push_outputs():
        ops.commit(LIVE_PATHS, "Daily outputs before the lock")
        live.push_with_merge(ops, on_conflict=on_conflict)

    rc = live.run_lock(now, offline, root=root, ops=ops, before_prediction=push_outputs)
    before = set(live.scores(root))
    live.run_score(now, offline, root=root)
    if set(live.scores(root)) != before:
        live.update_latest(root, now)
    if not core:
        rebuild(root)
    ops.commit(LIVE_PATHS + REBUILD_PATHS, "Daily update" + (f" {date}" if date else ""))
    try:
        if not live.push_with_merge(ops, on_conflict=on_conflict):
            print("push failed three times; the commits stay local for the next run")
            return 1
    except GitError as e:
        print(f"push failed: {e}")
        return 1
    return rc
