# Buy-side portfolio manager review (P4.2)

Reviewer: `buyside`. Date: 2026-11-11. Branch `prepub-audit` at `7b3ba7e`.

**Verdict: NO-GO as written.** Six blocking findings. The post itself is close to fair. What sits behind its two links is not in the same state as the post: the README's first image, the note, the dashboard's revenue panel, the interview notes and the resume bullets still describe 2026Q3 as a quarter that has not been reported, and the dashboard link returns 404 today.

Counts: **S1: 6. S2: 13. S3: 8.**

## What I read and how

Order: `docs/LINKEDIN_POST.md`, `README.md`, `site/index.html` with `site/app.js` and `site/data.json`, `report/note.html` and the PDF text (`pdftotext -layout output/GD_research_note.pdf`), the workbook's sheets with `openpyxl`, the five images in `output/charts/` with the Read tool, `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md`, `gh repo view`, `gh release view lock-2026Q3`.

The dashboard was not rendered. Its first screen is traced from `app.js` and `data.json`. Scratch scripts are in `~/gdn-prepub/agents/buyside/` (`recompute.py`, `byq.py`, `checks.py`, `checks2.py`, `guid_all.py`, `sec_local.py`, `wb.py`).

What held up when I recomputed it:

- Post and README headline figures. `recompute.py` over `results/holdout.csv` printed `ratio MAE 5.5234 n=26`, `guidance MAE 6.9173`, `seasonal MAE 4.6154`, `last 8.8077`, `raw 6.1923`. Every cell of the README's two Results tables, the year table, the truncation table and the five largest misses matches `results/metrics.json` or my recomputation.
- The live record. `results/live/2026Q3_score.json`: lock 31.953, reported 40, `ae_total` 8.047, `inside_band` false, `guidance_pace` 33.84, `guidance_ae` 6.16. The cached release (`data/raw/sec/0000040533-26-000036/gd-20261004exhibit991.htm`, queried by `sec_local.py`) reads "Large-cabin aircraft 35 33 101 95 Mid-cabin aircraft 5 6 18 18 Total 40 39 119 113".
- The lock. `shasum -a 256 predictions/2026Q3.json` and `git show lock-2026Q3:predictions/2026Q3.json | shasum -a 256` both print `3c4cdbd0...6f23`, the hash in the release body. `gh release view lock-2026Q3 --json publishedAt` prints `2026-10-29T05:51:24Z`, which is 01:51 ET. The cached EDGAR folder listing stamps the filing's files `2026-10-30 08:09:27`. If that stamp is Eastern time the lock is about 30 hours earlier.
- `site/data.json` metrics equal `results/metrics.json` (`checks2.py` printed `True`).

## The seven questions

### 1. After reading the post, what would I do with this?

Nothing with the number. In ninety seconds I take away: a student built a delivery estimate from FAA registrations, the one live quarter missed by 8 on 40, and on 26 past quarters the method did not beat repeating last year's quarter. I would not use it and the post does not ask me to. That takeaway is what the evidence supports, with three gaps:

- The post does not say the live miss was outside the band, or that every comparator was closer in that quarter (BUYSIDE-7).
- "The registry count" in the post is the scaled estimate, not the count (BUYSIDE-9).
- "GD's guidance pace" reads as GD's guidance. It is the author's quarterly split of GD's full-year number (BUYSIDE-10).

The one thing in here a PM would ask about is not on any surface: in 2026Q3 the unscaled count was 42 against 40 reported, and the scaling took it to 32.0. `site/data.json` shows large cabin as 35 events x 140/187 = 26.2 against 35 reported.

### 2. Is any sentence written so that a reader could take it as a trading signal or investment advice?

No sentence gives a rating, a target or a direction on the stock. `grep -n -i -w "buy\|sell\|long\|short\|alpha\|signal\|consensus\|target"` over the post, README, `index.html`, `note.html`, interview notes and resume bullets hits only the note's disclaimer (`note.html:57`) and the interview answer on price targets (`INTERVIEW_NOTES.md:23-24`). The nearest things to a call:

