# Statistician review (P4.3)

Reviewer: `statistician`. Date: 2026-11-11. Branch `prepub-audit` (`7b3ba7e` when I started, `9945499` when I finished; no file I cite changed in between).

## Verdict

**NO-GO as the repository stands today; GO once STAT-1 and the framing fixes in STAT-2, STAT-5 and STAT-6 are made.** No statistic needs recomputing. Every figure I recomputed reproduces at the precision shown, the tests are computed correctly, and the headline wording does not overclaim. What blocks is text: the owner material still describes the lock as a future event, and three framings would not survive a referee's first read.

Findings: **S1: 1. S2: 9. S3: 6.**

## How I worked

I rebuilt the holdout from `data/processed/gd_deliveries.csv`, `data/processed/registry_quarterly.csv`, `data/guidance.csv` and `data/processed/serials.csv` with my own code, importing nothing from `src/gdn`. Scripts are in `~/gdn-prepub/agents/statistician/` and run with `.venv/bin/python <script>`:

| Script | What it does |
|---|---|
| `core.py` | Loaders, the five models, exact binomial, incomplete beta, Student t, Clopper-Pearson by beta quantiles |
| `s1_headline.py` | Headline table, sign tests, Holm, design figures, by-year table, guidance subsets |
| `s2_tests.py` | Diebold-Mariano with the Harvey-Leybourne-Newbold correction, Newey-West, sign-flip permutation, circular block bootstrap, Wilcoxon, runs test |
| `s3_band_e2.py` | Past-miss band, coverage interval, live band for 2026Q3, the holdout under E2 |
| `s4_trunc_drift.py` | Truncation test, a like-for-like variant, the daily snapshots for 2026Q3, the as-of captures, deliveries per event |
| `s5_misc.py`, `s6_recent.py`, `s7_site.py`, `s8_q4band.py` | Trend fit, sign-test power, lock hash, the n = 30 nearest-rank claim, recent quarters, dashboard data, the 2026Q4 working file |

Every number below was printed by one of these scripts or by a command quoted beside it.

## What reproduces

Nothing failed to reproduce. Checked at the precision shown:

- README Results table, all five models and six columns: maximum absolute difference from `results/metrics.json` is 0.00e+00 (`s1_headline.py`). All 130 rows of `results/holdout.csv` match my totals and errors exactly.
- Sign tests: 14/12 p 0.4225, 11/15 p 0.8365, 16/10 p 0.1635. Relative miss 0.7985, 1.1967, 0.6271. Lag-1 autocorrelation 0.3531, -0.1915, 0.0952. Holm rejects none.
- Design window: ratio 5.472548 under E1, 5.580786 under E2, seasonal 5.0000, last 3.8333.
- Guidance: 22 sourced quarters, pace MAE 7.3568 on them; the note's 5.3 (5.2503) and 4.6 (4.6364) for ratio and seasonal on the same 22.
- Band: 18 of 26, 69.23%, Clopper-Pearson 48.210% to 85.674%.
- Truncation: 5.5234, 13.4682, 22.9287, 31.6719.
- Deliveries per event: mean 1.1824, sd 0.3516, no flag; last three quarters 0.692, 0.691, 0.719.
- By-year table and the five largest misses: all cells match.
- README Limitations: 0.52 in 2016 (63/121), 0.80 in 2019 (117/147), mid cabin 0.37 and 0.47 in 2016 and 2017; mid-cabin yearly counts since 2022 are 25/24, 20/22, 22/18, 25/22, 15/13 (registry/GD).
- As-of table: all four rows, and 206 against 203, 146 against 63, and the two extra own events in 2025Q3 (40 against 38).
- Live: nowcast 31.953209 from the file's own counts; band [21.233381, 37.241087] from the 38 errors at positions 4 and 35; miss 8.0468; guidance pace (160 - 79) x w3/(w3 + w4) = 33.8400.
- Lock: sha256 of `predictions/2026Q3.json`, of the same file at commit `a44e5aca37`, of `results/live/2026Q3_lock.json` and of the release body (`gh release view lock-2026Q3`) all read `3c4cdbd0...406f23`; `publishedAt` 2026-10-29T05:51:24Z.
- `site/data.json`: its `metrics` block equals `results/metrics.json`; 178 backtest values match mine with maximum difference 0.00e+00.

Not recomputed by me: GD's delivery counts against the filings, the guidance quotes against the transcripts, the dollar figures, the charts as images, the airframe audit.

---

## The ten questions

### 1. Sign tests on 26 autocorrelated quarters

**Is a one-sided exact sign test the right test?** It is a valid and conservative choice, and it was fixed in advance. It has three limits a referee would name.

1. It tests how often the estimate is closer, while the headline sentence is about the average miss. For guidance pace the two views happen to agree. For last quarter they do not (below).
2. It has little power at n = 26. Rejection needs 18 wins at a raw 0.05 and 19 under Holm's first step. If the estimate were truly closer in 60% of quarters, the test would reject 12% of the time under Holm; at 70%, 46% (`s5_misc.py`). "Does not reject" was the likely outcome for anything short of a three-in-four win rate.
3. It is one-sided toward "estimate better", so it cannot speak to the result that matters most, the same quarter last year being closer.

