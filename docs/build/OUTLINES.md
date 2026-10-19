# Outlines

## The note (`report/note.html`, Phase 6)

Title "General Dynamics (GD): Gulfstream delivery tracker". Four to eight Letter pages. Prose comes only from templates over the results files and from `report/claims.json`, each claim cited `<sup data-claim="id">`. No rating, price target or consensus. The owner's first person.

1. **Cover.** Title; date (the basis prediction's snapshot date, so a rebuild is stable); author line "Rishabb Shankar, rshankar.dev". Three key points, in the headline rule's wording:
   - Holdout: the null sentence with ratio's MAE and guidance's MAE (`metrics.json` holdout.mae), since Holm rejects none and 22 quarters have an outlook.
   - Live: the 2026Q3 estimate and its past-miss band (`estimates.json` basis: build until the lock, then `predictions/2026Q3.json` with `_lock.json` published_at), beside GD's guidance pace for the quarter (`model.guidance_pace`), and the release date (`config/calendar.json`).
   - Dollars: Aerospace from the delivery estimate in $B one decimal (`estimates.json`), under §3.7's label.
   - "Student research project. Not investment advice. No rating or price target." Then `~/.gdn_disclosure` word for word.
2. **Business overview.** Exhibit: segment revenue mix (TTM share, %) and TTM margins (%) from `estimates.json` segments / `segments.csv`. One paragraph: four segments, TTM revenue and margin figures from files; what each segment does as claims (bo-*).
3. **Gulfstream's product cycle.** Every statement a claim (pc-*): models in production and entry into service (G500, G600, G650/G650ER, G700, G800, G280 as the mid-cabin jet built with IAI), and the next models announced.
4. **The tracker.** One paragraph on the registry count (template); §2's framing sentence; holdout table of the five models (MAE, MAPE, bias, MAE ex 2020) and the three tests (wins, losses, p, Holm, relative MAE, lag-1 autocorrelation) from `metrics.json`; the headline sentence; `track_record.png`; error analysis in brief (`results/error_analysis.md` quarters, by-year MAE); truncation table and coverage flags (none); the live quarter from the `estimates.json` basis and its band with §3.4's caution that the band comes from a finished file. `signed_errors.png` beside it.
5. **Backlog, book-to-bill and the 2026Q3 estimates.** Aerospace backlog $B and coverage years (`backlog_2026Q2.csv`, `estimates.json`); 2026Q2 book-to-bill 1.5 Aerospace, 1.4 defense and company (`book_to_bill.csv`, with the release's sentence as claim os-btb). Table by segment: 2025Q3 actual (`segments.csv`), 2026Q3 estimate (`estimates.json`), change $ and %. Aerospace twice: from the delivery estimate and from the drift baseline, under §3.7's label. Sensitivity table (`estimates.json` sensitivity). GD's own 2026 outlook (about 160 deliveries, Aerospace revenue around $13.8B, 14.7% margin) from the 2026-07-29 call: claims os-del, os-rev, os-margin.
6. **The defense segments.** Coverage years by segment (`estimates.json`). One paragraph on the owner's backlog study with its six pooled MAPEs (constants the gate pins) and a link to it; it tested five other primes, so applying it to GD is an assumption. Drift estimates per defense segment.
7. **What the street watches on the print.** Deliveries against the outlook (YTD from `gd_deliveries.csv`, outlook claim); Aerospace margin 2026Q2 and H1 against 14.7% (`segments.csv`, claim); book-to-bill (files); Marine Systems margins by quarter (`segments.csv`) and what GD said about them (claims os-marine-*).
8. **Risks.** Business risks, each a claim (risk-*), from GD's 10-K risk factors and calls: business-jet demand and the economy, supply chain, certification and production ramp of new models, order cancellations and customer defaults, US government budgets, fixed-price contracts, tariffs. Kept apart from the method's limits.
9. **Limitations of the method.** The seven from `DECISIONS.md` (export, processing, military, handover, coverage, used jet, band), in plain words, plus the airframe audit's disagreement rate once Phase 9 has it.
10. **Model page.** The workbook's Summary (design and holdout MAEs) and Segments (TTM, drift, margin, backlog, coverage, the derived rows) as one exhibit, values as the formulas compute them.
11. **Sources.** Every release by accession (`gd_deliveries.csv`, `segments.csv`), every call cited (from claims and guidance rows used), the FAA file and snapshot date, the repository URL.

Claims to source (ids are stable; text is the sentence the note prints, quote is verbatim, 40 words or fewer):
- Product cycle (pc-*): G700 FAA certification and first delivery; G800 certification and first deliveries; G500 and G600 entry into service; G650 and G650ER status; G280 as Gulfstream's mid-cabin aircraft and its IAI production; G300 and G400 announcements and timing.
- Outlook and street focus (os-*): 2026 deliveries about 160; Aerospace revenue around $13.8B; Aerospace margin 14.7%; any stated upside or risk to the delivery outlook (large-cabin upside, G280); 2026Q2 book-to-bill sentence; Marine Systems margin and what GD said drives it; Aerospace margin drivers GD named.
- Business overview (bo-*): what each segment does, from the 10-K.
- Risks (risk-*): as listed in section 8.

## README (Phase 8)

Owner's first person. Title "Gulfstream delivery tracker"; one sentence on what it is; `output/charts/dashboard.png` under a link to https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/ (live once published).
- `## Results` (written by `report.py` from `metrics.json`): §2's framing sentence; the headline sentence under §3.4's rule (null wording, guidance named); table by model of average miss (MAE), MAPE, bias, large and mid MAE, MAE without 2020; the three sign tests with Holm verdicts, relative MAEs and lag-1 autocorrelations, with the caution where one is positive (guidance 0.35, last 0.10); guidance coverage (22 sourced, 2021's four quarters fall back) and why guidance leads; band coverage with its Clopper–Pearson interval; design MAEs and the chosen definition (E1).
- `## Error analysis` (`report.py`, from `holdout.csv`, `metrics.json`, `results/error_analysis.md`): average miss by year for every model; by cabin; the coverage ratio's mean and the flag result; the truncation table; one sentence naming the quarters that drive the average (the five largest); the five largest misses table.
- `## Live record` (`report.py`, from `results/live/` and `config/calendar.json`): one line per live quarter, every lock kept, "timestamped GitHub release" until `public` is true.
- `## Method` (hand-written): event definitions E1 and E2, the bound, windows, the five models, the tests, the band, truncation, coverage drift; `### Exploratory` for anything tried after the fact.
- `## Data`: the FAA files (ACFTREF, MASTER, DEREG) and the backtest snapshot; the G280's `IAI LTD` listing; GD's counts on the ASC 606 delivered basis, with 2016 from the 2017 releases' restated columns; the call transcripts behind `data/guidance.csv`; segment figures from Exhibit 99.1.
- `## Limitations`: the seven from `DECISIONS.md`, plus the airframe audit's disagreement rate.
- `## Reproduce`: `make all` offline from a clone; `make daily` on my Mac each day until the quarter is scored, because the FAA's site refuses GitHub's runners; the workflow is a fallback; the gate.
- Author line linking https://rshankar.dev.

## LinkedIn post (Phase 8, `report.py`)

At most 1,500 characters. Before the first score: what I built; the held-out result under the headline rule; that the 2026Q3 lock is scored on 2026-10-30. After a score: "One locked quarter so far: off by N" first, never claiming skill from one quarter. Two or three lines on testing, the dashboard link and the note, one question, at most three hashtags.

## Interview notes (Phase 8), at most 900 words, first person

1. The 60-second account: the question; the registry count and its scaling; the held-out test against GD's guidance (5.5 against 6.9, not distinguishable; 4.6 for the same quarter last year); the lock as a timestamped GitHub release; first scoring on 2026-10-30; the note and dashboard.
2. How the registry count works, in plain words: Gulfstream jets in the FAA file, the first customer registration or export, within a year of first airworthiness; counted in GD's quarters; scaled by deliveries per registration over the last four quarters.
3. Six questions:
   - Why GD's guidance is the benchmark (it is what the street anchors on; 22 of 26 quarters had a numeric outlook).
   - What the held-out result shows and does not (§2's framing; the band held 18 of 26).
   - Why no price target (a delivery tracker, not a valuation; student project).
   - What the locked quarter showed, or when it is scored (2026-10-30; results/live).
   - What failed or surprised (from DECISIONS.md, without counts): early-year coverage fell below my sanity bound because the registry keeps only current certificates; the G280 sits under IAI, not Gulfstream; GitHub's runner reached the FAA when it was expected to be refused; two machines wrote different gzip bytes for the same data; the same quarter last year did better than the registry estimate.
   - What I would do next (score more locked quarters; an as-of registry archive; ADS-B to date handovers; per-model revenue).
Figures only from §4's quotable list; dates as YYYY-MM-DD.

## Resume bullets (Phase 8)

Two or three lines starting "- ", each at most 220 characters, the first in the prompt's form with the null result.
