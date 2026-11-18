# Review round 2: code closures

Reviewer: a fresh subagent that built nothing here, working from `docs/build/briefs/review2_code.md`. I read `docs/build/REVIEW.md`, `docs/build/review1_ops.md`, `docs/build/review1_spec.md`, §3.5, §3.6 and §3.11 of the prompt, and `git diff 062e00e..HEAD -- src tests tools Makefile .github` (HEAD 74ce718). The diff touches no file under `.github` and does not touch the `Makefile`.

## What I ran

Nothing below wrote to the project folder except this file. Every git and `gh` step ran in throwaway clones under my scratchpad, against a scratch bare repository and the rehearsal's own `gh` shim. Nothing reached GitHub.

- `.venv/bin/python -m pytest -q -p no:cacheprovider tests` in the project: `98 passed in 5.42s`.
- `make all` in a fresh clone (no `data/raw`, no untracked files): exit 0, the log reads `backtest subset 2026-10-19 from the tracked files` and `workbook inputs unchanged; kept`, and `git status --short` printed nothing afterwards. The offline rebuild is still byte-identical.
- `revert.py`: in a second clone, it reverts one fix at a time, runs the tests named for it (or the whole suite where none is named), and restores the file with `git checkout`. Results are in the closure table.
- `gitcheck.py`: it imports the clone's `tools/rehearsal.py` as a module (its `main()` never runs) and points `BASE`, `BARE`, `WORK`, `OTHER` and the shim at my scratchpad. It then runs `daily.run` in process with the real `gitops.Ops`.
  - C1 repeats round 1's M1: `daily.run(core=True, offline=True)` at 19:05 ET on the eve, with a second clone pushing its own path row and latest file right before `run_lock`'s opening pull.
  - C2: two clones each add a lock-window subset for a different date on the same base, so the daily job's first pull conflicts in `MANIFEST.json`.
- `c3.py`: `daily.run` on an ordinary day with the snapshot step raising `faa.MissingColumn`.
- `tools/mutate.py` in a third clone, with `.venv` linked to the project's interpreter.
- `bash -n tools/eve_waiter.sh`: no syntax error.

## Closures

"Holds" means the code does what the row says. For the blocking and major rows I also confirmed that the named test fails when the fix is reverted.

