# Round 4: code, CI, the live path and reproduction (`code`)

Verdict: GO. Nothing I found is wrong on a public surface today, and on this Mac a clean clone builds, tests and reproduces its tracked outputs byte for byte (the PDF aside). Every defect below shows up only after posting: a dashboard the daily job cannot redeploy (stale from the day after the first deploy), a next lock that nothing schedules or warns about, and tests that fail at that lock. All are S2 or lower; fix CODE-1 before or right after posting and the rest before GD reports 2026Q4.

Counts: S1 0, S2 6, S3 6

## Answers

Tree: `~/gdn-prepub/round4_clone_code`, branch `prepub-audit`, HEAD `e7b9d3d`. Scratch scripts: `~/gdn-prepub/agents/round4_code/` (`sim.py`, `sim2.py`, `clock.py`, `oldev.py`, `used.py`). The "replays" below run the project's pure functions (`live.update_latest`, `report.live_record`, `report.post`, `site_data.build`) on copies of the tree inside that folder, with score and lock files written by hand. They never call `run_lock`, `run_score`, `daily.run`, `gitops`, SEC or FAA code, and they are not pytest runs. Figures they print from made-up inputs are not quoted here.

### 1. Reproduce as a public reader

Followed README `## Reproduce` (README.md:163-176) literally in the clone, with no `data/raw/`.

| Command | Tail of output |
|---|---|
| `python3.11 -m venv .venv` | rc 0 |
| `.venv/bin/python -m pip install -r requirements.lock` | `Successfully installed contourpy-1.3.3 ... pyee-13.0.1`, rc 0 |
| `make all` | `SEC not read (offline run); keeping the tracked SEC series.` ... `workbook inputs unchanged; kept` / `chart inputs unchanged; kept` / `wrote report/note.html` / `wrote site/data.json` / `docs/LINKEDIN_POST.md: 1281 characters`, rc 0, 7.5 s |
| `git status --short` | (nothing) |
| `make test` | `176 passed, 2 skipped, 14 warnings in 61.08s`, rc 0 |
| `make check-determinism` | `identical (50 files)`, rc 0 |
| `git status --short` | (nothing) |

`make check-determinism` deletes the workbook and chart input stamps, so it forces the rebuild that `make all` skips; the clean status after it shows the tracked workbook and charts are reproduced byte for byte. `make all` printed the backtest lines the README reports (`holdout MAE {... 'seasonal': 4.615, ..., 'ratio': 5.523}`, `guidance sourced 22 band 18 of 26`).

The README gives the Python version (3.11 or later, README.md:172). It does not tell a stranger three things (CODE-8): the browser tests need `python -m playwright install chromium` (test.yml:16 runs it; without it `tests/test_site_a11y.py:42-46` skips the module, so `make test` passes with those tests unrun; my run had a Chromium already in this machine's Playwright cache, so the stranger's result is read from the test file, not run); the tests need a git checkout, because two fixtures run `git clone` of the tree (`tests/test_after_score.py:21`, `tests/test_prepub_text.py:116`), which fails on a "Download ZIP" copy; and `make all` keeps, not rebuilds, the workbook and charts when their stamps match, while README.md:174 says it rebuilds them.

### 2. The first run after going public

Readers of `"public"` (`grep -rn` over `src`, `site`, `tests`, `.github`, `tools`):
- `src/gdn/report.py:56-64` `lock_words`: a lock is called public only if `public` is true **and** `public_since` is set and on or before the release's `published_at` date. Used by the README Live record, the post and the note.
- `src/gdn/site_data.py:82-83` copies `public` and `public_since` into `site/data.json`; `site/app.js:116` applies the same two-field rule.
- `src/gdn/live.py:412-415` only shapes a log line, ignores `public_since`, and tells the owner to set `"public": true` (CODE-4).
- `tools/prepub/ledger_rules.py:205-206` (audit tool, two-field rule).

So flipping `"public": true` alone changes no visible text; with `public_since` set to the go-public day, the 2026Q3 lock (published 2026-10-29) stays "made while the repository was private", which is right, and later locks become "public GitHub release".

