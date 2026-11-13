# Round 2 review: editor and fact checker

Reviewer: `round2_editor`. Date: 2026-11-11. Tree read: `~/gdn-prepub/round2_clean`.
Scratch scripts and their outputs: `~/gdn-prepub/agents/round2_editor/`.
Every number below was printed by one of those scripts, by `grep`, by `gh release view`, or shown by a source I opened.

## Verdict

**NO-GO as it stands. One S1, ten S2, ten S3.** No headline figure is wrong. Every figure I recomputed matched its source, and GD's own release confirms the 40. The one blocker is a sentence in the owner's interview notes: `docs/INTERVIEW_NOTES.md:30` says "the registry had the quarter's jets in time". The owner's own rule forbids that claim and the lock's own airframe table does not support it.

Fix first:

1. The S1 sentence (EDITOR-1), and the stale "last three quarters" on the README, the note and the dashboard (EDITOR-2).
2. The post, line 6 and line 4: gloss "registry count", change "years" to "months or years", and reconcile "8.0 jets (20.1%)" with 32.0 and 40 (EDITOR-3, EDITOR-4, EDITOR-5).
3. The note: its callout "I wrote this note before GD reported", its "live quarter" label, and its missing disclosure of the 2021 reading (EDITOR-6, EDITOR-7, EDITOR-21).

After those, GO from this seat.

## Findings

### S1, blocking

