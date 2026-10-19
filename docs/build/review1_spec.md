# Review round 1: spec auditor

Brief: `docs/build/briefs/review1_spec.md`. I read §3 of `GULFSTREAM_NOWCAST_PROMPT.md` (lines 111 to 306, in windows of 120 lines or less) against `src/gdn/` and `tests/` at HEAD `9b84384`. I built nothing in this project and edited no file but this one.

While I worked, other sessions changed `src/gdn/note.py`, `tests/test_claims.py`, `report/*` and the note PDFs in the working tree. Those changes are not mine and I did not audit them. Every file this review cites (`live.py`, `gitops.py`, `daily.py`, `faa.py`, `events.py`, `files.py`, `fiscal.py`, `data.py`, `model.py`, `stats.py`, `estimates.py`, `workbook.py`, `site_data.py`, the four test files) matches HEAD.

**Scope.** The tables below cover §3.1 to §3.8, and the parts of §3.11 that S3, S4 and S7 touch.
- I read `.github/workflows/nowcast.yml` and it matches §3.11 as written: the cron `'17 0,12 * * *'`, `workflow_dispatch`, `contents: write`, the concurrency group, the 45-minute timeout, `fetch-depth: 0`, Python 3.11, `requirements.lock`, the bot's `git config`, and `make daily PY=python` with `SEC_UA` and `GH_TOKEN` in its environment.
- The step order of `make daily` (`daily.py:70-105`) matches §3.11's sentence: pull, download, latest nowcast, lock, score, rebuilds, commit and push.
- I did not audit §3.9, §3.10, `pages.yml` or `test.yml`, because of the time box and because `note.py` was changing under me.

**What I ran.** All of it was read-only against the repository, with scripts and throwaway git repositories in the session scratchpad:
- `check1.py`. It rebuilt the 2026Q3 prediction from the stored 2026-10-19 subset, the way the lock reads it, and compared it with `_build.json`, `_latest.json`, the path row and the daily table. It checked the manifest hashes and the gzip headers. It rebuilt the subset from the raw zip under my own reading of §3.3, scanned the zip for characters that `str.splitlines` breaks on, ran `faa.lossless`, and recomputed `estimates.json` and the workbook's P10 and P90.
- `check_wb.py`. It opened `output/gd_gulfstream_model.xlsx` with openpyxl and checked its formulas, font colours and functions.
- `check_merge.py`. It ran the real `gitops.Ops` in two clones of a bare repository to see what a pull conflict inside `run_lock` leaves behind.
- `check_late.py`. It ran `run_lock` with the clock fixed at 23:58 ET on the eve, where the slow steps take seven minutes.
- `pytest -p no:cacheprovider` on `test_live.py`, `test_faa.py`, `test_model.py` and `test_sec.py`: 49 passed.

## Findings by severity

| Id | Severity | File and line | One line |
|---|---|---|---|
| S1 | blocking | `src/gdn/live.py:294,324,342,350`; `src/gdn/daily.py:50,80,90` | The lock checks "before 00:00 ET" against a clock read when the run starts, so it can lock late. `made_utc` is stale too. |
| S2 | major | `src/gdn/live.py:316`; `src/gdn/daily.py:56-57,86-88` | `run_lock` ignores a pull conflict. The next commit records the conflict markers and pushes them. |
| S3 | minor | `src/gdn/faa.py:85-89`; `tests/test_faa.py:144-154` | A second run on a lock-window date keeps the first zip. That breaks §3.11 and contradicts `DECISIONS.md:154`. |
| S4 | minor | `src/gdn/data.py:30-35`; `Makefile` `all:` | `make all` rewrites the backtest subset from the untracked raw zip, with no guard. |
| S5 | minor | `src/gdn/faa.py:132,189-199,260-269` | Byte-for-byte holds only when the zip decodes losslessly, and `lossless()` is never called. `_keep` lacks the comma-position fallback. |
| S6 | minor | `src/gdn/files.py:59-64` | New `.txt.gz` subsets get OS byte 255. That is not what `gzip.compress(data, mtime=0)` writes. |
| S7 | minor | `src/gdn/live.py:392-395` | The score waits for, and requires, a calendar release date, where §3.6 waits only for the 8-K. |
| S8 | minor | `src/gdn/daily.py:80-83`; `src/gdn/live.py:124` | Any exception from the download, ingest or nowcast aborts the run before the lock. |
| S9 | minor | `src/gdn/gitops.py:114-116`; `src/gdn/live.py:350` | When a Mac run and a runner run race, `gh release create` fails on the existing tag and the run ends in a traceback. |
| S10 | minor | `src/gdn/live.py:303-314` | A standalone `gdn lock` reads local state before it pulls. |
| S11 | minor | `tools/mutate.py:52-56,74-77`; `docs/build/MUTATION.md` | Mutants leak into later runs, so MUTATION.md does not prove the "Window edge" catch. |
| S12 | minor | `src/gdn/workbook.py:193` | Revenue per delivery uses `#,##0.0` where the spec says `#,##0` for dollars. Not gated. |
| T1 to T9 | major or minor | see "Rules with no test" | §3.5 and §3.6 rules, `estimates.py` and `workbook.py` have no test. |

