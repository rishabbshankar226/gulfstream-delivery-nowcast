# Round 2 review: statistician

Reviewer `round2_statistician`, 2026-11-11. Tree read: `~/gdn-prepub/round2_clean`.

## Verdict

**NO-GO as written, on one sentence (STAT-3, S1). GO once that sentence is fixed on the post and the three other places it appears.** Every figure on the post and on the README's first screen reproduces from the four input CSVs with my own code. Nothing I found changes a number. The one S1 is a sentence a reader can prove false from the repository's own dates. The rest is wording that says more than the tests carry, two things on the post that a careful reader will take for errors, two missing disclosures, and one generated sentence whose conclusion is fixed text.

Counts: **S1 1, S2 10, S3 9.**

The three I would fix first, all one-line edits:

1. **STAT-3 (S1), and STAT-2 in the same line of the post.** The post says the registry copy "had years to fill in"; three held-out quarters had 106, 197 and 292 days. The same line calls the scaled estimate "the registry count", when the README's own "Raw registry count" row says 6.2, not 5.5.
2. **STAT-1.** "8.0 jets (20.1%)" next to "32.0" and "40". A reader divides 8.0 by 40 and gets 20.0%. It is on the post, the README's first screen, the note's first page and the interview notes.
3. **STAT-4.** "No test finds the registry estimate better than a baseline." Three sign tests were run. A paired t-test on the same misses separates the estimate from the last-quarter rule at the unadjusted 5% level. Say "none of the three preregistered sign tests".

## What I ran

All scripts are in `~/gdn-prepub/agents/round2_statistician/`, run with the project's venv python from the tree root. None imports the project's code.

| Script | What it does | Log |
|---|---|---|
| `recompute.py` | Rebuilds the five models, tests, band, by-year table, sensitivity rows and the 2026Q3 score from `gd_deliveries.csv`, `registry_quarterly.csv`, `guidance.csv`, `quarter_plans.csv`; then diffs against `results/holdout.csv`, `results/metrics.json`, `results/exploratory/sensitivity.json`, `predictions/2026Q3.json`, `results/live/2026Q3_score.json` | `recompute.log` |
| `check2.py` | Counts the 2026Q3 window in each of the 24 daily airframe tables; rebuilds the truncation table from `serials.csv`; prints the as-of rows; my own paired tests | `check2.log` |
| `check3.py` | Near ties, combinations, leave-out, band width (my own, after the fact) | `check3.log` |
| `check4.py`, `check5.py` | Line locations; rebuilds the four as-of estimates | printed |
| `check6.py`, `check7.py` | Small derived figures; which quarters change sides between E1 and E2 | printed |
| `strip_note.py`, `site_scan.py` | Text of `report/note.html`, `site/index.html`, `site/app.js` | printed |

Also: `gh release view lock-2026Q3` (published `2026-10-29T05:51:24Z`, notes carry the sha256), and the PDF's pages 1 and 2 by eye.

Code read: `src/gdn/model.py`, `stats.py`, `sensitivity.py` and `fiscal.py` in full. `src/gdn/report.py` by `grep -n` and lines 126 to 139 and 232 to 263 only; the sentences I checked there are built from the metrics, with one exception (STAT-20).

## Q1. Recompute

Everything matches. `recompute.py` output, last block:

```
holdout.csv rows 130 cells compared 650 max abs diff 0.0
metrics.json mae/mape/bias/large/mid/ex2020 max abs diff 0.0
metrics band by_quarter max diff vs mine: 0.0 hit flags equal: True
band_errors max diff 0.0 38
sens ... (all 9 variants) max mae diff 0.00e+00, wins equal, p diff 0.00e+00
sha256(predictions/2026Q3.json) = 3c4cdbd0...6f23  equals lock: True
```

| Figure | Mine | Shown | Match |
|---|---|---|---|
| Average miss, registry estimate | 5.5234 | 5.5 | yes |
| Raw registry count | 6.1923 | 6.2 | yes |
| GD guidance pace | 6.9173 | 6.9 | yes |
| Same quarter last year | 4.6154 | 4.6 | yes |
| Last quarter | 8.8077 | 8.8 | yes |
| Sign test against guidance | 14 of 26, p 0.422509 | 14, 12, 0.423 | yes |
| Against same quarter last year | 11 of 26, p 0.836530 | 11, 15, 0.837 | yes |
| Against last quarter | 16 of 26, p 0.163470 | 16, 10, 0.163 | yes |
| Holm at 0.05 across three | none rejected | does not reject | yes |
| Relative miss | 0.7985, 1.1967, 0.6271 | 0.80, 1.20, 0.63 | yes |
| Lag-1 autocorrelation | 0.3531, -0.1915, 0.0952 | 0.35, -0.19, 0.10 | yes |
| Band coverage | 18 of 26, 69.2308% | 69.2% | yes |
| Clopper-Pearson 95% (my own bisection) | 48.2104 to 85.6740 | 48.2% to 85.7% | yes |
| Design window, ratio E1, E2 | 5.4725, 5.5808 | 5.47, 5.58 | yes |
| Sourced quarters, pace on them | 22, 7.3568 | 22, 7.4 | yes |
| Truncation 30, 60, 90 days (from `serials.csv`) | 13.4682, 22.9287, 31.6719 | 13.5, 22.9, 31.7 | yes |
| By-year table, 7 rows by 5 models | all | all | yes |
| 2023 and 2024: pace, estimate | 12.5149, 3.4817 | 12.5, 3.5 | yes |
| Other 18: pace, seasonal, estimate | 4.4294, 4.4444, 6.4308 | 4.4, 4.4, 6.4 | yes |
| Deliveries per event, mean 2017Q1 to 2025Q2 | 1.1824 | 1.18 | yes |
| Last three quarters | 0.6923, 0.6909, 0.7193 | 0.69, 0.69, 0.72 | yes |
| Sensitivity table, 9 rows by 7 figures | all | all | yes |
| 2026Q3 estimate, band | 31.9532, 21.2334 to 37.2411 | 32.0, 21.2 to 37.2 | yes |
| 2026Q3 miss | 8.0468, 20.117% | 8.0, 20.1% | yes, but see STAT-1 |
| 2026Q3 guidance pace and miss | 33.84, 6.16 | 33.8, 6.2 | yes |
| Same quarter last year, last quarter, raw count | 39 by 1, 41 by 1, 42 by 2 | same | yes |

