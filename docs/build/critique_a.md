# Critique A: design review

Assessment A only (design-director review). Inputs: `site/index.html`, `site/style.css`, `site/app.js`, `site/data.json`, the four screenshots in `.build/shots/` (cropped to full resolution for reading), and the live page at http://127.0.0.1:8766/ checked at 1280 and 390 px. The detector was not run and no detector output was read, per the brief. Every fix below stays inside the rubric: no font or colour changes, and no change to the section order.

## Design specificity verdict

**Authored, not interchangeable.** The page could only belong to this project. The headline question, the "2026Q3 · PROVISIONAL" status line, the band of past misses drawn behind the estimate, the shaded "Quarters that set the rule" span on the track record, the lock-before-release promise, the jets on Gulfstream's own registration, and the "registrations cut early" table all come from this method. No other product could reuse them unchanged. The tokens come from the defense backlog dashboard by specification, so I do not count that against it.

Generic residue:
- **Chart.js default chrome.** The top-left legend uses 28x2 px line swatches for every series, including a 2 px line for the band, which is drawn as a filled rectangle. The tooltip box is the stock one. The pipeline bars are default bars.
- **Structural sameness below the fold.** Five sections repeat the same template: h2, grey sub, chart or table, then "The figures as a table". Only the live quarter has its own shape. The tiles are five equal cells, and nothing marks which figure is this project's.
- **Missed signature.** The lock (a timestamped GitHub release with a sha256) is what makes this project credible, and it is the thing a recruiter would remember. Today it shows only as small uppercase muted text and in Method item 5. In the provisional state the page never gives the lock date.

## Nielsen heuristic scores

| # | Heuristic | Score | Key issue |
|---|-----------|-------|-----------|
| 1 | Visibility of system status | 3 | Status, snapshot date and release date are all visible. The lock date is implied ("the evening before GD reports"), never stated. The path chart gives no sign that it fills in day by day. |
| 2 | Match system / real world | 2 | The banned words are avoided. But "one-sided sign test", "p = 0.423", "Holm's correction", "positively correlated (0.35)", "held out for the test", "trailing Aerospace revenue per delivery" and registry model strings ("GVIII-G800", "550", "GVI") are left for a recruiter to decode. |
| 3 | User control and freedom | n/a | Read-only page with no state to exit or undo. The disclosures and legend toggles are reversible. |
| 4 | Consistency and standards | 3 | One clear section system. Drift: "jets" in the lead but "deliveries" everywhere else. The live note says "the evening before GD reports", Method 5 says "the day before". Method names three comparators, the track record names "five estimates", and "Raw registry count" is never defined. |
| 5 | Error prevention | n/a | No inputs or destructive actions. |
| 6 | Recognition rather than recall | 2 | The reader has to hold the lead's comparator (6.9) in mind while reading tiles that show a lower one (4.6), and match six dash patterns from the legend to lines. Tables sit behind three separate toggles. |
| 7 | Flexibility and efficiency | 2 | Tables give an expert fast path, and Chart.js legend clicks toggle series but nothing says so. There are no section anchors. Six scroll regions add dead tab stops at 1280 px. |
| 8 | Aesthetic and minimalist design | 3 | Restrained and calm: thin rules, one accent, tabular figures. The waste: a 400 px chart holding one point, a six-series chart, and six paragraph bullets of test statistics. |
| 9 | Error recovery | 2 | `fail()` prints the raw error ("HTTP 404" / "Failed to fetch") and names the README without linking to it. If `data.path` is missing, `pathChart()` returns early and leaves a blank 400 px canvas that still announces itself as a chart. |
| 10 | Help and documentation | 3 | Each section has a plain sub caption. A five-line Method, a limitations link, the research note and the code are all one click away. "Raw registry count" and "band of past misses" are the gaps. |
| **Total** | | **20/32** (62.5%) | **Acceptable.** Heuristics 3 and 5 scored n/a. |

## Cognitive load

Checklist failures: **3 of 8, moderate.**