## Findings

### S1. blocking. The lock compares "before 00:00 ET" with a stale clock, so it can lock late

- **Where.** `src/gdn/daily.py:50` reads the time once: `now = live.parse_now(now)`. Everything after that reuses it: the download at `daily.py:80` (`faa.download(root, now)`), the lock call at `daily.py:90` (`live.run_lock(now, ...)`), the late-lock guard at `live.py:324` (`if not before_release(now, rel):`), the prediction at `live.py:342` (`predict(root, q, rows, snap, now)`, which stamps `"made_utc": stamp(now)` at `live.py:140`), and then `release_create` at `live.py:350`. Between the clock read and the release sit curl (`--max-time 600 --retry 2`), the five-minute Chrome wait, the ingest, `push_outputs`, and up to three push attempts. The only check after the release is a log line at `live.py:354-356`. With a fixed clock, `lock_due` (`live.py:311`) implies `before_release`, so the guard at `live.py:324` can never fire. It is dead code.
- **Evidence.** `check_late.py` calls `run_lock` with `now` = 2026-10-29 23:58 ET, and its fake push advances the real clock by seven minutes:
  ```
  release_create called at 2026-10-30T00:05:00-04:00
  rc 0
  WARNING: lock-2026Q3 published at 2026-10-30T04:05:00Z, on or after the release date
  Locked 2026Q3 as a timestamped GitHub release: sha256 `b662...`
  made_utc 2026-10-30T03:58:00Z
  ```
  The release is published after 00:00 ET, the exit code is 0, and `made_utc` reads seven minutes before the prediction existed. §3.6 says "The release's `published_at` must fall before 00:00 ET on the release date" and "never lock late". The realistic trigger is a retry near midnight after the 19:00 ET lock failed. A runner run delayed by hours is a second one.
- **Fix.**
  1. Pass a clock function into the lock (`clock=utcnow`, which tests and rehearsals can replace), not a fixed `now`.
  2. Re-read the clock just before writing the prediction and again just before `release_create`. Refuse, without creating the release, unless at least a safety margin (say five minutes) remains before 00:00 ET.
  3. Stamp `made_utc` with the time the prediction is actually computed.
  4. Add a test where the fake ops advances the clock past midnight between the push and the release, and assert that no release is created.

### S2. major. `run_lock` ignores a pull conflict, and the next commit pushes conflict markers

