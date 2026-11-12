# Round 4: FAA registry and data engineer (`registry`)

Verdict: GO. Every registry figure on the public surfaces I checked rebuilds exactly from the stored subsets; what I found is one untested branch that feeds the count and five gaps in disclosure or robustness, none of them shown to change a headline, backtest or locked figure.

Counts: S1 0, S2 1, S3 5

Tree read: the cold copy at `~/gdn-prepub/round4/`. Scripts and outputs: `~/gdn-prepub/agents/round4_registry/` (`a1_integrity.py` to `a20_mae.py`), run with the project's Python 3.11 environment and the project's own `src/gdn` code, read-only, on the stored subsets and daily tables only. No FAA zip was fetched.

## Answers

**1. The airframe key (`events.py:32`, `code[:3]` plus upper-cased serial).**
- Collisions exist. Under prefix `450`, G100 and G200 serials 139 to 156 share keys, and G200 and G150 serials 204 to 250 share keys. Under `398`, a G-IIB record and a G150 record share serial 245. In all, 47 keys span two cabins or carry `YEARMFR` values two or more years apart (`a4_main.py`, section B).
- A merged key takes the older airframe's airworthiness date, so the bound drops the other airframe's later certificates. Keying by prefix, serial and model family instead adds 7 mid-cabin events in five held-out quarters. All 7 are G150 or G200 records with certificates dated 2021 to 2024. Five carry their own `YEARMFR` of 2007 to 2011, which makes them old airframes by the project's three-year test, and two have no year. So the collision mostly removes old airframes, by accident (REGISTRY-4).
- The cross-cabin collision at 398/245 moves nothing. Its 2025Q4 event belongs to the G-IIB record, and the G150 record carries no date. A key of prefix, serial and cabin gives the same quarterly counts as the tracked file in every quarter.
- Splits: a key of serial and cabin with no prefix changes exactly 2018Q2 and 2026Q2, by one mid-cabin event each. Those are the two double counts the README discloses (G150 serial 322 and G280 serial 2009).
- No serial variants within one prefix: with leading zeros and punctuation stripped, nothing merges.
- The FAA's third G280 code, `398012B`, appeared in the 2026-10-27 subset. So far it holds one record (G280 serial 2024) with no dates, so no event yet.

**2. E1, E2 and the bound (`events.py:37-58` against `PREREGISTRATION.md:29-30` and `README.md:111-115`).** The code matches the text field for field: the customer certificate, the Gulfstream cancellation, the export cancellation with the alphabetical tie-break, the earliest airworthiness date, the `(19|20)\d\d` year rule, the 365-day bound, the 31 December fallback, and a blank bound when neither date exists. Rebuilding with the project's functions reproduces `data/processed/serials.csv` and `registry_quarterly.csv` byte for byte (`a1_integrity.py`). Edge cases:
- Neither date: 386 of 4,053 airframes, supplying 75 of the 1,251 counted events. This branch has no test (REGISTRY-1).
- Year fallback only: it fires for no counted event from 2016Q1 to 2026Q2. Three airframes have a year, no airworthiness date and a candidate date.
- One-sided bound: 189 counted events are dated before the earliest airworthiness date the file shows. 31 are more than 365 days before it, for example a G-IV whose `YEARMFR` reads 1989, registered on 2020-07-23, whose airworthiness date reads 2025-12-19. These are covered by the README's used-jet wording.
- No counted event falls in a year before its `YEARMFR`.

**3. Used-jet leakage.** By the registry's year of manufacture, 246 of the 1,251 events from 2016Q1 to 2026Q2 (19.7%) are on airframes at least three years old, and 76 have no year. In the held-out quarters the figures are 186 of 913 and 58 with no year.
- The 2026Q3 lock: 5 of its 42 events are on airframes at least three years old, and 7 have no year. All of these figures match the README.
- The field is noisy. One of the lock's five is a GVIII-G700 (serial 87118) whose `YEARMFR` reads 2006 while its earliest airworthiness date is 2026-03-06. A G-IV (serial 1335) with no year and no airworthiness date is not among the five.
- The lock count went from 41 to 42 on the 2026-10-27 snapshot. That day a G150 whose `YEARMFR` reads 2014 lost its 2014-03-23 airworthiness record, so its earliest date became 2026-09-02 and its 2026-08-26 certificate passed the bound (`a6_diff.py`).
- Where the size is stated: the Live record (`README.md:106`) and the note's first page give 5 of 42. The README Results table (`README.md:30`) and the dashboard show the raw count with no size, which is given only in Limitations (`README.md:157`) (REGISTRY-6).