**Figures on the post and the README's first screen that do not reproduce at the precision shown: none from unrounded inputs. One does not follow from the figures printed beside it: 20.1% (STAT-1).**

## Findings

### STAT-1 (S2). The 20.1% does not follow from the 8.0 and the 40 printed with it

- **Surface.** `docs/LINKEDIN_POST.md:4`; `README.md:6` and `README.md:106`; `report/note.html:56` and `:78` (PDF page 1, key point 2); `docs/INTERVIEW_NOTES.md:30`.
- **Evidence.** `recompute.py`: `AE 8.046791443850267 APE 20.11697860962567` and `displayed: 8.0/40 = 20.0 %`. The estimate is 31.953, shown as 32.0. Each figure is a correct rounding of the unrounded value, but the three printed figures do not agree with each other: 40 less 32.0 is 8.0, and 8.0 over 40 is 20.0%.
- **Why it matters.** It opens the post's second paragraph. This is the one place a reader can check the arithmetic in their head, and it comes out different.
- **Why S2 and not S1.** No figure is wrong: 31.953, 8.047 and 20.117% each round as printed. The fault is that the printed figures do not agree with each other.
- **Fix.** Either "missed by 8.0 (20%)", or carry one more digit throughout: "I said 31.95 ... missed by 8.05 (20.1%)". The first is simpler.

### STAT-2 (S2). The post calls the scaled estimate "the registry count"

- **Surface.** `docs/LINKEDIN_POST.md:6`. Also the note's key point 1 (`report/note.html:55`, PDF page 1), where the clarifier sits a page later.
- **Evidence.** `README.md:30` has a row named "Raw registry count" with an average miss of 6.2. The 5.5 belongs to "Registry estimate (ratio)", `README.md:29`. `README.md:23` explains the wording; the post does not. The dashboard already says "the registry estimate" (`site/app.js:92` to `:95`).
- **Note.** The sentence is fixed by the headline rule (`docs/PREREGISTRATION.md:52`), so the words cannot change. A clarifier can follow them.
- **Why S2 and not S1.** The post's first paragraph says the tracker "scales FAA aircraft registrations into an estimate", so a reader can take "the registry count" as shorthand for it. The reading is open, so I cannot call the sentence false; it misleads once the reader meets the README's "Raw registry count" row.
- **Defensible version.** Keep the sentence and add, as the README does: "Here the registry count means my scaled estimate; the raw count missed by 6.2."

### STAT-3 (S1). "Years to fill in" is false for three held-out quarters

- **Surface.** `docs/LINKEDIN_POST.md:6` ("That test reads a registry copy that had years to fill in"); `README.md:153`; `report/note.html:78` and `:90`. `README.md:8` and `:19` and the note's page 1 say "months or years".
- **Evidence.** `recompute.py`: `min ('2026Q2', 106) max ('2020Q1', 2395)  under 1 year: [('2025Q4', 292), ('2026Q1', 197), ('2026Q2', 106)]` (days from fiscal end to the 2026-10-19 snapshot). The newest held-out quarter had three and a half months.
- **Why S1.** It is a claim the evidence does not support, on the post, and a reader can check it from two dates in the repository. There is no doubt to resolve. It errs on the cautious side, since it makes the backtest sound less like a live test than it is, and the fix is two words. It still fails the rule as written.
- **Defensible version.** "months or years" on every surface, as `README.md:19` has it.

### STAT-4 (S2). "No test finds the registry estimate better than a baseline" covers tests that were not run

- **Surface.** `README.md:8` (first screen); `docs/INTERVIEW_NOTES.md:33` ("no test separates my estimate from any baseline").
- **Evidence.** The project ran three sign tests. My own after-the-fact tests on the same 26 pairs of misses (`check2.py`):