**EDITOR-1 (S1). A claim the evidence does not support, and one the owner's framing rule forbids.**
Surface: `docs/INTERVIEW_NOTES.md:30`.
Text: "So the registry had the quarter's jets in time: the count had settled at 42 by the lock."
Evidence:
- `lines.py` over `data/snapshots/daily/2026-10-29.serials.csv.gz` (the lock's snapshot) printed: `lock events: 42 year>=2024: 30 no year: 7 year<=2023: 5 | large: total 35 old 4 | mid: total 7 old 1`. `misc.py` listed the five: a 1984 G-1159A, a 2009 G550, a 2016 G650ER, a G700 row with year 2006, a 2014 G150.
- By the registry's year field, then, at most 37 of the 42 events (30 dated 2024 or later, 7 with no year) can be new jets, against GD's 40. The G700 row dated 2006 cannot be read literally; if it is a field error the figure is 38. For large cabin it is 31, or 32 on that reading, against GD's 35. Either way the registry copy at the lock does not show 40 new jets.
- The registry counted 7 mid-cabin events; GD reported 5 (`results/live/2026Q3_score.json`).
- `daily.py` printed that the one change before the lock (41 to 42, snapshot 2026-10-27) was `('311', '2026-08-26', 'mid')`, and `lines.py` showed it is the 2014 G150.
- The README says the same thing carefully at `README.md:157`: "5 of the 42 events were airframes at least three years old".
Defensible version: "The raw count for the quarter was 42 at the lock, a miss of 2, and it has not changed in the 13 days of snapshots since. Five of those 42 events were airframes at least three years old by the registry's year field. My scaling took 0.76 deliveries per registry event from the four quarters before, and the quarter came in at 0.95."

### S2, major

**EDITOR-2 (S2). Stale sentence: "the last three quarters" no longer means the quarters its numbers describe.**
Surfaces:
- `README.md:81`: "the last three quarters sit at 0.69, 0.69, 0.72 against the 1.18 mean".
- `report/note.html:75` and PDF page 4 (beside Exhibit 6): same words.
- `site/app.js:388-395`, rendered: "GD delivered 0.69, 0.69, 0.72 jets per registry event in the last three quarters". The code hard-codes `["2025Q4", "2026Q1", "2026Q2"]`.
Evidence: `render.py` printed `cov recent [1.03, 0.69, 0.69, 0.72]` for 2025Q3 to 2026Q2. `lines.py` printed `40/42 = 0.952`. `README.md:92` says 2026Q3 "came in at 0.95". The last three quarters GD has reported are 2026Q1, 2026Q2 and 2026Q3: 0.69, 0.72, 0.95. On the README the two sentences sit eleven lines apart and cannot both be read as current. `README.md:156` already has the right words: "In the last three held-out quarters it sat at 0.69 to 0.72".
Severity note: S2, not S1. The sentence is about the backtest's coverage check, not the lock or the score, and its figures are right for the window the sentence before it names (2025Q3 to 2026Q2). It is still the first thing after EDITOR-1 that a reader of the dashboard can turn against the page.
Fix: "the last three held-out quarters (2025Q4 to 2026Q2) sit at 0.69, 0.69, 0.72 against the 1.18 mean; the locked quarter, 2026Q3, came in at 0.95". Same change in `src/gdn/note.py` and `site/app.js:394`.

**EDITOR-3 (S2). "8.0 (20.1%)" does not follow from the figures printed beside it.**
Surfaces: `docs/LINKEDIN_POST.md:4`, `README.md:6`, `README.md:106`, `report/note.html:56` and `:78`, dashboard live card (`site/app.js:165`), `docs/INTERVIEW_NOTES.md:30`.
Evidence: `lines.py` printed `8.0/40 = 20.00% | ae/40 = 20.12%`. The unrounded miss is 8.047 (`results/live/2026Q3_score.json`), so 20.1% is right and it is not a wrong number. A reader of the post has only "32.0", "40" and "8.0", and 8.0 over 40 is 20.0%.
Defensible version: in the post, drop the percentage or round it the same way as the rest: "missed by 8.0 jets, a fifth of the quarter" or "8.0 jets (20%)". On the README and the note, either print "20%" or print the estimate to two places once ("31.95").

**EDITOR-4 (S2). "Registry count" names two things. In the post it carries the wrong row's meaning with no gloss.**
Surfaces:
- Scaled estimate called "registry count": `docs/LINKEDIN_POST.md:6`, `README.md:21`, `report/note.html:55` (key point 1) and `:68`.
- Raw count called "registry count": `README.md:30` ("Raw registry count | 6.2"), `README.md:92` ("the quarter's count stood at 42"), `README.md:94`, `README.md:117` ("scales the registry count"), `results/error_analysis.md` ("why the registry count differed"), note key point 2 ("the raw registry count (42)").
- Dashboard lead (`site/app.js:92`): "the registry estimate was off by 5.5 jets a quarter on average, when GD delivers about 33". `README.md:8` and `docs/INTERVIEW_NOTES.md:7` also say "registry estimate".
Evidence: `canon.py` printed `mae: raw 6.19, ratio 5.52`. `docs/PREREGISTRATION.md:52` fixes the sentence "the registry count was off by X" for the README, the note, the dashboard and the post. The README (`:23`) and the note (`:68`) add a gloss. The post has none, and on the note's first page key point 1 says "registry count" for 5.5 while key point 2 says "raw registry count" for 42; the gloss comes a page later. The dashboard does not use the preregistered words at all.
Defensible version for the post: "Over 26 held-out quarters the registry count, scaled, was off by 5.5 jets a quarter on average" or add one clause after the sentence: "(the count scaled by the last four quarters' ratio)". For the note's key point 1, move the gloss into the key point. Decide whether the dashboard should match the preregistered sentence or the README should say why it differs.

**EDITOR-5 (S2). "Years to fill in" against the owner's own "months or years".**
Surfaces: `docs/LINKEDIN_POST.md:6` ("a registry copy that had years to fill in"), `README.md:153`, `report/note.html:78` (live quarter paragraph) and `:90` (Processing limitation).
Evidence: `lines.py` printed `days 2026-07-05 -> 2026-10-19: 106 | 2025-12-31 -> 2026-10-19: 292`. The copy had 106 days for 2026Q2 and 292 for 2025Q4. `README.md:19`, `report/note.html:68`, `site/app.js:102-103`, `docs/INTERVIEW_NOTES.md:24` and `results/error_analysis.md:3` all say "months or years".
Fix: "months or years" in all four places. In the post: "That test reads a registry copy that had months or years to fill in".

**EDITOR-6 (S2). "I wrote this note before GD reported 2026Q3" is not true of the whole note.**
Surface: `report/note.html:59`, PDF page 1 callout.
Evidence: `docs/build/README.md:9` says "On 2026-11-11 the pre-publication audit put the same two facts back", the two G300 and G280 bullets in the product cycle, and the Mid-cabin gap limitation leans on them. The callout sorts the note into "the key points above and Exhibit 8" (updated) and "the sections marked 'before the release'" (as written). Business overview, Gulfstream's product cycle, The tracker, The live quarter, Risks, Limitations and the Model page are in neither class, and the live quarter paragraph plainly was written after the release ("GD then reported 40").
Defensible version: "I made the estimates in this note before GD reported 2026Q3 on 2026-10-30. The key points, the live quarter paragraph and Exhibit 8 now carry what GD reported, and I revised other wording on 2026-11-11. The estimates in the sections marked 'before the release' are unchanged."

**EDITOR-7 (S2). A scored quarter is labelled "the live quarter".**
Surfaces: `site/index.html:42` (h2 "The live quarter", over "2026Q3 · Scored: missed by 8.0, outside the band"), `report/note.html:77` (h3 "The live quarter: 2026Q3").
Evidence: `README.md:107` treats 2026Q4 as the open quarter. `site/app.js:109-112` keeps the newest locked or scored quarter on the card, so the dashboard shows nothing for 2026Q4 and its first panel calls a quarter scored on 2026-10-30 "live". The facts under the label are current.
Fix: "The latest locked quarter" on the dashboard and "The locked quarter: 2026Q3" in the note. Optionally one line on the card: "2026Q4 is open; no estimate is shown until its window closes."

**EDITOR-8 (S2). "Its miss came from the scale, not from late postings" is firmer than the evidence, and sits beside "Registry processing can lag by months".**
Surface: `README.md:92` against `README.md:153`.
Evidence: `daily.py` printed 42 events for 2026Q3 in every stored snapshot from 2026-10-27 to 2026-11-11, so the sentence "it is the same in every daily snapshot since, to 2026-11-11" is right. `lines.py` printed `2026-10-29 -> 2026-11-11: 13`. Thirteen days cannot rule out a posting that arrives months late. The as-of file supports the README in spirit: `results/exploratory/asof.csv` shows own-quarter counts 23 to 29 days after quarter end of 40, 54 and 55 against 38, 55 and 57 in the 2026-10-19 copy. No filing or call is cited for the cause.
Defensible version: "Its count has not moved in the 13 days of snapshots since the lock. The estimate was low because the scale was 0.76 deliveries per registry event and the quarter came in at 0.95."

**EDITOR-9 (S2). "Every number in it traces to a filing or a registry file."**
Surface: `docs/INTERVIEW_NOTES.md:33`.
Evidence: `README.md:146` says the guidance outlooks are "read from call transcripts (Motley Fool, with MarketBeat where no Fool page loaded)". The 6.9 headline baseline rests on them. The as-of study rests on Wayback Machine captures (`README.md:127`), and the note's defense percentages come from another study.
Defensible version: "Every number traces to a GD filing, a call transcript or a registry file, and the repository holds the link for each."

**EDITOR-10 (S2). The workbook describes the date bound as two-sided.**
Surface: `output/gd_gulfstream_model.xlsx`, About!A6: "within 365 days of first airworthiness".
Evidence: `wb.py text` printed the cell. `README.md:115`: "no later than 365 days after the airframe's first airworthiness date ... The bound is one-sided: a date before the airworthiness date passes." The note (`report/note.html`, The tracker) says "no later than a year after". The workbook is the one surface left with the old wording.
Fix: "no later than 365 days after first airworthiness (a date before it passes)".

**EDITOR-21 (S2). The note and the dashboard leave out the two readings of GD's guidance that the README discloses, and the note's footnote is flatter than the README's account.**
Surfaces: `report/note.html`, footnote to Exhibit 5 (PDF page 4): "No 2021 call stated a full-year number, so guidance in 2021 is the same quarter last year." Also the paragraph under Exhibit 3, and the dashboard's test list (`site/app.js:381-383`).
Evidence: `README.md:49` says GD's 2021-01-27 call gave the year as "10 fewer aircraft", that "Read as 117, the guidance pace misses by 6.7 on average, not 6.9, and the registry estimate is closer in 13 of 26 quarters", and that with GD's stated quarter plans "the baseline misses by 6.0 on average, not 6.9, and the registry estimate is closer in 12 of 26 quarters". `final_checks.py` searched the note's text for "10 fewer", "117", "6.7", "stated plan", "quarter plans" and "sensitivity": 0 hits each. The dashboard's sentence gives the 22 and the 4 and nothing more. `docs/INTERVIEW_NOTES.md:18` gives the quarter plans (6.0, 12 of 26) but not the 117 reading. The note is the surface an analyst reads, and both readings move the baseline the headline is set against.
Fix for the note's footnote: "No 2021 call stated a full-year number that the preregistered rule reads. GD's January 2021 call gave it as '10 fewer aircraft' than 2020; read as 117, the guidance pace misses by 6.7 on average, and with the quarter plans GD stated on six calls, by 6.0. See results/exploratory/sensitivity.md." One clause on the dashboard pointing to the same file.

### S3, minor

**EDITOR-11 (S3).** Workbook About!A2: "can they estimate the count before GD reports it?" A question, not a claim, but it is the one place a public surface puts "before GD reports" next to "count". Suggest: "and how far off is an estimate locked the day before GD reports?"

**EDITOR-12 (S3).** `README.md:153`: "as the as-of study below shows". The as-of study is above, at `README.md:125`. Say "above".

**EDITOR-13 (S3).** `docs/INTERVIEW_NOTES.md:39` "would have dropped every mid-cabin jet" against `README.md:144` "would drop nearly every mid-cabin delivery". Use "nearly every".

**EDITOR-14 (S3).** `docs/INTERVIEW_NOTES.md:5`: "that count drives the Aerospace segment". A claim of cause with no filing or call cited. The note itself says Aerospace revenue carries services and Jet Aviation. Suggest dropping the clause: "General Dynamics reports how many Gulfstream jets it delivered each quarter. I wanted to know how closely FAA registrations track that count."

**EDITOR-15 (S3).** `output/charts/dashboard.png` is a stale screenshot. Its eyebrow reads "General Dynamics · Gulfstream"; `site/index.html:25` now reads "Student research · not affiliated with General Dynamics or Gulfstream". The rest of the screenshot matches what `data.json` renders today. `grep` finds no public page that shows `dashboard.png`, `coverage.png` or `nowcast_path.png`; only `track_record.png` and `signed_errors.png` are used. Reshoot or leave it out, and consider linking the coverage chart from `README.md:81`.

**EDITOR-16 (S3). One thing, several names.** None changes a figure.
- The revenue rule: "seasonal naive with drift" (`README.md:123`, note, workbook About!A10), "drift baseline" (note Exhibit 8), "growth rule" (dashboard `site/app.js:417`), "the same quarter last year scaled by trailing growth" (`site/index.html:87`), "Drift 2026Q3" (workbook Segments!L1).
- The estimate: "registry estimate", "ratio", "the lock", "delivery estimate", and "nowcast" (workbook Live!A9 to A11, Segments!A14 to A16, release title "Locked nowcast 2026Q3", file names). The README and note title say "tracker".
- Baseline columns: "Seasonal" and "Last" in note Exhibit 5 and the workbook, "Same quarter last year" and "Last quarter" everywhere else.
- The test set: "held-out quarters" (README, note, post), "test quarters" (`site/app.js:382`, `:386`, `:397`), "Holdout" (workbook).
- Two things, one name: `docs/prepub/ERRATA.md` numbers its entries E1 to E8, and E1 and E2 are also the two event definitions throughout the README.
- Units: "jets", "aircraft", "deliveries" and "airplanes" all name the same unit. "Miss, %" in note Exhibit 8 and the dashboard table is signed (-23.4%), while "missed by 8.0 (20.1%)" is absolute.

**EDITOR-17 (S3).** `docs/prepub/ERRATA.md` is not in first person and uses session words an outsider cannot read: "this run" (`:3`, `:18`), "Not re-measured by the main thread" (`:86`), "the registry reviewer" (`:83`). The README links it by name at `:159`.

**EDITOR-18 (S3). Dashboard small points**, all from `site/app.js` read against `site/data.json`.
- `:323-325`: the path chart's aria-label gives "latest 32.0" and the guidance pace but not GD's 40 or the lock marker, both of which the chart draws.
- `:283`: "A point posts with each day's registry snapshot" in the present tense for a finished path of 12 snapshots.
- `:143-144`: the card's big figure is the estimate locked from the 2026-10-29 snapshot, and the facts beside it cite "snapshot 2026-10-30". Same counts, two dates.
- `:427-436`: with the inserted sentence, the text reads "GD reported $3.5B of Aerospace revenue. That $85M includes services", and "That" now points at the wrong figure. "so the delivery-based figure fell" does not say fell against what.
- `:440-444` and note Exhibit 9: the delivery-count table stops at 36.0. GD reported 40.
- `:377`: the 0.10 autocorrelation against last quarter is called positive and "less reliable" with no size caveat; `README.md:47` says only the 0.35 exceeds one standard error.

**EDITOR-19 (S3).** Note Exhibit 11 is captioned "The workbook's Summary and Segments sheets" and leaves out the workbook's "MAE guidance" row (Summary!A6, C6), the 6.9 the headline is set against.

**EDITOR-20 (S3). Post and owner material, style.**
- `docs/LINKEDIN_POST.md:6`: "the rules: Over 26" has a capital after a colon, and "held out" then "held-out" in one sentence. Suggest: "The backtest: over 26 held-out quarters ...".
- `docs/INTERVIEW_NOTES.md:7` says the rules were committed before scoring and omits the README's caveat (`README.md:119`: two minutes before, same session, data already in the repository). `:24` gives "18 of 26" without the nominal 80%.
- The post and `docs/RESUME_BULLETS.md` say "I built" with no word on the AI coding agent; `README.md:176` and `docs/INTERVIEW_NOTES.md:36` disclose it. The owner's call; a hostile reader will set the two side by side.

## Headline figures across surfaces

Canonical values: `results/metrics.json`, `results/live/2026Q3_score.json`, `results/live/2026Q3_lock.json`, `predictions/2026Q3.json`, `results/estimates.json`, `data/processed/segments_reported.csv`. Dashboard values are what `site/app.js` renders from `site/data.json` (`render.py`; `site/data.json` metrics equal `results/metrics.json`: True).

| Figure | Canonical | Post | README | Note and PDF | Dashboard | Workbook | Interview, resume | Agree |
|---|---|---|---|---|---|---|---|---|
| Held-out quarters | 26 | 26 (`:6`) | 26 (`:3`, `:8`, `:21`) | 26 | 26 | Summary!C2:C6 over 26 rows | 26 | yes |
| Registry estimate, average miss | 5.523 | 5.5 "registry count" | 5.5 "registry count" (`:21`), "registry estimate" (`:8`, `:29`) | 5.5 "registry count" (key point 1), "registry estimate" (Exhibit 2) | 5.5 "registry estimate" | formula | 5.5 | value yes, name no (EDITOR-4) |
| GD guidance pace, average miss | 6.917 | 6.9 | 6.9 | 6.9 | 6.9 | formula | 6.9 | yes |
| Same quarter last year | 4.615 | 4.6 | 4.6 | 4.6 | 4.6 | formula | 4.6 | yes |
| Band coverage | 18 of 26, 69.2%, nominal 80%, 48.2% to 85.7% | not given | all four (`:51`), 18 of 26 and 80% (`:160`) | all four | all four | not given | 18 of 26 only | yes |
| Locked estimate | 31.953 | 32.0 | 32.0 | 32.0 (26.2 large, 5.8 mid) | 32.0 | Live!B11 formula | 32.0 | yes |
| GD reported | 40 (35 large, 5 mid) | 40 | 40 | 40 | 40 | Live!B16 = 40 | 40 | yes; SEC confirms |
| Miss | 8.047, 20.117% | 8.0 (20.1%) | 8.0 (20.1%) | 8.0 (20.1%) | 8.0 (20.1%) | formulas | 8.0, 20.1% | yes; see EDITOR-3 |
| Band | 21.23 to 37.24, outside | "outside my band" | 21.2 to 37.2 | 21.2 to 37.2 | 21.2 to 37.2 | Live!B14, B15 | 21.2 to 37.2 | yes |
| Guidance pace, 2026Q3 | 33.84, miss 6.16 | miss 6.2 | 33.8, 6.2 | 33.8, 6.2 | 33.8, 6.2 | Live!B20 = 33.84 | 33.8, 6.2 | yes |
| Last year's quarter | 39, miss 1 | (39) by 1 | (39) by 1 | (39) by 1 | 39, missed by 1 | n/a | miss of 1 | yes; SEC shows 39 |
| Raw count, last quarter | 42 miss 2; 41 miss 1 | not given | both (`:106`) | both | 35 + 7 registrations | Live!B3, B4 | 42, miss 2 | yes |
| Lock time | 2026-10-29T05:51:24Z | "the day before" | 01:51 ET on 2026-10-29 | same | 2026-10-29 at 01:51 ET | n/a | same | yes; `gh release view` shows the same time and sha256 |
| GD's release date | 2026-10-30 | not given | 2026-10-30 | 2026-10-30 | 2026-10-30 | n/a | 2026-10-30 | yes |
| Backtest snapshot | 2026-10-19 | not given | 2026-10-19 | 2026-10-19 | 2026-10-19 | About!A6, A18 | 2026-10-19 | yes; charts too |
| Lock snapshot | 2026-10-29 | not given | 2026-10-29 | 2026-10-29 | card cites 2026-10-30 | Live!B2 = 2026-10-29 | n/a | see EDITOR-18 |
| Words for the copy's age | "months or years" (owner's rule) | "years" | both | both | "months or years" | n/a | "months or years" | no (EDITOR-5) |
| Aerospace revenue: estimate, growth rule, reported, year ago | $2,710M, $3,631M, $3,536M, $3,234M | not given | not given | $2.7B, $3.6B, $3.5B, $3.2B | same | Segments formulas | not given | yes; SEC shows 3,536 and 3,234 |
| Revenue miss | -$826M, -23.4%; total -$1,373M, -9.4% | n/a | n/a | same | same | n/a | n/a | yes |
| Revenue per delivery | $84.8M | n/a | n/a | $85M | $85M | Segments!B13 | n/a | yes |