Pages: `pages.yml:3-6` deploys on a push to `main` that touches `site/**`, or on `workflow_dispatch`, and `pages.yml:16` skips while the repository is private. The daily job pushes with the default token (`nowcast.yml:16` checkout, `gitops.py:121` `git push origin HEAD`). GitHub's documentation says events triggered by the `GITHUB_TOKEN` "will not create a new workflow run", except `workflow_dispatch` and `repository_dispatch`. So no daily commit ever redeploys Pages (CODE-1). The flag flip touches `config/`, not `site/**`, so it does not deploy either.

The morning after the flip, the dashboard shows the `data.json` of whatever deploy last ran (the first one needs a manual dispatch or an owner push under `site/`). The featured card is 2026Q3's scored lock (`app.js:109-111` features the newest quarter with a lock or score), still correct. What goes stale from day two is the pipeline chart's snapshot date (`app.js:340`); after the 2026Q4 lock, the card keeps showing 2026Q3.

### 3. The next lock

`config/calendar.json` is `{"releases": {"2026Q3": "2026-10-30"}, "fiscal_ends": {}, "public": false}`. The live quarter is 2026Q4 (`live.py:73-79`; my `sim.py` printed `live_quarter now: 2026Q4 | release for it: None`).

The daily job skips quietly. `live.py:331-335` logs `no release date for 2026Q4; nothing to lock` and returns 0; the run stays green. Without a release date no subset is stored either (`live.py:188-196`; replay: `A1 in_lock_window 2027-01-26: False`). When GD's results 8-K appears, `run_score` still scores the quarter, unlocked (`live.py:442-479`, `score_quarter` sets `locked` false).

A public reader would see, in this order (replay wording):
- README, before the score: "not locked yet ... No release date is set in `config/calendar.json` yet, so no lock is scheduled." (`report.py:496-499`)
- README, after the score: "no lock (the quarter missed its window). GD reported N." (`report.py:484-485`). No window was ever set, so the stated cause is wrong (CODE-3).
- Dashboard after the score: 2026Q4 featured, status "Scored", the figure from `2026Q4_latest.json` labelled "deliveries, estimated", and the note "Not locked: the quarter missed its lock window, so this is the build estimate" (`app.js:168`). It is the latest estimate, not a build estimate (2026Q4 has no build file). The post is unchanged: one locked quarter.

Missing for 2027: `fiscal_ends["2027Q1"]`. `fiscal.py:48-57` returns `None` for any Q1 not in `fiscal_ends`, and Q2 and Q3 chain from it. Replay: `end 2027Q1 None | window 2027Q1 ('2026-12-31', None) | window 2027Q2 (None, None)`. After 2026Q4 is scored, `update_latest` logs `no estimate for 2027Q1: 2027Q1 has no fiscal end` and `run_score` returns 0 at `live.py:447-449` with no message, so 2027 gets no estimate, lock or score until it is added. Release dates for 2026Q4 and every 2027 quarter are also missing.

### 4. Lock and score integrity

- **Write a lock after the release time.** Absent on the scheduled path: `live.py:363-365` checks the run's `now` against the release date and, with `wall`, the real clock at least 10 minutes before 00:00 ET; `live.py:395-397` checks the real clock again just before `gh release create`. Tested (`test_live.py:308`, `:359`). Present as a manual footgun: any `--now` sets `wall` false (`__main__.py:54`, `daily.py:108`), so a rehearsal typed against the real tree would make a real release on a made-up clock, and `live.py:409-411` only warns afterwards; `live.py:468-474` then refuses to score a lock published at or after SEC's acceptance time (CODE-12).
- **Publish a lock whose hash differs from its release.** Guarded only after the release: the notes' sha256 is read from the working file (`live.py:394`), the release is created (`:399`), and only then `write_lock_json` compares the file with the tag and refuses the record (`live.py:283-294`). On the normal path the file was just committed, so they match. Nothing re-checks the prediction against the lock record's sha256 later: `score_quarter` reads `predictions/<Q>.json` as it stands (`live.py:430-435`), and `daily.py:22-28,116-121` auto-commits dirty files under `predictions/` as "Carry over". The real 2026Q3 record is clean (below).
- **Write a second lock in one quarter.** Absent: `live.py:343-344` (record exists), `:355-362` (release exists), GitHub tag uniqueness, and `:400-403` records a release another run made. Tested (`test_live.py:205`, `:279`, `:378`).
- **Score from the wrong exhibit or quarter.** Guarded by `sec.py:124-131` (first 8-K with item 2.02 filed within 70 days after the fiscal end) and `sec.py:117-121` (Exhibit 99.1 name), and `parse_deliveries` checks that the table adds up (`sec.py:199-201`). `run_score` does not check the release's period or cross-check its prior-year column against the reported series for the quarter a year earlier, which `data.py:86-92` does for the backtest. No path to a wrong score shown.
- **Print a lock on the missed-lock path.** Absent: `live.py:345-350` returns before any write. When a prediction was committed but no release made, the README says "no lock" (replay); the dashboard shows that unreleased prediction's figure (`site_data.py:61` sets `locked` from the file alone, `app.js:127` prefers it), labelled "estimated", "Not locked", and wrongly "the build estimate" (folded into CODE-3).
- **Dates at the DST end or a late-January release.** Correct. `clock.py` ran `lock_due`, `before_release` and `wall_clock_ok` (with `utcnow` fixed) across both cron slots for 2026-10-30 (EDT) and a 2027-01-27 release (EST): due only on the eve, never on the release date; midnight ET maps to 04:00Z in EDT and 05:00Z in EST. Every lock test uses October EDT times (`test_live.py:160-167`); there is no EST test. The real risk is the cron drift (CODE-5).