```
last     : mean D 3.284 t 2.227 one-sided p (ratio better) 0.0176 two-sided 0.0352 | Wilcoxon W+ 248.0 one-sided p~0.0334 | sign-flip mean test p~0.0174
block bootstrap (len 4) 95% interval for mean(AE_last - AE_ratio): 0.50 .. 6.03
guidance : mean D 1.394 t 0.917 one-sided p (ratio better) 0.1840
seasonal : mean D -0.908 t -0.753 one-sided p (ratio better) 0.7706
```

  A paired t-test finds the estimate better than the last-quarter rule at the unadjusted 5% level. Under Holm across three it just fails (0.0176 against a first threshold of 0.0167). Against the guidance pace and the same quarter last year, the magnitude tests agree with the sign tests.
- **Why S2 and not S1.** The natural reading is "no test I ran", and on that reading the sentence is true. Under the project's own Holm rule my t-test does not reject either. So I cannot prove the sentence false; I can show it is wider than what was tested. It also undersells the estimate; it does not flatter it.
- **Defensible version.** "None of the three preregistered sign tests finds the registry estimate better than a baseline." If the owner wants the stronger form: "nor does a paired t-test after Holm's correction, tried afterwards."

### STAT-5 (S2). The README's text on the variants stops short of the row that moves the comparison most

- **Surface.** `README.md:49` and `README.md:140`; `results/exploratory/sensitivity.md:17`.
- **Evidence.** The README gives the two alternative readings one at a time: 6.7 with the January 2021 statement read as 117, 6.0 with GD's stated quarter plans. The table's last row applies both: `plans + 117 n 26 5.5234 6.1923 5.7031 ... closer 11 of 26 p 0.8365`. With both, the baseline misses by 5.70 against the estimate's 5.52, and the estimate is closer in 11 of 26. That row is not in the README's text. `README.md:140` then says "Nothing tried after seeing the results has changed the headline", and lists four variants, leaving out both quarter-plan rows.
- **Why it matters.** The sentence is true only because the preregistration forbids a variant from changing the headline. A reader takes it to mean the comparison held up. The 1.4-jet gap in the headline shrinks to 0.2 under two readings of what GD actually said.
- **Defensible version.** "By the preregistration no variant may change the headline sentence. The variants do move the comparison: with GD's stated quarter plans and the January 2021 statement read as 117, the baseline misses by 5.7 against 5.5, and the registry estimate is closer in 11 of 26 quarters." List all eight variants at `README.md:140`.

### STAT-6 (S2). The preregistered guidance rules quote the calls they govern, and the 22-quarter threshold is met exactly

- **Surface.** `docs/PREREGISTRATION.md:45`, `:46`, `:52`; `README.md:49` and `:119`.
- **Evidence.** The preregistration is "cut ... from the build prompt, word for word" (`PREREGISTRATION.md:3`). That text quotes two of the calls it sets rules for: "five to six fewer than the 145" (the wording of the 2023-07-26 row in `data/guidance.csv`) and "$150 million to $155 million" (2025-07-23), and says "The gate pins every row through 2026-07-29". `docs/build/DECISIONS.md:115`: "T3 passes against the gate's 27 pinned calls". So what is shown: the rule text was written with at least two calls' wording in hand, and a checker held a reading of all 27 calls before the build wrote `guidance.csv`. `recompute.py`: `guidance sourced 22`; the rule names guidance first "when at least 22 holdout quarters have a numeric outlook". At 21 the headline would read "against 4.6 for the same quarter last year".
- **What the README says.** `README.md:119` is candid that the counts were in the repository and that the rules were committed two minutes before the scores. It does not say the reading rules quote the transcripts, or that the threshold has no margin.
- **What I could not check.** Whether every call had been read before the rules were written, when the number 22 was chosen, and whether the gate held expected held-out figures before the preregistration commit. The gate is outside the tree I may read; `DECISIONS.md:32` dates it 09:49 on the build day, before the design step at 11:58. I do not say the threshold was tuned. I say a referee will ask, and the README has no answer.
- **Fix.** One sentence in Method, worded to what the owner knows to be true, for example: "The rules for reading GD's calls quote two of the transcripts, so they were written with those calls in hand; a reading of all 27 calls existed before the rules were committed; exactly 22 quarters meet the threshold for naming the guidance pace first." The same-quarter-last-year figure is already in the headline, so the unflattering number is not hidden.

### STAT-7 (S2). The interview notes state the preregistration more strongly than the README does

- **Surface.** `docs/INTERVIEW_NOTES.md:7` ("I fixed the rules on 12 design quarters and committed them before scoring 26 held-out quarters") and `:33` ("I fixed the rules before I scored ... a test that was set up so it could fail").
- **Evidence.** `README.md:119`: "The commit order is all that backs the words 'held out' and 'preregistered' here: the registry counts and GD's counts for every quarter were already in the repository when the definition was chosen, and the rules were committed two minutes before the held-out scores, in the same build session. Only the locked quarters are out of sample in the strict sense."
- **Why it matters.** "Was the held-out data in hand when you wrote the rules?" is the first question a statistician on a panel asks. The notes' answer and the README's answer differ.
- **Defensible version.** Add to the notes: "The held-out quarters' data was already in the repository; the commit order, two minutes apart, is all that separates the rules from the scores. Only the locked quarters are out of sample."

### STAT-8 (S2). A stop rule fired on the design window and was overridden; the README does not say so, and the notes call it preregistered