- **Where.** In `src/gdn/live.py:316` the loop calls `ops.pull()` and discards the result, although `gitops.py:52-53` documents it as "Returns the conflicted paths". The repository is then mid-merge. Next comes `before_prediction`, which is `daily.push_outputs` at `daily.py:86-88`. It calls `ops.commit(LIVE_PATHS, ...)`, and `gitops.py:78` runs `git add -A -- <paths>`. That stages the files with their markers, and `git commit` then records the merge. When the conflicted paths lie outside `LIVE_PATHS`, the commit raises instead. The run dies mid-merge, and the next run's carry-over commit (`daily.py:56-57`, which commits `ALLOWED` whenever `dirty_tracked()` is non-empty and treats `UU` entries as dirty) records the markers then.
- **Evidence.** `check_merge.py` uses the real `gitops.Ops` on two clones. The runner pushes a path row for 2026-10-29, and the Mac writes a different one:
  ```
  pull() returned: ['results/live/2026Q3_path.csv']
  MERGE_HEAD present: True
  commit(LIVE_PATHS) returned: True
  HEAD parents: 2
  committed file:
  2026-10-28,31.0
  <<<<<<< HEAD
  2026-10-29,33.5
  =======
  2026-10-29,32.0
  >>>>>>> ff5ce17...
  ```
  `push_with_merge` then pushes that commit to GitHub. If the conflict is in `data/snapshots/MANIFEST.json`, `newest_stored` (`live.py:251`) fails to parse it and the lock dies on the eve. The trigger is both machines changing the same live file between the daily pull (`daily.py:71`) and the lock's pull. The Mac and the runner have no shared concurrency group.
- **Fix.**
  1. At `live.py:316`, handle the conflict the way `push_with_merge` does. Pass `on_conflict` down, or call `ops.abort_merge()` and `continue`.
  2. In `daily.py:56`, refuse to carry anything over while `git rev-parse -q --verify MERGE_HEAD` succeeds, and abort the merge or stop.
  3. Give `FakeOps.pull` a mode that returns conflicts, and test the lock with it.

### S3. minor. On a lock-window date a second run keeps the first zip, against §3.11 and `DECISIONS.md:154`

- **Where.** `src/gdn/faa.py:85-89`: `if date in manifest(root)["snapshots"] and is_zip(out): ... return date`. Once a date's subset is stored (the backtest date, or any lock-window date) and its raw zip is on disk, a second run on the same Chicago date never downloads again. That is the Mac's case; the runner has no `data/raw/`. The zip, the subset, the daily table and the path row all stay as the first run left them. `tests/test_faa.py:144-154` (`test_download_keeps_a_stored_snapshot`) asserts this behaviour.
- **Evidence.** §3.11 says "A second run on the same Chicago date replaces that date's row and files." `DECISIONS.md:154` says "a second download on a Chicago date replaces that date's daily table and path row, as §3.11 says, and the stored subset too, except when a prediction file names that snapshot date." On the runner, which has no raw zip, the code downloads again and `ingest` behaves as `DECISIONS.md:154` says. On the Mac it does what neither says. The guard that §3.6 actually needs already exists in `ingest` (`live.py:198-200`).
- **Fix.** Drop the early return, or narrow it to the backtest date and to dates that `predictions/*.json` names. Keep `ingest`'s `locked_on` guard as the protection, and update the test and `DECISIONS.md:154` to match.

### S4. minor. `make all` rewrites the backtest subset from the untracked raw zip

- **Where.** `src/gdn/data.py:30-35`: `if z.exists(): texts = faa.zip_texts(z); sub = faa.subset(texts); faa.store_subset(root, date, sub, z, backtest=True)`. `make all` runs `$(RUN) data --offline` first.
- **Evidence.** §3.11 says "`make all` is the offline rebuild from tracked files". With the zip present, this reads an untracked file and rewrites `data/snapshots/<backtest>/*.txt.gz` and `MANIFEST.json`. Nothing compares `zip_sha256` with the manifest first, and there is no `locked_on`-style guard. Today the zip matches the manifest (check1: `zip sha matches manifest: True`), so nothing changes. But a replaced zip would silently replace the subset that `_build.json`, every backtest figure, and any lock without a lock-window subset depend on.
- **Fix.** Under `--offline`, always read the tracked subset. Outside it, re-store only when the zip's sha256 equals the manifest's `zip_sha256`, or when no backtest entry exists yet.

### S5. minor. "Byte for byte" depends on a check that never runs, and `_keep` skips the spec's fallback