- **Chunking: fail.** The track record carries six series. "How it was tested" has six bullets of 35 to 55 words, each packing a win count, two averages, a p-value, a correction and an autocorrelation.
- **Visual hierarchy: fail below the fold.** Above the fold the hierarchy is strong: question, lead, 31.1. Below it every section has the same weight. The five tiles are equal and unranked, so the reader cannot tell which figure is this project's own.
- **Working memory: fail.** The lead compares 5.5 with GD's guidance pace (6.9). Two screens later the tiles show "Same quarter last year 4.6". To reconcile the two, the reader must recall the lead, find the answer in the second test bullet, and know that no gap passes the test.
- Passes: single focus, grouping, one thing at a time, progressive disclosure (tables are folded away), and minimal choices at the top (four header links).

Decision points with more than 4 visible options:
- the track record legend (6 series);
- the average-miss tiles (5);
- the "How it was tested" bullets (6, plus a table).

## Emotional journey

- **Opening:** curiosity. The question headline is good. The lead then hedges three times in 56 words ("not statistically distinguishable", "a registry copy ... that had time to fill in", "only the locked quarters test the estimate"). The first feeling is deflation before the reader has seen anything.
- **Peak:** the live quarter. A big **31.1** with its band on the next line, and the guidance pace and typical quarter in a ruled list beside it. Confident and fast at both widths.
- **Valley 1:** the estimate's path. Directly under the peak, a 400 px chart shows one dot, one grey bar, and ten empty days. It reads as broken.
- **Valley 2:** the track record. A tangle of six lines, then tiles where a rule of thumb (4.6) shows a lower miss than the registry estimate (5.5). The page never prepared the reader for that, so it reads as a gotcha rather than candour.
- **Flat middle:** the test statistics prose.
- **Valley 3:** "What it means for GD". The boldest number on the page is **-18.3%** on Aerospace, with **+12.3%** one row below and no sentence connecting them.
- **End:** Method plus the footer "Student research project. Not investment advice." Candid but flat. The end, which is what a reader remembers longest, never comes back to the lock, the project's strongest claim.

## Strengths

1. **The live quarter block shows comparators done right.** The estimate (3 rem, weight 600) is followed by "deliveries, estimated", then the band. The facts list sits beside it behind a 2 px accent rule. GD's guidance pace (33.8) and GD's typical quarter (about 33) appear right next to the estimate, as the rubric asks. It reads in five seconds at 1280 and at 390 px.
2. **The design itself carries the honesty, and the accessibility is real.**
   - Honest choices:
     - The band note says the band "is likely too narrow for a live quarter".
     - The rule-setting quarters are shaded.
     - The lowest tile correctly gets no accent, because no test allows "beat".
   - Accessibility:
     - Each canvas's `aria-label` is rewritten at runtime with the actual figures (for example "missed by 5.5 deliveries a quarter on average").
     - Every chart has a table.
     - Headings run h1 > h2 > h3 without skips.
     - A skip link is present.
     - Reduced motion sets Chart.js `animation: false`.
     - A change of colour scheme redraws the charts with the dark tokens.
3. **Token and layout discipline holds at both widths.** At 390 px, `scrollWidth` equals the viewport (390). Wide tables scroll inside their own regions. Tabular figures apply globally. Dark mode keeps the series order: ink for reported, accent for the estimate, warm greys for the baselines. There are no gradients, shadows, cards or icons.

## Priority issues

**[P1] The headline result is three sentences and names only the comparator the estimate beats. The simplest rule did better, and the first screen never says so.**
- *Why it matters:* The lead reads "Off by 5.5 ... against 6.9 for GD's own guidance pace." The tiles then show "Same quarter last year: 4.6", and `data.json` confirms seasonal 4.62 against the registry estimate's 5.52. A recruiter who finds that on their own will doubt the whole page. The rubric also asks for a one-sentence result, and the lead is three sentences and 56 words.
- *Fix:*
  - Rewrite `lead()` as one sentence that keeps guidance as the named comparator and adds the lowest baseline. For example: "Off by 5.5 deliveries a quarter on average, when GD delivers about 33: closer than GD's own guidance pace (6.9), not as close as the same quarter last year (4.6), and no gap passes the test."
  - Move the "test on past quarters ... registry copy of 2026-10-19 ... locked quarters" caveat to the first line of "How it was tested", or to the live-quarter note.
  - In `tiles()`, replace the repeated "deliveries a quarter" under each tile with a text comparator: "this project's estimate" under the registry tile, and "0.9 less than the registry estimate" / "1.4 more" under the others. The lowest figure is then stated in words, without the accent.
  - Optionally, add "Same quarter last year: 39 deliveries" to the live facts. That is the rule with the lowest average miss, and it disagrees with 31.1 by eight deliveries.