**4. Cabin classes.** The 11 airframes the README names (codes `3980202`, `3980211`, `3980401`, `3980404`, model strings without the `G100/G150/G200/G280` patterns) are filed as large and have no event from 2016Q1 to 2026Q2, which confirms `README.md:157`. No other mis-filing changes a count (see answer 1). The new code `398012B` is filed as mid, which is correct. Of the lock's 7 mid-cabin events, one is the G150 above.

**5. MASTER and DEREG.** One key gathers both files (`events.py:27-32`), so an airframe cannot count twice across them unless its prefix differs (answer 1).
- Sources of the 1,251 E1 events: a MASTER certificate for 884, a DEREG certificate for 88, and a Gulfstream export cancellation for 279.
- `STATUS-CODE` is never read (`faa.py:27-29`). A cancelled customer registration (sold, exported, destroyed or expired) keeps its certificate date in DEREG and counts the same as a current one. A Gulfstream-held cancellation counts for E1 only when `EXP-COUNTRY` is filled. The 35 Gulfstream-held DEREG records with no country feed only E2.
- Records are lost by overwriting, not by deregistration. Between the 2026-10-26 and 2026-10-27 tables, a G280's earliest customer certificate (serial 2053) changed from 2024-12-16 to 2026-10-24, so no record with the 2024 date remains and 2024Q4 lost an event.
- Between the 2026-10-19 and 2026-11-12 daily tables, seven past quarters each show a net change of -1 (`a10_misc.py`). This is direct evidence for the Coverage limitation.

**6. Holder and scope rules.**
- Holder (`events.py:14-15`): Gulfstream Leasing gives four events (2020Q4 twice and 2025Q4 twice), which matches `README.md:159`.
- Not disclosed: 5 events come from General Dynamics group registrants (three G500s registered to GENERAL DYNAMICS CORP in 2022, and two G280s registered to GD business units). Three DEREG records spell the name `GULFSTREAM AREOSPACE CORP`; their dates fall in 2004 and 2005, and they move no E1 count from 2016Q1 on.
- Also not disclosed: 111 events from 2016Q1 to 2026Q2 rest only on a record whose `NAME` is blank, so the rule has nothing to test. One blank-name record carries status `M`, which otherwise appears only on Gulfstream-held records (REGISTRY-3).
- Scope (`faa.py:179-187`): the subsets keep only in-scope codes, so the cold tree cannot show what the engine-type rule misses. The 17 G700s under `3980222` are under "Could not check".

**7. Snapshot integrity.** `MANIFEST.json` has 8 entries, all 24 file hashes match, and there are no orphan folders.
- Every stored row is in scope. Headers are present, CRLF line endings are kept, and there are no U+FFFD characters, no field-count mismatches and no blank serials.
- Each daily table that has a stored subset equals the table rebuilt from that subset.
- The backtest subset's gzip header byte differs from the later ones (REGISTRY-5).
- Daily tables for 2026-10-20 to 10-22 and 2026-10-30 to 11-12 have no subset or hash behind them. They are the evidence for `README.md:92` ("the same in every daily snapshot since"), which I confirmed against them: 42 in every table from 10-27 to 11-12, and 41 from 10-19 to 10-26.

**8. Fiscal quarters and time zones.**
- All 42 fiscal ends from 2016Q1 to 2026Q2, plus 2015-12-31 and the 2026Q3 end of 2026-10-04, equal the report dates of GD's 10-Q and 10-K filings (SEC submissions JSON, `a12_sec.py`, `a13_sec_old.py`).
- Windows are `(start, end]` (`fiscal.py:59-61`, `events.py:86-90`); 19 events fall on a quarter end or the day after, with no off-by-one.
- Snapshots are dated by the Chicago calendar day (`faa.py:40-41`) and locks by the ET day (`live.py:45-47`, `246-262`). Comparing the two at `live.py:252`, `377` and `381` can be off by a day only for a download between 23:00 and 24:00 CT. It did not matter for the 2026Q3 lock, whose snapshot came 25 days after the quarter end.
- DST is handled through `zoneinfo` (`live.py:261`).
- `fiscal_ends` is empty, so 2027Q1 has no end until one is added by hand. `predict` then raises, and `update_latest` logs it (`live.py:126-127`, `176-178`), which is visible, not silent.

