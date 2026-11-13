# Baseline (P0.3)

Measured on `prepub-audit` at `9c05aeb` (`origin/main` `36fed31` plus the P0.1 files), 2026-11-11 between 18:50 and 19:00 ET. Logs are in `.build/logs/` (untracked).

## Before

| Check | Command | Result |
|---|---|---|
| Tests | `make test` (log `p0_test.log`) | `6 failed, 114 passed, 14 warnings in 10.68s`, exit 2 |
| Gate, all ten families | the R11 command with `--only faa,truth,model,segments,prereg,live,workbook,docs,site,repo --output .build/gate_p0.json` (log `p0_gate.log`) | `42 assertions, 1 failing, 2 warning`, exit 1 |
| Offline rebuild | `make all` then `git status --short` (log `p0_make_all.log`) | exit 0; one file changed: ` M output/charts/nowcast_path.png` |
| Determinism | `make check-determinism` (log `p0_determinism.log`) | `identical (49 files)`, exit 0 |

### The six failing tests

| Test | Assertion that failed |
|---|---|
| `tests/test_after_score.py::test_a_missed_lock_is_said_in_the_post_and_the_note` | expects `missed its lock window` in the post; the post starts `One locked quarter so far: off by 3.0.` |
| `tests/test_after_score.py::test_a_locked_and_scored_quarter_keeps_its_text` | expects the post to start `One locked quarter so far: off by 3.9.`; it starts `... off by 3.0.` |
| `tests/test_site_a11y.py::test_a_scored_quarter_stays_featured_after_the_next_one_starts` | expects `#live-status` to start `2026Q3`; it reads `2026Q4 · SCORED` |
| `tests/test_site_a11y.py::test_without_a_lock_or_score_the_newest_quarter_is_featured` | expects `#live-status` to start `2026Q4`; it reads `2026Q3 · SCORED` |
| `tests/test_site_a11y.py::test_a_scored_quarter_without_a_lock_says_it_missed_the_window` | expects `missed its lock window` in the facts list |
| `tests/test_wording.py::test_exports_sources_and_claims` | expects `data-claim="os-release-date"` in `report/note.html` |

All six read the real tree's live state, which moved when 2026Q3 was locked and scored. They are traced in P5 (finding F003).

### The gate's lines that did not pass

- `FAIL N4 [('unused', 'os-release-date')]`: every cited claim in the note is in `report/claims.json`. The claim `os-release-date` is in `report/claims.json` but the note no longer cites it, because the note cites the release date only before a score.
- `WARN S3`: SEC segment figures for 2024Q3 and 2024Q4 could not be parsed by the gate (`unparsed`), so those pins were not compared with SEC in this run.
- `WARN L3 [('2026Q4', 'not locked yet', None)]`: expected, 2026Q4 has no lock.

The other 39 assertions passed: G0, F1 to F4, T1 to T3, M1 to M3, S1, S2, Q1, Q2, L1, L2, L4, W1 to W5, R1 to R4, K1, K2, N1 to N3, V1, Y1 to Y4, P1, P2.

### What `make all` changed

`output/charts/nowcast_path.png` only. The tracked copy dated from 2026-10-19 and showed no lock and no reported count. The rebuilt chart shows the locked estimate and GD's reported 40. This confirms lead L12 (finding F001). `output/charts/dashboard.png` is a screenshot that no `make` target writes (`tools/determinism.py` skips it); it still shows the 2026-10-19 page (finding F002).

## After

Measured 2026-11-12, about 09:47 to 09:53 ET, on a clean tree at commit `4c922cd`, after the last change to any public surface (the continue pass, DECISIONS D21) and after the merge of the daily workflow's 2026-11-12 commits (`bbf88fd`, D19) (P5.5, P6.4, P8.5, P8.6). The same battery ran at `89de502` before the merge and at `7a70d9e` after it; the gate, determinism and record lines were the same each time. One battery, run by two scripts; logs under `.build/logs/` (`final_a.log`, `final_b.log` and the files they name). Later commits change only files under `docs/prepub/`.