**[P1] "What it means for GD" puts an unexplained -18.3% in bold, and the sensitivity table rounds one step away.**
- *Why it matters:*
  - The first, bold row shows Aerospace at **$2.6B, -$593M, -18.3%**. The next row shows Aerospace at $3.6B, +12.3%. Nothing explains a $1.0B gap between two estimates of the same segment. It is the most alarming number on the page, and a recruiter may read it as a forecast that Gulfstream revenue collapses.
  - The sensitivity table steps by one delivery (about $85M) but prints in $0.1B, so the 30.1 and 31.1 rows both read "$2.6B". The step down from the central estimate disappears at that precision.
  - Its figures also have no comparator, which the rubric requires.
- *Fix:*
  - Add one sentence above the tables built from figures already in `data.json`: "The delivery estimate (31.1) is about 8 below the year-ago quarter's 39, at about $85M of Aerospace revenue a delivery; the growth row instead scales last year's Aerospace revenue by trailing growth."
  - Print the sensitivity column in $M (`usdM`, so "$2,556M" and "$2,641M").
  - Add a "Change from year-ago quarter" column so every row stands beside $3.2B.
  - Shorten row labels to "Aerospace, delivery estimate", "Aerospace, growth rule" and "Total, four segments". At 390 px they currently wrap to five lines.

**[P2] The estimate's path is a full-height chart with one point in it.**
- *Why it matters:* It sits directly under the page's peak. With one snapshot (2026-10-19), the 400 px canvas shows a dot, a grey bar and a dash-dot line across ten empty days to 2026-10-30. Without a caption saying it fills in daily, it looks unfinished. Early in every live quarter the chart will look like this.
- *Fix:*
  - In `pathChart()`, when there are fewer than 3 snapshots, drop the `tall` class (or set the box to about 220 px).
  - Draw a labelled vertical rule at the release date ("GD reports 30 Oct") and another at the lock date. A plugin like the existing `shade` will do this.
  - Set the sub caption from data: "One snapshot so far (19 Oct). A point posts each day until the estimate locks on the evening of 29 Oct."
  - Also guard the `return` at the top of `pathChart()` so that a missing path hides the chart box rather than leaving an empty `role="img"` canvas.

**[P2] The track record makes the reader separate six series by dash pattern alone, which fails at 390 px.**
- *Why it matters:*
  - The chart has one job: GD reported against the registry estimate. Four grey and blue dashed lines bury that comparison, especially in 2023 to 2026, where the guidance line spikes to 62.
  - At 390 px the legend wraps to three rows and the lines merge into one mass.
  - The colours are fixed, so the fix has to come from showing fewer series rather than recolouring them.
- *Fix:*
  - In `trackChart()`, set `hidden: true` on the raw, seasonal and last datasets. Keep GD reported, the registry estimate and GD's guidance pace (the lead's comparator) visible.
  - Add one line to the sub caption: "Select a name in the key to add the other estimates." Chart.js legend clicks already toggle series.
  - Nothing is lost: the five tiles directly below give all five averages, and the table gives every value.
  - Update the canvas `aria-label` to say which series are shown.

**[P2] The lower half has figures with no comparator, against the rubric.**
- *Why it matters:*
  - The rubric says every figure stands beside a comparator, a baseline or GD's typical quarterly count.
  - "On Gulfstream's own registration" shows 12 bars, 270 jets in all, with no total and no scale. A recruiter cannot tell whether 77 G800s is a lot.
  - The registrations-cut-early table (5.5 / 13.5 / 22.9 / 31.7) never says that 13.5 is already about double the guidance pace's 6.9.
- *Fix:*
  - Pipeline: put the total and a scale into `pipe-sub`: "270 jets, about eight quarters of deliveries at GD's typical 33."
  - Cut-early table: add a caption line or a column, "GD's guidance pace on the same quarters: 6.9".

## Persona red flags

**Alex (power user, reads the data fast):**
- The three charts' tables sit behind three separate "The figures as a table" toggles.
- There are no section anchors or in-page links, so Alex cannot jump from the header to the track record.
- The track table at 390 px is 457 px wide and scrolls sideways inside its region, and the Quarter column scrolls out of view with no sticky first column.
- Legend toggling works but nothing says so.
- At 1280 px all six `.scroll` regions carry `tabindex="0"` although none of them overflows. That makes 6 of the page's 15 tab stops do nothing.