- `report/note.html:55`: "that estimate implies $2.7B of Aerospace revenue for 2026Q3, against $3.2B a year earlier". A revenue figure for a print, in the present tense. It is now stale and was wrong (BUYSIDE-3).
- `report/note.html:78`, Exhibit 8: "Aerospace, from the delivery estimate ... -$524M ... -16.2%".
- `report/note.html:83`: the heading "What the street watches on the print". Sell-side preview framing in a document dated before a print that has happened.
- `site/index.html:82`: the dashboard heading "What it means for GD", over `app.js:399-401`: "The delivery estimate of 32.0 sits below the 39 deliveries of 2025Q3 ... so the delivery-based figure falls". A directional read on a segment's revenue, still in the present tense (BUYSIDE-4).
- `docs/RESUME_BULLETS.md`: nothing in the three bullets reads as a signal or advice.
- `docs/INTERVIEW_NOTES.md:18`: "Because it is what the street anchors on." No source (BUYSIDE-22).
- `README.md:3`: "I estimate how many Gulfstream jets General Dynamics (GD) will report delivering each quarter". Forward-looking, not advice (BUYSIDE-18).
- Workbook `Segments!A15`: "Aerospace from nowcast".
- GitHub description: "Gulfstream deliveries estimated from FAA registrations, tested on 26 held-out GD quarters, each live estimate locked". Clean.
- `docs/INTERVIEW_NOTES.md:7`: "So I report it as a tracker, not as an edge." This is the right sentence and it is on no public surface.

Disclaimers: the note (`note.html:57`) and the dashboard footer (`index.html:106`) say "Not investment advice". The post, the README and the workbook's About sheet do not (BUYSIDE-19).

### 3. Does the project say plainly that the simplest baseline beat it?

| Surface | Says it? | Where and how |
|---|---|---|
| Post | Yes | Line 5, third sentence of the results paragraph: "Simply repeating the same quarter last year missed by less on average, 4.6." |
| README | Not in a sentence | Table row at line 22 (4.6) and sign-test row at line 32 (11 closer, 15 further, relative miss 1.20). No prose. |
| Dashboard | Yes, first screen | `app.js:98-99`, the smaller paragraph under the lead: "Simply repeating the same quarter last year missed by less, 4.6." Tile: "0.9 less than the registry estimate". |
| Note | Yes | Key point 1, third sentence, and the callout (`note.html:53`, `:65`). |
| Interview notes | Yes | Line 7. |
| Resume bullets | No | Line 1 gives only "vs 6.9 for guidance" (BUYSIDE-15). |
| Workbook | Number only | `Summary!C4` "MAE seasonal". No guidance row at all (BUYSIDE-17). |

The post's order and wording are fair: the miss leads, the favourable comparison is hedged in the next sentence, and the winning baseline follows at once. The README headline is not fair on its own. The bold sentence names only the baseline the estimate did better than, and the README is the one surface where no sentence says the same quarter last year won (BUYSIDE-8). The same is true of the design window: `README.md:43` prints 5.47 for the ratio against 5.00 and 3.83 for the two rules of thumb and draws no conclusion.

### 4. Does the first live quarter appear as early and as plainly as the backtest?

| Surface | Miss stated | "Outside the band" | Guidance comparison | Position | Stale? |
|---|---|---|---|---|---|
| Post | Yes, first sentence | No | No | Before the backtest | No |
| README text | Yes, line 92 | Yes, line 92 | Pace 33.8 given, its miss (6.2) not | Line 92, after Results and Error analysis | Text is current |
| README first image (`dashboard.png`) | No | No | No | Line 5, first thing a reader sees | **Yes**: "2026Q3 · PROVISIONAL", 31.1, "Locks the evening of 2026-10-29" |
| Dashboard | Yes, last row of the facts list | No: `grep -c inside_band site/app.js` prints 0 | Pace shown, miss not: `grep -c guidance_ae` prints 0 | Second block in the page, directly under the lead (`index.html:37-48`); by the layout in `dashboard.png` it starts on the first desktop screen | Wording stale ("GD reports 2026-10-30", "Registrations so far"); revenue panel stale |
| Note | No | No | "against a guidance pace of 33.8", no miss | Key point 2 | **Yes** |
| Workbook | No | No | No | `Live` sheet holds the lock only | Outcome absent |
| Interview notes | No | No | No | Lines 9 and 27 | **Yes**, future tense, pre-lock 31.1 |
| Resume bullets | No | No | No | Line 2 | **Yes**, future tense |
| `nowcast_path.png` | Shown as a line at 40 above the band | Visible | Visible | Not linked from README or note | Source line stale |

