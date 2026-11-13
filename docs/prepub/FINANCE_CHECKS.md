# Finance checks (P4.7)

Run by the main thread on 2026-11-11 with the five reviewers' reports in hand. Each line of P4.7 has an answer, the evidence, and the finding it led to if any.

## 1. Look-ahead

**Each guidance row was public before the quarter it feeds: yes.**

- A script over `data/guidance.csv`, `data/processed/gd_deliveries.csv` and the project's calendar (`model.outlook_for`'s rule) printed `held-out quarters 26 with an outlook 22 look-ahead violations 0`. For each of the 22 quarters the outlook used comes from a call dated on or before the quarter's fiscal end and before that quarter's own release was filed, and every year-to-date count it subtracts was filed before that release.
- The sell-side reviewer rebuilt the pace independently and got the same: `MAE guidance (rebuilt) 6.9173 sourced n 22 ... lookahead flags 0`.
- A call held inside a quarter feeds that quarter's pace. That is not look-ahead against GD's report, but it means the pace knows what GD said about four weeks into the quarter. On six of those calls GD also gave the quarter's own plan, which the pace ignores: F058.

**No band, window or rule choice used a held-out quarter: yes for the arithmetic, with one stated limit.**

- The band for a quarter is built from that quarter's earlier misses only (`DEFECT_TRACE.md`, P5.3, "a band computed with information from after the quarter": absent; the recompute subagent rebuilt every band from the data files and matched, `RECOMPUTE_DIFF.md`).
- The scale for a quarter uses the four quarters before it, never the quarter itself (same trace).
- The design window, 2017Q1 to 2019Q4, made the one choice (E1 over E2). The held-out window starts at 2020Q1.
- The limit: the registry counts and GD's counts for every quarter were already in the repository when the rules were committed, 14 minutes after the counts and 2 minutes before the scores (F021). The README's "The test" paragraph says the commit order is all that backs "held out". An outsider cannot rule out a peek, and the README says so.
- One look-ahead in the design window: the 2017 estimates use 2016 counts as restated later in 2017 (F082, disclosed). No held-out quarter uses a 2016 count.

## 2. Survivorship and exports

**How exported and deregistered airframes move the count.**

- An export off Gulfstream's own registration is an E1 event (`src/gdn/events.py`: the earliest `DEREG` row held by Gulfstream with an export country). A jet exported with no US registration at all leaves no record; the README's Export limitation says so.
- A deregistered airframe stays in the FAA's `DEREG` file, so its customer certificate still counts.
- The registry keeps one certificate per airframe: the current one. When a jet is resold or its certificate renewed, the first owner's date is gone. The registry reviewer measured it: 1,250 of the 1,251 counted events rest on a single surviving record, and archived copies of the registry held more events for old quarters than the 2026-10-19 copy does (README: 146 against 63 for the four quarters before 2017Q1, 206 against 203 before 2026Q2).

**Does that explain deliveries per registry event drifting from 1.18 to about 0.70? In part, and no filing states a cause.**

- Lost records push old years' ratios up (1.92 in 2016, when the registry shows about half of GD's deliveries) and leave recent years' ratios low, because recent records have not yet been lost.
- Used jets push recent ratios down further: 246 of 1,251 counted events (19.7%) sit on airframes at least three years old (F033), and the sell-side reviewer found 39 of the 215 events behind the 2026Q3 lock's scale on types GD no longer builds.
- Four registrations to Gulfstream's own leasing arm count as deliveries (F055).
- The README states the drift (0.69, 0.69, 0.72 against 1.18), states that the ratio absorbs it only with a lag, and makes no claim of cause. The one-sided preregistered flag cannot see a fall (F051). Finding: F032, F051, both fixed.

## 3. Restatements

**Did GD revise any earlier quarter's count? Only 2016.**

- `reviews/sources_deliveries.csv`, columns `first_reported_total` and `later_restated_total`: the four 2016 quarters differ (27, 34, 27, 27 first reported; 28, 36, 29, 28 restated on the ASC 606 basis). No quarter from 2017Q1 to 2026Q3 was restated.

**Does every score use the count as first reported? Yes for every held-out and live quarter.**

- Each count from 2017Q1 on is the one in that quarter's own release (43 of 43 rows verified against the exhibits, five spot-checked again by the main thread).
- 2016 is used only as lag quarters for the 2017 design-window estimates, on the restated basis, from releases filed after those quarters ended. Finding F082, fixed by disclosure.

## 4. Breaks

`results/exploratory/sensitivity.md` (built by `make all`, labelled as tried after the fact) drops each. Average miss in aircraft:

| Window | Quarters | Registry estimate | Guidance pace | Same quarter last year | Estimate closer than guidance |
|---|---|---|---|---|---|
| All held-out quarters (preregistered) | 26 | 5.52 | 6.92 | 4.62 | 14 of 26 |
| Without 2020 (COVID) | 22 | 5.35 | 7.41 | 4.45 | 12 of 22 |
| Without 2023Q1 to 2024Q1 (before G700 deliveries began) | 21 | 6.04 | 5.42 | 4.86 | 9 of 21 |
| Without 2023 and 2024 | 18 | 6.43 | 4.43 | 4.44 | 6 of 18 |
| Only 2023 and 2024 | 8 | 3.48 | 12.51 | 5.00 | 8 of 8 |

Dropping 2020 changes little. Dropping the quarters before G700 deliveries began reverses the comparison with the guidance pace. The README says the estimate's lead over the guidance pace comes from 2023 and 2024 (F023). The same quarter last year stays ahead of the estimate in every row but the last.

## 5. Conventions

- **Percentage misses are of the reported count.** `results/live/2026Q3_score.json`: `ape_pct` 20.117 equals `ae_total / reported.total * 100`. The README's "Average % miss" is now defined in a sentence as the mean of each quarter's miss as a share of that quarter's deliveries (F050).
- **One rounding rule per surface.** `SURFACE.md` records it: one decimal for headline misses, two for the yearly and exploratory tables, each labelled. The ledger compares every shown figure with its source at the precision shown and prints 0 `rounding` rows on the final tree; plant 2 (69.2% shown as 69.3%) and plant 7 (4.6 shown as 4.7) prove the rule fires.
- **A figure shown two ways on two surfaces.** Two were found and fixed: the inverse coverage units (F032) and "registry count" for the scaled estimate beside "Raw registry count" (F012). The exploratory tables print 5.52 and 6.92 where the headline prints 5.5 and 6.9; both are the same figures at the table's stated precision.

## 6. The note

- **No rating, price target or "initiation" wording.** A script over the note's text: `initiat` 0 hits, `overweight` 0, `underweight` 0, `outperform` 0, `recommend` 0, "buy " 0, "sell " 0. "price target" appears twice, both in the disclaimer "No rating or price target".
- **A disclaimer on every page.** `pypdf` on `output/GD_research_note.pdf`: 8 pages, and each page's text begins "Student research project. Not investment advice. No rating or price target. Not affiliated ..." (F030).
- **A line stating the owner holds no position in GD.** The note carries "The author holds no position in General Dynamics." on page 1 and in the footer; the README carries "I hold no position in General Dynamics". The build carries the sentence forward from `~/.gdn_disclosure` or the earlier note, undated. Only the owner can state it: F081, open until the owner confirms and dates it in `GO_PUBLIC.md` step 1.