| Row | Severity | Verdict | Evidence |
|---|---|---|---|
| OPS-1 | blocking | Holds | Reverting the loop's `pull_clean` to `ops.pull()` fails `test_conflicted_pull_aborts_and_retries` (`assert (...`). Reverting both pulls fails it with a `GitError`. Disabling `refuse_markers` fails `test_commit_refuses_conflict_markers` (`DID NOT RAISE`). With real git (C1): `pull 2 conflicted: ['results/live/2026Q3_latest.json', 'results/live/2026Q3_path.csv']`, then `C1 rc 0; releases ['lock-2026Q3']; lock json on origin True; markers on origin []`. The next `gdn nowcast` exits 0. |
| OPS-2 | major | Holds, untested as REVIEW says | `eve_waiter.sh` loops from 19:05 to 23:30 ET, checks `origin/main:results/live/<Q>_lock.json` after a fetch, and logs `make daily-core`'s exit code. `daily.py:134-139` catches any lock-step exception. Reverting that catch passes the whole suite (R2C-6). |
| OPS-3 | major | Sound | §3.6 lets a run lock when "its newest snapshot is dated the eve", and a runner's own download qualifies. `DECISIONS.md:184` records the expected 08:17 EDT lock and the 08:00 to 08:45 ET quiet window, and `AGENT.md` carries it. |
| OPS-4 | major | Holds in `make daily`; see R2C-3 and R2C-4 | Reverting both wall checks fails both named tests. Reverting only the first fails `test_wall_clock_stops_a_late_lock`. Reverting only the second fails `test_clock_crossing_the_margin_during_the_push_stops_the_release`. But changing `daily.py:77` to `wall = False` passes the full suite, and `gdn lock` never sets `wall`. |
| OPS-5 | major | Holds | Removing the `flock` fails `test_daily_runs_one_at_a_time`, though it fails on `GitError: git status ...` in a non-repository and not on a second run going ahead. The `.part` name carries the PID (`faa.py:92`), and `.build/` and `data/raw/` are ignored. |
| OPS-6 | minor | Code holds; the named test does not test it (R2C-6) | `daily.py:145-151` commits and pushes the score before the rebuild, and `:152-157` wraps the rebuild. The rehearsal's release-day case is `gdn score --offline`, which never enters `daily.run`. Reverting both edits passes the full suite. |
| OPS-7 | minor | Holds; the wiring is untested (R2C-6) | C2: `pull conflicted: ['data/snapshots/MANIFEST.json']`, then `origin manifest dates ['2026-10-19', '2026-10-27', '2026-10-28', '2026-10-29']`. Breaking `merge_manifests` fails its test. Unwiring it in `on_conflict` passes the full suite. |
| OPS-8 | minor | Sound | An owner step in `DECISIONS.md:187`. `pages.yml` is unchanged. |
| S1 | blocking | Holds in `make daily` (as OPS-4) | Reverting `made_utc` to the run's start fails the crossing test. |
| S2 | major | Holds for `run_lock`; the `MERGE_HEAD` abort is untested (R2C-6) | Same tests as OPS-1. Replacing `if ops.merging():` with `if False:` (`daily.py:80`) passes the full suite. |
| S3 | minor | Holds | Restoring the old early return fails `test_download_replaces_an_ordinary_stored_date`. Dropping the locked-date exemption fails it too. |
| S4 | minor | Holds | Restoring `if z.exists():` fails `test_offline_data_reads_the_tracked_backtest_subset`. `make all` in a clean clone reads the tracked subset. |
| S5 | minor | Holds | `lossless()` is called in `ingest` (`live.py:203`) and `build_faa` (`data.py:35`). The reasoning for keeping `_keep` is in `DECISIONS.md:188`. |
| S6 | minor | Sound | An accepted deviation, recorded in `DECISIONS.md:189`. |
| S7 | minor | Holds | Restoring the calendar gate fails `test_the_score_waits_for_the_8k_not_the_calendar[with_sentence.htm-True]`. `results_8k` still requires `lo < filed <= lo + 70 days` (`sec.py:126`). |
| S8 | minor | Holds; the daily catch is untested (R2C-6), and failures exit 0 (R2C-5) | Making the fiscal-end error raise again fails its test. Making the 8-K parse raise again fails `[None-False]`. Narrowing `daily.py:126` to `ZeroDivisionError` passes the full suite. |
| S9 | minor | Holds | Removing the `try` fails `test_a_release_created_by_another_run_is_recorded` with the shim's `GitError`. |
| S10 | minor | Holds | Removing the opening `pull_clean` fails `test_the_lock_pulls_before_it_reads_local_state`. |
| S11 | minor | Fixed in 47af692, broken again by f3f1471 (R2C-2) | `tools/mutate.py` now stops at its clean copy. |
| S12 | minor | Code holds; the named test does not fail on revert (R2C-1) | Restoring `"#,##0.0"` gives `1 passed`. |
| T1, T2, T6 | major, minor | Hold | The T1 tests are the S1 tests above. Moving the window edge to `<` fails `test_ingest_stores_the_subset_only_in_the_lock_window`. Disabling the locked-subset guard fails `test_ingest_keeps_a_subset_that_a_prediction_names`. Disabling the build-once guard fails `test_build_file_is_written_once`. |
| T3 to T5, T7, T8 | minor | The tests exist and pass | Not reverted, since they are minor. |
| T9 | minor | Open; the reasoning is sound | The rehearsal's last case runs `gdn daily --core --offline` with the real `Ops` against a bare clone. |

## Findings

Six findings: none blocking, none major, six minor.

### R2C-1 (minor). S12's regression test reads the tracked workbook, so reverting the fix leaves it green

- File: `tests/test_outputs.py:50-53`.
- Evidence: `ws = load_workbook(ROOT / workbook.OUT)["Segments"]`. The test reads the committed `output/gd_gulfstream_model.xlsx`, not a workbook built from `workbook.py`. With `F_USD` reverted to `"#,##0.0"` at `workbook.py:193`, `revert.py` printed `S12 old format: rc 0` / `1 passed in 0.27s`.
- Fix: build the workbook into `tmp_path` with the `tree(tmp_path)` helper and `workbook.run(root)`, as `test_workbook_is_kept_until_an_input_changes` does, and check `number_format` there.