So: only the post leads with the live quarter, and only the README text says "outside the band". No surface says that GD's guidance pace, the same quarter last year, last quarter and the raw count were all closer than the lock in 2026Q3 (BUYSIDE-7).

### 5. Sizes and denominators

- Counts of quarters: given for every average in the post (26), README (26, 22, 12, 18 of 26), note and the dashboard's test list. The dashboard's lead sentence and the tiles' title carry no count (BUYSIDE-24).
- Scale: `recompute.py` printed a mean of 32.69 reported deliveries over the 26 quarters. The dashboard lead says "when GD delivers about 33". The post and the README prose never put 5.5 in scale (BUYSIDE-16).
- Percentage: the README and note tables give 17.9%. The post gives none. The live quarter's 20.1% (`ape_pct` 20.117) is on no surface: `grep -n -o "20\.1"` over the post, README, `app.js` and `note.html` returned nothing.
- The year table's rows are 4 quarters each, 2 for "2026, first half". Not labelled, readable.

### 6. Naming

Yes, it is a labelling error and a reader will catch it. "The registry count was off by 5.5" sits one line above a table whose "Raw registry count" row reads 6.2 and whose "Registry estimate (ratio)" row reads 5.5. The same sentence is at `docs/LINKEDIN_POST.md:5`, `README.md:13`, `report/note.html:53` and `:65`, and `docs/INTERVIEW_NOTES.md:7`. In the live quarter the collision is worse: the registry count was 42 (off by 2) and the thing the post calls the count was 32.0 (off by 8). See BUYSIDE-9. Other label drift is in BUYSIDE-25.

### 7. Would I interview this person on the strength of it?

On the post alone, yes. On what the links open today, not yet.

Raises my opinion:

- The post opens with the miss, in numbers, and does not explain it away.
- The winning baseline is named on the post, the dashboard's first screen and the note's first key point.
- The band's undercoverage (18 of 26 against a nominal 80%), the truncation table, the 10-of-30 audit disagreement and "Four quarters prove nothing" are all volunteered.
- The lock is checkable. I checked it: the hash matches and the release time precedes the filing.
- Every backtest number I recomputed matched.

Lowers it:

- The interview notes this person would speak from say the first lock "is scored when GD reports on 2026-10-30". GD reported twelve days ago.
- The README's first image shows a different estimate (31.1) from the README's text (32.0).
- A revenue preview for a reported quarter is still standing in the note and on the dashboard, with no actual beside it.
- In the one live quarter the method was the furthest of five from GD's count, and no surface says so.
- The rules were committed 2 minutes 16 seconds before the held-out quarters were scored, in a project built in one morning (BUYSIDE-13).
- Two clicks from the README, `docs/build/DECISIONS.md` shows an AI agent session built it, while the public prose says "I checked" and "I read" (BUYSIDE-14).
- No comparison with consensus, which is what a PM actually has. The interview notes assert the street anchors on a number the author built.

In the room I would ask: why did scaling turn 35 large-cabin events into 26.2 when GD reported 35; which of these steps did you do yourself; and what would make you drop the ratio for the raw count.

## Findings

### S1, blocking

**BUYSIDE-1. The README's first image shows the pre-lock state.** `README.md:5`, `output/charts/dashboard.png`.
Evidence: Read tool on the image: "2026Q3 · PROVISIONAL", "31.1 deliveries, estimated", "Band of past misses: 20.4 to 36.4", "Locks the evening of 2026-10-29", "One snapshot so far (2026-10-19)". `git log --format='%h %ad' -- output/charts/dashboard.png` prints `e5dbc5d 2026-10-19`. The record: lock 32.0, band 21.2 to 37.2, GD reported 40 (`results/live/2026Q3_score.json`). The image also reads "GD's own guidance pace" where the page now reads "GD's guidance pace".
Fix: retake the image from the page in its scored state, or drop it from the README.

