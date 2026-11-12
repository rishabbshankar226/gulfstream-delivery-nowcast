# Findings

One row per finding. Severity per §2 of the spec. Status is `fixed`, `erratum`, `open: <reason>` or `refuted: <reason>`.

- Sources: `L<n>` is a lead from the spec's §0; `ledger` is a flagged row of the first `LEDGER.csv`; an ID such as `BUYSIDE-3` points into `docs/prepub/reviews/`. Section 2 maps every reviewer finding to a row here.
- "Old tree" line numbers are the lines the reviewers read at `9a5cb5a`, before the fix pass.
- Test: the regression test for a code fix, with its result when the fix is reverted and when it is restored. All 20 pairs are in `REVERT_TESTS.md` (`tools/prepub/revert_check.py`): each reads FAIL reverted, PASS restored. Text written by hand has no code to revert; the ledger is its check (`LEDGER.csv`, 0 flagged rows).
- Commits are on `prepub-audit`. The fix pass was developed in a scratch clone and merged in `e778e23` (DECISIONS D5).

## 1. Findings

| ID | Surface, file:line | Sev | Evidence | Fix | Commit | Test (reverted / restored) | Status |
|---|---|---|---|---|---|---|---|
| F001 | `output/charts/*`, `src/gdn/daily.py` (`rebuild`) | S1 | L12. `make all` on the baseline changed one file, `output/charts/nowcast_path.png` (`BASELINE.md`, Before): the daily job never redrew charts, so the chart predated the score. | `daily.rebuild` runs the charts stage and writes `output/charts/inputs.sha256`; the path chart's source line names its own snapshots. | 5657b94, 58f7aba | `tests/test_daily.py::test_the_daily_rebuild_redraws_the_charts` FAIL / PASS | fixed |
| F002 | `README.md:5` image `output/charts/dashboard.png` | S1 | Ledger: 7 stale chart rows. The image read "2026Q3 PROVISIONAL 31.1", "Locks the evening of 2026-10-29" (BUYSIDE-1, COMPLIANCE-2, SELL-6). | The README's first image is now `output/charts/track_record.png`, which the daily job redraws (F001); `grep -n dashboard.png README.md` finds nothing. The screenshot was retaken from the scored dashboard (again after round 2); its figures are listed by hand in `tools/prepub/chart_numbers.csv` and traced. | 58f7aba, 4ea45a0, a354170 | none: an image, checked by the ledger's chart rows | fixed |
| F003 | `tests/` | S2 | `make test` on the baseline: `6 failed, 114 passed`. The six tests asserted the pre-score state. | Tests rewritten for the scored state. The suite now prints `176 passed`. | d0247f7, ba8453f | the six tests themselves: failed at baseline, pass now | fixed |
| F004 | `report/claims.json`, `src/gdn/note.py` (`rel_cite`) | S2 | Gate baseline: `FAIL N4`, the note's unused claim `os-release-date`. | The release-date claim is cited only while the release is ahead and pruned after the score. `N4` passes. | d0247f7 | `tests/test_prepub_text.py::test_the_release_date_claim_is_cited_only_while_the_release_is_ahead` FAIL / PASS | fixed |
| F005 | `config/calendar.json` `public`, `src/gdn/report.py`, `site/app.js` | S1 | P0.4: every reader of the `public` key called the lock a "public GitHub release" once the key was true. The 2026Q3 lock was made while the repository was private (COMPLIANCE-6). | A `public_since` date sits beside the key. A lock is called public only if it was published on or after that date. | 4ea45a0, ba8453f | `tests/test_after_score.py::test_a_lock_is_called_public_only_if_the_repository_was_public_that_day` FAIL / PASS | fixed |
| F006 | `docs/INTERVIEW_NOTES.md:9`, `:27` (old tree) | S1 | L1. "The first lock is scored when GD reports", "My build estimate is 31.1 ... band of 20.4 to 36.4". Ledger: 5 stale, 9 untraced rows. | Rewritten by hand to the scored record, with the answer to "Why publish a model that lost to the same quarter last year?" (P6.2). | 462ad30, 7c2a99f | none: hand-written, ledger rows traced | fixed |
| F007 | `docs/RESUME_BULLETS.md:1`, `:2` (old tree) | S1 | L2. "is scored on 2026-10-30". Bullet 1 gave 5.5 against 6.9 and left out 4.6 (v1 N11, BUYSIDE-15, COMPLIANCE-15). | Both bullets rewritten: the 4.6, the lock, the miss, the band. | 462ad30 | none: hand-written, ledger rows traced | fixed |
| F008 | `output/GD_research_note.pdf`, `site/GD_research_note.pdf` | S1 | L13. The PDF's input stamp did not equal `sha256(report/note.html)`; the PDF said "newest dated 2026-10-30" where the HTML said 2026-11-11. | The note no longer prints the daily snapshot date, so it changes only when its content does. PDF rebuilt after every change to the note; the stamp equals the hash (`BASELINE.md`, After). CI cannot build the PDF: `ERRATA.md` E3 and a `GO_PUBLIC.md` step. | d0247f7, 37a72ea | none: a build output, checked by the stamp | fixed |
| F009 | `site/app.js`, `site/index.html` (live card, lead) | S1 | Ledger: dashboard stale row, the past release date labelled "GD reports". The card read "32.0 deliveries, estimated" with no result (BUYSIDE-4, BUYSIDE-24, SELL-23). | A scored quarter reads in the past tense with its miss, its band and its comparators. | ba8453f | `tests/test_site_a11y.py::test_a_scored_lock_states_its_miss_and_its_band_in_the_past_tense` FAIL / PASS | fixed |
| F010 | `docs/build/` | S2 | Ledger: build-notes row. 28 dated build logs with no notice that their figures are as of their date (D7). | `docs/build/README.md` says what the folder is, and names the two entries known to be out of date. | 0ef3306, 7aaa5c1, 7c2a99f | none | fixed |
| F011 | `README.md:107`, `:156` (old tree) | S1 | L14. "Each day my Mac downloads the registry ... locks the estimate". `git log`: the snapshot, lock and lock-record commits of 2026-10-29 are by `github-actions[bot]`, as is every daily commit since 2026-10-31 (BUYSIDE-20, COMPLIANCE-9, REGISTRY-2). | README says the workflow runs the job and made the lock, and that the Mac is the second path. The bot-blocking sentence says what the job sends. | 4ea45a0, 7aaa5c1 | none: hand-written, ledger patterns | fixed |
| F012 | `README.md:13`, post, note callout | S2 | The headline's "registry count" is the scaled estimate (5.5); the table's "Raw registry count" is another row (6.2) (BUYSIDE-9, STAT-9). | A sentence after the headline says which row it is, on the README and in the note. | 4ea45a0, 1c5a76c | `tests/test_prepub_text.py::test_the_readme_headline_names_the_baseline_that_won_and_explains_its_terms` FAIL / PASS | fixed |
| F013 | note Exhibit 8 and key points, dashboard revenue panel, workbook | S1 | The note, dashboard and workbook showed 2026Q3 revenue estimates with no actual after GD reported. GD's release (0000040533-26-000036): Aerospace 3,536, Marine 4,960, Combat 2,386, Technologies 3,684 ($M). The delivery-based Aerospace estimate missed by 826 (23.4%) (BUYSIDE-3, COMPLIANCE-5, SELL-3, sources_claims SC-1). | `data/processed/segments_reported.csv` keeps what GD reported for each scored quarter. Note, dashboard and workbook print it beside each estimate with the miss. The preview section is dropped once scored. | 08a6a2c, d0247f7, ba8453f, 522a422 | `tests/test_live.py::test_what_gd_reported_by_segment_is_kept_for_a_scored_quarter` and `tests/test_prepub_text.py::test_the_note_sets_gd_reported_revenue_beside_each_estimate`, each FAIL / PASS | fixed |
| F014 | `src/gdn/daily.py` (`merge_manifests`) | S2 | P5.1: the codex commit refused two manifest entries for one date that differ only in `downloaded_utc`, which two machines downloading the same zip produce. | The merge compares content, not download time. | a2e1a01 | `tests/test_daily.py::test_a_manifest_merge_accepts_the_same_zip_downloaded_at_two_times` FAIL / PASS | fixed |
| F015 | git history: commit metadata | S1 | P3.5 (`EXPOSURE.md`): the owner's personal email address is the author address on 124 commits of `main`. A public repository shows it (COMPLIANCE-25). | None possible here: history is not rewritten (R3), and a rewrite would change the lock commit's hash. | none | none | open: the owner decides (`GO_PUBLIC.md`, decision A) |
| F016 | `docs/build/briefs/*` and history | S1 | P3.5: home-folder paths in 16 tracked files under `docs/build/briefs/` and in history (COMPLIANCE-24). The folder name equals the owner's public GitHub handle. | The audit's own files use `~` (63a1cc7), except the recompute output, kept byte for byte. The build logs are kept as written; history cannot change. | none | none | open: the owner decides (`GO_PUBLIC.md`, decision B) |
| F017 | `src/gdn/live.py` (`run_lock`) | S1 | P5.2 (`DEFECT_TRACE.md`): a lock could be made from the newest stored subset even when that subset predated the quarter's end (REGISTRY-7, second point). | No lock from a subset dated on or before the window's end. | f33819f | `tests/test_live.py::test_no_lock_from_a_subset_that_predates_the_quarter_end` FAIL / PASS | fixed |
| F018 | `src/gdn/live.py` (`score_quarter`) | S1 | P5.2: nothing stopped a score against a lock whose release was published after GD's filing was accepted. | The score compares the release's `published_at` with the filing's acceptance time and refuses a late lock. | f33819f | `tests/test_live.py::test_a_lock_published_after_the_filing_is_not_scored` FAIL / PASS | fixed |
| F019 | not used | | Number skipped. | | | | refuted: no finding carries this number |
| F020 | `src/gdn/report.py` (post) | S2 | The post's generator wrote "one quarter" wording that would be wrong at the second lock. | The post counts its locked quarters. | 4ea45a0 | `tests/test_after_score.py::test_the_post_counts_its_locked_quarters` FAIL / PASS | fixed |
| F021 | `README.md:105` (old tree), interview notes | S1 | "before I computed anything for a later quarter". `git log`: counts for every quarter committed 10:48:35 (`6725184`); definition chosen and preregistration committed 11:02:12 (`5c84d36`, `2c62ad3`); held-out scores 11:04:28 (`48c1ea0`), all 2026-10-19 (BUYSIDE-6, BUYSIDE-13, COMPLIANCE-4). | "The test" paragraph gives the commit order and says it is all that backs "held out" and "preregistered". | 4ea45a0 | none: hand-written | fixed |
| F022 | `README.md` Results, `data/guidance.csv` 2021 rows | S1 | A method choice that moves a headline figure: GD's 2021-01-27 statement "10 fewer aircraft" (than 2020's 127) is read as no outlook. Read as 117, the guidance pace's average miss is 6.66, not 6.92, and the estimate is closer in 13 of 26 (sources_guidance SRC-G-1, SELL-2). | `results/exploratory/sensitivity.md` scores the reading; the README states it beside the headline. The preregistered 6.9 stands. The 2021 sentence now says the rule reads no figure, not that GD gave none. | 913c83f, 4ea45a0, 7c2a99f | `tests/test_prepub_text.py::test_the_2021_reading_is_disclosed_with_its_effect_on_the_headline` FAIL / PASS | fixed |
| F023 | README Results, note | S2 | The estimate's lower average miss than the guidance pace comes from 2023 and 2024: 3.48 against 12.51 there, 6.43 against 4.43 on the other 18 quarters (BUYSIDE-11, STAT-5, SELL-10). | A generated sentence says so, and that the guidance pace was closer in each of the last five quarters, the locked one included. | 913c83f, 4ea45a0, 7aaa5c1 | `tests/test_prepub_text.py::test_the_split_sentence_names_the_years_that_carry_the_lead` FAIL / PASS | fixed |
| F024 | `README.md:13` first screen | S2 | L4. The README's bold headline did not say in words that the same quarter last year missed by less (4.6 against 5.5) (BUYSIDE-8, BUYSIDE-18, STAT-6, SELL-14). | The headline carries the sentence, and a live summary sits above it. | 4ea45a0 | same test as F012, FAIL / PASS | fixed |
| F025 | post, README Live record, dashboard, note | S2 | The live miss stood alone. `results/live/2026Q3_score.json`: miss 8.05; guidance pace 33.84, miss 6.16; same quarter last year 39 against 40 (BUYSIDE-7, BUYSIDE-16, STAT-7, SELL-13, v1 A2). | Each surface sets the lock beside the guidance pace, last year's quarter, last quarter and the raw count, and says "outside the band". | 4ea45a0, d0247f7, ba8453f | `tests/test_after_score.py::test_the_live_record_sets_the_lock_beside_the_other_misses` FAIL / PASS | fixed |
| F026 | post, README Live record, interview notes | S2 | No surface said the lock was made by the workflow while the repository was private (`LOCK_CHECK.md`: release and commit author `github-actions[bot]`) (BUYSIDE-12, COMPLIANCE-8). | Post, README, note and interview notes say so. | 4ea45a0, 462ad30 | none: hand-written, ledger state `Q3_bot_private` | fixed |
| F027 | README Method, interview notes | S2 | "Preregistered" with no qualifier: the rules were committed two minutes before the scores, from data already in the repository (BUYSIDE-13, COMPLIANCE-11). | Qualified wherever it is claimed (see F021). | 4ea45a0 | none | fixed |
| F028 | README | S2 | The build notes show an AI coding agent built the project; no public surface said so (BUYSIDE-14, COMPLIANCE-10). 42 commits carry a `Co-Authored-By: Claude` trailer. | README section "How this was built". | 4ea45a0 | none | fixed |
| F029 | post, README, note, dashboard, interview notes | S2 | "GD's guidance pace" read as a figure GD gives (BUYSIDE-10, BUYSIDE-22, COMPLIANCE-16). | Every surface says it is my construction from GD's full-year outlook. | 4ea45a0, 7aaa5c1, 1c5a76c | same test as F012, FAIL / PASS | fixed |
| F030 | README, post, workbook, note pages, dashboard | S2 | No "not investment advice" or affiliation line on the README, post or workbook; the note's disclaimer on page 1 only (BUYSIDE-19, COMPLIANCE-7, COMPLIANCE-12, COMPLIANCE-14). | One disclaimer line on each surface; the note's page footer prints it on every page (8 of 8). The no-position sentence is the owner's to confirm and date: see F081. | 4ea45a0, 522a422, d0247f7, ba8453f, 7aaa5c1 | `tests/test_prepub_text.py::test_the_note_footer_carries_the_disclaimer_on_every_printed_page` FAIL / PASS | fixed |
| F031 | `output/gd_gulfstream_model.xlsx` | S2 | The workbook had no guidance baseline and ended at the estimate (BUYSIDE-17, v1 O1). | Guidance columns, a Summary row and the scored live rows, all formulas. | 522a422 | `tests/test_outputs.py::test_the_workbook_carries_the_guidance_baseline_and_the_live_result` FAIL / PASS | fixed |
| F032 | `README.md:69`, `:142` (old tree) | S2 | L5. Deliveries per registry event (1.18) and registry events per delivery (0.52 to 0.80) in one document (BUYSIDE-23, STAT-4). | One unit throughout: deliveries per registry event. | 4ea45a0 | none: the ledger's unit rule (plant 5) | fixed |
| F033 | post line 3 (old tree), README Used jet, note | S1 | L6. The post said it counted "each Gulfstream jet's first customer registration or export". `data/processed/serials.csv`: 246 of the 1,251 counted events (19.7%) sit on airframes at least three years old, 76 more carry no year; 5 of the 42 in the locked quarter (REGISTRY-1, REGISTRY-3, SELL-8). | The post no longer says "first customer". README and note give the share. | 4ea45a0, 7c2a99f | none: generated from `serials.csv`, ledger rows traced | fixed |
| F034 | README Error analysis, dashboard | S2 | The truncation table (30-day row 13.5) read as a stand-in for a live lock; the live miss at 25 days was 8.05. "Flatters" and "too narrow" pointed one way (STAT-2, STAT-3). | A generated paragraph gives the lock's own facts: 25 days after the quarter's end, a count of 42 that has not changed since, a scale of 0.76 against a realised 0.95. | 4ea45a0, 7aaa5c1 | `tests/test_prepub_text.py::test_the_lock_timing_sentence_reads_the_lock_and_the_later_snapshots` FAIL / PASS | fixed |
| F035 | `report/note.html:55` (old tree) | S2 | "which do not fall with deliveries, so the delivery-based figure overstates the swing": a cause with no citation (sources_claims cause-6). | Clause removed. `grep -c` on the note: 0. | d0247f7 | none | fixed |
| F036 | note: outlook section, byline, G400 sentence | S1 | sources_claims: 18 stale rows, 1 mismatch. The note previewed a print that had happened and carried "Data as of 2026-10-29" over a 2026-10-30 figure. | The byline says what the page is; the outlook is headed "before the release" and dated to the 2026-07-29 call; "What the street watches" is dropped once scored. | d0247f7, 37a72ea | covered by the F013 note test | fixed |
| F037 | `.github/workflows/pages.yml` | S2 | Pages deploys on a push to `site/**` or a manual run. The daily job pushes with `GITHUB_TOKEN`, which starts no workflow, so the dashboard would go stale after publication (COMPLIANCE-20). | None in the tree: `.github/` is outside this run. | none | none | erratum: `ERRATA.md` E1, `GO_PUBLIC.md` steps |
| F038 | post links, README links | S1 | L3. `LINKS.csv`: 12 of 191 links point at the owner's repository or Pages site and return 404 while it is private (BUYSIDE-5, COMPLIANCE-3, SELL-7). | None in the tree: the URLs are right. | none | none | refuted: not a defect of the tree. The links resolve after `GO_PUBLIC.md` steps 4 and 5, each with its check (criterion 6) |
| F039 | `config/calendar.json` | S2 | L15. No 2026Q4 release date and no 2027Q1 fiscal end, so no lock can fire (REGISTRY-7). | README says a lock needs the date and that none is set. | 4ea45a0 | none | erratum: `ERRATA.md` E4, `GO_PUBLIC.md` step |
| F040 | L16: `results/live/2026Q4_latest.json` | S1 | Lead: the part-quarter figure 13.55 (band 2.8 to 20.4) might show as an estimate. `grep` on the post, README, note and interview notes: no 13.55 and no "2.8 to 20.4". | README names the working file and says it is not an estimate (STAT-16). | 7aaa5c1 | `tests/test_after_score.py::test_an_open_quarter_shows_no_partial_estimate` (in the suite before the audit) | refuted: no surface shows it as an estimate |
| F041 | L8: `site/data.json` path rows | S1 | Lead: 31.13 might show as the locked figure. `grep -c "31\\.1\\b"` on the post, README, note, interview notes and resume bullets: 0 each. The dashboard shows 31.1 only as a dated point on the path. | none needed | none | none | refuted: 31.1 appears only as a path point |
| F042 | L9: v1's open items A2, N11, O1, O3, O4, T9 | S3 | `docs/build/REVIEW.md` rows 50 to 82. | A2 comparator: F025. N11: F007. O1: F031. O4: overtaken by F013, which shows what GD reported. O3: F064. T9: F100. | see those rows | | fixed, except O3 (F064) |
| F043 | L10: `https://rshankar.dev`, the defense study's site, note study figures | S2 | `LINKS.csv`: both resolve. The study's `data.json` (fetched 2026-11-11): companies HII, LHX, LMT, NOC, RTX; next quarter 9.89, 7.31, 6.52; four quarters 9.40, 5.76, 6.04. The note prints 9.9, 7.3, 6.5 and 9.4, 5.8, 6.0. The 2018 XBRL sentence matches the study's README (SELL section 4). | none needed | none | none | refuted: links and figures verified |
| F044 | L11: `CLAUDE.md` | S3 | Untracked, stale pointers from v1. | Replaced with pointers to this spec; v1's kept at `.build/CLAUDE_v1.md` (P0.2). | untracked | none | fixed |
| F045 | README Method, note, interview notes | S2 | "within 365 days of the airworthiness date": `src/gdn/events.py` tests only `date <= bound`, so the rule is one-sided, and E1 uses the earliest customer certificate the registry still shows, not the first customer's (REGISTRY-3). | Wording changed on all three surfaces. | 4ea45a0, 9c0f7b8 | none: wording | fixed |
| F046 | README Used jet | S2 | Two airframes are counted twice or late under a second maker code: G150 serial 322 (2016Q2 and 2018Q2), G280 serial 2009 (2012 certificate, counted 2026Q2). A third G280 code appeared in October 2026 (REGISTRY-8). | Disclosed with the serials. The key is preregistered and stands. | 4ea45a0, 9c0f7b8 | none | fixed |
| F047 | README Used jet | S3 | The cabin rule files 11 airframes of older mid-cabin types as large; none has an event in the tested quarters (REGISTRY-9). | Disclosed. | 4ea45a0 | none | fixed |
| F048 | `src/gdn/model.py` comment | S3 | A comment said the P10 position at n = 30 is 4. `0.1 * 30` is exactly `3.0`, position 3 (STAT-10). | Comment corrected and pinned. The same error in a build note: `ERRATA.md` E8. | 0540e03, 7aaa5c1 | `tests/test_model.py::test_nearest_rank_positions_match_exact_arithmetic` (pins the behaviour; a comment has nothing to revert) | fixed |
| F049 | README Data | S3 | "delivered basis" and the `filed` column were not explained. | Data bullet says where 2016 comes from and why. | 4ea45a0 | none | fixed |
| F050 | README Method, sensitivity | S2 | The design window chose E1 on 5.47 against 5.58. The two definitions count the same in 11 of 12 design quarters and differ by one airframe in 2019Q4; under E2 the held-out miss is 5.47 against 5.52 (STAT-8). Also: the autocorrelation sentence gave no size (STAT-12), and "Average % miss" had no definition (STAT-14). | Generated sentences for each. | 913c83f, 7aaa5c1 | `tests/test_prepub_text.py::test_the_design_choice_sentence_counts_the_quarters_where_the_definitions_differ` FAIL / PASS | fixed |
| F051 | README Error analysis | S2 | The preregistered drift flag looks only above the mean; the drift ran below it (0.69, 0.69, 0.72 against 1.18) (STAT-4). | The paragraph says the flag is one-sided and which way the drift ran. | 7aaa5c1 | none: generated, ledger rows | fixed |
| F052 | README Coverage, as-of paragraph | S3 | "lost first-owner records": of the records lost between two snapshots some were later owners' (REGISTRY-13); "would drop every mid-cabin delivery" overstates by one (REGISTRY-14); the export comfort rests partly on used jets (REGISTRY-18). | Three wording changes. | 9c0f7b8 | none | fixed |
| F053 | `site/index.html` head | S3 | No link-preview tags (COMPLIANCE-23). | `og:title`, `og:description`, `og:url` added. | 7aaa5c1 | none | open: `og:image` needs an image under `site/` that the job keeps current; left for the owner |
| F054 | `data/guidance.csv` | S3 | The 2026-10-30 call was not in the file (sources_guidance SRC-G-4). The Fool transcript reads "We do not plan to update segment guidance.", spoken by the CEO (read twice from the page, once by the main thread and once by a fetch agent). No full-year delivery number was found on the call. | Row added with a blank outlook. `make all` changed no file under `results/` but the exploratory note. | a354170 | none: data | fixed |
| F055 | `src/gdn/events.py` (`gulfstream_held`), README | S2 | The holder rule matches names that start `GULFSTREAM AEROSPACE`. Four certificates to `GULFSTREAM LEASING LLC` count as deliveries: serials 72001 and 73002 (2020-11-13), 87001 and 88001 (2025-10-07) (REGISTRY-4, SELL-9). | Disclosed in README Limitations. The rule is preregistered. | 9c0f7b8 | none | erratum: `ERRATA.md` E6 |
| F056 | `src/gdn/faa.py` (`scope`), README, dashboard chart | S2 | The FAA files G700 type code `3980222` under engine-type code 2; the scope rule keeps 4 and 5. 17 MASTER rows in the FAA file of 2026-10-30, all registered to Gulfstream, none with a certificate date, none in DEREG (REGISTRY-6; rerun by the main thread). No past count is short; future deliveries of these jets would be missed. | Disclosed in README Limitations and under the dashboard's chart. The rule is preregistered and the stored subsets were filtered by it. | 9c0f7b8 | none | erratum: `ERRATA.md` E5, `GO_PUBLIC.md` decision C |
| F057 | README Used jet | S2 | 386 of 4,053 airframes have no bound; they supply 75 of the 1,251 counted events (REGISTRY-5; rerun by the main thread). | Disclosed with the counts. | 9c0f7b8 | none: ledger rows | fixed |
| F058 | README Results, `data/quarter_plans.csv`, `src/gdn/sensitivity.py` | S1 | A method choice that moves a headline figure: on six calls held inside a held-out quarter GD stated that quarter's delivery plan (2023-07-26: "We now expect to deliver 27 aircraft in the third quarter"; the pace says 43.1; GD delivered 27). The preregistered pace reads only full-year outlooks. With the six plans in its place the baseline misses by 6.02, not 6.92, and the estimate is closer in 12 of 26 (SELL-1). Each quote checked in the cached transcripts. A search of every cached call for a quarter's delivery number found these six; three more calls (2021-04-28, 2025-10-24, 2026-04-29) describe the quarter in words with no number and are not scored. | The six plans are a tracked file; the sensitivity table scores them; the README and interview notes say so beside the headline. The preregistered 6.9 stands (D12). | 7c2a99f | `tests/test_prepub_text.py::test_gd_stated_quarter_plans_are_scored_beside_the_guidance_pace` FAIL / PASS | fixed |
| F059 | note product cycle, README Limitations | S2 | The note left out the G300 and the G280's last delivery, which GD stated on 2026-07-29 and in its 2025Q3 10-Q; the mid-cabin count rests on the G280 alone (SELL-11). | Two claims restored under new ids with the wording v1's fact check proposed; a Mid-cabin gap limitation. | 7c2a99f | `tests/test_claims.py::test_claims_the_fact_check_removed_stay_out` still passes (the removed ids stay out) | fixed |
| F060 | README Data | S2 | No surface said what GD's count includes (SELL-17). GD's 2025 10-K: "generally upon delivery and acceptance by the customer of the fully outfitted aircraft"; 2022-01-26 call: "a few demonstrators all up about 11 aircraft". | Data bullet states both, quoted. | 7c2a99f | none | fixed |
| F061 | note Exhibits 9 and 11, workbook, dashboard revenue panel, README | S2 | The mechanical label was missing under two exhibits and on the workbook's Sensitivity sheet; the dashboard and workbook used the defense rule without calling it an assumption; the README did not say the estimate ignores GD's manufacturing and services split (SELL-12, SELL-16). | Labels and sentences added on each surface. | 7c2a99f, and 048dbb3 for the README sentence | none: wording | fixed |
| F062 | `.github/workflows/nowcast.yml`, lock timing | S2 | By committer time the 00:17 UTC run's commits landed between 04:44 and 07:21 UTC and the 12:17 UTC run's between 15:58 and 18:42 UTC (`git log`, 45 bot commits). A late run can miss a lock; `live.before_release` refuses a late one (REGISTRY-7). | None in the tree. | none | none | erratum: `ERRATA.md` E2, `GO_PUBLIC.md` step |
| F063 | `src/gdn/faa.py:161-170`, `src/gdn/live.py:197-210`, `:395-397` | S3 | Four latent code points read by the registry reviewer: a comma fallback that would mis-cut a row (0 in-scope rows today), no sanity check on an ingested file, a table rewrite before the locked-date test, a late-stamped release warned about and still scored (REGISTRY-12, -15, -16, -17). None changes a figure today. F018 covers the scoring half of the last. | none | none | none | open: each touches the preregistered parse or the lock path and needs the owner's design choice; over 15 minutes each |
| F064 | note Risks | S3 | Seven of eight risks are general 10-K factors (v1 O3, SELL-18). | none | none | none | open: new Gulfstream-specific risks need new sourced claims; editorial, over 15 minutes |
| F065 | note Risks, `risk-tariffs` | S3 | The 2025 10-K tariff sentence is overtaken by GD's 2026Q2 10-Q: "tariffs as applied in their current form and tariffs yet to be refunded are not material" (SELL-24, sources_claims). | A second claim cites the later filing. | 37a72ea | claims build keeps only claims whose quote is in the cached source | fixed |
| F066 | note Exhibit 10 | S2 | Backlog shown as of 2026Q2 after GD's 2026Q3 release reported Marine Systems total backlog of 146,865 ($M) against 65,182 (sources_claims, SELL-12). | The exhibit says it is as of 2026Q2 and gives the 2026Q3 figure with its accession. | 37a72ea | none: ledger row | fixed |
| F067 | workbook `About!A2`, `docs/INTERVIEW_NOTES.md:5` | S3 | "can they estimate the count before GD reports it?" (R9); "that count drives the Aerospace segment" (a cause, uncited) (SELL-22, SELL-25). | Both reworded. | 37a72ea | none | fixed |
| F068 | repository name, release title, workbook labels, chart legends | S3 | "nowcast" survives in names (BUYSIDE-25). The legends of `track_record.png` and `nowcast_path.png` say "GD guidance pace" with no word that it is my construction (FINANCE-4, the part regraded from S2). | none | none | none | open: the repository name and the release title are outward and part of the record |
| F069 | README (old tree) | S2 | "An independent gate outside this repository" cannot be checked by a reader (COMPLIANCE-17). | Sentence removed; `grep -n "gate" README.md` finds none. | 4ea45a0 | none | fixed |
| F070 | README Data, `data/snapshots/` | S2 | The stored FAA subsets carry registrants' names and street addresses; the README did not say so (COMPLIANCE-18). | Data bullet says so. Whether to publish them is the owner's (`GO_PUBLIC.md`, decision D). | 4ea45a0 | none | fixed |
| F071 | `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md`, `docs/prepub/` | S2 | Owner material and this audit's folder become public with the merge (COMPLIANCE-19, COMPLIANCE-31). | README says both folders are there. | 4ea45a0 | none | refuted: §3 lists the owner material as part of the public surface and D8 expects `docs/prepub/` to be public; the choice is put to the owner (`GO_PUBLIC.md`, decision E) |
| F072 | post (old tree) | S3 | Opener assumed context; `#GeneralDynamics` beside `#EquityResearch` (COMPLIANCE-21, -22). | P7.1 rewrite: the first line carries the result, GD is spelled out, hashtags are `#EquityResearch #Aerospace`. | 4ea45a0 | post length and content tests in `tests/test_after_score.py` | fixed |
| F073 | README footer and line 7 (old tree), `LICENSE` | S3 | "once the repository is public"; plain MIT with no word on data (COMPLIANCE-26, -27). | Sentence dropped; "License and data" section. | 4ea45a0 | none | fixed |
| F074 | README Results | S3 | The test counts wins while the headline talks about the average; no interval on the difference in averages (STAT-11). "Nominal 80%" is more than nearest rank delivers on 12 to 37 past errors (STAT-13). The as-of sentence would be tighter with margins (STAT-15). | none | none | none | open: each adds a statistic the preregistration does not define; left as stated limits |
| F075 | `data/snapshots/2026-10-19/*.gz` | S3 | Byte 9 of the stored gzip header differs from what the current writer produces; decompressed bytes identical (REGISTRY-10, not re-measured). | none: a stored snapshot | none | none | erratum: `ERRATA.md` E7 |
| F076 | note claim `pc-g700-first-deliveries` | S3 | "began G700 deliveries ... after FAA and EASA certification" copies the 10-K; EASA certification came after first deliveries (SELL-19, from web search). | The clause is cut: "Gulfstream began G700 deliveries in the second quarter of 2024." (R3-7). | 4ad3825 | claims build | fixed |
| F077 | README Data | S3 | The sha256 on each claim is of the bytes as fetched; a later download of an SEC page can differ (SELL-21: the reviewer's byte diff found a script tag that changes). | README Data says the hash is of the bytes as fetched and a later download may not match. | a354170 | none | fixed |
| F078 | dashes outside the main surfaces | S3 | 12 lines in `docs/build/` and `docs/PREREGISTRATION.md` hold an en or em dash, names and quotes among them (COMPLIANCE-30). | none | none | none | refuted: build notes are kept as written and the preregistration never changes (R7) |
| F079 | `site/app.js`, note | S3 | The quarter window was shown with its start date included; the rule is `start < date <= end` (REGISTRY-11). | "after ..., through ..." in the note; the dashboard shows the day after the start. | d0247f7, ba8453f | none | fixed |
| F080 | note sources | S2 | "GD reported 40" had no source in the note (SELL-15). | The note's sources list carries the EDGAR folder of every results 8-K, the 2026Q3 release among them (`grep -c 000004053326000036 report/note.html`: 1; the list prints folder URLs, which have no dashes). Exhibit 10 also names the accession. | d0247f7, 37a72ea | none | fixed |
| F081 | note page 1 and footer, `README.md:15` | S2 | "The author holds no position in General Dynamics" is undated and carried forward by the build (BUYSIDE-27, COMPLIANCE-12). The README's "I hold no position" is the same statement. Only the owner can make it. | none possible here | none | none | open: the owner confirms and dates it (`GO_PUBLIC.md` step 1); P4.7 asks for exactly this |
| F082 | README Data | S2 | P4.7, restatements. `reviews/sources_deliveries.csv`: GD restated only 2016 (first reported totals 27, 34, 27, 27; restated 28, 36, 29, 28) and nothing from 2017Q1 on. `data/processed/gd_deliveries.csv`: each restated 2016 count comes from the same quarter's 2017 release (filed 2017-04-26 to 2018-01-24), so the design window's 2017 estimates use 2016 counts not public in that form at the time. No held-out quarter uses a 2016 count. | README Data bullet says so. | 048dbb3 | none: hand-written | fixed |
| F083 | `docs/INTERVIEW_NOTES.md:30` (round 2 copy) | S1 | "So the registry had the quarter's jets in time: the count had settled at 42 by the lock." The lock's own airframe table has 5 of the 42 events on airframes at least three years old by the year field, so the registry did not show 40 new jets, and R9 forbids the claim. The sentence was written by this audit's fix pass (EDITOR-1, FINANCE-1, R2-STAT-9). | Replaced with the count, the five older airframes and the two ratios. The README's lock paragraph now gives the two ratios and no cause (EDITOR-8, R2-STAT-12, R2-STAT-20). | a354170 | `tests/test_prepub_text.py::test_the_lock_timing_sentence_reads_the_lock_and_the_later_snapshots` (F034's pair) | fixed |
| F084 | post, `README.md:153`, note (two places) | S1 | "a registry copy that had years to fill in": the 2026-10-19 copy had 106 days for 2026Q2 and 292 for 2025Q4 (R2-STAT-3, EDITOR-5). Other sentences already said "months or years". | "months or years" in all four places. | a354170 | `tests/test_after_score.py::test_the_post_is_short_and_carries_its_disclaimer` asserts the wording | fixed |
| F085 | `docs/INTERVIEW_NOTES.md:33` | S1 | "Every number in it traces to a filing or a registry file": the outlooks come from call transcripts and the defense percentages from another study (FINANCE-17, EDITOR-9). | Sentence names each kind of source. The note says where the study's percentages come from (FINANCE-9). | a354170 | none: hand-written | fixed |
| F086 | post, README, note, dashboard, interview notes | S2 | "8.0 (20.1%)" beside 32.0 and 40: 8.0 over 40 is 20.0%; 20.1% comes from the unrounded 31.953 (EDITOR-3, FINANCE-5, R2-STAT-1). | The percentage is printed as 20% wherever it appears; the post drops it. | a354170 | `tests/test_site_a11y.py::test_a_scored_lock_states_its_miss_and_its_band_in_the_past_tense` asserts "(20%)" | fixed |
| F087 | post | S2 | The post used "the registry count" and "GD's guidance pace" with no word on what they are (EDITOR-4, FINANCE-6, R2-STAT-2; the advisor's check of F012 and F029). The sentence is preregistered word for word, so it stays. | A clause after it: "(Registry count: my scaled estimate; the pace: mine.)". The dashboard's own wording is `ERRATA.md` E10. | a354170 | ledger pattern on the post | fixed |
| F088 | `README.md:81`, note, `site/app.js:394` | S2 | "the last three quarters sit at 0.69, 0.69, 0.72" after 2026Q3 came in at 0.95 (EDITOR-2). | "the last three held-out quarters" on all three. | a354170 | none: wording, ledger templates | fixed |
| F089 | README first screen, post | S2 | The band was used without its level or its backtest coverage (R2-STAT-10). | README live summary: nominal 80%, held 18 of 26. Post: "my 80% band". | a354170 | none: generated, ledger rows | fixed |
| F090 | `README.md:8`, interview notes | S2 | "No test finds the registry estimate better than a baseline" covers tests that were not run (R2-STAT-4). | "None of the three preregistered sign tests". | a354170 | none | fixed |
| F091 | README Results and Method | S2 | The text gave the two readings of GD's calls separately and not together (5.70 against 5.52, closer in 11 of 26), and said nothing tried had changed the headline (R2-STAT-5). The rules for reading calls quote two transcripts and the 22-quarter threshold is met exactly (R2-STAT-6). A build check on coverage failed for mid cabin in 2016 and 2017 and was waived; the notes called it preregistered (R2-STAT-8). | Each is now stated: the combined row in Results, the two facts in "The test", the failed check in the Coverage limitation and the interview notes. | a354170 | none: wording, ledger rows | fixed |
| F092 | interview notes | S2 | "I fixed the rules ... before scoring" stated more strongly than the README (FINANCE-11, R2-STAT-7). | "minutes before and in the same session, so only the locked quarters are out of sample in the strict sense". | a354170 | none | fixed |
| F093 | README Live record, interview notes | S2 | "The raw registry count (42) missed by 2" with no word on what the 42 were (FINANCE-2); "GD's guidance pace missed by 6.2" reads as GD's guidance being off when an even split of the 81 jets left would have said 40.5 (FINANCE-3). | Live record says 5 of the 42 were older airframes, and gives the even split beside the pace. | a354170 | none: generated, ledger rows | fixed |
| F094 | dashboard, workbook, note | S2 | The dashboard and workbook never said the pace is my construction; the note and dashboard left out the two readings (FINANCE-4, EDITOR-21). | Dashboard method step and test list, workbook About, note footnote. | a354170 | none | fixed. The chart legends keep the label "GD guidance pace", regraded S3 and left open under F068: the README's first paragraph, on the same screen as its first chart, calls it "a pace built from GD's own guidance", and Results says it is my construction |
| F095 | note Exhibits 9 to 11, workbook Sensitivity, dashboard sensitivity table | S2 | 2026Q3 estimates with no reported figure and no "before the release" mark (FINANCE-8); the callout "I wrote this note before GD reported" was not true of the whole note (EDITOR-6); a scored quarter was headed "The live quarter" (EDITOR-7). | Captions say "made before the release"; the callout says which parts were updated; headings say "locked quarter". | a354170 | `tests/test_prepub_text.py::test_the_note_sets_gd_reported_revenue_beside_each_estimate` asserts the callout | fixed |
| F096 | workbook About and Summary | S2 | The workbook described the date bound as two-sided (EDITOR-10) and its Summary sheet had neither plain result (FINANCE-7). | About says "no later than 365 days after"; Summary row 9 tells the reader how to read rows 2 to 6 and points to the Live sheet. | a354170 | none | fixed |
| F097 | `docs/prepub/ERRATA.md` | S3 | Not in first person; session words a reader cannot follow (EDITOR-17). Three guards in the lock and score code go beyond the preregistered text (advisor's check of F017, F018 and the codex commit against section 3.6). | Rewritten in first person; E9 dates the three guards and the README's Live paragraph names them. | a354170 | the guards' own tests (F017, F018) | fixed |
| F098 | round 2 minor points | S3 | Not fixed: more than one name for some things (EDITOR-16); dashboard small points (EDITOR-18, FINANCE-13 in part); Exhibit 11 leaves out the workbook's guidance row (EDITOR-19); style points in the post and owner material (EDITOR-20); unsized military and export gaps (FINANCE-12); workbook and small wording (FINANCE-15, FINANCE-16); "nominal 80%" is about 76% as built, two kinds of average for deliveries per event, a test on wins not on the difference, missing sensitivity rows, and four more wording points (R2-STAT-11, -13 to -19). Fixed among the minor points: README "below" to "above" (EDITOR-12), "nearly every" (EDITOR-13), the screenshot (EDITOR-15, FINANCE-14), two already fixed before round 2 read its copy (EDITOR-11, EDITOR-14). | see Evidence | a354170, 37a72ea | none | open: wording and added statistics, each over 15 minutes or a matter of taste; FINANCE-10 is F064 |
| F099 | `README.md` Reproduce | S2 | P8.4: a fresh clone with this Mac's `python3` (3.9.6) failed at `pip install -r requirements.lock` (`No matching distribution found for contourpy==1.3.3`, `.build/logs/clone_check1.log`). The README gave `make all` and `make test` with no word on the environment. | Reproduce section gives the two setup commands and says the pinned requirements need Python 3.11 or later. A second fresh clone with Python 3.11 builds (`BASELINE.md`, Fresh clone). | 9061039 | none: the fresh clone is the test | fixed |
| F100 | `tests/` (v1's T9) | S3 | `truncated_mae`, `coverage_drift` and `holdout_metrics` had no direct test (v1 T9, P5.4). | `tests/test_model_direct.py`: six tests rebuild each figure from the data files. `daily.run` is covered by `tests/test_daily.py`. | 9061039 | new tests, not a fix to revert | fixed |
| F101 | `output/gd_gulfstream_model.xlsx` `Live!B18` | S2 | Round 3 (R3-1, attacking F086): the cell `=B17/B16` had format `0.0%`, so the workbook still showed 20.1% beside 32.0, 40 and 8.0. | Format `0%`. | 4ad3825 | none: a number format | fixed |
| F102 | `report/note.html:56`, `:78` | S2 | Round 3 (R3-2, attacking F093): the "5 of the 42" caveat reached the README and not the note. | Both places in the note carry it, from the same function as the README. By the registry's year field the five include one G700 whose year reads 2006; the sentence says "by the registry's year of manufacture" for that reason. | 4ad3825 | ledger rows on the note | fixed |
| F103 | `docs/INTERVIEW_NOTES.md:33` | S2 | Round 3 (R3-3, attacking F092): "I fixed the rules before I scored the held-out quarters" was qualified on line 7 and not on line 33. | Same qualifier on line 33. | 4ad3825 | none | fixed |
| F104 | post, alternates | S2 | Round 3 (R3-4): the post's label "Backtest, held out from setting the rules" carried no qualifier, while the README says the commit order is all that backs "held out". Graded S2 by the precedent of F027 and F092: the sentence is true of the commit order and misleading without it. | The label reads "Backtest (rules set minutes before scoring)"; both alternates say the same. Two wording tests follow. | 4ad3825 | `tests/test_wording.py::test_baseline_wording` and `tests/test_after_score.py::test_the_post_is_short_and_carries_its_disclaimer` assert the new label | fixed |
| F105 | note, `site/app.js:170`, interview notes | S3 | Round 3 (R3-5): "likely too narrow" survived on three surfaces where the README says "may not fit" (see F034). R3-6: "It reads" after a parenthesis in the post read as the pace. R3-7: the G700 sentence's "after FAA and EASA certification" could be cut with no source (F076). | "may not fit a live lock" on all three; "The test reads"; the clause is cut from the claim. | 4ad3825 | none | fixed |
| F106 | `docs/prepub/` records | S3 | Round 3 (R3-8, R3-9): the after-state on file predated the last changes; fifteen source-reviewer IDs had no row in section 2; F080's evidence line was wrong; `BASELINE.md` had no "Fresh clone" section. | One battery rerun on the final tree and every count rewritten from it (`BASELINE.md`); the IDs mapped below; F080 corrected. | cd76867 | none | fixed |
| F107 | `data/guidance.csv:29` | S3 | Round 3 (R3-10, attacking F054): no cached transcript backs the new row. The passage, both sentences, and the speaker's printed title were read from the Fool page twice on 2026-11-11 (DECISIONS D16); the page is not cached under `data/raw/sources/calls/`. | none | none | none | open: the owner caches the transcript when next online, as the other calls are |
| F108 | `src/gdn/report.py` (`post`, `run`) | S2 | Found on the advisor's prompt, measured in a scratch clone: with two scored locks and the latest lock made while private, the post came to 1,307 and 1,305 characters. `report.run` exits over 1,300, so the daily rebuild would have stopped after the second score unless the repository had gone public first. No test covered that state. | The opener for two or more locks is shorter ("2 locked estimates so far"), and the test builds that state with a two-digit miss and requires ten characters of room. | 1e9a890 | `tests/test_after_score.py::test_the_post_counts_its_locked_quarters` FAIL / PASS (`REVERT_TESTS.md`) | fixed |

## 2. Reviewer findings, each mapped to a row

Round 1 reviewers read the tree at `9a5cb5a`. Round 2 reviewers (EDITOR, FINANCE and the second statistician, written here as R2-STAT) read a copy of `f34d393` with no history and no audit files. Every finding was checked against the tree or the data before it was accepted. "ok" means the reviewer's evidence reproduced.

| Reviewer ID | Sev (theirs) | Row | Status |
|---|---|---|---|
| BUYSIDE-1 | S1 | F002 | fixed |
| BUYSIDE-2 | S1 | F006, F007 | fixed |
| BUYSIDE-3 | S1 | F013, F036 | fixed |
| BUYSIDE-4 | S1 | F009, F013 | fixed |
| BUYSIDE-5 | S1 | F038 | refuted as a tree defect; `GO_PUBLIC.md` |
| BUYSIDE-6 | S1 | F021 | fixed |
| BUYSIDE-7 | S2 | F025 | fixed |
| BUYSIDE-8 | S2 | F024 | fixed |
| BUYSIDE-9 | S2 | F012 | fixed |
| BUYSIDE-10 | S2 | F029 | fixed |
| BUYSIDE-11 | S2 | F023 | fixed |
| BUYSIDE-12 | S2 | F026 | fixed |
| BUYSIDE-13 | S2 | F021, F027 | fixed |
| BUYSIDE-14 | S2 | F028 | fixed |
| BUYSIDE-15 | S2 | F007 | fixed |
| BUYSIDE-16 | S2 | F025 | fixed |
| BUYSIDE-17 | S2 | F031 | fixed |
| BUYSIDE-18 | S2 | F024 | fixed |
| BUYSIDE-19 | S2 | F030 | fixed |
| BUYSIDE-20 | S3 | F011 | fixed |
| BUYSIDE-21 | S3 | F008 | fixed |
| BUYSIDE-22 | S3 | F029 | fixed |
| BUYSIDE-23 | S3 | F032 | fixed |
| BUYSIDE-24 | S3 | F009 | fixed |
| BUYSIDE-25 | S3 | F068 | open |
| BUYSIDE-26 | S3 | F001 | fixed |
| BUYSIDE-27 | S3 | F081 | open: owner |
| COMPLIANCE-1 | S1 | F006, F007 | fixed |
| COMPLIANCE-2 | S1 | F002 | fixed |
| COMPLIANCE-3 | S1 | F038 | refuted as a tree defect; `GO_PUBLIC.md` |
| COMPLIANCE-4 | S1 | F021 | fixed |
| COMPLIANCE-5 | S1 | F013 | fixed |
| COMPLIANCE-6 | S1 | F005 | fixed |
| COMPLIANCE-7 | S2 | F030 | fixed |
| COMPLIANCE-8 | S2 | F026 | fixed |
| COMPLIANCE-9 | S2 | F011 | fixed |
| COMPLIANCE-10 | S2 | F028 | fixed |
| COMPLIANCE-11 | S2 | F027 | fixed |
| COMPLIANCE-12 | S2 | F030 (every page), F081 (undated) | fixed; open: owner |
| COMPLIANCE-13 | S2 | F008, F036 | fixed |
| COMPLIANCE-14 | S2 | F030 | fixed |
| COMPLIANCE-15 | S2 | F007 | fixed |
| COMPLIANCE-16 | S2 | F029 | fixed |
| COMPLIANCE-17 | S2 | F069 | fixed |
| COMPLIANCE-18 | S2 | F070 | fixed |
| COMPLIANCE-19 | S2 | F071 | refuted; owner's choice |
| COMPLIANCE-20 | S2 | F037 | erratum |
| COMPLIANCE-21 | S3 | F072 | fixed |
| COMPLIANCE-22 | S3 | F072 | fixed |
| COMPLIANCE-23 | S3 | F053 | open (`og:image`) |
| COMPLIANCE-24 | S3 | F016 | open: owner |
| COMPLIANCE-25 | S3 | F015 | open: owner |
| COMPLIANCE-26 | S3 | F073 | fixed |
| COMPLIANCE-27 | S3 | F073 | fixed |
| COMPLIANCE-28 | S3 | F001 | fixed |
| COMPLIANCE-29 | S3 | F011 | fixed |
| COMPLIANCE-30 | S3 | F078 | refuted |
| COMPLIANCE-31 | S2 | F071 | refuted; owner's choice |
| STAT-1 | S1 | F006, F007 | fixed |
| STAT-2 | S2 | F034 | fixed |
| STAT-3 | S2 | F034 | fixed |
| STAT-4 | S2 | F032, F051 | fixed |
| STAT-5 | S2 | F023 | fixed |
| STAT-6 | S2 | F024 | fixed |
| STAT-7 | S2 | F025 | fixed |
| STAT-8 | S2 | F050 | fixed |
| STAT-9 | S2 | F012 | fixed |
| STAT-10 | S2 | F048 | fixed; erratum E8 |
| STAT-11 | S3 | F074 | open |
| STAT-12 | S3 | F050 | fixed |
| STAT-13 | S3 | F074 | open |
| STAT-14 | S3 | F050 | fixed |
| STAT-15 | S3 | F074 | open |
| STAT-16 | S3 | F040 | fixed: the README names the working file and says it is not an estimate (the lead F040 itself is refuted) |
| REGISTRY-1 | S1 | F033 | fixed |
| REGISTRY-2 | S1 | F011 | fixed |
| REGISTRY-3 | S2 | F033, F045 | fixed |
| REGISTRY-4 | S2 | F055 | erratum |
| REGISTRY-5 | S2 | F057 | fixed |
| REGISTRY-6 | S2 | F056 | erratum |
| REGISTRY-7 | S2 | F017, F039, F062 | fixed; erratum |
| REGISTRY-8 | S2 | F046 | fixed |
| REGISTRY-9 | S3 | F047 | fixed |
| REGISTRY-10 | S3 | F075 | erratum |
| REGISTRY-11 | S3 | F079 | fixed |
| REGISTRY-12 | S3 | F063 | open |
| REGISTRY-13 | S3 | F052 | fixed |
| REGISTRY-14 | S3 | F052 | fixed |
| REGISTRY-15 | S3 | F063 | open |
| REGISTRY-16 | S3 | F063 | open |
| REGISTRY-17 | S3 | F063, F018 | open; the scoring half fixed |
| REGISTRY-18 | S3 | F052 | fixed |
| SELL-1 | S1 | F058 | fixed |
| SELL-2 | S2 | F022 | fixed |
| SELL-3 | S1 | F013 | fixed |
| SELL-4 | S1 | F006 | fixed |
| SELL-5 | S1 | F007 | fixed |
| SELL-6 | S1 | F002 | fixed |
| SELL-7 | S1 gate | F038 | refuted as a tree defect; `GO_PUBLIC.md` |
| SELL-8 | S2 | F033 | fixed |
| SELL-9 | S2 | F055 | erratum |
| SELL-10 | S2 | F023 | fixed |
| SELL-11 | S2 | F059 | fixed |
| SELL-12 | S2 | F061, F013, F066 | fixed |
| SELL-13 | S2 | F025 | fixed |
| SELL-14 | S2 | F024, F007 | fixed |
| SELL-15 | S2 | F080 | fixed |
| SELL-16 | S2 | F061 | fixed |
| SELL-17 | S2 | F060 | fixed |
| SELL-18 | S3 | F064 | open |
| SELL-19 | S3 | F076 | fixed |
| SELL-20 | S3 | F008 | fixed |
| SELL-21 | S3 | F077 | fixed |
| SELL-22 | S3 | F067 | fixed |
| SELL-23 | S3 | F001, F009 | fixed |
| SELL-24 | S3 | F065 | fixed |
| SELL-25 | S3 | F067 | fixed |
| SELL-26 | S3 | F010 | fixed |
| sources_guidance SRC-G-1 | S1 | F022 | fixed |
| sources_guidance SRC-G-4 | S3 | F054 | fixed |
| sources_claims SC-1 (12 stale figure rows) | S1 | F013 | fixed |
| sources_claims SC-4 (byline) | S2 | F036 | fixed |
| sources_claims cause-6 | overreach | F035 | fixed |
| sources_claims cause-8, cause-9 | unverified | F052 | fixed: the registry reviewer measured the mechanism (answer 10) |
| sources_claims cause-10 | unverified | F043 | refuted: matches the study's own README |
| EDITOR-1 | S1 | F083 | fixed |
| EDITOR-2 | S2 | F088 | fixed |
| EDITOR-3 | S2 | F086 | fixed |
| EDITOR-4 | S2 | F087 | fixed |
| EDITOR-5 | S2 | F084 | fixed |
| EDITOR-6, EDITOR-7 | S2 | F095 | fixed |
| EDITOR-8 | S2 | F083 | fixed |
| EDITOR-9 | S2 | F085 | fixed |
| EDITOR-10 | S2 | F096 | fixed |
| EDITOR-21 | S2 | F094 | fixed |
| EDITOR-11 to EDITOR-15 | S3 | F067, F098 | fixed |
| EDITOR-16, -18, -19, -20 | S3 | F098 | open |
| EDITOR-17 | S3 | F097 | fixed |
| FINANCE-1 | S1 | F083 | fixed |
| FINANCE-2, FINANCE-3 | S2 | F093 | fixed |
| FINANCE-4 | S2 | F094 | fixed; chart legends open |
| FINANCE-5 | S2 | F086 | fixed |
| FINANCE-6 | S2 | F087 | fixed |
| FINANCE-7 | S2 | F096 | fixed |
| FINANCE-8 | S2 | F095 | fixed |
| FINANCE-9 | S2 | F085 | fixed |
| FINANCE-10 | S3 | F064 | open |
| FINANCE-11 | S2 | F092 | fixed |
| FINANCE-12, -13, -15, -16 | S3 | F098 | open |
| FINANCE-14 | S3 | F098 | fixed |
| FINANCE-17 | S1 | F085 | fixed |
| R2-STAT-1 | S2 | F086 | fixed |
| R2-STAT-2 | S2 | F087 | fixed |
| R2-STAT-3 | S1 | F084 | fixed |
| R2-STAT-4 | S2 | F090 | fixed |
| R2-STAT-5, -6, -8 | S2 | F091 | fixed |
| R2-STAT-7 | S2 | F092 | fixed |
| R2-STAT-9 | S2 | F083 | fixed |
| R2-STAT-10 | S2 | F089 | fixed |
| R2-STAT-12, R2-STAT-20 | S3, S2 | F083 | fixed |
| R2-STAT-11, -13 to -19 | S3 | F098 | open |
| sources_claims SC-2, SC-14 (the preview section) | S1, S3 | F036 | fixed: the section is dropped once scored |
| sources_claims SC-3 | S2 | F066 | fixed |
| sources_claims SC-5, SC-7, SC-8 (July statements read after October) | S1, S2 | F036 | fixed: dated to the 2026-07-29 call under "before the release" |
| sources_claims SC-6 | S2 | F065 | fixed |
| sources_claims SC-9 | S3 | F004 | fixed |
| sources_claims SC-10 | S3 | F098 | open: the claim cites the 2024 10-K accurately; the 2025 10-K rewords it |
| sources_claims SC-11 | S2 | F035, F061 | fixed |
| sources_claims SC-12 | S3 | F035 | fixed: the sentence is no longer in the note (`grep -c "mix moves revenue per jet"`: 0) |
| sources_claims SC-13 | S3 | F077 | fixed |
| sources_guidance SRC-G-2 | S3 | F098 | open: the preregistration's example quote prints dollars where the transcripts print "150 to 155"; the preregistration does not change (R7) |
| sources_guidance SRC-G-3 | S3 | F098 | open: three MarketBeat links refuse automated readers (`LINKS.csv`: 3 of 145 external links, status 403); each quote was verified on another transcript |
| sources_guidance SRC-G-5 | S3 | F098 | open: the speaker column copies each page's label, so one 2021 title is shorter than the rest |
| R3-1 | S2 | F101 | fixed |
| R3-2 | S2 | F102 | fixed |
| R3-3 | S2 | F103 | fixed |
| R3-4 | S2 | F104 | fixed |
| R3-5, R3-6, R3-7 | S3 | F105, F076 | fixed |
| R3-8, R3-9 | S3 | F106 | fixed |
| R3-10 | S3 | F107 | open: owner |
| recompute (547 figures) | | `RECOMPUTE_DIFF.md` | 547 match, no finding |
| sources_deliveries (43 quarters) | | `SOURCES_DELIVERIES.csv` | 43 verified, no finding |

## 3. The first ledger's flagged rows (P1.3)

The first run on the real tree (`cc83c82`) flagged 25 rows. Each maps to a finding above, and the final ledger flags none.

| Surface | Rows | Finding |
|---|---|---|
| `interview` | 5 stale, 9 untraced | F006 |
| `resume` | 1 stale | F007 |
| `chart` | 7 stale | F002 |
| `dashboard` | 1 stale | F009 |
| `build-notes` | 1 stale | F010 |
| `note-pdf` | 1 stale | F008 |

## 4. Counts

`FINDINGS.md` holds 107 findings (F001 to F108; F019 is an unused number). They come from the spec's 16 leads, the first ledger, five round 1 reviewers, three source checkers, the recompute, three round 2 reviewers, one round 3 reviewer and the main thread's own checks.

| Severity | Fixed | Erratum | Refuted | Open | All |
|---|---|---|---|---|---|
| S1 | 19 | 0 | 3 | 2 | 24 |
| S2 | 48 | 5 | 2 | 1 | 56 |
| S3 | 18 | 1 | 1 | 7 | 27 |
| All | 85 | 6 | 6 | 10 | 107 |

Open S1: F015, F016. Open S2: F081. Open S3: F053, F063, F064, F068, F074, F098, F107.