- **Where.**
  - `src/gdn/faa.py:132` decodes with `errors="replace"`, and `store_subset` (`faa.py:237`) re-encodes `sub[k].encode("utf-8")`. So the stored subset equals the zip's bytes only when every file decodes losslessly. `faa.lossless()` (`faa.py:260-269`) exists for this purpose but nothing calls it (a grep finds no call site).
  - `_keep` (`faa.py:189-199`) selects rows with `csv.reader` alone. §3.3 says to split each line with `csv`, and to cut at the header line's comma positions when the field count differs from the header's. `read_table` does that (`faa.py:168-169`); `_keep` does not.
  - Both use `str.splitlines`, which also breaks on `\x0b \x0c \x1c-\x1e \x85    `.
- **Evidence.** None of this bites on the 2026-10-19 snapshot (check1):
  - `faa.lossless: True`, and the zip holds no `splitlines` hazards.
  - My spec subset matches the stored subset (`ACFTREF 54/54, MASTER 2821/2821, DEREG 1296/1296: spec subset == stored True`).
  - One DEREG line in the whole file needs the fallback: `csv code '7102308' | fallback code ''`, out of scope either way.

  The risk is latent and concerns future lock-window snapshots.
- **Fix.**
  1. Build the subset from the raw bytes: split on `b"\n"` and decode each line only to test its key, then write the kept lines' original bytes.
  2. Select rows with the same split-and-fallback as `read_table`.
  3. If you keep the text path, call `lossless()` in `ingest` and log, or refuse, when it is false.

### S6. minor. New subsets will not be `gzip.compress(data, mtime=0)` output

