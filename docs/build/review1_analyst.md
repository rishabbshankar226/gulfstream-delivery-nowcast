# Review round 1: analyst

Reviewer: a fresh reviewer who built nothing here, reading as an aerospace and defense equity research associate with five minutes. Reviewed at commit `062e00e` (2026-10-19 12:00 CDT). `output/GD_research_note.pdf` sha256 `00bdbbc08616318aa6d8bb99c4e18fb580b7ef7331d2911beb6ce006aede0b5a`, 7 pages. The PDF was rebuilt at 11:53 and again at 12:00, after the page images in `.build/shots/note/` (11:39), so I rendered the current PDF myself with PDFKit and read that. Where a page number is given it is the current PDF's. Line numbers in `report/note.html` are the generated note. Its source text is in `src/gdn/note.py` at the line given.

## Verdict

The note reads like a careful student note, and it follows the headline rule. Nowhere does it say the project counts jets before GD reports them. An analyst would still take away three wrong impressions in five minutes:
- the registry beats the obvious baselines (it does not);
- a ~0.7 coverage ratio is "no drift" (the preregistered check cannot see that direction);
- Gulfstream is heading for an 18% Aerospace revenue drop in 2026Q3 (that figure comes from a services-inclusive multiplier, and it is never set against GD's own outlook).

None of these is blocking under the preregistration. All three are major.

## The three weakest things

### A1. Coverage has fallen to about 0.7, the preregistered check looks only the other way, and used jets explain part of the fall (major)

- **Where:** note p3, Exhibit 6 caption, `report/note.html:72` (from `src/gdn/note.py:337`); dashboard `site/app.js:363`; `docs/INTERVIEW_NOTES.md:13`; the Coverage and Used jets limitations, note p6, `report/note.html:92-93`.
- **Claim:** note: "Coverage drift: no quarter from 2025Q3 to 2026Q2 sits above the mean plus two standard deviations of GD deliveries per registry event." Dashboard: "No quarter from 2025Q3 to 2026Q2 shows the registry counting unusually few jets per GD delivery." Interview notes: "gives a number that runs above or below GD's count by a fairly steady ratio".
- **Evidence:**
  - `results/metrics.json` `holdout.coverage_ratio` gives a mean of 1.182 and an sd of 0.352. The last three quarters are 2025Q4 0.692, 2026Q1 0.691 and 2026Q2 0.719, about 1.4 sd below the mean. Only 2022Q1 (0.658) is lower in the whole series. The series runs from 2.33 (2016Q1) to 0.72 (2026Q2). The flag tests only the upper tail, so it cannot fire on this drift.
  - From `data/processed/registry_quarterly.csv` against `gd_deliveries.csv`, large cabin: 2025 has 167 registry events against 136 delivered, and 2026H1 has 97 against 66.
  - Part of the cause is used jets that the one-year bound lets through. In `docs/build/AIRFRAME_AUDIT.csv`, the domestic-sale stratum has 5 of 10 rows marked `no`, and 4 of those 5 are used jets read as new deliveries (G450 4122 built 2008; G550 5340 and 5269; G-1159A 466 built 1985).
  - In `data/processed/serials.csv`, the E1 events of recent quarters include models out of production for years: G-IV, G-V, G-1159A, G150 and G550, built 1984 to 2018. That is 2 of 38 events in 2025Q3, 5 of 65 in 2025Q4, 7 of 55 in 2026Q1, 5 of 57 in 2026Q2 and 3 of 41 in 2026Q3.
  - Counting every airframe whose `year_mfr` is more than one calendar year before its event, the share is 46 of 215 in the four trailing quarters against 6 of 41 in 2026Q3.
  - Python over `serials.csv`: `[r for r in ev if r['year_mfr'] and int(r['year_mfr'])<int(r['e1'][:4])-1]`.
  - The positive holdout bias (+2.24) and the 2025Q4 miss (58.4 against 45) fit this. The note's Used jets bullet covers only jets "with no airworthiness date or year of manufacture". It leaves out the re-import path, where a fresh US airworthiness date passes the bound, which the audit found in practice.
- **Fix:**
  - Next to the flag sentence, print the last four ratios and their distance from the mean. Say plainly that the preregistered flag tests only the upper side, and that recent quarters sit well below the mean.
  - Rewrite the Used jets limitation to name the re-import path, and give the out-of-production counts above.
  - Replace "fairly steady ratio" in `INTERVIEW_NOTES.md:13` with the drift as measured (about 1.5 to 2.3 in 2016 to 2018, about 0.7 in 2025Q4 to 2026Q2).
  - Optionally add `results/exploratory/used_jets.{csv,md}`, labelled as tried after the fact. My recount drops airframes built more than a year before their event, which takes holdout MAE from 5.52 to 4.59 but design MAE from 5.47 to 5.72, so the design window would not have chosen it. The 2026Q3 estimate moves from 31.1 to 33.8. Dropping only the out-of-production models moves it to 31.6.
  - Change no definition and do not touch the headline.

### A2. The cover's 2026Q3 numbers come with no comparator, and the $2.6B overstates the swing (major)

- **Where:** note p1, key points 2 and 3, `report/note.html:54-55` (from `src/gdn/note.py:250`); Exhibit 8 on p4 and Exhibit 9 on p5 (`report/note.html:79`); the "What the street watches" bullets on p5.
- **Claim:** "My registry estimate for 2026Q3 is 31.1 Gulfstream deliveries, with a past-miss band of 20.4 to 36.4." And: "that estimate implies $2.6B of Aerospace revenue for 2026Q3, against $3.2B a year earlier."
- **Evidence:**
  - The note never prints the 2026Q3 guidance pace or the same-quarter-last-year figure. The dashboard does: "GD's guidance pace 33.8 deliveries" and "Same quarter last year 39 deliveries". I reproduced the 33.8: 160 minus 79 year-to-date, times the 2023 to 2025 Q3 share, 94 / (94 + 131). The 39 belongs to the model with the lowest held-out MAE (4.6).
  - The implied Q4 is never stated. With GD's ~160 outlook, 79 delivered in H1 and 31.1 in Q3, Q4 would need 49.9 deliveries, more than the 47 of 2024Q4, the highest quarter in `gd_deliveries.csv`. With GD's ~$13.8B Aerospace outlook, H1 Aerospace revenue of $6,804M (`segments.csv`) and $2,641M in Q3, Q4 would need about $4.36B, against a series high of $3,788M (2025Q4).
  - Exhibit 8 carries Aerospace at $2.6B (−18.3%) from deliveries and $3.6B (+12.3%) from drift, a $1.0B gap that the note leaves unreconciled. The cover shows only the $2.6B.
  - The $85M per delivery is total Aerospace revenue (Gulfstream services and Jet Aviation included) divided by deliveries, so every missing jet removes $85M of services as well. The note's own label says "services included". The −18% therefore overstates how far revenue moves with deliveries.
  - The registry snapshot is 15 days after the quarter end (2026-10-04 to 2026-10-19). `results/exploratory/asof.md` tested only captures 23 to 29 days after quarter end, and its one Q3 (2025Q3) missed low by 6.6 and fell outside its band (`Inside: no`).
  - Exhibit 9 runs only ±4 (27.1 to 35.1). That covers neither the band's low end (20.4) nor the 39.
  - The Aerospace operating earnings use the TTM margin of 13.8%. H1 2026 ran 14.7% ((493 + 510) / (3,279 + 3,525)), the same as GD's 14.7% guide for the year.
- **Fix:**
  - On the cover, put the 31.1 beside the guidance pace (33.8) and the same quarter last year (39), and add one sentence on what Q4 would then need (about 50 deliveries against a series high of 47).
  - Take the $2.6B off the cover, or show both Aerospace rows there.
  - In Exhibit 8, either split Aerospace into aircraft manufacturing and services from the 10-K's revenue by product line and scale only manufacturing, or keep the mechanical row and add a services-held-flat row.
  - Widen Exhibit 9 to cover the band (20 to 40) and mark the 33.8 and 39 rows.
  - In the live-quarter paragraph, say that the snapshot is younger than any archived copy the project tested.

### A3. The cover names only the baseline the registry beat, not the one that beat it (major)

- **Where:** note p1, key point 1, `report/note.html:53`; the p2 callout, `report/note.html:65` (both from `src/gdn/note.py:88`).
- **Claim:** "Over 26 held-out quarters the registry count was off by 5.5 jets a quarter on average, against 6.9 for GD's guidance pace. The difference is not statistically distinguishable."
- **Evidence:**
  - `results/metrics.json`: holdout MAE is 4.615 for seasonal against 5.523 for ratio, `rel_mae.seasonal` is 1.197, and `tests.seasonal` is 11 wins and 15 losses. In the design window ratio scored 5.47, against 5.0 for seasonal and 3.83 for last. So ratio was the best model in neither window.
  - `docs/LINKEDIN_POST.md:5` ("Simply repeating the same quarter last year did a little better, at 4.6"), `docs/INTERVIEW_NOTES.md:7` and the dashboard hero ("Simply repeating the same quarter last year missed by less, 4.6") all say this. The note's cover and callout do not, so the PDF, the document an analyst reads, is the one place it is left out.
  - The 6.9 also includes four quarters (2021Q1 to Q4) where "guidance" is the seasonal fallback. On the 22 sourced quarters, `results/holdout.csv` gives guidance 7.36, ratio 5.25 and seasonal 4.64. The note prints guidance's 7.4 (p2) but not ratio's figure on the same quarters.
- **Fix:**
  - Add to key point 1 and to the callout, after the prescribed wording: "Simply repeating the same quarter last year missed by less, 4.6." The headline rule does not forbid adding this, and the other three documents already do.
  - Next to "missed by 7.4 aircraft on average", add "against 5.3 for the registry estimate and 4.6 for the same quarter last year on those 22 quarters."

## Claims that outrun the evidence

| id | where | severity | evidence | fix |
|---|---|---|---|---|
| C1 | dashboard, `site/app.js:315`; phone shot, "On Gulfstream's own registration" | major | "270 in all, about 8 quarters of deliveries at GD's typical 33 a quarter." In `serials.csv`, 208 of the 270 held airframes with no event have no `first_airworthiness`. Nine first flew airworthy before 2016 (1985 to 2015), and the list includes G-IV, G-V, G450 and G550. 77 are G800s, a model that began deliveries only in 2025Q3. These are registrations, not a work-in-progress count. | Drop the "8 quarters of deliveries" comparison, or count only airframes with an airworthiness date in the last 12 months and call the rest "registrations reserved by Gulfstream". |
| C2 | note p3, `report/note.html:71` (from `src/gdn/note.py:327`) | major | "archived registry copies ... missed by less than the finished copy, because they read the lag quarters from the same unfinished file." `results/exploratory/asof.csv` shows the archived copies held **more** lag-quarter events than the 2026-10-19 copy in all four quarters: 146 against 63 (2017Q1), 184 against 176 (2025Q3), 197 against 192 (2026Q1), 206 against 203 (2026Q2). The 2017-04-27 copy counted 40 events in 2017Q1 against 19 today. The copies were not unfinished: the file loses first-owner events over time (DECISIONS.md:103). The same row's `Inside` is `no` for 2025Q3, and the note does not say that 1 of 3 held-out as-of quarters fell outside its band. | State the counts. Say that later copies lose events to resales and renewals as well as gaining late postings, so "had months or years to fill in" holds for recent quarters but not old ones. Add "its band held 2 of 3". |
| C3 | note p2, `report/note.html:65` and 68; dashboard `site/app.js:14` | minor | `app.js:14`: `guidance: "GD's own guidance pace"`. The figure is the author's spread of GD's full-year outlook by 2023 to 2025 seasonal shares (§3.4). GD issues no quarterly pace, and 4 of 26 quarters are seasonal fallback. Exhibit 5 (p3) shows 2021 guidance at 4.5, identical to seasonal, without marking it. | On first use, write "GD's full-year outlook, spread by seasonal share". Drop "own". Footnote the 2021 row of Exhibit 5 as fallback. Mark the 2026 row "2 quarters". |
| C4 | note p6 limitations, `report/note.html:88` (from `src/gdn/note.py:502`) | minor | "Many G280s, built by IAI in Israel, leave no Gulfstream record." Registry mid against GD mid by year: 2022 25/24, 2023 20/22, 2024 22/18, 2025 25/22, 2026H1 15/13. Since 2022 the registry counts as many mid-cabin events as GD delivers, or more. DECISIONS.md:103 traces the early shortfall to current-certificate attrition, not exports. | Say "G280s exported without a US registration would leave no record; since 2022 the registry's mid-cabin count has matched or exceeded GD's", or cut "Many". |
| C5 | note p7, sources, `report/note.html:109` (from `src/gdn/note.py:484`) | minor | "snapshot 2026-10-19; daily snapshots since." `results/live/2026Q3_path.csv` has one row (2026-10-19), and the dashboard says "One snapshot so far". | Print the count of snapshots ("1 snapshot to date"), or drop "daily snapshots since" until there are any. |
| C6 | note p1 key point 2; dashboard; `docs/LINKEDIN_POST.md:1`; `docs/INTERVIEW_NOTES.md:9,27` | minor | "GD reports on 2026-10-30" has no citation. The only source is the 2026-07-29 call (`data/raw/sources/calls/2026-07-29-fool.html`): "we expect to hold our Q3 earnings call on Friday, October 30". The lock fires off `config/calendar.json`. | Add a `call` claim for the date and write "GD expects to report on 2026-10-30". |
| C7 | note p2, `report/note.html:68` | minor | "The registry estimate's past-miss band held GD's count in 18 of 26 held-out quarters (69.2% ...)". Nothing says the band is P10 to P90, so nominally 80%. Without that a reader cannot tell it under-covers. | Add "against a nominal 80%". |
| C8 | `docs/LINKEDIN_POST.md:3` | minor | "checked it on 26 past quarters it never saw". The rule never saw them, but the registry copy it reads (2026-10-19) postdates all 26 quarters and GD's counts for them. The prescribed caveat appears two sentences later. | "checked it on 26 past quarters held out from the rule-setting". |
| C9 | note p6 limitations, `report/note.html:95` | minor | "in 10 of 30 airframes checked ... (33.3%)". `AIRFRAME_AUDIT.csv` is stratified (10 domestic, 10 export, 5 E2-only, 5 bound-removed). The domestic stratum is 5 of 10 `no`. Every audited event is dated 2016 to 2018, so the audit says nothing about the held-out or live quarters. | Give the rate by stratum, and say that the audited events all fall in 2016 to 2018. |
| C10 | note p2 product cycle, `report/note.html:62`; `report/claims.json` (text of `pc-g300-entry-timing`, and of `pc-g400-timing-update` at line 148) | minor | "the final G280 ought to deliver in the second quarter of next year ... late '27 or early '28"; "whipped up its efforts on the G400". These are transcript words inside a paraphrase, and "next year" is relative to a 2026-07-29 call. | Write "the second quarter of 2027", "late 2027 or early 2028" and "stepped up". |
| C11 | note p7 sources 1-3, 5, 7, 8 | minor | "GD SEC filing, https://sec.gov/Archives/edgar/data/40533/000004053326000006". No form type or date, and a folder rather than a document. An analyst cannot tell the 10-K from an 8-K. | Name the form and period, e.g. "Form 10-K for 2025, filed 2026-02-xx", and link the document. |

## Other weaknesses (not claims)

| id | where | severity | evidence | fix |
|---|---|---|---|---|
| O1 | workbook, `Summary!A1:C5`, `Live!A1:B15` | minor | Summary holds ratio, raw, seasonal and last only. Neither the headline comparator (guidance, 6.9) nor the 2026Q3 guidance pace (33.8) is anywhere in the workbook, so the note's central comparison cannot be reproduced or flexed there. `Live!B7`/`B8` are typed (187, 28) although they equal `SUM(Quarters!F40:F43)` and `G40:G43`. | Add a guidance-pace column to Quarters, a guidance row to Summary and the 2026Q3 pace to Live, using only the allowed functions. Make B7 and B8 `SUM` formulas if the spec allows. Put "$M" in the Segments headers and on `Segments!B13`. |
| O2 | `.build/shots/note/page-01.png` to `page-07.png` | minor | Dated 11:39, before the 11:53 and 12:00 PDF rebuilds. The images lack the as-of sentence (p3) and the Audit limitation (p6), and show "Registry est mate (ratio)" in the Exhibit 4 legend, a rasterising glyph drop that is absent from the current PDF and from `output/charts/track_record.png`. | Regenerate the page images in the same step that writes the PDF, or have the gate compare their timestamps. |
| O3 | note p5-p6, Risks | minor | All eight risks are generic 10-K risk factors (customer defaults, FX, fixed-price contracts, government spending). The print-specific risks the note already cites elsewhere (the Israel supplier delays on the G280, the G280-to-G300 production break, G700/G800 mix) sit under other headings. | Lead Risks with the two or three Gulfstream risks for the 2026Q3 print, each as a claim. Keep at most two of the 10-K risks. |
| O4 | note p4, Exhibit 8 defense rows | minor | Marine at $4.8B (+16.6%) is not set against GD's 2026 Marine outlook of about $18B (claim `os-marine-outlook`). H1 Marine was $9,003M, which implies about $4.5B a quarter for H2. | Add one line comparing each segment's drift estimate with GD's stated 2026 outlook, where one exists. |

## Checked and clean

- The workbook inputs match `gd_deliveries.csv`, `registry_quarterly.csv` (E1) and `segments.csv` for all 42 quarters and 32 segment cells. Recomputing its formulas gives design MAE of 5.47, 9.42, 5.00 and 3.83 and holdout MAE of 5.52, 6.19, 4.62 and 8.81, matching Exhibit 11 and `metrics.json`.
- Live: 35 × 140 / 187 + 6 × 23 / 28 = 31.13. Revenue per delivery is $84.8M, Aerospace from the estimate is $2,641M, and Aerospace operating earnings from it are $366M.
- Checked as stated: Aerospace margin of 14.5% in 2026Q2 and 14.7% for H1; Marine margins of 7.1, 7.2, 7.3 and 7.3%; Aerospace coverage of 1.73 years; 79 deliveries in H1; the sign-test p of 0.423 for 14 of 26; the 2026Q3 guidance pace of 33.8.
- The claims I checked against their quotes (`os-*`, `pc-*`, `risk-*`) say no more than the quote. The prescribed framing sentence appears on the cover, in the callout and in the post.

## Findings by severity

- **Blocking:** none. The headline rule is followed, and nothing says the project counts jets before GD reports them.
- **Major:**
  - A1, coverage drift and used jets;
  - A2, the cover's 2026Q3 numbers lack comparators and the $2.6B overstates the swing;
  - A3, the cover omits that the same-quarter baseline beat the registry;
  - C1, the "270 jets, about 8 quarters of deliveries" line on the dashboard;
  - C2, the as-of mechanism stated backwards.
- **Minor:** C3 to C11 and O1 to O4.