## The post

- Length: 1,283 characters (1,284 with the final newline), 13 lines. `post_links.py`.
- First 140: "My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40.\nI built a tracker that scale"
- First 210: "My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40.\nI built a tracker that scales FAA aircraft registrations into an estimate of the Gulfstream jets G"
- First two lines carry the live result (line 1, 111 characters) and what the project is (line 2). Yes.
- Names the baseline that beat the model: yes ("Simply repeating the same quarter last year missed by less on average, 4.6").
- Says the backtest reads a finished registry: yes, but with "years" (EDITOR-5).
- One disclaimer line with student project, not investment advice, no affiliation: yes (line 11).
- Hashtags: `#EquityResearch`, `#Aerospace`. No ticker.
- No dashes, no banned words, no non-ASCII characters. Does not say it counts jets before GD reports or beats anyone.
- Open: EDITOR-3 (20.1%), EDITOR-4 ("registry count"), EDITOR-5 ("years"), EDITOR-20 (colon and capital).

## Five sentences a hostile reader would quote back

1. `docs/INTERVIEW_NOTES.md:30`: "So the registry had the quarter's jets in time." Reply: five of your 42 events were old airframes, one from 1984. Say instead: the defensible version under EDITOR-1.
2. `docs/LINKEDIN_POST.md:6`: "the registry count was off by 5.5 jets". Reply: your README table says the raw registry count was off by 6.2. Say instead: "the registry count, scaled, was off by 5.5 jets".
3. `docs/LINKEDIN_POST.md:4`: "I said 32.0 ... reported 40 ... 8.0 jets (20.1%)". Reply: 8 over 40 is 20.0%. Say instead: "missed by 8.0 jets, a fifth of the quarter".
4. `README.md:81` and the dashboard: "the last three quarters sit at 0.69, 0.69, 0.72". Reply: your own live card shows 42 registrations against 40 deliveries last quarter. Say instead: "the last three held-out quarters (2025Q4 to 2026Q2) sit at 0.69, 0.69, 0.72; 2026Q3 came in at 0.95".
5. `report/note.html:59`: "I wrote this note before GD reported 2026Q3." Reply: your build notes say you edited it on 2026-11-11. Say instead: the defensible version under EDITOR-6.

