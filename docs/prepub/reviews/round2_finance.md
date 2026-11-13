# Round 2 review: finance reader (`round2_finance`)

Reviewer role: sell-side A&D analyst covering GD, and a buy-side PM reading student work.
Tree read: `~/gdn-prepub/round2_clean`. Date of the read: 2026-11-11.
Scratch scripts and fetched SEC files: `~/gdn-prepub/agents/round2_finance/`.

## Verdict

**NO-GO as it stands.** Two S1, both sentences in the interview notes that the project's own files contradict. The notes say the registry "had the quarter's jets in time", and the lock's airframe table shows it did not (FINANCE-1). They also say "Every number in it traces to a filing or a registry file", and the README says otherwise (FINANCE-17). Each fix is a sentence or two. With FINANCE-1, FINANCE-17, FINANCE-2, FINANCE-3 and FINANCE-5 fixed I would say GO: the lock is verifiable, every SEC figure I checked is right, and the null result and the live miss lead on four of the five first screens.

Findings: **S1: 2. S2: 9. S3: 6.**

Three things to fix first:

1. FINANCE-1, FINANCE-17 and FINANCE-2. Take out "the registry had the quarter's jets in time" and say what the 42 events were: 37 in-production models and 5 older types. Correct the sourcing sentence.
2. FINANCE-3 and FINANCE-4. On the live quarter, say that 33.8 is my split of "about 160" and what a plain reading of GD's words gave. Put "my construction" on the dashboard, the workbook and the chart legends.
3. FINANCE-5, FINANCE-7 and FINANCE-8. Make 32.0, 40, 8.0 and 20.1% reconcile. Put GD's reported figure beside every 2026Q3 estimate. Give the workbook's Summary sheet the two plain result lines the other first screens have.

## What I ran

| Check | Script or command | Result |
|---|---|---|
| Lock file hash | `integrity.py` | `predictions/2026Q3.json` sha256 `3c4cdbd0...6f23`, equal to `results/live/2026Q3_lock.json` and README:106 |
| Lock release | `gh release view lock-2026Q3 --repo ...` | tag `lock-2026Q3`, author `github-actions[bot]`, published `2026-10-29T05:51:24Z`, notes `sha256 3c4cdbd0...6f23` |
| GD's 8-K time | `sec_fetch.py 0000040533-26-000036` | filing date 2026-10-30, accepted `2026-10-30 08:09:27` |
| Lock before release | `derived.py` | lock precedes acceptance by `1 day, 6:18:03` |
| Note stamp | `integrity.py` | `sha256(report/note.html)` equals `output/GD_research_note.inputs.sha256`; site PDF bytes equal output PDF |
| Backtest figures | `recompute.py` over `results/holdout.csv` | every headline figure reproduced (list under "What is right") |
| Workbook | `wb.py`, `wb_full.py`, `wb_eval.py` | 42 rows of typed inputs, 0 mismatches against the CSVs; formulas evaluated by hand give the same figures as the other surfaces |
| Daily snapshots | `daily.py` | 2026Q3 window count 41 to 2026-10-26, 42 from 2026-10-27 to 2026-11-11 |
| Lock events | `q3events.py`, `q3odd.py`, `mix.py` | 42 events: 37 in-production models, 5 older types |
| Pace | `pace_alt.py` | preregistered pace reproduced to 7e-15 |
| Segment arithmetic | `derived2.py` over `data/processed/segments*.csv` | shares, margins, drift figures and Exhibit 8 misses reproduced; reported four-segment revenue 14566, earnings 1580 |
| SEC figures | `sec_fetch.py`, `sec_doc.py`, `sec_parse.py`, `sec_text.py` | 8 filings fetched with the declared header; table in Q8 |
| Call quotes | WebFetch, two Motley Fool transcripts | 2026-07-29 and 2023-07-26 quotes confirmed |
| PDF | Read tool, pages 1 to 7 | 7 pages, disclaimer footer on each. The venv has no pypdf, so text came from `report/note.html` (`note_text.py`) |
| Charts | Read tool, all five PNGs in `output/charts/` | axes, legends and source lines present; the three backtest charts stop at 2026Q2; `nowcast_path.png` shows the lock, the pace and GD's 40 |

## The nine questions

### 1. Is the delivery count GD's count?

No, and the project does not say it is. It counts registry events that overlap GD's count.