The 2026Q3 record:

```
$ shasum -a 256 predictions/2026Q3.json ; git show lock-2026Q3:predictions/2026Q3.json | shasum -a 256
3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23
3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23
$ git rev-list -n 1 lock-2026Q3 ; git log --format='%H %s' --diff-filter=AM -- predictions/2026Q3.json
a44e5aca3756941a075150d9e381020826f3fb81
a44e5aca3756941a075150d9e381020826f3fb81 Lock the 2026Q3 nowcast
```

Both equal `results/live/2026Q3_lock.json` (`sha256`, `commit`) and README.md:106. The file was added once and never modified.

### 5. Tests that will turn CI red in public

Bot pushes use the `GITHUB_TOKEN`, so they never start `test.yml` either. The daily commits leave a tree whose tests fail, and the red X lands on the owner's next push, on any pull request, or on a stranger's `make test`. Tests that pin today's live state (CODE-2), by replaying their steps:

After the 2026Q4 lock (`predictions/2026Q4.json` and `2026Q4_lock.json` exist; replay: `B1 dashboard featured after the 2026Q4 lock: 2026Q4`):
- `test_site_a11y.py::test_a_scored_lock_states_its_miss_and_its_band_in_the_past_tense` loads the tracked `site/data.json` and asserts the status starts `2026Q3` and says "missed by 8.0" (`:223-229`).
- `test_site_a11y.py::test_a_lock_made_after_the_repository_went_public_is_called_public` asserts "made while the repository was private" with `public_since` 2026-11-20 (`:243-245`); the featured 2026Q4 lock is later than that, so the replay gives "public GitHub release".
- `test_after_score.py::test_an_open_quarter_shows_no_partial_estimate[True]` and `[False]`: the fixture deletes only 2026Q3's files and `2026Q4_latest/path` (`:23-26`), so 2026Q4's prediction and lock remain and its README line carries "band" (replay: `'band' in q4: True`), against `:55`.

After the 2026Q4 score, also:
- `test_after_score.py::test_a_locked_and_scored_quarter_keeps_its_text` (`:74`), `::test_the_post_counts_its_locked_quarters` (`:115`) and `::test_the_readme_summary_block_is_rewritten_between_its_markers` (`:156`): the post and the README summary now count two locks (replay: `post starts 'My first locked estimate': False`; `report.live_summary` on the same copy starts `**Live record so far: 2 locked quarters`, so `'Live record so far: one locked quarter' in summary: False`).
- If 2026Q4 is scored without a lock, `test_an_open_quarter_shows_no_partial_estimate` instead stops at `next()` (`:54`) because no 2026Q4 line is left (replay: `README has a 2026Q4 line: False`).

`test_wording.py` reads README.md, the note and the post, but only for phrases the daily job does not change; `test_prepub_text.py::test_the_lock_timing_sentence...` reads the latest locked quarter dynamically. Neither breaks.

### 6. Workflows on a public repository

