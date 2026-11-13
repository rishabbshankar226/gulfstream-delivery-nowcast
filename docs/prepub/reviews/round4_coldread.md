# Round 4: coldread

Verdict: GO. Every figure on the first screens matches the result files and GD's SEC filing, and nothing I found is a blocking defect; one S2 framing fix on the README's first screen should still go in before the post.

Counts: S1 0, S2 1, S3 6

Tree read: `~/gdn-prepub/round4b/` (plain copy, no git). Scratch: `~/gdn-prepub/agents/round4_coldread/`.

## Answers

**1. Wrong figures, or two surfaces that disagree?** None found. I checked every figure on the post, README to the end of `## Results`, the dashboard's first screen, note pages 1 to 3 and 6 to 7, and the workbook Summary and Live sheets against the result files by command:

- Live: `results/live/2026Q3_score.json` gives nowcast 31.953, reported 40 (35 large, 5 mid), `ae_total` 8.047, `ape_pct` 20.1, `inside_band` false, `guidance_pace` 33.84, `guidance_ae` 6.16. `predictions/2026Q3.json` gives band [21.233, 37.241], events 35 large and 7 mid (raw 42). These match 32.0, 21.2 to 37.2, 40, 8.0 (20%), 33.8 and 6.2, and the raw count's miss of 2.
- GD's count: the 2026Q3 earnings release in accession 0000040533-26-000036 (fetched from sec.gov by `urllib`) reads "Large-cabin aircraft 35 33 ... Mid-cabin aircraft 5 6 ... Total 40 39", and Aerospace revenue "3,536 3,234". So 40, the year-ago 39, $3.5B and $3.2B are right.
- Lock: `gh release view lock-2026Q3` shows author github-actions[bot], published 2026-10-29T05:51:24Z (01:51 ET), notes `sha256 3c4cdbd0...6f23`. `shasum -a 256 predictions/2026Q3.json` prints the same hash.
- Backtest: `results/metrics.json` holdout MAE ratio 5.523, raw 6.192, guidance 6.917, seasonal 4.615, last 8.808; band hits 18 of 26, 69.2%, CP95 48.2 to 85.7; sign tests 14/12 p 0.423, 11/15 p 0.837, 16/10 p 0.163, all Holm non-reject. Every cell of the README tables and note Exhibits 2 and 3 rounds from these.
- Derived figures I recomputed from `results/holdout.csv` and `data/`: 22 sourced quarters, ratio 5.2503, guidance 7.357, seasonal 4.636 (note's 5.3, 7.4, 4.6); pace 33.8400 from 160 less 79 year to date, left 81, even split 40.5, Q3 and Q4 shares 94 and 131 over 2023 to 2025; the five largest misses (2022Q1 40.7 v 25, 2020Q2 18.5 v 32, 2025Q4 58.4 v 45, 2021Q2 31.7 v 21, 2021Q1 38.1 v 28); the guidance pace closer in 2025Q3, 2025Q4, 2026Q1, 2026Q2 and the lock (the note's "last five quarters"); 5 of the 42 window events at least three years old in `data/snapshots/daily/2026-10-29.serials.csv.gz`; 246 of 1,251 counted events (19.7%) in `serials.csv`; coverage 0.692, 0.691, 0.719 against a 1.182 mean; 163/215 = 0.7581 and 40/42 = 0.9524 (interview notes' 0.76 and 0.95); E1 and E2 differ only in 2019Q4 (35 v 36).
- Sensitivity rows in README line 49 (6.7 and 13 of 26, 6.0 and 12 of 26, 5.7 and 11 of 26) match `results/exploratory/sensitivity.md`; the 2023Q3 quote matches `data/quarter_plans.csv` line 7 and the pace 43.07 in `holdout.csv`.
- Cross-surface: `site/data.json` metrics equal `results/metrics.json`; `live[0].locked` equals `predictions/2026Q3.json`; `live[0].score` equals the score file (Python equality, all True). `site/GD_research_note.pdf` and `output/GD_research_note.pdf` have the same sha256.
- Workbook recomputed with `formulas`: Summary C2 to C6 = 5.5234, 6.1923, 4.6154, 8.8077, 6.9173; B2 to B5 = 5.4725, 9.4167, 5.0, 3.8333. Live B11 31.9532, B14 21.2334, B15 37.2411, B17 8.0468, B18 0.2012, B19 "outside", B21 6.16.

**2. False, stale, contradictory or misleading sentences?** Nothing false or stale on 2026-11-12. On who built the pace, the post ("My pace", "the pace: mine"), the dashboard ("Pace I built from GD's outlook") and the note's first key point ("my construction") are clear. The README's generated live summary is not: lines 6 and 8 say "GD's guidance pace" with no owner, and the definition comes at line 23, below the chart (COLDREAD-1, S2). On the band, every surface says the same thing: nominal 80%, held 18 of 26. Two smaller wording issues: COLDREAD-5 and COLDREAD-7.

**3. First chart.** `output/charts/track_record.png` draws the lock correctly. Pixel check on the 1600 by 900 image (y = 0 at pixel 765, 70 at 194): diamond at about 32.0, caps at about 21.2 and 37.1, GD's 2026Q3 vertex at 40. Nothing is clipped: the right-hand diamond and the source line (ends near x 1575) sit inside the frame. GD's 40 is shown only as the last vertex of the black line, with no marker or label (COLDREAD-3). The source line names only the 2026-10-19 snapshot, but the lock came from the 2026-10-29 snapshot (COLDREAD-2). `site/preview.png` is the same image.

**4. Post length and opening.** `len()` gives 1,282 characters, all ASCII, with no en or em dashes. That is under 1,300. The first 140 characters end "...(GD) reported 40.\nMy tracker scales FAA r". The first 210 end "...jets GD reports each q". Both carry the live result in full: locked 32.0 for 2026Q3, GD reported 40, a miss.

**5. Unsupported claims or trading signals?** None found. "Not statistically distinguishable" matches p = 0.423 with no Holm rejection. "Rules set minutes before scoring" matches README line 119 ("two minutes before the held-out scores, in the same build session"); I cannot check the commit order in a tree with no git. The revenue figures are labelled mechanical; the note says "No rating or price target"; the README and note say the author holds no GD position. No buy, sell or price language appears on any first screen.

## Findings

### COLDREAD-1 (S2): the README's first screen calls my constructed pace "GD's guidance pace", unlike the post and the dashboard

- Surface: `README.md:6` and `README.md:8`, inside the `live-summary` block. Generated by `src/gdn/report.py:125` (`f" GD's guidance pace missed by {pace[2]} ..."`) and `src/gdn/report.py:134` (`f"quarter on average, GD's guidance pace by ..."`).
- Evidence: `sed -n '6p;8p;23p' README.md`. Line 6: "GD's guidance pace missed by 6.2 and the same quarter last year (39) by 1." Line 8: "GD's guidance pace by 6.9". The definition ("my construction, not a figure GD publishes") first appears at line 23, after the chart. Line 3 says only "a pace built from GD's own guidance". By contrast, `docs/LINKEDIN_POST.md` says "My pace from GD's full-year outlook missed by 6.2", and the dashboard's live card says "Pace I built from GD's outlook: 33.8 deliveries (missed by 6.2)".
- Why it misleads: GD never guided a 2026Q3 figure. `data/guidance.csv` holds 160 for the year (2026-01-28 and 2026-07-29) and, on 2026-04-29, "the third and fourth will be our highest". With 79 delivered in the first half, that leaves 81, and an even split says 40.5. A reader of line 6 who takes "GD's guidance pace" as GD's own number concludes that GD's guidance missed by 6.2. README line 105 discloses the 40.5, but not on the first screen.
- Fix (generator, then rebuild): change both f-strings to "my pace from GD's outlook". The preregistered headline sentence fixes only "the registry count", with `<baseline>` left to fill in (`docs/PREREGISTRATION.md:52`), so this wording is allowed. Optionally add the even-split 40.5 to line 6.

### COLDREAD-2 (S3): the chart's source line names only the backtest snapshot, but the chart also draws the lock

- Surface: `output/charts/track_record.png` footer, also note Exhibit 4 and `site/preview.png`. Generated: `src/gdn/charts.py:33` (`SOURCE`) and `track_record()` at `charts.py:145`, which passes the backtest `snap`.
- Evidence: the footer reads "FAA aircraft registry snapshot 2026-10-19". `predictions/2026Q3.json` has `"snapshot": "2026-10-29"`.
- Fix: when `locked_points()` is not empty, add "; lock from the 2026-10-29 snapshot".

### COLDREAD-3 (S3): GD's 2026Q3 count is not marked on the first chart

- Surface: `output/charts/track_record.png`, the right-hand "Locked" column. Generated: `src/gdn/charts.py:125-133`.
- Evidence: a crop of x 1300 to 1600 shows the black "GD reported" line ending at 40 directly above the lock's upper cap (about 37.2), with no marker or number. At full size the gap is about 23 px of 900, and less on GitHub's scaled-down render.
- Fix: draw GD's count for each scored lock as a black point with a small "40" label beside the diamond.

### COLDREAD-4 (S3): the dashboard's path-chart legend shows "Locked estimate" and "GD reported" with the same swatch

- Surface: the dashboard's "The estimate's path" panel, below the first screen. Hand-written: `site/app.js:186` (`usePointStyle: false`), with datasets at `app.js:306-311`.
- Evidence: a zoomed screenshot at 1366 px shows both entries as identical thick black lines, but the lock is drawn as a diamond (`pointStyle: "rectRot"`).
- Fix: set `usePointStyle: true` for the lock dataset's legend item, or give the lock a distinct legend label.

### COLDREAD-5 (S3): the dashboard calls an autocorrelation of 0.10 a problem; the README says it is within one standard error

- Surface: the dashboard's "How it was tested", last-quarter item. Hand-written: `site/app.js:379` adds the warning for any `ac > 0`.
- Evidence: the dashboard reads "positively correlated (0.10), which makes the sign test less reliable". `README.md:47` says one standard error is "about 0.20, so only the one against GD's guidance pace is more than one standard error above zero".
- Fix: apply the warning only above 1/sqrt(n), or carry the README's caveat.

### COLDREAD-6 (S3): note Exhibit 11 says it shows the workbook's Summary but drops its guidance row

- Surface: `output/GD_research_note.pdf` page 7, Exhibit 11. Generated: `src/gdn/note.py:593-596`, `srow`, which has ratio, raw, same quarter last year and last quarter.
- Evidence: the Summary sheet has `A6 'MAE guidance'`, `C6 =AVERAGE(Quarters!T18:T43)` = 6.917. The exhibit has no guidance row, so the baseline named first in the headline is missing from the page that claims to mirror the sheet.
- Fix: add "Average miss, guidance pace", design blank and held-out 6.9.

### COLDREAD-7 (S3): resume bullet 1 says "a guidance pace" without saying whose

- Surface: `docs/RESUME_BULLETS.md:1`, hand-written. The line is 218 characters.
- Evidence: "missed by 5.5 jets a quarter vs 6.9 for a guidance pace, 4.6 for the year-ago quarter". Read cold, this could mean GD's own guidance.
- Fix: "vs 6.9 for my guidance pace" brings it to 219 characters and stays inside the 220 rule.

## Improvements that would raise the project's standing

1. In the post and the README live summary, give the even split of GD's remaining outlook (40.5) next to the 33.8 pace. It shows the reader that the guidance baseline's 2026Q3 miss came from my spreading rule, not from GD.
2. In the dashboard live card, add "Raw registry count: 42 (missed by 2)", which `predictions/2026Q3.json` supports, beside the note's caveat that 5 of the 42 are older airframes. A recruiter will ask why the scaled estimate fell below the raw count, and the answer (0.76 trailing, 0.95 in the quarter) is already in the interview notes.
3. Put GD's 40 in the dashboard's large-type line (for example "32.0 locked, GD reported 40"). At 375 px the first screen shows "missed by 8.0" but not GD's count.
4. For future locks, consider GitHub's immutable releases so the notes carrying the sha256 cannot be edited. This does not touch the 2026Q3 lock.
5. Give the chart's lock column a one-line caption such as "2026Q3: locked 32.0, GD 40". That makes the README's first image stand alone when shared as a link card.

## Checked and clean

- Post: 1,282 characters, live result in the first 116 characters, all figures right, ownership of the pace stated, the private-repository caveat present, the registry-lag caveat present, "not investment advice" present.
- README lines 1 to 54: every figure, both tables, the sensitivity sentences, the 22-of-26 disclosure, the band coverage and interval, and the design-window figures.
- Dashboard first screen at 1366 px (light) and at 375 px (light), plus the default dark render: no horizontal overflow (`scrollWidth` 375 = `clientWidth`), the error banner hidden, no console errors, the 01:51 ET conversion right, "Quarter window 2026-07-06 to 2026-10-04" consistent with GD's fiscal ends, "GD's typical quarter about 33" = 32.69 over 2020Q1 to 2026Q2.
- Note pages 1 to 3: key points, callout, Exhibits 1 to 4 and "Where it missed". Pages 6 to 7: Limitations figures (246 of 1,251, mid-cabin within a few jets since 2022: 2022 24 v 25, 2023 22 v 20, 2024 18 v 22, 2025 22 v 25).
- Workbook Summary and Live sheets recompute to the published figures.
- Interview notes: the 60-second figures, 12.5 and 3.5, 4.4 and 6.4, 0.76 and 0.95, "count has not changed" (42 in every daily file from 2026-10-29 to 2026-11-12), and the as-of study claim against `results/exploratory/asof.md`.
- GD's reported 2026Q3 count and Aerospace revenue against the SEC filing.

## Suspicions, not proven

- `gh release view` shows `immutable: false` for `lock-2026Q3`. The notes' sha256 matches the file today. Whether the notes or the tag target were ever changed after 2026-10-29 needs the release's edit history or the tag object, which a cold tree cannot show.
- LinkedIn crops link-card images to about 1.91:1. `site/preview.png` is 1600 by 900, so the source line at the bottom may be cut on the card. Settled by previewing the URL in LinkedIn's Post Inspector after the site is public.
- The post uses two names for one pace ("My pace from GD's full-year outlook", then "GD's guidance pace"). The parenthetical "the pace: mine" covers it, so I do not count it as a finding.

## Could not check, and refused commands

- The commit order behind "rules set minutes before scoring" and "two minutes before": my tree has no git.
- The audit's "10 of 30 airframes" and the transcript quotes beyond those cross-checked against `data/`: no time inside the 35-minute budget.
- The Risks page's GD attributions (the 2025 10-K's 30 basis points of tariff effect; the 2026Q2 10-Q's Israel-based supplier delays and IEEPA ruling): each carries a source number, but I spent my SEC fetch on the 2026Q3 release and did not open those filings.
- No command was refused. I ran no forbidden command. The local `http.server` on port 8767 was started as the brief directs and stopped with the harness task tool.