**9. Silent paths.**
- `parse_date` returns None on a bad date (`faa.py:115-123`). Only one non-blank unparsable value exists: a DEREG `YEARMFR` of `0000`, correctly ignored.
- `airframes` skips out-of-scope or blank-serial records (`events.py:30-31`). There are none in scope.
- The ratio's zero-denominator fallback never fires under E1 from 2017Q1 to 2026Q2.
- The broad `except Exception` blocks in `daily.py:173`, `185`, `191` and `204` print and set a non-zero exit code.
- The one path that can drop a record without a trace is the fixed-width fallback in `read_table` (REGISTRY-2).

## Findings

### REGISTRY-1 (S2): the neither-date branch of the bound has no test and feeds 75 counted events
- Surface: `src/gdn/events.py:47-58` (hand-written); tests `tests/test_faa.py:94-122`; fixture `tests/fixtures/faa/*.txt`.
- Evidence: every fixture airframe has a year, and five of six have an airworthiness date (`a9_fixture.py`). The year-fallback test checks only the bound's value, on an airframe with no candidate date.
  ```
  398 75004 air None yr 2026 bound 2027-12-31 cust None e1 None
  450 2050 air 2016-03-01 yr 2016 bound 2017-03-01 cust 2024-03-01 e1 None
  ```
  `a4_main.py`, section D: `airframes 4053 neither 386 neither events 75`. In the held-out quarters, 57 events have neither date.
- The code is right today: I reproduced the outputs byte for byte. But a change to `ok()` or to the bound would move up to 75 events with no test failing.
- Fix: add two fixture airframes. One has neither date and a 2024 certificate, and must count. One has only a year and a certificate after 31 December of the following year, and must be dropped.

### REGISTRY-2 (S3): the fixed-width fallback cuts real FAA rows at the wrong places, and its test uses a header the FAA does not ship
- Surface: `src/gdn/faa.py:161-170` (hand-written, preregistered at `PREREGISTRATION.md:14`); `tests/test_faa.py:39-43`; `tests/fixtures/faa/MASTER.txt:1`.
- Evidence: the real MASTER header is not padded. The data rows are fixed-width. The fixture header is padded to the field widths (`NAME                     ,`). I took a real row and replaced one character of `NAME` with a comma (`a7_keys.py`; the registrant name is redacted here):
  ```
  NNUMBER        original='100A'      with-comma='100A ,65'
  SERIALNUMBER   original='6550'      with-comma='0'
  MFRMDLCODE     original='3980050'   with-comma=''
  CERTISSUEDATE  original='20231204'  with-comma=''
  ```
  An empty `MFRMDLCODE` makes `events.airframes` skip the record with no message. No row in the 8 stored subsets triggers the fallback (0 field-count mismatches, `a16_subsets.py`), so no current count is affected.
- Why S3 and not S2: the branch is wrong on the real layout, but no stored row reaches it, so it feeds no published number today. It becomes S2 the first time a run logs a fallback row.
- Fix: the rule is preregistered, so log the number of fallback rows for each file and each snapshot. Cut at offsets measured from a data row, not the header, through a dated amendment. Give the fixture an unpadded header so the test matches the real layout.