- **Permissions.** `nowcast.yml:6-7` `contents: write` (needed for the push and `gh release create`); `test.yml:5-6` `contents: read`; `pages.yml` `contents: read, pages: write, id-token: write`. All set at the workflow level, all scoped as tightly as each job allows.
- **Pinning.** By major tag (`actions/checkout@v4`, `setup-python@v5`, `configure-pages@v5`, `upload-pages-artifact@v3`, `deploy-pages@v4`), not by SHA, including in the job that holds write access and the SEC secret (CODE-11).
- **`pull_request` vs `pull_request_target`.** `test.yml:3-4` uses `push` and `pull_request`; no workflow uses `pull_request_target`. A fork's pull request runs only `test.yml`, with a read-only token and no secrets. It cannot reach `nowcast.yml` (schedule and dispatch only) or `pages.yml`.
- **Secrets in logs.** `SEC_UA` goes only to the `make daily` step; the code never prints it (`sec.py:31-39`, `:72-74`, `:267-279` return status text only), and GitHub masks secrets.
- **Concurrency.** `nowcast` group with `cancel-in-progress: false` (runs queue); `pages` group cancels in progress. A Mac `make daily` and a workflow run are not in one group; `.build/daily.lock` (`daily.py:92-104`) is per machine, and the cross-machine race rests on merges and tag uniqueness (`live.py:398-403`), which is sound.
- **Cron drift.** `'17 0,12 * * *'` (`nowcast.yml:4`, unchanged since the one commit that added the file). The bot's commit times in UTC put the 00:17 slot at 05:09 to 07:21 since 2026-10-27 and the 12:17 slot at 15:58 to 18:42. These are commit times, a proxy for run starts (CODE-5).

### 7. The unreviewed delta (`git diff 4ca7d35..HEAD -- src tests`, 8 files, +79 -16)

Read every hunk.
- `charts.py`: the pace label becomes "Pace built from GD's outlook" (`:31`, `:198`); `_preview` copies `output/charts/track_record.png` to `site/preview.png` on both the redraw and the "unchanged; kept" path (`:253-258`, `:269`, `:277`). Correct and tested (`test_prepub_text.py:198-213`). The same "GD guidance pace" label survives in `report.py:13` and reaches README.md:31 and :77 and the note's Exhibit 2, under the relabelled chart at README.md:11 (CODE-9).
- `daily.py:25`: `site/preview.png` added to `REBUILD_PATHS`. Correct.
- `note.py`: `old_events_line` (`:645-651`) is appended in the cover paragraph (`:315`) and in section 4 (`:487`), so the note says the same sentence twice (CODE-10). It calls `report.lock_old_events` (`report.py:252-263`), which feeds README.md:106 and the note, and no test covers it (CODE-6). My independent count agrees: `lock_old_events: (5, 42)` against cabin counts `{'large': 35, 'mid': 7}`. The band sentence softens from "likely too narrow" to "may not fit a live lock". The new Risks intro cites the product-cycle section, and the note does carry G400 timing there.
- `report.py:556-584`: shorter post opener and "Backtest (rules set minutes before scoring)". Post today 1281 of 1300 characters. My grid of two-lock states with wide numbers maxed at 1284 (`sim2.py`).
- `workbook.py:189`: "Miss, % of reported" format becomes `0%`, matching the README's 20%.
- Tests: the post cap test extended (F108), the wording tests follow the new phrase, and two new tests (preview image, pace label).

No bug that changes a figure; one untested path that feeds a public figure (CODE-6).

### 8. Code quality a hiring engineer would notice

