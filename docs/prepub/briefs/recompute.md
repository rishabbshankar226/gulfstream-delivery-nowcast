# Brief: independent recompute

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `recompute`. Scratch folder: `~/gdn-prepub/agents/recompute/`.

## Goal

Recompute every headline figure of this project from its input data alone, with your own code, so the main session can compare your figures with the published ones. You are the independent pipeline. If you read the project's code or results, the comparison is worthless.

## What you may read (nothing else in the repository)

- `data/processed/gd_deliveries.csv` (GD's reported deliveries, 2016Q1 to 2026Q2, with each fiscal quarter end)
- `data/processed/registry_quarterly.csv` (registry event counts per fiscal quarter, definitions E1 and E2, large and mid cabin)
- `data/guidance.csv` (GD's full-year delivery outlook by earnings call)
- `data/snapshots/` (stored FAA registry subsets: `<date>/ACFTREF.txt.gz`, `MASTER.txt.gz`, `DEREG.txt.gz`, and `MANIFEST.json`). Do not read `data/snapshots/daily/`: those tables are the project's own derived output.
- `predictions/2026Q3.json` (the locked 2026Q3 prediction)
- `docs/PREREGISTRATION.md` (the rules, fixed before the test)
- `docs/prepub/recompute/toy/` (a toy dataset, see below)
- this brief and `_common.md`

You must never open `src/`, `tools/`, `results/`, `tests/`, `README.md`, `report/`, `site/`, `output/`, `docs/build/`, or any other file under `docs/`. Do not import any module from the repository. Do not use `git log -p` or `git show` on those paths. Write your own code in your scratch folder, using only the Python standard library (plus `scipy` only if it is already installed for `python3`; do not install anything).

## GD's 2026Q3 count

GD reported its 2026Q3 Gulfstream deliveries in the earnings release filed under accession `0000040533-26-000036`: 35 large cabin, 5 mid cabin, 40 total. (`data/processed/gd_deliveries.csv` ends at 2026Q2.) GD's fiscal 2026Q3 ended on 2026-10-04.

## The method, as the project's README states it

> **The count.** I read the FAA's `ReleasableAircraft.zip` and keep every aircraft type whose maker or model name contains GULFSTREAM and whose engines are turbojet or turbofan. That keeps the G280, which the registry files under the maker `IAI LTD`, and drops Gulfstream's old turboprops. An airframe is the first three characters of its maker-model code plus its serial number, gathered across the current registrations (MASTER) and the cancelled ones (DEREG). For each airframe I take:
> - **E1**: the earlier of the first customer's registration certificate and the cancellation of Gulfstream's own registration for export;
> - **E2**: the earlier of the first customer's certificate and any cancellation of Gulfstream's own registration.
>
> Either date must fall within a year of the airframe's first airworthiness date (or by the end of the year after its year of manufacture), which keeps out renewed certificates and most used jets. I count the dates in each of GD's fiscal quarters, by cabin size.
>
> **The models.** For each quarter and cabin, the ratio model scales the registry count by how many deliveries GD reported per registry event over the four quarters before. The baselines are the same quarter last year, the last quarter, and GD's guidance pace: the full-year outlook from GD's latest call, less the deliveries already reported that year, spread over the remaining quarters by their usual share of the year. I also report the raw registry count.
>
> **The test.** The design window, 2017Q1 to 2019Q4, chose between E1 and E2 before I computed anything for a later quarter, and the rules were committed in docs/PREREGISTRATION.md before the held-out quarters were scored. Over the 26 held-out quarters, 2020Q1 to 2026Q2, I run one-sided exact sign tests against each baseline with Holm's correction, report the relative miss and the autocorrelation of the differences, and build a past-miss band for each quarter from the earlier quarters' misses only. A truncation test cuts each quarter's own events 30, 60 and 90 days early, and a coverage-drift check watches the latest quarters.
>
> **Live.** Each day my Mac downloads the registry, writes the latest estimate and its airframe table, and, on the day before GD reports, locks the estimate as a GitHub release whose notes carry the file's sha256. When GD reports, the run scores the lock against GD's count. A GitHub workflow runs the same job as a fallback.
>
> **The dollars.** The Aerospace estimate is the delivery estimate × trailing Aerospace revenue per delivery, services included: a mechanical estimate.

Where the README text is not exact enough to compute from, `docs/PREREGISTRATION.md` §3.3 to §3.6 is the rule. If the two disagree, or if a rule is ambiguous, compute both readings, report both, and say so in your output under "Ambiguities". That is a finding the main session wants.

## Part A (required): from the processed files

Work at full floating-point precision and print each figure to 6 decimals. Use the chosen definition from the design window for the held-out quarters, as the preregistration says. Compute and write to your output file:

1. The ratio estimate (large, mid, total) for every quarter it can be computed for, 2017Q1 to 2026Q2, under E1 and under E2.
2. Design window (2017Q1 to 2019Q4, 12 quarters): MAE of same quarter last year, last quarter, raw registry count and ratio under E1 and under E2; which definition the rule chooses.
3. Held-out window (2020Q1 to 2026Q2, 26 quarters), five models (ratio, raw registry count, GD's guidance pace, same quarter last year, last quarter): MAE, mean absolute percentage error (percent of GD's reported total), bias (mean of estimate minus GD's count), MAE for large cabin and for mid cabin separately, and MAE with the four 2020 quarters dropped.
4. The same held-out MAE by calendar year (2020 to 2026) for each of the five models.
5. Three exact one-sided sign tests that the ratio estimate's absolute error is smaller than each baseline's (guidance pace, same quarter last year, last quarter): wins, losses, ties, p. Holm's step-down at 0.05 across the three. The relative MAE against each baseline.
6. The lag-1 autocorrelation of the difference series AE(baseline) minus AE(ratio), in quarter order, for each baseline.
7. GD's guidance pace (large, mid, total, and the outlook used) for every held-out quarter, and for 2026Q3. Say which quarters have no numeric outlook and what they fall back to. The MAE of the guidance pace over only the quarters that have a numeric outlook, and the ratio estimate's and the same-quarter-last-year MAE over those same quarters.
8. The past-miss band for each held-out quarter (low, high, hit or miss), the hit count, the coverage percentage, and the exact Clopper-Pearson 95% interval for the coverage.
9. Deliveries per registry event (GD's reported total over the registry total, chosen definition) for every quarter 2016Q1 to 2026Q2; its mean and sample standard deviation over 2017Q1 to 2025Q2; which of 2025Q3 to 2026Q2 exceed the mean plus two standard deviations. Also the inverse (registry events per delivery) by calendar year, 2016 to 2026, for total and for mid cabin alone.
10. The five held-out quarters with the largest absolute error of the ratio estimate, with estimate, GD's count and signed error.
11. The 2026Q3 score: from `predictions/2026Q3.json` and GD's count above, the absolute miss, the miss as a percent of GD's count, whether GD's count fell inside the locked band, the guidance pace for 2026Q3 and its absolute miss. Also the sha256 of the bytes of `predictions/2026Q3.json`.
12. GD's average quarterly deliveries over 2020Q1 to 2026Q2, and the 2025Q3 count.

## Part B (required): from the raw registry subsets

13. From `data/snapshots/2026-10-19/` (the backtest snapshot), rebuild the airframe table by the preregistration's §3.3 rules and count E1 and E2 events per fiscal quarter and cabin, 2016Q1 to 2026Q2. Compare every count with `data/processed/registry_quarterly.csv` and list each difference (quarter, definition, cabin, yours, theirs). Say how many airframes you found, how many have an E1 date, and how many are large and mid.
14. From `data/snapshots/2026-10-29/` (the snapshot the lock names), rebuild the 2026Q3 prediction: the quarter's E1 events by cabin, the trailing four quarters' registry and reported sums, the ratio estimate by cabin and in total, and the past-miss band (the preregistration says a live band uses every signed error to date, design and holdout). Compare each value with `predictions/2026Q3.json`.
15. In the backtest airframe table, list the models whose cabin class is `large` under the preregistered rule but whose model name is a mid-cabin type (for example a model named `GULFSTREAM 200` or `GULFSTREAM 100`, which the rule's `G200` and `G100` patterns do not match). For each: how many airframes, and how many have an E1 or E2 date falling in 2016Q1 to 2026Q2.

## The toy check (required, do it first)

`docs/prepub/recompute/toy/` holds `gd_deliveries.csv` and `registry_quarterly.csv` with the same columns as the real files, for nine made-up quarters, 2001Q1 to 2003Q1. Your Part A script must take the data folder as an argument so it runs on the toy files unchanged. Run it on the toy folder and report, to 6 decimals: the ratio estimate's total and absolute error under E1 for each of 2002Q1 to 2003Q1, and the MAE over those five quarters. The main session has computed this by hand and will compare. (The toy folder has no guidance file: skip the guidance model there.)

## Output

Write one text file: `docs/prepub/reviews/recompute.txt`. Plain text, one figure per line as `key = value`, grouped under numbered headings that match the list above, with an "Ambiguities" section and a "Could not compute" section at the end. Put the commands that produced it at the top. Keep your scripts under `~/gdn-prepub/agents/recompute/` and also copy them into `docs/prepub/recompute/` (that folder is yours too).

Do not round to match anything. Do not look for the "right" answer anywhere. If a figure looks odd, report it as it is.