**What does the autocorrelation do?** With positive dependence the win count varies more than a Binomial(26, 1/2), so the exact p-value is too small. Here it cannot matter: no test rejects, so dependence cannot turn a non-rejection into a false rejection. Only guidance pace shows dependence worth the name: lag-1 0.353 is 1.80 standard errors (1/sqrt(26) = 0.196), lags 2 and 3 are 0.287 and 0.271, the win/loss series itself has lag-1 0.265, and it contains ten straight wins (2023Q1 to 2025Q2) followed by four straight losses. A Newey-West variance with four lags is 2.17 times the independent one; an AR(1) reading gives about 12 effective quarters, not 26.

**Is the direction of the caveat right for each baseline?** Yes, with one overstatement. README line 37 applies the "overstates the evidence" caveat to guidance pace (0.35) and last quarter (0.10) and leaves out the same quarter last year (-0.19). That is the right direction for each. But 0.10 is half a standard error and -0.19 is one: neither differs from zero. Saying the last-quarter differences "are positively autocorrelated" reports noise as a property (STAT-12). For the same quarter last year the win/loss series alternates (lag-1 -0.380, 18 runs against 13.7 expected, z 1.77); a negative correlation makes the independent test conservative if anything, and the result runs the wrong way for the estimate regardless.

**Alternatives computed** (`s2_tests.py`; D = baseline's miss minus the estimate's, positive when the estimate is closer):

| Baseline | Mean D | DM with HLN, one-sided (two-sided) | Newey-West L=4, one-sided | Sign-flip permutation, one-sided | Block bootstrap (block 4), 95% interval for mean D | Wilcoxon, one-sided |
|---|---|---|---|---|---|---|
| GD's guidance pace | 1.39 | 0.184 (0.368) | 0.266 | 0.184 | -2.38 to 5.53 | 0.170 |
| Same quarter last year | -0.91 | 0.771 (0.459) | 0.797 | 0.770 | -2.82 to 1.19 | 0.823 |
| Last quarter | 3.28 | 0.018 (0.035) | 0.021 | 0.017 | 0.49 to 6.05 | 0.033 |

For guidance pace and the same quarter last year every alternative agrees with the README. For last quarter the mean-based tests reject at a raw 5% where the sign test gives 0.163; under Holm across three they sit just above the first threshold (0.0176 against 0.0167). So the project understates its edge over the weakest baseline. That is an error in the safe direction and changes no headline.

### 2. Holm across three tests

The family is right: three baselines, one direction, fixed before scoring. The code (`src/gdn/stats.py:17-27`) is a correct step-down. Nothing is gained and nothing is hidden: the smallest raw p is 0.163, so all three fail with or without the correction, and the raw p-values are printed beside the Holm column. Two things a reader could miss: the correction only guards the "estimate better" direction, so it says nothing about the seasonal result (two-sided sign test p 0.557, also not distinguishable); and "does not reject" under a test with the power shown above is weak evidence of no difference. An interval would say more than the p-value does (STAT-11).

### 3. E1 against E2 on a 0.11 gap over 12 quarters

**Is the choice meaningful?** No. The two definitions give the same registry count in 11 of the 12 design quarters. They differ in 2019Q4 by one large-cabin airframe (29 against 30), which moves that quarter's estimate from 47.267 to 48.566 against 44 reported. The whole design gap is 1.2989 aircraft of summed error from that one quarter (`s1_headline.py`, `s3_band_e2.py`). Across all 42 quarters the counts differ in seven quarter-cabins, by one or two airframes each.

**Held-out results under E2** (my sensitivity, not preregistered):

| | E1 (published) | E2 |
|---|---|---|
| Ratio average miss | 5.5234 | 5.4683 |
| Ratio average % miss | 17.91 | 17.83 |
| Ratio bias | 2.236 | 2.227 |
| Raw count average miss | 6.1923 | 6.2692 |
| Wins against guidance pace | 14 of 26, p 0.423 | 17 of 26, p 0.084 |
| Wins against same quarter last year | 11 of 26, p 0.837 | 12 of 26, p 0.721 |
| Wins against last quarter | 16 of 26, p 0.163 | 17 of 26, p 0.084 |
| Band hits | 18 of 26 | 19 of 26 |

The unchosen definition did slightly better out of sample. The headline would read 5.5 either way, Holm would reject nothing either way, and the same quarter last year wins either way. At the lock, E2 would have given 31.40 against E1's 31.95 (`s4_trunc_drift.py`). So the fragility is harmless, but the project does not say how thin the choice was on any front-page surface (STAT-8). `docs/build/DECISIONS.md:92` does say the definitions "agree to the airframe except 2019 large".

**Anything else chosen in the design window and not disclosed?** I found none. What the design window also produced is disclosed in `docs/build/DECISIONS.md`: a planned stop on low mid-cabin coverage in 2016 and 2017 that the owner overrode at 11:59 EDT (lines 90 to 106, also in the interview notes), and the fact that the ratio lost to last quarter in the design window (line 123). The four-quarter scale, the 365-day bound, the per-cabin scaling, the baselines and the tests come from the build spec, which predates the repository; I cannot check what its author had seen.

### 4. The band

