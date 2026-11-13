# Round 4: rendered artifacts and accessibility (`rendered`)

Verdict: NO-GO. No drawn number is wrong, but three first-screen framings mislead: the README hero and link-card image leave out the only live quarter, the phone chart hides the baseline that won, and the dashboard's first screen calls my own pace "GD's guidance pace" with no qualifier in sight.

Counts: S1 0, S2 3, S3 10

Tree read: the cold copy at `~/gdn-prepub/round4/`. Scratch scripts: `~/gdn-prepub/agents/round4_rendered/`. Pixel reads use the project environment's Pillow; the PDF and workbook checks use the tools environment (`pypdf`, `openpyxl`, `formulas`). The dashboard was served from the cold `site/` on 127.0.0.1:8765 and driven in an emulated Chromium at 1280 x 900 and 375 x 812, light and dark.

## Answers

**1. Every number drawn, against its source.**

| Image | Drawn | Source file and field | Method | Match |
|---|---|---|---|---|
| `track_record.png` | GD reported, 42 quarters 2016Q1 to 2026Q2 | `site/data.json` `reported.total`, equal to `data/processed/gd_deliveries.csv` `total` (0 of 42 differ) | pixel read, `track_px.py` | yes, every point within 0.7 aircraft |
| `track_record.png` | Registry estimate (ratio), 38 quarters | `results/design.csv` and `results/holdout.csv`, model `ratio`, E1 | pixel read | yes, 36 of 38 within 0.7; 2019Q3 and 2020Q1 sit under the thicker GD line and could not be read |
| `track_record.png` | Raw count, pace, same quarter last year, last quarter | same CSVs, models `raw`, `guidance`, `seasonal`, `last` | spot-checked by eye at 6 points (raw 2025Q4 65, pace 2023Q4 62 and 2024Q4 61, pace 2020Q1 34.8, last 2020Q1 44, seasonal 2025Q1 24) | yes |
| `track_record.png` | shaded design window 2017Q1 to 2019Q4 | `docs/PREREGISTRATION.md` windows, as the README states them | by eye | yes |
| `signed_errors.png` | 38 bars, estimate minus GD's count | `results/*.csv`, `ratio` E1 `total` minus `actual` | pixel read, `err_px.py` | yes, all 38 within 0.1 |
| `signed_errors.png` | past-miss band | `results/metrics.json` `holdout.band.by_quarter` (2020Q1 band in error space -4.1 to 9.2) | by eye at 3 quarters | yes |
| `coverage.png` | 42 ratios, GD deliveries per registry event | `results/metrics.json` `holdout.coverage_ratio.by_quarter` | pixel read, `cov_px.py` | yes, max difference 0.074 |
| `coverage.png` | mean 1.18, mean plus two SD about 1.89 | same, `mean` 1.182 and `sd` 0.352 | by eye | yes |
| `nowcast_path.png` | 12 snapshots: 31.1 for 2026-10-19 to 10-26, 32.0 for 10-27 to 10-30 | `results/live/2026Q3_path.csv` `nowcast_total` | by eye at 12 points | yes |
| `nowcast_path.png` | bands 20.4 to 36.4, then 21.2 to 37.2; pace 33.8; GD 40; lock diamond 32.0 on 10-29; release line 10-30 | `2026Q3_latest.json` `band`; `2026Q3_score.json` `guidance_pace` 33.84 and `reported.total` 40; `predictions/2026Q3.json` `snapshot` 2026-10-29, `nowcast.total` 31.95 | by eye | yes |
| `dashboard.png` | 5.5, 33, 6.9, 4.6, 32.0, 21.2 to 37.2, 35 and 7 registrations, 33.8 (6.2), 39 (1), 40, 8.0 (20%), 12 snapshots | `site/data.json` live[0] and `metrics.holdout` | read against the live page text | numbers yes; one sentence stale (RENDERED-4) |
| `site/preview.png` | identical bytes to `track_record.png` | sha256 `7a50239d...` for both | `shasum` | same as row 1 |

`site/data.json` `backtest` equals the results CSVs in all 178 quarter-model pairs (`cmp_csv.py`: "compared 178 mismatches 0"). The chart input stamp `output/charts/inputs.sha256` checks OK for all 14 inputs.