**BUYSIDE-2. Interview notes and resume bullets describe the lock in the future tense, with the pre-lock estimate.** `docs/INTERVIEW_NOTES.md:9`, `:27`; `docs/RESUME_BULLETS.md:2`.
Evidence: "The first lock is scored when GD reports on 2026-10-30." "My build estimate is 31.1 deliveries, with a band of 20.4 to 36.4. It locks on 2026-10-29". "the first, for 2026Q3, is scored on 2026-10-30". `git log -1` on each file prints `a2f8e76 2026-10-19`.
Defensible version: "The first lock, for 2026Q3, was 32.0 with a band of 21.2 to 37.2, made at 01:51 ET on 2026-10-29. GD reported 40 on 2026-10-30: a miss of 8.0, outside the band. GD's guidance pace missed by 6.2."

**BUYSIDE-3. The note is a pre-print preview with the result inserted.** `report/note.html:51`, `:54`, `:55`, `:75`, `:78`, `:79`, `:83-84`; same text in `output/GD_research_note.pdf` and `site/GD_research_note.pdf` (identical sha256 `7f661070...`).
Evidence, from `pdftotext`:
- Byline "Data as of 2026-10-29", yet key point 2 says "GD reported 40", which is 2026-10-30 data.
- Key point 2: "My registry estimate for 2026Q3 is 32.0". Present tense. The miss and the band outcome are not stated, here or in "The live quarter: 2026Q3" ("GD then reported 40.").
- Key point 3 and Exhibit 8 give a 2026Q3 Aerospace revenue estimate of $2.7B, down 16.2%. `checks.py` against the cached release printed `Aerospace from delivery estimate 2710M vs actual 3536M: diff -826M (-23.4%)`, `actual aerospace yoy: 9.3%`, and `total ... 13193M vs actual 14566M: diff -1373M (-9.4%)`. The release reads "Revenue: Aerospace $ 3,536 $ 3,234 $ 302 9.3 %".
- "What the street watches on the print" says "GD delivered 79 jets in the first half of 2026". The release shows 119 through nine months.
Defensible version: state the score in key point 2 ("The lock missed by 8.0, or 20.1%, outside the band; GD's guidance pace missed by 6.2"). Relabel Exhibit 8 as what the lock implied before the release and add GD's reported column. Date the "watches" section to before the release or remove it.

**BUYSIDE-4. The dashboard still speaks of 2026Q3 as unreported: the revenue panel and two labels on the live card.** `site/index.html:81-89`; `site/app.js:128`, `:136`, `:262-263`, `:383-411`; `site/data.json` (`estimates.target` is `2026Q3`, `live[0].release_date` is `2026-10-30`).
Evidence: `app.js:399-404` builds "The delivery estimate of 32.0 sits below the 39 deliveries of 2025Q3 ... so the delivery-based figure falls". The live card on the same page says GD reported 40. The table heads its column "Estimate" with no reported column. Actuals as in BUYSIDE-3. On the live card of the scored quarter, `app.js:128` prints "Registrations so far", `:136` prints the row "GD reports" with 2026-10-30, and `:262-263` prints "12 snapshots so far". All three are in the present tense about a quarter GD reported twelve days ago.
Fix: once a quarter is scored, show GD's reported revenue beside each estimate and put the sentence in the past tense, or hide the panel until the next quarter has an estimate. For a scored quarter print "Registrations at the lock", "GD reported on" and "12 snapshots".

**BUYSIDE-5. The post's dashboard link returns 404.** `docs/LINKEDIN_POST.md:7`; also the repository's `homepageUrl` and `README.md:5`, `:7`.
Evidence: WebFetch of the link on 2026-11-11 returned "HTTP 404 Not Found". `gh repo view --json visibility` prints `PRIVATE`. `docs/build/DECISIONS.md:203` lists "enabling Pages" as not done, and `:187` says "`pages.yml` will not redeploy after a runner lock or score". So making the repository public is not enough: Pages must be enabled and the workflow run by hand, and the deployed copy must show the scored state. `README.md:7` ("once the repository is public") is then stale and should go.
Fix: a blocking pre-post step. Open the live URL in a private window and read the live card before posting. I could not test the second link (the repository) as an outsider while it is private.

