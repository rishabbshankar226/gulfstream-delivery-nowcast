# Registry and data engineer review (P4.4)

Reviewer: `registry`. Date: 2026-11-11. Branch `prepub-audit`.

**Verdict: NO-GO for the post as worded, GO once REGISTRY-1 and REGISTRY-2 are reworded.** Both are wording fixes. The engineering record (hashes, lock chain, fiscal calendar, live path arithmetic) verifies end to end. What the count is said to count does not.

Findings: 2 S1, 6 S2, 10 S3.

## How I worked

Every figure below was printed by a script in `~/gdn-prepub/agents/registry/`. The scripts import the project's own read-only functions (`faa.read_subset`, `events.airframes`, `fiscal.Calendar`, `live.lock_due`) and add independent readers. `rekey.py` holds a replica of `events.airframes` that takes a different key, holder rule or cabin rule; on the 2026-10-19 subset the replica equals the project's function on all 4,053 rows, and `a_overview.py` rebuilds `serials.csv` and `registry_quarterly.csv` byte for byte and row for row. I ran no `make`, no `pytest`, no `python -m gdn`. SEC was read with `urllib` and the agent string from `~/.sec_ua`, never printed.

**The used-jet flag.** Two rules, reported separately.
- *Data rule*: the airframe's `YEARMFR` is 3 or more years before the event year. Registry fields only.
- *Type rule*: the event comes well after the newest `YEARMFR` the registry itself holds for that family. Those newest values, over every stored row (`gap3_final.py`): G-II 1989, G-III 2000, G-IV 2006, G-V 2005, G450 2017, G550 2021, G150 2017, G200 2011, G100 2006. The window starts in 2016, ten or more years after the newest G-II to G-V value, so every event on those four families is flagged. For G450, G550, G150, G200 and G100 the rule fires only when the event year is at least two years after the family's newest value (G450 from 2020, G550 from 2023, G150 from 2019).
- Validation on the project's own audit: of the 20 audited E1 events, the combined flag fires on 5 of the 5 the audit calls used and on 0 of the other 15. The data rule alone fires on 4 of the 5 (the fifth, serial 466, has no `YEARMFR`) and on 0 of 15.

## Answers to the brief's questions

### 1. The airframe key

Yes to both. `q1_key.py` and `rekey.py` on `data/snapshots/2026-10-19/`:

- **Collisions (two airframes, one key): 61 keys.** 60 sit under prefix `450`, where G150, G200 and G100 serial ranges overlap (for example key `450/212` holds N104SG, a `GULFSTREAM 200`, and N150JN, a `GULFSTREAM G150`). One sits under `398`: key `398/245` holds N222NP (`G1159B`) and a `G150` DEREG row. 16 of the 61 keys hold two current MASTER rows.
- **Splits (one airframe, two keys): 7 airframes** (G150 2, G-III family 2, G280 1, G100 1, G200 1). 3 have an E1 on both keys.
- **Events in 2016Q1 to 2026Q2.** Splits add 2 E1 events, both mid cabin and the same under E2:
  - G150 serial 322: `450/322` gives 2016-06-28 (2016Q2), `398/322` gives 2018-05-22 (2018Q2). One airframe, two events, the second inside the design window.
  - G280 serial 2009: `398/2009` gives 2012-08-01, `450/2009` gives 2026-05-26 (2026Q2, N280LP). A jet first certificated in 2012 is one of the 6 mid-cabin events of 2026Q2, a held-out quarter and a lag of the 2026Q3 lock.
- Collisions remove 7 events (2021Q1 1, 2022Q3 1, 2023Q2 2, 2023Q4 2, 2024Q3 1). All 7 carry the used-jet flag (5 by the data rule, 2 by the type rule with no `YEARMFR`), so the collision suppresses them by accident.
- Net: 1,251 E1 events under the project's key, 1,256 under a (family, serial) key. All nine affected events are on G150, G200 or G280 airframes.
- G650 and G650ER share prefix `398` (codes 3980121, 3980212, 3980214, 3980050) and do not split. G-IV and G450 share `398` and their serial ranges do not overlap. The G600 has two prefixes (`056` 23 airframes, `398` 244); no serial appears under both.
- **Ahead:** on 2026-10-27 the FAA added ACFTREF code `398012B` (`GULFSTREAM`, `G280`). One MASTER row uses it on the lock snapshot: N991AG, serial 2024, no certificate yet. The same serial sits under `450/2024` with an E1 of 2013-10-28. When a G280 is re-registered under the new code with no airworthiness date and no year, it will count again, as serial 2009 did.

### 2. E1 and E2 dates

**The code does what the preregistration says, clause for clause.** I checked `events.airframes` (events.py:23 to 64) against `docs/PREREGISTRATION.md` §3.3: key, `customer_cert`, `gulfstream_cancel`, `export_cancel` with the alphabetical tie rule, `held_by_gulfstream`, model from the alphabetically first code, earliest airworthiness, earliest four-digit year, the bound, and "drop any input dated after `bound`". All match.

**The README paraphrase differs in two places** (REGISTRY-3): "within a year of" reads two-sided where the rule is one-sided, and "first customer's" and "first airworthiness" describe records the file often no longer holds.

**`gulfstream_held`** (events.py:14) matches `GULFSTREAM AEROSPACE CORP` (479 DEREG and 260 MASTER rows), `... CORPORATION` (32 and 3), `... LLC` (16 and 7), `... LP` (1 DEREG) and `... COCRP` (1 DEREG). It would match "Gulfstream Aerospace Corp of Georgia"; no such name is in the file. No registrant name contains `IAI` or `ISRAEL A`. It misses (`q2_held.py`):