- **Structure.** Small, single-purpose modules (`src/gdn`, 4,724 lines), one CLI table (`__main__.py:8-29`), every time-dependent function taking `now`, and a test suite that fakes git and gh (`tests/test_live.py`) and blocks the network (`tests/conftest.py`). This reads well.
- **Duplicated logic.** `report.lock_old_events` re-implements the window filter of `events.count` with inline imports (`report.py:254-262`). The "public" rule exists in three places (`report.py:56-64`, `app.js:114-117`, `live.py:412-413`), and the third disagrees with the other two.
- **Dead code.** `gitops.warn` (`gitops.py:165-166`) has no caller in `src/gdn` or `tools/` (`grep -rn 'warn(' src/gdn tools/*.py`). `live.unscored_quarters` wraps `live_quarter` for one caller.
- **Finding IDs.** 3 `F0xx` IDs in `src` comments (`daily.py:46`, `note.py:300`, `note.py:628`) and 31 in tests, plus `BUYSIDE-n` and review-round IDs in tests and `§n` spec-section references in docstrings (36 `BUYSIDE-n` and `§n` together). `test_wording.py:2` says its IDs refer to `docs/build/REVIEW.md`; the `F0xx` IDs belong to the pre-publication audit's files under `docs/prepub/`, which I may not open, so I have not shown that they resolve. A reader meets them with no key.
- **Broad `except`.** Four, all in `daily.py` (`:173`, `:185`, `:191`, `:204`). Each is deliberate and logged, and each sets a failing exit code, but it prints only `type: message`, so a CI failure loses its traceback. The guard at `:204` does not catch the `SystemExit` that `report.run` raises (CODE-7).
- **Developer docs.** README `## Reproduce` plus `docs/build/` (build-day notes, frozen). No CONTRIBUTING file, no note on running `make daily` safely (it commits, pushes, may open Chrome on a Mac, and may call `gh release create`), and nothing about `public_since` or `tools/eve_waiter.sh`. Enough to rebuild, not enough to contribute to the live path.

## Findings

### CODE-1 (S2): Pages never redeploys from the daily job's commits
Surface: `.github/workflows/pages.yml:3-6,16`, `.github/workflows/nowcast.yml:16`, `src/gdn/gitops.py:119-124`, `site/app.js:481`. Hand-written workflows.

Evidence: `pages.yml` deploys on `push` to `main` with `paths: ["site/**"]`, or on `workflow_dispatch`. The nowcast job pushes with the checkout's default token. GitHub's docs (docs.github.com, "GITHUB_TOKEN"): events triggered by it "will not create a new workflow run", with `workflow_dispatch` and `repository_dispatch` as the only exceptions. The dashboard reads `fetch("data.json", ...)` from the deployed artifact (`app.js:481`). README.md:176 says every daily commit since 2026-10-31 came from the workflow. So the README follows the job and the dashboard does not: from day two its pipeline snapshot date lags, and at the 2026Q4 lock it keeps featuring 2026Q3 until someone pushes under `site/` or dispatches `pages`. After a lock or score the owner's PDF rebuild may not change `site/` at all, because the note's target is fixed at 2026Q3 (`estimates.py:7`).

Fix: on go-public day, dispatch `pages` by hand (the flag flip touches `config/`, not `site/**`, so nothing else starts the first deploy) and confirm the Pages URL serves before posting. Then deploy Pages from `nowcast.yml` itself (a second job with `pages: write`, `id-token: write`, `needs: daily`, running the upload and deploy actions on the pushed commit), or trigger `pages.yml` with `workflow_run` on `nowcast` completion, and check that a deploy follows the next bot commit.

### CODE-2 (S2): Tests pin today's live state, so the 2026Q4 lock leaves a tree that fails `test.yml`
Surface: `tests/test_site_a11y.py:219-237`, `:240-251`; `tests/test_after_score.py:17-42`, `:49-56`, `:69-81`, `:111-115`, `:146-159`. Hand-written tests.

Evidence: replay output (`sim.py`):
```
B1 dashboard featured after the 2026Q4 lock: 2026Q4 | test_site_a11y.py:225 expects status to start with 2026Q3
B1 lockWords with public_since 2026-11-20: public GitHub release | test_site_a11y.py:245 expects 'private'
fixture on state B: README has a 2026Q4 line: True (test_after_score.py:54 takes next() over it)
'band' in q4: True | 'latest estimate' in q4: False | '2026-12-31' in q4: False
fixture on state B: post starts 'My first locked estimate': False (test_after_score.py:74 and :115 expect it)
fixture on state A: README has a 2026Q4 line: False (test_after_score.py:54 takes next() over it)
```
The `scored` fixture "puts back" the tree by deleting a fixed list of 2026Q3 and 2026Q4 files (`test_after_score.py:23-26`), and the dashboard tests read the tracked `site/data.json`. Bot pushes do not run CI, so the failure appears on the owner's next push or the first outside pull request after the lock. That is a red check on a public repository, or on a stranger's PR that changed nothing related.

Fix: in the fixtures, delete every live file for quarters after 2026Q3 (glob `results/live/*`, `predictions/*` other than the ones being rebuilt). In the two dashboard tests, select 2026Q3 from `data["live"]` and drop later quarters before loading, as `_before_any_lock` already does.