**Sam (screen reader, keyboard, low vision):**
- The track and path canvas labels end "The table below lists every value" and "... every snapshot", but those tables are collapsed inside a `<details>`. The labels promise something Sam cannot reach without finding and opening a disclosure. The pipeline canvas label does not mention its table at all.
- The track record's baselines differ only by thin (1.6 px) dash patterns in close warm greys: [5,4], [2,3] and dash-dot. That is hard to tell apart at low vision. The tables mitigate it.
- When the `li.best` accent fires, "lowest" is conveyed by border colour alone. Add the word in the tile's text.
- If `data.path` is missing, an empty canvas still announces as a chart.
- Focus rings (2 px ink), heading order, the skip link and the live-updated canvas labels are all sound.

**Recruiter, two minutes:**
- The first screen asks them to parse a 56-word, three-sentence lead that ends in a methodology caveat.
- The second screen is a nearly empty chart.
- The third is a tangle of lines, then tiles where "Same quarter last year 4.6" shows a lower miss than the project's 5.5. This is the likely exit point, with the reader unsure whether the project worked.
- A reader who scrolls on hits "-18.3%" in bold with no explanation.
- They never see the lock date. "Locked on GitHub before GD reports, kept whether it hits or misses" is the line that would impress them, and it is in 13 px muted text and the last Method item.
- Fix within the rubric: set the provisional status line to "2026Q3 · Provisional · locks the evening of 29 Oct (ET)".

## Minor observations

**Copy and terminology**
- **"How it was tested" is written for a statistician.**
  - Lead each bullet with the plain verdict: "Closer than GD's guidance pace in 14 of 26 quarters, about a coin flip".
  - Move the sign test, p-value, Holm correction and correlation into a three-row table (Comparator | Closer in | Average miss | Passes the test?) or a closing clause.
  - Rename "Average miss on the quarters held out for the test" to "Average miss on the 26 test quarters, 2020 to 2026".
- **Wording drift.**
  - "jets" in the lead against "deliveries" everywhere else.
  - "the evening before" in the live note against "the day before" in Method 5.
  - Method item 4 names three comparators, while the chart and tiles show five estimates.
  - "Raw registry count" needs a clause: "the same count before scaling".
- **Pipeline bar labels are raw registry strings.** "GVIII-G800", "GULFSTREAM G280", "GV-SP (G550)", "GVI" and "550" are codes to a lay reader, and "550" is ambiguous. Map them to the names Gulfstream sells under (G800, G280, G550, G650), and keep the registry string in the table.
- **ISO dates everywhere** (2026-10-30). "30 Oct 2026" reads faster in the live facts and captions. Keep ISO in the tables.

**Typography and numbers**
- Negative figures use a hyphen-minus ("-$593M", "-18.3%"). Use U+2212 in `usdB`, `usdM` and `pct`. With tabular figures the minus then matches the plus in width.

**Charts**
- The path chart's legend draws the band as a 2 px line, because the global `boxHeight: 2` applies to all swatches. The shaded rectangle has no matching swatch.
- The guidance swatch's dash-dot pattern breaks up at 28 px wide in both charts.

**Layout**
- **At 390 px, the five tiles in a two-column grid leave "Last quarter 8.8" alone on its own row.** Either use three columns at that width (3 + 2), or let the registry tile span both columns as a lead row.
- **Table widths at 1280 px.**
  - The two-column cut-early table stretches to 720 px, which puts each value about 600 px from its label. Size two-column tables to their content.
  - "Year-ago quarter" and "Change, %" wrap to two lines.

**Error handling and accessibility**
- **Error message.**
  - `fail()` shows the raw error string to the reader.
  - Make "README on GitHub" a link to `#results`.
  - Put the technical error in a `<details>`.
- **Dead tab stops.** Give `.scroll` regions `tabindex="0"` only when `scrollWidth > clientWidth`, checked after render and on resize.
- **Inline styles.** `table()` sets `fontWeight`, `textAlign` and `borderBottom` on every row header. Those belong in `style.css` (`tbody th { ... }`) so both themes and print stay in one place.