- **Surface.** `docs/INTERVIEW_NOTES.md:39` ("lower in the early design years than my preregistered sanity check allowed"); `README.md:156`; `docs/build/DECISIONS.md:90` to `:106`.
- **Evidence.** `check4.py`: `PREREGISTRATION.md 'sanity': 0`, `'0.5': 0`, `'§8': 0`. The check is not in the public preregistration. `DECISIONS.md:101`: "Mid cabin falls below 0.5 in 2016 and 2017 under both definitions, which is §8's Phase 2 stop", then `:106`: owner's answer "Keep §3, continue". The README's Coverage limitation gives the figures behind it ("sat above 2 for mid cabin in 2016 and 2017") but not that a stop condition was met and waived.
- **Why it matters.** A choice made after seeing data, on which every later figure rests. It was made on design-window data before any held-out score, which limits the harm; it should still be stated where the method is described.
- **Why S2 and not S1.** The check may have been fixed in advance in the build prompt, which I cannot read, so I cannot show "preregistered" is false. I can show the public preregistration does not contain it.
- **Fix.** One sentence in the README's Coverage limitation, and drop "preregistered" from the notes or point to where the check is written.

### STAT-9 (S2). "The registry had the quarter's jets in time" is more than one quarter shows

- **Surface.** `docs/INTERVIEW_NOTES.md:30`.
- **Evidence.** What the files show (`check2.py`): the 2026Q3 window held 41 events in every daily table from 2026-10-19 to 2026-10-26 and 42 from 2026-10-27 to 2026-11-11. So the count has not moved in the 13 days since the lock. That is all. The 42 events were not matched to GD's 40 deliveries, and `README.md:157` says 5 of the 42 were airframes at least three years old. `README.md:153` says processing "can lag by months".
- **Supporting context the notes could use instead.** Archived copies taken 23 to 29 days after three recent quarter ends held 40, 54 and 55 of the quarter's own events, against 38, 55 and 57 in the 2026-10-19 copy (`check2.py`, as-of rows). That is three more quarters where the count at lock time was close to the later count.
- **Why S2 and not S1.** The claim may be right, and the as-of rows lean its way. I cannot prove it wrong; one quarter and 13 days cannot prove it right.
- **Defensible version.** "The count for the quarter stood at 42 at the lock and has not changed since, so late postings do not explain the miss so far. I have not matched those 42 events to GD's 40 deliveries."

### STAT-10 (S2). The post and the README's first screen use the band without its level or its backtest coverage

- **Surface.** `docs/LINKEDIN_POST.md:4` ("outside my band of past misses"); `README.md:6`.
- **Evidence.** The band is a nominal 80% band that held 18 of 26 (`README.md:51`), stated in Results, Limitations, the note and the dashboard, but not where the band is first used to describe the miss. Also from `recompute.py` and `check3.py`: `lock abs miss rank ... held-out only: 7` (six of the 26 held-out misses were larger than 8.0), and `live band width: 16.01 below est: 10.72 above est: 5.29`. The band sits mostly below the estimate because past misses ran high, and GD's count came in above.
- **Why it matters.** A reader cannot tell how surprising "outside the band" is. With a band that held 69% of the time, one miss in three falls outside.
- **Defensible version.** README first screen: "(80% band 21.2 to 37.2; in the backtest it held 18 of 26)". The post has less room; "outside my 80% band of past misses" is enough.

### STAT-11 (S3). "Nominal 80%" overstates what the band was built to hold in the backtest

- **Surface.** `README.md:51`, `:160`; `report/note.html:71`; `site/app.js:386`.
- **Evidence.** With n past errors, a band from the nearest-rank 10th and 90th percentiles holds a new exchangeable error with probability (ceil(0.9n) - ceil(0.1n)) / (n + 1). `recompute.py`: `[(12, 69.2), (13, 71.4), ... (19, 80.0), (20, 76.2), ... (37, 78.9)]`, `mean expected coverage over the 26 quarters: 76.37  expected hits: 19.85`. So 18 hits compares with about 19.9 expected, not 20.8. `P(hits<=18 | p=0.80): 0.1313`, `P(hits<=18 | p=mean nominal): 0.258`. The shortfall is not statistically distinguishable from nominal under either figure, which no surface says; the interval printed (48.2% to 85.7%) contains 80%.
- **Defensible version.** "against a nominal 80%, or about 76% once the small number of past misses is allowed for; the shortfall is within what 26 quarters can show by chance."
- **Related.** "likely too narrow at a live lock" (`note.html:78`, `:96`; `INTERVIEW_NOTES.md:24`) is a fair hedge but rests on one lock and a shortfall of two quarters. The README's "may not fit" (`:160`) is the better wording.

### STAT-12 (S3). "Its miss came from the scale, not from late postings" is half identity

