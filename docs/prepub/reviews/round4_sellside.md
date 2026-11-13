# Round 4: sell-side aerospace and defense analyst (`sellside`)

Verdict: NO-GO. The note states as fact that GD "stopped tagging backlog in XBRL in 2018", which GD's own 10-Qs contradict, and its first page charges GD's guidance with a 6.2-jet miss on a pace that did not use GD's statement that Q3 and Q4 would be its highest quarters.

Counts: S1 1, S2 4, S3 3

Tree read: `~/gdn-prepub/round4/` (cold copy, no git). SEC documents were fetched with Python `urllib` from `www.sec.gov` and `data.sec.gov` and cached under `~/gdn-prepub/agents/round4_sellside/sec/`. The workbook was recomputed with the `formulas` package. Call quotes were checked with WebFetch on the Motley Fool pages that `report/claims.json` and `data/guidance.csv` cite.

## Answers

**1. Is the scored count GD's count, as GD defines it? Where does the registry differ by definition, and is each difference disclosed?**

Yes. The truth series is the "Gulfstream Aircraft Deliveries (units)" table in each results 8-K's Exhibit 99.1. I compared nine releases with `data/processed/gd_deliveries.csv` and found no mismatch. The current-quarter columns match its rows for 2024Q3 to 2026Q2 (large, mid and total). The prior-year columns match its rows for 2023Q3 to 2025Q3. The 2026Q3 count matches `results/live/2026Q3_score.json` and workbook Live!B16. The 2026Q3 release (0000040533-26-000036) prints 35 large, 5 mid, 40 total. GD's 10-K for 2025 (0000040533-26-000006) recognises new-aircraft revenue "generally upon delivery and acceptance by the customer of the fully outfitted aircraft". The README's 2016 account also checks out. The 2016Q1 release (0000040533-16-000063) printed green 31 and outfitted 27. The 2017Q1 release (0000040533-17-000012) restates 2016Q1 as 28 (20 large, 8 mid) for ASC 606, "which we adopted on January 1, 2017".

Definitional differences, and where each one is disclosed:

| Difference | README | Note | Dashboard |
|---|---|---|---|
| Outfitted handover against a registration or export-cancellation date | yes (Handover; Data quotes the 10-K) | yes (Handover), without GD's outfitted basis | no; links to README Limitations |
| Pre-owned jets (GD reported them on a separate line in 2016 and 2017; the registry can count them as new) | yes (Used jet, 19.7% of events) | yes (Used jets) | no |
| Sold test aircraft and demonstrators, in GD's count (2022-01-26 call: about 11 in 2021) | yes (Data) | **no** | no |
| Military and special-mission aircraft | yes | yes, one line | no |
| Exports with no US registration | yes | yes | no |
| G280 built by IAI, filed under maker `IAI LTD` | yes | yes | no |
| Gulfstream Leasing LLC registrations counted as deliveries | yes (Holder and scope) | **no** | no |
| One G700 type code (`3980222`) outside the scope rule | yes (Holder and scope) | **no**; the note says it reads "every Gulfstream jet" | no |

The note is thinner than the README, and one sentence in it overclaims (SELLSIDE-5). Whether GD's count includes green aircraft delivered to government or special-mission customers is not stated in any release I read; see Suspicions.

**2. Program facts checked against a GD filing or call.**

| Fact (note.html:65 unless stated) | Source | Result |
|---|---|---|
| G500 entered service 2018, G600 2019 | 10-K 2025, 0000040533-26-000006 | matches verbatim |
| G700 deliveries began 2024Q2 after FAA and EASA certification | 10-K 2024, 0000040533-25-000008; 10-K 2025 says "G700 entered service in 2024" | matches |
| G800 type-certified by FAA and EASA on 2025-04-16 | 10-Q 2025Q1, 0000040533-25-000014 | matches verbatim |
| G800 deliveries began 2025Q3 | 10-K 2025; the 2025-10-24 call row in `data/guidance.csv`. The 2025Q1 10-Q had expected deliveries "late in the second quarter", so the slip is consistent | matches |
| G650 production ended 2025Q1; the G800 replaces it | 10-Q 2025Q1. The 10-Q 2025Q3 (0000040533-25-000045) adds that the G650 "had its final delivery in the second quarter of 2025" | matches (production end and last delivery differ, with no contradiction) |
| Large-cabin models built in Savannah; G280 assembled by a non-U.S. partner | 10-K 2024 | matches verbatim |
| G300 announced September 2025 to replace the G280 | 10-Q 2025Q3 ("In September 2025"); 10-K 2025 says "In the second half of 2025" | matches |
| Final G280 in 2027Q2; G300 "late '27, early '28"; planned production break (note.html:65, README:158) | 2026-07-29 call (page states July 29, 2026) | matches. The 2026-10-30 call now says the G280 finishes deliveries around mid-2027 and expects G300 certification toward the end of 2027. No contradiction |
| G400: more to say "over the next couple of quarters" | 2026-07-29 call; the 10-K 2025 says Gulfstream "is currently developing" the G400 | matches |
| 2026 outlook: about 160 deliveries, about $13.8B Aerospace revenue, 14.7% margin (note.html:82) | 2026-07-29 call | matches. The 10-K 2025 had said about $13.6B and about 14% |
| 2021 deliveries included test aircraft and "a few demonstrators all up about 11 aircraft" (README:145) | 2022-01-26 call | matches |
| G280 a "joint effort" with IAI (archived 2012 Gulfstream release) | web.archive.org | could not fetch |