**2. Current? Legends, units, dates.** Every chart is current with its stamped inputs, but the README hero (`track_record.png`, also `site/preview.png` and the note's Exhibit 4) ends at 2026Q2. It does not show the scored 2026Q3 lock (32.0) or GD's count (40) (RENDERED-1). Axis labels and units are right on all five PNGs: "Aircraft delivered per quarter", "Estimate minus GD's count (aircraft)", "GD deliveries per registry event (ratio)", "Estimated deliveries (aircraft)". Each source line names the right snapshot (2026-10-19 for the backtest; 2026-10-19 to 2026-10-30 for the path). No PNG legend calls the pace GD's: they say "Pace built from GD's outlook". The dashboard's chart legends and live card say "GD's guidance pace" (RENDERED-3). The four 2021 quarters drawn under the pace's name are the same-quarter-last-year fallback, with no mark (RENDERED-13).

**3. Open 2026Q4 shown as an estimate?** No chart, PDF page or dashboard screen shows it. `app.js` `current()` (line 109) picks the newest quarter with a lock or score, so the page shows 2026Q3. `charts.py` `featured_path` picks the same. The PDF and the post never mention 2026Q4. The served `site/data.json` does carry 2026Q4 under the key `nowcast` with a `band` (RENDERED-10).

**4. The PDFs.** `output/GD_research_note.pdf` and `site/GD_research_note.pdf` are the same file (sha256 `ba3441e2...` for both). The input stamp equals `sha256(report/note.html)` (`e0b89a40...`). The file has 8 Letter pages, and the full disclaimer is on every page (text extraction: once per page, twice on page 1). Its four link annotations go where their text says: the author's site and the repository on page 1, the defense backlog dashboard on page 5, the repository on page 8. All fonts are Type3 glyphs with `/CharProcs` and `/ToUnicode` on every page, so nothing is missing and text extracts. The PDF is tagged, and its two figures carry alt text. I saw no clipped text and no overflowing table on the eight rendered pages. Exhibit 3's "not rejected" wraps onto two lines, and page 8 is mostly blank. The sources' SEC, Fool and archive URLs are plain text, not links, and the PDF has no bookmarks (RENDERED-8).

**5. The workbook.** `formulas` recomputed 1,197 cells. All 513 formula cells evaluated, none to an error and none empty. The Summary sheet gives a held-out average miss of 5.523 for ratio, 6.192 raw, 4.615 same quarter last year, 8.808 last quarter and 6.917 guidance. The design figures are 5.473, 9.417, 5.0 and 3.833. These match the README table (5.5, 6.2, 4.6, 8.8, 6.9) and the note's Exhibits 2 and 11. The Live sheet gives 31.953, band 21.233 to 37.241, GD 40, miss 8.047, "outside", pace 33.84 and pace miss 6.16, matching `2026Q3_score.json`. `fullCalcOnLoad` is True, as About!A21 says.

**6. The dashboard.**
- First screen, honest? Yes at desktop. The first 900 px show the backtest lead and the live card: "2026Q3 · SCORED: MISSED BY 8.0, OUTSIDE THE BAND", 32.0, band 21.2 to 37.2, GD reported 40, miss 8.0 (20%). The live card cites the 2026-10-30 snapshot for a lock made from 2026-10-29 (RENDERED-11). "GD's guidance pace" is undefined on that screen (RENDERED-3).
- 375 px: works. `scrollWidth` 375 equals `clientWidth` 375, and no element overflows the page. Three tables wider than the screen (422, 457, 427 px) scroll inside focusable regions. The track chart hides three of its five estimates by default at that width, including the winning baseline (RENDERED-2).
- Console: no messages. Every request (page, CSS, font, Chart.js, `app.js`, `data.json`) returned 200.
- Accessibility: there is a skip link, and a 2 px solid ink focus ring is visible on links. Light-mode text contrast runs from 6.22:1 (muted on background) to 16.64:1, and dark mode from 6.31:1. Each canvas has `role="img"` and an `aria-label` built from the data, a table holds every value, and a `noscript` fallback is present. The legend toggles cannot be reached by keyboard (RENDERED-6), and the path chart's legend draws "Locked estimate" like "GD reported" (RENDERED-5).
- `og:image`: it points at `preview.png` on the Pages URL. The file exists in `site/` and matches the current `track_record.png`, but it is backtest-only (RENDERED-1). It is 1600 x 900, 16:9, not the 1.91:1 that link cards use (see Suspicions).

**7. A recruiter on a phone.** The LinkedIn post leads with the miss ("My first locked estimate ... missed: I said 32.0 for 2026Q3, General Dynamics reported 40"). The card under it is `preview.png`. Scaled to 360 px wide (`track_360.png`), its legend and source line can't be read, six lines tangle, and nothing marks 2026Q3. Tapping through to the dashboard, the first 812 px show the title, the backtest lead, the line that the same quarter last year missed by less (4.6), the links, then "SCORED: MISSED BY 8.0, OUTSIDE THE BAND" and "32.0 deliveries, locked estimate". GD's 40 sits just below the fold. Those words are the right thing. The card image is the wrong thing to sit under a post about the miss. The first chart they scroll to hides the same quarter last year (RENDERED-2).

## Findings

### RENDERED-1, S2. The README hero, the link-card image and the note's Exhibit 4 stop at 2026Q2 and leave out the only live quarter

Surface: `README.md:11`, `site/index.html:12-13` (og:image), `output/GD_research_note.pdf` page 3. Generated by `src/gdn/charts.py` `track_record` (line 88). `site/preview.png` is a byte copy made at `charts.py:250-256`.

Evidence:
```
$ shasum -a 256 site/preview.png output/charts/track_record.png
7a50239d...  site/preview.png
7a50239d...  output/charts/track_record.png
$ track_px.py (last rows)
2026Q1 rep 38 px 38.2 | ratio 45.4 px 45.5
2026Q2 rep 41 px 40.9 | ratio 44.8 px 44.9
```
`site/data.json` `quarters` has 42 entries, 2016Q1 to 2026Q2. The image's title says "GD's count against five estimates" and its alt text says the same. Nothing marks it as backtest-only. The post's first line is the 2026Q3 miss. The card under that post, the first image in the README and Exhibit 4 all show a chart in which the registry line hugs GD's line, and none shows the lock, GD's 40 or the band it fell outside.

Fix: in `track_record`, plot each scored lock after the held-out span: a diamond for the locked estimate, GD's count as an ink point, and its band as a bar, under a "Locked" label. If that can't be done, add "Backtest, 2016Q1 to 2026Q2" to the title and alt text. Then `make charts` (this refreshes `preview.png`), `make claims` and `make pdf`, since the note embeds the image.

### RENDERED-2, S2. On phones the track chart hides the baseline that won the backtest

Surface: dashboard "Track record" at widths up to 760 px. `site/app.js:221`, hand-written.

Evidence:
```
site/app.js:221  hidden: narrow.matches && (m === "raw" || m === "seasonal" || m === "last")
results/metrics.json holdout.mae: seasonal 4.615, ratio 5.523, guidance 6.917
```
At 375 x 812, light and dark, the chart opens with three lines: GD reported, Registry estimate and GD's guidance pace. The guidance pace spikes to 62 and 61. "Same quarter last year", which missed by least, appears in the key struck through. The words above the chart and the tiles below it state 4.6, so the figure is disclosed. The default picture is the comparison that flatters the registry estimate.

Fix: on narrow screens hide `raw` and `last` only. Or show `seasonal` in place of `guidance`, so the default view holds the baseline that won.

### RENDERED-3, S2. The dashboard's first screen and chart legends say "GD's guidance pace" with no sign it is my construction

Surface: dashboard lead, the live card fact "GD's guidance pace 33.8 deliveries (missed by 6.2)", and the legends of the path and track charts. `site/app.js:10`, `:14`, `:147`, `:300`, hand-written.

Evidence:
```
site/app.js:10   guidance: "GD's guidance pace",
src/gdn/charts.py:31  "guidance": "Pace built from GD's outlook",
docs/LINKEDIN_POST.md: "A pace I derived from GD's own full-year outlook missed by 6.2"
```
The PNGs and the post were reworded so the pace reads as mine. The dashboard was not. On a phone the definition ("my construction, not a figure GD publishes") first appears in "How it was tested", several screens below the live card. A reader of the card can take 33.8 for a number GD gave for the quarter. The README and the note use the same term, but each defines it within a few lines.

Fix: use the PNG wording in `NAME.guidance`, or add "(my construction from GD's full-year outlook)" to the lead and the live-card fact.

### RENDERED-4, S3. `output/charts/dashboard.png` is a stale manual screenshot

Surface: `output/charts/dashboard.png`. It is not made by `charts.py`: `CHARTS` at line 226 lists four files, and `tools/determinism.py:15` skips it. Nothing public embeds it. `docs/build/VISUAL_QA.md:76` calls it the "README image", but the README uses `track_record.png`.

Evidence: the screenshot's band note reads "so it is likely too narrow for a live quarter". The live `app.js:170` now writes "so it may not fit a live quarter". Its numbers match `data.json`.

Fix: regenerate it from the served page, or drop it from `output/charts/` and correct the VISUAL_QA line.

### RENDERED-5, S3. The path chart's key draws "Locked estimate" the same as "GD reported"

Surface: dashboard "The estimate's path", all widths and both themes. `site/app.js:184` sets `usePointStyle: false`, and `:304-309` defines both datasets in ink.

Evidence: in the 375 px screenshots, light and dark, the key shows "Locked estimate" and "GD reported" as identical solid bars. On the chart, one is a diamond and the other a line at 40.

Fix: set `usePointStyle: true` with `pointStyle: "rectRot"` for the lock dataset, or give the key per-dataset styles.

### RENDERED-6, S3. The legend toggles are the only way to show the hidden lines, and they work only by pointer

Surface: dashboard track chart. The sub-text (`site/index.html:65`) says "Select a name in the key to show or hide its line". Chart.js draws the key on the canvas, so it takes no keyboard focus and has no accessible name. With RENDERED-2, a keyboard or screen-reader user on a narrow screen cannot bring back three of the five lines. The table under "The figures as a table" holds every value, so no figure is lost.

Fix: render the key as HTML checkboxes wired to `chart.setDatasetVisibility`.

### RENDERED-7, S3. The PNGs' "Last quarter" line is under 3:1 contrast

Surface: `track_record.png`, `site/preview.png`, note Exhibit 4. `src/gdn/charts.py:20,28` (`GREY_L "#a39c90"`).

Evidence (`contrast.py`): "png GREY_L last on white 2.72". WCAG 1.4.11 asks 3:1 for graphical objects. The dashboard's light theme uses `#8f897f` at 3.15:1 and passes.

Fix: darken `GREY_L` to about `#8f897f`.

### RENDERED-8, S3. The PDF's source URLs are not clickable, and the PDF has no bookmarks

Surface: `output/GD_research_note.pdf` pages 7 and 8, generated by `src/gdn/note.py` (sources list near line 613-625).

Evidence:
```
$ pdfinfo.py: link annotations
link p1 ... (author's site)   link p1 ... (repository)
link p5 ... (defense backlog dashboard)   link p8 ... (repository)
$ pypdf: '/Outlines' in root -> False
```
Sources 1 to 9 print about 40 SEC URLs, plus a Fool and an archive URL, as plain text. A reader can't click through to check a figure.

Fix: wrap each source URL in `<a>` in `note.py`, and print with a document outline.

### RENDERED-9, S3. The sensitivity tables round away their own step

Surface: note Exhibit 9 (page 5) and the dashboard's "Made before the release" table. `src/gdn/note.py:534-536` and `site/app.js:440-444`.

Evidence: the computed workbook gives 2,455.9 and 2,540.7 ($M) for 29 and 30 deliveries, and 2,964.8 and 3,049.6 for 35 and 36. Both PDF and page print "$2.5B" twice and "$3.0B" twice. The Deliveries column prints 28.0 to 36.0 for values of 27.953 to 35.953.

Fix: print Aerospace revenue in $M, as the dashboard's change column already does.

### RENDERED-10, S3. The served `data.json` holds 2026Q4's part count under the key `nowcast`, with a band

Surface: `site/data.json` `live[1]`, generated by `src/gdn/site_data.py` from `results/live/2026Q4_latest.json` (written by `src/gdn/live.py:142`). Nothing renders it.

Evidence:
```
2026Q4 latest: snapshot 2026-11-12, events large 17 mid 2,
  nowcast total 14.307..., band [3.587..., 21.108...], guidance_pace 41.0
```
`README.md:107` says this file "holds that part count and is not an estimate". The JSON key and its band say otherwise to anyone who opens the public data file.

Fix: write open quarters with `"partial": true` and leave out `band`, or keep them out of `data.json` until the window closes.

### RENDERED-11, S3. The live card cites a later snapshot than the one the lock used

Surface: dashboard live card, "Registrations in the quarter ... (snapshot 2026-10-30)". `site/app.js:142-144` takes `L.latest`, not `L.locked`.

Evidence: `data.json` `live[0].locked.snapshot` is 2026-10-29 and `latest.snapshot` is 2026-10-30. Both count 35 large and 7 mid, so no figure differs. The card's headline figure is the 10-29 lock.

Fix: when `L.lock` exists, cite `L.locked.events` and `L.locked.snapshot`.

### RENDERED-12, S3. The dashboard treats a 0.10 autocorrelation as weakening the test, where the README draws the line at 0.35

Surface: "How it was tested", against last quarter. `site/app.js:377` adds the warning for any autocorrelation above 0.

Evidence: the page reads "positively correlated (0.10), which makes the sign test less reliable". `README.md:47` says only the one against GD's guidance pace is more than one standard error (about 0.20) above zero.

Fix: add the warning only when the autocorrelation exceeds `1/sqrt(n)`, or quote the README sentence.

### RENDERED-13, S3. The pace line in 2021 is the same-quarter-last-year fallback, drawn under the pace's name

Surface: `track_record.png`, `site/preview.png`, note Exhibit 4 and the dashboard track chart.

Evidence: `data.json` `backtest.guidance` for 2021Q1 to 2021Q4 is 23, 32, 32, 40, equal to `backtest.seasonal` for those quarters. The legend says "Pace built from GD's outlook" (PNG) or "GD's guidance pace" (dashboard), with no mark on those four points. The text in the README, the note and the dashboard discloses the fallback.

Fix: break the pace line across 2021, or draw those four points hollow and footnote them.

## Improvements that would raise the project's standing

1. Make `preview.png` a 1200 x 630 card built for the link preview: the 2026Q3 lock, its band and GD's 40 large, with the backtest as a small inset. It is the first image most readers will see.
2. Add a test that reads the drawn values back from the PNGs (the `track_px.py`, `err_px.py` and `cov_px.py` approach in my scratch folder) and compares them with `results/`, so a chart can't drift from its source unnoticed.
3. Show scored locks as their own segment in the dashboard's track chart, so the backtest and the live record sit on one axis.
4. Give the PDF a bookmark outline and clickable sources, so a reader can go from any figure to its filing in one tap.
5. Render chart keys as HTML controls, which fixes keyboard access and lets the phone view label hidden series plainly.

## Checked and clean

- Both PDFs are identical. The input stamp matches. All 8 pages carry the disclaimer. The 4 link annotations are correct. The fonts are Type3 with ToUnicode, so none are missing. The PDF is tagged, and its 2 figures have alt text.
- The note's "Marine Systems backlog of $146.9B" (page 5) matches Exhibit H of accession 0000040533-26-000036, Marine Systems total backlog 146,865 ($M), fetched from sec.gov. Its Aerospace 2026Q2 backlog, 23,977, matches the workbook's `Segments!N2`.
- Note page 3: "On those 22 quarters GD's guidance pace missed by 7.4 ... against 5.3 ... and 4.6" recomputes as 7.357, 5.2503 and 4.636.
- Note Exhibit 8 totals: 13.193 estimated against 14.566 reported gives -1,373 ($M) and -9.4%, from the workbook and `reported_segments`.
- Workbook: 513 formula cells, 0 errors. Summary and Live match the README, the note and `2026Q3_score.json`. Recalculation on load is set.
- `site/data.json` backtest matches `results/*.csv` (178 of 178). The deliveries match `gd_deliveries.csv` (42 of 42).
- `signed_errors.png` (38 bars) and `coverage.png` (42 points) match their sources by pixel read.
- Dashboard: no console messages, all requests 200, no page overflow at 375 px, skip link, visible focus ring, text contrast at least 6.2:1 in both themes, canvas labels drawn from the data, noscript fallback. Dark mode renders the path and track charts legibly at 375 px.
- Typical quarter "about 33": the mean of GD's counts for 2020Q1 to 2026Q2 is 850 / 26 = 32.7.
- Pipeline "258 in all" equals the sum of `data.json` `pipeline`.
- No public surface shows 2026Q4 as an estimate.

## Suspicions, not proven

- **Link-card crop.** `preview.png` is 16:9. If LinkedIn center-crops it to 1.91:1, my simulated crop (rows 31 to 868, `track_card.png`) cuts the bottom source line, the one that credits SEC, FAA and the calls. I have not seen how LinkedIn crops this image. LinkedIn's Post Inspector on the Pages URL, once public, would settle it.
- **Pipeline "Other".** `app.js:335` maps the registry model name "550" to "Other", while a "GV-SP (G550)" bucket exists. That one jet may be a G550 shown as Other. Reading the "550" row's make and model in the 2026-11-12 snapshot would settle it.

## Could not check, and refused commands

- I did not fetch the Pages URL, the author's site or the defense backlog dashboard. Each URL carries the owner's account name or name, which the hard limits keep out of outside requests. The repository and Pages URLs return 404 while private in any case.
- Workbook rendering in Excel, Numbers or a phone previewer was not checked. I recomputed with `formulas` only. About!A21 warns that non-calculating previewers show formula cells blank, so a phone previewer may show an empty Summary sheet.
- The dashboard was checked in emulated Chromium only, not Safari on iOS or a real phone.
- The four dashed series in `track_record.png` and the 12 points in `nowcast_path.png` were checked by eye, not by pixel read.
- No command was refused. My first browser navigation failed before the local server was ready, and a retry worked. The local server on 127.0.0.1:8765 was a background task of this session, and it is now stopped.