**BUYSIDE-6. "Before I computed anything for a later quarter" is not what the commits show.** `README.md:105`.
Evidence: `git show 6725184 --stat` (2026-10-19 10:48:35 -0500) adds `data/processed/registry_quarterly.csv` and `gd_deliveries.csv`. `git show 6725184:data/processed/registry_quarterly.csv | grep -c "^202"` prints 26, with columns `e1_large,e1_mid,e2_large,e2_mid`; the same count for `gd_deliveries.csv`. E1 was chosen in `5c84d36` at 11:02:12. So both definitions' counts for all 26 later quarters, and GD's counts beside them, existed 14 minutes before the choice.
Defensible version: "before I scored any later quarter". `results/holdout.csv` first appears in `48c1ea0` at 11:04:28, after the preregistration commit `2c62ad3`. I cannot prove what was looked at; the commit order supports only the narrower sentence.

### S2, major

**BUYSIDE-7. No surface compares the live miss with anything, and only the README says "outside the band".** `docs/LINKEDIN_POST.md:1`; `README.md:92`; `site/app.js:144-147`; `report/note.html:54`, `:75`.
Evidence: `recompute.py` printed `ae 8.0468`, `guid ae 6.16`, `seasonal(2025Q3 actual=39) ae 1`, `last (2026Q2=41) ae 1`, `raw 42 ae 2`. The lock was the furthest of the five. GD's 40 sat 2.8 above the band's top (37.24). The post gives the backtest a comparator and the live quarter none.
Defensible version for the post's opening: "One locked quarter so far: off by 8.0 on 40, outside my band. GD's guidance pace missed by 6.2 and last year's same quarter by 1." For the README and dashboard: add the four comparator misses and "outside the band" to the live record.

**BUYSIDE-8. The README never says in a sentence that the same quarter last year won.** `README.md:13`.
Evidence: `grep -n "missed by less" README.md` hits only line 122, on the as-of study. The post, dashboard and note all carry the sentence; the README's bold headline stops after the guidance comparison.
Fix: append to the bold sentence what the other three surfaces say: "Simply repeating the same quarter last year missed by less on average, 4.6." Add at line 43 that both rules of thumb also beat the ratio in the design window.

**BUYSIDE-9. "The registry count" names the scaled estimate; the table's "Raw registry count" is a different row.** `docs/LINKEDIN_POST.md:5`; `README.md:13`, `:19-20`; `report/note.html:53`, `:65`; `docs/INTERVIEW_NOTES.md:7`. Also `README.md:80` and `note.html:71` ("why the registry count differed from GD's count") beside columns of raw registry counts.
Evidence: `grep -n -o -i "the registry count was off[^.]*\."` over the surfaces lists those five lines. README table: "Registry estimate (ratio) | 5.5", "Raw registry count | 6.2".
Defensible version: "the registry estimate was off by 5.5". The sentence is fixed by the project's headline rule and may be checked by the gate, so the main session must decide where the wording is changed.

**BUYSIDE-10. "GD's guidance pace" is the author's construction and the post does not say so.** `docs/LINKEDIN_POST.md:3`, `:5`; `docs/RESUME_BULLETS.md:1` ("vs 6.9 for guidance").
Evidence: `README.md:103` defines it as the full-year outlook less deliveries to date, "spread over the remaining quarters by their usual share". `guid_all.py` printed all 27 rows of `data/guidance.csv`. Four rows carry a quarterly number GD stated, and the rule does not read them (their `outlook` cell is empty): 2021-07-28 "we have planned 32 deliveries in the third quarter and 39 in the fourth"; 2021-10-27 "we will deliver 40 aircraft in the fourth quarter"; 2022-04-27 "we expect to deliver 26 aircraft"; 2022-10-26 "we'll deliver 40 to 41 aircraft in the fourth quarter". In those quarters the pace came out at 32.0, 40.0, 26.7 and 41.0 (`byq.py`), so no figure moves by more than about one jet. The other rows give a full-year number or none. For the live quarter the pace was 33.8, below 2026Q1 (38) and 2026Q2 (41), while the 2026-04-29 row quotes GD's president: "the third and fourth will be our highest, and that's per plan." GD reported 40.
A related wording point at `README.md:39`: "no 2021 call stated a full-year number" is true, but two 2021 calls stated quarterly numbers, so "GD stated a numeric delivery outlook covering 22 of the 26" undercounts what GD said. The fallback values for 2021Q3 and 2021Q4 (32 and 40) equal GD's stated numbers, so the averages do not change.
Defensible version for the post: "against 6.9 for a quarterly pace I derived from GD's full-year delivery outlook".