All 21 filing quotes in `report/claims.json` appear verbatim in the filings I fetched (script match, 21 of 21).

**3. Is the guidance pace built the way the street would build it? Is the difference disclosed and fair to GD?**

Only in part. For a fourth quarter the pace is the outlook less year-to-date deliveries, with nothing constructed (`src/gdn/model.py:119-133`). Those misses are GD's own: 2023Q4 pace 62.0 against 39, and 2024Q4 61.0 against 47. For the first three quarters the pace spreads the remainder by pooled quarterly shares from the three prior years. A street model would first use GD's own quarterly color. GD gave that color for 2026Q3. On the 2026-04-29 call it said Q2 "will be very similar to first quarter" and "the third and fourth will be our highest, and that's per plan" (`data/guidance.csv`, and the call page). The pace put 2026Q3 at 33.8, below both reported quarters (38 and 41). GD gave no Q3 number, so I do not claim it pointed to 40. Its plan did put Q3 above the first half, and the pace did not. Disclosure: the README gives the 40.5 even split (README:106) and the quarter-plan and January 2021 variants (README:49). The note, the post and the dashboard give neither the even split nor GD's statement, and the note's key point names the 33.8 "GD's guidance pace" (SELLSIDE-2). In the backtest, the closest thing to a street pace (GD's stated quarter plans plus the January 2021 reading) misses by 5.70 against 5.52 for the registry (`results/exploratory/sensitivity.md`). The README reports this; the note does not.

**4. Is the Aerospace revenue estimate labelled mechanical everywhere?**

Yes. Note: key point 3 (note.html:57), the Exhibit 8 source line (:81), the Exhibit 9 caption (:82) and the Exhibit 11 source line (:100). Workbook: About!A10, Segments!A20, Sensitivity!A12. Dashboard: the "What it means for GD" subhead (`site/index.html`). README: "The dollars" (README:123). The README does not show the $2.7B figure. Each label says services are included. Key point 3 adds that the $85M "includes services and Jet Aviation revenue, which a delivery count does not measure".

**5. Segment, earnings, backlog and book-to-bill figures against the filings.**

A script (`~/gdn-prepub/agents/round4_sellside/q5.py`) compared all 64 typed segment cells against the parsed Exhibit C tables: revenue and operating earnings for 4 segments over 8 quarters, in `data/processed/segments.csv` and workbook Segments!B2:I10. It printed `checked 64 mismatches 0`. A second script (`q5b.py`) rebuilt every derived figure in the note from the parsed releases alone, and each one matches.

| Figure | Surface | Filing (accession) | Value in filing | Match |
|---|---|---|---|---|
| Aerospace revenue 2025Q3, $3.2B | note.html:81; Segments!F2 | 0000040533-25-000043 | 3,234 | yes |
| Aerospace revenue 2025Q4 (feeds $13.8B TTM) | Segments!G2 | 0000040533-26-000003 | 3,788 | yes |
| Aerospace revenue 2026Q1 | Segments!H2 | 0000040533-26-000010 | 3,279 | yes |
| Aerospace revenue 2026Q2 | Segments!I2 | 0000040533-26-000029 | 3,525 | yes |
| Aerospace TTM $13.8B, 25.2% share, 13.8% margin | note.html:62-63 | four releases above; OE 430, 481, 493, 510 | 13,826; 1,914 | yes |
| Marine TTM $17.9B, 7.2% margin | note.html:62 | same four | 17,917; OE 1,294 | yes |
| Combat TTM $9.4B, 14.4% margin | note.html:62 | same four | 9,360; OE 1,344 | yes |
| Technologies TTM $13.8B, 9.4% margin | note.html:62 | same four | 13,758; OE 1,295 | yes |
| Aerospace TTM to 2025Q2, $12.3B | note.html:100 | 0000040533-24-000041, -25-000003, -25-000012, -25-000033 | 2,482+3,743+3,026+3,062 = 12,313 | yes |
| Aerospace backlog 2026Q2, $24.0B, 1.73 years | note.html:80; Segments!N2 | 0000040533-26-000029, Exhibit H | 23,977 | yes |
| Marine backlog 2026Q2, $65.2B | note.html:84; Segments!N3 | same | 65,182 | yes |
| Combat backlog 2026Q2, $29.4B | note.html:84; Segments!N4 | same | 29,350 | yes |
| Technologies backlog 2026Q2, $18.0B | note.html:84; Segments!N5 | same | 17,989 | yes |
| Book-to-bill 2026Q2: Aerospace 1.5, defense 1.4, company 1.4 | note.html:80 | 0000040533-26-000029 | "1.4-to-1 ... defense segments, 1.5-to-1 for the Aerospace segment, and 1.4-to-1 on a company-wide basis" | yes |
| Aerospace revenue 2026Q3, $3.5B | note.html:57, :81 | 0000040533-26-000036 | 3,536 | yes |
| Marine, Combat, Technologies 2026Q3: $5.0B, $2.4B, $3.7B; total $14.6B | note.html:81 | same | 4,960; 2,386; 3,684; 14,566 | yes |
| Four-segment operating earnings 2026Q3, $1.6B | note.html:81 | same | 513+391+330+346 = 1,580 | yes |
| Marine backlog 2026Q3, $146.9B | note.html:84 | same, Exhibit H | 146,865 | yes |
| 2025Q3 total revenue, $12.9B | note.html:81 | 0000040533-25-000043 | 12,907 | yes |
| Deliveries 2026Q3: 40 (35 large, 5 mid) | note.html:56; Live!B16 | 0000040533-26-000036 | 35, 5, 40 | yes |
| Deliveries over four quarters to 2026Q2: 163 | note.html:100; Segments!B12 | four releases above | 39+45+38+41 | yes |

The derived figures also match: drift estimates of 3,631, 4,775, 2,325 and 3,382; estimate less reported of +95, -185, -61, -302 and -826; total 13,193 against 14,566, a 9.4% miss; segment operating earnings of 1,372; coverage of 1.73, 3.64, 3.14 and 1.31.

**6. Does the defense half overreach?**

Mostly no. It uses a naive rule and says "Applying that study to GD is an assumption: it did not test GD" (note.html:85). It states that the Exhibit 10 backlog is stale and gives the 2026Q3 Marine backlog. The one overreach is a factual sentence about GD's filings, which is wrong as written (SELLSIDE-1). I could not check the six error percentages, or whether the study tested companies or segments, because the study's page sits under the owner's account name (Could not check). As an analyst I would call this half thin rather than overreaching. Three quarters of GD's revenue get one paragraph, and the $93.8B of defense orders in 2026Q3 appear only as a backlog footnote.

**7. Do the risks read as generic 10-K text or as specific to this estimate?**

Generic. The intro names two product-cycle risks. All nine bullets restate 10-K or 10-Q text, and three of them (fixed-price contracts, U.S. government spending, FX) do not bear on a Gulfstream delivery estimate. The section leaves out the risk GD itself tied to deliveries, in the same 10-Q paragraph the note cites for tariffs (SELLSIDE-4). It also omits risks that GD's calls tie to deliveries: some risk on the G280 "for obvious reasons" (2026-07-29), possible "minor impact" on the G280 from the Middle East conflict (2026-04-29), the G700 and G800 completion learning curve (2026-07-29), and the history of deliveries slipping at year-end ("10 of the deliveries slipping into next year", 2024-10-23, `data/guidance.csv`).

**8. The workbook's Summary sheet.**

It computes without errors: the `formulas` solution has 1,197 nodes (cells and ranges), and none is an error value. Design: ratio 5.47, raw 9.42, seasonal 5.00, last 3.83. Held out: 5.52, 6.19, 4.62, 8.81, and guidance 6.92. These match the note (Exhibits 2 and 11) and the README tables after rounding. Live gives a band of 21.23 to 37.24, a miss of 8.05 (20.1%), "outside" and a pace miss of 6.16. An analyst could audit the ratio, raw and naive columns without the author: they are live formulas over typed counts, and the counts match `gd_deliveries.csv`. Three things need the author or the code (SELLSIDE-8). The guidance pace is a typed number with no outlook, year-to-date or weights. Four of its rows (2021) are the same-quarter-last-year fallback under the "Guidance pace" header, unflagged. The band percentiles are typed. The labels ("MAE", "seasonal") differ from the note's wording, and Exhibit 11 leaves out the Summary's guidance row (SELLSIDE-6).

**9. Would I forward it?**

Not yet. The arithmetic is clean; I found no wrong filing figure. The framing of GD's guidance and the risk section would draw the first objection from anyone who covers GD. Three changes would make me forward it:
1. In the note and the post, put GD's 2026-04-29 statement and the 40.5 even split next to the 33.8. In the backtest, give the street-style variant (5.70 against 5.52) and the 2023-24 concentration beside the preregistered 6.9 (SELLSIDE-2, -3).
2. Replace the boilerplate risks with the estimate-specific risks GD has stated, starting with the Israel-based supplier delay (SELLSIDE-4).
3. Correct the XBRL sentence (SELLSIDE-1), and bring the note's scope statement in line with the README's (SELLSIDE-5).

## Findings

### SELLSIDE-1 (S1): the note's reason GD was left out of the defense study is contradicted by GD's filings
- Surface: research note, `report/note.html:85` and the PDF, page 5. Generated by `src/gdn/note.py:554`.
- The claim: "GD was left out because it stopped tagging backlog in XBRL in 2018."
- Evidence: GD's 10-Qs still tag `us-gaap:RevenueRemainingPerformanceObligation`, which they call total backlog. In the 2021Q2 10-Q (0000040533-21-000043) the value is $89.2B, "which we also refer to as total backlog". The 2026Q2 10-Q (0000040533-26-000032) has $136.5B and the 2025Q1 10-Q (0000040533-25-000014) has $88.7B. In 10-Qs the fact carries a typed dimension, `RevenueRemainingPerformanceObligationExpectedTimingOfSatisfactionStartDateAxis`. The SEC company-facts API (`data.sec.gov`) returns the undimensioned fact quarterly only to 2018-09-30, then only for the year-ends 2023, 2024 and 2025:
```
2018-09-30 69500000000 10-Q 2018 Q3 0000040533-18-000060
2023-12-31 93600000000 10-K 2023 FY 0000040533-24-000007
2024-12-31 90600000000 10-K 2024 FY 0000040533-25-000008
2025-12-31 118000000000 10-K 2025 FY 0000040533-26-000006
```
- Fix: the defensible version is "After 2018Q3, GD's 10-Qs tag backlog (remaining performance obligations) only on a timing dimension, so the SEC company-facts API returns no quarterly GD backlog series." The owner should confirm that this API was the study's source before saying it explains why GD was left out. Edit the generator, then rebuild the note and PDF.

### SELLSIDE-2 (S2): the 2026Q3 "GD's guidance pace" ignores GD's stated plan, and the note and post do not say so
- Surfaces: note key point 2 (`report/note.html:56`) and the locked-quarter paragraph (:78), generated by `src/gdn/note.py:313` and `:481`. Post, `docs/LINKEDIN_POST.md:4`, generated by `src/gdn/report.py:567`. README:6 and :106, generated by `src/gdn/report.py`. The dashboard's live fact, `site/app.js`.
- Evidence: `data/guidance.csv` row 2026-04-29 says "the third and fourth will be our highest, and that's per plan" (the call page matches). The pace for 2026Q3 is 33.84 (`results/live/2026Q3_score.json`). That is below both reported first-half quarters, 38 and 41. GD then delivered 40. README:106 gives "an even split would have said 40.5". The note, the post and the dashboard give neither the even split nor GD's statement. The note's key point calls the 33.8 "GD's guidance pace" without the "my construction" qualifier, which appears two sections later.
- Fix: in the note's key point and locked-quarter paragraph, and in the post's pace line, add one sentence: GD had said Q3 and Q4 would be its highest quarters, and an even split of the 81 remaining jets gives 40.5. Keep 33.8 as the preregistered figure.

### SELLSIDE-3 (S2): the note's backtest headline omits where the registry's edge over the pace comes from
- Surface: note.html:55, :68 and :71 (generated by `src/gdn/note.py`). README:69 has the disclosure.
- Evidence: a command over `results/holdout.csv` printed, for the 18 quarters outside 2023 and 2024, ratio 6.43, guidance 4.43 and seasonal 4.44. Over the last four held-out quarters the pace missed by less than the registry each time (6.0 against 6.8, 5.5 against 13.4, 6.0 against 7.4, 3.7 against 3.8), and in 2026Q3 as well (6.2 against 8.0). `results/exploratory/sensitivity.md` gives the street-style variant, guidance 5.70 against registry 5.52, with the registry closer in 11 of 26 quarters. The note gives only the year table (Exhibit 5) and a footnote with 6.7 and 6.0.
- Fix: add the README:69 sentences and the 5.70 combined variant to the note, labelled exploratory.

### SELLSIDE-4 (S2): the risk section leaves out the delivery risk GD states in the 10-Q the note cites
- Surface: note.html:86-87 (generated by `src/gdn/note.py:571`), PDF page 6.
- Evidence: the 2026Q2 10-Q (0000040533-26-000032) is source 8 in the note, cited for the tariff bullet. The sentence just before the tariff passage reads: "we have experienced some delays including at our Israel-based supplier of mid-cabin airframes caused by conflicts in the Middle East." GD's calls say the same: possible "minor impact" on the G280 (2026-04-29) and "some risk on the 280 deliveries" (2026-07-29). The note's mid-cabin count rests on the G280 alone (note.html:95), and 2026Q3 mid-cabin came in at 5 against 7 registry events.
- Fix: add a bullet quoting that sentence. Drop or demote the defense-only bullets (fixed-price, U.S. spending) from a Gulfstream estimate's risk list.

### SELLSIDE-5 (S2): the note says it reads "every Gulfstream jet"; the README says the scope rule does not
- Surface: note.html:67, generated by `src/gdn/note.py:373`. Against README:159 and README:145.
- Evidence: the note says "I read every Gulfstream jet in the FAA's aircraft registry". README:159 says the FAA files G700 type code `3980222` under engine-type code 2, "so the 17 G700s registered to Gulfstream under it on 2026-10-30 are outside the count". It also says `GULFSTREAM LEASING LLC` registrations count as deliveries. README:145 says GD's count includes sold test aircraft and demonstrators. None of the three appears in the note. The tracked snapshot rows hold no `3980222` row (`2026-10-29` ACFTREF, MASTER and DEREG: 0 rows each), so a reader of the note cannot learn of the gap.
- Fix: replace "every Gulfstream jet" with "every Gulfstream turbojet or turbofan type". Add one Limitations line covering the G700 type-code gap, Gulfstream Leasing, and the sold test and demonstrator aircraft in GD's count.

### SELLSIDE-6 (S3): Exhibit 11 omits the Summary sheet's guidance row
- Surface: note.html:100 (generated by `src/gdn/note.py:587-598`) against workbook Summary!A6:C6.
- Evidence: Summary!C6 `=AVERAGE(Quarters!T18:T43)` computes to 6.92. Exhibit 11 is captioned "The workbook's Summary and Segments sheets" but shows four of the five rows, leaving out the note's main comparison.
- Fix: add the "Average miss, GD guidance pace" row (no design-window figure, 6.9 held out).

### SELLSIDE-7 (S3): Exhibit 9's delivery column rounds in a way that makes one row look like an arithmetic error
- Surface: note.html:82; workbook Sensitivity!B10:C10 (generated by `src/gdn/note.py` and `src/gdn/workbook.py`).
- Evidence: the formulas recompute gives B10 = 35.953 and C10 = 3,049.6. The note prints "36.0" and "$3.0B" beside a stated $85M per delivery, and 36 × $85M is $3.06B. Every row is the estimate (31.95) plus an offset, displayed to one decimal.
- Fix: show the offset rows as 27.95 to 35.95, or print revenue to two decimals ($3.05B).

### SELLSIDE-8 (S3): the workbook's pace and band cannot be audited without the code
- Surface: `output/gd_gulfstream_model.xlsx`, Quarters!S18:S43, Live!B7:B8, B12:B13 and B20 (generated by `src/gdn/workbook.py:28`, `:191`).
- Evidence: S18:S43 are typed blue inputs. For example S32 holds 43.07 for 2023Q3, with no outlook, year-to-date or weights beside it. S22:S25 hold 23, 32, 32 and 40, which are the 2020 actuals (the same-quarter-last-year fallback), under the header "Guidance pace" with no flag. Live!B7:B8 are typed 187 and 28. They equal SUM(Quarters!F40:F43) and SUM(Quarters!G40:G43) but are not linked to them. The band percentiles in B12:B13 are typed.
- Fix: add columns for the outlook, the year-to-date deliveries and the seasonal weight, and make S a formula. Mark the 2021 fallback rows. Link Live!B7:B8 to the Quarters sums.

## Improvements that would raise the project's standing

1. Add a street-style pace as an exploratory row beside the preregistered one: outlook less year-to-date, allocated by GD's own quarterly color where a call gives it.
2. Split Aerospace revenue into aircraft manufacturing and aircraft services, which the 10-K reports separately. Scale only manufacturing with deliveries, as an exploratory figure beside the mechanical one.
3. Add GD's own Aerospace revenue guide as a baseline. About $13.8B less the first-half $6,804M implies about $7.0B for the second half; label it as derived from the outlook.
4. Track the mid-cabin registry count against GD's mid-cabin count quarter by quarter through the G280 wind-down, and state the 2026Q3 mid-cabin result (7 events, 5 delivered).
5. Give the workbook a "Sources" column with each quarter's accession number. `gd_deliveries.csv` already has them.

## Checked and clean

- PDF input stamp equals `sha256(report/note.html)` (`e0b89a40...5c3d`). `site/GD_research_note.pdf` and `output/GD_research_note.pdf` are byte-identical.
- All 64 typed segment cells, the four 2026Q2 backlog inputs, the 2026Q2 book-to-bill sentence and the 2026Q3 segment figures match the SEC releases.
- Every derived dollar figure in Exhibits 1, 8, 10 and 11 and key point 3 is reproduced from the parsed releases alone.
- Delivery counts: the current-quarter columns of nine releases match `gd_deliveries.csv` and the workbook for 2024Q3 to 2026Q2. 2026Q3 matches the score file and Live!B16. The prior-year columns show no later change to any count from 2023Q3 to 2025Q3. The 2016 restatement checks out (green 31, outfitted 27, restated 28).
- The lock time 2026-10-29T05:51:24Z is 01:51 EDT, as stated. The lock arithmetic checks out: 35 × 140/187 + 7 × 23/28 = 31.95, and the scale 163/215 = 0.76.
- The 22-quarter averages (7.36, 5.25 and 4.64, printed as 7.4, 5.3 and 4.6) and README:69's figures (4.4, 4.4 and 6.4, and the last five quarters) reproduce from `results/holdout.csv`.
- The 21 filing quotes in `claims.json` are verbatim. The call quotes I checked (2026 outlook, G280, G300, G400, the 2021 test aircraft) match in substance.
- The mechanical label is on every surface that shows the delivery-based revenue figure.
- The note says GD's 2026Q3 release reports Marine backlog of $146.9B. That is correct, and the note says its own table is stale.

## Suspicions, not proven

- **Special-mission and government aircraft.** GD's releases do not say whether green aircraft sold to government or special-mission customers are in the delivery count. GD's own statement would settle it.
- **Sold test aircraft and demonstrators.** The registry's 365-day airworthiness bound may drop them, which would make a systematic gap in years like 2021. Checking the 2021 test-aircraft serials against the event table would settle it. The 2021 misses ran the other way (registry high), so I make no claim.
- **The defense study.** It may have tested company totals rather than segments, and its "drift" may be additive rather than the multiplicative trailing-growth rule used here. The study's data file would settle both.
- **G700 type code.** Customer-registered G700s may sit under `3980222` and be missing from past counts. The tracked rows exclude that code, so only the raw FAA file can settle it. README:159 says none had an event.
- **Transcript URL.** The Fool URL for the 2026-07-29 call is dated 2026/08/07. The page itself says July 29, 2026, so this is not an error.

## Could not check, and refused commands

- The defense study page and its data file: the URL contains the owner's account name, which the common rules bar me from sending to an outside service. So the six percentages at note.html:85 are unchecked.
- The archived Gulfstream G280 certification release (web.archive.org): WebFetch refused the host.
- Call quotes were checked through WebFetch's extraction, not a byte-level string match.
- Exhibits 4 and 7 (charts) were not checked point by point.
- I ran no forbidden command, and none was refused.
