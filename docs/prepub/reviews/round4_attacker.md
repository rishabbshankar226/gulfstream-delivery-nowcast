# Round 4: attacker of the earlier audit

Verdict: NO-GO. F015, F016 and F081 are still open with no owner decision logged, and the note's first page carries one more open S2 that the earlier audit counted as fixed (ATTACKER-1).

Counts: S1 0, S2 3, S3 5

Tree: `~/gdn-prepub/round4_clone_attack`, branch `prepub-audit`, `HEAD` `e7b9d3d`. `git status --short` printed nothing before and after my work. Scratch scripts are in `~/gdn-prepub/agents/round4_attacker/`. Every number below was printed by a command I ran on this tree, or read from the source named beside it.

## Answers

### 1. The verdict's measurements, row by row

| # | Status | Evidence |
|---|---|---|
| 1 | confirmed | `count_findings.py` on `FINDINGS.md`: `S1 {'fixed': 19, 'open': 2, 'refuted': 3}`. The open two are F015 and F016. The F015 measurement inside the row is wrong in its count of commits: see ATTACKER-2. |
| 2 | confirmed "no"; measurement text wrong if ATTACKER-1's grade is upheld | F081 is open, and `sed -n 15p README.md` printed the undated "I hold no position in General D..." line. The row also says "No other S2 is open on those five surfaces". ATTACKER-1 grades the note's first page S2 by the audit's own precedent (F087, F089). |
| 3 | confirmed for the file, cannot check the plants | A script over `docs/prepub/LEDGER.csv` printed `rows 2864` and `Counter({'traced': 2864})`. Rerunning the ledger or the nine plants means running `tools/prepub/*.py`, which are not scratch scripts. |
| 4 | criterion holds, measurement text **wrong** | Summing `RECOMPUTE_DIFF.md` printed `compared 547 match 547`. The row says `git diff --stat 36fed31..HEAD -- results data/processed` "lists only files the audit added". It lists five files, two of them the workflow's: see ATTACKER-3. |
| 5 | confirmed | `gh release view lock-2026Q3 ... --json publishedAt,author,tagName,body,targetCommitish` printed `2026-10-29T05:51:24Z github-actions[bot] lock-2026Q3`, with the hash in the body `True`. `git rev-parse lock-2026Q3^{commit}` printed `a44e5aca3756`. `git log --format=%H origin/main \| grep -c '^a44e5ac'` printed `1`, and the same for `HEAD`. The SEC filing index of 0000040533-26-000036, fetched by `urllib`, printed `Accepted -> 2026-10-30 08:09:27`. `shasum` of `predictions/2026Q3.json` matches. |
| 6 | partly confirmed | `gh repo view ... --json visibility` printed `"PRIVATE"`, so 404s are expected today. Whether the links resolve after steps 4 and 5 cannot be checked before those steps. |
| 7 | cannot check by read-only command | `make`, `pytest` and the gate are outside my allowed commands. |
| 8 | confirmed | `grep -c` on `docs/INTERVIEW_NOTES.md`: `32.0` 2, `21.2 to 37.2` 2, `01:51 ET` 1, `reported 40` 2, `8.0` 3, `6.2` 3. `docs/RESUME_BULLETS.md:2` gives the lock, 32.0, 40, a miss of 8.0 and "outside its band". |
| 9 | confirmed | `reviews/round3.md:9`: "Counts: S1 0, S2 4, S3 6". Its four S2 fixes are on the tree. The workbook diff prints `Live B18 ... 0.0% -> ... 0%`. The note PDF holds "5 were airframes at least three years old" 2 times. `INTERVIEW_NOTES.md:33` carries "minutes before and in the same session". The post reads "Backtest (rules set minutes before scoring)". |
| 10 | confirmed | A script over the three files printed: deliveries `{'verified': 43}`; guidance `{'verified': 24, 'verified elsewhere': 3, 'not in file': 1}` (the 2026-10-30 row, F054); claims `verified 202, verified elsewhere 2`, and 23 others. Every one of the 23 cites F004, F013, F035, F036, F043, F052, F065 or F066. |
| 11 | confirmed | `shasum -a 256 -c docs/prepub/RECORD_HASHES.txt`: 59 `OK`; `results/live/2026Q4_latest.json` and `results/live/2026Q4_path.csv` `FAILED`. |
| 12 | confirmed | F015 and F016 are open in `FINDINGS.md`. No decision on A or B is in `DECISIONS.md`. |
| 13 | confirmed | `grep -E '\| *(todo\|cut\|open\|doing)' PLAN.md` printed nothing. The table has 41 `\| done` rows, and "Cut items" reads "(none)". |