| Check | Command | Result |
|---|---|---|
| Offline rebuild | `make all`, `make claims`, `python -m gdn note`, `make pdf`, then `git status --short` | exit 0; `note unchanged; PDF kept`; status empty |
| PDF stamp | `shasum -a 256 report/note.html` against `output/GD_research_note.inputs.sha256` | equal: `e0b89a405ce56671...` |
| Tests | `make test` | `178 passed, 14 warnings in 28.45s`, exit 0 |
| Gate, all ten families | the R11 command, `--output .build/gate.json` | `42 assertions, 4 failing, 3 warning`, exit 1 |
| Determinism | `make check-determinism` | `identical (50 files)`, exit 0 |
| Ledger | `tools/prepub/ledger.py --root . --out docs/prepub/LEDGER.csv` (at `daf25c1`, the last commit that touches a public surface) | `rows 2864  flagged 0` |
| Revert tests (R6) | `tools/prepub/revert_check.py` on a fresh clone (`REVERT_TESTS.md`) | 22 fixes checked, 22 with FAIL when reverted and PASS when restored, 0 otherwise. |
| Nine plants on the final tree | `tools/prepub/plant_selftest.py` (`LEDGER_SELFTEST.md`, rerun section) | 9 planted, 9 caught, 0 missed. |
| Links | `tools/prepub/links.py` (`LINKS.csv`) | 191 links: 142 external resolve, 34 in-repo resolve, 12 point at the owner's repository or Pages site and return 404 until it is public, 3 external return 403 to an automated reader |
| Record | every hash in `RECORD_HASHES.txt` recomputed; `git diff --stat 36fed31..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` | 59 of 61 match. The two that differ are the open quarter's working files, `results/live/2026Q4_latest.json` and `results/live/2026Q4_path.csv`, each equal to its version in `origin/main` `8c7692f` (DECISIONS D20). A diff from `36fed31` over `predictions/`, `docs/PREREGISTRATION.md`, `.github/` and the 2026Q3 lock and score files prints nothing |

### The gate's lines, after

35 assertions pass, 4 fail, 3 warn. Passing families: `faa`, `truth`, `model`, `segments`, `prereg`, `live`, `workbook`, `repo`. The baseline's one failure, `N4`, passes.

Warnings:

- `WARN T3`: `{'unpinned later calls': ['2026-10-30']}`. New: the 2026-10-30 call added to `data/guidance.csv` (F054) is later than the calls the gate pins.
- `WARN S3`: unparsed segment cells for 2024Q3 and 2024Q4 in the gate's own SEC parse. In the baseline.
- `WARN L3`: `['2026Q4', 'not locked yet', None]`. In the baseline.

Failures, all four in the `docs` and `site` families and all four caused by sentences and fields this audit added (DECISIONS D10, under R11). The gate prints at most eight items per list:

- `FAIL R2` (every number in Results, Error analysis and Live record is a figure the gate computed): `0.20, 117, 6.7, 43.1, 5.7, 12.5, 3.5, 6.4`.
- `FAIL K1` (every number in the post, the bullets and the interview notes is a figure the gate computed): `12.5, 3.5, 6.4, 0.76, 0.95, 246, 1,251`.
- `FAIL N1` (every number in the note is a figure the gate computed): `117, 6.7, 0.76, $826, 23.4%, $95, 2.7%, $5.0`.
- `FAIL Y1` (`site/data.json` holds what the gate computes): unexpected keys `public`, `public_since`, `reported_segments`.

## Fresh clone (P8.4)

`git clone --branch prepub-audit` of this repository into `~/gdn-prepub/clone2`, `data/raw/` copied in, `origin` set to the GitHub URL, `python3.11 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.lock` (exit 0). Then, after `git pull` of the final commit `4c922cd`:

