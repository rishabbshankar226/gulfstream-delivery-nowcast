# Review round 1: ops auditor

Reviewer: a fresh subagent that built nothing here, working from `docs/build/briefs/review1_ops.md`. Read `src/gdn/live.py`, `src/gdn/daily.py`, `src/gdn/gitops.py`, `Makefile` and `.github/workflows/nowcast.yml` against §3.5, §3.6 and §3.11 of the prompt, plus the pieces they call (`faa.download`, `sec.Client`, `note.disclosure`, `files.write_gz`) and `CLAUDE.md`'s eve plan. Reran the lock rehearsal, then ran four checks of my own (R1, R2, M1, M2 below) with `tools/rehearsal.py`'s helpers pointed at a scratch base outside the repository, plus read-only `gh` queries. Nothing was pushed to GitHub and no release was created there. `docs/build/REHEARSAL.md` was restored with `git checkout -- docs/build/REHEARSAL.md`.

The repository moved while I worked: HEAD was 9b84384 when I started, the rehearsal cloned 069cb0f, and my own checks cloned 062e00e. None of those commits touched `live.py`, `daily.py`, `gitops.py`, `faa.py`, the Makefile or the workflow.

## Rehearsal table (copied from the rerun)

Run by `tools/rehearsal.py` on 2026-10-19 from commit 069cb0f. Exit 0.

| Case | Command | Exit | Expected | Observed | Result |
|---|---|---|---|---|---|
| Eve 18:00 ET, older snapshot | `gdn lock --now 2026-10-29 18:00 ET` | 0 | no lock | no release, no prediction | pass |
| Eve 19:00 ET, older snapshot | `gdn lock --now 2026-10-29 19:00 ET` | 0 | lock from 2026-10-28 | release published 2026-10-29T23:00:00Z, snapshot 2026-10-28, sha256 in notes | pass |
| Second lock | `gdn lock --now 2026-10-29 21:00 ET` | 0 | refused, one lock per quarter | still one release | pass |
| Release without _lock.json | `gdn lock --now 2026-10-30 07:00 ET` | 0 | writes _lock.json from the release | lock record restored, no new release | pass |
| Score on a fixture 8-K | `gdn score --offline --now 2026-10-30 12:00 ET` | 0 | score with the lock | locked True, reported {'large': 33, 'mid': 7, 'total': 40}, AE 8.868220015278837 | pass |
| Gate `live` on the work clone | `jetgate.py --only live, shim on PATH` | 0 | no failing code | 5 assertions, 0 failing, 1 warning / WARN L4 [('2026Q3', 'release not parsed; score checked for arithmetic only')] | each released quarter is scored against GD's reported count | pass |
| Eve 08:00 ET, same-day snapshot | `gdn lock --now 2026-10-29 08:00 ET` | 0 | lock from 2026-10-29 | snapshot 2026-10-29 | pass |
| Eve 23:59 ET | `gdn lock --now 2026-10-29 23:59 ET` | 0 | lock | release at 03:59 UTC | pass |
| Release date 00:00 ET | `gdn lock --now 2026-10-30 00:00 ET` | 0 | no lock | 2026Q3 missed its lock window (release 2026-10-30); no late lock | pass |
| Rejected push | `gdn lock --now 2026-10-29 19:30 ET, second clone pushes first` | 0 | reset to upstream, lock on retry | attempt 1 rejected and reset; competing commit kept; lock target on main | pass |
| make daily-core on the eve | `gdn daily --core --offline --now 2026-10-29 19:05 ET` | 0 | daily outputs pushed, then the lock | release and lock record on main | pass |