### R2C-2 (minor). `tools/mutate.py` can no longer run, so S11's closing check is gone

- File: `tools/mutate.py:14` (`SKIP = {..., "output", ...}`), `tools/mutate.py:64-66`, and `tests/test_outputs.py:51`.
- Evidence: in a fresh clone, `.venv/bin/python tools/mutate.py` printed `the clean copy does not pass: 1 failed, 85 passed, 2 skipped` and exited 1 before the first mutant. Calling `mutate.run_tests` on mutate's own copy names the failure: `['tests/test_outputs.py::test_revenue_per_delivery_is_formatted_as_dollars']`. The copy leaves out `output/`, and that test reads `output/gd_gulfstream_model.xlsx`. `docs/build/MUTATION.md` was last written in 47af692 (12:36:19 -0500), and f3f1471 added the test at 12:37:12. REVIEW names "the clean rerun inside `tools/mutate.py`" as S11's regression test, and that check cannot run now.
- Fix: R2C-1's fix removes the dependence on `output/`. Then rerun `tools/mutate.py` and commit the regenerated `MUTATION.md`.

### R2C-3 (minor). Only `make daily` turns the late-lock guard on, and no test checks that it does

- File: `src/gdn/daily.py:77`; `src/gdn/__main__.py:46-48`; `src/gdn/live.py:316-317`.
- Evidence:
  - `run_lock(..., wall=False)` defaults the guard off.
  - Only `daily._run` sets `wall = now is None`. Changing that line to `wall = False` passed the full suite (`OPS-4 daily never sets wall: rc 0`, `96 passed, 2 skipped`). The named tests call `run_lock(..., wall=True)` directly.
  - The CLI never passes `wall`: `if a.stage in ("build", "snapshot", "nowcast", "lock", "score", "daily"): kw["now"] = a.now; kw["offline"] = a.offline`.
  - So `make lock` keeps the old check against the clock read at its start, with no 10-minute margin, and stamps `made_utc` with that start time. The exposure is small, because a standalone lock does no download.
  - `DECISIONS.md:186` says "A real run re-reads the wall clock", which is not true of `gdn lock`.
- Fix: in `__main__.py`, pass `wall=a.now is None` for the `lock` stage. Add a test that patches `live.run_lock` and asserts that `daily.run(now=None, ...)` passes `wall=True`.

### R2C-4 (minor). A refusal after the prediction push leaves an unlocked prediction on main and stops reporting the missed window

- File: `src/gdn/live.py:355-359`, `:373-383`, `:341`; `src/gdn/site_data.py:61`.
- Evidence:
  - The first wall check (`live.py:355`) runs before `before_prediction()`, and in `make daily` that is `push_outputs`, which can pull, merge, rebuild and push. The prediction is written later, at `:373-375`. So the check is not "when the prediction is written", as the docstring and `DECISIONS.md:186` say.
  - When the second check trips (`:381-383`), `predictions/2026Q3.json` is already committed and pushed with no release. `test_clock_crossing_the_margin_during_the_push_stops_the_release` asserts exactly that state (`rc == 1 and not ops.creates`, then reads the committed prediction).
  - Every later run then returns 0 without saying the window was missed, because `:341` logs only `if not before_release(now, rel) and not pred_p.exists()`.
  - `site_data.py:61` publishes the file as `"locked"`, which `site/app.js:112` shows as the estimate, and `estimates.json` switches its basis to it.
  - The trigger is narrow: the real clock has to cross 23:50 ET between two adjacent steps.
- Fix:
  1. Re-read the wall clock just before `write_json(pred_p, pred)`, after `before_prediction()`, so that a refusal never leaves a pushed prediction behind.
  2. At `:341`, also log the missed window when the prediction exists but `_lock.json` does not.

### R2C-5 (minor). A failed snapshot or score step ends `make daily` with exit 0

- File: `src/gdn/daily.py:126-127`, `:143-144`, `:166`; `src/gdn/live.py:446-450`.
- Evidence:
  - `c3.py` made the snapshot step raise `faa.MissingColumn` on 2026-10-21 and printed `snapshot step failed: MissingColumn: 'MASTER lacks MFR MDL CODE'; carrying on to the lock` and then `C3 daily.run returned 0`.
  - The score step's `except` does not touch `rc` either.
  - `run_score` returns 0 for an 8-K with no delivery table.
  - On the runner, a changed FAA header or a changed exhibit gives a green workflow run every time, and the only trace is a log line. Before round 1 these failures made the run fail. S8 asked that they not cost the lock, which the code now delivers, but it did not ask that they go unreported.
  - I rate this minor because nothing is lost: the next run retries, the eve's lock still reads the newest stored subset, and the Mac session reads each daily run's output.
