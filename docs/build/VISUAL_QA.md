# Visual QA

One row per image or page and per criterion. `pass` or `open`, with a reason. Three fix rounds at most.

## Charts (Phase 6), read as PNGs after round 2

Round 1 found three faults, all fixed in round 2. The track record's legend sat inside the plot near the guidance pace's 2023Q4 and 2024Q4 peaks. The signed-error legend showed matplotlib's default blue swatches. The path chart hid its band on a single snapshot and clipped its last date label.

| Image | Criterion | Result | Reason |
|---|---|---|---|
| track_record.png | Units on axes | pass | y "Aircraft delivered per quarter", x "Fiscal quarter" |
| track_record.png | Source line | pass | bottom left, names SEC, FAA snapshot 2026-10-19, calls |
| track_record.png | Legend clear of data | pass | above the plot since round 2 |
| track_record.png | Nothing clipped | pass | full 2016Q1 to 2026Q2, y from 0 to 73 |
| track_record.png | Legible at print size | pass | 15 to 22 pt type on a 16 x 9 inch figure |
| track_record.png | Colours consistent | pass | the same STYLE map as every chart: ink for GD, accent for ratio, dashes for the rest |
| track_record.png | Figures match files | pass | ratio 2022Q1 40.7 and 2020Q2 18.5, guidance 2023Q4 62, as in results/holdout.csv |
| coverage.png | Units on axes | pass | "GD deliveries per registry event (ratio)" |
| coverage.png | Source line | pass | |
| coverage.png | Legend clear of data | pass | above the plot |
| coverage.png | Nothing clipped | pass | |
| coverage.png | Legible at print size | pass | |
| coverage.png | Colours consistent | pass | accent for the series, greys for reference lines |
| coverage.png | Figures match files | pass | 2020Q2 2.13 (32 / 15), mean 1.18, no flags, as in metrics.json |
| signed_errors.png | Units on axes | pass | "Estimate minus GD's count (aircraft)" |
| signed_errors.png | Source line | pass | |
| signed_errors.png | Legend clear of data | pass | above the plot; swatches fixed in round 2 |
| signed_errors.png | Nothing clipped | pass | symmetric y range around the largest miss |
| signed_errors.png | Legible at print size | pass | |
| signed_errors.png | Colours consistent | pass | design grey, holdout accent, band accent at 13% |
| signed_errors.png | Figures match files | pass | 2022Q1 +15.7, 2020Q2 -13.5, matching band_errors |
| nowcast_path.png | Units on axes | pass | "Estimated deliveries (aircraft)", "Snapshot date" |
| nowcast_path.png | Source line | pass | |
| nowcast_path.png | Legend clear of data | pass | above the plot |
| nowcast_path.png | Nothing clipped | pass | x runs to the release date plus two days since round 2 |
| nowcast_path.png | Legible at print size | pass | |
| nowcast_path.png | Colours consistent | pass | guidance pace keeps its dash-dot grey from the track record |
| nowcast_path.png | Figures match files | pass | 31.1, band 20.4 to 36.4, as in 2026Q3_latest.json |

## The note (Phase 6), read as page images after round 3

Round 1 (8 pages): a forced page break left half-empty pages; "Gd's" capitalisation; a negative change printed "$-593M"; the model page labelled Aerospace's drift as "2026Q3 estimate". Round 2: citation markers numbered per claim ran to 32 and repeated sources; the model page heading was stranded at the foot of page 6. Round 3: markers number sources (8), the source list is one list, the model page breaks between its tables, and the release folders sit in two columns. The note prints on 7 pages with room for the lock and score text.

| Page | Criterion | Result | Reason |
|---|---|---|---|
| 1 cover | Figures match files | pass | 5.5 against 6.9 (metrics.json), 31.1 with band 20.4 to 36.4 (2026Q3_build.json), $85M and $2.6B (estimates.json) |
| 1 cover | Disclaimer and disclosure | pass | the disclaimer line, then ~/.gdn_disclosure word for word |
| 1 to 2 | Nothing clipped | pass | product-cycle list flows to page 2 |
| 2 | Tables legible at print size | pass | 8.1 pt tables, tabular figures |
| 3 | Chart legible at print size | pass | track record at 3.3 in tall, legend above the plot |
| 3 | Figures match files | pass | by-year table matches holdout.csv; truncation table matches metrics.json |
| 4 | Chart and source line | pass | signed errors with its band; source line on the chart |
| 4 to 5 | Figures match files | pass | segment estimates match estimates.json; 2025Q3 actuals match segments.csv |
| 5 | Claims read right | pass | each sentence checked against its quote in claims.json |
| 6 | Risks apart from method limits | pass | two separate sections |
| 6 to 7 | Model page | pass | Summary and Segments as the workbook computes them |
| 7 | Sources | pass | 8 cited sources, every release folder, the FAA file and snapshot, the repository |
| all | Colours consistent | pass | the chart PNGs' palette; one accent for citation markers and links |

## The dashboard (Phase 7), read as Playwright screenshots after the Impeccable fixes

Headless Chrome cannot render narrower than its minimum window width, so the 390 px shots come from Playwright at a true 390 px viewport (`tools/shoot.py`).

| Image | Criterion | Result | Reason |
|---|---|---|---|
| desktop_light.png, desktop_dark.png | Live card | pass | status, big estimate, band, registrations by cabin, guidance pace, typical quarter, same quarter last year, release and lock dates |
| desktop_light.png | Path chart | pass | one snapshot shown with its band, guidance pace line, caption with the lock date |
| desktop_light.png | Track record and tooltips | pass | five estimates against GD's line; tooltip lists each value with its miss; design window shaded |
| desktop_light.png | Test panel | pass | sign tests in words, guidance coverage, band coverage, coverage drift, truncation table with a comparator |
| desktop_light.png | Bars | pass | twelve models by name with a total and scale in the caption |
| desktop_light.png | Tables | pass | estimates with the year-ago comparator; sensitivity with its change column |
| phone_light.png, phone_dark.png | No sideways scroll | pass | scrollWidth equals the viewport; tables scroll in their own regions |
| phone_dark_top.png | Legibility | pass | lead, live card and facts readable at 390 px in dark mode |
| all | Colours consistent | pass | one ink, one accent, warm greys, matching the PNG charts |
| all | Figures match files | pass | 5.5, 6.9, 4.6, 31.1, 20.4 to 36.4, 33.8 as in metrics.json, the latest file and data.json |
| output/charts/dashboard.png | README image | pass | 1280 x 900, light, the first screen |