### REGISTRY-3 (S3): the holder-rule limitation names only Gulfstream Leasing
- Surface: `README.md:159` (hand-written); the note's Limitations list (`src/gdn/note.py:669-700`).
- Evidence (`a4_main.py` section G, `a11_blank.py`, `a14_status.py`):
  - **General Dynamics registrants.** Five counted events come from registrants named GENERAL DYNAMICS: three G500s in 2022Q2 and 2022Q4 (GENERAL DYNAMICS CORP), a G280 whose `YEARMFR` reads 2010 in 2023Q3, and a G280 in 2016Q3 (registered to GD business units). Four of them fall in held-out quarters.
  - **Blank names.** 120 events (111 from 2016Q1 to 2026Q2) rest only on a record with a blank `NAME`. In the 2026-10-19 file, blank-name MASTER records set 7, 5, 8, 6 and 3 events in 2025Q3 through 2026Q3.
  - **A status-`M` record without a name.** In the 2026-10-19 MASTER subset, status `M` appears on 243 named records, all Gulfstream-held (all registrant type 3, 238 of them on GA or GD N-numbers), and on no other named registrant. One blank-name record also carries status `M` and type 3, on a GA-series N-number (G700 serial 87131). This one has no certificate date and moves no count. The 2026-11-12 daily table reads `held_by_gulfstream` 0 for it, so if it is Gulfstream's, it is missing from the dashboard's chart of jets on Gulfstream's own registration.
- I cannot show that any of these events is wrong (see Suspicions), so this is a disclosure gap.
- Fix: one sentence giving the two sizes (5 General Dynamics group events, 111 blank-name events), and say the rule cannot test a blank name.

### REGISTRY-4 (S3): the airframe key can merge two airframes, which is not disclosed
- Surface: `README.md:111` and `157` (hand-written); `src/gdn/events.py:32`.
- Evidence: answer 1. Keying by prefix, serial and model family (`a8_family.py`):
  ```
  2021Q1 (27,1)->(27,2)  2022Q3 (23,8)->(23,9)  2023Q2 (19,8)->(19,10)
  2023Q4 (34,4)->(34,6)  2024Q3 (30,6)->(30,7)
  extra events: G200 serials 207, 208, 220, 247; G150 serials 224, 234, 238
  own YEARMFR (a21_final.py): 224 2007, 208 2008, 238 2008, 220 2009, 247 2011, 207 and 234 none
  ```
  The held-out ratio MAE is 5.5234 under the project key and 5.4858 under the family key (`a20_mae.py`). Both round to the headline's 5.5.
- Fix: one clause in Used jet: the key can merge two older mid-cabin airframes that share a serial number, which removed 7 events on G150 and G200 airframes from five held-out quarters. Keep the preregistered key.

### REGISTRY-5 (S3): the stored subsets were written two ways, so their gzip hashes depend on the writer
- Surface: `data/snapshots/MANIFEST.json` (generated by `src/gdn/faa.py:232-250` through `files.py:71-93`); `PREREGISTRATION.md:21`.
- Evidence (`a2_gzhdr.py`): the 2026-10-19 files have gzip OS byte 19, and 2026-10-23 to 10-29 have 255. Apart from that byte the bytes are identical. The preregistration names `gzip.compress(data, mtime=0)`, which writes 19 on this Mac (`3.11.16 19`). The code now writes 255, so the lock's subset (2026-10-29) was not written by the preregistered call. The content is the same.
- Fix: record the deviation as an erratum if it is not already there. Also add the sha256 of the decompressed text to each manifest entry, so a reader can check a subset whatever gzip wrote it.

### REGISTRY-6 (S3): the used-jet size is not next to the raw count on the README Results table or the dashboard
- Surface: `README.md:30` and `76` (generated by `src/gdn/report.py`); dashboard `site/index.html` and `site/app.js`.
- Evidence: `grep -c 'three years old'` gives 0 for `site/index.html`, `site/app.js` and `site/data.json`, and 2 for `README.md`, at `106` and `157`. The dashboard links to the README's Limitations ("What this method cannot see", `site/index.html:106`).
- Fix: one clause under the README table and in the dashboard's backtest caption: "By the registry's year of manufacture, 246 of the 1,251 counted events (19.7%) are on airframes at least three years old, and 76 have no year."

## Improvements that would raise the project's standing