| Name | Rows | Effect in 2016Q1 to 2026Q2 |
|---|---|---|
| `GULFSTREAM LEASING LLC` (Savannah GA) | 10 MASTER, 1 DEREG | 4 E1 events: serials 72001 and 73002 on 2020-11-13 (2020Q4), 87001 and 88001 on 2025-10-07 (2025Q4) |
| `GENERAL DYNAMICS CORP` and two GD subsidiaries | 5 MASTER | 5 E1 events: G280 2097 (2016Q3), G500 72095 (2022Q2), 72106 and 72107 (2022Q4), G280 2003 (2023Q3) |
| `GULFSTREAM AREOSPACE CORP` (misspelt) | 3 DEREG | none: cancels dated 2004 and 2005; all three exports are lost outside the window |
| blank `NAME` | 199 MASTER, 44 DEREG | see below |

A miss turns an intra-group registration into a customer certificate, and turns that entity's export cancel into nothing. The four `GULFSTREAM LEASING LLC` airframes carry `YEARMFR` 2015, 2017, 2020 and 2022 and marks N500GA, N720GD, N700GA and N800G; their `CERTIFICATION` field reads 41756, 41567, 41056 and 41567, where the General Dynamics rows printed beside them read `1T`. I cannot say whether GD counts the five jets registered to General Dynamics entities as deliveries.

Blank names read as "not Gulfstream". 112 E1 customer-certificate events in the window sit on airframes with a blank-name record. One blank-name row is a miss in the other direction: DEREG N750GA, serial 87050 (`GVIII-G700`), cancelled 2025-04-16 with export country GREECE and no name, so the airframe has no E1 and no E2. Trustee registrations cannot be told from the name; 25 MASTER-only airframes with an E1 in the window still wear a mark ending GA or GD.

### 3. The one-year airworthiness window

- **Events the bound drops, by fiscal year of the dropped date (E1):** 2016 48, 2017 80, 2018 93, 2019 84, 2020 90, 2021 156, 2022 160, 2023 172, 2024 197, 2025 292, 2026 first half 155. Total 1,527 (E2: 1,530). Without the bound the window holds 2,778 E1 events; with it 1,251.
- **No bound applies to 386 of 4,053 airframes** (no airworthiness date and no year). Another 4 have a year only; none of those has an event in the window.
- **75 of the 386 produce an E1 event in 2016Q1 to 2026Q2** (E2: 75). By year: 2016 2, 2017 4, 2018 3, 2019 9, 2020 7, 2021 6, 2022 6, 2023 5, 2024 8, 2025 11, 2026 14. 57 fall in the holdout and 19 in the last four held-out quarters (2025Q4 5, 2026Q1 5, 2026Q2 9).
- 29 of the 75 are G-II, G-III, G-IV or G-V family airframes (for example `C-20A` serial 83-0502 registered to a NASA centre, 2018Q4; `G1159B` serial 245, 2025Q4). The other 46 are current types with blank fields (G280 27, G700 7, G600 5, G650 4, G500 2, G800 1).
- **The bound is one-sided.** It tests `date <= airworthiness + 365 days` and nothing else. 189 of the 1,251 E1 events have an airworthiness date later than the event, 31 of them more than 365 days later (for example `G-IV` serial 1256, `YEARMFR` 1994, event 2017-10-17, airworthiness 2025-12-09). 1,250 of the 1,251 events sit on airframes with exactly one stored record, so "first" airworthiness is that record's current date.

### 4. Used-jet leakage

**Estimate** (`gap1_flag.py`, `final_numbers.py`):

| Period | E1 | GD | E1 per delivery | Data rule | Type rule adds | Combined | Combined share | Unflagged per delivery |
|---|---|---|---|---|---|---|---|---|
| 2016Q1 to 2026Q2 | 1,251 | 1,359 | 0.92 | 246 | 30 | 275 | 22.0% | 0.72 |
| Design, 2017Q1 to 2019Q4 | 275 | 388 | 0.71 | 52 | 12 | 64 | 23.3% | 0.54 |
| Holdout, 2020Q1 to 2026Q2 | 913 | 850 | 1.07 | 186 | 16 | 201 | 22.0% | 0.84 |
| 2025Q3 | 38 | 39 | 0.97 | 4 | 0 | 4 | 10.5% | 0.87 |
| 2025Q4 | 65 | 45 | 1.44 | 16 | 2 | 18 | 27.7% | 1.04 |
| 2026Q1 | 55 | 38 | 1.45 | 11 | 1 | 12 | 21.8% | 1.13 |
| 2026Q2 | 57 | 41 | 1.39 | 13 | 1 | 14 | 24.6% | 1.05 |
| 2025Q4 to 2026Q2 | 177 | 124 | 1.43 | 40 | 4 | 44 | 24.9% | 1.07 |

The combined count leaves out one data-rule hit where I judged the year a registry error: G280 serial 2214, `YEARMFR` 2000, certificated 2025-01-07 (2025Q1). Counting it gives 276. 19 of the 275 are current types built 3 or more years earlier (for example G700 serial 87005, `YEARMFR` 2020, certificated 2026-01-26); GD may count some of those. 66 of the 1,251 events are G-II to G-V family airframes.

"Flagged" is a registry measure: an airframe built three or more years before the event, or of a type the registry last shows built years earlier. I did not check any single airframe's delivery against an outside source.

**Does it explain about 1.4 events per delivery? Yes, for the level; no, for the trend.**
- In the last three held-out quarters the registry shows 177 events against 124 deliveries. 44 events are flagged. Without them the figure is 1.07.
- The share is steady, between 15.9% and 26.6% in every year from 2016 to 2026. What rose is the unflagged count per delivery, from 0.44 in 2016 to 1.09 in 2026, which is the README's own Coverage story (old certificates lost).
- The archived captures settle it (`q_asof_used.py`). Read as each capture stood, for the four lag quarters it scored:

| Capture | E1 | GD | E1 per delivery | Flagged | Unflagged per delivery |
|---|---|---|---|---|---|
| 2017-04-27 | 146 | 121 | 1.21 | 29 (19.9%) | 0.97 |
| 2025-10-21 | 184 | 149 | 1.23 | 40 (21.7%) | 0.97 |
| 2026-05-01 | 197 | 158 | 1.25 | 43 (21.8%) | 0.97 |
| 2026-08-03 | 206 | 160 | 1.29 | 42 (20.4%) | 1.02 |

A fresh file has shown 1.21 to 1.29 events per delivery since 2017, and without the flagged events it matches GD's count almost one for one. About one counted event in five is flagged, in every period I can read.

**Is the README's account of the audit accurate against the CSV? Yes, number for number** (`q4b_used.py`): 30 rows; 10 `no`, 20 `yes` (33.3%); five used (4122, 5340, 5269 and 4076 with an airworthiness date in the event year, 466 with none); two earlier stated deliveries (571, a G-V, 2000Q1 against 2000Q2, E2 only; 6270, a G650ER, 2017Q3 against 2018Q1); three unconfirmed (72023, 5467, 2177); 29 `mirror` sources and 1 `release`; counted-event dates from 2000-06-02 to 2019-09-06. One thing the paragraph does not say: the five used jets are 5 of the 20 E1 events sampled, 25%, which agrees with the 22.0% above.

*One labelled line, reviewer's own, after the fact, not for any public surface:* with flagged events removed from every quarter the ratio model's holdout average miss is 4.35 against the published 5.52, and its design-window miss is 6.24 against 5.47. It cuts both ways and is not a fix.

### 5. The mid-size airframes filed as large

- **Confirmed and one more: 11 airframes.** `serials.csv` has 8 `GULFSTREAM 200` and 2 `GULFSTREAM 100` rows with cabin `large`, plus 1 `GALAXY` row (`398/051`). All 11 sit under prefix `398`.
- **None has an E1 or E2 event in 2016Q1 to 2026Q2.** Reclassing them moves no published figure. On the lock snapshot the 2026Q3 counts stay 35 large and 7 mid.
- **Every model name in scope (54 codes on 2026-10-19):**
  - Large, correct: `G-1159`, `G-1159A`, `G1159B`, `G-IIB`, `GII`, `G-III`, `C-20A`, `G-IV`, `G-IV SP`, `IV SP`, `G-IV (G300)`, `G-IV (G350)`, `G-IV (G400)`, `GIV-X`, `GIV-X (G350)`, `GIV-X (G450)`, `G-V`, `GV-SP`, `GV-SP (G500)`, `GV-SP (G550)`, `GVI`, `G650`, `GVI (G650)`, `GVI (G650ER)`, `GVII-G400`, `GVII-G500`, `GVII-G600`, `GVIII-G700`, `GVIII-G800`.
  - Mid, correct: `G150`, `G100` (code 3980402), `GULFSTREAM G150`, `GULFSTREAM G280`, and under prefix `450` `GULFSTREAM 200` and `GULFSTREAM 100` (mid through the maker rule).
  - **Classed large, mid-size by name:** `GULFSTREAM 200` (3980202, 3980211), `200` (3980213), `GALAXY GSTREAM 200` (3980304), `GALAXY` (3980401), `ASTRA SPX` (3980403), `GULFSTREAM 100` (3980404). Only `GULFSTREAM 200`, `GULFSTREAM 100` and `GALAXY` appear as an airframe's table model.
  - Unclear: code 3970250, maker `GULFSTREAM AEROSPACE`, model `550`, TYPE-ACFT 4, 6 seats, one airframe, no event.
- No Westwind code and no C-37 code is in scope. `C-20A` has one airframe and one event (2018Q4). Out of scope by the name rule, with registry rows: `1124` (174 rows), `1125 WESTWIND ASTRA` (68), `ASTRA SPX` under `ISRAEL AIRCRAFT INDUSTRIES` (63), `GALAXY` (29), `G200` under two IAI maker names (22 and 4).
- **A current type is out of scope** (REGISTRY-6): code 3980222, `GVIII-G700`, carries TYPE-ENG 2.

### 6. Deregistration reasons

No. The code reads two DEREG fields, `CANCEL-DATE` and `EXP-COUNTRY`. It never reads `STATUS-CODE` (23 distinct values in scope) or `INDICATOR-GROUP`, so it cannot tell a destroyed or scrapped airframe from any other cancel. An "export" is any Gulfstream-held DEREG row with a non-blank country.