What the rehearsal does not cover: the runner's environment, the full `make daily` (only `daily-core`), a conflicting push from the other machine during a lock, two Mac runs on one tree, and a wall clock that moves during a run. My checks below cover the first four. One path stays untested by the rehearsal and by my checks alike: the `on_conflict` handler for a conflict at the job's first pull (`daily.py:59-75`, take upstream's copy, finish the merge, recompute, commit). In M1 the markers were committed before any later pull could see a conflict, so `on_conflict` never ran in any case.

## My own checks

Script: `opscheck.py` in this session's scratchpad. It imports `tools/rehearsal.py` as a module (its `main()` never runs) and points `BASE`, `BARE`, `WORK`, `OTHER` and the gh shim at a scratch directory. Each case starts from `fresh(["2026-10-28"])`.

| Check | Setup | Exit | Observed |
|---|---|---|---|
| R1 runner, eve | full `gdn daily --offline --now 2026-10-29 20:17 ET`; `data/raw` deleted, `HOME` an empty dir (no `~/.gdn_disclosure`, no `~/.sec_ua`), `CI=true` | 0 | Locked 2026Q3; workbook, note, site data, README and post rebuilt; `git status` clean; 0 commits ahead; `_lock.json` on origin; note's `id="disclosure"` carried over from the tracked `report/note.html` |
| R2 runner, release date | fresh clone of R1's origin, only `data/raw/sec/submissions` plus the fixture 8-K (what a fetch would bring); full `gdn daily --offline --now 2026-10-30 08:17 ET` | 0 | `scored 2026Q3: GD reported 40, locked 31.1`; rebuild ran; `git status` clean; `_score.json` on origin |
| M1 conflict during a lock | Mac clone runs `daily.run(core=True, offline=True)` at 19:05 ET; `Ops.pull` is wrapped so that right before run_lock's pull a second clone pushes its own 2026-10-29 path row and latest file | 0 | `[pull returned conflicted paths: ['results/live/2026Q3_latest.json', 'results/live/2026Q3_path.csv']]`, then a lock. `origin/main` holds both files with `<<<<<<< HEAD` markers. The next `gdn nowcast` on that tree: exit 1, `json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 5 column 1 (char 87)` |
| M2 two Mac runs at once | two `gdn daily --core --offline --now 2026-10-29 19:05 ET` started together on one tree, three trials | 0 and 1 | In all three trials one run exited 1 with git's `Another git process seems to be running in this repository`. The other locked; one release; `_lock.json` on origin |

Read-only GitHub facts (`gh`): the repository is private (`"isPrivate":true`); the secret `SEC_UA` exists (set 2026-10-19T16:10:29Z); `nowcast` has run once, by `workflow_dispatch`, successfully (run 39283382067). That run's log reads `FAA snapshot 2026-10-19 by curl, 72927535 bytes` and `SEC reachable: HTTP 200, 155154 bytes`. Its `make daily` step took about 11 seconds and it pushed commit b205fbe, `Daily snapshot 2026-10-19`. No scheduled run has happened yet. At that run, workbook, note, site data and report were `not written yet`, so the full rebuild has never run on a real runner. R1 and R2 are the only evidence it works there.

## Findings

### OPS-1 (blocking). The lock loop ignores a conflicted pull, and the daily job then commits and pushes conflict markers

- File: `src/gdn/live.py:315-317`, together with `src/gdn/daily.py:86-88`.
- Evidence: `for attempt in range(1, 4):` / `ops.pull()` / `if ops.release_view(tag):`. The list of conflicted paths that `Ops.pull` returns (`gitops.py:52-60`, `return conflicted`) is dropped. When a lock is due, `before_prediction` runs `push_outputs`, whose `ops.commit(LIVE_PATHS, "Daily outputs before the lock")` runs `git add -A` on the conflicted files. That resolves the merge with the markers still in the files, and `push_with_merge` pushes the result. M1 reproduced this end to end: both live files on origin had `<<<<<<< HEAD`, the lock still went through, and the next nowcast crashed on `JSONDecodeError`. From then on, every `make daily` on either machine dies in `update_latest` before its first commit, and that includes the 2026-10-30 score run. If `data/snapshots/MANIFEST.json` is among the conflicted files, `newest_stored` raises before the prediction is written, so the lock itself is lost too.
- Trigger: the other machine pushes a change to the same live lines between the locking run's first pull (`daily.py:71`) and run_lock's pull. On the Mac that gap includes the FAA download, up to 600 s of curl plus 300 s of Chrome. On the eve, a Mac run and the runner's 08:17 or 20:17 EDT run can fall inside one such gap (see OPS-3).
- Fix: in `run_lock`, handle the pull's return value the way `push_with_merge` does: `conflicted = ops.pull()`, then `if conflicted and not (on_conflict and on_conflict(conflicted)): ops.abort_merge(); continue`. Pass daily's `on_conflict` into `run_lock`. Add a rehearsal case that runs M1's injection, and assert that no file under `results/live` or `data/snapshots` on origin contains `<<<<<<<`.

### OPS-2 (major). The 19:05 ET sleeper refuses to run when a tracked file outside the daily paths is dirty, and nothing retries it

- File: `src/gdn/daily.py:52-55`; `CLAUDE.md:37`.
- Evidence: `dirty = [p for p in ops.dirty_tracked() if not _under(p, ALLOWED)]` / `print(f"Refusing to run: ...")` / `return 2`. This happens before the pull and before the lock. CLAUDE.md:37 tells the main session to start a one-shot sleeper in the morning that "runs `make daily-core` at 19:05 ET" and to "list it under `## Running`", which is an edit to the tracked `docs/build/PLAN.md`. That file is outside `ALLOWED`. The pattern is live: at the start of this review `git status` showed ` M docs/build/PLAN.md`, and the main session committed it mid-review (069cb0f). If the session is in the middle of any step at 19:05 ET, the sleeper exits 2 and the planned Mac lock does not happen. What remains is the session's own `make daily-core` or the runner at 20:17 EDT. A transient `gh` error has the same result, because `Ops.release_view` raises on anything but a 404 (`gitops.py:109-111`: `raise GitError(f"gh release view {tag} failed: ...")`) and neither `run_lock` nor `daily.run` catches it.
- Fix: make the sleeper a loop. From 19:05 ET, run `make daily-core` every 10 minutes until `results/live/2026Q3_lock.json` exists on `origin/main` or 23:30 ET, logging every exit code to `.build/logs/`. Commit PLAN.md as soon as the sleeper is listed, and keep the tree clean from 18:55 ET. Separately, catch `GitError` around `run_lock` in `daily.run` so that one failed `gh` call does not also skip the commit and push.

### OPS-3 (major). The runner's FAA download works, so the runner will probably lock at about 08:17 EDT on the eve, not the Mac at 19:05

- File: `src/gdn/live.py:243`, `src/gdn/faa.py:93`, `src/gdn/live.py:201-203`; spec §3.11; `CLAUDE.md:37`.
- Evidence: §3.11 says "Expect the FAA download to fail there" and "Its 12:17 UTC run can lock only when the Mac has already pushed a snapshot dated the eve." The only real runner run says otherwise: `FAA snapshot 2026-10-19 by curl, 72927535 bytes`, inside an 11-second `make daily` step. On 2026-10-29 at 12:17 UTC (08:17 EDT, 07:17 CDT) the runner downloads a snapshot dated 2026-10-29 (`snapshot_date` uses the Chicago date). `ingest` stores its full subset because 2026-10-29 is in the window (`in_lock_window`). Then `lock_due` returns `newest_snapshot == eve.isoformat() or t.hour >= LOCK_HOUR_ET`, which is True, so the runner locks from its own morning snapshot. That is legal under §3.6, but the eve plan in CLAUDE.md, with its sleeper, CronCreate and 22:30 fallback, assumes an evening Mac lock. The runner's morning run is also where OPS-1 and OPS-5 are most likely to bite, if the Mac runs anything around 08:00 ET.
- Fix: no scheduled `nowcast` run has happened yet, so check that one shows up after 2026-10-20 00:17 UTC before counting on either runner time. Write this in `DECISIONS.md` as the expected path. On the eve morning, check `gh release view lock-2026Q3` and `_lock.json` on origin by about 08:45 ET, and keep the Mac from running `make daily` or `daily-core` between 08:00 and 08:45 ET. If the owner wants the lock to come from the evening file, that changes a preregistered rule, so it is a §8 question for the owner and not a code change.

### OPS-4 (major). A run checks "before midnight ET" against the time it started, not the time it creates the release

- File: `src/gdn/daily.py:50` and `:80`/`:90`; `src/gdn/live.py:324-326` and `:354-356`.
- Evidence: `now = live.parse_now(now)` is fixed once at the start of `daily.run`. Then comes `faa.download` (up to 600 s of curl, then 300 s of Chrome on the Mac, or 3 × 120 s with retries on the runner), and only then `run_lock(now, ...)`. Inside it, `if not before_release(now, rel):` tests that stale `now`. After `release_create`, a late publish only logs: `log(f"WARNING: {tag} published at {obj['published_at']}, on or after the release date")`, and the lock stands. A Mac run started at 23:50 ET, or a delayed scheduled runner run starting near 23:55 ET, can therefore publish `lock-2026Q3` after 00:00 ET. That breaks "never lock late" and §3.6's rule that `published_at` falls before 00:00 ET, and the release cannot be taken back without deleting it. No rehearsal case covers this, because `--now` freezes the clock.
- Fix: just before `ops.release_create`, also test the wall clock: `if not before_release(utcnow(), rel) or not before_release(now, rel): log(...); return 1`. This keeps rehearsals working, since the real clock is before 2026-10-30. Better still, stop at 23:50 ET wall-clock time to leave a margin for the `gh` call.

### OPS-5 (major). Nothing stops two Mac runs on one working tree, and the eve plan starts up to three

- File: `src/gdn/daily.py:48-57` (no guard); `src/gdn/faa.py:91-93`; `CLAUDE.md:37`.
- Evidence: CLAUDE.md:37 schedules a sleeper at 19:05 ET, "a CronCreate one-shot for 18:07 local" (19:07 EDT, since the Mac runs on CDT), and the session's own "`make daily-core`" at or after 19:00 ET. `daily.run` takes no lock file, and `faa.download` writes every run's curl output to the same `part = out.with_suffix(".part")`. M2 started two runs together three times, and each time one died with `Another git process seems to be running in this repository`. The lock survived in all three trials, but only because the offline runs were short. With real downloads, two curls write the same `.part` file and the first run's `part.replace(out)` moves a file the second curl is still writing.
- Fix: take an exclusive `fcntl.flock` on `.build/daily.lock` at the top of `daily.run` and exit 0 with a log line when it is held. Give each run its own `.part` name, for example with the PID in it. Trim CLAUDE.md:37 to one Mac trigger, the retrying sleeper from OPS-2.

### OPS-6 (minor). The score is committed only after the rebuild, so a rebuild error on the runner loses it

- File: `src/gdn/daily.py:92-97`.
- Evidence: `live.run_score(now, offline, root=root)` writes `_score.json`, then `if not core: rebuild(root)`, and only then `ops.commit(LIVE_PATHS + REBUILD_PATHS, ...)`. No try/except surrounds the rebuild. On the throwaway runner, any exception in estimates, workbook, note, site data or report drops the score with the runner, and it keeps doing so every run until the rebuild is fixed. R2 shows the rebuild works today with a fixture score. The full rebuild has never run on a real runner (run 39283382067 skipped every stage as `not written yet`).
- Fix: `ops.commit(LIVE_PATHS, f"Score {q}")` and `push_with_merge` right after `run_score` changes the score set, before `rebuild`. Wrap `rebuild` so that a failure is logged and the run still commits and pushes the live files.

### OPS-7 (minor). A merge takes upstream's copy of `MANIFEST.json` and the stored subsets wholesale, which can drop a local snapshot's manifest entry

- File: `src/gdn/daily.py:59-61`; `src/gdn/gitops.py:62-65`.
- Evidence: `if all(_under(p, LIVE_PATHS) or _under(p, GENERATED) for p in paths): ops.take_theirs(paths)`, where `LIVE_PATHS` includes `data/snapshots`, so `data/snapshots/MANIFEST.json` is covered. If the Mac stored a subset for one date and the runner a subset for an adjacent date in the same window, both sides add neighbouring entries to the sorted manifest, the hunk conflicts, and `git checkout --theirs` keeps only upstream's entry. The local `data/snapshots/<date>/*.txt.gz` files stay in the tree with no manifest entry, so `newest_stored` (`live.py:250-252`) never sees that date. I found this by reading the code and did not reproduce it.
- Fix: resolve `MANIFEST.json` by merging both sides' `snapshots` maps keyed by date (they never disagree on a date's files, because `ingest` keeps a subset that backs a lock), and take upstream only for the other live files.