1. Add two counts to the five-quarter error table and to the drift paragraph: events on airframes at least three years old, and events with no year. Examples: 2025Q4 has 16 and 5 of 65; 2022Q1 has 12 and 3 of 38; 2025Q4 to 2026Q2 have 40 and 19 of 177. Show the counts only, with no cause attached.
2. Publish the past-quarter loss rate from the daily tables. Seven past quarters each show a net change of -1 between 2026-10-19 and 2026-11-12. That measures, from the project's own files, what the as-of study infers.
3. Have each daily run print three counts: fallback rows, blank-name records, and status-`M` records that fail the holder rule. A silent shift then shows up in the log.
4. Decide the cabin rule for the G300 before it first appears in the registry. The `MID` pattern (`faa.py:32`) lacks `G300`, and ACFTREF already holds an old large-cabin `G-IV (G300)` code, so a bare `G300` pattern would mis-file that code.
5. Put a content hash next to each gzip hash in `MANIFEST.json` (see REGISTRY-5).

## Checked and clean

- Manifest: 8 entries, 24 hashes match, no orphan folders. `serials.csv` and `registry_quarterly.csv` rebuild byte for byte from the 2026-10-19 subset.
- The 2026Q3 lock: the window `(2026-07-05, 2026-10-04]`, 35 large and 7 mid events, trailing registry counts of 187 and 28, and trailing reported counts of 140 and 23 all recompute from the 2026-10-29 subset. 35 × 140 / 187 and 7 × 23 / 28 give the locked 26.20 and 5.75.
- README registry figures I recomputed:
  - 1,251 events; 246 (19.7%) on old airframes; 76 with no year; 386 of 4,053 airframes with neither date, supplying 75 events.
  - 11 mid-cabin airframes filed as large; 2 double counts; 4 Gulfstream Leasing events.
  - 42 events in every daily table from 2026-10-27 to 11-12; 5 of 42 old.
  - 0.76 and 0.95 deliveries per event; 25 days from the quarter end to the lock snapshot.
  - GD deliveries per event of 1.92 in 2016 and 1.26 in 2019, and above 2 for mid cabin in 2016 and 2017. Since 2022, yearly mid-cabin gaps of -1, 2, -4 and -3.
  - E1 and E2 differ only in 2019Q4, by one airframe. The third G280 code dates from 2026-10-27.
- All fiscal ends match GD's SEC report dates.
- The subset rows are clean (answer 7). The ratio's zero-denominator fallback never fires. The excepts in `daily.py` are logged.
- The dashboard's chart of jets on Gulfstream's own registration says it includes jets taken back for resale and leaves out the G700s under the excluded type code (`site/app.js:340-343`).

## Suspicions, not proven

- **Four blank-name events may be Gulfstream's own registrations.** Each comes from a status-`V` record of registrant type 3 or 7 on a Gulfstream GA-series N-number, the same pattern as Gulfstream's named status-`V` records:
  - G800 serial 88026, 2026Q1;
  - G280 serial 2323, 2026Q2;
  - G700 serial 87092, 2026Q3 (one of the lock's 42);
  - G500 serial 72199, 2026-10-19 (the open quarter).
  
  If any of them is Gulfstream's own registration with the name withheld, it is a test registration read as a delivery. To settle it: the registrant in the FAA inquiry for each, or a later record once a name appears.
- **Two G280 exports to Israel.** Two of the lock's 7 mid-cabin events (G280 serials 2325 and 2326) are cancellations of Gulfstream's registration for export to Israel. The registry files the G280 under the maker `IAI LTD`. No E1 export to Israel appears in 2016Q1 to 2026Q2 in the backtest file. They may be Israeli customers. To settle it: an outside source for the two serials.
- **GD's own jets.** The three G500s registered to GENERAL DYNAMICS CORP in 2022 count as deliveries. Whether GD counted them in its reported deliveries would be settled by a GD filing or call that says so.

## Could not check, and refused commands

- The raw zips are not in the tree and were never downloaded. So I could not check that the subsets are the zips' in-scope rows byte for byte, or the `zip_sha256` values.
- Out-of-scope ACFTREF codes, including `3980222` (the 17 G700s in `README.md:159`) and any other Gulfstream code with an engine type other than 4 or 5: the subsets keep only in-scope codes.
- `docs/prepub/ERRATA.md`: not read, because the launch message limited my reads under `docs/prepub/` to the two round 4 briefs, even though cold auditors normally hold that file. So I did not check whether REGISTRY-5's deviation is already recorded.
- No tests, `make` targets or gate runs, as the brief requires. No command was refused.
