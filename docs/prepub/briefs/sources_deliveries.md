# Brief: source check of GD's delivery counts (P3.1)

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `sources_deliveries`. Output file: `docs/prepub/reviews/sources_deliveries.csv`, plus a short notes section you return in your final reply. Scratch folder: `~/gdn-prepub/agents/sources_deliveries/`.

## Goal

Check every Gulfstream delivery count the project uses, 2016Q1 to 2026Q3, against the delivery table in GD's earnings release exhibit on SEC EDGAR, by accession number. Large cabin, mid cabin and total for each quarter.

## Inputs

- `data/processed/gd_deliveries.csv`: `quarter,fiscal_end,large,mid,total,accn,filed`, 2016Q1 to 2026Q2. The `accn` column is the accession number of the 8-K whose Exhibit 99.1 the count came from.
- 2026Q3 is stored only in `results/live/2026Q3_score.json` (`reported` and `accn` fields).
- GD's CIK is 40533. An accession `0000040533-26-000036` lives at `https://www.sec.gov/Archives/edgar/data/40533/000004053326000036/` (the index page lists the exhibit files; the filing index JSON is at the same path plus `index.json`).

Do not use the project's cached copies in `data/raw/sec/` as the source, and do not import `src/gdn/sec.py`. Fetch from `sec.gov` with `urllib` and the header from `~/.sec_ua`, as `_common.md` says. Cache what you fetch in your scratch folder so you fetch each file once. Write your own parser for the "Gulfstream Aircraft Deliveries (units)" table. After your own check is done, you may compare with `data/raw/sec/` to explain a difference.

## What to check for each quarter

1. The accession exists, is a GD 8-K (item 2.02), and its Exhibit 99.1 is the earnings release for that quarter. Record the filing date and the SEC acceptance timestamp if the index shows it.
2. The exhibit's delivery table gives large-cabin, mid-cabin and total units for the quarter. Quote the three figures as the exhibit prints them (the quarter column, not the year-to-date column) and compare with the CSV.
3. The `fiscal_end` in the CSV equals the period end the release states for that quarter ("Three months ended ..."). Quote it.
4. The `filed` date in the CSV equals the filing date.
5. 2016: GD adopted ASC 606 on 2017-01-01 and restated 2016. The project takes 2016's counts from the restated prior-year columns of the 2017 releases. Confirm that from the exhibits: quote the 2016 figure in the 2017 release, and fetch the original 2016 release for the same quarter (find its accession through `https://data.sec.gov/submissions/CIK0000040533.json` and its older-filings files) and quote the count as first reported. Record both.
6. Restatements after 2017: for every quarter from 2017Q1 on, check whether the following year's release (the prior-year column) shows the same count as first reported. Flag any quarter GD later revised, with both figures.
7. Year-to-date cross-check: the four quarters of each year should sum to the full-year figure in the fourth-quarter release. Flag any year where they do not.
8. 2026Q3: accession `0000040533-26-000036`. Quote large, mid and total. Record the SEC acceptance timestamp of that 8-K exactly as SEC shows it (the filing index page shows "Accepted" with a date and time, which is US Eastern time; say where you read it). Also quote, from the same exhibit, the Aerospace segment's revenue and operating earnings for the quarter, and the period end date.

## Output

`docs/prepub/reviews/sources_deliveries.csv` with the header:

`quarter,accn,exhibit_url,filed_csv,filed_sec,fiscal_end_csv,period_end_quoted,large_csv,mid_csv,total_csv,large_exhibit,mid_exhibit,total_exhibit,first_reported_total,later_restated_total,match,note`

One row per quarter, 2016Q1 to 2026Q3 (43 rows). `match` is `verified` when large, mid, total, fiscal end and filing date all agree with the exhibit, otherwise `mismatch: <what>` or `unverified: <why>`. Use `lineterminator="\n"`. Begin the file with comment lines (starting `#`) that give the commands you ran.

In your final reply give: the count of verified, mismatch and unverified rows; every mismatch in one line each; the 2026Q3 acceptance timestamp; the 2026Q3 Aerospace revenue and operating earnings; and any restatement you found.