- **Clopper-Pearson: correct.** `stats.clopper_pearson` solves the two binomial tail equations by bisection. My independent beta-quantile version gives 48.210% to 85.674% for 18 of 26; the file stores 48.2104 and 85.6740.
- **Confidence or prediction interval wording: none found.** `grep -rn -i -E "confidence|prediction interval|credible|error bar|uncertainty"` over the README, post, `docs/*.md`, `site/`, `report/note.html` and `src/gdn/*.py` returns only the preregistration's own "never a confidence interval". The workbook labels read "Past-miss P10", "Past-miss P90", "Band low", "Band high". "Against a nominal 80%" does treat the band as an 80% band, which is what a P10 to P90 band is.
- **Live band built as preregistered: yes.** 38 signed errors (12 design, 26 holdout), nearest rank at positions 4 and 35, band [21.233381, 37.241087], equal to `predictions/2026Q3.json`. The 2026Q4 working file uses 39 errors including the lock's -8.05, as the rule says (`s8_q4band.py`).
- **Described honestly?** Mostly. The README (line 144), the note (twice) and the interview notes say the band comes from a finished file. Two gaps. First, the reason given, "when recent registrations have not posted", is not what the repository's own data show (STAT-3). Second, "nominal 80%" is higher than the rule can deliver: with n past errors a new exchangeable error falls between the two chosen order statistics with probability (s - r)/(n + 1), which is 69.2% at n = 12 and 78.9% at n = 37, 76.4% on average over the 26 quarters (`s3_band_e2.py`). The realised 69.2% is not distinguishable from 80% (P(18 or fewer | 0.80) = 0.131) nor from 76.4% (0.258). So "covers 69% against 80%" is a fair but slightly harsh self-description, and the undercoverage is not established (STAT-13).
- The eight misses split five below the band and three above.

### 5. Reconciling the truncation test with the live miss

They measure different things, and the difference is large.

**What `truncated_mae` measures** (`src/gdn/model.py:165-175`): for each held-out quarter it deletes every event dated in the last d days of the quarter and scales what is left by the full, uncut four-quarter ratio. At d = 30 that keeps 55.4% of the quarter's own events on average, because 44.6% of a quarter's events are dated in its last 30 days (range 26.3% to 68.4%). The scale is not adjusted, so the estimate is low by construction: it misses low in 25 of 26 quarters, with a mean signed error of -13.32. The 13.5 is close to a mechanical undercount, not a forecast error. If the four lags are cut the same way, so the scale compensates, the 30-day miss is 8.92, not 13.47 (my variant; 14.48 at 60 days, 23.78 at 90).

**What `live.predict` measured on 2026-10-29** (`src/gdn/live.py:121-141`): every event dated in the quarter that had posted by the snapshot, 25 days after the quarter ended, scaled by the same snapshot's four lags. The daily tables show the quarter's own count at 41 on 2026-10-19 (15 days after the end), 42 from 2026-10-27, and still 42 on 2026-11-11 (38 days after). The count of events dated in the window's last 30 days was 15 on 2026-10-19 and is 15 today. No event that was missing at the lock has appeared since.

**Why 8.05 and not 13.5.** The lock was never in the truncation test's situation. In "days cut" terms it sits at a negative number: 25 days after the end, not 30 before. The archive captures say the same: at 23 to 29 days after the end, the quarter's own count was 40 against 38 in the finished copy (2025Q3), 54 against 55 (2026Q1) and 55 against 57 (2026Q2). The shortfall from late posting at lock time has been zero to two events, against the 45% the 30-day row removes.

**Where the live miss came from.** The scale. The registry counted 42 events against GD's 40, and 35 large-cabin events against GD's 35. The trailing scale was 163/215 = 0.758 (large 0.749), while the quarter's own turned out to be 40/42 = 0.952 (large 1.000). The raw count missed by 2; the scaled estimate missed by 8.05.

**Could the README mislead?** Yes, in both directions (STAT-2).
- Too pessimistic about posting: the dashboard calls the table "a crude stand-in for a live quarter" under the heading "When the registry has not finished posting" and sets its rows "against 6.9 for GD's guidance pace". A reader takes 13.5 as the likely live miss and concludes the method loses to guidance once it runs live. The lock's data do not support that.
- Too optimistic about everything else: the table holds the scale fixed, so it is silent on the error source that produced the live miss, and on the loss of first-owner records in the lag quarters. A reader who works out that the lock comes after the quarter ends could wrongly conclude the 0-day row, 5.5, is the live expectation.

### 6. Deliveries per event at 0.69 to 0.72 against a 1.18 mean

**The 1.18 mean is not a stable level.** Over the baseline window 2017Q1 to 2025Q2 the series falls steadily: Kendall tau -0.602, Mann-Kendall z -5.00, first half mean 1.426, second half 0.939, a fitted fall of 0.84 over the window (`s4_trunc_drift.py`). A straight line through that window reads 0.712, 0.687 and 0.661 at 2025Q4, 2026Q1 and 2026Q2, against the observed 0.692, 0.691 and 0.719. The last three quarters are on a nine-year trend, not a recent break.