- **Surface.** `README.md:92`; `docs/INTERVIEW_NOTES.md:30`; `report/note.html:78`.
- **Evidence.** The arithmetic is right: 25 days, 42 events, `trailing deliveries per event: 0.7581`, `quarter itself: 0.9524`. But with the count fixed, the miss is the scale's by construction: the realised ratio always "explains" the gap. The evidence-bearing half is "not from late postings", and it holds for 13 days so far (STAT-9). Also the 0.76 is pooled across cabins; the model scales each cabin: `large-only trailing 0.7487 ... mid-only trailing 0.8214 ... large q 1.0 mid q 0.7143`, `per-cabin miss: large -8.797 mid 0.75`. The whole miss was large cabin.
- **Defensible version.** "No event dated in the quarter has posted since the lock, so late postings explain none of the miss so far. The miss was in large cabin: the four quarters before gave 0.75 large-cabin deliveries per event, and the quarter came in at 1.00."

### STAT-13 (S3). The truncation paragraph says the table is not a model of a lock but not why

- **Surface.** `README.md:83` to `:92`.
- **Evidence.** The table drops events dated in the last 30, 60 or 90 days of the quarter. A lock reads the file about 25 days after the quarter ends, so no row of the table describes it. The dashboard says this in one clause: "which is made weeks after the quarter ends" (`site/index.html:74`). The README gives the 2026Q3 facts and leaves the reader to infer the reason. Two more things the table hides: at 90 days the model predicts about one aircraft (`cut 90 days: MAE 31.6719  mean estimate 1.02  mean reported 32.69`), so the bottom row is GD's average quarter, not a measured lag; and the as-of rows are the direct evidence on lag (STAT-9), which the paragraph does not cite.
- **Fix.** Add the dashboard's clause, and point to the as-of table for what a file looks like 23 to 29 days after a quarter.

### STAT-14 (S3). Deliveries per registry event: two kinds of average, and a drift sentence that leans on a long-run mean

- **Surface.** `README.md:81`, `:92`, `:156`; `report/note.html` coverage-drift paragraph; `site/app.js:393`.
- **Units and direction.** Right on every surface: deliveries over events; the flag fires on high values, which mean fewer events per delivery; a fall means more events per delivery.
- **Averages.** The 1.18 is the mean of 34 quarterly ratios. The same window pooled is `1.1048`. The other figures for this quantity are pooled: 1.92 and 1.26 by year (`2016 pooled 1.921`, `2019 pooled 1.256`), and the lock's 0.76 over four quarters. The README does not say which is which.
- **The drift sentence.** "0.69, 0.69, 0.72 against the 1.18 mean ... more events per delivery than usual". True against that mean. But the series fell for a decade (yearly pooled: 1.54, 1.51, 1.26, 1.35, 1.04, 0.88, 0.95, 0.92, 0.82 for 2017 to 2025), so "usual" for recent years is about 0.8 to 1.0. `mean-2sd 0.4792`: the three quarters sit 1.3 to 1.4 standard deviations below the mean (`check6.py`: 1.39, 1.4, 1.32), inside two, so a two-sided version of the flag would not have fired either. "The flag is one-sided: it cannot fire on a fall" reads as if it would have. Only `2022Q1` (0.658) is lower in the baseline window. And the first live quarter came in at 0.95, which the next paragraph says but this one does not.
- **Defensible version.** "The last three held-out quarters sit at 0.69, 0.69 and 0.72, the lowest run in the series and below the 0.8 to 1.0 of 2022 to 2025. They are within two standard deviations of the 2017Q1 to 2025Q2 mean of 1.18 (a mean of quarterly ratios), so no two-sided flag would fire either. The first live quarter came in at 0.95."

### STAT-15 (S3). The headline's test is on who was closer, not on the difference in average miss

- **Surface.** `README.md:21`; post line 6; note page 1.
- **Evidence.** "5.5 against 6.9. The difference is not statistically distinguishable" rests on a sign test of 14 of 26. A sign test does not test a difference of means. My magnitude tests agree (STAT-4: t 0.917, block-bootstrap interval -2.37 to 5.55), so the sentence stands. Separately, no surface says that the same-quarter-last-year rule's lead is not distinguishable either: `reverse sign test: seasonal AE lower than ratio: wins 15 of 26 p 0.2786`, paired t -0.753. "Missed by least" (`README.md:8`) is a fact about the sample, not an established ranking.
- **Fix.** README Results: "A paired t-test on the misses, tried afterwards, agrees. The same quarter last year's lead over the registry estimate is not distinguishable either (15 of 26)."

### STAT-16 (S3). The autocorrelation sentences

- **Surface.** `README.md:47`; `site/app.js:377`.
- **Evidence.** The README calls the last-quarter differences "positively autocorrelated" at 0.10, then says only the 0.35 is more than one standard error (0.196) above zero. The second sentence is right and none of the three is two standard errors from zero. The dashboard prints "positively correlated (0.10), which makes the sign test less reliable" with no such caveat. The autocorrelation is of the differences' sizes; a sign test uses their signs, whose lag-1 values are `0.265`, `-0.380`, `0.063` (`check2.py`). No conclusion changes, since nothing rejects.
- **Fix.** Dashboard: print the caveat only above one standard error, or add "about 0.20 is one standard error".

### STAT-17 (S3). "The choice decided little" is true of the average, not of the count

- **Surface.** `README.md:53`; `results/exploratory/sensitivity.md:15`.
- **Evidence.** Average miss 5.47 under E2 against 5.52: right. But `E2 ... closer 17 of 26 p 0.0843` against 14 of 26, p 0.423 under E1. Three quarters change sides (`check7.py`):