| Check | Result |
|---|---|
| `make all`, then `git status --short` | exit 0; status empty |
| `make test` | `178 passed, 14 warnings in 30.40s`, exit 0 |
| `make check-determinism` | `identical (50 files)`, exit 0 |
| Gate, all ten families, `--repo ~/gdn-prepub/clone2` | `42 assertions, 4 failing, 3 warning`: the same four failures and three warnings as the main tree, number for number |

The first attempt, in `~/gdn-prepub/clone` with this Mac's `python3` (3.9.6), failed at `pip install`: `No matching distribution found for contourpy==1.3.3`. The README gave no setup step. That is finding F099, fixed (DECISIONS D14); the log is `.build/logs/clone_check1.log`.

### As a public reader gets it: no raw files

The clone above had `data/raw/` copied in, as P8.4 says. A reader of the public repository has only the tracked files, and the README says `make all` rebuilds from them. Checked 2026-11-12 in a third clone, `~/gdn-prepub/clone3`, at `59b05b0`, with no `data/raw/` and the project's Python (`PY=` set to the main environment): `make all` exit 0 and `git status --short` empty; `make test` prints `176 passed, 2 skipped, 14 warnings in 32.78s`, exit 0, status still empty. The two skips are `tests/test_claims.py:16` and `tests/test_model.py:125`, each with the reason "source cache absent, as in a clone". Log: `.build/logs/clone3_noraw.log`.

## Merge check (P8.5)

- 2026-11-11, 21:06 and 22:09 ET: `origin/main` was still at `36fed31`; `git merge --no-commit --no-ff origin/main` on the throwaway branch `prepub-mergecheck` printed `Already up to date.`
- 2026-11-12, 09:25 ET: `origin/main` had two new commits from the daily workflow (`1481ce0`, `8c7692f`). A trial merge on `prepub-mergecheck2` stopped on two generated files, `README.md` and `report/note.html`. Both were regenerated from the merged data, the merge was committed (`bbf88fd`) and `prepub-audit` was fast-forwarded to it (DECISIONS D19). `git log prepub-audit..origin/main` is now empty, so `main` can take `prepub-audit` with no conflict until the workflow commits again. `GO_PUBLIC.md` step 2 says what to do when it has.

## Round 4 (11 auditors), before launch

Measured 2026-11-12, 13:59 to about 14:10 ET, on a clean tree at the frozen commit `4388294`, before any round 4 file existed. `git fetch --all --prune` at 13:59 ET: `git log --oneline prepub-audit..origin/main` printed nothing, and `origin/prepub-audit` equals `4388294` (DECISIONS D23). `make all` was not run in the owner's checkout this round; the `code` auditor runs it in its own clone.

| Check | Command | Result |
|---|---|---|
| Gate, all ten families | the R11 command, `--output .build/gate_round4.json`, log `.build/logs/round4_gate.log` | `42 assertions, 4 failing, 3 warning`, exit 1. Failing: `R2`, `K1`, `N1`, `Y1`, with the same lists as D18. Warnings: `T3`, `S3`, `L3`. |
| Tests | `make test` | `178 passed, 14 warnings in 85.57s` |
| Determinism | `make check-determinism` | `identical (50 files)` |
| Record | `shasum -a 256 -c docs/prepub/RECORD_HASHES.txt` | 59 of 61 OK. The two that fail are `results/live/2026Q4_latest.json` and `results/live/2026Q4_path.csv`, as in D20. `predictions/2026Q3.json` hashes to `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`. |
| Ledger | `tools/prepub/ledger.py --root . --out <scratch>/LEDGER_round4.csv` | `rows 2864  flagged 0`; `cmp` with the committed `docs/prepub/LEDGER.csv` finds no difference. |

### Round 4, after the register and verdict

At `f88b7c8`, a clean tree that differs from `4388294` only under `docs/prepub/`: the full gate (`--output .build/gate_round4_final.json`) printed `42 assertions, 4 failing, 3 warning`, with the same `R2`, `K1`, `N1`, `Y1` lists and the same `T3`, `S3`, `L3` warnings as before launch. `shasum -a 256 predictions/2026Q3.json` printed `3c4cdbd0...6f23`. `git diff --stat 4388294..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` printed nothing.