**Is the two-standard-deviation flag a meaningful check?** No. The standard deviation, 0.352, is inflated by the trend (0.248 around the trend line). The flag's threshold is 1.886; inside the baseline window only 2017Q4 and 2020Q2 exceed it, and the three other quarters that do are all in 2016. Even a two-sided version would not fire: the lower limit would be 0.479 and the recent quarters sit at z = -1.39, -1.40 and -1.32. "None is flagged" is true and says nothing. The README does add that the drift runs the other way, which is to its credit, but it measures the drift against a mean that the trend makes meaningless.

**What the trend is.** Mostly the age of the file. The README's own as-of section shows the 2026-10-19 copy holds 63 events for the four quarters of 2016 where the April 2017 archive held 146. Read at the time, the registry showed 1.21 events per reported delivery for 2016, and 1.23, 1.25 and 1.29 in the three recent captures. In the finished copy the same quantity reads 0.52 for 2016. So the registry has shown about 1.2 to 1.3 events per delivery in every fresh copy the project has, and "fewer than 1 before" is what old quarters look like after years of lost first-owner records.

**Is the excess explained with evidence?** Half of it. The low early coverage is explained with evidence (`docs/build/DECISIONS.md:103`: G280s whose only date is a certificate about seven years after first airworthiness; the 146 against 63). Why a fresh registry holds 20% to 45% more first-customer events than GD reports deliveries is not explained anywhere. The airframe audit found used jets read as new, but every event it could date fell between 2000 and 2019. The 1.39 to 1.45 events per delivery of the last three quarters has no stated cause, and under the project's own rule none can be given without a filing.

**What it means for the ratio model.** The model assumes this quarter's scale equals the trailing four-quarter scale. Across the 26 held-out quarters the gap between those two scales correlates 0.918 with the signed error: the scale gap is the error. And the quarterly scale does not drift smoothly, it whipsaws: 1.026, 0.692, 0.691, 0.719 in the last four held-out quarters, then 0.952 in the live one. "Absorbs only with a lag" predicts over-estimates, which is what 2025Q4 to 2026Q2 showed (+13.4, +7.4, +3.8). The live quarter then missed low by 8.0 when the scale snapped back. A trailing mean cannot follow a series like that, and the README's sentence would have led a reader to expect the opposite sign at the lock.

**Inverse units.** Yes. README line 69 uses deliveries per event (1.18; 0.69, 0.69, 0.72). README line 142 uses events per delivery (0.52 in 2016, 0.80 in 2019). On one scale the series is 0.52, 0.65, 0.66, 0.80, 0.74, 0.96, 1.13, 1.05, 1.09, 1.22 events per delivery by year from 2016 to 2025, and 1.42 for the first half of 2026: one continuous rise that the README shows as two unrelated facts. Also, "averaged 1.18" is the mean of the quarterly ratios; total deliveries over total events in the same window is 1075/973 = 1.105 (STAT-4, STAT-14).

### 7. Is "not statistically distinguishable" the right phrase for each result?

- **Guidance pace** (estimate closer on average, p 0.42): right. Every test I ran agrees (one-sided 0.17 to 0.27; block-bootstrap interval for the mean difference -2.4 to +5.5 jets).
- **Same quarter last year** (estimate further on average): the phrase is never applied to it, correctly. The surfaces say it "missed by less on average, 4.6", which is the plain fact. That difference is itself not distinguishable (two-sided sign test 0.557, DM 0.459), and saying so would be fair to the project.
- **Last quarter** (estimate closer, sign-test p 0.16): the table's "does not reject" is right for the sign test. A test on the average does separate them (two-sided 0.035). The project is understating here.

**Does the headline hide the loss to a naive baseline?** Not in the post, the note, the dashboard or the interview notes: each follows the headline with "Simply repeating the same quarter last year missed by less on average, 4.6." The README does not. Its Results section never says in words that a naive baseline beat the estimate; a reader has to find 4.6 in the table and 1.20 in the next one. The resume bullet says "5.5 jets a quarter vs 6.9 for guidance, not significant" and stops (STAT-6).

Two further things the headline does not show (STAT-5): the whole edge over guidance pace comes from 2023 and 2024, and the estimate has lost to guidance pace in each of the last five quarters, the live one included.

### 8. P-hacking, forks, denominators

**Commit order.** `git log --format='%h %ad %s' --date=iso -- docs/PREREGISTRATION.md results/metrics.json results/holdout.csv` returns two commits: `2c62ad3` at 2026-10-19 11:02:12 -0500 (preregistration) and `48c1ea0` at 11:04:28 -0500 (holdout). The preregistration came first. Each file has been committed once and never changed. The README's sentence, that the rules were committed before the held-out quarters were scored, is supported.

What the order cannot show: the two commits are 2 minutes 16 seconds apart in one session; the registry counts and GD's counts for every held-out quarter were committed at 10:48:35 (`6725184`); and the full scoring code was committed in the same second as the preregistration (`5c84d36` adds all 272 lines of `src/gdn/model.py`). Git proves the order of commits, not that nothing was run earlier. I found no evidence that anything was: `results/diagnostics/coverage_design.csv`, the one diagnostic committed before the preregistration, covers 2016 to 2019 only. I report this as a limit of the evidence, not as a finding.