```
FLIP 2022Q4: E1 miss 3.254 E2 miss 2.939 guidance miss 3.000 | own-quarter count E2-E1 +0, four-lag count E2-E1 +1
FLIP 2025Q3: E1 miss 6.802 E2 miss 5.488 guidance miss 5.986 | own-quarter count E2-E1 +2, four-lag count E2-E1 +2
FLIP 2026Q2: E1 miss 3.810 E2 miss 2.501 guidance miss 3.722 | own-quarter count E2-E1 +0, four-lag count E2-E1 +6
```

  They flip on count differences of one to six airframes in the quarter or its four lags, because five quarters are within one aircraft of a tie against the pace under E1: `[('2020Q4', 0.29), ('2021Q2', 0.28), ('2022Q4', -0.25), ('2025Q3', -0.82), ('2026Q2', -0.09)]`. Neither p rejects, so no conclusion changes. It does show how little a win count on 26 quarters pins down.
- **Fix.** Add "(under E2 the estimate is closer than the pace in 17 of 26, p 0.084; still not rejected)".

### STAT-18 (S3). What the sensitivity table lacks

- **Surface.** `results/exploratory/sensitivity.md`; `README.md:49`.
- **Labelling.** Good. Line 3 says "Tried after the held-out results were seen" for the whole table, and row 1 is named as the preregistered comparison. One row is mislabelled in the cautious direction: the averages without 2020 are a preregistered secondary figure (`PREREGISTRATION.md:51`); only that row's sign test is after the fact.
- **Missing, in the order a referee would ask.**
  1. The test against the baseline that wins. The table's last two columns are against the guidance pace only. `sensitivity.json` already holds `ratio_vs_seasonal` for every row; the table does not print it. Mine: 11 of 26 (p 0.837) preregistered; 9 of 22 without 2020; 6 of 18 without 2023 and 2024; 5 of 8 in 2023 and 2024; 12 of 26 under E2.
  2. The 22 sourced quarters alone, the like-for-like comparison with the pace: `ratio 5.2503 guidance 7.3568 seasonal 4.6364`, `closer 13 of 22 p 0.2617`. The note prints the three averages (`note.html:71`); the README prints only the pace's 7.4.
  3. A test on the size of the misses (STAT-4).
  4. Another loss. Median miss and root mean square both keep the order (`median AE ratio 4.220 ... seasonal 3.000`; `RMSE 6.935 ... 6.076 ... guidance 8.865`), so this would be a clean row.
  5. Leave-out of the largest misses, since the README says five quarters drive much of the average (they are 44.2% of the total): `drop ratio's top 3: ratio 4.391 seasonal 4.957`. The ranking against the same quarter last year turns on three quarters.

### STAT-19 (S3). "If public registrations cannot beat the company's own outlook, they add little"

- **Surface.** `docs/INTERVIEW_NOTES.md:18`.
- **Evidence.** Beating a forecast and adding to it are different questions; the second is tested by combining forecasts. My own after-the-fact check (`check3.py`), untested and on 26 quarters: `mean of ratio and seasonal: MAE 4.132` against 5.523 and 4.615 alone; correlation of the two signed errors 0.297. I am not proposing this for any surface. It is the follow-up a panel statistician will ask, and the notes' sentence gives the wrong answer to it.
- **Defensible version.** "If registrations cannot beat the company's own outlook on their own, the next question is whether they add anything in combination, which I have not tested."

### STAT-20 (S2). The lock explanation's conclusion is fixed text, and no test names it

- **Surface.** `src/gdn/report.py:252` to `:263`, which writes `README.md:92`.
- **Evidence.** The generator counts the quarter's events in each later daily table. When every later count equals the count at the lock it prints "it is the same in every daily snapshot since" (`report.py:254`); otherwise it prints "and it stands at N in the <date> snapshot" (`:256`). The next sentence is not conditional: "Its miss came from the scale, not from late postings" (`:261` to `:262`) prints in both cases. `grep -rn -E 'late postings|stands at|same in every daily' tests src/gdn` finds only those three lines of `report.py`, so no test names either branch's text.
- **Why it matters.** If one more 2026Q3 event posts, the next rebuild will say in one breath that the count changed and that the miss did not come from late postings. That would be a stale sentence about the live record, written by the job with nobody looking. The count has been flat for 13 days, so it has not happened. The 2026Q2 lag did lose an event on 2026-11-03 (57 to 56), so these counts are not frozen.
- **Why S2 and not S1.** Nothing printed today is wrong. It is an untested path to a public sentence.
- **Fix.** Print the conclusion only on the "same in every snapshot" branch. On the other branch print the two counts and the two scales and draw no conclusion. Add a test for each branch. STAT-12 gives the wording I would use.

## Q2. Every statistical sentence

README Results and Error analysis, and the note's pages 1 and 2 (same sentences).

