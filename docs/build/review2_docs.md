# Review round 2: document closures

Reviewer: a fresh reviewer who built nothing here. Brief: `docs/build/briefs/review2_docs.md`. Read at HEAD `74ce718`, 2026-10-19 13:40 to 13:55 EDT, with a clean tree before and after.

## What I read and ran

- Round 1's rows in `docs/build/REVIEW.md` that the brief gives me (FC-F1 to FC-F3, the A, C and O ids, the N ids), and the three original reports.
- `git diff 062e00e..HEAD` over `README.md`, `docs`, `report`, `site`, `src/gdn/note.py`, `src/gdn/report.py` and `results`.
- The PDF: `output/GD_research_note.pdf`, sha256 `f732c8e0...e147b`, byte-identical to `site/GD_research_note.pdf`, 7 Letter pages. I rendered it with `swift tools/pdfpages.swift` into my scratch directory and read every page. I rendered page 3 again at 5x to check the Exhibit 4 legend.
- The dashboard as built: the existing local server on 127.0.0.1:8766 serves `site/` (its `app.js` and `data.json` hash the same as the tracked files), and I read `document.body.innerText` and the three canvas labels.
- Recomputations with Python over `results/metrics.json`, `results/holdout.csv`, `results/design.csv`, `results/exploratory/asof.csv`, `results/estimates.json`, `data/processed/gd_deliveries.csv`, `data/processed/registry_quarterly.csv`, `data/processed/serials.csv`, `data/processed/segments.csv` and `docs/build/AIRFRAME_AUDIT.csv`. Scripts live in my scratch directory.
- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_wording.py tests/test_claims.py -q -p no:cacheprovider`: 18 passed.

I ran no `make` target, did not touch the gate, its cache or `~/.sec_ua`, and wrote only this file.

## Summary

| Severity | Count | Ids |
|---|---|---|
| Blocking | 0 | |
| Major | 0 | |
| Minor | 9 | R2D-1 to R2D-9 |

Every round 1 closure I own holds in the places its row names, with two partial exceptions: C2/N1 (the counts the row says each surface states are missing from two of three surfaces, and one new sentence misreads one of four quarters) and O2 (one stored page image is stale). The headline rule holds on every surface, §2's framing sentence still appears everywhere it did, nothing says the project counts jets before GD reports them, the note is 7 pages, and no em dash appears in any prose surface.

## Findings

### R2D-1. The new as-of sentence says the archived estimates "came out lower"; one of four came out higher

- File and line: `README.md:121`; `results/exploratory/asof.md:12`.
- Severity: minor. It is new text from a2f8e76 and sits in the secondary analysis; the note's version (`report/note.html:71`) avoids the claim.
- Evidence: README: "Their estimates came out lower and, given the ratio's upward bias in the held-out quarters, closer." `asof.md`: "so their estimates came out lower and, given the ratio's upward bias, closer." From `results/exploratory/asof.csv` against `results/holdout.csv` and `results/design.csv`:

  | Quarter | As-of estimate | Estimate on the 2026-10-19 copy | GD reported |
  |---|---|---|---|
  | 2017Q1 | 33.34 | 35.55 | 30 |
  | 2025Q3 | 32.39 | 32.20 | 39 |
  | 2026Q1 | 43.33 | 45.38 | 38 |
  | 2026Q2 | 42.69 | 44.81 | 41 |

  In 2025Q3 the archived copy's estimate is higher, not lower, and it is closer because both copies missed low. The archived copy held 184 lag events against 176, which lowers the estimate, but also 40 own-quarter events against 38, which raises it more.
- Fix: "In three of the four (2017Q1, 2026Q1 and 2026Q2) their estimates came out lower and, given the ratio's upward bias, closer. In 2025Q3 both copies missed low, and the archived copy, with two more of the quarter's own events, came out slightly higher." Apply the same wording in `asof.md` (and in whatever writes it), and add the phrase to `tests/test_wording.py::test_as_of_mechanism_is_stated_as_measured`.

### R2D-2. The C2/N1 closure says each surface states the counts; the note and `asof.md` do not

- File and line: `docs/build/REVIEW.md:64`; `report/note.html:71` (PDF p3); `results/exploratory/asof.md:12`.
- Severity: minor.
- Evidence: REVIEW.md: "Each states the counts and that the later file lost first-owner records." Only the README gives counts ("206 against 203 for 2026Q2, 146 against 63 for 2017Q1"). The note says "They held more events for the same past quarters than today's file", and `asof.md` says "The archived copies held more lag-quarter events than the 2026-10-19 copy", both without a number. The analyst's C2 also asked the note to add "its band held 2 of 3"; the note still does not say that the 2025Q3 as-of band missed (`asof.csv` `inside_band` is 0 for 2025Q3).
- Fix: either add the two count pairs to the note's sentence and to `asof.md`, and "its band held GD's count in two of the three held-out quarters" to the note, or change the REVIEW.md row to say only the README states the counts.

### R2D-3. "The jets checked were delivered by 2019" is not established for three of the 30

- File and line: `README.md:144`; `report/note.html:95` (PDF p6); enforced by `tests/test_wording.py:52` (`present(NOTE, "All but one source", "delivered by 2019")`).
- Severity: minor.
- Evidence: in `docs/build/AIRFRAME_AUDIT.csv`, the three unconfirmed rows have a blank `source_date` and registry dates of 2024-12-13 (72023), 2023-04-13 (5467) and 2025-01-17 (2177). `DECISIONS.md:176` says of them: "three airframes the bound removed (72023, 5467, 2177) for which no source dates a first delivery." The same sentence in the README says they "could not be confirmed". The audit cannot give a delivery year for jets it could not date. What the file does show: every dated event falls between 2000-06-02 and 2019-09-06, and every audited airframe has an airworthiness date or build year of 2019 or earlier.
- Fix: "Every event the audit could date fell between 2000 and 2019, so it says little about recent quarters." Change the test's required phrase to match.

### R2D-4. The post still says "GD's own guidance pace", the phrase C3 removed elsewhere

- File and line: `docs/LINKEDIN_POST.md:3`, written by `src/gdn/report.py` `post()`.
- Severity: minor. C3's row named only `site/app.js:14` and the note, and the closure holds there; the same phrase survives in the post.
- Evidence: "checked it on 26 past quarters held out from setting the rules, against GD's own guidance pace and two simple baselines." `tests/test_dashboard_labels` checks `APP` and `NOTES` for "own guidance pace" but not `POST`. (README:3's "against GD's own guidance" refers to the outlook itself and is fine.)
- Fix: "against GD's guidance pace and two simple baselines" in `report.py`, and add `absent(POST, "own guidance pace")` to the test.

### R2D-5. The dashboard's revenue caption keeps the reading the note's cover now corrects

- File and line: `site/app.js:392-393`; rendered under "What it means for GD".
- Severity: minor. A2's row named the note only, and the closure holds there.
- Evidence: rendered text: "The delivery estimate of 31.1 sits below the 39 deliveries of 2025Q3, and each delivery carries about $85M of Aerospace revenue, so the delivery-based figure falls." The note's cover (p1, key point 3) now says: "The $85M includes services and Jet Aviation, which do not fall with deliveries, so the delivery-based figure overstates the swing." The dashboard gives no such caveat beyond the §3.7 label.
- Fix: append the note's sentence to the caption: "The $85M includes services and Jet Aviation, which do not fall with deliveries, so the delivery-based figure overstates the swing."

### R2D-6. The cover states the release date more firmly than the claim it cites

- File and line: `report/note.html:54` (PDF p1, key point 2).
- Severity: minor.
- Evidence: the cover reads "GD reports on 2026-10-30.<sup>1</sup>", citing `os-release-date`, whose text is "GD said it expected to hold its third-quarter 2026 earnings call on Friday, October 30." and whose quote is "we expect to hold our Q3 earnings call on Friday, October 30, at 9:00 a.m." The analyst's C6 fix asked for "GD expects to report on 2026-10-30".
- Fix: "GD expects to report on 2026-10-30." in `note.py`'s cover line.

### R2D-7. The G400 claim keeps an undated relative time, the same kind of problem C10 fixed

- File and line: `docs/build/claims_product.json:157`; `report/note.html:62` (PDF p2).
- Severity: minor.
- Evidence: "GD said it has stepped up its work on the G400 and will say more over the next couple of quarters about where the G400 will be." The note never says when GD said it, so "the next couple of quarters" has no anchor for a reader in late October 2026. C10 objected to "next year" from the same 2026-07-29 call for this reason.
- Fix: "On its 2026-07-29 call, GD said it had stepped up its work on the G400 and would say more over the following couple of quarters about where the G400 will be."

### R2D-8. O4's "open, for the same reason" does not hold: the Marine comparison is arithmetic, not editing

- File and line: `docs/build/REVIEW.md:82`; `report/note.html:78` (Exhibit 8, PDF p4) and `report/note.html:84` (p5).
- Severity: minor.
- Evidence: O3's reason ("reordering the risks is editorial") does not carry over. From `data/processed/segments.csv` and `results/estimates.json`: Marine revenue in 2026Q1 and 2026Q2 sums to $9,003M, and the drift estimate for 2026Q3 is $4,775M. GD's outlook of about $18 billion (`os-marine-outlook`, already cited on p5) leaves about $4.5B a quarter for the second half. The note prints $4.8B and the $18B outlook a page apart and never sets one against the other.
- Fix: one sentence under Exhibit 8 or in the Marine bullet on p5: "GD's outlook of about $18B for 2026, with $9.0B in the first half, implies about $4.5B a quarter for the second half, below the drift baseline's $4.8B." Then close O4 in REVIEW.md.

### R2D-9. O2 does not fully hold: one stored page image predates the final PDF

- File and line: `.build/shots/note/page-02.png` (untracked); `docs/build/REVIEW.md:80`.
- Severity: minor.
- Evidence: the stored images are dated 12:34:17 and the PDF 12:35:32. Six of seven match my render byte for byte; page 2 does not (`9f3432f3f8f6` against `c3cfd640524e`). The stored page 2 ends "On those 22 quarters GD's guidance pace missed by 7.4 aircraft on average. The registry estimate's past-miss band ..."; the PDF reads "... missed by 7.4 aircraft on average, against 5.3 for the registry estimate and 4.6 for the same quarter last year." The second half of O2 holds: at 5x the Exhibit 4 legend reads "Registry estimate (ratio)", so the "est mate" is a render artefact.
- Fix: regenerate the page images from the final PDF in the step that writes it, and refer to them only after that.

## Each round 1 row

"Holds" means the fix is present and correct in every place the row names. Surfaces: README; note HTML and PDF; post; interview notes (notes); resume bullets (bullets); the dashboard as rendered (app).

| Row | Verdict | Where checked |
|---|---|---|
| FC-F1 | Holds. `pc-g300-entry-timing` is gone from `claims_product.json`, `report/claims.json` (31 entries) and the note; no "G300", "next year" or "late '27" remains. | claims files, note, PDF p1 to p2 |
| FC-F2 | Holds. `pc-g300-announced` is gone, and the 2025Q3 10-Q it cited (0000040533-25-000045) no longer appears among the note's sources. | claims files, note, PDF p7 |
| FC-F3 | Holds. The text is dated to the 2025 annual report, and the quote still contains every fact in it. | claims.json, PDF p6 |
| A1, N3, N10 | Holds. The note's Exhibit 6 caption, README:69 and the dashboard each say the flag looks only for high ratios and print 0.69, 0.69, 0.72 against 1.18. The note's Used jets limitation names the re-import path. Notes:13 gives the drift as measured. | PDF p3, p6; README; app; notes |
| A2 | Holds where named: cover adds 39 in 2025Q3, the Q4 needed against the best quarter of 47, the $3.6B drift figure and the services caveat; the live paragraph says the snapshot is younger than any as-of copy (15 days against 23 to 29). See R2D-5 for the dashboard. Open part: Exhibit 9's range is fixed by §3.7 (k from -4 to 4), so leaving it is right, though the row should cite §3.7. The guidance pace before a score rests on `DECISIONS.md:161`; I did not run the gate to confirm the rejection. | PDF p1, p4, p5; app |
| A3, N12, N14, C8 | Holds. Cover and callout add "Simply repeating the same quarter last year missed by less on average, 4.6." The guidance paragraph adds 5.3 and 4.6. Post and notes use "missed by less on average"; the post says "held out from setting the rules". | PDF p1, p2; post; notes |
| C1 | Holds. The 8-quarters comparison is gone; the caption says the 270 include registrations for jets with no airworthiness date and are not a count of jets awaiting delivery (208 of 270 have no airworthiness date). | app, index.html |
| C2, N1 | Partly. The direction is right on all three surfaces and the README's counts recompute (206 against 203, 146 against 63). See R2D-1 and R2D-2. | README, PDF p3, asof.md |
| N2, C9 | Holds for the breakdown (four, one, two, three; 29 mirror and 1 release source; `DECISIONS.md:175-176,183` agree). See R2D-3 for "delivered by 2019". | README, PDF p6, DECISIONS.md |
| N4 | Holds. The bullet now describes a job that locks and scores, with the first score on 2026-10-30 in the future tense. | bullets |
| C3 | Holds where named: "own" is dropped from `app.js`, the note and the dashboard define the pace, and Exhibit 5 footnotes 2021. See R2D-4 for the post. | app, PDF p2, p3 |
| C4 | Holds. Registry against GD mid-cabin since 2022: 25/24, 20/22, 22/18, 25/22 and 15/13 for the first half of 2026, so within 1 to 4 jets. | README, PDF p6 |
| C5 | Holds. Source 9 reads "snapshot 2026-10-19 for the backtest." and will name a newer daily snapshot only when one exists. | PDF p7 |
| C6 | Holds for the citation (`os-release-date`, verbatim quote, same sha256 as the other call claims). See R2D-6 for the wording. | PDF p1, claims.json |
| C7 | Holds. "against a nominal 80%" on all three. | README, PDF p2, app |
| C10 | Holds for "stepped up"; "next year" went with FC-F1. See R2D-7. | PDF p2, claims files |
| C11 | Holds. Sources 2, 3, 4, 6 and 7 are named by form and period, and each accession matches the fact-checker's file. | PDF p7 |
| N5, N6 | Holds. Every two-decimal yearly mean recomputes from `holdout.csv`, and the 2026 row reads "2026, first half" (two quarters). | README, PDF p3 |
| N7, N8 | Holds. "Evening" and "eve of the release" appear nowhere; each surface says 2026-10-29, the day before GD reports. | README, PDF p4, notes, bullets, app, index.html |
| N9 | Holds. "best next-quarter baseline" in the README, the note and bullet 3. | README, PDF p5, bullets |
| N11 | No change; the reasoning holds. Bullet 1 is 219 characters against §6's cap of 220, and §6 fixes its form, so the 4.6 and the framing do not fit; both are in the post and the notes. | bullets |
| N13 | Holds. Type "550" is labelled "Other". | app |
| O1 | Open; the reasoning holds. §3.8 lists every Quarters column and Summary row, and makes Live B7 and B8 inputs. | spec §3.8 |
| O2 | Partly. See R2D-9. | `.build/shots/note/` |
| O3 | Open; the reasoning holds. §3.9 item 8 is met (each risk is a cited claim), and the print-specific risks (G280 supplier delays, the G280 deliveries risk) are cited under "What the street watches". This is round 2, so I would close it as no change. | PDF p5 to p6 |
| O4 | Open; the reasoning does not hold. See R2D-8. | PDF p4, p5 |
| T9 | Not mine; it is a code row for the code reviewer. | |

## Checked and clean

- **The 22 sourced quarters.** Guidance 7.357, ratio 5.250 and seasonal 4.636 over the 22 quarters outside 2021Q1 to 2021Q4, so 7.4, 5.3 and 4.6 as printed.
- **Yearly means.** Every cell of the README's and Exhibit 5's tables matches `holdout.csv` to two decimals, for example 2020 guidance 4.2319 (4.23), 2023 guidance 14.0632 (14.06), 2026 ratio 5.5955 (5.60).
- **Coverage ratios.** 2025Q4 0.6923, 2026Q1 0.6909, 2026Q2 0.7193, mean 1.1824, sd 0.3516, no flags. Only 2022Q1 (0.6579) is lower. "About two deliveries per event in 2016" in the notes fits 2016's 121 deliveries over 63 events (1.92).
- **Lag events and best quarter.** Lag events 206 against 203 (2026Q2) and 146 against 63 (2017Q1). First-half 2026 deliveries 79. Best quarter 47 (2024Q4), the highest from 2016Q1 on. 160 minus 79 minus 31.13 leaves 49.9, above 47, so the cover's Q4 sentence holds. 2025Q3 delivered 39.
- **Cover dollars.** Revenue per delivery $84.8M ($85M), Aerospace from the estimate $2,641M ($2.6B), drift $3,631M ($3.6B), 2025Q3 Aerospace $3,234M ($3.2B).
- **As-of capture ages.** 23, 25, 26 and 29 days after quarter end, against 15 for the 2026-10-19 snapshot of 2026Q3 (window end 2026-10-04).
- **Headline rule (§3.4).** No surface says the registry beat a baseline: Holm rejects none and the relative misses are 0.80, 1.20 and 0.63. The README, note cover and callout, and post carry the prescribed sentence with guidance named first (22 sourced quarters); the dashboard's hero is the close variant round 1 accepted. The only "beat" on any surface is a conditional in notes:18 ("If public registrations cannot beat the company's own outlook, they add little"), which claims nothing.
- **Framing (§2).** The sentence is on the note's cover and callout (PDF p1, p2), README:11 and notes:21. Close variants are on the dashboard hero and post:5. Nothing says the project counts jets before GD reports them; every "before GD reports" is about the lock date.
- **Length and dashes.** The note is 7 pages, inside 4 to 8. No em or en dash and no CR in the README, the note, the post, the notes, the bullets, `app.js`, `index.html`, `data.json` or `asof.md`. The only em dash in `report/claims.json` is inside the verbatim 10-K quote of `bo-technologies`; it predates round 1 and is not printed.
- **Limits.** The interview notes have 825 words (cap 900) and the post has 1,194 characters (cap 1,500).
- **Regression tests.** The named tests in `tests/test_wording.py` and `tests/test_claims.py` pass at HEAD (18 passed). Two of them lock in wording this review questions: `test_audit_breakdown_matches_the_audit_file` requires "delivered by 2019" (R2D-3), and `test_dashboard_labels` does not check the post (R2D-4).