**Forks.** None found. `results/exploratory/` holds only the as-of study. Its numbers are identical in its first commit (`9b84384`) and today; later commits changed prose only. No alternative model, window or test appears anywhere in the history of the results files.

One observation, not a finding: the rule that puts guidance pace first in the headline needs 22 sourced quarters, and exactly 22 are sourced. With 21 the preregistered headline would have named the same quarter last year, the baseline that won. I cannot show the threshold was set with the count in view.

**The as-of sentence.** "In all four the copy from a few weeks after the quarter missed by less than the finished copy" is true: 3.34 against 5.55, 6.61 against 6.80, 5.33 against 7.38, 1.69 against 3.81. It is fair as written because the README gives the denominators (75 captures, six in the window, four scorable), says one of the four is a design quarter by listing "three held-out", and ends with "Four quarters prove nothing". Two things would make it tighter: the margins (0.2 to 2.2 jets; in 2025Q3 it is 0.19), and that the four are not independent (2026Q1 and 2026Q2 share three lag quarters) (STAT-15).

**Denominators.** Present where I looked: 18 of 26, 22 of 26, 10 of 30, four of six captures, n = 1 for the live record.

### 9. The live record of one

"One quarter shows how it works live, not whether it works" is the right thing to say about n = 1.

**What can be said.** The estimate was locked before GD reported (release published 2026-10-29T05:51:24Z, hash verified). It missed by 8.05 jets, 20.1%. GD's count was 2.76 above the top of the band. Six of the 26 held-out misses were at least that large, so the miss is in the upper quarter of the backtest's misses, not outside its range. All four comparators were closer that quarter: the same quarter last year 39 (miss 1), last quarter 41 (miss 1), the raw count 42 (miss 2), guidance pace 33.84 (miss 6.16). The miss came from the scale, not from late postings (question 5).

**What cannot be said.** That the band is miscalibrated: a single draw falls outside an 80% band one time in five, and outside a band that held 18 of 26 about 31% of the time (95% interval 14% to 52%). That live accuracy is worse than the backtest: counting the three held-out as-of quarters with the lock gives misses of 6.61, 5.33, 1.69 and 8.05, mean 5.42, with the band holding two of four, and four is still nothing. That the method works, or that it does not.

**What is missing.** Only the README says the miss fell outside the band. The note gives "GD reported 40, against a guidance pace of 33.8" and leaves the subtraction and the band comparison to the reader. No surface says that every comparator was closer (STAT-7). And the interview notes and resume bullets still describe the lock as in the future (STAT-1).

### 10. Averages and rounding

- **Averages of rounded values: none.** Every table cell matches a recomputation from full precision. The relative misses are computed from unrounded averages and also equal the ratios of the rounded ones at two decimals.
- **Wrong base: none.** 69.2% is 18/26; 33.3% is 10/30; each quarter's percentage miss divides by that quarter's reported total.
- **The percentage column.** "Average % miss" (README line 17) and "Average miss, %" (note, Exhibit 2) are the mean of the 26 per-quarter percentages, which is what `model.py:202` computes. Neither label says so. The average miss over average deliveries (32.692 a quarter) would be 16.9% for the estimate, not 17.9%; 14.1% against 15.2% for the same quarter last year; 21.2% against 23.2% for guidance pace. The order of the models is the same either way, but a reader who divides 5.5 by a typical quarter will not get the printed figure (STAT-14).
- The post's "off by 8.0" is 8.047 rounded and agrees with 40 less 32.0.

---

## Findings

### STAT-1 (S1). The owner material still describes the lock as a future event

- **Surface:** `docs/INTERVIEW_NOTES.md:9`, `docs/INTERVIEW_NOTES.md:27`, `docs/RESUME_BULLETS.md:2`.
- **Evidence:** `grep -n -i -E "first lock|is scored|locks on|build estimate" docs/INTERVIEW_NOTES.md docs/RESUME_BULLETS.md` returns: line 9, "The first lock is scored when GD reports on 2026-10-30."; line 27, "My build estimate is 31.1 deliveries, with a band of 20.4 to 36.4. It locks on 2026-10-29 ... One quarter will show how the method behaves live"; resume line 2, "the first, for 2026Q3, is scored on 2026-10-30". `results/live/2026Q3_score.json` shows the lock scored: 31.95 against 40, `ae_total` 8.0468, `inside_band` false. Both files were last changed on 2026-10-19.
- **Why it blocks:** the answer to "What did the locked quarter show?" is the one an interviewer will ask first, and it currently gives a superseded estimate (31.1, not the locked 32.0) and no result.
- **Fix:** "The first lock, for 2026Q3, was 32.0 with a band of 21.2 to 37.2, published at 01:51 ET on 2026-10-29. GD reported 40. I missed by 8.0, outside the band. GD's guidance pace was 33.8 and missed by 6.2; the same quarter last year and last quarter each missed by 1. One quarter shows how it works live, not whether it works." Resume: "the first lock, for 2026Q3, missed by 8.0 jets (32.0 against 40)".

### STAT-2 (S2). The truncation table is offered as a stand-in for a live quarter, and it is not one