| Sentence | Right statement, direction, denominator? |
|---|---|
| `README:21` "5.5 ... against 6.9 ... not statistically distinguishable" | Right. 26 stated. Test is a sign test, not a test of the averages (STAT-15). |
| `README:21` "same quarter last year missed by less on average, 4.6" | Right. |
| `README:8` "missed by least. No test finds ..." | First half right for the sample. Second half too wide (STAT-4). |
| `README:8`, `:19` "months or years to fill in"; post line 6, `README:153` "years" | The first is right. The second is false for three quarters (STAT-3). |
| `README:35` bias and average % miss definitions | Right. Mean of quarterly percentages 17.915; pooled would be 16.895. Stated as the mean of quarterly shares, so no issue. |
| `README:37` to `:43` sign-test table | Right. One-sided, direction "registry closer", ties shown, Holm column right. |
| `README:45` relative miss | Right. |
| `README:47` autocorrelation | Right in the second sentence; first sentence loose for 0.10 (STAT-16). 1 over root 26 is 0.196. |
| `README:49` 22 of 26; pace 7.4 on the 22; 6.7 and 13 of 26; 6.0 and 12 of 26; 43.1 for 2023Q3 | All right (7.3568; 6.6567, 13; 6.0184, 12; 43.074). Omits the combined row (STAT-5). |
| `README:51` band 18 of 26, 69.2%, 48.2% to 85.7% | Right. "Nominal 80%" see STAT-11. |
| `README:53` design window 5.47, 5.58, 5.00, 3.83; 11 of 12 quarters agree; one airframe in 2019Q4; 5.47 against 5.52 held out | All right. "Decided little" see STAT-17. |
| `README:69` 12.5 and 3.5; 4.4, 4.4, 6.4; pace closer in each of the last five | All right. 2026Q2 is close: 3.722 against 3.810. |
| `README:81` 1.18; flag direction; 0.69, 0.69, 0.72 | Right. See STAT-14. |
| `README:83` to `:92` truncation and the lock | Arithmetic right. See STAT-12, STAT-13. |
| `README:94` five quarters drive much of the average | Right: 44.2% of total absolute miss. |
| `README:136` as-of: all four missed by less; band held two of three; 206 against 203; 146 against 63 | All right (`check5.py` rebuilds the four estimates exactly). "Four quarters prove nothing" is the right weight. |
| Note page 2 "On those 22 quarters ... 7.4 ... 5.3 ... 4.6" | Right (7.3568, 5.2503, 4.6364). |

## Q3. The sensitivity table

Labelled as after the fact as a whole (line 3). All nine rows reproduce. The README's text says less than the table in one place that matters (STAT-5) and "decided little" hides a 14 to 17 move in the count (STAT-17). Missing variants: STAT-18.

## Q4. The band

Described consistently as a band of past misses, never as a confidence interval. Coverage and interval are right and are in the README Results and Limitations, the note and the dashboard. Missing where the band is first used (STAT-10). "Nominal 80%" is about 76% as built (STAT-11). The one live quarter is stated plainly as outside on every surface.

## Q5. One live quarter

Claims from n = 1, by surface:

- Post, README first screen, Live record, note page 1, resume bullet: a miss of 8.0, outside the band, with the pace, last year, last quarter and raw count beside it. All computed correctly (table in Q1). "One quarter is one data point" (post). Within what one quarter carries.
- `README:92`, note, interview notes: the miss "came from the scale, not from late postings". Partly an identity (STAT-12).
- `INTERVIEW_NOTES:30`: "the registry had the quarter's jets in time". Too much (STAT-9).
- `README:160`, note: the band "may not fit" or is "likely too narrow" live. A hedge, acceptable; one lock adds almost nothing to it (STAT-11).
- `README:69`: "the guidance pace has been closer in each of the last five quarters, the locked one included". Right, and correctly a count, not a claim.

Nothing claims the method works or fails on the strength of the one quarter. Good.

## Q6. The truncation table and the lock

The text now says the table is not a model of a live lock, and its four figures are right: 25 days from 2026-10-04 to 2026-10-29; 42 events; unchanged in every daily table to 2026-11-11 (it was 41 until 2026-10-26); 163 over 215 is 0.758; 40 over 42 is 0.952. What is thin is the reason (STAT-13) and the word "scale" (STAT-12), and the conclusion would survive a change in the count (STAT-20). One more fact from the daily tables worth a line: the 2026Q2 lag lost an event on 2026-11-03 (57 to 56), so trailing counts move after a lock too.

## Q7. Deliveries per registry event

Units and direction right everywhere. The drift sentence is true against the 1.18 mean and says a little more than the data: "than usual" ignores the decade-long fall, the wording implies a two-sided flag would have fired, and two kinds of average are mixed (STAT-14).

## Q8. Forking paths

Choices a surface relies on, and whether each is disclosed where it is used.