- 279 of the 1,251 E1 events are such export cancels.
- **Yes, some are used aircraft.** 5 of the 279 have a `YEARMFR` 3 or more years before the export: G450 4076 (2007, to Mexico 2016; the project's own audit calls it a resale), G650ER 6134 (2015, 2019), G600 73010 (2019, 2024), G550 5394 (2012, 2025), G700 87004 (2020, 2026). 26 export events have no `YEARMFR` and cannot be checked this way.
- 35 Gulfstream-held cancels carry no country (by year since 2016: 2018 1, 2019 1, 2020 1, 2021 2, 2023 1, 2025 5, 2026 1). E1 ignores them; E2 counts them. 9 airframes have an E2 in the window with no E1.
- 88 E1 customer-certificate events sit on airframes with DEREG rows only: a later owner's certificate on a jet since cancelled.

### 7. Snapshot hashing

- **Hashes match.** All 24 file hashes in `MANIFEST.json` equal the recomputed sha256 (`q7_hash.py`). The 7 raw zips still on this Mac (10-19, 10-23, 10-25 to 10-29) match their `zip_sha256` and `zip_bytes`. 10-24 has no local zip; its manifest zip hash equals 10-25's and 10-26's.
- **Deterministic, with one exception.** 21 of the 24 files rebuild to identical bytes through `files.gz_bytes`. The three 2026-10-19 files differ at byte 9 only: they hold OS byte 19, the others 255 (REGISTRY-10).
- **Byte for byte: yes.** An independent filter on raw bytes (`q7b_bytes.py`) reproduces all three stored files for each of the 7 dates with a local zip. I could not test 10-24.
- **`errors="replace"`** changes nothing in these files: every ACFTREF, MASTER and DEREG member in all 7 zips decodes as strict UTF-8, with no lone CR and none of the separators `str.splitlines` also splits on (printed for each of the 7 dates). If a future zip holds an invalid byte the stored subset will carry U+FFFD and the claim fails for that date; `ingest` logs a warning and stores it anyway.
- The DEREG hash changes on days when no row changes: the FAA writes the same rows in a different order (10-23 to 10-29: 0 rows added or removed on all six steps, order differs on four).

### 8. Fiscal quarter mapping

- **All 42 `fiscal_end` values match a 10-Q or 10-K period end on SEC** (`q8_sec.py`, submissions index read 2026-11-11). Every Q1 to Q3 end is a Sunday; every Q4 end is December 31.
- **2026-10-04 is right for 2026Q3.** 10-Q `0000040533-26-000038`, filed 2026-10-30, reports period 2026-10-04. The rule gives the same: 2026-07-05 plus 91 days.
- **The 91-day rule holds** for every Q2 and Q3 from 2016Q2 to 2026Q2: no violation.
- **Q1 is not a nearest-Sunday rule.** GD's first quarters ended on day 94, 92, 91, 90, 89, 94, 93, 92, 91, 89 and 95 of the year (2016 to 2026). 2026Q1 ended 2026-04-05.
- **2027Q1 needs a `fiscal_ends` entry** in `config/calendar.json` (now `{}`). Without it `Calendar.end` returns `None`, `predict` raises, and `update_latest` logs "no estimate" and carries on. My inference, not a source: 2026-04-05 plus 364 days is Sunday 2027-04-04. SEC cannot confirm it before the 2027Q1 10-Q, which comes after that quarter's lock.
- **The window rule is applied the same way everywhere:** `events.count` (events.py:90) tests `lo < date <= top`, and the truncation test, the coverage diagnostics and `tools/asof.py` all go through it or repeat it.
- **Two surfaces print the start as if inclusive** (REGISTRY-11): the dashboard's "Quarter window" (site/app.js:129) and the note (note.py:397).

### 9. Timezones and the lock window

I called the project's own `faa.snapshot_date`, `live.lock_due` and `live.before_release` over a grid of start times (`gap2_q9.py`). Observed landings of the workflow from `git log` (committer time): the 00:17 UTC cron landed between 04:44 and 07:21 UTC; the 12:17 UTC cron between 15:58 and 18:42 UTC.

**October (EDT), the real case, release 2026-10-30:**

| Start UTC | ET | Chicago | Snapshot name | Outcome |
|---|---|---|---|---|
| 10-29 04:44 | 00:44 eve | 23:44 day before | 2026-10-28 | no lock, not due |
| 10-29 05:01 | 01:01 eve | 00:01 eve | 2026-10-29 | locks if the download works |
| 10-29 05:51 (what happened) | 01:51 eve | 00:51 eve | 2026-10-29 | locks |
| 10-29 15:58 to 18:42 | 11:58 to 14:42 eve | same day | 2026-10-29 | locks if an eve-dated table exists |
| 10-29 23:07 | 19:07 eve | 18:07 eve | 2026-10-29 | locks from the newest stored subset, any date |
| 10-30 03:51 | 23:51 eve | 22:51 eve | 2026-10-29 | refused, inside the 10-minute margin |
| 10-30 04:44 to 07:21 | 00:44 to 03:21 release date | | | no lock |

**January (EST), illustrative release date 2027-01-27** (GD filed its 2025Q4 release on Wednesday 2026-01-28; no 2027 date is announced):

| Start UTC | ET | Chicago | Snapshot name | Outcome |
|---|---|---|---|---|
| 01-26 04:44 | 23:44 day before | 22:44 | 2027-01-25 | no lock, not the eve yet |
| 01-26 05:01 to 05:59 | 00:01 to 00:59 eve | 23:01 to 23:59 day before | 2027-01-25 | no lock: eve in ET, snapshot named for the day before |
| 01-26 06:01 to 07:21 | 01:01 to 02:21 eve | 00:01 to 01:21 eve | 2027-01-26 | locks if the download works |
| 01-26 15:58 to 18:42 | 10:58 to 13:42 eve | same day | 2027-01-26 | locks if an eve-dated table exists |
| 01-27 00:17 (cron on time) | 19:17 eve | 18:17 eve | 2027-01-26 | locks from the newest stored subset |
| 01-27 04:51 | 23:51 eve | | | refused, margin |
| 01-27 05:01 to 07:21 | 00:01 to 02:21 release date | | | no lock |

- **Can a lock be made after 00:00 ET on the release date? Not by this code path.** `lock_due` needs the ET date to be the eve, `before_release` repeats it, and `wall_clock_ok` re-reads the real clock twice, the second time just before `gh release create` (live.py:383). The residue: `Ops.run` has no timeout, and if a release were stamped on or after the release date the run only logs a warning and still writes `_lock.json`; `score_quarter` then counts it as locked (REGISTRY-17).
- **Can a lock be missed? Yes.**
  - With no release date in the config there is no lock at all. `config/calendar.json` holds only 2026Q3 today.
  - Before 19:00 ET a lock needs an eve-dated airframe table, so one FAA download must succeed on the eve.
  - GitHub's 00:17 UTC run is the only workflow run that could use the 19:00 ET rule. On time it starts at 20:17 EDT or 19:17 EST on the eve. At the observed landings (04:44 to 07:21 UTC) it starts at 23:44 EST at the earliest, and after midnight in EDT; from 23:50 it is refused. After 19:00 ET the lock rests on the Mac.
  - In EST a run landing between 05:00 and 06:00 UTC is on the eve in ET with a snapshot named for the day before. Four of the workflow's late-October runs landed at 05:45 to 05:52 UTC. Harmless: the next run locks.
- DST is handled: `ZoneInfo` on both sides, and the margin test builds midnight ET for the release date itself.

### 10. Double counting, and the two snapshots

- **MASTER and DEREG:** no double count inside a key. All of an airframe's rows share one key and yield one E1 and one E2.
- **Two events or two quarters for one airframe:** only through a split key. 3 airframes; 2 in the window (answer 1).
- **A different date in two snapshots: yes.** `q10_snapdiff.py`, 2026-10-19 against 2026-10-29: 4,053 against 4,056 airframes; **3 lost their E1 and E2, 0 changed date, 8 gained one.** The three losses move the backtest's own counts: 2019Q3 large 20 to 19, 2019Q4 large 29 to 28 (E2 30 to 29), 2024Q4 mid 8 to 7. Across all 24 daily tables (10-19 to 11-11): 10 lost, 1 changed, 16 gained.
- **The one change** is G550 serial 5291 (`YEARMFR` 2011): E1 2026-05-26 in the backtest file (2026Q2), 2026-11-01 from the 2026-11-03 table on (2026Q4). It was in 2026Q2's published count and is now in the live 2026Q4 count.
- **On "the later file has lost first-owner records":** the mechanism is confirmed. All three losses are re-registrations in October 2026.
  - G650ER 6379: a Gulfstream-held export cancel of 2019-12-23 on the 10-19 file. On 10-29 the DEREG row is gone and a MASTER row for a new registrant, certificated 2026-10-20, stands in its place with the 2019 airworthiness date. A real first delivery vanished.
  - G450 4166 (`YEARMFR` 2009, counted 2019Q3) and G280 2053 (`YEARMFR` 2014, counted 2024Q4): both were already flagged events. What vanished was a later owner's certificate.
  - So 1 of the 3 records lost in ten days was a first-owner record. The sentence is right about the mechanism and too narrow about what is lost (REGISTRY-13).

### 11. The live path

- **Arithmetic: right in every row** (`q11_live.py`). All 12 rows of `2026Q3_path.csv` and all 13 of `2026Q4_path.csv` recompute from their daily airframe tables: events, trailing registry sums, and the three estimates. Trailing reported sums are 140 and 23 for 2026Q3, 142 and 22 for 2026Q4.
- **`site/data.json`:** the `path` block has 0 mismatching cells against both CSV files; the `live` block's `locked`, `lock` and `score` objects equal `predictions/2026Q3.json`, `_lock.json` and `_score.json`.
- **The lock read the 2026-10-29 snapshot.** From the stored subset I recompute 35 and 7 events, 187 and 28 trailing registry, 31.953208556149733, and the band 21.233380969942836 to 37.24108734402852: all equal to the prediction file.
- **Stored with its hash before the lock: yes.**
  - `878d040`, 2026-10-29T05:51:16Z, adds the three subset files and the manifest entry.
  - `a44e5ac`, 05:51:22Z, adds `predictions/2026Q3.json` and nothing else. Its tree holds the subset files, and their sha256 equal the manifest entry in that same commit.
  - Release `lock-2026Q3`: target `a44e5ac`, published 2026-10-29T05:51:24Z, body `sha256 3c4cdbd0...06f23`, equal to the file's sha256 at that commit and today.
  - GD's 8-K `0000040533-26-000036` was accepted by SEC at 2026-10-30T12:09:27Z: 1 day, 6:18:03 after the lock.
- The release author is `github-actions[bot]` (REGISTRY-2).
- **Inside the locked count:** 5 of the 42 events are flagged: G-1159A serial 445 (`YEARMFR` 1984), G-IV 1335 (no year), G550 5260 (2009), G650ER 6206 (2016), G150 311 (2014). A sixth data-rule hit is left out as a likely year error: G700 serial 87118 reads `YEARMFR` 2006 where serials 87117 and 87119 read 2026. The G150 is the seventh mid-cabin event that moved the path from 31.1 to 32.0 on 2026-10-27.

## Also report: silent failures

No bare `except:` exists in the modules I read. These places can lose or change a count without an error:

1. **`faa.read_table` fallback (faa.py:161 to 170).** When a line's field count differs from the header's, it cuts the line at the header's comma positions. The real header is not padded: header commas sit at 8, 22, 35 and the first MASTER row's at 5, 36, 44. I put one comma inside a real Gulfstream-held name: the row came back with serial `00`, no code and no parseable date, so it would be dropped unseen. 0 in-scope rows trigger it today; 1 DEREG row in the full file has an extra comma. The test (tests/test_faa.py:39) passes on a fixture whose header is padded (REGISTRY-12).
2. **`faa.parse_date` (faa.py:115).** Any other format returns `None` and the event disappears. If the FAA changed its date format every count would fall to zero with no error. Today 0 non-blank date cells are rejected.
3. **`YEARMFR` is optional (faa.py:31).** If the column goes, nothing raises.
4. **`faa.scope` hard-codes TYPE-ENG `4` and `5`.** A wrong code drops a type unseen; it already has (REGISTRY-6). Nothing checks that a subset holds a plausible number of rows before a lock reads it.
5. **Blank `NAME`** is "not Gulfstream" (answer 2).
6. **`daily._run`** catches `Exception` around the snapshot, lock and score steps (daily.py:127, 139, 145) and around the rebuild (:158). Each prints and sets a non-zero exit code, so they are not silent, but a failed snapshot step lets the lock go ahead on the newest stored subset, whatever its date (REGISTRY-7). A failed `git pull` (:116) is printed and the run goes on unpulled.
7. **`live.update_latest`** catches `ValueError` (live.py:174): a quarter with no fiscal end logs "no estimate" and the daily job reports nothing else.
8. **`files.write_gz`** keeps an old file whose content matches, so the 10-19 files keep their odd header byte for good.
9. **`live.ingest`** writes the daily table before it checks whether the date backs a lock (REGISTRY-16).

## Findings

### REGISTRY-1 (S1). The post says it counted first customer registrations; about one counted event in five sits on an airframe built years earlier

- **Surface:** `docs/LINKEDIN_POST.md:3`: "I counted each Gulfstream jet's first customer registration or export in a registry copy".
- **Evidence:** `gap1_flag.py` and `final_numbers.py`. 246 of 1,251 E1 events (19.7%) sit on airframes whose `YEARMFR` is 3 or more years before the event; 275 (22.0%) with the type rule. 66 are G-II to G-V family airframes. The flag matches the project's audit 5 of 5 with 0 of 15 false hits, and the audit itself found 5 used jets among 20 sampled E1 events. The locked 2026Q3 count holds 5, a `G-1159A` with `YEARMFR` 1984 among them. The post carries no caveat.
- **Defensible version:** "I counted, for each Gulfstream jet, the earliest customer registration the registry still shows, or an export. About one counted event in five is on an airframe built three or more years earlier, which the date rule lets through." If the post has no room for the second sentence, drop "first": "a customer registration or an export".

### REGISTRY-2 (S1). The README says the Mac downloads and locks and that the FAA has refused GitHub's runners; the record shows the workflow did both

- **Surface:** `README.md:107`: "Each day my Mac downloads the registry ... locks the estimate as a GitHub release". `README.md:156`: "bot blocking that has refused GitHub's runners" and "runs the same job twice a day as a fallback".
- **Evidence:**
  - `gh release view lock-2026Q3 --json author`: `github-actions[bot]`. Commits `878d040` (the snapshot), `a44e5ac` (the lock) and `0c7e8ab` (the lock record) are all by `github-actions[bot]`. The manifest's `downloaded_utc` for 2026-10-29 is 05:51:09Z, seven seconds before the bot's snapshot commit.
  - `git log --since=2026-10-18 | grep "Daily snapshot"`: 19 by `github-actions[bot]`, 6 by the owner. The owner's six are dated 10-20 to 10-26. Every snapshot commit dated 2026-10-27 to 2026-11-11 is the bot's.
  - The owner's last daily commits are dated 2026-10-30 (the score). `data/raw/faa/` on this Mac ends at `ReleasableAircraft-2026-10-30.zip`.
- **Rubric:** "A stale sentence about the live record."
- **Could not check:** whether the Mac's task has run since 2026-10-30 without leaving a commit or a zip.
- **Defensible version:** "A GitHub workflow runs the job twice a day. It downloaded the registry and made the 2026Q3 lock, and it committed a snapshot on 2026-10-19, 10-20, 10-24 and every day from 10-27 to 11-11. My Mac runs the same job as a second path." If the bot-blocking history stays, cite the preregistration's own figure for it and date it.

### REGISTRY-3 (S2). The method text describes the date rule more strongly than the rule is, and gives the leak no size

- **Surface:** `README.md:98` and `:99` ("the first customer's registration certificate"); `README.md:101` ("within a year of the airframe's first airworthiness date ... keeps out renewed certificates and most used jets"); `README.md:143`; `site/index.html:94` ("gets a delivery date"); `report/note.html:64`; `docs/INTERVIEW_NOTES.md:13`.
- **Evidence:** answers 3 and 4. The rule is one-sided (189 events have a later airworthiness date, 31 by more than a year). 1,250 of 1,251 events rest on a single surviving record. The leak is 22.0% of counted events and has been 19.9% to 21.8% on four archived captures. "Most used jets" is true as arithmetic: the bound drops 1,527 dates and lets 275 flagged events through.
- **Defensible version:** "E1: the earlier of the earliest customer certificate the registry still shows and an export off Gulfstream's own registration. Either date must fall no later than a year after the airworthiness date on the airframe's record. That drops renewed certificates and most used jets. It does not drop a used jet that arrives with a new airworthiness date or with none: about one counted event in five (275 of 1,251) is on an airframe built three or more years earlier or of a type long out of production."

### REGISTRY-4 (S2). `gulfstream_held` misses `GULFSTREAM LEASING LLC`; four of its registrations are counted as deliveries

- **Surface:** `src/gdn/events.py:14`; `README.md:86` (the 2025Q4 row, registry large 57); every count that includes 2020Q4 or 2025Q4.
- **Evidence:** `q2_held.py` and `show.py 2026-10-19 --name "GULFSTREAM LEASING"`. Serials 72001 and 73002 certificated 2020-11-13; 87001 (N700GA, `YEARMFR` 2020) and 88001 (N800G, `YEARMFR` 2022) certificated 2025-10-07. Registrant city and state SAVANNAH GA, as on Gulfstream Aerospace Corp's own rows. A wider holder rule removes 9 events in the window (7 large, 2 mid), the other 5 being General Dynamics entities.
- **Also:** 2025Q4 is one of the README's five driver quarters. Its 65 events against 45 deliveries include 18 flagged ones, these two among them. `README.md:80` says no filing or call states why the counts differed; that is true, and the registry file itself shows most of the difference.
- **Defensible version:** the rule is preregistered, so it stays. Add to Limitations: "The holder rule matches names that start `GULFSTREAM AEROSPACE`. It misses `GULFSTREAM LEASING LLC`, whose four registrations in 2020Q4 and 2025Q4 count as deliveries, and it reads a blank name as a customer." Any wider rule goes in `results/exploratory/`, labelled as tried after the fact.

### REGISTRY-5 (S2). Airframes with no bound produce 75 events; the limitation says "can" and gives no count

- **Surface:** `README.md:143`.
- **Evidence:** answer 3. 386 airframes, 75 E1 events in the window, 57 in the holdout, 19 in the last four held-out quarters, 29 of them G-II to G-V family.
- **Defensible version:** "386 of 4,053 airframes have no airworthiness date and no year, so no bound applies. They supply 75 of the 1,251 counted events, 29 of them Gulfstream II to V airframes."

### REGISTRY-6 (S2). The scope rule drops a G700 code; 17 jets registered to Gulfstream are invisible, and their deliveries will be

- **Surface:** `src/gdn/faa.py:184`; `README.md:97`; the dashboard's "On Gulfstream's own registration" chart (`site/data.json` `pipeline`, `GVIII-G700`: 52).
- **Evidence:** `q5b_scope.py` and `q5c_g700.py` on the raw 2026-10-19 and 2026-10-30 zips. ACFTREF `3980222,GULFSTREAM AEROSPACE CORP,GVIII-G700,5,2` carries TYPE-ENG 2, the code the same file gives `G-159` and the Commander `690` and `695` rows. 17 MASTER rows use it, all `GULFSTREAM AEROSPACE CORP`, status `M`, no certificate date: serials 87171, 87172, 87174, 87176 to 87182, 87184 to 87187 and 87191 to 87193. None of the 17 serials is in the 2026-10-19, 2026-10-30 or 2026-11-11 daily table.
- **Effect today:** no past event is missed (0 DEREG rows, no certificate dates). The 2026-10-30 airframe table counts 53 G700s on Gulfstream's own registration, and that day's raw file holds these 17 more. The dashboard's figure, from the 2026-11-11 table, is 52. I could not read a raw file for 2026-11-11.
- **Effect ahead:** when these jets are certificated to customers or exported they will not be counted, with no error.
- **Rubric note:** by its caption the chart's G700 figure is short, which reads as "a wrong number on any public surface". I grade it S2 because the figure follows the stated scope rule and I proved the gap on 10-30 only. The main session may regrade.
- **Defensible version:** caption or Limitations: "The scope rule keeps engine-type codes 4 and 5. The FAA files one G700 code (3980222) under engine-type code 2, so 17 G700s registered to Gulfstream on 2026-10-30 are outside this count." Changing the rule is a dated deviation from the preregistration and must be made, and said, before those jets deliver.

### REGISTRY-7 (S2). Three things stand between the project and a correct 2026Q4 lock

- **Surface:** `config/calendar.json`; `src/gdn/live.py:326`, `:370` to `:375`; `README.md:93`.
- **Evidence:**
  - `config/calendar.json` is `{"releases": {"2026Q3": "2026-10-30"}, "fiscal_ends": {}, "public": false}`. With no 2026Q4 date `run_lock` logs "no release date" and returns, and `in_lock_window` stores no subset.
  - The lock reads `newest_stored(root)`. The only test is `snap >= rel`. The newest stored subset is 2026-10-29. If the release date is set but no download succeeds inside the seven-day window, a run at or after 19:00 ET on the eve locks 2026Q4 from the October file.
  - GitHub's evening run cannot serve the 19:00 ET rule at observed delays (answer 9).
  - 2027Q1 has no fiscal end (answer 8).
- **Rubric:** "Any defect that could let a lock or score be wrong or unverifiable" is S1. None of this touches the 2026Q3 lock, which verifies; I grade it S2 as a forward risk. The main session may regrade.
- **Defensible version:** set the 2026Q4 release date the day GD announces it. Before the eve, check that a subset dated inside the window is in the manifest. State in the README what a missed lock looks like. A freshness test in `run_lock` is a change to preregistered §3.6 and needs a dated note.

### REGISTRY-8 (S2). The key double counts two airframes in the window, and a new FAA code will add more

- **Surface:** `src/gdn/events.py:32`; `README.md:97`, `:143`; 2018Q2 and 2026Q2 mid-cabin counts.
- **Evidence:** answer 1. G150 322 counted in 2016Q2 and 2018Q2; G280 2009 counted in 2026Q2 on a 2012 airframe. Code `398012B` appeared on 2026-10-27.
- **Defensible version:** Limitations: "Two airframes in the window are counted twice or late because the FAA filed them under a second maker code (G150 serial 322, G280 serial 2009). The FAA added a third G280 code (398012B) in October 2026, so this can recur."

### REGISTRY-9 (S3). Eleven mid-size airframes are classed large

- **Surface:** `src/gdn/faa.py:32`, `:185`; `data/processed/serials.csv`.
- **Evidence:** answer 5. 8 `GULFSTREAM 200`, 2 `GULFSTREAM 100`, 1 `GALAXY`; no event in the window; no figure moves.
- **Fix:** one line in Limitations, or leave: the rule is preregistered and harmless here.

### REGISTRY-10 (S3). The backtest subset's gzip header differs from every other date's

- **Surface:** `data/snapshots/2026-10-19/*.gz`; `src/gdn/files.py:71`, `:79`.
- **Evidence:** `q7d_gz.py`: stored byte 9 is 19, rebuilt 255, no other byte differs. The fix to byte 9 landed in commit `64c7eec` on 2026-10-19. `write_gz` never rewrites a file whose content matches.
- **Effect:** the manifest hashes for 10-19 are right for the stored files but cannot be rebuilt from the zip by the current code. The decompressed bytes are identical.
- **Fix:** say so next to the manifest, or record a content hash as well.

### REGISTRY-11 (S3). Two surfaces show the window with its start included

- **Surface:** `site/app.js:129` ("Quarter window": start "to" end); `src/gdn/note.py:397`, rendered in `report/note.html` as "2026Q3's window (2026-07-05 to 2026-10-04)".
- **Evidence:** the rule is `start < date <= end`. The dashboard shows 2026Q4 as 2026-10-04 to 2026-12-31 and the note shows 2026Q3 ending 2026-10-04, so 2026-10-04 appears in both.
- **Fix:** print "after 2026-10-04, through 2026-12-31", or show the day after the start.

### REGISTRY-12 (S3). The comma-in-name fallback mis-cuts on the real file layout

- **Surface:** `src/gdn/faa.py:161` to `:170`; `tests/test_faa.py:39`; `docs/PREREGISTRATION.md` §3.3 ("cut the line at the header line's comma positions").
- **Evidence:** `q_fallback.py`, item 1 of "Also report".
- **Effect:** none today (0 in-scope rows). A latent silent drop.

### REGISTRY-13 (S3). "Lost first-owner records" is right about the mechanism and too narrow

- **Surface:** `README.md:122`; `docs/INTERVIEW_NOTES.md:33`.
- **Evidence:** answer 10. Of the 3 records lost between 10-19 and 10-29, 1 was a first delivery and 2 were later owners' certificates on used jets.
- **Defensible version:** "so the later file has lost certificate records since".

### REGISTRY-14 (S3). "Would drop every mid-cabin delivery" overstates by one

- **Surface:** `README.md:130`.
- **Evidence:** `q_mid.py`: of 197 mid-cabin E1 events in the window, 1 sits under a code whose maker field contains `GULFSTREAM` (G150 serial 322, the double-counted one). Since 2026-10-27 a G280 code also exists under maker `GULFSTREAM`.
- **Defensible version:** "would drop nearly every mid-cabin delivery".

### REGISTRY-15 (S3). Nothing checks that a registry file is sane before it feeds a count

- **Surface:** `src/gdn/faa.py`, `src/gdn/live.py`.
- **Evidence:** items 2 to 5 of "Also report". No test on rows kept, dates parsed or codes in scope.
- **Fix:** log the three numbers on every ingest and stop the lock when one falls far below the day before.

### REGISTRY-16 (S3). A second download on a locked date rewrites that date's airframe table

- **Surface:** `src/gdn/live.py:197` to `:210`.
- **Evidence:** `ingest` calls `write_table` before it tests `locked_dates`. On a fresh runner the raw zip is absent, so `faa.download` fetches again. It did no harm on 2026-10-29: the stored table equals a rebuild from the stored subset, and the Mac's zip has the manifest's hash.
- **Effect:** latent. The path row for a lock date could stop matching the lock.

### REGISTRY-17 (S3). A release stamped late is warned about and still scored as a lock

- **Surface:** `src/gdn/live.py:395` to `:397`, `:413`; `src/gdn/gitops.py:19`.
- **Evidence:** by reading. `score_quarter` sets `locked` from the two files' existence alone.
- **Effect:** latent, and it needs `gh` to stall for more than ten minutes.

### REGISTRY-18 (S3). The Export limitation's comfort rests partly on used jets

- **Surface:** `README.md:138`: "Since 2022 the registry's yearly mid-cabin count has stayed within a few jets of GD's".
- **Evidence:** `q_mid.py`. The figures are right: registry 25, 20, 22, 25, 15 against GD's 24, 22, 18, 22, 13 for 2022 to 2026 first half. Flagged mid-cabin events are 7, 6, 3, 5, 1, leaving 18, 14, 19, 20, 14.
- **Defensible version:** keep the sentence and add "though 7, 6, 3, 5 and 1 of those yearly counts are events flagged as used jets, so the match is looser than it looks in 2022 and 2023."

## What I could not check

- Whether GD counts as deliveries the five jets registered to General Dynamics entities, or any sale of an airframe that Gulfstream itself held for years.
- Whether any blank-name row is a Gulfstream registration.
- The meaning of DEREG `STATUS-CODE` and `INDICATOR-GROUP` values: I did not open the FAA's field guide.
- The 2026-10-24 subset against its zip (no local zip), and any raw file after 2026-10-30.
- Whether the Mac's scheduled job has run since 2026-10-30.
- GD's 2027Q1 period end and its 2026Q4 release date: neither is public.
- Delivery status of any single airframe against an outside source. The flag is registry evidence, checked against the project's own 30-airframe audit and nothing else.
- Whether a future mid-size model name will match the cabin rule.

## What holds

- `serials.csv` and `registry_quarterly.csv` rebuild exactly from the stored 2026-10-19 subset.
- README registry figures reproduce: 0.52 and 0.80 events per delivery (2016, 2019); mid cabin 0.37 and 0.47 (2016, 2017); the 1.18 mean; 0.69, 0.69, 0.72; 206 against 203 and 146 against 63.
- The audit paragraph matches its CSV on every number.
- The lock, its snapshot, its hash, its release time and GD's filing time are consistent and in the right order.
- All 42 fiscal ends match SEC, and 2026-10-04 is confirmed.

## GO or NO-GO

**NO-GO while REGISTRY-1 and REGISTRY-2 stand. GO when they are reworded.** Nothing I found changes a headline number, the lock or the score. The risk is a reader who opens `serials.csv` or the release page: the first shows a 1984 airframe inside the locked count, the second shows a bot where the README says a Mac.

The three things I would fix first:

1. **Say what is counted.** Change the post's method sentence (REGISTRY-1) and the README Method and Limitations text (REGISTRY-3, -4, -5) to give the used-jet share with its numbers: 275 of 1,251, the 5 of 20 in the audit, and the as-of table that shows 0.97 to 1.02 unflagged events per delivery.
2. **Make the Live paragraphs match the record** (REGISTRY-2): the workflow downloads and locked; the Mac is the second path.
3. **Protect the January lock** (REGISTRY-7, -6, -8): enter the 2026Q4 release date when GD announces it, confirm a subset dated inside the window is stored before the eve, and decide in writing, with a date, whether code 3980222 and `GULFSTREAM LEASING LLC` stay as disclosed limitations or become a labelled deviation from the preregistration.