- **Surface:** `README.md:71-78`, `README.md:139`, `site/index.html:69-70`, `site/app.js:377`, `report/note.html:71`.
- **Evidence:** question 5. The 30-day row keeps 55.4% of a quarter's own events, leaves the scale uncut and misses low in 25 of 26 quarters (mean signed error -13.32). The lock was made 25 days after the quarter ended, when the quarter's count (42) equalled its count 13 days later (42). Three archive captures at 23 to 29 days show the count within two events of the finished copy. The live miss came from the scale (0.758 trailing, 0.952 realised). A like-for-like cut of the lags gives 8.92 at 30 days, not 13.47.
- **Defensible version:** keep the table, since it is preregistered, and add: "This table cuts events dated in the last days of the quarter and does not rescale, so it mostly measures how back-loaded a quarter is: 45% of a quarter's events are dated in its last 30 days. It is not what a lock faces. A lock is made about 25 days after the quarter ends; in the three recent archive copies and at the 2026Q3 lock, the quarter's own count was within two events of the later copy. The 2026Q3 miss came from the scale, 0.76 trailing against 0.95 realised, not from late postings." On the dashboard, drop "A crude stand-in for a live quarter" and the comparison with guidance pace in the table caption.

### STAT-3 (S2). "Had months or years to fill in", "flatters" and "too narrow when registrations have not posted" point one way; the repository's evidence points the other

- **Surface:** `README.md:11`, `README.md:139`, `README.md:144`, `docs/LINKEDIN_POST.md:5`, `site/index.html:100`, `site/app.js:101-102`, `report/note.html:53`, `:65`, `:75`, `:89`, `:94`, `results/error_analysis.md:3`, `docs/INTERVIEW_NOTES.md:21`.
- **Evidence:** the framing says the finished copy is the more complete one. For old quarters it is the less complete one: 63 events for 2016 against 146 in the April 2017 archive; 19 own events for 2017Q1 against 40 at capture (`s4_trunc_drift.py`). In all four as-of quarters the at-the-time copy missed by less. The 2026Q3 count has not grown since the lock. The dashboard's "why the test on past quarters flatters it" (`site/index.html:100`) is therefore not supported by anything in the repository, and README line 144 gives a reason ("when recent registrations have not posted") that the lock's own path contradicts. The note already has the better sentence: "a later file is not simply a more complete one".
- **What stands:** the conclusion. One copy cannot show what a lock would have read, so only the locked quarters test that.
- **Defensible version:** "The backtest reads one registry copy, from 2026-10-19. For recent quarters that copy has had time to fill in; for older quarters it has lost first-owner records (63 events for 2016, against 146 in an April 2017 archive). Either way it is not what a lock would have read, so only the locked quarters test whether the registry counts deliveries in time." Dashboard: "why the test on past quarters is not a test of a live estimate". Band: "so it may not fit a live lock; the first lock fell outside it."
- **Note:** the first sentence is the project's mandated framing. I am not saying it is false for recent quarters, where the copy did gain one or two events. I am saying it tells the reader the wrong direction for most of the sample. The dashboard's "flatters" and "stand-in for a live quarter" are the two phrases here closest to a blocking defect.

### STAT-4 (S2). The drift paragraph measures a trend against its own mean, uses a flag that cannot fire, and states the quantity in inverse units elsewhere

- **Surface:** `README.md:69`, `README.md:142`, `report/note.html:72`, `site/app.js:369-375`.
- **Evidence:** question 6. Kendall tau -0.602 inside the baseline window; trend line reads 0.712, 0.687, 0.661 where the data read 0.692, 0.691, 0.719; flag threshold 1.886, lower two-sigma limit 0.479, recent z about -1.4; fresh copies show 1.21 to 1.29 events per delivery in 2017, 2025 and 2026; scale gap correlates 0.918 with the signed error; the live scale was 0.952 against a trailing 0.758.
- **Defensible version:** "In the 2026-10-19 copy, registry events per reported delivery rise almost every year, from 0.52 in 2016 to 0.80 in 2019, 1.22 in 2025 and 1.42 in the first half of 2026. Most of that is the file's age: older quarters have lost first-owner records, and archive copies read at the time show about 1.2 to 1.3 events per delivery as far back as 2017. I cannot say from any filing why a fresh registry holds more first-customer events than GD reports deliveries. The preregistered flag looks only for a fall in events per delivery and found none; it could not have caught this. The quarter's own scale also swings from one quarter to the next (1.03, 0.69, 0.69, 0.72 deliveries per event, then 0.95 in 2026Q3), and that swing, which a four-quarter average cannot follow, accounts for most of the estimate's miss."

### STAT-5 (S2). The edge over guidance pace comes from 2023 and 2024 alone, and the last five quarters all went the other way

