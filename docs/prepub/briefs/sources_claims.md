# Brief: source check of the note's claims and financial figures (P3.3)

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `sources_claims`. Output file: `docs/prepub/reviews/sources_claims.csv`. Scratch folder: `~/gdn-prepub/agents/sources_claims/`.

## Goal

Check every claim in `report/claims.json`, and every segment, revenue, backlog, book-to-bill and earnings figure in the research note and the workbook, against its source.

## Part 1: the claims registry

`report/claims.json` is a list of claims. Each has an `id`, the claim `text` the note prints, a `quote`, a `source_type`, a `url_or_accn`, and a hash of a cached copy (the cache itself is not in git). For each claim:

1. Open the source. For an SEC accession, build the URL from GD's CIK 40533 (`https://www.sec.gov/Archives/edgar/data/40533/<accession without dashes>/`, find the document in `index.json`) and fetch with `urllib` and the header from `~/.sec_ua` as `_common.md` says. For any other URL use WebFetch. If it does not load, find the same document elsewhere and record both URLs.
2. Is the `quote` in the source, word for word? Record `exact`, `close` or `absent`.
3. Does the quote support the claim `text` as the note words it? A claim can quote correctly and still say more than the quote does. Read each one as a hostile editor would.
4. Is the claim still true on 2026-11-11? Flag anything a later GD release or call has overtaken (for example a statement about what GD "will say" in coming quarters, an expected release date, a certification or delivery that has since happened).
5. Is the claim cited in `report/note.html` (search for `data-claim="<id>"`)? List claims that are in the registry but not cited, and any `data-claim` id in the note that is not in the registry.
6. Does any claim state a cause (why deliveries, revenue or margins moved)? The project's rule: no claim of cause unless a filing or a GD call states it, cited. Quote each causal sentence in the note (`report/note.html`) and say whether a cited source states that cause.

## Part 2: financial figures

The note (`report/note.html`) and the workbook (`output/gd_gulfstream_model.xlsx`, formulas only, no cached values: read the typed inputs with `openpyxl` from `.venv/bin/python`) carry segment revenue and operating earnings for 2024Q3 to 2026Q2, the 2026Q2 backlog by segment, book-to-bill ratios, and trailing-twelve-month sums. Their inputs are `data/processed/segments.csv`, `data/processed/backlog_2026Q2.csv` and `data/processed/book_to_bill.csv`.

1. For every row of `data/processed/segments.csv` (segment, quarter, revenue, operating earnings, accession): fetch that quarter's earnings release Exhibit 99.1 from SEC and compare the revenue and operating earnings as the exhibit prints them (in millions). Note whether a later release restated the figure in its prior-year column and which one the project uses.
2. Every row of `data/processed/backlog_2026Q2.csv` and `data/processed/book_to_bill.csv` against the 2026Q2 release (and the call, if the ratio was only stated there).
3. Every dollar figure, share, margin and growth rate the note prints (strip the HTML and list them): recompute each from the checked inputs and compare at the precision shown.
4. The note's estimate is for 2026Q3, and GD reported 2026Q3 on 2026-10-30 (accession `0000040533-26-000036`). From that release, quote the actual 2026Q3 revenue and operating earnings for each of the four segments. Compare with the note's estimates in `results/estimates.json` and say what the note should now tell the reader.

## Output

`docs/prepub/reviews/sources_claims.csv` with the header:

`kind,id_or_field,value_in_repo,source,source_url,value_or_quote_in_source,status,note`

`kind` is `claim` or `figure`. One row per claim and one row per figure (each segments.csv cell pair, each backlog row, each book-to-bill row, each printed note figure). `status` is `verified`, `verified elsewhere: <url>`, `mismatch: <what>`, `stale: <why>`, `overreach: <why>` or `unverified: <why>`. Use `lineterminator="\n"`. Begin the file with comment lines (starting `#`) that give how you fetched. Quote sources in under 25 words.

In your final reply give: the count by status, every mismatch, stale and overreach row in one line each, and the four segments' actual 2026Q3 revenue and operating earnings.