**BUYSIDE-11. The 5.5 against 6.9 comparison rests on two years.** `docs/LINKEDIN_POST.md:5`; `README.md:13`, `:49-57`.
Evidence: `byq.py` printed, excluding 2023 and 2024, `ratio 6.43 n=18`, `guidance 4.43 n=18`, `seasonal 4.44 n=18`. By year the guidance pace is closer in 2020, 2021, 2022, 2025 and 2026H1; the ratio is closer only in 2023 (3.93 against 14.06) and 2024 (3.04 against 10.97). The year table discloses the rows. No sentence draws the line, and the post's reader never sees the table. Four of those 18 quarters are the 2021 fallback, where the guidance pace is the same quarter last year.
Defensible version, one sentence under the year table: "The registry estimate's lead over the guidance pace comes from 2023 and 2024; in the other 18 quarters it missed by 6.4 against 4.4."

**BUYSIDE-12. The lock was made in a private repository.** `docs/LINKEDIN_POST.md:1`; `README.md:92`.
Evidence: `gh repo view --json visibility` prints `PRIVATE`; `config/calendar.json` reads `"public": false`; `docs/build/DECISIONS.md:203` says the hash was not posted publicly. "Locked ... on GitHub before GD reported" is true by the release's `publishedAt`, but no outsider could have seen it. `gh release view` also prints `immutable: false`, and the release has no asset; the proof is GitHub's timestamp plus the tag.
Defensible version: add to the README's live record "The repository was private when the lock was made; the release time is GitHub's."

**BUYSIDE-13. The preregistration precedes scoring by two minutes.** `README.md:105`; `docs/PREREGISTRATION.md:3`; `docs/INTERVIEW_NOTES.md:7`.
Evidence: `git log --reverse --format='%h %ad %s' --date=iso-local`: `2c62ad3 2026-10-19 11:02:12 Preregister ...`, `48c1ea0 2026-10-19 11:04:28 Score the 26 held-out quarters ...`. First commit 10:08:13; `docs/build/PLAN.md:3` says the critical path was "done 2026-10-19 12:35 EDT". "Held out" and "preregistered" are true as commit order within one sitting, on quarters whose data already existed. A reader will take the words to mean more than that.
Defensible version: "I committed the rules, then scored the 26 quarters in the same session; the split is a discipline of the pipeline, not a wait."

**BUYSIDE-14. The build log shows an AI agent session; the public prose says "I".** `README.md:145` links `docs/build/AIRFRAME_AUDIT.csv`, so `docs/build/` is one click away.
Evidence: `docs/build/DECISIONS.md:41` "The session runs in the agent's desktop app"; `:115` "three checker subagents, nine calls each"; `:105` "Asked the owner how to proceed"; `docs/PREREGISTRATION.md:3` "cut by `tools/preregister.py` from the build prompt, word for word". Against `README.md:145` "I checked 30 airframes against outside sources" and `docs/INTERVIEW_NOTES.md:30` "I stopped, checked the cause". No public surface says how the project was built.
Fix I would make: one sentence in the README saying how it was built and what the owner did himself, and a pass over every first-person sentence so that each is one he can defend aloud. This is a hiring risk, not a numbers defect. `docs/prepub/` on this branch would add to it if merged; I did not read it.

**BUYSIDE-15. Resume bullet 1 gives only the favourable comparison.** `docs/RESUME_BULLETS.md:1`.
Evidence: "off by 5.5 jets a quarter vs 6.9 for guidance, not significant". No 4.6, no live result.
Defensible version: "off by 5.5 jets a quarter vs 6.9 for a guidance-based pace and 4.6 for last year's same quarter; first live lock missed by 8 of 40".

**BUYSIDE-16. The post never puts the miss in scale.** `docs/LINKEDIN_POST.md:1`, `:5`.
Evidence: no typical delivery count and no percentage in the post. `recompute.py`: mean reported 32.69; MAPE 17.915; live `ape` 20.117.
Defensible version: "off by 5.5 jets a quarter on average, about 18%, when GD delivers about 33".