### CODE-3 (S2): The next lock is unscheduled and nothing warns; the record then blames a "missed lock window"
Surface: `config/calendar.json` (hand-written); `src/gdn/live.py:331-335`, `:447-449`; `src/gdn/fiscal.py:48-57`; `src/gdn/report.py:484-485` (README Live record, generated); `site/app.js:156`, `:168` (hand-written).

Evidence: no `2026Q4` release date and empty `fiscal_ends` (Answer 3). The lock step logs one line and returns 0; the score for a quarter with no fiscal end returns 0 with no message. Replay:
```
A2 README:  - **2026Q4**: no lock (the quarter missed its window). GD reported N.
A2 dashboard featured: 2026Q4 | locked: False | lock: False | score: True | release_date: None | figure source: latest
A2 update_latest: no estimate for 2027Q1: 2027Q1 has no fiscal end: add it under fiscal_ends in config/calendar.json
```
(N stands for the made-up count the replay used.) No window was ever set, so "missed its window" states the wrong cause. The dashboard's "this is the build estimate" (`app.js:168`) is wrong for any quarter but 2026Q3, and on the missed-after-commit path it shows the unreleased prediction (`site_data.py:61`, `app.js:127`).

Fix: add `"2026Q4": <GD's announced date>` as soon as GD announces it, and `fiscal_ends["2027Q1"]`. Make the daily run exit nonzero, with a WARNING, when the live quarter's fiscal end has passed and it has no release date, or when the next quarter has no fiscal end. Word the unlocked line by cause ("no release date was set" against "the lock window passed"), and call the dashboard figure "the latest estimate, never locked".

### CODE-4 (S2): `public_since` is required but undocumented, and the lock job names only `"public": true`
Surface: `src/gdn/live.py:412-415` (log), `src/gdn/report.py:56-64`, `site/app.js:114-117` (all hand-written code); `docs/PREREGISTRATION.md:70` (immutable; not to be edited).

Evidence: `live.py:414-415` tells the owner to set "public": true and does not mention `public_since`. `lock_words` and `lockWords` need both fields. The suite's own test row `({"public": True}, "made while the repository was private")` (`test_after_score.py:96`, which passed under `make test`) shows that `"public": true` alone keeps the private wording. `grep -c public_since` gives 0 for README.md, `docs/PREREGISTRATION.md`, `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md` and `docs/LINKEDIN_POST.md`, and `grep -rn` finds none in `docs/build/`. I may not read `docs/prepub/`, where the errata could document it. An owner who follows the job's own instruction gets a 2026Q4 lock, made after going public, that the README, note and dashboard call "made while the repository was private". That is a wrong sentence about the live record, though in the cautious direction.

Fix: change the log line to name both fields, and document `public_since` in the README's Live section (or set it in the same commit that sets `"public": true`).

### CODE-5 (S2): At the observed cron drift, the workflow's evening lock fallback looks out of reach
Surface: `.github/workflows/nowcast.yml:4`, `src/gdn/live.py:246-252`, README.md:176 (hand-written).

Evidence: `lock_due` locks on the eve when the newest table is dated the eve (a same-day FAA download, Chicago date, `faa.py:40-41`) or at 19:00 ET or later. Bot commit times (`TZ=UTC git log --author=github-actions`):
```
2026-11-12 07:14|Daily snapshot 2026-11-12
2026-11-11 06:26|Daily snapshot 2026-11-11
2026-10-29 18:29|Daily update 2026-10-29
2026-10-29 05:51|Lock the 2026Q3 nowcast
2026-10-28 18:22|Daily update 2026-10-28
```
In EDT the 00:17Z slot lands at about 01:10 to 03:20 ET and the 12:17Z slot at about 12:00 to 14:40 ET. No bot commit is timed between 19:00 and 23:50 ET. Commit times are a proxy for run times, and a run that changes nothing commits nothing (the 12:17Z slot has left no commit since 2026-10-30). `clock.py` with a failed eve download: every run on the eve before 19:00 ET gives `due False`, and the next runs land after midnight with `before_release False`. So if the FAA download fails on both eve runs, the workflow will not lock from the subsets stored in the window, though README.md:176 reads as if it falls back to them. `tools/eve_waiter.sh` (a Mac loop from 19:05 ET) covers this, but the README does not mention it. The January eve is in EST, where the early run gets the eve's Chicago date only after 01:00 EST. No test covers EST.