- **Surface:** `README.md:13`, `docs/LINKEDIN_POST.md:5`, `report/note.html:53` and `:65`, `site/app.js:92-94`, `docs/INTERVIEW_NOTES.md:7`, `docs/RESUME_BULLETS.md:1`.
- **Evidence** (`s1_headline.py`, `s6_recent.py`): in 2023 and 2024 the estimate was closer in 8 of 8 quarters, 3.48 against 12.52. In the other 18 quarters guidance pace was closer on average, 4.43 against 6.43, and the estimate won 6 of 18. Dropping 2023 alone turns the mean difference from +1.39 to -0.20. In those two years GD cut its own outlook during the year (`data/guidance.csv`: 145 to 134 in 2023, 160 to 150 in 2024), and the pace rule puts the whole remaining outlook into the fourth quarter (62.0 against 39 reported in 2023Q4, 61.0 against 47 in 2024Q4). From 2025Q3 to 2026Q2 the estimate was fourth of the five models in every quarter (average miss 7.85 against 5.30 for guidance pace), and in the live quarter it was fifth of five.
- **Why S2:** the by-year table shows the raw numbers, so nothing is hidden, but no sentence tells the reader that "5.5 against 6.9" is two unusual years.
- **Defensible version, after the headline:** "That edge comes from 2023 and 2024, when GD cut its own outlook during the year: the estimate was closer in all eight of those quarters. In the other 18, GD's guidance pace was closer on average, 4.4 against 6.4, and it has been closer in each of the last five quarters, the locked one included."

### STAT-6 (S2). The README never says in words that a naive baseline beat the estimate

- **Surface:** `README.md:13` to `:43`; `docs/RESUME_BULLETS.md:1`.
- **Evidence:** the post (line 5), note (line 53), dashboard (`site/app.js:99`) and interview notes (line 7) all carry "Simply repeating the same quarter last year missed by less on average, 4.6." `grep -n "Simply repeating" README.md` returns nothing. The design sentence (line 43) gives 5.47 against 5.00 and 3.83 without saying the estimate lost to both. The same quarter last year was the closest of the five models in 11 of 26 quarters; the estimate in 5.
- **Fix:** add the sentence under the bold headline, and to line 43 "so in the design window both simple baselines were closer". Resume: "5.5 jets a quarter against 6.9 for GD's guidance pace and 4.6 for a same-quarter-last-year rule; no difference significant".

### STAT-7 (S2). The live record is reported without its comparators, and two surfaces never say the lock fell outside its band