**BUYSIDE-17. The workbook cannot show the headline comparison or the live result.** `output/gd_gulfstream_model.xlsx`, sheets `Summary`, `Quarters`, `Live`, `About`.
Evidence: `wb.py Summary` prints four rows: "MAE ratio", "MAE raw", "MAE seasonal", "MAE last". `Quarters` row 1 has no guidance column, though `About!A8` says the quarters are "scored against seasonal, last-quarter and GD guidance baselines". `Live` holds the lock's inputs and band and no reported count, miss or band result. `Quarters` ends at 2026Q2.
Fix: add the guidance column and a Summary row for it, and three cells on `Live` for GD's count, the miss and inside or outside the band.

**BUYSIDE-18. The README opens as if the estimate works ahead of the release, and its live record is 90 lines down.** `README.md:3`, `:90-93`.
Evidence: "I estimate how many Gulfstream jets General Dynamics (GD) will report delivering each quarter". The site's own description is the careful version: "A test of whether FAA aircraft registrations can estimate the Gulfstream deliveries General Dynamics reports". The first live result appears only at line 92, after the stale image at line 5.
Defensible version for line 3: "I test whether FAA aircraft registrations can estimate the Gulfstream deliveries GD reports ... The first locked quarter, 2026Q3, missed by 8.0." Move the Live record above Results, as the post does.

**BUYSIDE-19. No "not investment advice" line on the README, the post or the workbook.**
Evidence: the `grep` in question 2 finds the disclaimer only at `report/note.html:57` and `site/index.html:106`. The README carries a revenue method (`README.md:109`) and links the note and model.
Fix: the note's own sentence, "Student research project. Not investment advice. No rating or price target.", at the foot of the README and on the workbook's About sheet.

### S3, minor

**BUYSIDE-20. The README's account of who locks does not match the one lock.** `README.md:107`, `:156`. `git log --format='%h | %an' 0c7e8ab -3` shows `github-actions[bot]` authored the 2026-10-29 snapshot, the lock commit and its record; `gh release view --json author` agrees; `git log --format='%an' | sort | uniq -c` prints 45 runner commits of 110. The README says the FAA's blocking "has refused GitHub's runners" and that "my Mac ... locks the estimate". Fix: say the 2026Q3 lock came from the workflow's run.

**BUYSIDE-21. The PDF and `note.html` disagree, and the byline is out of date.** PDF text line 384: "the newest dated 2026-10-30"; `report/note.html:108`: "the newest dated 2026-11-11". The daily commit edits `note.html` (`git show --stat 36fed31`) and the PDF's file date is Oct 30.

**BUYSIDE-22. "Because it is what the street anchors on."** `docs/INTERVIEW_NOTES.md:18`. No source, and the pace is the author's construction. Defensible: "Because it is the only delivery number GD itself gives. I had no consensus data."

**BUYSIDE-23. Two inverse coverage measures in one README.** `README.md:69` uses GD deliveries per registry event (mean 1.18); `README.md:142` uses registry events per delivery (0.52 to 0.80). `checks2.py` confirmed both (63/121 = 0.521, 117/147 = 0.796). Pick one.

**BUYSIDE-24. The dashboard's lead has no count and no subject, and the card's large figure is still the estimate.** `site/app.js:92-94`: "Off by 5.5 jets a quarter on average, when GD delivers about 33" names neither the estimate nor the 26 quarters; the tiles' title (`index.html:61`) gives no count either. `app.js:122`: the card's large figure stays "32.0 deliveries, estimated" with GD's 40 in a small row. The stale labels on the same card are in BUYSIDE-4.

**BUYSIDE-25. Label drift.** "nowcast" survives in the repository name, the release title ("Locked nowcast 2026Q3"), and workbook labels (`Live!A9-A11`, `Segments!A14-A16`), while the prose says "estimate" and "tracker". The same model is "Registry estimate (ratio)", "Registry estimate", "Ratio", "MAE ratio". The defense rule is "seasonal naive with drift" (`README.md:109`), "drift baseline" (note) and "growth rule" (`app.js:391`). The note's Exhibit 5 heads columns "Seasonal" and "Last".