Next in line: `docs/LINKEDIN_POST.md:6` "a registry copy that had years to fill in" (106 days for 2026Q2), and `docs/INTERVIEW_NOTES.md:33` "Every number in it traces to a filing or a registry file".

## What is right, checked

- **GD's 2026Q3 release.** Fetched Exhibit 99.1 of accession 0000040533-26-000036 from sec.gov (`sec_check.py`): "Large-cabin aircraft 35 33 ... Mid-cabin aircraft 5 6 ... Total 40 39", and revenue "Aerospace $ 3,536 $ 3,234 ... Total $ 14,566 $ 12,907". Matches the score file, the segments file and every surface.
- **The lock.** `gh release view lock-2026Q3` shows published 2026-10-29T05:51:24Z by `github-actions[bot]`, notes `sha256 3c4cdbd0...6f23`. My hash of `predictions/2026Q3.json` is the same. 05:51 UTC is 01:51 ET.
- **Staleness.** No sentence on the post, README, note, dashboard, workbook, error analysis, interview notes or resume bullets reads as if the 2026Q3 lock were ahead, unscored or provisional, apart from EDITOR-2 and the labels in EDITOR-7. No "will", "once" or "soon" about a past event (`sweep.py stale`). `nowcast_path.png` shows GD's 40, the lock diamond and "GD reported 2026-10-30". The workbook's Live sheet carries GD's 40 and the accession. The dashboard renders "Scored: missed by 8.0, outside the band".
- **Build stamps.** sha256 of `report/note.html` equals `output/GD_research_note.inputs.sha256`. `output/GD_research_note.pdf` and `site/GD_research_note.pdf` are byte-identical. The PDF has 7 pages and the disclaimer footer is on each.
- **README figures recomputed from `results/holdout.csv`, `metrics.json`, the registry and delivery files** (`holdout.py`, `holdout2.py`, `misc.py`, `final_checks.py`): the model table, the sign-test table, the by-year table, the cabin table, the five largest misses, 22 sourced quarters at 7.4, the note's 5.3 on those quarters (5.2503), 12.5 and 3.5 for 2023 and 2024, 4.4, 4.4 and 6.4 for the other 18, "closer in each of the last five quarters", the design-window figures, "11 of the 12 design quarters" and 2019Q4, 1.92 to 1.26, mid cabin above 2 in 2016 and 2017, mean 1.18 over 2017Q1 to 2025Q2, 246 of 1,251 (19.7%), 4,053 airframes, 5 of the 42 lock events, 25 days, 0.76 and 0.95, the truncation table, the as-of table and its 206 against 203 and 146 against 63.
- **`README.md:92`, "the same in every daily snapshot since".** True: 42 in all sixteen stored snapshots from 2026-10-27 to 2026-11-11 (`daily.py`). The trailing-count step from 189 to 188 on 2026-11-03 in `results/live/2026Q4_path.csv` is a 2026Q2 event leaving the file (57 to 56), not a 2026Q3 one.
- **Sensitivity and as-of write-ups** agree with the README's sentences that cite them.
- **Units.** Deliveries per registry event is used the right way round on the README, the note, the dashboard, the interview notes and `coverage.png`. Percent misses use GD's count as the base. Millions and billions agree between the note, the dashboard and the SEC release.
- **The call quotes.** The Motley Fool page for the 2026-07-29 call (published 2026-08-07, which explains the URL date) carries "Gulfstream will still deliver about 160 airplanes" and "the final 280 ought to deliver in the second quarter of next year".
- **Wording rules.** No em or en dash in prose on any surface, the workbook's 228 text cells included (`sweep.py`, `final_checks.py`). The only hits are a verbatim GD quote (`report/claims.json:34`) and "Clopper–Pearson" in `docs/PREREGISTRATION.md:53`, which is immutable. None of the banned words appears. No surface says the project beats the market or GD.
- **Links.** Every relative link in the README, the note, `docs/build/README.md` and `site/index.html` resolves in the copy. The dashboard's `#results` and `#limitations` anchors exist in the README.
- **Alt text.** The README's and the note's alt text match their images. Chart titles, legends and source lines match the data and the snapshot dates.
- **2026Q4.** No surface shows an estimate for it. `site/data.json` and `results/live/2026Q4_latest.json` hold a part count labelled `nowcast` (14.3), which `README.md:107` discloses.

## Not checked

- The repository and Pages links, and the two owner links (`rshankar.dev`, the defense backlog site): the first two return 404 until launch, and I did not send the owner's handle to an outside service.
- "Every daily commit since 2026-10-31 has come from the workflow" (`README.md:172`): the copy has no git history.
- The 75 Wayback captures, the 17 G700s under type code `3980222` (the raw zip is not in the copy), and the defense study's percentages in the note.
- The workbook in Excel: it stores no cached values, so I read formulas and typed inputs only, not number formats.
- The dashboard in a browser: I derived the rendered text from `site/app.js` and `site/data.json`, and compared it with `output/charts/dashboard.png`.
- The owner's tests: not run, by the brief.
- `docs/build/` beyond its README, and `docs/PREREGISTRATION.md` beyond section 3.6 and the headline rule.
