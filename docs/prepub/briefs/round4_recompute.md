# Round 4 brief: blind recompute (`recompute`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are the independent pipeline. You recompute this project's headline figures from its input data alone, with your own code, before you see a single published figure. If you see the published figures first, the comparison is worthless. So the order below is strict.

## Phase A: blind (do this first, and finish it before phase B)

**Your tree for phase A:** `~/gdn-prepub/round4_data/`. It holds only these, and you read nothing else:

- `data/processed/gd_deliveries.csv`: GD's reported deliveries, 2016Q1 to 2026Q2, with each fiscal quarter end.
- `data/processed/registry_quarterly.csv`: registry event counts per fiscal quarter, definitions E1 and E2, large and mid cabin.
- `data/guidance.csv`: GD's full-year delivery outlook, by earnings call.
- `data/snapshots/`: stored FAA registry subsets. Do not read `data/snapshots/daily/`; those tables are the project's own output.
- `predictions/2026Q3.json`: the locked 2026Q3 prediction.
- `docs/PREREGISTRATION.md`: the rules.
- `METHOD.md`: the README's method text, copied out word for word.

GD's 2026Q3 count is not in these files. Read it yourself from GD's earnings release exhibit, filed with the SEC under accession `0000040533-26-000036`. Fetch the filing index and the exhibit from `sec.gov` as `round4_common.md` says. GD's fiscal 2026Q3 ended on 2026-10-04.

Compute, with your own code in your scratch folder, and without importing anything from the project:

1. The ratio estimate for each quarter, by cabin and in total, under E1 and E2.
2. The average miss (mean absolute error) and the bias of five models: the ratio estimate, the raw registry count, GD's guidance pace, the same quarter last year, and the last quarter. Compute each over the 12 design quarters (2017Q1 to 2019Q4) and over the 26 held-out quarters (2020Q1 to 2026Q2).
3. The miss of each of the five as a percent of GD's reported count.
4. Three exact one-sided sign tests of the ratio estimate against guidance pace, the same quarter last year and the last quarter, with Holm's correction. Also the lag-1 autocorrelation of each set of differences.
5. The past-miss band for each held-out quarter, exactly as the preregistration defines it, and its coverage over the 26 quarters. Give an exact Clopper-Pearson 95% interval on that coverage.
6. The guidance pace for every quarter, 2026Q3 included.
7. The 2026Q3 score: the locked estimate and band from `predictions/2026Q3.json`, GD's count from the filing, the miss, the miss as a percent of the count, whether the count fell inside the band, and the miss of the guidance pace and of the same quarter last year.
8. Deliveries per registry event for each quarter, its mean over the whole series, and its value for the last three quarters.

Write all of it as **section A** of your output file: a table per item, with values to four decimals and the code's path in your scratch folder. From the moment section A is written, never edit it. Then start phase B.

## Phase B: compare

**Your tree for phase B:** `~/gdn-prepub/round4/`, the plain copy of the published files.

1. Find every place each of your figures appears in public: `docs/LINKEDIN_POST.md`, `README.md`, `site/data.json` as the dashboard shows it, `report/note.html`, the workbook (recompute it with the `formulas` package in the tools environment), `docs/INTERVIEW_NOTES.md` and `docs/RESUME_BULLETS.md`.
2. Compare each one at the precision shown. Write **section B**: a table of figure, surface and `file:line`, the published value, your value, and the result (`match`, `rounding`, or `MISMATCH`). Every mismatch is a finding.
3. **Section C, consistency:** the same figure across all those surfaces. List any figure shown two ways.
4. Then the report format in `round4_common.md`. Your "Answers" are sections A, B and C.
