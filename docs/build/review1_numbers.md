# Review round 1: numbers reader

Reviewer: fresh reader, built nothing here. Brief: `docs/build/briefs/review1_numbers.md`. Read against HEAD `1d7df03` (2026-10-19 12:06 CDT; the README's Audit bullet arrived in `062e00e` while this review ran). Spec: §2, §3.4 and §4 of `GULFSTREAM_NOWCAST_PROMPT.md`.

Surfaces read: `README.md`, `docs/LINKEDIN_POST.md`, `docs/RESUME_BULLETS.md`, `docs/INTERVIEW_NOTES.md`, the text of `report/note.html` (tags stripped), and the page at http://127.0.0.1:8766/ as rendered (`document.body.innerText` and the three canvas `aria-label`s), with `site/app.js` read against `site/data.json`.

Line numbers are file lines. `note.html` keeps each paragraph on one line, so a note line can hold several sentences.

## Recomputed with `.venv/bin/python` (all match the files)

- Holdout MAE of all five models from `results/holdout.csv`: ratio 5.523, raw 6.192, guidance 6.917, seasonal 4.615, last 8.808. MAE without 2020: 5.351, 5.818, 7.406, 4.455, 8.682.
- Sign tests from the AEs: guidance 14/12/0, p = 0.4225; seasonal 11/15/0, p = 0.8365; last 16/10/0, p = 0.1635. The smallest p is above 0.05/3, so Holm rejects none.
- Past-miss band by quarter, rebuilt from `band_errors` by nearest rank: every low, high and hit matches `metrics.json`. 18 hits. Clopper–Pearson by bisection: 48.21% to 85.67%.
- Truncation MAE rebuilt from `serials.csv`, `registry_quarterly.csv` and `gd_deliveries.csv`: 5.523, 13.468, 22.929, 31.672.
- Live band: P10 = −5.288 and P90 = 10.720 over 38 errors, so the band is [20.41, 36.42] around 31.13.
- Guidance pace for 2026Q3: (160 − 79) × 94 / (94 + 131) = 33.84.
- "About 33" a quarter: 850 / 26 = 32.69. Pipeline: 270 airframes, and 270 / 32.69 = 8.3 quarters.
- `site/data.json`: `metrics` equals `metrics.json`; `estimates` equals `estimates.json` without `basis`; every `backtest` total equals its `design.csv` or `holdout.csv` row.
- Segments: the shares (25.2, 32.7, 17.1, 25.1%), the TTM margins, Exhibit 8's changes and percents, H1 2026 deliveries of 79, the Aerospace margin (14.5% in Q2, 14.7% in H1), the Marine margins (7.1, 7.2, 7.3, 7.3%), and the sensitivity rows.
- README Limitations, Coverage: 63/121 = 0.52 (2016) and 117/147 = 0.80 (2019); mid cabin 10/27 = 0.37 and 14/30 = 0.47.

## Brief checks

- **"Beat."** No sentence on any surface says the registry estimate beat a baseline. Holm rejects for none of the three; relative MAE is 0.80, 1.20 and 0.63. `app.js` `beats()` returns an empty list, so the tiles get no accent and the lead takes the null branch. The headline and null sentence match §3.4 on all five surfaces, with guidance named first (22 sourced quarters, so `headline: true`).
- **"Counts jets before GD reports them."** No surface claims it. The closest is README L3, "I estimate how many Gulfstream jets General Dynamics (GD) will report delivering", which is a claim about an estimate. §2's framing sentence appears in the README, the note, the interview notes and the dashboard, and the post has a close variant.

## Findings

### Major

**N1. The as-of explanation runs opposite to the as-of data.**
- Where: `README.md` L121; `report/note.html` L71.
- Severity: major.
- Evidence: README L121 says "Reading the lags from the same unfinished file seems to offset part of what has not posted". The note says the archived copies "missed by less than the finished copy, because they read the lag quarters from the same unfinished file."
  - `results/exploratory/asof.csv` against `data/processed/registry_quarterly.csv` (E1, large + mid). Columns: archived copy's lag events, finished copy's lag events, archived copy's own-quarter events, finished copy's own-quarter events.

    | Quarter | Archived lags | Finished lags | Archived own | Finished own |
    |---|---|---|---|---|
    | 2017Q1 | 146 | 63 | 40 | 19 |
    | 2025Q3 | 184 | 176 | 40 | 38 |
    | 2026Q1 | 197 | 192 | 54 | 55 |
    | 2026Q2 | 206 | 203 | 55 | 57 |

  - In all four quarters, the archived copy holds more lag events than the 2026-10-19 copy, not fewer.
  - In two quarters it also holds more of the quarter's own events, and in the other two it is short by only one or two.
  - "Unfinished" and "has not posted" imply the early file is missing records. The data says the opposite: the later file has lost records, which fits the README's own Coverage limitation (resales overwrite first-owner certificates).
  - The as-of estimates came out lower mainly because their denominators were larger. With ratio's +2.2 holdout bias, a lower estimate lands closer.
- Fix:
  - Drop the causal clause in the note ("because they read the lag quarters from the same unfinished file").
  - In the README, replace the "unfinished file" sentence with what the files show: "The archived copies held more events for the four lag quarters than the 2026-10-19 copy does (for example 206 against 203 for 2026Q2, and 146 against 63 for 2017Q1), so the later file has lost first-owner records since. Their estimates came out lower and, given the model's upward bias, closer."
  - Give the same correction to `results/exploratory/asof.md` L12 ("so it is the harsher test").

**N2. The README's audit breakdown misreads `docs/build/AIRFRAME_AUDIT.csv`.**
- Where: `README.md` L144; `report/note.html` L95.
- Severity: major.
- Evidence: README L144 reads "five were used jets that a fresh US airworthiness date let through as new deliveries, one military jet was delivered a quarter earlier than its registry date, and four could not be confirmed. Every source was a registry mirror or aircraft-history site". The ten rows with `agree = no`, read against `serials.csv`:
  - Four used jets let through by a fresh airworthiness date: 4076 (airworthiness 2016-01-22, built 2007), 4122 (2016-11-17, built 2008), 5269 (2017-08-23, built 2010) and 5340 (2018-07-03, built 2011).
  - One used jet with no date at all: 466, a 1985 GIII. `first_airworthiness` and `year_mfr` are both blank, so `bound` is blank. No fresh airworthiness date let it through; the missing bound did. That is the README's "Used jet" limitation, a different mechanism.
  - One new jet whose source dates delivery earlier: 6270, a G650ER built in 2017. The registry date is 2018-03-09; the source says "Delivery Date 2017-09-22", two quarters earlier. The note column reads "conflict unresolved, so no". The README puts it in none of its three groups, since "four could not be confirmed" only adds up if it is counted there.
  - One military jet: 571, a USAF C-37A, dated 2000Q1 against 2000Q2. That is its E2 date (`event` = "only under E2"); E1 gives it no event.
  - Three unconfirmed: 72023, 5467 and 2177, all "removed by the bound".
  - `source_kind` counts 29 `mirror` and 1 `release` (row 571 cites a GD release dated February 21, 2000). So "Every source was a registry mirror or aircraft-history site" is false; the note's "every source was a registry mirror or aircraft-history site" (L95) is false for the same reason.
  - The totals are right: 10 of 30, 33.3%.
- Fix:
  - README: "In 10 of 30 (33.3%) the source disagreed with the registry reading or could not confirm it: five were used jets (four let through by a fresh US airworthiness date, one with no airworthiness date or year at all), two had a stated delivery earlier than the registry date (a military G-V by one quarter, under E2 only, and a G650ER by two), and three could not be confirmed. All but one source was a registry mirror or aircraft-history site."
  - Note L95: change "every source" to "all but one source".

**N3. The interview notes call the coverage ratio "fairly steady".**
- Where: `docs/INTERVIEW_NOTES.md` L13.
- Severity: major.
- Evidence: L13 says "Counting those dates by quarter gives a number that runs above or below GD's count by a fairly steady ratio". In `metrics.json` `holdout.coverage_ratio.by_quarter`:
  - The ratio of reported deliveries to registry events falls from 2.33 (2016Q1) and 2.25 (2016Q2) to 0.69 (2025Q4), 0.69 (2026Q1) and 0.72 (2026Q2).
  - Over 2017Q1 to 2025Q2 the sample sd is 0.35 around a mean of 1.18.
  - README L141 says of the same quantity "It drifted", and INTERVIEW_NOTES L30 itself describes the drift.
- Fix: "Counting those dates by quarter gives a number that tracks GD's count, though not one for one, and the gap drifted from about two deliveries per event in 2016 to about 0.7 in 2026. So I scale this quarter's count by the last four quarters' ratio, which follows the drift."

**N4. The resume bullet says locks and scores happened. None exist.**
- Where: `docs/RESUME_BULLETS.md` L2.
- Severity: major.
- Evidence: the bullet opens "Locked each live quarter's estimate on GitHub as a timestamped release ... then scored it from GD's SEC filing". But `ls predictions` returns "No such file or directory", `results/live/` holds only `2026Q3_build.json`, `_latest.json` and `_path.csv`, and README L92 says "not locked yet". The trailing "the first lock is scored on 2026-10-30" contradicts the opening verbs. A recruiter reads the bullet as work done.
- Fix: "Built a daily job that locks each quarter's estimate on GitHub as a timestamped release carrying its sha256 before GD reports, and scores it from GD's SEC filing; the first lock, for 2026Q3, is scored when GD reports on 2026-10-30." Update it to past tense only after `results/live/2026Q3_lock.json` exists.

### Minor

**N5. Yearly tables round exact halves to the even neighbour.**
- Where: `README.md` L51–57; `report/note.html` L72 (Exhibit 5).
- Severity: minor.
- Evidence: the yearly means are averages of four integer errors, so several sit exactly on .x5.
  - Rounded down: raw 2020 8.25 → "8.2", raw 2021 3.25 → "3.2", seasonal 2022 2.25 → "2.2", seasonal 2024 6.25 → "6.2", last 2021 9.25 → "9.2", last 2022 8.25 → "8.2".
  - Rounded up in the same table: seasonal 2023 3.75 → "3.8", last 2023 8.75 → "8.8".
  - A reader who recomputes gets 8.25 and expects 8.3. The page's `f1` rounds half up, so the same value would print differently on the dashboard.
- Fix: print these tables with two decimals, which the gate accepts, or round half up in `note.py` and the README writer.

**N6. The 2026 row averages two quarters without saying so.**
- Where: `README.md` L57; `report/note.html` L72.
- Severity: minor.
- Evidence: row "2026 | 5.6 | 16.5 | 4.9 | 2.5 | 5.0". `holdout.csv` has only 2026Q1 and 2026Q2. Raw's 16.5 is the mean of 2 errors (16 and 17), set beside four-quarter years.
- Fix: label the row "2026 (Q1–Q2)" or add a note: "2026 has two quarters."

**N7. The note's eve date can be read as 2026-10-30.**
- Where: `report/note.html` L75.
- Severity: minor.
- Evidence: "the locked estimate replaces it on the eve of the release, 2026-10-30." The appositive can attach to "the eve". `config/calendar.json` has release 2026-10-30, so the eve is 2026-10-29.
- Fix: "replaces it on 2026-10-29, the eve of the 2026-10-30 release."

**N8. "The evening before" misstates when the lock can fire.**
- Where:
  - `README.md` L92 and L106
  - `docs/INTERVIEW_NOTES.md` L9 and L27
  - `docs/RESUME_BULLETS.md` L2
  - `site/app.js` L136 ("Locks: the evening of 2026-10-29"), L144 and L259
  - `site/index.html` L98
- Severity: minor.
- Evidence: `src/gdn/live.py` L241–243 reads `if t.date() != eve: return False` and `return newest_snapshot == eve.isoformat() or t.hour >= LOCK_HOUR_ET`. A run on 2026-10-29 that holds a snapshot dated 2026-10-29 locks at any hour, for example the Mac's morning run or the runner's 12:17 UTC run. §3.6 says "on the release date's eve", meaning the day, not the evening.
- Fix: write "on the day before GD reports" (README L3 already does), or "on 2026-10-29, the eve of the release".

**N9. "Hardest to beat" is unqualified, and the note's own figures contradict it at four quarters.**
- Where: `README.md` L108; `report/note.html` L82.
- Severity: minor.
- Evidence: "the baseline my defense backlog study found hardest to beat". The same note paragraph gives four-quarter MAPEs of "5.8% for trailing revenue and 6.0% for trailing revenue with drift", so drift was not best four quarters out. §2 calls it "the study's best next-quarter baseline".
- Fix: "the study's best next-quarter baseline, the seasonal naive with drift (6.5% against 7.3% without drift and 9.9% for backlog)".

**N10. The coverage-drift sentence reads only the side that cannot fire.**
- Where: `README.md` L69; `report/note.html` L72 (the "Coverage drift:" sentence); `site/app.js` L363.
- Severity: minor.
- Evidence: README L69 reads "No quarter from 2025Q3 to 2026Q2 sits above the mean plus two standard deviations, so the latest quarters show no sign that the registry is counting fewer jets per delivery than usual." The figure is read right, since the flag is one-sided by §3.4. But the window's values are 1.03, 0.69, 0.69 and 0.72 against a mean of 1.18 and sd of 0.35. The last three sit about 1.3 to 1.4 sd below the mean, among the lowest in the series (only 2022Q1 is lower, at 0.66). So the registry is counting more events per delivery than usual. A reader takes "no sign" to mean stable.
- Fix: in the README and the note, add "The last three sit at 0.69 to 0.72, below the 1.18 mean: the registry is counting more events per delivery than usual, which the ratio's trailing scale absorbs only with a lag."

**N11. The first resume bullet quotes only the guidance comparison and drops the framing.**
- Where: `docs/RESUME_BULLETS.md` L1.
- Severity: minor.
- Evidence: "tested on 26 held-out quarters against GD's guidance and naive baselines; off by 5.5 jets a quarter vs 6.9 for guidance, not significant". The post (L5) and the interview notes (L7) both add that the same quarter last year did better, at 4.6; the bullet does not. It also carries nothing of §2's after-the-fact framing, which §2 asks for "everywhere".
- Fix: "...off by 5.5 jets a quarter vs 6.9 for GD's guidance and 4.6 for last year's same quarter, no difference significant, on a registry copy that had years to fill in".

**N12. Seasonal "did better" has no test behind it either.**
- Where: `docs/LINKEDIN_POST.md` L5; `docs/INTERVIEW_NOTES.md` L7.
- Severity: minor.
- Evidence: the post says "Simply repeating the same quarter last year did a little better, at 4.6", and the notes say "simply repeating the same quarter last year did better, at 4.6". 4.6 < 5.5 is true, but the sign test against seasonal gives 11 wins and 15 losses for ratio, p = 0.837. No test supports a verdict for seasonal. The dashboard's wording, "Simply repeating the same quarter last year missed by less, 4.6", states only the average.
- Fix: use the dashboard's wording, "missed by less on average, 4.6".

**N13. The dashboard relabels a 1983 prototype as a G550.**
- Where: `site/app.js` L309.
- Severity: minor.
- Evidence: `k = m ? m[0] : (n === "550" ? "G550" : ...)`. The ACFTREF row is `3970250,GULFSTREAM AEROSPACE,550,...,NO-ENG 01, NO-SEATS 006`, and its one pipeline airframe is serial 551, `year_mfr` 1983, airworthiness 1985-09-16: a single-engine, six-seat type, not a G550. The G550 bar shows 5, of which this is 1.
- Fix: map `"550"` to its own label, for example "550 (1983 single-engine)", or "Other".

**N14. "Past quarters it never saw" overstates what the test held out.**
- Where: `docs/LINKEDIN_POST.md` L3.
- Severity: minor.
- Evidence: "checked it on 26 past quarters it never saw". The rules never saw those quarters, but the registry copy the test reads (2026-10-19) contains them in full. That is the point §2's framing makes, and L5 makes it a paragraph later.
- Fix: "checked it on 26 past quarters held out from setting the rules".

## Noted, outside this brief

- The note's Limitations list now has eight bullets (L88–95, with "Audit" added at L95). §4's R3 speaks of "seven limitations" for the README. Which count the gate expects for the note is for the spec reviewer.

## Summary

| Severity | Count | Ids |
|---|---|---|
| Blocking | 0 | |
| Major | 4 | N1, N2, N3, N4 |
| Minor | 10 | N5 to N14 |
