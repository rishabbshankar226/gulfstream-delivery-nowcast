"""The lock rehearsal (Phase 5): every lock and score case against a local bare copy and a gh shim.

Nothing reaches GitHub: origin is a bare copy at
/tmp/gdn-rehearsal/github.com/rishabbshankar226/gulfstream-delivery-nowcast.git, whose path still
names the repository, and `gh` is a shim first on PATH that answers `release view`, `release create`
and `api repos/.../releases` from a JSON file. Writes docs/build/REHEARSAL.md.

Usage: .venv/bin/python tools/rehearsal.py
"""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
PY = REPO / ".venv/bin/python"
BASE = Path("/tmp/gdn-rehearsal")
SLUG = "rishabbshankar226/gulfstream-delivery-nowcast"
BARE = BASE / "github.com" / f"{SLUG}.git"
WORK, OTHER, PRISTINE = BASE / "work", BASE / "other", BASE / "pristine.git"
BIN, STATE, LOG = BASE / "bin", BASE / "gh_state.json", BASE / "gh_calls.log"
ET = ZoneInfo("America/New_York")
SEC_FIXTURE_ACCN = "0000040533-26-990001"

SHIM = r'''#!/usr/bin/env python3
"""gh shim for the lock rehearsal."""
import json, os, subprocess, sys
state_p, log_p = os.environ["GDN_SHIM_STATE"], os.environ["GDN_SHIM_LOG"]
args = sys.argv[1:]
with open(log_p, "a") as f:
    f.write(json.dumps(args) + "\n")
st = json.load(open(state_p))
def opt(name):
    return args[args.index(name) + 1] if name in args else None
if args[:2] == ["release", "view"]:
    r = st["releases"].get(args[2])
    if not r:
        print("release not found", file=sys.stderr)
        sys.exit(1)
    fields = (opt("--json") or "tagName,publishedAt").split(",")
    print(json.dumps({k: r[k] for k in fields}))
elif args[:2] == ["release", "create"]:
    tag, target = args[2], opt("--target")
    if tag in st["releases"]:
        print("a release with the same tag name already exists", file=sys.stderr)
        sys.exit(1)
    subprocess.run(["git", "--git-dir", os.environ["GDN_SHIM_BARE"], "tag", tag, target], check=True)
    now = os.environ["REHEARSAL_NOW"]
    st["releases"][tag] = {"tagName": tag, "publishedAt": now, "createdAt": now, "targetCommitish": target,
                           "name": opt("--title"), "body": opt("--notes")}
    json.dump(st, open(state_p, "w"))
    print("https://github.com/%s/releases/tag/%s" % (os.environ["GDN_SHIM_SLUG"], tag))
elif args and args[0] == "api" and args[1].endswith("/releases"):
    print(json.dumps([{"tag_name": r["tagName"], "published_at": r["publishedAt"], "created_at": r["createdAt"],
                       "target_commitish": r["targetCommitish"], "name": r["name"], "body": r["body"]}
                      for r in st["releases"].values()]))
else:
    print("gh shim: unsupported call %r" % (args,), file=sys.stderr)
    sys.exit(2)
'''

PRE_PUSH = r'''#!/bin/sh
# Rehearsal: the first push from the work clone loses a race to a commit from a second clone.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX
if [ ! -f "$GDN_RACE_MARKER" ]; then
  touch "$GDN_RACE_MARKER"
  cd "$GDN_OTHER" && git pull -q --no-rebase && echo race >> race.txt && git add race.txt \
    && git -c user.name=other -c user.email=other@example.invalid commit -qm "A competing push" && git push -q origin HEAD
fi
exit 0
'''

EXHIBIT = """<html><body><p>REHEARSAL FIXTURE, not a GD filing.</p>
<p>Supplemental Aerospace Data:</p><table>
<tr><td>Gulfstream Aircraft Deliveries (units):</td></tr>
<tr><td>Large-cabin aircraft</td><td>33</td><td>33</td><td>99</td><td>95</td></tr>
<tr><td>Mid-cabin aircraft</td><td>7</td><td>6</td><td>20</td><td>18</td></tr>
<tr><td>Total</td><td>40</td><td>39</td><td>119</td><td>113</td></tr>
<tr><td>Aerospace Book-to-Bill:</td></tr></table></body></html>
"""


