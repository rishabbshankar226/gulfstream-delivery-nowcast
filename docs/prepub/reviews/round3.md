# Round 3 attacker (P8.2)

Reviewer `round3`, 2026-11-11. Scripts are in `~/gdn-prepub/agents/round3/`. I edited nothing but this file.

**The tree moved while I read it.** I started at `a7fcb3c` on a clean tree. The main session then committed `9061039`, `e041ea1`, `719c377` and `4ca7d35`. Every finding below was rechecked at `4ca7d35`, and once more just before I handed back: `git log --oneline | head -1` still printed `4ca7d35`, and `git status --short` listed only this file and `docs/prepub/VERDICT.md` as untracked. Anything committed after that I have not seen; R3-8 is the finding most likely to be overtaken. Two things I had drafted (the F002 row and `GO_PUBLIC.md` step 4 still describing `dashboard.png` as the README's image) were corrected by `4ca7d35` before I wrote them up, so they are not findings.

## Verdict

**I found no S1.** Counts: S1 0, S2 4, S3 6.

No public figure I recomputed is wrong. The four S2 are round 2 fixes that reached some of the places the reviewers named and not others, and one clause in the post that says more than the README does.

## The record (item 7)

- `shasum -a 256 predictions/2026Q3.json` printed `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23  predictions/2026Q3.json`. It matches.
- `git diff --stat 36fed31..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` printed nothing, at `a7fcb3c` and again at `4ca7d35`.
- `shasum -a 256 report/note.html` printed `4f4dffca...243e09`, equal to `output/GD_research_note.inputs.sha256`. `output/GD_research_note.pdf` and `site/GD_research_note.pdf` have the same hash (`c8792588...aab592`).

## Findings

### R3-1 (S2). The workbook still shows 20.1% beside 32.0, 40 and 8.0

- **Attacks:** F086 ("The percentage is printed as 20% wherever it appears"), status `fixed`.
- **Surface:** `output/gd_gulfstream_model.xlsx`, sheet `Live`, cell `B18`; `src/gdn/workbook.py:18` and `:189`.
- **Evidence:** `fmt.py` (openpyxl) printed `B18 '=B17/B16' 0.0%`, `B17 '=ABS(B11-B16)' 0.0`, `B11 '=B9+B10' 0.0`. `grep -n "% of reported\|0\.0%" src/gdn/workbook.py` printed `18:F_USD, F_AIR, F_PCT, F_RATIO = "#,##0", "0.0", "0.0%", "0.00"` and `189: ("Miss, % of reported", "=B17/B16", F_PCT, False),`. `pct.py` on `results/live/2026Q3_score.json` printed `Live!B18 value 0.2011697860962567 shown with format 0.0% as 20.1%`. So Excel shows nowcast 32.0, GD reported 40, miss 8.0, miss 20.1%: the same four figures F086 was raised on. The README (line 6, line 106), the note and the dashboard say 20%. The file holds formulas with no cached values (`cached.py`, openpyxl with `data_only=True`, printed `{'B11': None, 'B17': None, 'B18': None}`), so I computed the display; I did not open it in Excel.
- **Fix:** give that cell a whole-percent format (`0%`) in `workbook.py`, rebuild, and add an assertion to `tests/test_outputs.py` on the cell's number format. Then correct F086's "wherever it appears" if any place is left.

### R3-2 (S2). The "5 of the 42" caveat did not reach the note, and the five are not quite what the README says

- **Attacks:** F093 (FINANCE-2), status `fixed`.
- **Surface:** `report/note.html:56` (key point 2) and `:78` (locked-quarter paragraph); `README.md:106` and `:157`; `docs/INTERVIEW_NOTES.md:30`.
- **Evidence, first part:** FINANCE-2 names four places: `README.md:106`, `report/note.html:56`, `:78` and `docs/INTERVIEW_NOTES.md:30` (`round2_finance.md:165`). `grep -n -o "the raw registry count (42) by 2\|The raw count of 42 events missed by 2[^.]*\." report/note.html` printed line 56 and line 78, both with no word on what the 42 were. `grep -c "at least three years old" report/note.html` printed `1`, and that one is the 246 of 1,251 sentence in the limitations (line 94). The README and the interview notes carry the caveat; the note, which a finance reader opens first, does not.
- **Evidence, second part:** FINANCE-2 also said the five by year are not the five by type. `q3events.py` reads the lock's own table (`data/snapshots/daily/2026-10-29.serials.csv.gz`) and printed the events with a year field at least three years back: `G-1159A 445 (1984)`, `GV-SP (G550) 5260 (2009)`, `GVI (G650ER) 6206 (2016)`, `GULFSTREAM G150 311 (2014)` and `GVIII-G700 87118, year 2006, first airworthiness 2026-03-06`. A G700 with a 2006 year field is a registry entry error, not an old airframe. The same script printed a `G-IV 1335` event with no year, which the count of five leaves out. So "5 of the 42" is right by the year field. It also equals the number of events on the older types in the script's model count (one each of G-IV, G-1159A, G550, G650ER and G150), which agrees with FINANCE-2's "37 were current-production models". But the two fives are not the same five: one counted by year is a new G700, and the G-IV is not counted. The README's wording "by the registry's year of manufacture" keeps the sentence true; nothing tells the reader the field is wrong for one of them.
- **Fix:** in `src/gdn/note.py`, add the README's sentence to the locked-quarter paragraph and a clause to key point 2. In the README's Used jet limitation, say that the year field is the registry's own and is wrong for at least one of the five (the G700, serial 87118), and that one G-IV in the quarter carries no year.

### R3-3 (S2). One of the two interview-note lines FINANCE-11 and R2-STAT-7 named was not changed

- **Attacks:** F092, status `fixed`.
- **Surface:** `docs/INTERVIEW_NOTES.md:33`.
- **Evidence:** both reviewers cite `:7` and `:33` (`round2_finance.md:229`, `round2_statistician.md:136`). Line 7 now carries "minutes before and in the same session, so only the locked quarters are out of sample in the strict sense". Line 33 still reads "I fixed the rules before I scored the held-out quarters" and "a test that was set up so it could fail", with no qualifier (`residue.py 'I fixed the rules'` printed both lines). Line 33 is the answer to "Why publish a model that lost?", which will be said aloud on its own, away from line 7.
- **Also, not part of this finding:** `report/note.html:67` says the design window "chose the event definition (E1) before I scored the 26 quarters" with no qualifier. Neither reviewer named it, it speaks only of the event definition, and the commit order backs it, so I leave it out of the count. A half-sentence there ("minutes before, in the same session") would make the note match the README.
- **Fix:** line 33: "The rules were committed before the held-out scores, minutes before and in the same session, and the answer came back plainly: ...". Keep "set up so it could fail" only if the sentence also says the held-out data was already in the repository.

### R3-4 (S2). The post says "held out from setting the rules" with no qualifier; the README says the commit order is all that backs it

- **Attacks:** the closure of F021, F027 and F091 as far as the post goes. Round 1's compliance reviewer passed this clause "for commit order" (`compliance.md:65`) before round 2 found the point below.
- **Surface:** `docs/LINKEDIN_POST.md:6` ("Backtest, held out from setting the rules:"); `src/gdn/report.py:578`; `docs/prepub/POST_ALTERNATES.md:13` and `:33`; pinned by `tests/test_after_score.py:134` and `tests/test_wording.py:74`.
- **Evidence:** `README.md:119` now says "The commit order is all that backs the words 'held out' and 'preregistered' here: the registry counts and GD's counts for every quarter were already in the repository when the definition was chosen" and "The rules for reading GD's calls quote two of the transcripts, so they were written with those calls in hand, and exactly 22 quarters meet the threshold of 22". `docs/PREREGISTRATION.md:46` names the 2025-07-23 call and quotes its transcripts ("$150 million to $155 million"), and `:45` gives as its example "five to six fewer than the 145", the wording of the 2023-07-26 call (`data/guidance.csv:16`: "five to six fewer aircraft than the 145 we forecast"). Both calls are inside the held-out window. The guidance pace of 6.9 in the post's next sentence is built by those rules. So the clause holds for the event definition and for the commit order, and it does not hold in the strict sense for the rules that build the baseline the post names. The README carries that qualifier and the post carries none. The clause is older than the audit (`git show 36fed31:docs/LINKEDIN_POST.md` has "26 past quarters held out from setting the rules" on line 3) and it is not part of the preregistered sentence, which already says "held-out quarters". The audit qualified the same words on the README (F021, F027, F091) and in the interview notes (F092) and left them bare here.
- **Why S2 and not S1:** this is the same defect as F027, F091 and F092, an unqualified "held out", which the register grades S2. It is not the F084 kind (a clause false for part of what it covers): the rules were committed before the scores, and the event definition was chosen on the design quarters only. The reviewers who raised the same words in the interview notes wrote "framing, not a false claim" (`round2_finance.md:230`).
- **Fix:** change the lead-in to "Backtest:" or "Backtest on past quarters:" in `report.py`, in both alternates, in the paste-ready copy at `GO_PUBLIC.md:130` and in the two tests. The post is 1,280 characters, so a shorter lead-in fits.

### R3-5 (S3). "Likely too narrow" survives on three surfaces after the README dropped it

- **Attacks:** F034 (STAT-3) and the "Related" note under R2-STAT-11, which is in F098 as open.
- **Surface:** `report/note.html:78` and `:96`, `site/app.js:170`, `docs/INTERVIEW_NOTES.md:24`, against `README.md:160` ("so it may not fit a live lock").
- **Evidence:** `residue.py 'too narrow'` printed those four lines. STAT-3's evidence was that the repository points the other way: in all four as-of quarters the copy from a few weeks after the quarter missed by less than the finished copy (`README.md:136`). The second statistician called the phrase "a fair hedge" and the README's wording "the better" (`round2_statistician.md:169`). One lock outside the band does not show a direction.
- **Fix:** use the README's "may not fit a live lock" in `note.py` (two places), `app.js` and the interview notes.

### R3-6 (S3). `POST_CHECK.md` quotes a sentence the post does not contain, and the post's "It" has no clear subject

- **Attacks:** `docs/prepub/POST_CHECK.md:39`; `docs/LINKEDIN_POST.md:6`.
- **Evidence:** `grep -c "That test reads a registry copy"` printed `0` for `docs/LINKEDIN_POST.md` and `1` for `POST_CHECK.md`; `grep -c "It reads a registry copy"` printed `1` for the post. The check quotes the wording of the alternates. In the post, "It reads a registry copy" follows the parenthesis "(Registry count: my scaled estimate; the pace: mine.)", so "It" reads as the pace.
- **Checked and holds:** `postlen.py` printed `len with newline 1280 stripped 1279`, as `POST_CHECK.md` says.
- **Fix:** "The backtest reads a registry copy ..." in `report.py` (ten more characters; with R3-4's shorter lead-in the post stays under 1,300), then quote the post as it stands in `POST_CHECK.md` and refresh the paste-ready copy at `GO_PUBLIC.md:130`.

### R3-7 (S3). F076 is left open for want of a source, but the fix needs none

- **Attacks:** F076, status `open: needs a sourced claim for the EASA date`.
- **Surface:** `report/note.html:65`, claim `pc-g700-first-deliveries` in `report/claims.json`.
- **Evidence:** the note says in its own voice "Gulfstream began G700 deliveries in the second quarter of 2024, after FAA and EASA certification." The claim's quote is GD's: "which began deliveries in the second quarter of 2024 following ... (FAA) and ... (EASA) certification" (`claim.py pc-g700-first-deliveries`). SELL-19 reports that EASA certification (2024-05-15) came after the first deliveries (April 2024), from a web search I did not repeat. Cutting the clause leaves a sentence the same quote still supports, so no new source is needed.
- **Fix:** "Gulfstream began G700 deliveries in the second quarter of 2024." Or attribute the order: "GD's annual report says deliveries began ... following FAA and EASA certification."

### R3-8 (S3). The after-state on file predates the last four commits that changed surfaces and tests

- **Attacks:** the closing evidence of F003, F099 and the "After" table that every `fixed` row with a test leans on (R5).
- **Evidence:**
  - `docs/prepub/BASELINE.md:41`: "Measured 2026-11-11, 20:48 to 20:51 ET, at commit `7277a6d`". `git log -1 --format='%h %ci' -- docs/prepub/BASELINE.md` printed `37a72ea 2026-11-11 19:56:37 -0600`. Four commits after `7277a6d` changed surfaces or tests (`37a72ea`, `048dbb3`, `a354170`, `9061039`). `git diff --stat 7277a6d..HEAD -- README.md report/note.html site/app.js site/index.html output/gd_gulfstream_model.xlsx docs/LINKEDIN_POST.md docs/INTERVIEW_NOTES.md src/gdn` printed `11 files changed, 161 insertions(+), 85 deletions(-)`, among them `README.md` (34 lines), `report/note.html` (25), `src/gdn/report.py` (93), `src/gdn/note.py` (45), `src/gdn/workbook.py` (14) and `site/app.js` (8). `git diff --stat 7277a6d..HEAD -- tests` at `a7fcb3c` printed 3 files, 7 insertions, 6 deletions, and `9061039` then added `tests/test_model_direct.py`.
  - `FINDINGS.md:16` (F003) says "Now `170 passed`"; `GO_PUBLIC.md:57` says "176 tests passed when the audit ended". No file in `docs/prepub/` records a run that printed 176.
  - `BASELINE.md:49` says the ledger printed `rows 2794  flagged 0`. `ledger.py` on the current `docs/prepub/LEDGER.csv` printed `data rows 2852` and `status {'traced': 2852}`. Flagged 0 still holds for the file as committed; the row count on record is stale.
  - `docs/prepub/REVERT_TESTS.md` was last committed at `f34d393`. `git log f34d393..HEAD -- tests/test_after_score.py tests/test_prepub_text.py tests/test_site_a11y.py` printed `a354170`: all three test files it runs changed after its 19 results were recorded.
  - F099 and D14 cite "`BASELINE.md`, Fresh clone". `grep -n "Fresh clone" docs/prepub/BASELINE.md` printed nothing, and `docs/prepub/PLAN.md:56` still reads `| P8.4 | Fresh clone check | todo | |` beside F099's `fixed`.
  - The gate's four failing lists (D10, `BASELINE.md`) were printed at `7277a6d`; `a354170` added figures to the README and the note after that.
- **What I could not check:** I may not run `make`, `pytest` or the gate, so I do not say any of these would fail. I say the numbers on file were printed before the last edits that could change them.
- **Fix:** rerun the tests, the gate, the ledger and the revert harness at the final commit, write the outputs into `BASELINE.md` with that commit's hash, add the Fresh clone section, and make F003 and `GO_PUBLIC.md` quote the same count.

### R3-9 (S3). Section 2 does not map every reviewer finding, and two rows cite evidence that no longer reads as stated

- **Attacks:** `FINDINGS.md` section 2 ("maps every reviewer finding to a row here"), F080, STAT-16.
- **Evidence:**
  - `scids.py` printed the IDs in the three source files: `SC-1` to `SC-14` and `SRC-G-1` to `SRC-G-5`. In `FINDINGS.md` it found only `SC-1`, `SC-4`, `SRC-G-1`, `SRC-G-4`. Fifteen IDs have no row in section 2: SC-2 and SC-5 (both S1 in their reviewer's grading), SC-3, SC-6 to SC-14, SRC-G-2, SRC-G-3, SRC-G-5. I checked the two S1 on the tree and both are gone: SC-2's section (`grep -c "What the street watches\|watch list" report/note.html` printed `0`) and SC-5's Marine outlook sentence (`grep -c "18 billion\|7\.4%" report/note.html` printed `0`). The outlook paragraph that remains at `note.html:82` is headed "before the release" and opens "As of GD's 2026-07-29 call". So this is a gap in the map, not a surviving defect that I found. SC-9 to SC-14 and SRC-G-2, -3, -5 I did not chase.
  - F080 says the accession is in the sources list, "`grep -c`: 1". `grep -c "0000040533-26-000036" report/note.html` now prints `2`, and both hits are exhibit text (lines 81 and 84). The sources list at line 110 carries the folder URL (`000004053326000036`, no hyphens). The fix is present; the evidence line is not what the command prints.
  - STAT-16 is `fixed` in section 2 (line 194) and its row F040 is `refuted` (line 53). Both are fair (the README sentence was added, the lead was refuted), but the two statuses read as a mismatch.
- **Fix:** add the fifteen IDs to section 2 with their rows (F036, F065, F066, F061 cover most), correct F080's evidence to the URL form, and write STAT-16 as "fixed (README sentence); the lead itself refuted".

### R3-10 (S3). The new 2026-10-30 guidance row carries a second sentence and a speaker title that no record in the audit checks

- **Attacks:** F054, status `fixed`.
- **Surface:** `data/guidance.csv:29`.
- **Evidence:** the row's quote is "We do not plan to update segment guidance. As usual, we will provide our forecast for 2027 in January after our planning process has concluded." with speaker "Phebe Novakovic, Chairman and Chief Executive Officer". F054, D16 and `sources_guidance.csv:38` record only the first sentence and "the CEO". `callq.py` found no cached copy of that call under `data/raw/sources/` (the newest is `calls/2026-07-29-fool.*`), so nothing in the tree can check the row, unlike every earlier row. The outlook is blank, so no figure depends on it. I did not fetch the page: the main session's second fetch of it was refused (D16) and I did not route around that.
- **Fix:** cache the transcript under `data/raw/sources/calls/` as the other calls are, check both sentences and the title against it, or cut the quote to the one sentence that was read.

## What I attacked and could not break

**New README numbers against their files (item 1).** `nums.py`, `plans.py`, `used.py` and `q3events.py` read `results/holdout.csv`, `results/metrics.json`, `results/live/2026Q3_score.json`, `data/quarter_plans.csv`, `data/processed/serials.csv` and the daily tables. Each printed the README's figure:

| README figure | Script output |
|---|---|
| 5.5, 6.9, 4.6 over 26 | `ratio 5.5234, guidance 6.9173, seasonal 4.6154` |
| 2023 and 2024: 12.5 against 3.5; other 18: 4.4, 4.4, 6.4 | `guidance 12.5149, ratio 3.4817`; `guidance 4.4294, seasonal 4.4444, ratio 6.4308` |
| guidance closer in each of the last five quarters, the lock included | 2025Q3 6.802 against 5.986; 2025Q4 13.399 against 5.5; 2026Q1 7.381 against 6.0; 2026Q2 3.81 against 3.722; 2026Q3 8.05 against 6.16. 2025Q2 went the other way (1.653 against 6.141), so five is exact |
| stated plans: 6.0, closer in 12 of 26; pace for 2023Q3 43.1 | `guidance mae with plans: 6.018...  ratio closer: 12  ties 0`; `2023Q3 pace 43.074` |
| read as 117: 6.7, 13 of 26; both: 5.7, 11 of 26 | `results/exploratory/sensitivity.md` rows: 6.66, 13 of 26; 5.70, 11 of 26 (generated; I did not rebuild the 117 reading myself) |
| 0.69, 0.69, 0.72 against 1.18 | `2025Q4 0.692, 2026Q1 0.691, 2026Q2 0.719`, mean `1.1824` |
| one standard error about 0.20 | `1/sqrt(26) = 0.1961` |
| count 42 at the lock, the same in every daily snapshot to 2026-11-11 | 14 tables from 2026-10-29 to 2026-11-11, each `42` |
| 0.76 and 0.95 | 163 over 215; 40 over 42 |
| 81 jets left, even split 40.5 | 160 less 38 and 41; 81 over 2 |
| 246 of 1,251 (19.7%), 76 with no year; 386 of 4,053 airframes, 75 events | `246 share 19.7 no year: 76`; `386`; `4053`; `75` |
| Gulfstream Leasing: four registrations in 2020Q4 and 2025Q4 | serials 72001, 73002 (2020-11-13), 87001, 88001 (2025-10-07) |
| eight quotations added by the audit (10-K revenue sentence, the two 2022-01-26 phrases, the 2023-07-26 plan, the two G280 phrases, "10 fewer aircraft", the tariff sentence) | `quotes.py` and `q10k.py`: each `FOUND` in the cached source the README or the note names |

- **Note, "5.3 for the registry estimate" on the 22 sourced quarters** (`note.html:71`): the year table suggested 5.2. `nums.py` printed `5.2503`, which rounds to 5.3. It holds.
- **Note Exhibit 8:** the misses follow from `data/processed/segments_reported.csv` (3,536, 4,960, 2,386, 3,684; operating earnings sum 1,580).
- **Note Exhibit 10, Marine Systems backlog $146.9B:** I suspected a company total set against a segment figure. `sources_claims.csv:226` and `sellside.md:295` both read the release: Marine 146,865, company 220,339. It holds.

How item 1 was done: by recomputing the figures above and by searching every surface for the phrases the fixes removed. I did not open each of the S1 and S2 `fixed` rows one by one against its surface; R3-1, R3-2 and R3-3 came from reading the round 2 findings against the tree.

**Fixed rows whose commits miss the surface named (item 3, second test).** `git show --stat --format=` on the twelve commits that carry the surface fixes (`4ea45a0`, `7aaa5c1`, `7c2a99f`, `9c0f7b8`, `37a72ea`, `a354170`, `d0247f7`, `ba8453f`, `462ad30`, `522a422`, `048dbb3`, `1c5a76c`), compared with the rows by hand. Two rows list commits that do not touch every surface they name: F026 names the note but lists `4ea45a0` and `462ad30`, neither of which touches `report/note.html`; F029 names the interview notes but lists `4ea45a0`, `7aaa5c1` and `1c5a76c`, none of which touches `docs/INTERVIEW_NOTES.md`. In both cases the surface carries the fix today (`note.html:56` "made while the repository was private"; `INTERVIEW_NOTES.md:18` "The pace is my construction"), so the commit lists are short, not the fixes. No other mismatch found. F005 says a `public_since` date "sits beside the key"; `config/calendar.json` has the keys `releases`, `fiscal_ends`, `public` and no `public_since` yet (`used.py`), which is the state `GO_PUBLIC.md` step 3 expects, and the wording on every surface is the private one.

**Refutations (item 2).**
- F040: `site/app.js:279` draws the path for `current()`, the newest quarter with a lock or a score, which is 2026Q3. `site/data.json` carries the 2026Q4 part figure (`14.307`, band `3.59` to `21.11`, snapshot 2026-11-11) under `live[1].latest` and `path["2026Q4"]`, and the page does not print it. `residue.py '13\.55|2\.8 to 20\.4|14\.3\b'` found nothing on any surface. The refutation stands. The row's 13.55 is an older snapshot's figure.
- F041: `residue.py '31\.1\b'` found nothing. Stands.
- F038, F071, F078: these rest on the spec and on R7, not on a measurement. I found nothing against them.
- F043 and sources_claims cause-10: I could not refetch the other study, so I neither confirm nor attack them.

**Errata and open rows (item 4).** I read E1 to E10 against the README. E5 (17 G700s outside the scope rule) and E6 (four Gulfstream Leasing registrations) are disclosed where the reader meets the figures (`README.md:159`, `site/app.js:343`), and neither is a wrong number today. The one open row I would close now is F076 (R3-7). F081 (the undated no-position sentence) is rightly the owner's.

**Ten reviewer findings picked at random (item 5).** `pick.py`, `random.seed(20261111)` over the 176 IDs of the eight review files:

| Finding | Row and status | Tree |
|---|---|---|
| COMPLIANCE-2 | F002 fixed | README image is `track_record.png`; `dashboard.png` shows the scored card. Matches |
| COMPLIANCE-14 | F030 fixed | dashboard eyebrow says "not affiliated"; README line 15; note footer. Matches |
| COMPLIANCE-20 | F037 erratum | E1 and `GO_PUBLIC.md` step 5. Matches |
| STAT-11 | F074 open | no interval in the README. Matches |
| REGISTRY-7 | F017 fixed, F039 and F062 errata | guard at `src/gdn/live.py:384`; E2, E4. Matches |
| REGISTRY-15 | F063 open | Matches |
| SELL-22 | F067 fixed | `About!A2` reworded; `Live` holds GD's count and the pace. Matches |
| SELL-26 | F010 fixed | `docs/build/README.md` names `FACT_CHECK.md` F1 and F2. Matches |
| FINANCE-11 | F092 fixed | line 7 fixed, line 33 not: R3-3 |
| R2-STAT-11 | F098 open | Matches |

Nine of ten match. The tenth is R3-3.

**The post (item 6).** Every figure in it is one the scripts above printed. "Outside my 80% band of past misses" gives the level and not the coverage (18 of 26); the second statistician accepted that wording for the post (`round2_statistician.md:162`), so I do not raise it. What I raise is R3-4 and R3-6.

**Phrases earlier rounds removed.** `residue.py` over the post, README, dashboard, note, interview notes, resume bullets, alternates and errata found none of: `20.1%`, "had years to fill", "first customer", "before GD reports it", "overstates the swing", "once the repository is public", "Each day my Mac", "is scored on", the word "gate" in the README, an en or em dash, or a word on the R8 list.

## How I worked, where it left the brief

- Two early commands used `paste` and `bc` to add a count, and one `grep -rl` ran over the whole tree, `data/raw` included, printing file names only. Neither is on the brief's allowed list. After that I used scratch scripts and named paths.
- `q3events.py` imports `gdn.live` and `gdn.events` to read the daily tables (`table_dates`, `read_table`, `events.count`). It writes nothing. `quotes.py`, `q10k.py` and `callq.py` search the cached sources under `data/raw/sources/` by script and print matches only.
- I made no network request.

## What I could not check

- The tests, the gate, the ledger run and the revert harness (R3-8). I may not run them.
- The twelve links that return 404 until the repository is public, and the lock release on GitHub.
- The Motley Fool page for the 2026-10-30 call (R3-10) and the other study's data file (F043).
- The dashboard as a browser renders it. I read `site/app.js`, `site/data.json` and the screenshot `output/charts/dashboard.png`.
- The workbook as Excel shows it. I read formulas and number formats with openpyxl.
- The 2016 restatement sentence (F082) and the as-of table; I did not recompute them.