- Fix: keep running through the lock, commit and push, but end with a non-zero code when the snapshot or score step failed or an 8-K could not be parsed, the way the rebuild branch sets `rc = rc or 1` (`daily.py:157`). `eve_waiter.sh` retries on the lock record, not on the exit code, so it is unaffected.

### R2C-6 (minor). `daily.run`'s round 1 changes have no test that fails when they are reverted, and OPS-6 cites a test that does not reach them

- File: `src/gdn/daily.py:80-83` (S2's `MERGE_HEAD` abort), `:93-99` (OPS-7's manifest union in `on_conflict`), `:120-127` (S8's snapshot catch), `:134-139` (OPS-2's lock-step catch), `:145-157` (OPS-6's early score commit and rebuild catch); `docs/build/REVIEW.md` OPS-6 row.
- Evidence: each revert below passed the full suite (`96 passed, 2 skipped`):
  - `S2 MERGE_HEAD abort off: rc 0`
  - `OPS-7 manifest union not wired: rc 0`
  - `S8 snapshot step not caught in daily: rc 0`
  - `OPS-2 lock-step exception not caught: rc 0`
  - `OPS-6 score not committed before rebuild: rc 0`

  REVIEW names "the lock rehearsal's release-day case" for OPS-6, but that case runs `gdn score --offline --now 2026-10-30 12:00 ET` (`docs/build/REHEARSAL.md`), which calls `live.run_score` and never `daily.run`. My C1 and C2 checks show the wiring works today with real git. Nothing would catch a regression.
- Fix: add `daily.run` tests that use a fake `Ops` with `merging`, `pull`, `stage_version`, `take_theirs`, `finish_merge`, `commit` and `push`. Cover a leftover merge, a manifest conflict, a snapshot step that raises, a lock step that raises, and a rebuild that raises after a new score, and assert the commits and pushes in order. Or add C1 and C2 as rehearsal cases. Then correct the OPS-6 row in REVIEW.

## Checked and found right

- No path locks twice or rewrites a committed prediction.
  - `ops.tracked(pred_p)` still guards every write (`live.py:364-366`).
  - A failed `gh release create` records the existing release instead of retrying (`:384-389`).
  - The "release without `_lock.json`" path is unchanged.
- No path replaces a subset a lock depends on.
  - `faa.download` skips the backtest date and every `locked_dates` date (`faa.py:86`).
  - `ingest` keeps a locked date's subset (`live.py:206`).
  - `build_faa` re-stores the backtest subset only from the zip the manifest recorded (`data.py:34`).
  - In the merge path, `on_conflict` takes upstream's copy of a subset only before this machine's prediction is computed, because `push_outputs` settles the subsets on origin first. I checked that path and not the download race in which the other machine stores the same date between this machine's `push_outputs` and its prediction push. In that race `faa.locked_dates` cannot yet see the prediction, and only `write_gz` keeping the bytes of an identical same-day file protects the subset. That behavior predates the diff, so it is not a finding here.
- The score cannot be lost to a rebuild error: it is committed and pushed at `daily.py:145-151`, before `rebuild`.
- `wall_clock_ok` builds midnight as `2026-10-30T00:00` in America/New_York and compares aware times. The margin is `LAST_LOCK_MINUTES = 10`.
- `eve_waiter.sh` compares `YYYY-MM-DDTHH:MM` strings inside `[[ ]]`, logs `$?` from `make daily-core`, needs no `set -e`, and stops after 23:30 ET.
- `merge_manifests` writes the same layout as `files.write_json` (`indent=2`, trailing newline). Upstream wins for a date both sides hold, which matches `take_theirs` for that date's files.
- `refuse_markers` checks only the staged text files. Binary `.gz` conflicts never reach it, because `on_conflict` resolves them or `pull_clean` aborts the merge.
- The new `Second lock` mutant's target string (`live.py:348-349`) is unique, which `mutate.py` checks with `src.count(old) != 1`.
