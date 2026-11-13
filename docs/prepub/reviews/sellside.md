# Sell-side review (P4.1): Gulfstream delivery tracker

Reviewer role: sell-side aerospace and defense analyst covering General Dynamics. Date of review: 2026-11-11. Branch `prepub-audit` at `7b3ba7e`.

## Verdict

**NO-GO as the surfaces stand today.** The post itself is honest about the one locked quarter and about the baseline that wins. What it links to is not ready. Three owner documents and the README's front image still describe 2026Q3 as unscored. The note and dashboard still present 2026Q3 revenue as an estimate twelve days after GD reported it, and the Aerospace figure missed by 23%. The lead comparison, "6.9 for GD's guidance pace", charges GD with a 16-jet miss in a quarter where GD told the street the number and hit it exactly, and with larger misses than GD's own stated figure in three more. A GD analyst finds that within a minute of opening `data/guidance.csv`.

Count: 6 S1 (one of them a publish-time gate I could not verify), 11 S2, 9 S3.

The three things I would fix first are at the end.

## What I ran

All scripts are in `~/gdn-prepub/agents/sellside/`. Each is read-only.

| Script | What it does |
|---|---|
| `guidance.py` | Rebuilds the guidance pace per held-out quarter from `data/guidance.csv` and `gd_deliveries.csv`, checks it against `results/holdout.csv`, checks for look-ahead |
| `guidance2.py` | What-ifs: GD's stated quarter figures, and the 2021 total GD implied |
| `split.py` | Average miss in 2023 to 2024 against the other 18 held-out quarters |
| `grepcalls.py`, `sents.py` | Sentences in the cached call transcripts (`data/raw/sources/calls/`) |
| `secfetch.py`, `spot.py`, `exh.py`, `doctext.py`, `docparas.py`, `subs.py` | Live fetches from sec.gov and parsing of the exhibits, the 10-K, the 10-Qs and the filing index |
| `serials.py`, `leasing.py`, `names.py`, `midyear.py`, `sums.py`, `lockwhatif.py` | What the registry events are, by model, year and registrant; the 2026Q3 estimates against GD's reported figures |
| `wb.py`, `wbtext.py`, `sitedata.py`, `hashes.py`, `bdiff.py`, `final.py` | Workbook formulas and labels, dashboard data, file hashes, build years of the other-model events |

Sources opened outside the repository: sec.gov (eight earnings exhibits 2024Q3 to 2026Q2, the 2026Q3 exhibit, the 2026Q3 10-Q, the 2025 10-K and its Exhibit 21, the 2024 10-K, the 2025Q1 10-Q, two 8-Ks, the filing index), the Motley Fool transcript of the 2026-10-30 call (through WebFetch, which summarises, so its quotes are approximate), the defense study's page, data file and README, and two web searches on G700 certification dates.

## Findings

| ID | Sev | Surface | Finding |
|---|---|---|---|
| SELL-1 | S1 | Post line 5, README:13, note, dashboard lead | "GD's guidance pace" ignores the quarter figures GD stated on its calls. With them, guidance's average miss is 6.0, not 6.9, and the registry is closer in 12 of 26 quarters, not 14 |
| SELL-2 | S2 | README:39, note.html:64 and :72, app.js:361 | "No 2021 call stated a full-year number" is narrowly true and reads as if GD gave no figure: three of the four 2021 calls gave delivery numbers |
| SELL-3 | S1 | note (HTML and both PDFs), dashboard, workbook | 2026Q3 revenue is still shown as an estimate with no actual. GD reported Aerospace revenue of $3,536M against the note's $2.7B |
| SELL-4 | S1 | `docs/INTERVIEW_NOTES.md`:9 and :27 | Says the first lock "is scored when GD reports", gives 31.1 and 20.4 to 36.4 |
| SELL-5 | S1 | `docs/RESUME_BULLETS.md`:2 | "the first, for 2026Q3, is scored on 2026-10-30", no result |
| SELL-6 | S1 | README:5, `output/charts/dashboard.png` | The README's front image shows "2026Q3 · PROVISIONAL", 31.1, "Locks the evening of 2026-10-29" |
| SELL-7 | S1 gate | Post lines 7 and 8 | Both links return 404 to an anonymous reader today. Not proven broken: the repository is private until launch |
| SELL-8 | S2 | Post line 3, README:97 to :101, :138 to :145 | The "registry count" is not a count of new deliveries, and the size of the gap is not stated |
| SELL-9 | S2 | `src/gdn/events.py`:15, PREREGISTRATION.md:23 | Registrations to Gulfstream Leasing LLC, a wholly owned GD subsidiary, count as customer deliveries |
| SELL-10 | S2 | README:13, :47 to :57 | The registry's whole edge over the guidance pace sits in 2023 and 2024, the G700 slip. Outside those years guidance was closer |
| SELL-11 | S2 | note.html:62 | The product-cycle section leaves out the G300 and the planned end of the G280 |
| SELL-12 | S2 | index.html:83, workbook `About!A9`, note Exhibit 10 | The defense baseline is not called an assumption on the dashboard or in the workbook, and the note shows no actuals |
| SELL-13 | S2 | Post line 1, README:92, dashboard live card | In the one live quarter both baselines were closer than the lock. No surface says so |
| SELL-14 | S2 | README:13, RESUME_BULLETS.md:1 | The README's prose headline and the resume bullet leave out the baseline that wins |
| SELL-15 | S2 | note.html:74, Sources | "GD reported 40" has no source in the note and no entry in `report/claims.json` |
| SELL-16 | S2 | note Exhibits 9 and 11, workbook `Sensitivity` | The "mechanical" label is missing in three places, and the method ignores a revenue split GD prints each quarter |
| SELL-17 | S2 | README:131, :141 | What GD's count includes is never described: fully outfitted aircraft, and test aircraft and demonstrators when sold |
| SELL-18 | S3 | note Risks | All eight risks are 10-K text. Item O3 is still open |
| SELL-19 | S3 | note.html:62 | "after FAA and EASA certification": first G700 deliveries came before EASA certification |
| SELL-20 | S3 | note.html:51 and :108, both PDFs | "Data as of 2026-10-29" over text that carries 10-30 facts; the PDF and its HTML source differ |
| SELL-21 | S3 | README:134, `report/claims.json`, `data/sec_manifest.json` | The stored sha256 of every SEC source I refetched did not match today's download |
| SELL-22 | S3 | workbook `About!A2`, `About!A8`, `Live` | A "before GD reports it" question; guidance named but absent; no reported count |
| SELL-23 | S3 | `output/charts/nowcast_path.png`, index.html:42, app.js:136 | Small stale labels on a scored quarter |
| SELL-24 | S3 | note Risks, tariffs | GD's later filings supersede the tariff sentence |
| SELL-25 | S3 | INTERVIEW_NOTES.md:5 and :18 | "that count drives the Aerospace segment" and "it is what the street anchors on" |
| SELL-26 | S3 | `docs/build/FACT_CHECK.md`:63 to :85 | Cites note text that no longer exists |