| Choice | When made | Disclosed where used? |
|---|---|---|
| E1 over E2 | Design window, preregistered | Yes (`README:53`), with both figures. Count effect not in text (STAT-17). |
| Rules for reading GD's calls; "same sentence" rule | In the build prompt, which quotes two of the calls | Partly. The 2021 reading is disclosed with its effect. That the rule text quotes the transcripts is not (STAT-6). |
| 22-quarter threshold for naming guidance first | In the build prompt; met exactly; timing against the reading not checkable | No (STAT-6). |
| Pace ignores GD's stated quarter plans | Preregistered; plans found after | Yes (`README:49`, notes, table). |
| Four of the 26 "guidance" quarters are the same quarter last year | Preregistered fallback | Yes in Results and the note; not on the post or first screen. Acceptable: on the 22 the pace is worse (7.4), so the headline is the cautious one. |
| Continue after the design-coverage stop | After seeing design-window coverage | Only in build notes and interview notes (STAT-8). |
| Sign test, Holm, one-sided; band percentiles; truncation days; drift flag one-sided | Preregistered | Yes. |
| Split at 2023 and 2024 in Error analysis | After the by-year table | Described as what it is ("the two years the guidance pace missed by most") in the sensitivity table; in `README:69` it is descriptive and makes no test claim. Acceptable. |
| "Without 2023Q1 to 2024Q1" row | After | Labelled. |
| Five largest misses | After | Descriptive. Acceptable. |
| "Drift runs the other way" | After; the preregistered flag looked up only | Stated as an observation beside the flag. Acceptable, wording in STAT-14. |
| Comparisons printed beside the lock (last year, last quarter, raw) | After the score; only the pace is in the preregistered score file | All three are unflattering and labelled "other misses". Acceptable. |
| The lock explanation (scale, not late postings) | After the score | Stated as fact; should be hedged (STAT-12), and its conclusion is fixed text (STAT-20). |
| Used-jet threshold of three years; audit sample of 30 | After | In Limitations only; no headline relies on them. |
| As-of window of 20 to 30 days | Preregistered as secondary | Yes. I could not check whether capture dates were known when the window was set. |

## Q9. Averages and rounding

- No average of rounded values found: every printed average matches the unrounded mean.
- One percentage that does not follow from the figures printed with it: 20.1% (STAT-1).
- One quantity averaged two ways: deliveries per event (STAT-14).
- Average % miss is a mean of quarterly percentages (17.9%), and the README says so. Pooled it would be 16.9%. No issue.
- Precision: the headline is at one decimal (5.5), the design window, by-year table and sensitivity table at two (5.52). The figures agree. The large-cabin and mid-cabin misses (5.0 and 2.2) do not add to the total (5.5) because cabin errors offset; a half-sentence would save a reader the question.
- "Without 2020" 5.4 (README table) and 5.35 (sensitivity): both right roundings of 5.3509.
- Note, live section: "32.0 (26.2 large, 5.8 mid)" adds up as printed.

## Interview notes: what a statistician on a panel would call wrong

1. Lines 7 and 33: the preregistration claim without the README's caveat (STAT-7).
2. Line 33: "no test separates my estimate from any baseline" (STAT-4).
3. Line 30: "the registry had the quarter's jets in time" (STAT-9), and "what missed was my scaling" (STAT-12).
4. Line 39: "my preregistered sanity check", which the public preregistration does not contain (STAT-8).
5. Line 18: "cannot beat ... add little" (STAT-19).
6. Line 24: the band "held GD's count in 18 of 26" with no level given; say "an 80% band".
7. Line 33: "Every number in it traces to a filing or a registry file." The guidance outlooks come from call transcripts on Motley Fool and MarketBeat (`README.md:146`), which are neither.
8. Line 13: "about two deliveries per event in 2016" (1.92 pooled) and "0.72 in 2026Q2" are right.

## What is right

- All 650 cells of `results/holdout.csv`, every figure in `metrics.json` I rebuilt, and all nine sensitivity rows match my independent code to the last digit.
- The sign tests are computed and stated in the right direction, with ties and Holm handled as preregistered.
- The Clopper-Pearson interval is right.
- The lock file's sha256 equals the one in `2026Q3_lock.json` and in the release notes; the release shows `published: 2026-10-29T05:51:24Z`, which is 01:51 ET, before the release date.
- The 2026Q3 estimate, band, miss, guidance pace (160 less 79 reported, times 0.2321 over 0.5556, is 33.84) and the three other comparisons all rebuild from the files.
- The truncation table rebuilds from `serials.csv`, and `serials.csv` reproduces every quarterly E1 count (0 mismatches over 42 quarters and two cabins).
- The daily airframe tables back "the same in every daily snapshot since, to 2026-11-11".
- The as-of estimates rebuild from their own rows; the weight put on them ("four quarters prove nothing") is right.
- The headline names the baseline that wins. The README says the pace is the author's construction, gives its sourced count, the 2021 reading and the quarter plans, and admits the commit order is all that backs "held out". That is more candour than most forecasting write-ups carry.
- "No held-out quarter had fewer than 3 mid-cabin deliveries": right (minimum 3, in four quarters).

## What I could not check

- GD's reported 40 (35 large, 5 mid) against the SEC release; I took `2026Q3_score.json` as given.
- Commit order and the "two minutes" (no git history in the copy).
- The gate, and whether it held expected held-out figures before the preregistration (outside my tree).
- The workbook's formulas, the PDF beyond pages 1 and 2, and the dashboard as rendered. I read `app.js` text only.
- Most of `src/gdn/report.py` (549 lines). I read two windows and grepped the rest; a fixed sentence elsewhere in it could go stale the way STAT-20 describes.
- The tests. I may not run `pytest`; STAT-20's "no test names it" rests on a grep of `tests/`.
- Whether the snapshot counts for 2026Q3 will stay at 42 after 2026-11-11.