Fix: change the rule first. On the eve, once this run's download has failed, lock at any hour from the newest stored subset dated after the fiscal end, so the fallback does not depend on when GitHub starts the run. A cron slot cannot be timed for this: with no drift a slot at 20:17Z lands at 15:17 EST, and with the observed drift the 00:17Z slot lands after midnight. Add an EST case to `test_lock_due_rule`, and name `tools/eve_waiter.sh` in the README.

### CODE-6 (S2): The old-airframe count in the Live record and the note has no test
Surface: `src/gdn/report.py:252-263`, `:476-480`; `src/gdn/note.py:645-651`; feeds README.md:106 ("5 were airframes at least three years old") and the note (generated).

Evidence: `grep -rn 'lock_old_events\|old_events_line\|at least three years old' tests/*.py` prints nothing. The figure is right today: `oldev.py` printed `lock_old_events: (5, 42) | events.count by cabin: {'large': 35, 'mid': 7}`, and an independent count gave 5.

Fix: a test that builds a small daily table with known ages and asserts `lock_old_events` and the README and note sentences. Have it reuse `events.count`'s window rule rather than its own filter.

### CODE-7 (S3): The rebuild guard in `daily.py` does not catch the `SystemExit` that `report.run` raises
Surface: `src/gdn/daily.py:201-207`; `src/gdn/report.py:511`, `:522`, `:607` (hand-written code).

Evidence: `sim2.py`: `not caught by except Exception; SystemExit escapes: LinkedIn post is 1301 characters, over 1300`. The comment at `daily.py:204` says a rebuild error "must not stop the live files reaching GitHub", but a post over the cap or a missing README section would skip the final commit and push (`:207-215`). On CI, that run's snapshot table, latest and path rows would be lost. Today the post is 1281 characters and my two-lock grid maxed at 1284, so this is latent.

Fix: catch `(Exception, SystemExit)` there, or have `report.run` raise a `ValueError`.

### CODE-8 (S3): `## Reproduce` leaves out the browser, the git checkout, and what `make all` keeps
Surface: README.md:163-176 (hand-written).

Evidence: Answer 1. `test.yml:16` installs Chromium and the README does not. `test_after_score.py:21` and `test_prepub_text.py:116` run `git clone` of the tree. `make all` printed `workbook inputs unchanged; kept` and `chart inputs unchanged; kept`.

Fix: add `.venv/bin/python -m playwright install chromium` before `make test`, say to clone rather than download a ZIP, name `make check-determinism` as the full rebuild, and say what `make daily` does to git before naming it.

### CODE-9 (S3): The pace is relabelled in the charts but still "GD guidance pace" in the README tables and the note
Surface: `src/gdn/report.py:13` (generator of README.md:31, :77); `src/gdn/charts.py:31`; note Exhibit 2.

Evidence: the delta's test gives its reason: a legend that says "GD guidance pace" reads as GD's (`test_prepub_text.py:217`). Counts: README "GD guidance pace" 2, the note 1; "Pace built from GD's outlook" 0 on both. README.md:11 embeds the relabelled chart directly above the table at :31.

Fix: use the chart's label in `report.NAMES["guidance"]` and the note's exhibit, or explain the one label everywhere.

### CODE-10 (S3): The note says the old-airframe sentence twice
Surface: `src/gdn/note.py:315`, `:487`; `report/note.html` (generated).

Evidence: `grep -o 'so the raw count is not a count of new jets' report/note.html | wc -l` prints 2.

Fix: keep it in section 4 only.

### CODE-11 (S3): Actions pinned by tag in the job that can push and release
Surface: `.github/workflows/nowcast.yml:16,19` and the other two workflows (hand-written).

Evidence: `uses: actions/checkout@v4`, `actions/setup-python@v5`, in a job with `contents: write` and `SEC_UA`.

Fix: pin to full commit SHAs with the tag in a comment, at least in `nowcast.yml`.

### CODE-12 (S3): `--now` turns off the wall-clock check on the real repository
Surface: `src/gdn/__main__.py:54`, `src/gdn/daily.py:108`, `src/gdn/live.py:409-411` (hand-written code).