Detail for each follows under the question it belongs to.

---

## 1. Is the delivery count GD's count?

**Short answer.** The project's file of GD's counts is right. Its description of what GD counts is thin but not wrong. The registry event does not line up with GD's count in three specific ways the surfaces do not size, and one of them is a plain error an aviation reader will catch.

### What GD counts, from the filings

- The table is "Gulfstream Aircraft Deliveries (units)" with rows "Large-cabin aircraft", "Mid-cabin aircraft", "Total". The 2026Q3 exhibit (accession 0000040533-26-000036, fetched live) reads 35, 5, 40 for the quarter and 101, 18, 119 for nine months.
- GD's 2026Q3 10-Q (0000040533-26-000038) says it records new-aircraft revenue when the customer obtains control, "generally upon delivery and acceptance by the customer of the fully outfitted aircraft."
- The 2017Q1 exhibit (0000040533-17-000012) carries one delivery table with no green or outfitted split, and the footnote "Prior-period information has been restated for the adoption of ASC Topic 606, which we adopted on January 1, 2017." Its prior-year column reads 20 large and 8 mid, which is the 2016Q1 row of `gd_deliveries.csv`. The 2017Q4 exhibit reads 22 and 6 for 2016Q4, also as in the file.
- GD counts test aircraft and demonstrators when it sells them. 2022-01-26 call: "a number of test aircraft ... as well as a few demonstrators all up about 11 aircraft" of the 119 delivered in 2021.
- All nine quarters I parsed live (2024Q3 to 2026Q3) match `gd_deliveries.csv` and `2026Q3_score.json` on both cabins (`spot.py`, `exh.py`).

So README:131 ("the delivered basis it adopted with ASC 606 on 2017-01-01, so 2016 comes from the restated prior-year columns of the 2017 releases") is supported. I did not open a pre-2017 release, so I cannot confirm the old green and outfitted layout from a primary source.

### SELL-17 (S2). What the count includes is not described

- Surface: README:131, README:141 ("GD counts a delivery at its own handover"), note Limitations.
- Evidence: the 10-Q and call quotes above. No surface says "fully outfitted", and none says GD's count includes test aircraft and demonstrators when sold. `grep -n "outfitted\|demonstrator\|test aircraft" README.md report/note.html` returns nothing.
- Why it matters: the registry rule keys on a "first customer" and a one-year bound from first airworthiness. Ex-test and demonstrator airframes are exactly where that rule behaves oddly (see SELL-9).
- Fix: one sentence in the README Data section and the note's tracker section: "GD's count is fully outfitted new aircraft accepted by the customer, and it includes test aircraft and demonstrators in the quarter GD sells them."

### SELL-8 (S2). The registry count is not a count of deliveries, and the gap is not sized