### 2. The unread delta (`4ca7d35..HEAD`)

`git diff --stat 4ca7d35..HEAD` over the surfaces, code and data changed 29 files. Each public sentence and figure that changed, against its source:

| Surface | Change | Check |
|---|---|---|
| `README.md:92` | "the same in every daily snapshot since, to 2026-11-12" | `q3count.py` (the project's `events.count` on each daily table) printed `35 7 42` for every table from 2026-10-29 to 2026-11-12. Holds. |
| `README.md:107` | "the 2026-11-12 snapshot counts only part of it" | `results/live/2026Q4_latest.json` `snapshot` is 2026-11-12. Holds. |
| `docs/LINKEDIN_POST.md:6` | "Backtest (rules set minutes before scoring):" | `git log`: `5c84d36` and `2c62ad3` at 11:02:12, scores `48c1ea0` at 11:04:28, all on 2026-10-19. Holds. |
| post | "Repeating the same quarter last year missed by less on average, 4.6." and "The test reads a registry copy ..." | `recomp.py`: `seasonal 26 4.6154`. Holds. |
| post | length | `wc -m` 1281. Python `len` 1281, and 1280 stripped. The post equals the paste-ready copy in `GO_PUBLIC.md` step 8 (`diff` printed nothing). |
| `report/note.html:56`, `:78` | "Of the 42 events in the raw count, 5 were airframes at least three years old by the registry's year of manufacture" | `g700row.py` on the lock's table (`2026-10-29`) printed 42 events and 5 at least three years old by the year field. One of the five is G700 serial 87118, year field 2006, first airworthiness 2026-03-06. Seven events have no year: one `G-IV` and six `G280`. The sentence says "by the registry's year of manufacture", so it is true of the field. R3-2 raised the G700 already, and I do not raise it again. |
| note product cycle | "Gulfstream began G700 deliveries in the second quarter of 2024." | The claim quote in `report/claims.json` (`pc-g700-first-deliveries`) supports it. Holds. |
| note Risks | opens with "the planned production break between the last G280 and the G300, and the timing of the G400" | Claims `pc-g280-final-delivery` and `pc-g400-timing-update` quote the 2026-07-29 call. WebFetch of the Fool page returned the 400 sentence and both halves of the G280 and G300 passage. Holds. |
| note, `site/app.js:170`, interview notes | "may not fit a live lock" / "a live quarter" | Wording only. |
| `site/index.html:12-13` | `og:image` to `preview.png`; alt "GD's reported Gulfstream deliveries by quarter against the five estimates" | `shasum`: `site/preview.png` equals `output/charts/track_record.png` (`7a50239d...`). I viewed it. It shows GD reported plus five series, under the title "GD's count against five estimates". Holds. |
| `site/data.json` | `pipeline_snapshot` and the 2026Q4 `latest` move to 2026-11-12; a new path row | `q4count.py` printed `2026Q4 to 2026-11-12: 17 2`, and `2026Q4_latest.json` has trailing registry `188`, `30`, matching the new row. Holds. |
| workbook | `Live!B18` format `0.0%` to `0%` | `wbdiff.py` (old file from `git show 4ca7d35:...`) printed that one cell and nothing else. 8.047 over 40 shows as 20%. Holds. |
| charts | legends now "Pace built from GD's outlook" | Seen on `preview.png`. Holds; the naming split is F098. |
| PDFs | rebuilt | `shasum -a 256 report/note.html` equals `output/GD_research_note.inputs.sha256` (`e0b89a40...`). The two PDF copies are identical (`ba3441e2...`). pypdf: 8 pages, footer on 8 of 8, the new Risks sentence present 1 time, "20.1%" 0, "likely too narrow" 0, "newest dated" 0. |

Nothing in the delta is a wrong figure. The one open S2 I found sits in text that predates `4ca7d35` (ATTACKER-1).

### 3. Figures the audit added, against primary sources

**D10 and D18 gate lists.** Each was recomputed from tracked files (`recomp.py` and inline scripts) or read from the filing:

- `0.20`: `1/sqrt(26) 0.1961`.
- `117`, `6.7`: `outlook_2021_as_117` guidance `6.657`.
- `43.1`: `2023Q3 guidance 43.07441860465116 27`.
- `5.7`: `quarter_plans_and_2021_as_117` guidance `5.703`.
- `12.5`, `3.5`, `6.4`: `2023-24 8 {'guidance': 12.5149, 'ratio': 3.4817}` and `other 18 {... 'ratio': 6.4308}`.
- `0.76`, `0.95`: `predictions/2026Q3.json` trailing 140+23 over 187+28 (0.758), and 40 over 42 (0.952).
- `246`, `1,251`: events after 2015-12-31 through 2026-07-05 printed `(1251, 246, 76, 75)`.
- `$826M`, `23.4%`, `$95M`, `2.7%`, `$5.0B`, `$185M`, `3.7%`: `site/data.json` gives Aerospace from the estimate 2,710.3, Aerospace drift 3,631.4 and Marine drift 4,775.4 ($M). The 8-K exhibit (urllib, `ex991.txt`) prints Aerospace 3,536 and Marine Systems 4,960. The differences give -826 (-23.4%), +95 (2.7%) and -185 (-3.7%). `data/processed/segments_reported.csv` matches the exhibit's revenue and operating earnings for all four segments.

All hold.

**Constants in `tools/prepub/ledger_rules.py`.**

- Marine Systems backlog 146,865 ($M): Exhibit H of the 8-K prints "Marine Systems 47,289 99,576 146,865". Holds.
- "about 11" demonstrators: WebFetch of the Fool page for the 2022-01-26 call returned Novakovic's sentence on test aircraft and a few demonstrators, about 11 aircraft in all. Holds, read through WebFetch's summariser.
- 2027 and 2028: WebFetch of the 2026-07-29 page returned the G300 passage with late 2027 and, on a second question, early 2028 as the years given. Holds.
- Engine-type codes 4 and 5: `src/gdn/faa.py:184` keeps `TYPEENG` in `("4", "5")`. Holds.
- Engine-type code 2 on ACFTREF `3980222`: cannot be checked from tracked files. Every stored `ACFTREF.txt.gz` is the scoped subset and holds only `3980221` (engine type 5). The FAA inquiry page returned 403.
- The study's as-of date 2026-10-13: could not check (see "Could not check").

**`data/guidance.csv:29` (2026-10-30).** WebFetch of the Fool transcript returned the two sentences word for word as in the row (the first is "We do not plan to update segment guidance."). It returned the turn label "Phebe Novakovic". The participants list prints "Chairman and Chief Executive Officer - Phebe Novakovic", which matches the row's speaker. The date "Oct. 30, 2026" matches. Asked for every sentence with a delivery number, the page gave 40 for the quarter and 200 in 2030, found no "160", and no fourth-quarter delivery figure. So the blank outlook is right under the rule, and the 2026Q4 pace still rests on 160. The row holds. F107 (no cached copy) stays open as a cache gap only.

### 4. Wrong closures

**Seeded draw.** `draw.py`: population = the 67 rows at S1 or S2 whose status starts `fixed`, sorted by ID; `random.seed(20261112)`; `random.sample(rows, 10)`.

| Row | Check on the tree | Commits touch the named surfaces |
|---|---|---|
| F008 S1 | stamp equals `sha256(report/note.html)`; PDFs identical; "newest dated" 0 in the PDF | yes |
| F018 S1 | guard at `src/gdn/live.py:468-474`; test `tests/test_live.py:539` exists. Holds when EDGAR gives an acceptance time; the guard is skipped when it does not (ATTACKER-8) | yes |
| F030 S2 | "not investment advice" on README (2), post (1), `site/index.html` (1), note (2), workbook `About!A3`; footer on 8 of 8 PDF pages | yes |
| F058 S1 | `data/quarter_plans.csv` six rows; README line 49; `quarter_plans` guidance `6.018`, closer 12 of 26; the 2023-07-26 quote matched on the Fool page | yes |
| F082 S2 | README Data bullet; 2016 rows filed 2017-04-26 to 2018-01-24 | yes |
| F084 S1 | "had years to fill" 0 on the post, README, note, `app.js` and interview notes | yes |
| F088 S2 | "the last three held-out quarters": README 2, note 1, `app.js` 1; bare form 0 | yes |
| F092 S2 | `INTERVIEW_NOTES.md:7` carries the qualifier | yes |
| F103 S2 | `INTERVIEW_NOTES.md:33` carries the qualifier | yes |
| F108 S2 | `report.py:561` short opener; `POST_MAX = 1300` at `:515`; test at `tests/test_after_score.py:111` | yes |

Ten of ten hold on the tree (`touch.py` printed `yes` for every surface). F018 holds only in part (ATTACKER-8).

**Found outside the draw:**

- F029, F012 and F089 are `fixed` because each surface says somewhere what the pace, the registry count and the band are. The note's first page says none of the three, and F087 set the standard for a first-screen surface (ATTACKER-1).
- F015's count of 124 is author and committer lines, not commits (ATTACKER-2).
- F016's "equals" is wrong as written (ATTACKER-5).
- F068 names "workbook labels" but its open reason leaves them out (ATTACKER-6).
- R3-2's second part, the G700 among the five, was closed with a qualifier that keeps the sentence true of the year field (see Q2). I do not raise it.
- On errata that should be fixes: none of E1 to E10 is a fix within the audit's reach that it ducked. E3 needs a PDF engine in CI, which means `.github/`.

### 5. The NO-GO

It is right. F015 and F016 (criteria 1 and 12) and F081 (criterion 2) are open, and `DECISIONS.md` logs no decision on them. Beyond those three:

- ATTACKER-1 is a further open S2 on a first-screen surface, so criterion 2 fails on more than F081. It is fixable in the generator, unlike the three owner items.
- F018 (S1, `fixed`) holds on the path EDGAR serves today. Its untested empty-acceptance branch is ATTACKER-8, graded S2. I found no new S1.
- The band's undercoverage was tested as a possible regrade. The post says "outside my 80% band of past misses" with no coverage figure. The round 2 statistician named that exact wording as enough for the post (`reviews/round2_statistician.md:162`), so I leave the post alone. The note's first page has neither the level nor the coverage, and that goes into ATTACKER-1.
- F098's naming split stays S3. Three names for the pace sit on the README's first screen: "a pace built from GD's own guidance" (line 3), "GD's guidance pace" (live summary) and "Pace built from GD's outlook" (the image's legend). Line 3 defines the pace before either other name appears. That makes it wording, not a misleading frame.
- No other open S3 is an S2 on a first-screen surface.

### 6. The record

- `shasum -a 256 predictions/2026Q3.json` printed `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`. It matches.
- `git diff --stat 36fed31..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` printed three files: `data/snapshots/daily/2026-11-12.serials.csv.gz` (new, 60028 bytes), `results/live/2026Q4_latest.json`, `results/live/2026Q4_path.csv`.
- `git rev-parse HEAD:<f>` equals `git rev-parse 8c7692f:<f>` for all three. `1481ce0` (author `github-actions[bot]`) added exactly these three.
- D20 explains the two `2026Q4` files by name. It does not name the new snapshot file. D3 covers it in general ("new files under `data/snapshots/daily/`"), D19 covers it as part of the merge, and `RECORD_HASHES.txt` has no line for it (ATTACKER-4). Nothing in `predictions/`, the 2026Q3 lock and score, `docs/PREREGISTRATION.md` or `.github/` changed.

## Findings

### ATTACKER-1 (S2). The note's first page uses "registry count", "GD's guidance pace" and the band with none of the glosses the post and the README's first screen carry

- **Surface:** `report/note.html:55-56` (key points 1 and 2, PDF page 1), generated by `src/gdn/note.py`.
- **Evidence:**
  - pypdf on `output/GD_research_note.pdf`, counting page by page:

    ```
    page 1 {'80%': 0, '18 of 26': 0, '69.2%': 0, 'nominal': 0, 'registry estimate': 1, 'scaled': 0, 'my construction': 0, "GD's guidance pace": 2}
    page 2 {... 'scaled': 1, 'my construction': 1, "GD's guidance pace": 3}
    page 3 {'80%': 1, '18 of 26': 1, '69.2%': 1, 'nominal': 1, ...}
    ```

  - Page 1 carries the preregistered sentence ("the registry count was off by 5.5 ..., against 6.9 for GD's guidance pace"). A few lines later it says "the raw registry count (42)". So "registry count" means two things on the page, and the pace twice reads as GD's own figure.
  - The note glosses both on page 2 (`note.html:68`) and gives the band's level and its 18 of 26 on page 3.
  - The same page says the lock missed "outside the band" with neither the band's level nor its backtest coverage.
  - The audit graded each of these S2 when it was missing from the post or the README's first screen: F087 for the two terms on the post, F089 (STAT-10) for the band. It required the gloss on the same screen.
  - F029 and F089 were closed for the note because the note explains each somewhere.
  - Criterion 2 names the note's first page as its own surface.
- **Also, not graded:** on the dashboard the lead and the live card call the pace "GD's guidance pace" (`site/app.js:14`, `:94`, `:147`). The explanation sits under "How it was tested" (`site/index.html:73`, `:103`). I infer from HTML order, not a rendered page, that this is below the first screen, so I leave the dashboard to the rendered-page auditor. The lead says "registry estimate", so only the pace is unglossed there.
- **Fix:**
  - In `note.py`, follow key point 1 with the post's clause, e.g. "(Registry count: my scaled estimate; the pace: my construction from GD's full-year outlook.)".
  - Give the band its level and coverage in key point 2, as the README's live summary does ("nominal level is 80% and which held 18 of 26").
  - Then `make all`, `make claims`, `make pdf`, and check the stamp.
  - The preregistered sentence stays word for word.

### ATTACKER-2 (S2). F015's "124 commits" counts author and committer lines, not commits, and leaves out that the merge adds 59 more

- **Surface (hand-written, all public with the merge):**
  - `docs/prepub/FINDINGS.md:28` (F015)
  - `docs/prepub/VERDICT.md:9`, `:50`
  - `docs/prepub/GO_PUBLIC.md:9` (decision A)
  - `docs/prepub/EXPOSURE.md:10`
- **Evidence:** a script over `git log` (addresses hidden, counts printed):

  ```
  36fed31     commits 107 non-bot author addresses 1 counts [62]  author+committer lines non-bot 124
  origin/main commits 109 non-bot author addresses 1 counts [62]  author+committer lines non-bot 124
  HEAD        commits 168 non-bot author addresses 1 counts [121] author+committer lines non-bot 242
  audit-era commits 36fed31..HEAD 61 {'personal-or-other': 59, 'actions-bot': 2}
  ```

  - The personal address is on 62 commits of `main`, as author and committer. 124 is 62 times two.
  - The command decision A gives the owner (`git log --format='%ae' | sort | uniq -c`) prints 62, so the owner's check will not reproduce the audit's figure.
  - Step 2 merges `prepub-audit` with `--no-ff`, which publishes the 59 audit commits made with the same address. That brings the total to 121 commits, and decision A does not say so.
- **Severity note:** by `round4_common.md`'s S1 line ("a wrong number on any public surface") this could be read as S1, since `docs/prepub/` goes public. I grade S2 because the figure is about the exposure, not the project, and the owner's choice between A's two options does not turn on it.
- **Fix:**
  - Write "62 commits of `main`" in the four places.
  - Add to decision A that merging `prepub-audit` adds 59 more.
  - Say whether a squash merge is an option the owner wants to weigh. It keeps every existing hash, including `a44e5ac`, but it drops from `main` the audit commits that `FINDINGS.md` cites by hash. It also helps only if `origin/prepub-audit`, which D21 and D23 say is already on GitHub, is deleted before the repository goes public (decision E). I cannot see GitHub's branches.

### ATTACKER-3 (S3). Criterion 4's measurement misstates its own diff

- **Surface:** `docs/prepub/VERDICT.md:24`, hand-written.
- **Evidence:** `git diff --stat 36fed31..HEAD -- results data/processed` printed five files:
  - `data/processed/segments_reported.csv`
  - `results/exploratory/sensitivity.json`
  - `results/exploratory/sensitivity.md`
  - `results/live/2026Q4_latest.json`
  - `results/live/2026Q4_path.csv`

  The row says it "lists only files the audit added". The same five print at `4c922cd`, so the row predates the merge's effect or missed it. The criterion still holds: the two `2026Q4` files are the open quarter's working files, which the recompute did not cover.
- **Fix:** name the two workflow files and point to D20.

### ATTACKER-4 (S3). D20 explains two of the three files in the protected-path diff

- **Surface:** `docs/prepub/DECISIONS.md:89-90`, `docs/prepub/BASELINE.md:54`, `docs/prepub/VERDICT.md:31`, hand-written.
- **Evidence:** Q6 above. `data/snapshots/daily/2026-11-12.serials.csv.gz` is in the diff. It has no line in `RECORD_HASHES.txt`, and D20 and the BASELINE record row do not name it. Its blob equals `8c7692f`'s.
- **Fix:** add one sentence to D20: the diff also lists the 2026-11-12 daily table, added by `1481ce0` and equal to `origin/main`'s.

### ATTACKER-5 (S3). F016 says the home-folder name "equals" the GitHub handle; it does not

- **Surface:** `docs/prepub/FINDINGS.md:29`, hand-written.
- **Evidence:**
  - A script read every tracked file with a home-folder path (24 files) and printed per-file classes without values. 16 files under `docs/build/briefs/` and 2 recompute files hold the owner's account name.
  - The others hold only a placeholder of three dots where a name would go.
  - The equality test against the handle printed `False`.
  - The exposure F016 describes stands, since the two strings are closely related. The sentence as written is not true.
- **Fix:** "The folder name is close to the owner's public GitHub handle."

### ATTACKER-6 (S3). F068's open reason leaves out the workbook labels its surface names

- **Surface:** `docs/prepub/FINDINGS.md:81`; `output/gd_gulfstream_model.xlsx` (generated by `src/gdn/workbook.py`).
- **Evidence:** openpyxl found "nowcast" in `Live!A9`, `A10`, `A11` ("Nowcast large/mid/total") and `Segments!A14`, `A15`, `A16`, `A20`. F068's surface lists "workbook labels", while its status reads "open for the names only: the repository name and the release title".
- **Fix:** either rename the seven labels in `workbook.py` (and the ledger's labels), or add "workbook labels" to the open reason.

### ATTACKER-7 (S3). `GO_PUBLIC.md` step 2 contradicts D23 about the pushed branch

- **Surface:** `docs/prepub/GO_PUBLIC.md:47`, hand-written.
- **Evidence:**
  - Step 2 says `origin/prepub-audit` "sits at `f14a400`" and that a pull request from it "would leave out the last commits (the chart legends, the preview image and the final records)".
  - `DECISIONS.md:107` (D23) says `origin/prepub-audit` "now equals `4388294`", which comes after `daf25c1`, the commit with the legends and the preview image.
  - I cannot see GitHub's branch head (`gh api` is not allowed), but the two audit files disagree.
- **Fix:** tell the owner to run `git log --oneline origin/prepub-audit..prepub-audit` and push if it prints anything, and drop the named hash.

### ATTACKER-8 (S2). The late-lock guard behind F018 and E9 is skipped when the SEC record has no acceptance time, and no test covers that branch

- **Surface:** `src/gdn/live.py:468` (hand-written), `src/gdn/sec.py:101`, `tests/test_live.py:538`, and `docs/prepub/ERRATA.md` E9 item 2.
- **Evidence:**
  - `live.py:468` reads `if lock_p.exists() and f.get("accepted"):`, so the comparison runs only when an acceptance time is present.
  - `sec.py:101` sets `"accepted": pg.get("acceptanceDateTime", [""] * len(pg["form"]))[i] or ""`, so a missing field gives `""`. With `""` the quarter is scored with no timing check.
  - The test is parametrised on two non-empty times only (`("2026-10-30T12:09:27.000Z", True), ("2026-10-29T12:00:00.000Z", False)`).
  - E9 states the guard with no condition: "A quarter is not scored when its lock's release was published at or after the time the SEC accepted GD's 8-K."
  - Scoring writes `results/live/<q>_score.json`, which feeds every surface. That makes this "a code path with no test that feeds a public number" (`round4_common.md`, S2).
- **Why not S1:** for 2026Q3 the filing index printed an acceptance time, and `live.before_release` is a second, date-level guard on the lock side. Whether EDGAR ever omits the field is unproven (Suspicions).
- **Fix:**
  - Refuse to score when a lock exists and `accepted` is empty: log it and return 1, as the late case does.
  - Add `("", False)` to the test's parameters.
  - Run the R6 revert pair.
  - Or, if the owner keeps the guard as it is, add "when the SEC record gives an acceptance time" to E9.

## Improvements that would raise the project's standing

1. **Show the locked quarter on the image recruiters see first.** The README's first image and the LinkedIn preview (`site/preview.png`) stop at 2026Q2 (`charts.py` `QS = qrange("2016Q1", "2026Q2")`). Marking the 2026Q3 lock (32.0, its band) and GD's 40 on that chart, labelled as the live lock, would put the one out-of-sample result in the picture.
2. **Settle the post's position line in GO_PUBLIC step 1.** When the position sentence is dated, decide whether the post carries it. The post is 1,281 characters against `POST_MAX = 1300` (`report.py:515`), so only a short form fits without cutting elsewhere.
3. **Record the study's `as_of` beside its figures in F043.** Today the only record of the 2026-10-13 date is the constant that the ledger traces to.
4. **Cache the 2026-10-30 transcript (F107).** Its wording, speaker and date checked out on the Fool page today; caching it would make the row checkable offline like every other.
5. **Give the repository description the result.** It reads "tested on 26 held-out GD quarters, each live estimate locked" with no result. A clause such as "first lock missed by 8" would match the post's honesty.

## Checked and clean

- The post's figures: 32.0, 40, 8.0, 6.2, 39, 5.5, 6.9, 4.6, the 80% band and "outside". Each was recomputed or read from `results/live/2026Q3_score.json` and the 8-K.
- The README's first screen and Results: the live summary, the headline, the 7.4 on 22 sourced quarters (`guidance 22 7.3568`), and 18 of 26 (69.2%) from `results/metrics.json`. "The guidance pace was closer in each of the last five quarters" holds: 2025Q3 to 2026Q2 guidance closer, 2025Q2 not.
- The README sentence "every daily commit since 2026-10-31 has come from the workflow": 26 such commits, all `github-actions[bot]`.
- The lock-timing sentence is computed in `report.py:285-313`, so it will not go stale.
- README line 15 sits outside the generated sections, so GO_PUBLIC step 1's hand edit survives rebuilds. The note's position sentence comes from `~/.gdn_disclosure` or the previous note (`note.py:69-78`).
- `site/preview.png` equals `output/charts/track_record.png`, and `daily.REBUILD_PATHS` includes it.
- The quarter-plans quote for 2023Q3 matched the Fool page word for word.
- `segments_reported.csv` against Exhibit C of the 8-K, all eight figures. GD's Q3 delivery table (35, 5, 40; 39 a year earlier) against `results/live/2026Q3_score.json` and the README.
- The workbook between `4ca7d35` and `HEAD`: one cell format changed, nothing else.

## Suspicions, not proven

- **The S1 route behind ATTACKER-8.** A late lock would be scored only if EDGAR's submissions record for a results 8-K came without `acceptanceDateTime`. I have not seen that happen. To settle: check whether EDGAR guarantees the field, or fix the code so the question does not matter.
- **The study's as-of date (2026-10-13) has no record in the audit but the constant itself.** F043's evidence lists the study's companies and figures and not its `as_of`. `git grep 2026-10-13 -- docs/prepub` finds only the ledger row traced to the constant. To settle: read `as_of` from the study's `data.json`.

## Could not check, and refused commands

- `make`, `pytest`, the gate, `tools/prepub/ledger.py`, the nine plants and the revert harness: not allowed to me. That covers criteria 3 (plants), 6 (after the steps) and 7.
- ACFTREF engine-type code 2 on `3980222`: stored subsets are scoped, so they leave the row out. `registry.faa.gov` returned 403.
- The study's `data.json`: its URLs carry the owner's handle or name, and the hard limits forbid putting either into a request.
- GitHub's head for `origin/prepub-audit`: needs `gh api`.
- GD's first-reported 2016 counts (27, 34, 27, 27) against the 2016 releases: not fetched, for time.
- The dashboard as a browser renders it: I read `site/index.html` and `site/app.js`.
- WebFetch answers come through a summarising model. I asked for verbatim text in narrow pieces and compared them with the rows myself.
- No command was refused.
- The `git grep -c` sweep for home-folder paths over `HEAD` matched, by count only, two `round4_*` briefs other than mine (placeholders). I read nothing else in them.
- Imports of `gdn` ran with `-B` and `sys.dont_write_bytecode`, and the clone's `git status --short` stayed empty.