**BUYSIDE-26. `nowcast_path.png` source line.** It plots snapshots to 2026-10-30 and cites "FAA aircraft registry snapshot 2026-10-19", and labels "GD reports 2026-10-30" in the present tense. Not linked from the README or the note.

**BUYSIDE-27. The position disclosure dates from the build.** `report/note.html:57` "The author holds no position in General Dynamics." `docs/build/DECISIONS.md:39` records it as a chat answer on 2026-10-19. The owner should confirm it is true on the day of the post.

## Also report

**Figures that differ between two surfaces**

- 31.1 with band 20.4 to 36.4 (`dashboard.png`, `INTERVIEW_NOTES.md:27`) against 32.0 with band 21.2 to 37.2 (README text, post, note, `data.json`).
- "Locks the evening of 2026-10-29" (`dashboard.png`) against 01:51 ET on 2026-10-29 (README, note, release).
- Newest snapshot 2026-10-30 (PDF) against 2026-11-11 (`note.html`).
- "Data as of 2026-10-29" (note byline) against a result from 2026-10-30 in the same note.
- No backtest figure differs between surfaces.

**Figures I could not trace to `results/` or `results/live/`**

- The defense study's percentages at `report/note.html:82` (9.9%, 7.3%, 6.5%, 9.4%, 5.8%, 6.0%). They are not in `results/`, and the study's page loaded for WebFetch without its figures.
- "75 successful captures" at `README.md:113`. Not checked.
- Traced elsewhere, not in `results/`: 0.52 and 0.80 (`data/processed/`), 203 and 63 (same), the as-of rows (`results/exploratory/asof.csv`), 1.18 and 0.69, 0.69, 0.72 (`metrics.json`).

**Overclaims**

- "before I computed anything for a later quarter" (`README.md:105`): BUYSIDE-6.
- "I estimate how many ... GD will report" (`README.md:3`): BUYSIDE-18.
- "nowcast" in the repository name, release title and workbook: BUYSIDE-25. The evidence carries "estimate locked before the release", once, and a miss.
- "before GD reported" in the post is supported by the timestamps. It is silent on the repository being private: BUYSIDE-12.
- The framing sentence about a registry copy that had time to fill in is present, in the project's words or close, on the post, README, dashboard, note, interview notes and error analysis. I found no sentence saying the project counts jets before GD reports them.

**What I could not check**

- The filing's acceptance time on SEC itself. The session refused my `urllib` request to `sec.gov`; I used the cached folder listing in `data/raw/sec/`.
- The rendered dashboard, and any deployed copy (there is none).
- The workbook's values. It stores formulas with no cached results; I read formulas and labels and did not evaluate them, so I did not confirm that `Summary` returns 5.5 and 4.6.
- The repository link as an outsider.
- The 30-airframe audit, the claims in `report/claims.json`, and whether GD changed its outlook on the 2026-10-30 call (`data/guidance.csv` ends 2026-07-29; the 2026Q4 pace of 41.0 in `data.json` is not displayed).

## GO or NO-GO

**NO-GO as written.** The post's numbers are right and its order is honest. It cannot go up while its first link is dead, and while the README image, the note, the dashboard's revenue panel and the owner's own interview notes describe the lock as still to come.

The three things I would fix first:

1. **Bring every surface to the scored state of 2026Q3, then bring the dashboard up.** Retake `dashboard.png`; rewrite the note's key points 2 and 3, Exhibit 8 and the "watches" section; fix the dashboard's revenue panel; rewrite `INTERVIEW_NOTES.md:9`, `:27` and `RESUME_BULLETS.md:2`; enable Pages, run the workflow and read the live page (BUYSIDE-1 to 5).
2. **Say the whole live result and the whole backtest result wherever either appears.** "Outside the band" and the comparator misses beside the 8.0; the same-quarter-last-year sentence under the README's bold headline and in the resume bullet; "registry estimate" in place of "registry count" (BUYSIDE-7, 8, 9, 15).
3. **Correct the three sentences that claim more than the record shows.** `README.md:105`; the undefined "GD's guidance pace" in the post; and the silence on the private lock and on how the project was built (BUYSIDE-6, 10, 12, 13, 14).
