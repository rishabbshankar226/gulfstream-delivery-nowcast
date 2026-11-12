# Round 4: editor

Verdict: NO-GO. Sixteen public build-brief files print the owner's home-folder path, account name included, and the first screens of the dashboard and the note present the owner's own guidance pace as "GD's guidance pace" with no word that GD never published it.

Counts: S1 1, S2 5, S3 11

## Answers

**1. Staleness.** The scored state is `results/live/2026Q3_score.json`: reported 40 (35 large, 5 mid), lock 31.95, AE 8.05, APE 20.1%, outside the band, guidance pace 33.84 with AE 6.16. The lock (`results/live/2026Q3_lock.json`) was published 2026-10-29T05:51:24Z; `gh release view lock-2026Q3` printed the same time, and `shasum -a 256 predictions/2026Q3.json` printed the sha256 in the lock file. Every live-record sentence on the post, README, dashboard, note, interview notes and resume bullets matches these values. On the workbook's Live sheet only the typed inputs could be compared (snapshot 2026-10-29, 35, 7, 187, 28, 40, 33.84, the accession); its formula cells hold no cached values. The README's claim that the 2026Q3 count "is the same in every daily snapshot since, to 2026-11-12" (README:92) holds: a script over `data/snapshots/daily/*.serials.csv.gz` printed 35 large and 7 mid from 2026-10-27 through 2026-11-12. The README's live sections are generated (`src/gdn/report.py`), so they move with the data. Stale or near-stale wording I found:
- `report/note.html:74` says the archived copies "held more events for the same past quarters than today's file". The file compared is the 2026-10-19 copy, not today's (EDITOR-9).
- `report/note.html:80` gives book-to-bill "For the quarter" under a 2026Q3 heading. The figures are 2026Q2's (`data/processed/book_to_bill.csv`), and GD has since reported 2026Q3 ratios that differ widely (EDITOR-9).
- The workbook's Segments sheet shows the 2026Q3 estimates with no line saying GD has reported. The Sensitivity sheet carries one (EDITOR-8).
- `README:107` says `results/live/2026Q4_latest.json` "is not an estimate of the quarter", but that file's own key is `nowcast` (total 14.3, band 3.6 to 21.1) (EDITOR-16).
- `docs/PREREGISTRATION.md:3` says "before any holdout figure, live estimate or prediction exists". That is present tense pinned to the commit date, and the file is immutable, so this is not a finding.
- Labelled as of a date and still correct: `note.html:82` ("As of GD's 2026-07-29 call ... about 160"; GD's 2026-10-30 call row in `data/guidance.csv` gives no new number) and `note.html:84` (backlog flagged "not current").

**2. Contradictions between surfaces.**
- The guidance baseline is worded at least seven ways. The post (`docs/LINKEDIN_POST.md:4`) calls it "A pace I derived from GD's own full-year outlook", and `:6` calls it "GD's guidance pace" and "the pace". The README calls it "a pace built from GD's own guidance" (`README:3`), "GD's guidance pace" (`:6`, `:21`) and "GD guidance pace" (`:31`). The chart legend reads "Pace built from GD's outlook" (`output/charts/track_record.png`, `site/preview.png`). The workbook says "GD guidance baselines" (About!A9), "MAE guidance" (Summary!A6) and "Guidance pace" (Live!A20). The resume says "a guidance-based pace" (`docs/RESUME_BULLETS.md:1`) (EDITOR-2).
- The defense and Aerospace growth rule goes by four names. `README:123` and workbook About!A10 say "seasonal naive with drift". `site/index.html:89` says "the same quarter last year scaled by trailing growth". `site/app.js:417` and `:437` say "growth rule" and "growth row". `report/note.html:81` says "drift baseline" and `:85` "seasonal naive with drift". The workbook's Segments!L1 says "Drift 2026Q3" (EDITOR-5).
- The deadline for the G700 scope decision differs. `README:159` says "the amendment to decide before the next lock". `docs/prepub/ERRATA.md:65` says "before the 2026Q4 window closes on 2026-12-31" (EDITOR-6).
- The note's Exhibit 11 says it shows "The workbook's Summary and Segments sheets" (`report/note.html:100`), but it drops the Summary sheet's guidance row (workbook Summary!A6, C6) and relabels the rows (EDITOR-7).
- "Registry count" against "registry estimate": the preregistered sentence uses "registry count" (`docs/PREREGISTRATION.md:52`). The post, README and note use it, and the dashboard says "registry estimate". `ERRATA.md:113` (E10) records this. On page 1 of the note, though, "registry count" (5.5) and "raw registry count" (42) sit in adjacent key points, and the definition comes on page 2 (EDITOR-11).
- Band name: the preregistration says "Call it the past-miss band everywhere" (`docs/PREREGISTRATION.md:53`). The post (`:4`) and dashboard (`site/index.html:58`; `site/app.js:138`, `:294`, `:385`) say "band of past misses". The meaning is the same and no erratum records the change (EDITOR-12).
- "E1" and "E2" are the event definitions in `README:112` and `:113`, and also the errata IDs in `ERRATA.md:11` and `:23`. `README:121` cites "(E9)" (EDITOR-14).
- Figures that agree on every surface: 32.0, 21.2 to 37.2, 40, 8.0 (20%), 33.8 and 6.2, 39 and 1, 42 and 2, 41 and 1, 5.5, 6.9, 4.6, 18 of 26 (69.2%, 48.2% to 85.7%), 01:51 ET on 2026-10-29, and the window ending 2026-10-04.

**3. Units and rounding.**
- `README:156` uses "coverage" for registry events over GD's count ("registry coverage of at least half of GD's count"). It then says "In the last three held-out quarters it sat at 0.69 to 0.72", which is GD deliveries per registry event, the reciprocal. Read as coverage, the sentence says the registry saw about 70% of deliveries, the opposite of the truth (EDITOR-4). `report/note.html:93` uses "coverage of GD's count" with no number, so its direction is consistent. The metrics key `coverage_ratio` (`results/metrics.json`) is deliveries per event, the reverse of the README's word.
- Deliveries per registry event is used correctly elsewhere: `README:81` (1.18 mean, 0.69, 0.69, 0.72), `README:92` (0.76, 0.95), the dashboard tests list (`site/app.js:392` to `:395`), `note.html:75` and `:78`, and `docs/INTERVIEW_NOTES.md:13`.
- Script checks: the 2017Q1 to 2025Q2 mean is 1.1824 over 34 quarters; 163/215 = 0.76; 40/42 = 0.95; the yearly ratios are 1.92 (2016) and 1.26 (2019); mid cabin was 2.7 in 2016 and 2.14 in 2017.
- Percent bases: `README:35` defines "Average % miss". The note's Exhibit 2 heads a column "Average miss, %" with no base (`report/note.html:69`). The lock's "(20%)" is unbased on `README:6` and `:106`, `note.html:56`, `site/app.js:165` and `docs/INTERVIEW_NOTES.md:30`. Only the workbook says "Miss, % of reported" (Live!A18). The figure is right: 8.05/40 = 20.1% (EDITOR-17).
- Rounding is consistent on every surface: 31.95 to 32.0; 5.75 to 5.8 mid (26.2 + 5.8 = 32.0); 5.523 to 5.5; 6.917 to 6.9; 5.2503 to 5.3 (the note's 22-quarter figure, recomputed); 43.07 to 43.1. Exhibit 8 (`note.html:81`) recomputes to -$826M (-23.4%), $95M (2.7%), -$185M (-3.7%), -$61M (-2.6%), -$302M (-8.2%) and -$1,373M (-9.4%), and the four segments' reported operating earnings sum to $1.58B, printed as $1.6B.

**4. Style rules.** A Python scan (U+2014, U+2013, HTML entities, `\u` escapes, and the thirteen words with suffixes) ran over every surface in the brief, the workbook strings and the full PDF text. Hits:
- `docs/PREREGISTRATION.md:53`: "Clopper-Pearson" written with an en dash (immutable file).
- `docs/build/DECISIONS.md:111` and `docs/build/OUTLINES.md:32`: the same name with an en dash.
- `docs/build/review1_numbers.md:13` (the name), and `:86`, `:98`, `:114`, `:155`, where line and quarter ranges are written with an en dash; `docs/build/review1_spec.md:238` (the name).
- `report/claims.json:34`: an em dash inside a verbatim GD quote. Keep it: it is the source's punctuation, and the note paraphrases it without the dash.
- `docs/build/critique_a.md:44`: the heading "Emotional journey" (banned word).
- `docs/build/review2_code.md:76`: "unlocked prediction" means "not locked". That is not the banned sense.
- The post, README, dashboard, note, PDF, workbook, interview notes, resume, errata and `results/*.md` have no dash or banned-word hits.
- First person: "The author holds no position in General Dynamics" (`report/note.html:6`, `:60`) against "I hold no position" (`README:15`). The tile reads "this project's estimate" (`site/app.js:263`). The post's `:6` "(Registry count: my scaled estimate; the pace: mine.)" is not a sentence (EDITOR-13). Every "we" or "our" sits inside a quote.
- Causes: `results/error_analysis.md` states no cause for any of the five misses, and its two GD quotes are cited. `README:94` says no filing gives a cause. I found no uncited causal claim.

**5. Framing rules.** No sentence says the project counts jets before GD reports them, or beats GD or the market. The fill-in sentence appears on the post (`:6`), README (`:8`, `:19`), dashboard (`site/app.js:102` and `:103`), note (`:55`, `:68`), `results/error_analysis.md:3` and `docs/INTERVIEW_NOTES.md:24`. Close calls (EDITOR-10 and EDITOR-15):
- `docs/RESUME_BULLETS.md:1` gives the backtest figures with neither the fill-in caveat nor "not statistically distinguishable".
- The 60-second version (`docs/INTERVIEW_NOTES.md:7`) gives the backtest figures without the fill-in caveat. It carries only the commit-timing caveat.
- `docs/INTERVIEW_NOTES.md:20` asks "Where did the lead over the guidance pace come from?". The answer at `:21` disclaims the lead.
- Workbook Summary!A9 says a baseline with a lower holdout figure "beat the registry estimate". That defines "beat" by average miss alone, against the preregistered rule (`PREREGISTRATION.md:52`). By the sheet's own test, the registry estimate "beat" GD's guidance pace and last quarter.
- `site/app.js:88` holds a latent "The registry estimate beat ..." sentence. It renders only if Holm rejects, which the fixed backtest data does not do today.

**6. Jargon** (for a finance graduate without statistics or FAA background).
- Post: "80% band of past misses" is not explained. "held-out quarters" is undefined. "rules set minutes before scoring" (`:6`) is cryptic. "registry count" is defined in the parenthesis. "guidance pace" is defined at `:4`. "not statistically distinguishable" will parse.
- README first screen (`:1` to `:15`): "held-out" is undefined until `:119`. "nominal level is 80%" (`:6`) is undefined. "preregistered sign tests" (`:8`) is undefined on the first screen; "preregistered" comes at `:119`, and "sign test" is never put in plain words (`:37` adds "one-sided exact" and "Holm's correction"). "baseline" will parse. "registry copy" parses in context. "lock" is explained by `:6`.
- Elsewhere: "P10 to P90" (`output/charts/signed_errors.png` legend), "MAE" and "Holdout" (workbook Summary), "Past-miss P10" and "Past-miss P90" (workbook Live!A12, A13), and "Lag-1 autocorrelation" (`README:39`; half explained at `:47`) (EDITOR-17).

**7. Leftovers.** No TODO, FIXME, TBD or placeholder text appears on any surface. Internal codes a reader will see:
- `README:121` "(E9)", which clashes with the E1 and E2 definitions.
- `docs/prepub/ERRATA.md:84` "(`reviews/registry.md`, REGISTRY-10)", a reviewer's finding number (both in EDITOR-14).
- `ERRATA.md:9` cites `docs/prepub/RECOMPUTE_DIFF.md`, absent from the cold copy. That is known and not a finding.
- `docs/build/README.md:9` cites FACT_CHECK "F1 and F2" and claim ids. These are build notes and are labelled as such.
- The build briefs are prompts to coding agents and carry local paths (EDITOR-1).
- `docs/build/PLAN.md:58` to `:64` list scheduled tasks in the owner's desktop app. These are build notes, as of their date.

## Findings

**EDITOR-1. S1. Home-folder paths with the owner's account name in 16 public files.**
- Surface: `docs/build/briefs/`, hand-written (build session prompts). 24 lines: `review1_analyst.md:3,5`; `guidance_check_1.md:3`; `guidance_check_2.md:3`; `guidance_check_3.md:3`; `airframe_audit_1.md:3`; `airframe_audit_2.md:3`; `airframe_audit_3.md:3`; `critique_a.md:5`; `critique_b.md:5,6,7`; `_claims_common.md:3`; `review1_factcheck.md:3`; `review1_ops.md:3,5`; `review1_spec.md:3,5`; `review1_numbers.md:3,5`; `review2_code.md:3,11`; `review2_docs.md:3,13`.
- Evidence: a recursive `grep -rIl` for the macOS home-folder prefix over the text files outside `data/` and `.venv/` lists exactly these 16 files. A second grep over the CSV, JSON and Markdown files in `data/` found none. Each line holds an absolute path under the owner's macOS home folder. Some also show a private prompt-library folder and a plugin cache path, which reveal the local folder layout.
- Why S1: this round's rules treat the macOS account name and any home-folder path as data that must not be published, and the S1 clause covers exposing personal data when the repository goes public.
- Fix: replace each home-folder prefix with `<repo>` or `~` and add one dated line to `docs/build/README.md` saying paths were redacted. If these files exist in earlier commits, the history will still show them once public, and history may not be rewritten. Weigh that before going public.

**EDITOR-2. S2. "GD's guidance pace" reads as a GD figure on the dashboard's and the note's first screens.**
- Surfaces:
  - Dashboard live card: the fact "GD's guidance pace: 33.8 deliveries (missed by 6.2)" (`site/app.js:147` and `:148`, hand-written) and the lead "against 6.9 for GD's guidance pace" (`site/app.js:94`). The words "my construction, not a figure GD publishes" first appear far below, in Method (`site/index.html:103`) and in the tests list (`site/app.js:383`).
  - Note page 1, key points 1 and 2 (`report/note.html:55`, `:56`; generated by `src/gdn/note.py`). The definition arrives on page 2 (`report/note.html:68`). I read PDF pages 1 and 2 as images to confirm.
- Evidence: `results/live/2026Q3_score.json` has `"guidance_pace": 33.84`. GD's latest stated number is the full-year "about 160" (`data/guidance.csv`, 2026-07-29 row), and its 2026-10-30 call gave none. A finance reader will take "GD's guidance pace 33.8" as GD's quarterly guidance.
- The many wordings in Answer 2 compound this. The README (`:3`, `:23`) and the post (`:4`) handle it.
- Fix: at first use on each first screen, write "my pace from GD's full-year outlook" or add "(my construction, not a GD figure)". Pick one name and use it on every surface, including the chart legend (`src/gdn/charts.py`), the workbook (`src/gdn/workbook.py`) and the resume.

**EDITOR-3. S2. The post calls the band "my 80% band" with no word on its undercoverage.**
- Surface: `docs/LINKEDIN_POST.md:4`, generated by `src/gdn/report.py:565`.
- Evidence: the post says "outside my 80% band of past misses". `results/metrics.json` band: hits 18, n 26, coverage_pct 69.23, cp95_pct 48.21 to 85.67. `README:6` says "nominal level is 80% and which held 18 of 26", and `note.html:71` gives 69.2%. The post, the surface recruiters read, gives only the nominal level.
- Fix: "outside my band of past misses (nominally 80%; it held 18 of 26 backtest quarters)."

**EDITOR-4. S2. One README sentence quotes a number in the reciprocal of the word it uses.**
- Surface: `README:156` (Limitations, hand-written).
- Evidence: the paragraph defines a check as "registry coverage of at least half of GD's count", then says "In the last three held-out quarters it sat at 0.69 to 0.72". `results/metrics.json` `coverage_ratio.by_quarter`: 2025Q4 0.692, 2026Q1 0.691, 2026Q2 0.719. These are GD deliveries per registry event (the preregistered C(q), `PREREGISTRATION.md:55`), so registry events outnumber deliveries. Read as coverage, the sentence says the registry missed about 30% of deliveries.
- Fix: "In the last three held-out quarters GD delivered 0.69 to 0.72 jets per registry event, so the registry recorded more events than GD delivered." Keep "coverage" for one direction only.

**EDITOR-5. S2. The growth rule for the defense segments and Aerospace has four names across surfaces.**
- Surfaces: `README:123` and `report/note.html:85` say "seasonal naive with drift". `site/index.html:89` and `report/note.html:81` say "same quarter last year scaled by trailing growth". `site/app.js:417` and `:437` say "growth rule" and "growth row". `report/note.html:81` also says "drift baseline". The workbook says "seasonal naive with drift" (About!A10) and "Drift 2026Q3" (Segments!L1). `index.html` and `app.js` are hand-written; the note, workbook and README Method come from `src/gdn/note.py`, `src/gdn/workbook.py` and hand edits.
- Evidence: the strings above, from grep and `openpyxl`. `site/app.js:414` shows the rule is multiplicative: year-ago revenue equals `drift_usd * ttm_prior / ttm`.
- Fix: name it once, for example "the same quarter last year scaled by trailing growth (the seasonal naive with drift of my defense study)", then use one short name everywhere.

**EDITOR-6. S3. Two different deadlines for one decision.**
- Surfaces: `README:159` (hand-written) and `docs/prepub/ERRATA.md:65` (hand-written).
- Evidence: the README says the scope amendment is "to decide before the next lock". The errata say "before the 2026Q4 window closes on 2026-12-31". The next lock falls on the eve of GD's 2026Q4 release, after 2026-12-31 (`config/calendar.json` has no 2026Q4 date yet).
- Why S3: meeting the errata date also meets the README's, so the README is looser, not contradictory.
- Fix: use the errata date in the README.

**EDITOR-7. S2. The note's Exhibit 11 claims to show the workbook's Summary sheet but drops its guidance row.**
- Surface: `report/note.html:100`, generated by `src/gdn/note.py:584` to `:587`.
- Evidence: the exhibit lists four rows ("Average miss, ratio", "raw", "same quarter last year", "last quarter"). The workbook's Summary sheet has five, including A6 "MAE guidance" with C6 `=AVERAGE(Quarters!T18:T43)`. The labels also differ ("MAE ratio" against "Average miss, ratio"). The caption says "every figure above is a live formula over typed inputs", but the backlog figures in the same exhibit are typed inputs, not formulas: `openpyxl` shows Segments!N2 to N5 as the numbers 23977, 65182, 29350 and 17989, while J, K, L, M and O hold formulas.
- Fix: add the guidance row (6.9 held out, blank design) and either match the workbook's labels or say "relabelled". Say "formulas or typed inputs".

**EDITOR-8. S3. The workbook's Segments sheet has no line saying GD has reported 2026Q3.**
- Surface: workbook Segments!A20, generated by `src/gdn/workbook.py`.
- Evidence: Segments!L1 "Drift 2026Q3" and A15 "Aerospace from nowcast" show pre-release estimates. Sensitivity!A12 says "These are estimates made before the quarter's release"; Segments has no such line. GD reported Aerospace revenue of $3,536M (`site/data.json` `reported_segments`).
- Fix: add the Sensitivity sheet's sentence to Segments, with a pointer to what GD reported.

**EDITOR-9. S3. Two sentences in the note read stale on 2026-11-12.**
- Surfaces: `report/note.html:74` ("than today's file"), generated at `src/gdn/note.py:433`; and `report/note.html:80` ("For the quarter, GD's book-to-bill ... 1.4-to-1 for the defense segments"), text from `report/claims.json:40`.
- Evidence: the comparison file is the 2026-10-19 copy (`README:136`). `data/processed/book_to_bill.csv` holds 2026Q2 rows only. GD's 2026Q3 release (accession 0000040533-26-000036, fetched from SEC) reports book-to-bill of 8.5-to-1 for the defense segments, 1.4-to-1 for Aerospace and 6.8-to-1 company-wide. The section heading names 2026Q3, and Exhibit 10 (`:84`) flags its backlog as not current while this sentence carries no flag.
- Fix: write "than the 2026-10-19 copy", and "In 2026Q2, GD's book-to-bill ...", with the same "not current" line Exhibit 10 carries.

**EDITOR-10. S3. The fill-in caveat is missing from the resume and from the 60-second interview answer.**
- Surfaces: `docs/RESUME_BULLETS.md:1`, `docs/INTERVIEW_NOTES.md:7`, hand-written.
- Evidence: both give 5.5 against 6.9 and 4.6. Neither says the backtest copy had months or years to fill in, and the resume also omits "not statistically distinguishable".
- Fix: append "on a registry copy that had years to fill in; not statistically distinguishable" to the bullet, and one sentence to `:7`.

**EDITOR-11. S3. "Registry count" (5.5) and "raw registry count" (42) sit in adjacent key points on the note's first page.**
- Surface: `report/note.html:55`, `:56`, generated by `src/gdn/note.py`.
- Evidence: the clarifier ("In that sentence the registry count is the registry estimate") is at `:68`, on PDF page 2. E10 (`ERRATA.md:117` and `:118`) says each surface carries the clarifier, which is true for the note only from page 2.
- Fix: add the clarifier in a parenthesis to key point 1.

**EDITOR-12. S3. Dash and banned-word hits outside the main surfaces, plus the band name.**
- Surfaces: the hits listed in Answer 4 (PREREGISTRATION:53 is immutable; `docs/build/` files are hand-written build notes). Band name: `docs/LINKEDIN_POST.md:4`, `site/index.html:58` and `site/app.js:138`, `:294`, `:385` use "band of past misses" where `PREREGISTRATION.md:53` says "past-miss band everywhere".
- Fix: leave the preregistration as it is. Replace the en dashes in `docs/build/` with "to" or a plain hyphen if those notes may change. Use "past-miss band" on the post and dashboard, or add an erratum like E10.

**EDITOR-13. S3. Third person and a fragment where the owner set first person and plain sentences.**
- Surfaces: `report/note.html:6`, `:60` ("The author holds no position"). The sentence is read from `~/.gdn_disclosure` by `src/gdn/note.py:69`, so the fix is in that file. Also `docs/LINKEDIN_POST.md:6` ("(Registry count: my scaled estimate; the pace: mine.)", generated by `src/gdn/report.py:583`) and `site/app.js:263` ("this project's estimate").
- Fix: "I hold no position in General Dynamics." "(By registry count I mean my scaled estimate; the pace is mine.)" "my estimate".

**EDITOR-14. S3. Errata IDs collide with the event definitions, and a reviewer code shows.**
- Surfaces: `docs/prepub/ERRATA.md:11`, `:23` ("E1.", "E2."), `:84` ("REGISTRY-10"); `README:121` "(E9)", next to `README:112` and `:113`, which define E1 and E2.
- Fix: rename the errata "Erratum 1" and so on, or "X1", and cite by name. Drop the reviewer code.

**EDITOR-15. S3. Framing near-misses with the word "beat" or "lead".**
- Surfaces: workbook Summary!A9 (`src/gdn/workbook.py:142`); `docs/INTERVIEW_NOTES.md:20`; `site/app.js:88` (latent; it does not render with the current `metrics.json`, where `holm_reject` is false for all three baselines).
- Evidence: Summary!A9 says "a baseline with a lower holdout figure than MAE ratio beat the registry estimate". By that test the registry estimate "beat" the guidance pace (5.5 against 6.9), which `README:8` says no test supports.
- Fix: "missed by less than the registry estimate". "Where did the lower average miss against the guidance pace come from?" Make the `app.js:88` branch say "was closer than ... and the sign test rejects".

**EDITOR-16. S3. The README says the 2026Q4 file is not an estimate; the file labels it `nowcast`.**
- Surface: `README:107`, generated by `src/gdn/report.py:490` and `:491`.
- Evidence: `results/live/2026Q4_latest.json` has `"nowcast": {"total": 14.307...}` and `"band": [3.587..., 21.108...]`. The preregistration fixes the key names, so only the README can change.
- Fix: "Its `nowcast` field scales a part-quarter count and is not an estimate of the quarter."

**EDITOR-17. S3. Undefined jargon and unstated percent bases.**
- Surfaces: post `:4`, `:6`; `README:6`, `:8`, `:37`; `output/charts/signed_errors.png` legend; workbook Summary and Live!A12, A13; `report/note.html:69` ("Average miss, %"); the "(20%)" on `README:6`, `:106`, `note.html:56`, `site/app.js:165`.
- Fix:
  - Define "held-out" in a few words where it first appears: "quarters kept out of rule-setting".
  - Write "band of past misses, nominally 80%".
  - Say "sign test (counts the quarters each estimate was closer)".
  - Use "10th to 90th percentile" in the chart legend.
  - Use "average miss" in place of "MAE".
  - Write "20% of GD's count".

## Improvements that would raise the project's standing

1. Put the locked 2026Q3 point (32.0 against 40) on the README and preview chart. Today the image a LinkedIn reader sees (`site/preview.png`) shows only the backtest.
2. Give the guidance baseline one name that carries its authorship, such as "my pace from GD's outlook", on every surface. That name would remove the clarifier sentences now needed on three surfaces.
3. Add one plain-words line under the README's first screen that defines held-out quarter, the band and the sign test. A recruiter will stop at these three terms.
4. In `results/error_analysis.md`, under 2025Q4, cross-reference the two `GULFSTREAM LEASING LLC` events that `ERRATA.md:73` to `:76` and `README:159` record for that quarter. This is a known contributor, not a cause.
5. Bring the interview notes' one-line answer to "what did the lock show" to the top. It is the project's most honest and most interesting result.

## Checked and clean

- Live record figures on all surfaces against `2026Q3_score.json`, `2026Q3_lock.json`, `predictions/2026Q3.json` (sha256 matches) and `gh release view` (published 2026-10-29T05:51:24Z, which is 01:51 ET).
- `README:21` to `:53` figures against `results/metrics.json`. The by-year table (`README:59` to `:67`), the 2023 and 2024 split (12.51 and 3.48; other 18 quarters 4.43 and 6.43) and "closer in each of the last five quarters" (2025Q3 to 2026Q3; 2025Q2 went to the ratio) were recomputed from `results/holdout.csv`.
- The as-of table and its lag sums (206 against 203; 146 against 63) against `results/exploratory/asof.csv` and `data/processed/registry_quarterly.csv`.
- The sensitivity figures cited in `README:49`.
- The minimum held-out mid-cabin count of 3 (`README:158`). The dashboard pipeline total of 258.
- GD's 2026Q3 release, fetched from SEC (acceptance 2026-10-30 08:09:27): deliveries 35, 5, 40 (39 a year earlier); segment revenue as in `site/data.json`; Marine Systems total backlog $146,865M, which matches the note's $146.9B (`note.html:84`, hand-typed at `src/gdn/note.py:551`). Lock to acceptance is about 30 hours, as `ERRATA.md:109` says.
- All relative links in the README, errata, build README and interview notes resolve in the cold copy.
- Text files in the tree (outside `.venv/`) hold no email address other than placeholder test addresses (`example.com`, `example.invalid`) and no common token prefix (`ghp_`, `github_pat_`, `gho_`, `AKIA`, `sk-`, `xox`). A script that read the SEC user-agent at run time, without printing it, found it in 0 files. The workbook's creator property is the owner's public name only.
- The error analysis states no cause, and its GD quotes are cited.

## Suspicions, not proven

- `docs/build/REHEARSAL.md:9` shows a rehearsal score on a fixture 8-K with total 40 (33 large, 7 mid), the same total GD later reported (35 and 5). A skeptic could read it as foreknowledge. `git log` on that file, showing it last changed before 2026-10-30, would settle it. `docs/build/README.md:3` says every build note was last changed 2026-10-19, which I cannot check in a tree without history.
- "Seasonal naive with drift" usually names an additive drift in forecasting texts, while the code scales by trailing growth (`site/app.js:414`). Whether the defense study uses the same multiplicative form would settle whether the name fits. I did not open that study.

## Could not check, and refused commands

- Tree read: the cold copy at `~/gdn-prepub/round4/` (no git history). The PDF's input stamp equals `sha256(report/note.html)` (both `e0b89a40...`), so the PDF text is the note's text; I read PDF pages 1 and 2 as images and the full text with `pypdf`.

- Git history claims: `README:119` ("two minutes before"), `README:176` ("every daily commit since 2026-10-31"), `docs/build/README.md:3`, and `ERRATA.md:8` (547 figures recomputed). My tree has no history.
- External pages: I did not fetch the Pages dashboard, the defense backlog study, the personal site, or the fool.com and MarketBeat transcripts. Their URLs carry the owner's handle or name, or are outside my lane. Also unchecked: the Wayback captures; `README:157` ("The FAA added a third G280 type code in October 2026"); and the 17 G700 rows (`README:159`, `ERRATA.md:55` to `:59`), since the stored subsets are filtered by the scope rule and the raw file is not in the tree.
- The dashboard was not rendered. Its text was traced from `site/app.js` with `site/data.json`.
- No command was refused.