Evidence: `kw["wall"] = a.now is None`, and the comment calls a fixed `--now` a rehearsal. Nothing checks that the root is a rehearsal tree or that `gh` is a shim, so `python -m gdn daily --now <eve>` on the real checkout would publish a real release at any real time. The score refuses it later (`live.py:468-474`), but the tag would stay public.

Fix: refuse `--now` unless an environment flag names a rehearsal, or unless `origin` is not the GitHub repository.

## Improvements that would raise the project's standing

1. Deploy Pages from the nowcast workflow (CODE-1), and put a "data as of <snapshot>" line on the dashboard's first screen so staleness can be seen.
2. A "next lock" self-check in the daily run: a red run when the live quarter's fiscal end has passed with no release date, or the next quarter lacks a fiscal end (CODE-3).
3. Verify the record on every read: compare `sha256(predictions/<Q>.json)` with `<Q>_lock.json` before scoring and before printing, compute the release-notes digest from the target commit's bytes rather than the working file (`live.py:394`), and drop `predictions` from the carry-over paths (`daily.py:27-28`).
4. Make the state tests quarter-agnostic (CODE-2), and add an EST lock test plus an eve fallback that does not depend on when GitHub starts the run (CODE-5).
5. Cross-check each live score's prior-year column against the reported series, as `data.py:86-92` does for the backtest, so a wrong exhibit fails loudly.

## Checked and clean

- Clean-clone reproduction: install, `make all`, `make test` (176 passed, 2 skipped), `make check-determinism` (identical, 50 files), and `git status --short` empty after each.
- The 2026Q3 record: the file's sha256 equals the tag's file, the lock record and README.md:106; the tag commit equals the record's `commit` and the file's only adding commit.
- Lock timing arithmetic in EDT, EST and at the DST end (`clock.py`); one lock per quarter; no prediction written on the missed-lock path; the SEC-acceptance check on the score.
- No secret printed; `test.yml` uses `pull_request` with a read-only token; no `pull_request_target` anywhere; tests block outside network (`tests/conftest.py`).
- The delta: preview-image copy and its test, `REBUILD_PATHS`, the post cap in two-lock states (max 1284 of 1300 on my grid), and the workbook format.
- The used-jet figures: `note.used_share` prints 246 of 1,251 (19.7%), as README.md:157 says; the lock's old-airframe count of 5 of 42 recomputed independently.

## Suspicions, not proven

- "Python 3.11 or later" (README.md:172) is tested only on 3.11. `matplotlib==3.9.2` may have no wheel for the newest Python. Settled by a pip install on 3.13 and 3.14, which my brief does not allow.
- `results_8k` takes the first 8-K with item 2.02 in the 70-day window (`sec.py:124-131`). If GD filed a non-earnings 2.02 8-K first, every run would fail to parse it and never score. There is no evidence such a filing exists. Settled by listing GD's 2.02 8-Ks per quarter.
- How often the FAA download fails on CI, which sets how real CODE-5 is. The history cannot show it, because a failed download with unchanged outputs commits nothing. Settled by the Actions logs.
- A hand edit to a tracked prediction after its lock would be auto-committed by `daily.py:116-121` and scored as edited, with no hash re-check. That needs a manual edit; there is no automated writer.

## Could not check, and refused commands

- `gh release view lock-2026Q3 --repo <owner>/gulfstream-delivery-nowcast --json tagName,publishedAt,body,targetCommitish` was denied by the session's permission classifier, so the release notes' sha256 and `publishedAt` were not compared with the lock record here. Not routed around.
- `TZ=UTC git log ... -- .github/workflows/nowcast.yml` with `-p` was denied. `git log --oneline` on that path shows one commit, so the cron line never changed.
- Actual workflow run start times (`gh run` is barred). Drift is inferred from bot commit times.
- Pages behaviour on a public repository cannot be observed while private (`pages.yml:16` skips).
- `make test` on a machine without a cached Chromium, and pytest on the replayed states: neither allowed. Answers 1 and 5 rest on reading the tests and replaying their steps.
- Byte-for-byte reproduction on any machine but this Mac (Linux CI, another Python patch release): not run. `make check-determinism` excludes the PDF.
- I did not print pytest's skip reasons. The two skips match the two `source cache absent` skips in the tree (`test_claims.py:16`, `test_model.py:125`), but that is not confirmed.