### OPS-8 (minor). A lock or score pushed by the runner will not redeploy Pages once the repository is public

- File: `.github/workflows/nowcast.yml:26-29`; `.github/workflows/pages.yml:2-5`.
- Evidence: the runner pushes with `GH_TOKEN: ${{ github.token }}` through checkout's persisted credentials, and GitHub does not start other workflows from a push made with `GITHUB_TOKEN`. `pages.yml` runs only `on: push: paths: ["site/**"]` or by dispatch. Today the repository is private (`"isPrivate":true`), so the deploy job is skipped either way. After the owner makes it public, a lock or score that the runner pushes changes `site/data.json` without a deploy, and the Mac's next daily then finds nothing new under `site/` to push.
- Fix: no change to `pages.yml`, which §3.11 fixes word for word. After going public, run `gh workflow run pages` once after the lock and once after the score, or record this in `DECISIONS.md` as an owner step.

## Checked and found right

- Time zones. 2026-10-30T00:17Z is 2026-10-29 20:17 EDT and 19:17 CDT; 2026-10-29T12:17Z is 08:17 EDT and 07:17 CDT; 2026-10-30T04:00Z is 00:00 EDT. Daylight time ends 2026-11-01, so both runner times fall on the eve's ET date and the snapshot's Chicago date is the eve. For every hour that can lock, the Chicago snapshot date matches the ET eve date. I checked this with `zoneinfo`.
- The 19:00 ET rule. `lock_due` (`live.py:237-243`) requires the ET date to be the eve, and then either a snapshot dated the eve or an hour of 19 or later. Rehearsal rows 1, 2, 7 and 8 pass at 18:00, 19:00, 23:59 and 00:00 ET.
- The workflow matches §3.11: cron `'17 0,12 * * *'`, `workflow_dispatch`, `contents: write`, concurrency group `nowcast` with `cancel-in-progress: false`, `ubuntu-latest`, `timeout-minutes: 45`, `fetch-depth: 0`, Python 3.11, `requirements.lock` (which includes `openpyxl==3.1.5`), the bot's name and email, and `make daily PY=python` with `SEC_UA` and `GH_TOKEN`. The `SEC_UA` secret exists.
- The runner's environment. R1 and R2 used the Mac's `.venv` interpreter, so they do not test the runner's Python; run 39283382067 and the passing `test` runs on Python 3.11.17 cover that. They did run with no `~/.gdn_disclosure` (`note.disclosure` falls back to the tracked `report/note.html`), no `~/.sec_ua` and no `data/raw`, and left a clean tree. The PDF is skipped under `CI` (`daily.py:42`).
- A same-date re-download on the other platform does not churn the gz files. `write_gz` keeps the old bytes when the content matches (`files.py:71-75`). Commit b205fbe predates that guard: it rewrote `2026-10-19.serials.csv.gz` with identical decompressed content and only the gzip OS byte changed (`0x13` on the Mac, `0x03` on Linux).
- The subset behind a lock is never re-stored. `ingest` skips `store_subset` for any date named in `predictions/*.json` (`live.py:198-200`).
- `make all` never downloads, locks, scores or touches live files (`Makefile:67-78`).