def sh(*cmd, cwd=None, env=None, check=True):
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env, capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"{' '.join(map(str, cmd))} failed: {r.stderr or r.stdout}")
    return r


def et(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=ET).astimezone(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def env_for(now):
    e = dict(os.environ)
    e.update({"PATH": f"{BIN}:{e['PATH']}", "PYTHONPATH": str(WORK / "src"), "GDN_SHIM_STATE": str(STATE),
              "GDN_SHIM_LOG": str(LOG), "GDN_SHIM_BARE": str(BARE), "GDN_SHIM_SLUG": SLUG,
              "REHEARSAL_NOW": iso(now), "GDN_RACE_MARKER": str(BASE / "race.marker"), "GDN_OTHER": str(OTHER),
              "GIT_AUTHOR_NAME": "rehearsal", "GIT_AUTHOR_EMAIL": "rehearsal@example.invalid",
              "GIT_COMMITTER_NAME": "rehearsal", "GIT_COMMITTER_EMAIL": "rehearsal@example.invalid"})
    e.pop("SEC_UA", None)
    return e


def fresh(snapshots, race=False):
    """A clean bare copy, work clone and shim state, with stored snapshots for the given dates."""
    for p in (BASE / "github.com", WORK, OTHER, STATE, LOG, BASE / "race.marker"):
        shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
    BARE.parent.mkdir(parents=True)
    shutil.copytree(PRISTINE, BARE)
    sh("git", "clone", "-q", BARE, WORK)
    sh("git", "clone", "-q", BARE, OTHER)
    STATE.write_text(json.dumps({"releases": {}}))
    man_p = WORK / "data/snapshots/MANIFEST.json"
    man = json.loads(man_p.read_text())
    bt = man["backtest"]
    for d in snapshots:
        shutil.copytree(WORK / "data/snapshots" / bt, WORK / "data/snapshots" / d)
        man["snapshots"][d] = dict(man["snapshots"][bt], downloaded_utc=f"{d}T12:00:00Z")
        shutil.copy(WORK / f"data/snapshots/daily/{bt}.serials.csv.gz", WORK / f"data/snapshots/daily/{d}.serials.csv.gz")
    man_p.write_text(json.dumps({"backtest": man["backtest"], "snapshots": dict(sorted(man["snapshots"].items()))},
                                indent=2) + "\n")
    e = env_for(et("2026-10-28T12:00"))
    sh("git", "add", "data/snapshots", cwd=WORK, env=e)
    sh("git", "commit", "-qm", "Rehearsal snapshots", cwd=WORK, env=e)
    sh("git", "push", "-q", "origin", "HEAD", cwd=WORK, env=e)
    # Raw SEC files for the score case: the real submissions plus one fixture 8-K.
    raw = WORK / "data/raw/sec"
    shutil.copytree(REPO / "data/raw/sec/submissions", raw / "submissions")
    if race:
        hook = WORK / ".git/hooks/pre-push"
        hook.write_text(PRE_PUSH)
        hook.chmod(0o755)


def add_fixture_8k():
    raw = WORK / "data/raw/sec"
    p = raw / "submissions/CIK0000040533.json"
    j = json.loads(p.read_text())
    r = j["filings"]["recent"]
    for k in r:
        r[k].insert(0, {"accessionNumber": SEC_FIXTURE_ACCN, "filingDate": "2026-10-30", "reportDate": "2026-10-30",
                        "form": "8-K", "items": "2.02,9.01", "primaryDocument": "fixture.htm"}.get(k, ""))
    p.write_text(json.dumps(j))
    d = raw / SEC_FIXTURE_ACCN
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.json").write_text(json.dumps({"directory": {"item": [{"name": "fixture-exhibit991.htm"}]}}))
    (d / "fixture-exhibit991.htm").write_text(EXHIBIT)


def gdn(stage, when, *extra):
    now = et(when)
    r = sh(PY, "-m", "gdn", stage, "--now", iso(now), *extra, cwd=WORK, env=env_for(now), check=False)
    return r


def state():
    return json.loads(STATE.read_text())["releases"]


def tracked(path):
    return bool(sh("git", "ls-files", path, cwd=WORK).stdout.strip())


def upstream_has(path):
    sh("git", "fetch", "-q", "origin", cwd=WORK)
    return sh("git", "cat-file", "-e", f"origin/main:{path}", cwd=WORK, check=False).returncode == 0


def gate_live():
    g = Path.home() / "Desktop/prompt library/gulfstream-delivery-nowcast/gate/jetgate.py"
    gp = Path.home() / ".cache/jetgate/venv/bin/python"
    sh("git", "pull", "-q", "--no-rebase", "--tags", cwd=WORK, env=env_for(et("2026-10-30T12:30")))
    r = sh(gp, g, "--repo", WORK, "--only", "live", cwd=BASE, env=env_for(et("2026-10-30T12:30")), check=False)
    return r


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    BIN.mkdir(exist_ok=True)
    (BIN / "gh").write_text(SHIM)
    (BIN / "gh").chmod(0o755)
    shutil.rmtree(PRISTINE, ignore_errors=True)
    sh("git", "clone", "-q", "--bare", REPO, PRISTINE)
    head = sh("git", "rev-parse", "--short", "HEAD", cwd=REPO).stdout.strip()
    rows = []

    def record(case, cmd, r, expect, ok, saw):
        rows.append((case, cmd, r.returncode, expect, saw, "pass" if ok else "FAIL"))

    # 1. Eve, 18:00 ET, newest snapshot the day before: no lock yet.
    fresh(["2026-10-28"])
    r = gdn("lock", "2026-10-29T18:00")
    record("Eve 18:00 ET, older snapshot", "gdn lock --now 2026-10-29 18:00 ET", r, "no lock",
           not state() and not (WORK / "predictions/2026Q3.json").exists(), "no release, no prediction")

    # 2. Eve, 19:00 ET, older snapshot: lock.
    fresh(["2026-10-28"])
    r = gdn("lock", "2026-10-29T19:00")
    rel = state().get("lock-2026Q3")
    lk = json.loads((WORK / "results/live/2026Q3_lock.json").read_text()) if (WORK / "results/live/2026Q3_lock.json").exists() else {}
    pred = json.loads((WORK / "predictions/2026Q3.json").read_text()) if (WORK / "predictions/2026Q3.json").exists() else {}
    ok = bool(rel) and upstream_has("predictions/2026Q3.json") and upstream_has("results/live/2026Q3_lock.json") \
        and lk.get("published_at") == "2026-10-29T23:00:00Z" and pred.get("snapshot") == "2026-10-28" \
        and rel["body"] == f"sha256 {lk.get('sha256')}"
    record("Eve 19:00 ET, older snapshot", "gdn lock --now 2026-10-29 19:00 ET", r, "lock from 2026-10-28",
           ok, f"release published {lk.get('published_at')}, snapshot {pred.get('snapshot')}, sha256 in notes")
    # 3. A second lock attempt the same evening.
    r = gdn("lock", "2026-10-29T21:00")
    record("Second lock", "gdn lock --now 2026-10-29 21:00 ET", r, "refused, one lock per quarter",
           len(state()) == 1 and r.returncode == 0, "still one release")
    # 4. A release with no _lock.json: the next run writes it.
    e = env_for(et("2026-10-30T06:00"))
    sh("git", "rm", "-q", "results/live/2026Q3_lock.json", cwd=WORK, env=e)
    sh("git", "commit", "-qm", "Rehearsal: drop the lock record", cwd=WORK, env=e)
    sh("git", "push", "-q", "origin", "HEAD", cwd=WORK, env=e)
    r = gdn("lock", "2026-10-30T07:00")
    record("Release without _lock.json", "gdn lock --now 2026-10-30 07:00 ET", r, "writes _lock.json from the release",
           upstream_has("results/live/2026Q3_lock.json") and len(state()) == 1, "lock record restored, no new release")
    # 5. Score on a fixture 8-K.
    add_fixture_8k()
    r = gdn("score", "2026-10-30T12:00", "--offline")
    sc = WORK / "results/live/2026Q3_score.json"
    s = json.loads(sc.read_text()) if sc.exists() else {}
    record("Score on a fixture 8-K", "gdn score --offline --now 2026-10-30 12:00 ET", r,
           "score with the lock", s.get("locked") is True and s.get("reported", {}).get("total") == 40,
           f"locked {s.get('locked')}, reported {s.get('reported')}, AE {s.get('ae_total')}")
    e = env_for(et("2026-10-30T12:05"))
    sh("git", "add", "results/live/2026Q3_score.json", cwd=WORK, env=e)
    sh("git", "commit", "-qm", "Rehearsal score", cwd=WORK, env=e)
    sh("git", "push", "-q", "origin", "HEAD", cwd=WORK, env=e)
    g = gate_live()
    gate_line = (g.stdout.strip().splitlines() or ["(no output)"])
    rows.append(("Gate `live` on the work clone", "jetgate.py --only live, shim on PATH", g.returncode,
                 "no failing code", " / ".join(gate_line[:4]), "pass" if " 0 failing" in gate_line[0] else "FAIL"))

    # 6. Eve with a same-day snapshot, in the morning.
    fresh(["2026-10-28", "2026-10-29"])
    r = gdn("lock", "2026-10-29T08:00")
    pred = json.loads((WORK / "predictions/2026Q3.json").read_text()) if (WORK / "predictions/2026Q3.json").exists() else {}
    record("Eve 08:00 ET, same-day snapshot", "gdn lock --now 2026-10-29 08:00 ET", r, "lock from 2026-10-29",
           bool(state()) and pred.get("snapshot") == "2026-10-29", f"snapshot {pred.get('snapshot')}")

    # 7. Eve, 23:59 ET.
    fresh(["2026-10-28"])
    r = gdn("lock", "2026-10-29T23:59")
    record("Eve 23:59 ET", "gdn lock --now 2026-10-29 23:59 ET", r, "lock",
           bool(state()) and state()["lock-2026Q3"]["publishedAt"] == "2026-10-30T03:59:00Z", "release at 03:59 UTC")

    # 8. Release date, 00:00 ET: no late lock.
    fresh(["2026-10-28", "2026-10-29"])
    r = gdn("lock", "2026-10-30T00:00")
    record("Release date 00:00 ET", "gdn lock --now 2026-10-30 00:00 ET", r, "no lock",
           not state() and not (WORK / "predictions/2026Q3.json").exists(), (r.stdout.strip() or "no output")[:90])

    # 9. A rejected push: a second clone pushes first.
    fresh(["2026-10-28"], race=True)
    r = gdn("lock", "2026-10-29T19:30")
    ok = len(state()) == 1 and upstream_has("race.txt") and upstream_has("predictions/2026Q3.json")
    tgt = state().get("lock-2026Q3", {}).get("targetCommitish", "")
    in_up = sh("git", "merge-base", "--is-ancestor", tgt, "origin/main", cwd=WORK, check=False).returncode == 0 if tgt else False
    record("Rejected push", "gdn lock --now 2026-10-29 19:30 ET, second clone pushes first", r,
           "reset to upstream, lock on retry", ok and in_up and "lock push rejected (attempt 1)" in r.stdout,
           "attempt 1 rejected and reset; competing commit kept; lock target on main")

    # 10. The eve through make daily-core (offline download), as the session's 19:05 waiter runs it.
    fresh(["2026-10-28"])
    r = gdn("daily", "2026-10-29T19:05", "--core", "--offline")
    record("make daily-core on the eve", "gdn daily --core --offline --now 2026-10-29 19:05 ET", r,
           "daily outputs pushed, then the lock", bool(state()) and upstream_has("results/live/2026Q3_lock.json"),
           "release and lock record on main")

    lines = ["# Lock rehearsal", "",
             f"Run by `tools/rehearsal.py` on {dt.date.today().isoformat()} from commit {head}. Origin is a bare copy at "
             f"`{BARE}` and `gh` is a shim first on PATH that answers from `{STATE}`. Times are ET; the "
             "release date is 2026-10-30. Nothing here reached GitHub.", "",
             "| Case | Command | Exit | Expected | Observed | Result |", "|---|---|---|---|---|---|"]
    for case, cmd, rc, expect, saw, res in rows:
        lines.append(f"| {case} | `{cmd}` | {rc} | {expect} | {saw} | {res} |")
    out = "\n".join(lines) + "\n"
    (REPO / "docs/build/REHEARSAL.md").write_text(out)
    print(out)
    return 0 if all(r[-1] == "pass" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