- Surface: post line 3 ("I counted each Gulfstream jet's first customer registration or export"), README:97 to :101 ("keeps out renewed certificates and most used jets"), README:143 (Used jet), note.html:64.
- Evidence, `midyear.py` (registry E1 events against GD's count, by year):

```
year | registry large, GD large | registry mid, GD mid | registry total / GD total
2016 | 53 94   | 10 27 | 0.52
2019 | 96 114  | 21 33 | 0.8
2022 | 111 96  | 25 24 | 1.13
2025 | 167 136 | 25 22 | 1.22
2026 (2 quarters) | 97 66 | 15 13 | 1.42
```

- Evidence, `leasing.py`, the four quarters that scale the 2026Q3 lock (2026-10-29 snapshot):

```
four lag quarters  large: events 187 | models GD builds today 149 | other models 38 {'G-IV': 4, 'G1159B': 1, 'G-V': 4, 'GV-SP (G550)': 9, 'GVI': 2, 'GVI (G650)': 5, 'GVI (G650ER)': 13}
four lag quarters  mid  : events  28 | models GD builds today  27 | other models  1 {'GULFSTREAM G150': 1}
2026Q3 itself      large: events  35 | models GD builds today  31 | other models  4
2026Q3 itself      mid  : events   7 | models GD builds today   6 | other models  1
```

- Evidence, `final.py`, the build years of those 39 other-model events:

```
other-model events in the four lag quarters: 39
  by build year: {'no year': 4, 'built before 2020': 32, 'built 2020 to 2023': 3}
  G650 family (GVI, G650, G650ER): 20 build years: [('2013', 3), ('2014', 1), ('2015', 2), ('2016', 3), ('2017', 3), ('2018', 3), ('2019', 2), ('2020', 1), ('2021', 1), ('2023', 1)]
  trigger: {'customer_cert': 39}
```

- Reading: 38 of the 187 large-cabin events and 1 of the 28 mid-cabin events behind the live scale are on types GD does not build today. Of the 39, 35 carry a build year and none is later than 2023; four carry no year. So none can be shown to be a new aircraft delivered in those quarters, and 35 are used. GD also said on 2025-10-24 that 2025Q3 was "the first quarter where we had no deliveries of the high gross margin G650ER". Examples from `serials.py`: a G550 built 2009 (serial 5221) with a US airworthiness date of 2025-05-29 and an event on 2025-09-23; a G-V built 2003 (serial 5030) with an event on 2025-11-14.
- The README does name the mechanism (README:143, and the audit bullet at :145 reports five used jets in 30). What no surface says is how large it is in the quarters that set the live estimate, or that the registry now counts more events than GD delivers.
- Exploratory, after the fact, not preregistered (`lockwhatif.py`): the lock rebuilt on models GD builds today reads `31 x 140/149 = 29.1` large and `6 x 23/27 = 5.1` mid, total 34.2, a miss of 5.8 against the locked 8.0. One quarter proves nothing. It does show the used-jet share is not noise.
- `sums.py`: `2025: registry E1 events 192, GD deliveries 158`; `2026 first half: registry E1 events 112, GD deliveries 79`; `four quarters to 2026Q2: registry E1 events 215, GD deliveries 163`.
- Defensible version: "I count registry events, not deliveries. An event is a first non-Gulfstream registration or an export within a year of a US airworthiness date. In 2025 the registry held 192 such events against GD's 158 deliveries, and 39 of the 215 events in the four quarters to 2026Q2 were on types GD no longer builds, 35 of them airframes built in 2023 or earlier. The ratio rescales for this; it does not remove it."

### SELL-9 (S2). Gulfstream's own leasing subsidiary is read as a customer

- Surface: `src/gdn/events.py`:15 (`startswith("GULFSTREAM AEROSPACE")`), PREREGISTRATION.md:23, README:98 ("the first customer's registration certificate").
- Evidence, `leasing.py` on the stored 2026-10-19 and 2026-10-29 subsets:

```
MASTER N500GA sn 72001 GVII-G500  name GULFSTREAM LEASING LLC cert 20201113 | e1 2020-11-13 quarter 2020Q4 | this record is the event: True
MASTER N720GD sn 73002 GVII-G600  name GULFSTREAM LEASING LLC cert 20201113 | e1 2020-11-13 quarter 2020Q4 | this record is the event: True
MASTER N700GA sn 87001 GVIII-G700 name GULFSTREAM LEASING LLC cert 20251007 | e1 2025-10-07 quarter 2025Q4 | this record is the event: True
MASTER N800G  sn 88001 GVIII-G800 name GULFSTREAM LEASING LLC cert 20251007 | e1 2025-10-07 quarter 2025Q4 | this record is the event: True
events dated by one of these registrations, by quarter: {'2020Q4': 2, '2025Q4': 2}
```

- GD's 2025 10-K, Exhibit 21 (fetched live, `ex21-20251231.htm`): "Gulfstream Leasing LLC Georgia 100". It is a wholly owned subsidiary.
- These are serial 001 of the G500, G700 and G800 and serial 002 of the G600. Three of the four are on GA or GD tail numbers (N500GA, N720GD, N700GA), which the preregistration itself calls Gulfstream's test registrations; the fourth is N800G. The tracker counts the first-serial G700 and G800 as two customer deliveries in 2025Q4, one of the five largest misses (58.4 against 45).
- The rule also misses three DEREG records under the FAA's misspelling "GULFSTREAM AREOSPACE CORP"; none of those carries an event.
- Size: four events in the 26 held-out quarters. It will not move the headline. It is the detail an aviation reader repeats.
- The rule is preregistered, so do not change the scored numbers. Fix: add a Limitations bullet ("Own fleet: a registration to Gulfstream Leasing LLC, a GD subsidiary, reads as a customer; four held-out events are Gulfstream's own test airframes, two of them in 2025Q4"), and put the corrected rule in `results/exploratory/` for live quarters after this one.

### Where the project does say it cannot

Exports, military and special-mission airframes, handover timing, coverage drift and used jets each have a Limitations bullet (README:138 to :145), and the wording on military airframes ("may never reach the civil registry, though GD may count them") is properly hedged. I found no primary statement on whether GD's unit table includes special-mission airframes, so I could not test that bullet. The G280 scope rule (maker `IAI LTD`) is described the same way in the README, note and interview notes, and GD's filings support the Israel supplier point (2026Q3 10-Q: "delays including at our Israel-based supplier of mid-cabin airframes").

---

## 2. Is the guidance pace built the way the street would build it?

**Short answer.** No. It is a fair mechanical proxy for a year in which GD gives only a full-year number. It has no look-ahead. But GD often tells the street the coming quarter's number outright, the construction throws those away, and the headline figure depends on that.

### What checks out

`guidance.py` rebuilds every quarter from the two input files and matches `results/holdout.csv` to 1e-6 on all 26:

```
n 26 MAE guidance (rebuilt) 6.9173 sourced n 22 MAE sourced 7.3568 lookahead flags 0
```

Every outlook used comes from a call dated on or before the quarter's fiscal end, and every year-to-date count was filed before the quarter's own release. No outlook is used before it was public. The six blank rows outside 2021 (2022-04-27, 2022-10-26, 2024-04-24, 2025-04-23, 2025-10-24, 2026-04-29) hold no management full-year figure in the cached transcripts; the only "160" on the 2024-04-24 call is in an analyst's question.

### SELL-1 (S1). The baseline ignores the quarter figures GD stated

- Surface: post line 5, README:13 and :21, note.html:53 and Exhibit 2, dashboard lead, INTERVIEW_NOTES.md:7, RESUME_BULLETS.md:1. Rule: PREREGISTRATION.md:45 ("A call that ... gives only a quarter's plan, states none").
- Evidence, `grepcalls.py` on the cached transcripts, then `guidance2.py`:

```
2021Q3: GD said 32.0 on 2021-07-28 | repo pace 32.00 (miss 1.00)  | actual 31 | miss on GD's own figure 1.00
2021Q4: GD said 40.0 on 2021-10-27 | repo pace 40.00 (miss 1.00)  | actual 39 | miss on GD's own figure 1.00
2022Q2: GD said 26.0 on 2022-04-27 | repo pace 26.73 (miss 4.73)  | actual 22 | miss on GD's own figure 4.00
2022Q4: GD said 40.5 on 2022-10-26 | repo pace 41.00 (miss 3.00)  | actual 38 | miss on GD's own figure 2.50
2023Q2: GD said 26.0 on 2023-04-26 | repo pace 32.07 (miss 8.07)  | actual 24 | miss on GD's own figure 2.00
2023Q3: GD said 27.0 on 2023-07-26 | repo pace 43.07 (miss 16.07) | actual 27 | miss on GD's own figure 0.00

Repo as published:                              guidance avg miss 6.9173 | registry closer 14, further 12 | registry/guidance 0.798
B: explicit quarter plans where stated, else repo: guidance avg miss 6.0184 | registry closer 12, further 14 | registry/guidance 0.918
B1: only 2023Q3 swapped to GD's stated 27:        guidance avg miss 6.2990 | registry closer 13, further 13
C: B plus 2021Q1 and 2021Q2 from the implied 117:  guidance avg miss 5.7031 | registry closer 11, further 15 | registry/guidance 0.968
```

- The quotes. 2023-07-26, Novakovic: "We now expect to deliver 27 aircraft in the third quarter, with a rapid increase in the fourth quarter deliveries." GD delivered 27. 2023-04-26: "Looking forward next quarter, we expect to deliver 26 aircraft". 2022-04-27: "we expect to deliver 26 aircraft". Each call fell inside the quarter it guided, before that quarter's end, so each passes the project's own timing rule.
- Why this is the reading-stopper: an analyst on that July 2023 call had 27 in the model for the third quarter. The project's "GD's guidance pace" has 43.1 and books a 16-jet miss against GD. I found six such quarters by searching for "deliver" beside a digit; there may be more.
- Effect: with GD's own quarter figures, guidance's average miss is 6.0, the registry is closer in 12 quarters and further in 14, and the relative miss is 0.92. With 2021 read as GD implied it (SELL-2), 5.7, 11 against 15, and 0.97. The conclusion "not statistically distinguishable" survives. The number 6.9 and the phrase "GD's guidance pace" do not.
- The preregistered figure must stay as scored. The fix is naming and disclosure:
  - Call it what it is: "a pace I built from GD's full-year outlook", not "GD's guidance pace" (post, README, note, app.js:10 and :14) or "GD's own guidance pace" (the stale `dashboard.png`).
  - Add, labelled exploratory: "On six of the 26 quarters GD also stated the quarter's own delivery plan on its call. Using those figures instead, the outlook-based baseline misses by 6.0 on average and the registry is closer in 12 of 26 quarters."
  - INTERVIEW_NOTES.md:18 says the guidance pace "is what the street anchors on". The street anchors on the quarter figure when GD gives one. Reword.

### SELL-2 (S2). "No 2021 call stated a full-year number"

- Surface: README:39, note.html:72 (Exhibit 5 footnote), note.html:64 ("where no call gave a number"), app.js:361, INTERVIEW_NOTES.md:18.
- Evidence, from the project's own `data/guidance.csv` lines 6, 8 and 9 and the cached transcripts:
  - 2021-01-27, in the 2021 guidance section: "we will deliver 13 fewer G550s", then "So all up, 10 fewer aircraft." The same call states 2020's count: "127 deliveries versus our expectation of 130." That is 117 for 2021. GD delivered 119.
  - 2021-07-28: "we have planned 32 deliveries in the third quarter and 39 in the fourth", and later "We've got 71 deliveries to go".
  - 2021-10-27: "we will deliver 40 aircraft in the fourth quarter."
- So "no call stated a full-year number" is true in the narrow sense that no one sentence held the total, and the preregistered rule reads the rows correctly. It is misleading to anyone who covered GD: a reader takes it, and the note's "where no call gave a number" (note.html:64), to mean GD gave no delivery figure for 2021, when a model built on the January call had 117 in it. I rate it S2 for that reason; it is still in my first fix because it sits under the headline comparison.
- Fairness of the fallback: for 2021Q3 and 2021Q4 the same quarter last year happens to equal GD's stated plan (32 and 40), so no harm. For 2021Q2 the fallback is 32 against an actual 21, an 11-jet miss charged to "guidance" in a quarter GD had flagged on 2021-04-28 as "our most challenging from a delivery perspective". Spreading 117 the project's own way gives 25.39 for 2021Q2 (`guidance.py`, what-if A: guidance average miss 6.6567, registry closer in 13, further in 13).
- Under PREREGISTRATION.md:45 the rows are read correctly ("a stated change from a figure named in the same sentence"; "only a quarter's plan, states none"). So keep the scored number and fix the sentence. Defensible version: "GD's 2021 calls gave no single full-year total. In January GD said 10 fewer aircraft than 2020's 127, and from July it gave quarter plans (32, then 39 or 40). My preregistered rule reads none of these as an outlook, so 2021 falls back to the same quarter last year. Reading January's statement as 117 lowers the baseline's average miss from 6.9 to 6.7."

### SELL-10 (S2). The registry's edge is the G700 slip

- Surface: README:13 and the year table at :47 to :57, post line 5.
- Evidence, `split.py`:

```
ratio     all 26: 5.52 | 2023-2024 (8 quarters): 3.48  | other 18: 6.43 | share of total miss from 2023-2024: 19.4%
guidance  all 26: 6.92 | 2023-2024 (8 quarters): 12.51 | other 18: 4.43 | share of total miss from 2023-2024: 55.7%
other 18 quarters: registry closer than guidance in 6 | further in 12
2023-2024: registry closer than guidance in 8 of 8
```

- GD stated the cause, so the project's rule on causes is met. 2023-10-25: "we anticipate in excess of 60 deliveries in the quarter, assuming we're granted FAA certification before the end of the year." 2024-01-24: "we did not receive the certification of the G700 in the fourth quarter and did not deliver 15 aircraft we had ready to go."
- The year table shows the numbers. No sentence says the comparison reverses outside those two years. A reader of the post takes "5.5 against 6.9" as a general result.
- Defensible version: "The registry was closer than the outlook-based pace in all eight quarters of 2023 and 2024, when the G700's certification slipped and GD's full-year outlooks did not hold. In the other 18 quarters the pace missed by 4.4 and the registry by 6.4."

### Smaller points

- `data/guidance.csv` stops at 2026-07-29 and README:132 says so. The 2026Q4 pace in `site/data.json` (41.0) therefore rests on the July outlook. The Motley Fool transcript of the 2026-10-30 call, as WebFetch relayed it, has Novakovic saying "We do not plan to update segment guidance", so 160 stands, but the row for that call should be added before the 2026Q4 lock.
- The weights for 2021 to 2023 pool 2020, a pandemic year. Disclosed by construction, no finding.

---

## 3. Is the Aerospace revenue estimate labelled as mechanical everywhere it appears?

**Short answer.** Labelled in most places, missing in three. Every place still presents it as an estimate for a quarter GD has reported, and no surface gives the actual.

### Where it appears

| Place | Label present | Says what GD reported |
|---|---|---|
| note.html:55, summary point 3 | Yes ("a mechanical estimate") | No |
| note Exhibit 8 and footnote (note.html:78) | Yes | No |
| note Exhibit 9 (note.html:79) | **No** | No |
| note Exhibit 10, "2026Q3 estimate" column | Not applicable (defense) | No |
| note Exhibit 11, "Derived" rows (note.html:98) | **No** | No |
| workbook `About!A9`, `Segments!A20` | Yes | No |
| workbook `Sensitivity` sheet | **No** | No |
| dashboard, "What it means for GD" (index.html:83, app.js:383 to :404) | Yes | No |
| `results/estimates.json`, `site/data.json` | Data only, no label field | No |
| README:109, "The dollars" | Yes, no figures | Not applicable |
| INTERVIEW_NOTES.md:24 | Yes ("only mechanically") | Not applicable |

### SELL-3 (S1). 2026Q3 revenue is shown as an estimate with no actual

- Surface: note.html:51 to :55, :74 to :84 (and both PDFs, which are byte-identical, sha256 `7f661070...`), index.html:81 to :89 with app.js:383 to :404, workbook `Live` and `Segments`.
- Evidence, the 2026Q3 earnings exhibit fetched live from sec.gov (accession 0000040533-26-000036, `exh.py`):

```
Revenue:
Aerospace | 3,536 | 3,234 | 302 | 9.3
Marine Systems | 4,960 | 4,096 | 864 | 21.1
Combat Systems | 2,386 | 2,252 | 134 | 6.0
Technologies | 3,684 | 3,325 | 359 | 10.8
Total | 14,566 | 12,907 | 1,659 | 12.9
Operating earnings: Aerospace 513, Marine Systems 391, Combat Systems 330, Technologies 346
```

- Against the project's figures (`lockwhatif.py`):

```
Aerospace, delivery estimate: estimate 2710, GD reported 3536, miss -826 $M (-23.4%)
Aerospace, drift: estimate 3631, GD reported 3536, miss +95 $M (+2.7%)
Marine Systems: estimate 4775, GD reported 4960, miss -185 $M (-3.7%)
Combat Systems: estimate 2325, GD reported 2386, miss -61 $M (-2.6%)
Technologies: estimate 3382, GD reported 3684, miss -302 $M (-8.2%)
Total, four segments: estimate 13193, GD reported 14566, miss -1373 $M (-9.4%)
segment operating earnings: estimate 1372 vs reported 1580 (Aerospace 513 vs 375 estimated)
revenue check: 40 x 84.82 = 3393.0 $M vs reported Aerospace revenue 3536 $M
```

- The note was updated for the delivery count ("GD reported 40", note.html:54 and :74) and not for revenue. It says the estimate "implies $2.7B of Aerospace revenue for 2026Q3, against $3.2B a year earlier" in the present tense. GD reported $3.5B, up 9.3%. The estimate pointed to a 16.2% fall on the year-ago quarter and GD reported a 9.3% rise (`sums.py`). Showing the delivery actual and leaving out the revenue actual reads as selective even if it is only an unfinished update.
- The same note carries a section titled "What the street watches on the print" (note.html:83) and "GD's own outlook for 2026" (note.html:79) written before the print: 79 jets in the first half (now 119 through nine months), a 1.5 Aerospace book-to-bill for 2026Q2 (1.4x for 2026Q3), Marine Systems margin 7.3% (7.9% in 2026Q3), Aerospace margin 14.5% and 14.7% for the half (14.5% and 14.7% for nine months, unchanged).
- The dashboard's table is captioned "2026Q3 revenue by segment against the year-ago quarter" with an "Estimate" column, and its note says the estimate "sits below the 39 deliveries of 2025Q3 ... so the delivery-based figure falls" (app.js:399). GD delivered 40 and the figure rose.
- Fix: add a "GD reported" column and a miss column to Exhibit 8, Exhibit 10 and the dashboard table; put the actual in summary point 3; retitle the street section as written before the print or rewrite it for 2026Q4; date the note by its last edit. Defensible sentence for point 3: "The delivery estimate implied $2.7B of Aerospace revenue for 2026Q3; GD reported $3.5B. Scaling last year's quarter by trailing growth gave $3.6B. Even at GD's actual 40 deliveries the per-delivery method gives $3.4B, because services do not move with deliveries."

### SELL-16 (S2). Label gaps, and a split GD prints that the method ignores

- Exhibit 9 (note.html:79), Exhibit 11's Derived rows (note.html:98) and the workbook's `Sensitivity` sheet show delivery-based Aerospace revenue with no "mechanical" label. The Exhibit 11 rows also show "Aerospace operating earnings from the estimate $0.4B", which is the mechanical revenue times a trailing margin.
- GD's 10-Q splits Aerospace revenue. 2026Q3 10-Q, Note on revenue (`doctext.py`): "Aircraft manufacturing $ 2,452 ... Aircraft services 1,084" for the quarter. The $85M per delivery is total Aerospace revenue, services included, over deliveries. A per-delivery figure on aircraft manufacturing revenue alone, with services carried forward separately, is the version an analyst would build, and the inputs are public.
- Fix: repeat the label under Exhibits 9 and 11 and on the `Sensitivity` sheet. State in Limitations that GD reports manufacturing and services revenue separately and the estimate does not use the split.

---

## 4. Does the note's defense half overreach?

**Short answer.** The note does not. It states the assumption in plain words. The dashboard and the workbook use the same figures without that statement, and no surface reports how the figures did.

- The study's numbers check out. The study's data file (`data.json` on the study's site, key `ALL`, through WebFetch) gives 9.892, 7.310 and 6.524 for the next quarter and 9.400, 5.763 and 6.039 for four quarters, over HII, LHX, LMT, NOC and RTX. The study's README gives the same as 9.9%, 7.3%, 6.5% and 9.4%, 5.8%, 6.0%, and says of GD: "Its 10-Qs last tagged remaining performance obligations for the quarter ended September 2018". The note's paragraph (note.html:82) matches on every figure. I could not confirm the study's exact growth formula; its README says only "scales it by trailing growth".
- The note's sentence "Applying that study to GD is an assumption: it did not test GD" is the right strength. README:109 says the same. No defense sentence in the note claims accuracy for GD.

### SELL-12 (S2). The assumption label is missing on two surfaces, and there are no actuals

- index.html:83: "The defense segments use the same quarter last year scaled by trailing growth." No word that this is borrowed from a study of other companies.
- Workbook `About!A9`: "defense segments use the seasonal naive with drift." Same gap. `Segments!L1` is headed "Drift 2026Q3".
- Note Exhibit 10 is headed "Backlog, 2026Q2" and shows Marine Systems at $65.2B and 3.64 years. That was right at 2026Q2 (live exhibit: 65,182). The 2026Q3 exhibit shows Marine Systems total backlog of 146,865, and the release headline reads "6.8-to-1 book-to-bill, $220 billion backlog". GD's 2026Q3 10-Q: total backlog "was $220.3 billion at the end of the third quarter of 2026 compared with $136.5 billion at the end of the second quarter." The label is dated, so the figure is not wrong, but a reader on or after posting day sees a coverage table from before that change.
- The defense figures did reasonably: misses of 3.7%, 2.6% and 8.2% (above), against 17.4%, 5.6% and 9.7% for the same quarter last year with no drift (`lockwhatif.py`). Reporting that is the honest and the flattering thing to do. Three data points on GD are still not a test.
- Fix: add "applying it to GD is an assumption" to the dashboard sentence and the workbook `About` sheet. Add the 2026Q3 actuals beside the estimates.

---

## 5. Do the note's risks read as generic 10-K text?

**Yes. Item O3 is still open, and the print has made it worse.**

The eight risks (note.html:85 to :86, each cited to the 2025 10-K):

| Risk as printed | Verdict |
|---|---|
| "if Aerospace customers default on existing contracts and the contracts are not replaced ..." | Boilerplate. Aerospace-specific but nothing to do with a delivery count |
| "customer demand for its business aircraft can be affected by changes in general economic conditions, the availability and cost of credit ..." | Boilerplate |
| "it typically assumes more risk with fixed-price contracts ..." | Boilerplate, and about the defense businesses |
| "non-U.S. transactions can involve increased risks from foreign exchange rate variability ..." | Boilerplate |
| "many of its new products must meet extensive, time-consuming regulatory requirements ..." | Generic wording for the one risk that drove the backtest (G700 certification). Not tied to it, to the G400 or to the G300 |
| "it sometimes relies on only one or two sources of supply ..." | Generic wording for the G280 and its Israel supplier. Not tied to it |
| "tariffs had not had a material impact ... but reduced Aerospace operating margins by 30 basis points in 2025" | Specific and dated, but superseded (SELL-24) |
| "decreases in U.S. government defense and other spending ..." | Boilerplate |

None is specific to the tracker. The risks that are specific to this tracker and this stock sit elsewhere or nowhere:
- the 41 deliveries the fourth quarter needs to reach 160 (160 less 119), with GD saying on 2026-10-30 it would not update segment guidance;
- the G280's end and the gap to the G300 (SELL-11), which takes the mid-cabin count toward zero for some quarters in 2027;
- G700 and G800 mix and lot maturity, which GD cites for margin;
- the certification timing of the G400 and G300.

The "Limitations of the method" list that follows the risks is specific, well written and is the part a reader will trust. **SELL-18 (S3):** lead the Risks section with three Gulfstream risks tied to cited GD statements, and keep at most two of the 10-K lines.

**SELL-24 (S3).** The tariff sentence is attributed to "its 2025 annual report", which keeps it accurate. GD's 2026Q3 10-Q now says: "the U.S. Supreme Court held that tariffs imposed under the International Emergency Economic Powers Act (IEEPA) were unauthorized" and "tariffs as applied in their current form and tariffs yet to be refunded are not material to our results of operations." Cite the later filing.

---

## 6. Segment, backlog, book-to-bill and margin figures

**All clean.** `spot.py` fetched the eight exhibits behind `segments.csv` live from sec.gov and compared 64 cells (revenue and operating earnings, four segments, eight quarters): `segment cells compared: 64 mismatches: 0`. Each live document equals the cached copy once sec.gov's injected script tag is removed.

| # | Figure in the note or workbook | From the live exhibits | Result |
|---|---|---|---|
| 1 | Aerospace revenue, four quarters to 2026Q2, $13.8B | 13,826 | Match |
| 2 | Marine Systems $17.9B, Combat Systems $9.4B, Technologies $13.8B | 17,917; 9,360; 13,758 | Match |
| 3 | Shares 25.2%, 32.7%, 17.1%, 25.1% | 25.2, 32.7, 17.1, 25.1 | Match |
| 4 | Operating margins 13.8%, 7.2%, 14.4%, 9.4% | 13.8, 7.2, 14.4, 9.4 | Match |
| 5 | Backlog 2026Q2: $24.0B, $65.2B, $29.4B, $18.0B | 23,977; 65,182; 29,350; 17,989 | Match |
| 6 | Book-to-bill 2026Q2: 1.5 Aerospace, 1.4 defense, 1.4 company | "1.4-to-1 ... for the defense segments, 1.5-to-1 for the Aerospace segment, and 1.4-to-1 on a company-wide ba[sis]"; table 1.5x | Match |
| 7 | Aerospace margin 14.5% in 2026Q2, 14.7% first half | 14.5, 14.7 | Match |
| 8 | Marine Systems margins 2025Q3 to 2026Q2: 7.1, 7.2, 7.3, 7.3 | 7.1, 7.2, 7.3, 7.3 | Match |
| 9 | 2025Q3 actuals $3.2B, $4.1B, $2.3B, $3.3B, total $12.9B | 3,234; 4,096; 2,252; 3,325; 12,907 | Match |
| 10 | Deliveries: 163 over four quarters, 79 in the first half, $85M per delivery | 163; 79; 84.82 | Match |
| 11 | Drift estimates $3.6B, $4.8B, $2.3B, $3.4B (workbook `Segments!L2:L5`) | 3,631; 4,775; 2,325; 3,382 | Match |
| 12 | 2026Q3 reported deliveries 35, 5, 40 (`2026Q3_score.json`) | 35, 5, 40 | Match |

Coverage in years (1.73, 3.64, 3.14, 1.31) is backlog over trailing revenue from rows 1, 2 and 5 and agrees with `results/estimates.json`.

**SELL-15 (S2).** The note's most important number, "GD reported 40", has no source. The Sources list (note.html:108, item 8) ends at accession 0000040533-26-000029, the 2026Q2 release, and `report/claims.json` has 31 entries, none for the 2026Q3 count. Add 0000040533-26-000036.

**SELL-21 (S3).** README:134 offers "the sha256 of the cached source" as the check on each claim. Every SEC source I refetched today hashed differently from the stored value: the nine exhibits against `data/sec_manifest.json` (`spot.py`, for example 2026Q2 live `575b749966fb` against manifest `8e584f9a813f`), and three filings against `report/claims.json` (`final.py`: the 2025 10-K, claims `0200d601a9b15c4d` against live `88868a5ae7f4a86e`; likewise the 2024 10-K and the 2025Q1 10-Q). On the two files I diffed byte by byte (`bdiff.py`: the 2026Q3 exhibit, lengths 335,542 and 335,549; the 2025 10-K, lengths 2,454,442 and 2,454,440) the only differing bytes are the path inside a `<script type="text/javascript" src="/...">` tag that sec.gov appends before `</body>`. That path was the same across my own fetches today and different in each of the project's cached copies, so it changes over time. I did not test how often. Hash the document with that tag stripped, or say the hash covers the bytes as fetched and may not match a later download.

---

## 7. Product-cycle facts

| Claim in the note (note.html:62) | Check | Result |
|---|---|---|
| "The G500 entered service in 2018 and the G600 in 2019." | 2025 10-K, live: "The G500 and G600 entered service in 2018 and 2019, respectively." | Correct |
| "Gulfstream began G700 deliveries in the second quarter of 2024, after FAA and EASA certification." | 2024 10-K, live: "began deliveries in the second quarter of 2024 following U.S." [FAA and EASA certification] | Faithful to GD's wording; order is off (SELL-19) |
| "The FAA and EASA type certified the G800 on 2025-04-16." | 2025Q1 10-Q, live: "On April 16, 2025 ... G800 received type certification from the U.S." | Correct |
| "G800 deliveries began in the third quarter of 2025." | 2025 10-K, live: "the G800 that began deliveries in the third quarter of 2025" | Correct |
| "G650 production ended in the first quarter of 2025, and the G800 replaces it." | 2025Q1 10-Q, live: "The G800 is the replacement aircraft for the G650, which correspondingly ended production in the first quarter of 2025." | Correct. Final deliveries ran into 2025Q2 (2025-07-23 call: "we made the final deliveries of this high-margin product") |
| "a non-U.S. partner assembles the mid-cabin G280" and the IAI joint-effort quote | 2024 10-K and the archived 2012 release, cached | Correct as quoted; see SELL-11 for what is missing |
| "On its 2026-07-29 call, GD said it had stepped up its work on the G400 and would say more over the following couple of quarters" | Cached transcript: "we've whipped up our efforts on the 400, and we'll have more to say over the next couple of quarters" | Correct. One of those quarters has passed |

### SELL-11 (S2). The G300 and the end of the G280 are missing

- Surface: note.html:62 (product cycle) and the G280 bullet at note.html:84.
- Evidence:
  - 2025 10-K, live, the same filing the note cites for the G500 and G600: "In the second half of 2025, we announced the all new, super midsize G300 ... The aircraft will replace the G280".
  - 2026-07-29 call, cached, two sentences before the G400 sentence the note quotes: "the final 280 ought to deliver in the second quarter of next year, and the onset of the 300, which late '27, early '28", then "we'll have a planned production break".
  - 2026-10-30 call, Motley Fool through WebFetch (approximate wording), Danny Deep: the G280s "finish delivery" around the middle of next year; "we expect the G300 to be certified towards the end of next year"; "our intent is to deliver 200 aircraft in 2030." The G400 does not appear in what WebFetch returned.
  - `grep -rn G300` over the README, note, site, source and data finds no mention. `docs/build/FACT_CHECK.md`:63 to :85 shows two G300 claims were in an earlier draft and were flagged for wording, minor. They were removed, not reworded.
- Why it matters here: the tracker's mid-cabin leg is the G280 alone. GD has said those deliveries end in mid-2027 with a gap before the G300. The ratio's mid-cabin term divides by the last four quarters of mid-cabin events, so the method's behaviour through that gap is a stated product-cycle fact the note should carry, and a note on Gulfstream's product cycle that omits the newest announced model looks out of date.
- Fix: restore both claims with the wording FACT_CHECK.md proposed, and add one line to Limitations on the 2027 mid-cabin gap.

**SELL-19 (S3).** FAA certification of the G700 was announced on 2024-03-29, first customer deliveries followed in April, and Gulfstream's EASA release is dated 2024-05-15 (web search results, including the gd.com article path `/Articles/2024/05/gulfstream-g700-earns-easa-certification`). So deliveries began before EASA certification. The note copies the 10-K's compressed wording. Defensible version: "Gulfstream began G700 deliveries in April 2024, after FAA certification on 2024-03-29; EASA certification followed in May."

**SELL-26 (S3).** `docs/build/FACT_CHECK.md` is public from the README in two clicks and says `report/note.html:62` prints the G300 text. It no longer does. Add a line to that file saying the claims were removed, or restore them.

Context an analyst will know and the note need not carry: GD's 8-K of 2026-10-08 (0001193125-26-417188) says the board "elected Danny Deep as Chief Executive Officer, effective January 1, 2027". The note attributes its July quotes correctly.

---

## Also report

### Numbers that differ between two surfaces

| Where | One surface | The other |
|---|---|---|
| README:5 image `dashboard.png` against README:92 | 31.1, band 20.4 to 36.4, "PROVISIONAL", "Locks the evening of 2026-10-29" | 32.0, band 21.2 to 37.2, locked 01:51 ET, GD reported 40 |
| INTERVIEW_NOTES.md:27 against the post | "My build estimate is 31.1 deliveries, with a band of 20.4 to 36.4" | "locked an estimate of 32.0" |
| note.html:108 against both PDFs | "newest dated 2026-11-11" | "newest dated 2026-10-30" (PDF page 7, item 9) |
| note.html:51 | "Data as of 2026-10-29" | The same page reports GD's 2026-10-30 count |
| Workbook `About!A8` against the workbook | "scored against seasonal, last-quarter and GD guidance baselines" | No guidance column or average in `Quarters` or `Summary` |
| Workbook `Live` against README:92 | Ends at the estimate and band | GD reported 40, miss 8.0 |
| README:13 against post, note and dashboard | No sentence on the same quarter last year | "Simply repeating the same quarter last year missed by less on average, 4.6" |
| INTERVIEW_NOTES.md:30 against README:156 | "GitHub's runner downloaded the registry even though it was expected to be blocked" | "bot blocking that has refused GitHub's runners" (both may be true at different times; say which) |

Every other cross-surface figure I compared agrees: 5.5, 6.9, 4.6, 8.8, 6.2; 14, 12, 0.423; 22 of 26 and 7.4; 5.3 on the 22 quarters (5.2503); 18 of 26; 32.0, 21.2 to 37.2, 33.8, 40, 8.0; the lock time and the sha256 (`gh release view lock-2026Q3`: `publishedAt 2026-10-29T05:51:24Z`, body `sha256 3c4cdbd0...`, equal to the hash of `predictions/2026Q3.json`).

### Stale sentences about the live quarter

**SELL-4 (S1).** `docs/INTERVIEW_NOTES.md`, last changed 2026-10-19 (`git log`):
- line 9: "The first lock is scored when GD reports on 2026-10-30."
- line 27, under "What did the locked quarter show?": "My build estimate is 31.1 deliveries, with a band of 20.4 to 36.4. It locks on 2026-10-29 ... One quarter will show how the method behaves live".
- Fix: "I locked 32.0 (band 21.2 to 37.2) at 01:51 ET on 2026-10-29. GD reported 40 the next morning: a miss of 8.0, outside the band. The outlook-based pace was 33.8 and the same quarter last year was 39, so both were closer."

**SELL-5 (S1).** `docs/RESUME_BULLETS.md`:2: "the first, for 2026Q3, is scored on 2026-10-30". Fix: "the first lock, for 2026Q3, missed by 8.0 (32.0 against GD's 40)". Line 1 gives "5.5 ... vs 6.9 for guidance, not significant" and omits the 4.6 (SELL-14).

**SELL-6 (S1).** `output/charts/dashboard.png` (file dated 2026-10-19) is the first thing on the repository page. I opened it: "2026Q3 · PROVISIONAL", "31.1 deliveries, estimated", "Band of past misses: 20.4 to 36.4", "GD reports 2026-10-30", "Locks the evening of 2026-10-29". Retake it from the current dashboard.

**SELL-3** covers the note, dashboard and workbook.

**SELL-20 (S3).** The PDFs were built on 2026-10-30 and `note.html` has been rewritten daily since; date the note by its last content change and rebuild the PDF from the same source.

**SELL-23 (S3).** `nowcast_path.png` is current (GD reported 40, the lock diamond, the pace line) but its source line says "FAA aircraft registry snapshot 2026-10-19" over a path that runs to 2026-10-30. On the dashboard a scored quarter still reads "32.0 deliveries, estimated" and "GD reports 2026-10-30" in the present tense (index.html:42, app.js:136).

The other four charts I opened (`track_record.png`, `coverage.png`, `signed_errors.png`, `nowcast_path.png`) carry no stale statement about the live quarter. `2026Q4`: README:93 says no estimate is shown yet, and the dashboard does keep the scored 2026Q3 card up, as its code intends.

### Claims of counting before GD, or of beating GD or the market

None found as a claim. `grep -rn -i "beat\|before GD report\|outperform\|edge"` over the post, README, note, site and owner documents returns only the lock wording ("locked ... before GD reported", which the release timestamp supports), the interview line "I report it as a tracker, not as an edge", and the framing sentence. The framing sentence appears in the post, README:11, note.html:53 and :65, the dashboard and the interview notes.

Two soft spots:
- **SELL-22 (S3).** Workbook `About!A2`: "can they estimate the count before GD reports it?" It is a question, not a claim, but it is the one place the forbidden idea appears. Reword to "how closely do they track it, and does a locked estimate hold up?"
- **SELL-13 (S2).** The post's first line gives the miss and stops. `results/live/2026Q3_score.json` has `guidance_ae 6.16` against `ae_total 8.05`, and the same quarter last year was 39 against 40. README:92 and note.html:54 print 33.8 and 39 but do not say either was closer. The post says "Simply repeating the same quarter last year missed by less" for the backtest only. A reader who checks will see the lock finished last of three. Say it first: "GD's outlook-based pace (33.8) and last year's quarter (39) were both closer."

**SELL-14 (S2).** README:13's bold headline is the rule's sentence and nothing more. The table two lines below shows 4.6 for the same quarter last year and a relative miss of 1.20, so nothing is hidden, but the post, note and dashboard all say it in words and the front page does not. Add the sentence. Same for RESUME_BULLETS.md:1.

**SELL-25 (S3).** INTERVIEW_NOTES.md:5: "that count drives the Aerospace segment." In 2026Q3 deliveries rose by one and Aerospace revenue rose 9.3%, with services at $1,084M of $3,536M. "Is the largest single driver of" is defensible.

### SELL-7 (S1 gate). The post's links

WebFetch on 2026-11-11 returned HTTP 404 for `https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/` and for `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast`. The repository is private today, so this is expected and I cannot call either link broken. It is a gate: the dashboard link needs GitHub Pages switched on as well as the repository made public, and `config/calendar.json` still reads `"public": false`. Check both links, the README's release link and the PDF link from a signed-out browser before the post goes up.

---

## GO or NO-GO

**NO-GO today.** Reasons, in the order a reader meets them:

1. The README's first image and two owner documents say the quarter is unscored (SELL-4, SELL-5, SELL-6).
2. The note and dashboard give a 2026Q3 Aerospace revenue estimate of $2.7B as if GD had not reported $3.5B (SELL-3).
3. The lead comparison is against a baseline named "GD's guidance pace" that differs from the quarter figure GD stated in four quarters, by up to 16 jets, and the sentence that explains 2021 sits beside quotes in the project's own file that give 2021 delivery numbers (SELL-1, SELL-2).

None of this touches the lock or the score, which I traced to the release timestamp, the file hash and GD's filing. I rebuilt the guidance column and checked the delivery and segment inputs against SEC. I did not rescore the ratio model. The fixes are text, one screenshot, three table columns and two labelled exploratory lines.

**The three things I would fix first**

1. **The guidance baseline's name and its disclosure.** Rename it as a pace built from the full-year outlook. Rewrite the 2021 sentence. Add the exploratory line (6.0 with GD's stated quarter plans; registry closer in 12 of 26) and the 2023 to 2024 split (8 of 8 against 6 of 18). Keep 6.9 as the preregistered figure.
2. **Bring every 2026Q3 surface past the print.** Actuals beside every estimate in the note, dashboard and workbook; the street section rewritten; interview notes, resume bullets and the README image updated; the 2026Q3 release added to the note's sources; the PDF rebuilt.
3. **Say what the registry event is.** Events, not deliveries: more events than deliveries since 2022, 39 of the last 215 on types GD no longer builds, Gulfstream Leasing LLC read as a customer, and the G280's end in 2027. One paragraph in the README and the note.

## What I could not check

- The pre-2017 green and outfitted delivery table; I opened no release earlier than 2017Q1.
- Whether GD's unit table includes special-mission or military airframes; I found no primary statement.
- The 2026-10-30 call beyond WebFetch's summary of the Motley Fool page. Its quotes are approximate, and "the G400 is not mentioned" is unconfirmed.
- The defense study's growth formula.
- The post's links for a public reader (SELL-7).
- The ratio backtest itself. I rebuilt the guidance column and checked the registry counts of four quarters against `serials.csv`; I did not rescore the ratio model.
- There may be more calls with a stated quarter figure than the six in SELL-1. My search was for "deliver" beside a digit.
- Process note: one repository-wide `grep` printed a single truncated line from another reviewer's file under `docs/prepub/reviews/` (a claim text that is also in `report/claims.json`). I read nothing else there.