- **Surface:** `README.md:92`, `docs/LINKEDIN_POST.md:1`, `report/note.html:54` and `:75` (and the PDF's first page), `site/app.js:143-147`.
- **Evidence:** `s3_band_e2.py`: 2026Q3 misses were 1 (same quarter last year, 39), 1 (last quarter, 41), 2 (raw count, 42), 6.16 (guidance pace) and 8.05 (the lock). `grep -n -o -i "outside" report/note.html` finds no sentence about the band; the note says "GD reported 40, against a guidance pace of 33.8" and nothing more. The dashboard shows the miss and the band but not the words; `site/data.json` carries `inside_band: false` unused. The post compares the backtest with two baselines and the live quarter with none.
- **Defensible version:** README and note: "GD reported 40: the lock missed by 8.0, outside the band. GD's guidance pace (33.8) missed by 6.2; the same quarter last year (39) and last quarter (41) each missed by 1; the unscaled registry count (42) missed by 2." Post, if space allows: "GD's own guidance pace missed by 6.2 that quarter."

### STAT-8 (S2). The design window's one choice rested on one airframe in one quarter

- **Surface:** `README.md:43`, `README.md:105`, `report/note.html:64`, `site/index.html:59` and `:97` ("set the rule"), `docs/INTERVIEW_NOTES.md:7` ("I fixed the rules on 12 design quarters").
- **Evidence:** question 3. E1 and E2 agree in 11 of 12 design quarters; the 0.108 gap is 1.2989 aircraft of summed error from 2019Q4; under E2 the held-out miss is 5.4683 against 5.5234 and the band holds 19 of 26.
- **Why S2:** no figure moves, but "the design window chose" and "set the rule" present as a selection step something that selected nothing of substance, and E2 was marginally the better choice out of sample. A referee will compute this in five minutes.
- **Defensible version:** "The two definitions give the same count in 11 of the 12 design quarters and differ by one airframe in 2019Q4, so the choice of E1 is close to arbitrary. Under E2 the held-out miss would be 5.5 as well (5.47 against 5.52)." Interview notes: "I fixed the rules before the build and used 12 design quarters only to pick between two near-identical event definitions."

### STAT-9 (S2). The headline's "registry count" is not the table's "Raw registry count"

- **Surface:** `README.md:13` against `README.md:19-20`; `docs/LINKEDIN_POST.md:5`; `report/note.html:53`; `docs/RESUME_BULLETS.md:1`.
- **Evidence:** the headline says "the registry count was off by 5.5". In the table two rows down, 5.5 belongs to "Registry estimate (ratio)" and the "Raw registry count" is off by 6.2 (6.1923). The sentence is the preregistered template.
- **Defensible version:** "the registry estimate was off by 5.5 jets a quarter". If the template must stay word for word, add after the table: "'Registry count' in the headline means the scaled estimate; the unscaled count missed by 6.2."

### STAT-10 (S2). The decision log and a code comment say the 2024Q3 band uses position 4; the code uses position 3

- **Surface:** `docs/build/DECISIONS.md:110`, `src/gdn/stats.py:33-34`.
- **Evidence:** the log says "at n = 30 the P10 position is 4, not 3" and the comment says "0.1 * 30 is 3.0000000000000004 and the position is 4". `.venv/bin/python -c "import math; print(repr(0.1*30), math.ceil(0.1*30))"` prints `3.0 3`. The stored 2024Q3 band high is 40.5944, which is the position-3 value; position 4 would give 40.4235 (`s5_misc.py`). For n from 12 to 60 the floating-point positions equal the exact ones (`s3_band_e2.py`).
- **Effect:** none on any figure. The code follows the preregistered formula exactly; the log wrongly says it departs from it. I did not check the gate's version of this.
- **Fix:** delete the sentence and the comment, or replace with "0.1 * 30 rounds to 3.0 in double precision, so the position is 3, as the formula says."

### STAT-11 (S3). The test counts wins while the headline talks about the average; no interval is given

- **Surface:** `README.md:13`, `README.md:27-33`.
- **Evidence:** questions 1 and 2. Power of the Holm-corrected sign test is 12% at a true 60% win rate. The matched test on the average gives the same answer for guidance pace (DM with HLN two-sided 0.368) and a different one for last quarter (0.035).
- **Suggested addition:** "The average gap to GD's guidance pace is 1.4 jets, with a 95% block-bootstrap interval of about -2.4 to +5.5." Label it as computed after the fact.

### STAT-12 (S3). The autocorrelation sentence treats 0.10 as a finding

- **Surface:** `README.md:37`, `site/app.js:357`.
- **Evidence:** standard error 0.196 at n = 26; 0.35 is 1.80 standard errors, 0.10 is 0.49, -0.19 is -0.98.
- **Defensible version:** "The differences against GD's guidance pace are positively autocorrelated (0.35, about 1.8 standard errors), so those 26 quarters carry less evidence than 26 independent ones. The other two autocorrelations are within noise."

### STAT-13 (S3). "Nominal 80%" is more than the nearest-rank rule can deliver on 12 to 37 past errors

- **Surface:** `README.md:41`, `report/note.html:68`, `site/app.js:366`.
- **Evidence:** question 4: 69.2% at n = 12, 78.9% at n = 37, 76.4% on average. The live band at n = 38 is (35 - 4)/39 = 79.5%.
- **Suggested wording:** "against a nominal 80% (about 76% given how few past misses the early bands had)". Also say what the 95% interval is an interval for: the hit rate.

### STAT-14 (S3). Two averages are not labelled as what they are

- **Surface:** `README.md:17` ("Average % miss"), `report/note.html:66` ("Average miss, %"), `README.md:69` ("averaged 1.18").
- **Evidence:** question 10 and question 6: mean of per-quarter percentages 17.91% against 16.90% for the average miss over average deliveries; mean of quarterly ratios 1.182 against 1.105 for total deliveries over total events.
- **Fix:** "Average % miss is the mean of each quarter's miss as a share of that quarter's deliveries." "The quarterly ratio of GD deliveries to registry events averaged 1.18."

### STAT-15 (S3). The as-of sentence would be tighter with its margins

- **Surface:** `README.md:122`, `docs/INTERVIEW_NOTES.md:33`.
- **Evidence:** margins 2.21, 0.19, 2.05, 2.12 jets; 2026Q1 and 2026Q2 share three lag quarters.
- **Suggested wording:** "In all four the earlier copy missed by less, by 0.2 to 2.2 jets; the four overlap in their lag quarters and are not independent."

### STAT-16 (S3). The 2026Q4 working file carries a band on a part-quarter count

- **Surface:** `results/live/2026Q4_latest.json`, `site/data.json` (`live[1]`, `path.2026Q4`).
- **Evidence:** `s8_q4band.py`: "nowcast" 14.31 with band [3.59, 21.11] at 38 of 88 days of the window. The band's errors come from full quarters. The README (line 93) correctly says no estimate is shown yet, and the dashboard shows the scored quarter instead. A reader who opens the JSON sees an estimate and a band that mean nothing yet.
- **Suggested fix:** one line in the README's Live record: "the working file `results/live/2026Q4_latest.json` holds a part-quarter count; its band does not apply until the window closes."

---

## What I could not check

- Whether anything was run on the held-out quarters before the preregistration commit. Git shows the order of commits only.
- Whether the build spec's choices (ratio, four lags, 365-day bound, the 22-quarter threshold) were made with any data in view.
- How the gate computes the nearest rank at n = 30.
- Why a fresh registry shows more events than GD reports deliveries. `serials.csv` has no owner names, and that belongs to the registry reviewer.
- GitHub's server-side push times for the early commits (`gh api` is off limits).

## The three things I would fix first

1. **The live record, everywhere.** Update the interview notes and resume bullets with the scored result (STAT-1), and state on each surface that reports the lock that it fell outside the band and that all four comparators were closer (STAT-7).
2. **What the backtest does and does not say about a live lock.** Rewrite the truncation text, the "fill in" framing, the band's stated reason and the drift paragraph so they say what the repository's own data show: late posting has cost zero to two events at lock time, old quarters lose records, and the live miss was a scale miss (STAT-2, STAT-3, STAT-4).
3. **The headline's context on the README.** Add the sentence that the same quarter last year was closer, and the sentence that the edge over guidance pace is 2023 and 2024 only and reversed in the last five quarters (STAT-5, STAT-6). Then the "registry count" label (STAT-9) and the E1/E2 line (STAT-8).
