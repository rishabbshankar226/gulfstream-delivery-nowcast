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

(P5.5 and P6.4 fill this in.)