## Round 4 fix pass, after

Measured 2026-11-12 between 20:45 and about 20:50 ET, on clean trees at `b461695` and `de26f49` (the last commit that touches a public surface is `de26f49`, which shortened a resume bullet).

| Check | Command | Result |
|---|---|---|
| Tests | `make test` | `197 passed, 14 warnings in 47.60s` (at `b461695`) |
| Determinism | `make check-determinism` | `identical (50 files)` |
| Offline rebuild | `make all`, then `git status --short` | exit 0; status empty |
| PDF stamp | `shasum -a 256 report/note.html` against `output/GD_research_note.inputs.sha256` | equal: `ea2b7d56533ea144...` |
| Gate, all ten families | the R11 command, `--output .build/gate_round4_fix.json` | at `de26f49`: `42 assertions, 4 failing, 3 warning`, the same IDs as D18 (`R2`, `K1`, `N1`, `Y1`); N1's list now names the note's new figures (DECISIONS D24). At `b461695` a fifth, `K2`, failed on a 246-character resume bullet; `de26f49` shortened it to 218. |
| Ledger | `tools/prepub/ledger.py --root . --out docs/prepub/LEDGER.csv` | `rows 2923  flagged 0` |
| Nine plants | `tools/prepub/plant_selftest.py`, copies `plantA8`, `plantB8` at `de26f49` | 9 planted, 9 caught, 0 missed |
| Revert tests (R6) | `tools/prepub/revert_check.py ~/gdn-prepub/scratch/revert_round4` (`REVERT_TESTS.md`) | 36 fixes checked, 36 FAIL when reverted and PASS when restored |
| Fresh clone, no `data/raw/` | `git clone` to `~/gdn-prepub/clone_round4`; `make test`, `make all`, `git status --short` with the main checkout's venv | `195 passed, 2 skipped`; `make all` exit 0; status empty |
| Record | `shasum -a 256 -c docs/prepub/RECORD_HASHES.txt`; `git diff --stat 4388294..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` | 59 of 61, as in D20; the diff prints nothing |

### Round 4, final (after F130)

Measured 2026-11-12 from 21:06 ET on a clean tree at `2393a18`, after the last change to any public surface (`4f96be4`).

| Check | Result |
|---|---|
| `make test` | `198 passed, 14 warnings in 56.10s` |
| `make check-determinism` | `identical (50 files)` |
| `make all`, then `git status --short` | exit 0; status empty |
| PDF stamp | `sha256(report/note.html)` equals `output/GD_research_note.inputs.sha256` (`ea2b7d56533ea144...`) |
| Gate, all ten families (`.build/gate_round4_final.json`) | `42 assertions, 4 failing, 3 warning`: `R2`, `K1`, `N1`, `Y1`, as in D18 and D24 |
| Ledger | `rows 2923  flagged 0` |
| Nine plants (`plantA9`, `plantB9`) | 9 planted, 9 caught, 0 missed |
| Revert tests (`~/gdn-prepub/scratch/revert_round4b`, `REVERT_TESTS.md`) | 37 fixes checked, 37 FAIL when reverted and PASS when restored |
| Fresh clone without `data/raw/` (`~/gdn-prepub/clone_round4b`) | `196 passed, 2 skipped` |
| Record | 59 of 61 hashes, as in D20; the protected-path diff from `4388294` prints nothing |

### Round 4, last (after the advisor's review)

At `fc3157c`, a clean tree (its only code change since `2393a18` is the chart title for two or more locks, which leaves today's image byte-identical): `make test` `198 passed, 14 warnings in 48.07s`; `make check-determinism` `identical (50 files)`; `make all` exit 0 with an empty status; gate (`.build/gate_round4_last.json`) `42 assertions, 4 failing, 3 warning`, the IDs `R2`, `K1`, `N1`, `Y1` of D18 and D24; ledger `rows 2927  flagged 0`; the protected-path diff from `4388294` prints nothing.