- `mix.py`: trailing four quarters, 215 events against 163 GD deliveries; 176 of the 215 are in-production models (G400, G500, G600, G700, G800, G280) and 39 (18.1%) are older types. That 39 is a count by model name. It includes G650 and G650ER events whose ages I did not print, so it is not a count of used jets.
- `mix.py`: the 2026Q3 lock, 42 events against 40 GD deliveries; 37 are in-production models (31 large, 6 mid, against GD's 35 and 5) and 5 are older types.
- GD's count is new aircraft. 10-K 0000040533-26-000006: "the number and mix of new aircraft deliveries".

What each surface says:

| Topic | README | Note | Dashboard | Post | Workbook |
|---|---|---|---|---|---|
| Green against completed | README:145, with the 10-K quote (confirmed: "generally upon delivery and acceptance by the customer of the fully outfitted aircraft") and the 2016 restatement | Not stated | Not stated | No | No |
| Gulfstream's own fleet, test and demo aircraft | README:145, GD's "about 11 aircraft" for 2021 (quote not checked by me) | No | Pipeline panel, 258 jets, labelled as not a count of jets awaiting delivery | No | No |
| Leasing arm | README:159, sized: four registrations, 2020Q4 and 2025Q4 | No | No | No | No |
| Special mission and military | README:154 and note Limitations, no size | No size | Link to README only | No | No |
| G280's Israeli build | README:111 and :144; note product cycle; interview notes | Yes | Method step 1 does not name it | No | No |
| Used jets | README:157, sized: 246 of 1,251 events (19.7%), 5 of the 42 lock events | Sized, 246 of 1,251 | Link only | No | No |
| Exports with no US record | README:152, mid-cabin yearly match only | Same | Link only | No | No |

I reproduced the sizes: 1,251 events, 246 at least three years old (19.7%), 76 with no year, 386 airframes with no bound supplying 75 events (`misc.py`). Mid-cabin by year, GD against registry: 2022 24 and 25, 2023 22 and 20, 2024 18 and 22, 2025 22 and 25.

Gaps: the lock quarter's composition by model is nowhere (FINANCE-2). Military and export gaps carry no size on any surface (FINANCE-12). The dashboard states none of it on the page and links to the README (acceptable for a dashboard).

### 2. Is the guidance pace built the way the street would build it, and is it named honestly?

Built: not the way the street would. The pace takes the latest full-year number, subtracts deliveries to date and spreads the rest by each quarter's share over the three prior years (`src/gdn/model.py:119-133`; no look-ahead, and I reproduced it to 7e-15). A covering analyst overlays what management says about cadence. For Q4 the two are the same. For Q1 to Q3 they can differ a lot, and for the live quarter they did (FINANCE-3).

Named: README:23 and :117, note.html:68, the post ("A pace I derived from GD's own full-year outlook") and INTERVIEW_NOTES:18 say it is the author's construction. The dashboard, the workbook's Summary and Quarters sheets and the chart legends print "GD's guidance pace" or "GD guidance pace" with no such words (FINANCE-4). `grep -n -i "construction\|GD publishes\|not a figure" site/index.html site/app.js` returns nothing.

GD's own stated plan: README:49, INTERVIEW_NOTES:18 and `results/exploratory/sensitivity.md` give it (6.0 against 6.9, registry closer in 12 of 26; reproduced: `plans variant MAE 6.0184 closer 12 of 26`). The note and the dashboard do not (FINANCE-4). I confirmed one of the six plan quotes at source (2023-07-26: "We now expect to deliver 27 aircraft in the third quarter"). I could not check that the list of six is complete.

### 3. Is the Aerospace revenue estimate labelled as mechanical everywhere, and is GD's reported figure beside every 2026Q3 estimate?

Mechanical label: yes on every appearance I found. README:123; note key point 3, Exhibit 8 footnote, Exhibit 9 title, Exhibit 11 footnote; dashboard "What it means for GD" sub-head; workbook About A10, Segments A20, Sensitivity A12; INTERVIEW_NOTES:27.

GD reported beside every estimate: no (FINANCE-8). Present in the post, README, dashboard live panel and segment table, note key points and Exhibit 8, workbook Live sheet. Missing in note Exhibits 9, 10 and 11, the workbook's Segments and Sensitivity sheets and the dashboard's sensitivity table.

### 4. Does the note's defense half overreach? Do the risks read as generic 10-K text?

Overreach: no in words. note.html:85 says "Applying that study to GD is an assumption: it did not test GD", and Exhibit 8 shows the three defense misses (Marine -3.7%, Combat -2.6%, Technologies -8.2%; I recomputed each from SEC figures). But the six study figures in that paragraph have no source record in this repository (FINANCE-9), and Exhibit 10 prints 2026Q3 defense estimates with no reported figure (FINANCE-8).

Risks: yes, generic. Seven of the eight bullets are 10-K risk-factor paraphrases that fit any year ("GD says ..."). Only the tariff bullet has a number (30 basis points, confirmed in the 10-K). The risks a GD analyst would list for Gulfstream are elsewhere in the note or absent: the G280 production break (in product cycle and Limitations), G400 timing, the G700 and G800 ramp, book-to-bill. FINANCE-10.

### 5. After reading the post, what would I do with this?

Nothing with the stock, and the project gives me no reason to. The tracker lost to "same quarter last year" on 26 quarters and missed its one live quarter by 8. As a PM I would file it as an honest negative result on registry data.

- No rating, target or initiation word on any surface. `grep -n -i -w "buy|sell|hold|overweight|underweight|outperform|initiat*|price target|rating|upside|downside|alpha|edge|signal|trade|trading|consensus|street"` over the post, README, dashboard files, interview notes, resume bullets and note text returns only disclaimers, "I had no consensus data" and "Why no price target or rating?".
- Disclaimer: post line 11; README:15 and :182; dashboard eyebrow and footer; note cover box and the footer of all 7 PDF pages; workbook About A3 only (FINANCE-15).
- Closest thing to a signal: the dashboard panel titled "What it means for GD" (FINANCE-13) and a public `site/data.json` that updates daily with a part-quarter 2026Q4 count. README:107 says that count "is not an estimate of the quarter", and `app.js:109-112` keeps the scored 2026Q3 on screen until 2026Q4 locks, so no pre-release number is drawn. Good.

### 6. Does the project say plainly that the simplest baseline beat it?

| Surface | Says it | Where |
|---|---|---|
| Post | Yes | line 6: "Simply repeating the same quarter last year missed by less on average, 4.6." |
| README first screen | Yes | README:8: "Simply repeating the same quarter last year missed by least. No test finds the registry estimate better than a baseline." |
| Dashboard first screen | Yes, in the smaller line under the lead | `app.js:99-101`, seen in `output/charts/dashboard.png` |
| Note first page | Yes | key point 1 |
| Workbook Summary | No | A8 says only "The lowest holdout figure in column C is the baseline that missed by least" (FINANCE-7) |

Every surface names the guidance pace first (5.5 against 6.9), which is the comparison the estimate wins on the average, and the winning baseline second. That order is preregistered (PREREGISTRATION.md:52), and the winner follows in the next sentence each time, so I do not call it a finding.

### 7. Does the first live quarter appear as early and as plainly as the backtest?

| Surface | Verdict | Detail |
|---|---|---|
| Post | Yes | It is the first line, with the pace (6.2) and last year's quarter (1) beside it |
| README first screen | Yes | README:6 comes before the backtest paragraph |
| Dashboard first screen | Mostly | The hero text is backtest only. The panel under it reads "2026Q3 · Scored: missed by 8.0, outside the band", but its biggest figure is the missed 32.0 and "GD reported 40 deliveries" is the seventh fact (FINANCE-13) |
| Note first page | Yes | key point 2, with all four comparisons |
| Workbook Summary | No | The live result is on the Live sheet, fourth tab; Summary and About do not mention it (FINANCE-7) |

### 8. Ten figures against SEC filings

All fetched with Python `urllib` and the header read at run time from `~/.sec_ua`. Every figure matches.

| # | Figure in the project | SEC source (accession) | Row printed by `sec_parse.py` |
|---|---|---|---|
| 1 | 2026Q3 deliveries 35 large, 5 mid, 40 | 0000040533-26-000036, filed 2026-10-30 | `Large-cabin aircraft \| 35 \| 33 \| 101 \| 95`, `Mid-cabin aircraft \| 5 \| 6 \| 18 \| 18` |
| 2 | 2026Q3 Aerospace revenue $3,536M, earnings $513M | same | `Aerospace \| 3,536 \| 3,234 \| 302 \| 9.3`, `Aerospace \| 513 \| 430 \| 83 \| 19.3` |
| 3 | 2026Q3 Marine $4,960M, Combat $2,386M, Technologies $3,684M; earnings 391, 330, 346 | same | `Marine Systems \| 4,960`, `Combat Systems \| 2,386`, `Technologies \| 3,684`; `391`, `330`, `346` |
| 4 | 2025Q3 Aerospace revenue $3,234M, earnings $430M, 39 deliveries (33, 6) | 0000040533-25-000043, filed 2025-10-24 | `Aerospace \| 3,234 \| 2,482 \| 752 \| 30.3`, `Aerospace \| 430 \| 305`, `Large-cabin aircraft \| 33 \| 24 \| 95 \| 76`, `Mid-cabin aircraft \| 6 \| 4 \| 18 \| 13` |
| 5 | 2026Q2 backlog: Aerospace $23,977M, Marine $65,182M, Combat $29,350M, Technologies $17,989M | 0000040533-26-000029, filed 2026-07-29 | `Aerospace \| 22,992 \| 985 \| 23,977`, `Marine Systems \| 42,356 \| 22,826 \| 65,182`, `Combat Systems \| 27,507 \| 1,843 \| 29,350`, `Technologies \| 11,256 \| 6,733 \| 17,989` |
| 6 | 2026Q2 book-to-bill 1.5 Aerospace, 1.4 defense, 1.4 company | same | "1.4-to-1 for the quarter for the defense segments, 1.5-to-1 for the Aerospace segment, and 1.4-to-1 on a company-wide basis" |
| 7 | 2026Q2 deliveries 35, 6; Aerospace $3,525M and $510M | same | `Large-cabin aircraft \| 35 \| 32 \| 66 \| 62`, `Aerospace \| 3,525`, `Aerospace \| 510` |
| 8 | 2026Q1 deliveries 31, 7; Aerospace $3,279M and $493M; fiscal end 2026-04-05 | 0000040533-26-000010, filed 2026-04-29 | `Large-cabin aircraft \| 31 \| 30`, `Mid-cabin aircraft \| 7 \| 6`, `April 5, 2026` |
| 9 | 2025Q4 deliveries 41, 4; Aerospace $3,788M and $481M | 0000040533-26-000003, filed 2026-01-28 | `Large-cabin aircraft \| 41 \| 42 \| 136 \| 118`, `Aerospace \| 3,788`, `Aerospace \| 481` |
| 10 | 2024Q3 deliveries 24, 4; Aerospace $2,482M and $305M | 0000040533-24-000041, filed 2024-10-23 | `Large-cabin aircraft \| 24 \| 22 \| 76 \| 57`, `Aerospace \| 2,482`, `Aerospace \| 305` |
| 11 | 2016Q1 restated to 20 large, 8 mid | 0000040533-17-000012, filed 2017-04-26 | `Large-cabin aircraft \| 23 \| 20`, `Mid-cabin aircraft \| 7 \| 8` |
| 12 | Fiscal quarter end 2026-10-04 (the lock's window end) | 0000040533-26-000036 | `October 4, 2026 \| September 28, 2025` |
| 13 | Tariffs cut Aerospace margin by 30 basis points in 2025; revenue recognised on the "fully outfitted aircraft" | 10-K 0000040533-26-000006, filed 2026-01-30 | both passages found by `sec_text.py` |

Derived figures recomputed from these: trailing margins 13.8%, 7.2%, 14.4%, 9.4%; revenue shares 25.2%, 32.7%, 17.1%, 25.1%; revenue per delivery $84.8M; the Exhibit 8 misses.

### 9. Would I interview this person?

Yes. The test was set up so it could fail, it failed twice, and the failure is the first line of the post. Most student work I see does the opposite. The SEC work is clean.

First hole I would poke: "Your raw count for 2026Q3 was 42 and GD said 40. What were the 42?" The honest answer is 37 current-production jets and five older ones, including a 1984 Gulfstream III. INTERVIEW_NOTES:30 instead says "So the registry had the quarter's jets in time". That answer is not truthful to the project's own data (FINANCE-1), and a GD analyst will find the G-III in the lock's airframe table in a minute.

Second: "GD said 160 for the year and had delivered 79. Why does your 'GD guidance pace' say 33.8 for Q3?" (FINANCE-3). The notes answer the general question well (line 18) and not this one.

Third: "What did you do and what did the agent do?" INTERVIEW_NOTES:36 and README:176 answer plainly.

The notes also drop the README's own caveat on "held out" (FINANCE-11) and overstate where the numbers come from (FINANCE-17).

## Findings

### FINANCE-1 (S1). "The registry had the quarter's jets in time" is not supported by the lock's own airframe table

- Surface: `docs/INTERVIEW_NOTES.md:30`: "So the registry had the quarter's jets in time: the count had settled at 42 by the lock. What missed was my scaling". Softer form at `README.md:92`: "Its miss came from the scale, not from late postings".
- Evidence. `q3odd.py` and `mix.py` over `data/snapshots/daily/2026-10-29.serials.csv.gz`:
  - `2026Q3 events 42 in-production models 37 (large 31 mid 6) GD 40 (35/5) other: {'G-IV': 1, 'G-1159A': 1, 'GV-SP (G550)': 1, 'GVI (G650ER)': 1, 'GULFSTREAM G150': 1}`
  - The five: G-IV s/n 1335 (no year), G-1159A s/n 445 (year 1984), G550 s/n 5260 (2009), G650ER s/n 6206 (2016), G150 s/n 311 (2014). Four carry a first US airworthiness date in July to September 2026, which is how they pass the 365-day bound.
  - GD's count is new aircraft (10-K 0000040533-26-000006). Gulfstream no longer builds any of those five types; the note itself says G650 production ended in 2025Q1.
  - The likely objection: README:145 says GD's count can include test aircraft and demonstrators it sells. That does not rescue these five. Four are airframes built from 1984 to 2016 whose first US airworthiness date is in 2026, the pattern README:157 itself gives for an imported used jet; a demonstrator kept on Gulfstream's US registration would carry its original date. None of the five has a Gulfstream cancellation on record (`gulfstream_cancel` blank in all five rows). The G-IV has no date and no year, so it rests on its type alone.
  - So the bound is 38 on dated evidence and 37 with the G-IV. Either way fewer than GD's 40 deliveries were in the count, and at most 32 of GD's 35 large-cabin jets (31 with the G-IV out). The registry did not have the quarter's jets by the lock. The raw count landed near 40 because used jets offset a shortfall of at least two, and three on my reading.
- What does hold: the count stopped moving (`daily.py`: 42 in every snapshot from 2026-10-27 to 2026-11-11), and the scale applied was 0.758 against 0.952 for the quarter (`recompute.py`).
- Defensible version: "By the lock the quarter's event count had settled at 42 and has not moved since. Of those 42, 37 were current-production models, against GD's 40, and 5 were older types that cannot be new deliveries. So the raw count's near match is partly luck. The estimate missed because I scaled by 0.76 deliveries per event when the quarter came in at 0.95. I cannot say the registry had the quarter's jets in time."

### FINANCE-2 (S2). "The raw registry count (42) missed by 2" is shown as a result with no word on what the 42 were

- Surface: `README.md:106`, `report/note.html:56` (key point 2) and `:78`, `docs/INTERVIEW_NOTES.md:30`.
- Evidence: as FINANCE-1. By cabin the 42 are 35 large and 7 mid against GD's 35 and 5, which looks like a near-perfect large-cabin match. By model it is 31 in-production large against 35, and 6 G280s against 5.
- Also: `README.md:157` says "5 of the 42 events were airframes at least three years old by that field". True by the year field, but the five by year are not the five by type. `q3events.py` shows the year-field five include G700 s/n 87118 with year of manufacture 2006, which looks like an entry error in the registry (its first airworthiness date is 2026-03-06), and leave out the G-IV with no year.
- Fix: next to each "raw registry count (42) by 2", add "of which 37 were current-production models". In README:157 name the five older types, and note the one G700 whose year field is wrong.

### FINANCE-3 (S2). On the live quarter, "GD's guidance pace missed by 6.2" makes GD's guidance look worse than a plain reading of it

- Surface: `docs/LINKEDIN_POST.md:4`, `README.md:6` and `:106`, note key point 2, dashboard live panel (`site/app.js:147`), `docs/INTERVIEW_NOTES.md:9` and `:30`.
- Evidence. `pace_alt.py`: `2026Q3: remaining 81.0 share Q3 0.4178 pace 33.84 even split 40.5 GD reported 40`, and `Q3 and Q4 by year: [(2023, 27, 39), (2024, 28, 47), (2025, 39, 45)]`. The 41.8% share for Q3 comes from three years with heavy fourth quarters. `data/guidance.csv`, 2026-04-29 call: "the third and fourth will be our highest, and that's per plan". 2026-07-29 call (confirmed at source): "Gulfstream will still deliver about 160 airplanes."
- So GD's words left 81 jets for two quarters it called its highest. The printed even split is 40.5. My judgment, not a measured fact: a covering analyst would have written a Q3 figure near that, not 33.8. GD delivered 40. The project's pace scores GD's guidance as a 6.2 miss.
- In fairness: the split rule is preregistered, it is not tilted against guidance on average (`pace_alt.py`: an even split scores 8.087 over the 26 quarters, worse than 6.9), and the post says "A pace I derived". The issue is the live sentence, which a reader takes as "GD's own guidance was off by 6".
- Defensible version: "My pace split the 81 jets GD's outlook left for the second half as 33.8 and 47.2, by the last three years' pattern, and missed by 6.2. An even split would have said 40.5."

### FINANCE-4 (S2). The dashboard, workbook and charts never say the pace is the author's construction; the note and dashboard omit the stated-plan variant

- Surface: `site/app.js:10`, `:14`, `:92-95`, `:147`, `:300`; `site/index.html:101`; workbook Summary A6 ("MAE guidance"), Quarters S1 ("Guidance pace"); chart legends in `output/charts/track_record.png` and `nowcast_path.png` ("GD guidance pace"); `report/note.html:67` calls it "the main comparison" with no stated-plan figure anywhere in the note.
- Evidence: `grep -n -i "construction\|GD publishes\|not a figure\|stated plan\|quarter plan" site/index.html site/app.js` prints nothing. `grep -n -i "construction" src/gdn/workbook.py src/gdn/charts.py src/gdn/site_data.py` prints nothing. Workbook About A9 describes the arithmetic but not whose it is.
- Fix: one clause on the dashboard hero or Method step 4 ("my construction, not a figure GD publishes"), the same in workbook About A9, and one sentence in the note: "With GD's stated quarter plans in place of my pace in six quarters, the baseline misses by 6.0, not 6.9, and the registry estimate is closer in 12 of 26."

### FINANCE-5 (S2). The four live figures do not reconcile as printed: 32.0, 40, 8.0 and 20.1%

- Surface: `docs/LINKEDIN_POST.md:1` and `:4`, `README.md:6` and `:106`, note key point 2, dashboard live panel, `docs/INTERVIEW_NOTES.md:30`.
- Evidence. `recompute.py`: `lock 31.953208556149733 miss 8.046791443850267 pct 20.11697860962567` and `8.0/40= 20.0`. Each figure is right unrounded. A reader of the post divides 8.0 by 40, gets 20.0% and sees 20.1%.
- Fix: print "20%", or print 31.95 and 8.05. On the post I would drop the percentage.

### FINANCE-6 (S2). "Registry count" in the headline sentence means the scaled estimate; the dashboard calls it something else; the post has no explanation

- Surface: `docs/LINKEDIN_POST.md:6`, `README.md:21`, note key point 1: "the registry count was off by 5.5". Dashboard hero (`site/app.js:92`): "the registry estimate was off by 5.5 jets a quarter on average, when GD delivers about 33". INTERVIEW_NOTES:7: "my registry estimate".
- Evidence: the table's "Raw registry count" row is 6.2 and "Registry estimate (ratio)" is 5.5 (README:29-30, `recompute.py`). README:23 and note.html:68 add a sentence to untangle it. The post does not, and for 2026Q3 the README then says the "raw registry count (42)" missed by 2 while the post says the tracker missed by 8.
- The sentence is preregistered word for word (PREREGISTRATION.md:52), and the dashboard already departs from it.
- Fix: in the post write "the scaled registry count" or "my estimate". Pick one name and use it on the dashboard too.

### FINANCE-7 (S2). The workbook's Summary sheet has neither plain result

- Surface: `output/gd_gulfstream_model.xlsx`, Summary A1:C8.
- Evidence (`wb.py Summary`): five rows labelled "MAE ratio", "MAE raw", "MAE seasonal", "MAE last", "MAE guidance" and A8: "The lowest holdout figure in column C is the baseline that missed by least." No sentence says the same quarter last year beat the estimate. No cell mentions 2026Q3; the lock, GD's 40 and the miss are on the Live sheet. The file stores no cached values, so a previewer shows the Summary numbers blank (About A21 admits this).
- Fix: two typed text rows on Summary: "Same quarter last year missed by least (4.6 against 5.5)" and "First live lock, 2026Q3: 32.0 against GD's 40, outside the band; see Live". Use the other surfaces' row names.

### FINANCE-8 (S2). 2026Q3 estimates printed with no reported figure beside them

- Surface and evidence:
  - Note Exhibit 9 (`report/note.html:82`): Aerospace revenue for 28.0 to 36.0 deliveries. No reported row, and the range stops short of GD's 40 (`derived.py`: `sensitivity delivery range: 28.0 to 36.0`).
  - Note Exhibit 10 (`:84`): "2026Q3 estimate" for three defense segments, no reported column. Its section is marked "before the release".
  - Note Exhibit 11, "Model page" (`:99-100`): "2026Q3 delivery estimate 32.0", "Aerospace revenue from the estimate $2.7B", "Revenue, all four segments $13.2B". Not marked "before the release". The cover box (`:59`) says only the key points and Exhibit 8 carry what GD reported.
  - Workbook Segments L1:L5 ("Drift 2026Q3") and B14:B18, and the Sensitivity sheet: no reported figure, no "before the release" label.
  - Dashboard sensitivity table (`site/app.js:440-444`): compares with "the year-ago quarter", not with what GD reported.
- GD reported $3,536M Aerospace and $14,566M for the four segments against estimates of $2,710M and $13,193M (`wb_eval.py`, `derived2.py`, SEC rows 2 and 3). At 40 deliveries the mechanical figure is $3,393M (`derived.py`).
- Fix: add a "GD reported" row or column to each, or mark each "made before the release; see Exhibit 8". Add a 40-delivery row to the two sensitivity tables.

### FINANCE-9 (S2). Six defense-study figures in the note have no source record in this repository

- Surface: `report/note.html:85`; generator `src/gdn/note.py:546-550`.
- Evidence: 9.9%, 7.3%, 6.5%, 9.4%, 5.8% and 6.0% are string literals in `note.py`. `grep -rn "9\.9%\|7\.3%\|6\.5%" tests/*.py report/claims.json` finds nothing: no claim id, no quote, no hash, no test. The same sentence gives a cause, "GD was left out because it stopped tagging backlog in XBRL in 2018", with no cited filing.
- I did not open the study page (its address carries the owner's handle), so I could not check the six figures or the XBRL statement.
- Fix: add them to `report/claims.json` with the study's own table as the quoted source, or cut the paragraph to "my earlier study of five other primes found the seasonal naive with drift the best next-quarter baseline" with the link.

### FINANCE-10 (S3). The note's risks are generic 10-K text

- Surface: `report/note.html:86` onward, eight bullets.
- Evidence: seven are restated risk factors that begin "GD says". Only the tariff bullet has a figure. See Q4.
- Fix: keep three, and add the Gulfstream risks the note already sources elsewhere: the G280 production break before the G300, G400 timing, and delivery timing risk in the second half ("some risk on the 280 deliveries", 2026-07-29 call, in `data/guidance.csv`).

### FINANCE-11 (S2). The interview notes state "held out" more strongly than the README does

- Surface: `docs/INTERVIEW_NOTES.md:7` ("I fixed the rules on 12 design quarters and committed them before scoring 26 held-out quarters") and `:33` ("I fixed the rules before I scored the held-out quarters").
- Evidence: `README.md:119` says the commit order "is all that backs the words", that every count was already in the repository, and that the rules were committed "two minutes before the held-out scores, in the same build session". The notes carry none of that. The sentences are true as far as they go, so this is framing, not a false claim. I could not check the commit times (no git history in my copy).
- Defensible version: "The rules were committed before the held-out scores, minutes before and in the same session, so only the locked quarters are out of sample in the strict sense."

### FINANCE-17 (S1). "Every number in it traces to a filing or a registry file" is contradicted by the project's own files

- Surface: `docs/INTERVIEW_NOTES.md:33`.
- Evidence:
  - `README.md:146`: the full-year outlooks are "read from call transcripts (Motley Fool, with MarketBeat where no Fool page loaded)". Those outlooks feed the 6.9, the 33.8 and the 6.2, three of the headline figures. `data/guidance.csv` holds 27 call rows (`derived2.py`), each with a fool.com or marketbeat.com link.
  - `src/gdn/note.py:546-550`: six percentages in the note come from the author's other study and have no source record here (FINANCE-9).
- Severity: by the brief's rule this is a claim the evidence does not support, in material that goes out with the post, so S1. It is the smaller of the two S1s and the easier fix. An interviewer who asks "where does 160 come from?" gets "a Motley Fool transcript", which is fine, but it is not what the sentence says.
- Defensible version: "Every delivery and dollar figure traces to an SEC filing, every registry figure to a stored FAA snapshot, and every outlook to a linked call transcript."

### FINANCE-12 (S3). Military, special-mission and export gaps carry no size on any surface

- Surface: `README.md:152` and `:154`; note Limitations.
- Evidence: both say what the registry cannot see and give no count. Every other limitation in the README has one.
- Fix: say that these are unsized and that the trailing scale absorbs them only if they are steady.

### FINANCE-13 (S3). Dashboard first screen: the miss is there but the missed estimate is the headline figure; two panel titles mislead a little

- Surface: `site/index.html:42` ("The live quarter"), `:86` ("What it means for GD"); `site/app.js:131-166`.
- Evidence: `output/charts/dashboard.png`. The hero is backtest only. In the panel the largest type is "32.0 deliveries, locked estimate"; "GD reported 40 deliveries" is the seventh of eight facts. The quarter is scored, not live. "What it means for GD" heads a table of estimates that GD has since reported against.
- Fix: put "GD reported 40" beside the 32.0 at the same size; title the panels "The latest locked quarter" and "Revenue estimates made before the release".

### FINANCE-14 (S3). `output/charts/dashboard.png` is older than the page it shows

- Evidence: the screenshot's eyebrow reads "General Dynamics · Gulfstream"; `site/index.html:25` reads "Student research · not affiliated with General Dynamics or Gulfstream". Nothing on the public surface embeds the file (`grep` finds it only in `tools/determinism.py`).
- Fix: reshoot or remove it.

### FINANCE-15 (S3). Workbook wording

- The disclaimer is on About A3 only; a sheet opened or printed alone carries none.
- About A6 says "within 365 days of first airworthiness"; README:115 says the bound is one-sided.
- Sheets say "Nowcast" where every other surface says "estimate".
- README's first chart (`track_record.png`) stops at 2026Q2, so the first picture a reader sees leaves the live miss out. A marked 2026Q3 point would match the text above it.

### FINANCE-16 (S3). Small wording

- `docs/LINKEDIN_POST.md:6`: "the rules: Over 26" has a capital after the colon.
- `docs/prepub/ERRATA.md` speaks in the audit's voice ("this run", "the main thread", "Owner:"). README:176 discloses the agent, so this is a tone point only.
- `report/note.html:59` says the key points and Exhibit 8 carry what GD reported; the section "The live quarter: 2026Q3" does too.

## Also asked for

**Sentences about 2026Q3 that read as if GD had not reported.** None found on the post, README, dashboard files, note text, interview notes or resume bullets (`grep -n -i "will report|has not reported|not yet reported|yet to report|upcoming|provisional|awaiting|scheduled"`; the two hits are the 2026Q4 status and the method description). The nearest things are the unmarked pre-release tables in FINANCE-8 and the panel title in FINANCE-13.

**Figures that differ between two surfaces.** No number differs. Differences of naming or coverage: "registry count" against "registry estimate" (FINANCE-6); the note's Exhibit 11 Summary has four rows where the workbook's has five (no guidance row); the dashboard screenshot's eyebrow (FINANCE-14); the workbook's "within 365 days" (FINANCE-15).

**Claims of cause with no cited filing or call.**
- INTERVIEW_NOTES:30, "the registry had the quarter's jets in time ... What missed was my scaling" (FINANCE-1).
- note.html:85, "GD was left out because it stopped tagging backlog in XBRL in 2018" (FINANCE-9).
- README:156 and INTERVIEW_NOTES:39 and :42 give a registry mechanism (only the current certificate is kept) as the cause of coverage drift. It rests on the as-of study's own counts (146 against 63 events for 2017Q1's lags), not on a filing. Reasonable, and labelled as the author's reading.
- No business cause is asserted anywhere. README:94 says no filing or call explains the five largest misses, and the 2023 and 2024 guidance misses are reported with no reason given.

## What is right

- **The lock is real and checkable.** File hash, lock record, README and release notes agree. GitHub published the release 30 hours before SEC accepted GD's 8-K. The README is candid that the repository was private and that absence of later edits cannot be shown.
- **Every SEC figure I checked is right** (13 rows above, 8 filings), including the restated 2016 count and the fiscal quarter end the lock window depends on.
- **Every backtest figure reproduces** from `results/holdout.csv`: 5.5234, 6.1923, 6.9173, 4.6154, 8.8077; sign tests 14/12, 11/15, 16/10 with p 0.4225, 0.8365, 0.1635; 22 sourced quarters 7.3568, 5.2503, 4.6364; 2023 and 2024 12.515 against 3.482; the other 18 quarters 4.429, 6.431, 4.444; the stated-plan variant 6.0184 and 12 of 26; the five largest misses; the yearly table.
- **"The guidance pace has been closer in each of the last five quarters"** is true: 2025Q3 5.99 against 6.80, 2025Q4 5.5 against 13.4, 2026Q1 6.0 against 7.38, 2026Q2 3.72 against 3.81, 2026Q3 6.16 against 8.05.
- **README:92's snapshot claim is true**: 42 in every daily file from 2026-10-27 to 2026-11-11.
- **The workbook's typed inputs equal the CSVs** (42 rows, 0 mismatches) and its formulas give the published figures.
- **The framing is right on four of five first screens**: the live miss, the losing comparison with last year's quarter, the "registry copy that had years to fill in" sentence, and "One quarter is one data point".
- **No advice language**, a disclaimer on every PDF page, a no-position statement, no price target, and INTERVIEW_NOTES:27 explains why.
- **The pace has no look-ahead**: it reads the latest call on or before the fiscal end and shares from the three prior years.
- **Two call quotes confirmed at source** (2026-07-29: 160 airplanes, $13.8 billion, 14.7%, final G280 in the second quarter of next year; 2023-07-26: 27 in the third quarter, five to six fewer than 145).
- **Limitations are unusually frank and mostly sized**: used jets, the leasing arm, the dropped G700 type code, the double-counted airframes, the audit's 10 of 30.

## What I could not check

- The two links in the post and the README's Pages link (private until launch, as the brief says).
- The defense study page and the owner's personal site: I did not request either, because the addresses carry the owner's handle or name. So the six study figures and the XBRL statement are unchecked (FINANCE-9).
- Anything that needs git history: the commit order behind "held out", the "two minutes", "every daily commit since 2026-10-31 has come from the workflow", and whether the note's "before the release" sections are unchanged since 2026-10-29.
- Whether the six stated quarter plans in `data/quarter_plans.csv` are all there are. I read one of the 27 calls at source for this.
- The raw FAA zips (not in the tree), so ERRATA E5's 17 G700s and the stored subsets' completeness are taken as given.
- The 2016 releases' green and outfitted tables (I checked the restated 2016Q1 column only) and the 2022-01-26 "about 11 aircraft" quote.
- PDF text by extraction: the venv has no pypdf. I read all 7 pages as images and took text from `report/note.html`, whose hash equals the PDF's input stamp.