- **Where.** `src/gdn/files.py:59-64` sets `b[9] = 255`, and `store_subset` writes the subset through `write_gz` (`faa.py:237`).
- **Evidence.** `xxd` shows the backtest subset headers as `1f8b0800000000000213` (OS byte 0x13, Python 3.11's zlib output on macOS). check1 confirms `gzip.compress(mtime=0) here == file True; gz_bytes (OS 255) == file False`. Any subset stored from now on (the lock window) will carry 0xFF. Python 3.11 writes 0x03 on Linux and 0x13 on macOS, so neither platform's `gzip.compress(data, mtime=0)` produces that header. §3.3 says to write each file "with `gzip.compress(data, mtime=0)`". The manifest hashes whatever bytes were written, so the manifest stays consistent. The change is recorded in `DECISIONS.md:153`. A gate that recompresses with `gzip.compress(..., mtime=0)` and compares bytes would fail on the lock's subset.
- **Fix.** Either ask the owner to accept the deviation for the `.txt.gz` subsets, or write the subsets with plain `gzip.compress(data, mtime=0)` and keep OS byte 255 for the daily tables, which §3.3 does not govern.

### S7. minor. The score waits for, and requires, the calendar's release date

- **Where.** `src/gdn/live.py:392-395`: `if not end or not rel or et_date(now) < dt.date.fromisoformat(rel): return 0`.
- **Evidence.** §3.6 says "When the quarter's results 8-K appears (§3.2's rule), parse its counts and write `results/live/<Q>_score.json`". It makes no condition on `config/calendar.json`. With the shipped calendar (`{"releases": {"2026Q3": ...}}`), 2026Q4 will never be scored until someone adds its release date. An 8-K filed before the calendar date is also ignored until that date.
- **Fix.** Look for the 8-K whenever `Calendar.end(q)` has passed. Keep the release date only for the lock.

### S8. minor. An exception before `run_lock` costs the lock

- **Where.** `src/gdn/daily.py:80-83` calls `faa.download`, `live.ingest` and `live.update_latest` with no guard. `ingest` raises on a bad zip (`zipfile.BadZipFile`) or on a changed header (`faa.MissingColumn` from `check_columns`, `faa.py:140-146`). `predict` raises `ValueError` at `live.py:124` for any live Q1 when `fiscal_ends` is empty, which first happens for 2027Q1. `run_score` (`live.py:408`) lets `parse_deliveries`'s `ValueError` escape too.
- **Evidence.** If the eve's zip cannot be read, the run aborts before `daily.py:90`, even though an older stored subset could still be locked. From the 2026Q4 score on, every run dies at `daily.py:83` and nothing is committed: the score file is written at `live.py:410`, and the crash comes at `daily.py:94`, before the commit at `daily.py:97`.
- **Fix.** Wrap the snapshot steps and `update_latest` in `try/except`, log, and carry on to the lock with the newest stored subset. In `update_latest`, log a missing fiscal end and skip it rather than raising.

### S9. minor. In a Mac and runner race, `gh release create` raises on the existing tag

- **Where.** `src/gdn/gitops.py:114-116` runs `gh release create` with `check=True`, and `live.py:350` does not catch the error.
- **Evidence.** Two runs that both pass `release_view` (`live.py:317`) before either creates the release will both call `release_create`. GitHub refuses the second, so there is no second lock, but that run ends in a `GitError` traceback. It skips the lock record (`live.py:351-353`) and the rest of `daily.run`. A later run repairs the lock record through `live.py:303-308`.
- **Fix.** Catch `GitError` around `release_create`, call `release_view` again, and when the release exists, go to `write_lock_json` and log "already locked by another run".

### S10. minor. A standalone `gdn lock` reads local state before it pulls

- **Where.** `src/gdn/live.py:303-314`. The first release check depends on a local `pred_p.exists()`. `if lock_p.exists(): return 0` and `lock_due(...)` also read the local tree. The first `ops.pull()` comes at `live.py:316`.
- **Evidence.** §3.6 says "It starts with `git pull --no-rebase --tags` and `gh release view lock-<Q>`, and stops at once when that release exists." Under `make daily`, `daily.py:71` pulls first, so this matters only for `make lock`. Even there, the loop's pull and release view still come before any prediction is written.
- **Fix.** Begin `run_lock` with `ops.pull()` (handling conflicts, see S2) and `ops.release_view(tag)`.

### S11. minor. The mutation record does not show that each mutant was caught on its own

- **Where.** `tools/mutate.py:52-56` runs pytest without `-B` or `PYTHONDONTWRITEBYTECODE`. `tools/mutate.py:74-77` restores each file and does not clear `__pycache__`.
- **Evidence.** In `docs/build/MUTATION.md`, `test_faa.py::test_airframes` and `test_window_edges` fail for every mutant from "Earliest date in E1 and E2" on, including ones that cannot touch `events.py`: "Zero rule", "Nearest rank", "Eve boundary" and "Second lock". That pattern fits stale bytecode. The `min`/`max` and `<`/`<=` swaps keep the file's size, and the suite runs in about 0.2 s, so the restored source can share the mutant's mtime second and size, and Python keeps the mutant's `.pyc`. As a result, the "Window edge" row's only failing tests are the two that the earlier mutant already broke. The later rows do each name a relevant test.
- **Fix.** Pass `-B` (or set `PYTHONDONTWRITEBYTECODE=1`) in `run_tests`, delete `__pycache__` after each restore, re-run the clean suite between mutants, and regenerate `MUTATION.md`.

### S12. minor. A format nit, not gated

- **Where and evidence.** `src/gdn/workbook.py:193`: `("Revenue per delivery", "=J2/B12", "#,##0.0")`. §3.8 asks for "`#,##0` on dollars".
- **Fix.** Use `F_USD`.

## Rule by rule

The verdicts are "as written", "diverges" (with its finding), or "as written, untested".

### §3.6 The lock and the score

| Rule | Verdict | Code |
|---|---|---|
| `config/calendar.json` shape | As written. The file holds `{"releases": {"2026Q3": "2026-10-30"}, "fiscal_ends": {}, "public": false}`. | `config/calendar.json` |
| Lock on the eve (ET), when the newest snapshot is dated the eve or the time is 19:00 ET or later | As written for the decision. The time it uses is stale (S1). | `live.py:237-243,311` |
| Starts with pull and release view, and stops when the release exists | The daily path does. A standalone lock reads local state first (S10). Pull conflicts are ignored (S2). | `daily.py:71`, `live.py:303-323` |
| From seven days before the release, every snapshot stores its full subset with a manifest entry | As written (`rel-7 <= d < rel`). Untested (T2). | `live.py:181-189,201-203`, `faa.py:231-249` |
| First commits and pushes its own daily outputs, subsets included | As written | `daily.py:86-88`, `live.py:327-332` |
| Recomputes from the newest snapshot with a stored subset | As written. check1 shows the lock-style prediction from the stored subset equals the build, latest and path row (`subset-pred == build: True == latest: True`, `path row matches: True`). | `live.py:337-342` |
| Commits `predictions/<Q>.json` alone and pushes | As written: `git commit -m msg -- <path>` | `gitops.py:84-87`, `live.py:344-345` |
| On rejection, `git fetch` and `git reset --hard @{u}`, then again from release view, three attempts | As written. The retry also pulls first, which the spec does not ask for. | `live.py:345-348`, `gitops.py:96-98` |
| `gh release create lock-<Q> --target <commit> --title ... --notes "sha256 <hex>"`, then fetch the tag | As written (adds `-R <slug>`) | `live.py:349-351`, `gitops.py:114-119` |
| `_lock.json` from `gh release view --json publishedAt,tagName` and `git rev-list -n 1` | As written | `live.py:268-276` |
| Commits and pushes it, and prints the sha256 in backticks plus one line to the owner | As written | `live.py:352-360` |
| A release without `_lock.json`: fetch the tag and write the file | As written. Tested (`test_release_without_lock_json_is_recorded`). | `live.py:303-308,317-321` |
| The prediction file is committed once and never changed | As written. I found no path that rewrites a committed prediction: the code checks `ops.tracked(pred_p)` before every write (`live.py:333-335`), nothing else writes `predictions/`, and the carry-over commit (`daily.py:57`) could only add an untracked file. | `live.py:333-344` |
| `published_at` before 00:00 ET on the release date | **Diverges (S1).** Checked only against a stale clock, and only warned about afterwards. Untested. | `live.py:324,354-356` |
| Snapshot date before the release date | As written. Untested. | `live.py:338-340` |
| One lock per quarter | As written, given GitHub's tag uniqueness. A race raises (S9). | `live.py:317-323` |
| A missed window gets no lock and says so | Says so (`live.py:312-313`). "Never lock late" fails under S1. | `live.py:311-326` |
| "Timestamped GitHub release" until `"public": true` | As written in the log; the note and README take the word from `cfg["public"]`. | `live.py:357-358`, `note.py:222-223`, `report.py:141` |
| Score when the 8-K appears | **Diverges (S7).** | `live.py:387-412` |
| Score object keys, nulls without a lock, guidance pace and AE | As written. Tested. | `live.py:367-384` |

### §3.5 The live nowcast

| Rule | Verdict | Code |
|---|---|---|
| The live quarter: the earliest unscored quarter from 2026Q3 whose four lags are all reported | As written. Untested (T4). | `live.py:70-76` |
| Prediction keys, nested shapes, `made_utc` format | As written, but `made_utc` is stale on the lock path (S1). | `live.py:120-140` |
| Every count comes from the named snapshot, past quarters included | As written | `live.py:128-130` |
| Reported history: §3.2, then scored live quarters | As written. Untested (T4). | `live.py:62-67` |
| The live band uses design, holdout and each scored locked error | As written. Untested (T5). | `live.py:109-116,133-134` |
| `_build.json` for 2026Q3 only, written once | As written. Untested (T6). | `live.py:222-233` |
| `_latest.json` rewritten at each snapshot | As written. It skips the rewrite when only `made_utc` would change (`same_but_time`). Untested. | `live.py:163-178` |
| `_path.csv`: one row per snapshot date, with the stated columns | As written. A same-date row is replaced. Untested (T3). | `live.py:19-20,143-156` |
| Every snapshot a nowcast reads writes its airframe table | As written. check1: `serials.csv == daily table text: True == airframes(subset): True`. | `live.py:96-97,197`, `live.py:230` |
| Path rows keep accruing after the lock until the score | As written: the live quarter does not move until it is scored. | `live.py:70-76,165` |
| No 2026Q4 file before 2026Q3 is scored | As written | `live.py:73-76`, `daily.py:93-94` |

### §3.3 Ingest, subset and airframes

| Rule | Verdict | Code |
|---|---|---|
| The download chain: curl with the headers, then Chrome on the Mac, else no snapshot | As written (120 s under `CI`, per §3.11) | `faa.py:52-106` |
| A snapshot is named for its America/Chicago date | As written | `faa.py:40-41` |
| Case-insensitive file names, UTF-8 with replacement, header normalization | As written. Tested. | `faa.py:110-132` |
| Required fields; `YEARMFR` optional | As written. Tested. | `faa.py:25-31,140-146` |
| csv split, with the comma-position fallback | As written in `read_table` (tested). **Not in `_keep`** (S5). | `faa.py:149-174,189-199` |
| Dates | As written. Tested. | `faa.py:114-122` |
| Scope and cabin | As written. Tested. | `faa.py:178-186` |
| Stored subset: header plus in-scope rows, byte for byte, in file order, `gzip.compress(mtime=0)`, manifest shape | Byte for byte holds on 2026-10-19 (verified against the raw zip) but is not guaranteed (S5). Gzip header (S6). Manifest shape as written. | `faa.py:202-249`, `files.py:59-81` |
| A second run on the same date replaces that date's files (§3.11) | **Diverges (S3)** | `faa.py:85-89` |
| No path replaces a subset a lock depends on | `ingest` guards it (`live.py:198-200`). `make data` and `make all` bypass the guard for the backtest subset (S4). The guard is untested (T2). | `live.py:192-203`, `data.py:30-35` |
| Airframe key, Gulfstream-held, `customer_cert`, `gulfstream_cancel`, export, `held`, model and cabin, airworthiness, year, bound, E1 and E2 | As written. Tested on fixtures, and re-derived on the 2026-10-19 data (check1 item 2). | `events.py:14-64` |
| `serials.csv` order and columns; `registry_quarterly.csv` windows | As written. Tested. | `events.py:9-11,86-102`, `data.py:122-129` |
| Pipeline | As written (site uses the newest daily table). Tested. | `events.py:105-111`, `site_data.py:49-51` |

### §3.7 Estimates

| Rule | Verdict | Code |
|---|---|---|
| `basis`: `predictions/2026Q3.json` once it exists, else `_build.json`, with its sha256 | As written. Today `basis.sha256` equals the build file's sha256 (check1). Untested (T7). | `estimates.py:16-19,46` |
| TTM, prior TTM, drift, margin, backlog, coverage | As written. `estimates.compute(root) == results/estimates.json` is True. Untested. | `estimates.py:32-38` |
| `ttm_deliveries` (163), revenue per delivery, `nowcast_total` | As written: `ttm_deliveries` reads 163 | `estimates.py:39-41` |
| Aerospace and segment operating earnings from the estimate; totals without Corporate; sensitivity −4 to 4 | As written. Untested. | `estimates.py:42-57` |

### §3.8 Workbook

| Rule | Verdict | Code |
|---|---|---|
| Sheet order; blue inputs, black formulas; allowed functions; `fullCalcOnLoad` | As written. check_wb: `functions used ['ABS', 'AVERAGE', 'IF', 'SUM']`, `colour problems [] 0`, `fullCalcOnLoad True`. | `workbook.py:15-16,28-34,243-263` |
| Quarters columns A to R, rows 2 to 43, from row 6 on | As written (row 6 checked cell by cell) | `workbook.py:89-114` |
| Summary rows 6 to 17 and 18 to 43 | As written | `workbook.py:117-126` |
| Live B1 to B15 from the basis prediction | As written. B12 and B13 are recomputed from `metrics.json`, not read from the prediction's own band, but they reproduce it exactly (check1: `[20.4119..., 36.4196...]` both ways). | `workbook.py:129-165` |
| Segments rows 2 to 5, 7 to 10, and A12 to A18 with their formulas | As written (format nit S12) | `workbook.py:168-205` |
| Sensitivity | As written | `workbook.py:208-217` |
| Byte-identical build; inputs sha256 skip | As written (`tools/determinism.py` covers it). The skip is untested (T8). | `workbook.py:220-277` |

### §3.1, §3.2 and §3.4 (lighter pass)

- **§3.1.** Pinned ends come from `gd_deliveries.csv` up to 2026Q2. After that the code applies Q4 = December 31, Q2 and Q3 = the quarter before plus 91 days, and Q1 from `fiscal_ends`, with 2015Q4 = 2015-12-31. As written (`fiscal.py:48-61`). The build's `window_end` reads 2026-10-04.
- **§3.2.** 42 rows. 2016 comes from the 2017 prior-year columns: 2016Q1 reads `0000040533-17-000012`. 8-K selection: first 2.02 filing within 70 days, with tests. Sentence-agreement check, tested. The one-failure stop and the 5-per-second limit: as written (`data.py:72-78`, `sec.py:62-82,121-128,178-206`).
- **§3.4.** Ratio and its zero rule, guidance pace, design choice (E1 on a tie), holdout rows, sign test and Holm, nearest rank, lag-1, past-miss band and Clopper–Pearson, truncation, coverage drift, `metrics.json` keys: as written (`model.py`, `stats.py`). `holdout_metrics`, `truncated_mae` and `coverage_drift` have no direct test (T9).

## Rules with no test

The evidence for each line is that its function name appears in no file under `tests/`:

```
for s in in_lock_window ingest update_latest update_path live_quarter reported_history write_build run_score \
  estimates workbook daily push_with_merge on_conflict lossless before_release holdout_metrics truncated_mae coverage_drift
```

Each of those names matched no test file. `band_errors` matches only the fixture's metrics key, and `Ops(` matches only `FakeOps`.

| Id | Severity | Rule | Code | Test to add |
|---|---|---|---|---|
| T1 | major | `published_at` before 00:00 ET, and a clock that advances during the lock | `live.py:324,354` | Fake ops advances the clock past midnight; assert no release (S1) |
| T2 | major | The seven-day window stores the full subset; `ingest` keeps a subset that a prediction names | `live.py:181-203` | `ingest` on 10-22, 10-23 and 10-30 with a fixture zip; a second ingest of a locked date leaves the bytes unchanged |
| T3 | minor | Path rows: one per date, replaced on the same date, accruing after the lock | `live.py:143-178` | Two `update_latest` calls on the same date and a later date, and one after a prediction exists |
| T4 | minor | The live quarter moves on after a score; reported history includes scored quarters | `live.py:62-76` | Write a 2026Q3 score; assert the live quarter is 2026Q4 and its lags use the scored counts |
| T5 | minor | The live band includes each scored locked error | `live.py:109-116` | A scored locked quarter adds one error to `band_errors` |
| T6 | minor | `_build.json` is written once | `live.py:222-227` | A second `write_build` leaves the bytes unchanged |
| T7 | minor | The `estimates.json` basis switch and its formulas | `estimates.py:16-58` | Fixture segments and a fixture prediction; assert the basis path switches to the prediction once it exists |
| T8 | minor | The workbook's inputs sha256 skip and its formulas | `workbook.py:235-277` | Build twice and compare bytes; change `metrics.json` and see a rebuild; assert the key formulas |
| T9 | minor | `daily.run` refuses outside paths, stages by explicit list, resolves conflicts; real `Ops` reset, `commit_only`, conflicts; `holdout_metrics`, `truncated_mae`, `coverage_drift` | `daily.py:48-105`, `gitops.py`, `model.py:165-241` | Use a throwaway bare repository, as `check_merge.py` does |

## Checked and found clean

- **The lock, the build and the path rows agree.** The 2026Q3 prediction rebuilt from the stored 2026-10-19 subset equals `_build.json`, `_latest.json` and the path row (made time aside). The daily table equals `serials.csv`, and both equal `airframes(read_subset(...))`.
- **The stored subset matches the zip.** It equals a from-scratch spec subset of the raw zip, byte for byte, and the manifest hashes match the files and the zip.
- **The files that build on it agree.** `estimates.json` equals `compute()` from the build basis. The workbook formulas match §3.8 cell by cell.
- **The lock cannot run twice.** GitHub refuses a second release; S9 only turns that refusal into a traceback.
- **No code path rewrites a committed prediction.**

