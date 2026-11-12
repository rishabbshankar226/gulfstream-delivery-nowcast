# Errata

Dated 2026-11-11. Before I made this repository public I had every public figure and sentence audited. Each entry
here is a fault that audit found in something I do not change after the fact: the 2026Q3 lock, its score, the
predictions file, the preregistration, a stored snapshot, or a workflow under `.github/`. The record stays as it
is. Each entry says what is wrong, what it affects, and what I do about it.

No preregistered figure changed. An independent recompute from the data files matched all 547 figures it produced
(`docs/prepub/RECOMPUTE_DIFF.md`), so there is no erratum of the "old value, new value" kind.

## E1. Pages does not redeploy after the workflow's own commits

- **Where:** `.github/workflows/pages.yml` (push to `main` touching `site/**`, or manual dispatch) and
  `.github/workflows/nowcast.yml` (commits with the built-in `GITHUB_TOKEN`).
- **Fault:** GitHub does not start a workflow from a push made with `GITHUB_TOKEN`. The daily job's commits to
  `site/data.json` therefore do not redeploy the dashboard. Once Pages is on, the dashboard shows the last state a
  person pushed or dispatched.
- **Affects:** the dashboard's freshness after every lock and every score. No figure in the repository.
- **Not fixed yet because:** the audit did not edit `.github/`.
- **What I do:** run `gh workflow run pages` after each lock and after each score, until `nowcast.yml` dispatches
  it.

## E2. The workflow's runs land hours after their cron time

- **Where:** `.github/workflows/nowcast.yml`, cron `17 0,12 * * *` (UTC).
- **Fault:** by committer time in `git log`, the 00:17 UTC run's commits landed between 04:44 and 07:21 UTC and the
  12:17 UTC run's between 15:58 and 18:42 UTC. The 2026Q3 lock was made by the first of these at 05:51 UTC
  (01:51 ET) on the eve, from a snapshot dated the eve.
- **Affects:** a lock can be missed, never made late: `live.before_release` refuses a lock on or after the release
  date. A run that lands after midnight ET on the eve needs an eve-dated download to lock; the 19:00 ET rule is
  out of the workflow's reach at these delays.
- **What I do:** on each release eve I check by noon ET that the lock release exists; if not, I run `make daily`
  on my Mac before midnight ET.

## E3. CI cannot build the note's PDF

- **Where:** `src/gdn/daily.py` (`rebuild` builds the PDF only on a Mac outside CI), `src/gdn/note.py` (`run_pdf`).
- **Fault:** the workflow rewrites `report/note.html` daily and after each lock and score, and leaves
  `output/GD_research_note.pdf` and `site/GD_research_note.pdf` as they were. The PDF's input stamp
  (`output/GD_research_note.inputs.sha256`) then no longer equals `sha256(report/note.html)`.
- **Affects:** the PDF linked from the dashboard and the README can lag the HTML note by one or more days.
- **What I do:** run `make pdf` on my Mac after each lock and each score and push it.

## E4. No release date for 2026Q4 and no fiscal end for 2027Q1

- **Where:** `config/calendar.json` (`releases` holds only 2026Q3; `fiscal_ends` is empty).
- **Fault:** with no 2026Q4 release date the job logs "no release date" and makes no lock. 2027Q1's window end
  also needs GD's fiscal quarter end.
- **Affects:** the next lock. Nothing in the record.
- **What I do:** add the 2026Q4 release date the day GD announces it, and 2027Q1's fiscal end from GD's filings.

## E5. The scope rule drops one G700 type code

- **Where:** `docs/PREREGISTRATION.md` section 3, rule 1 (`TYPEENG` is `4` or `5`) and `src/gdn/faa.py` (`scope`).
- **Fault:** the FAA's ACFTREF file of 2026-10-30 holds the row
  `3980222,GULFSTREAM AEROSPACE CORP,GVIII-G700,5,2`: a G700 type code with engine-type code 2. The rule drops it.
  That day's MASTER file has 17 rows under the code, all registered to `GULFSTREAM AEROSPACE CORP`, none with a
  certificate date, and DEREG has none (serials 87171, 87172, 87174, 87176 to 87182, 87184 to 87187, 87191 to
  87193). Counted by script from the FAA's file of 2026-10-30 on 2026-11-11.
- **Affects:** no past count, since none of the 17 has a delivery event. The dashboard's chart of jets on
  Gulfstream's own registration leaves them out. When these jets are registered to customers or exported, the
  count will miss them unless the rule is amended.
- **Not changed yet because:** the rule is preregistered, and the stored snapshot subsets were filtered by it, so an
  amendment changes what every later subset holds. That is a dated deviation, to be made and stated in the open.
- **What I do:** before the 2026Q4 window closes on 2026-12-31 I either amend the rule (naming the code and dating
  the change in the README and in a new entry here, never in the preregistration) or keep it and keep the README's
  Holder and scope limitation.

## E6. The holder rule misses `GULFSTREAM LEASING LLC`

- **Where:** `docs/PREREGISTRATION.md` section 3 and `src/gdn/events.py` (`gulfstream_held`: names that start
  `GULFSTREAM AEROSPACE`).
- **Fault:** four certificates issued to `GULFSTREAM LEASING LLC` count as customer deliveries: serials 72001 and
  73002 on 2020-11-13 (2020Q4), and 87001 and 88001 on 2025-10-07 (2025Q4). Source:
  `data/snapshots/2026-10-19/MASTER.txt.gz` joined to `data/processed/serials.csv`.
- **Affects:** the 2020Q4 and 2025Q4 large-cabin counts, by two events each, under the preregistered rule. The
  figures stand as preregistered.
- **What I do:** nothing to the record. A wider holder rule belongs in `results/exploratory/`, labelled as tried
  after the fact.

## E7. The 2026-10-19 subset's gzip header

- **Where:** `data/snapshots/2026-10-19/*.gz`.
- **Fault:** a reviewer of the registry code reported (`reviews/registry.md`, REGISTRY-10) that byte 9 of the stored
  gzip header differs from what the current `files.write_gz` writes, with identical decompressed bytes. The
  manifest hashes are right for the stored files, but the current code would not rebuild those exact compressed
  bytes from the zip. I have not measured this a second time.
- **Affects:** nothing computed. A reader who rebuilds the subset should compare decompressed content.

## E8. A build note states the wrong nearest-rank position

- **Where:** `docs/build/DECISIONS.md:110` says the 2024Q3 band uses nearest-rank position 4.
- **Fault:** the code uses position 3, as the preregistered formula gives, because `0.1 * 30` is exactly `3.0` in
  floating point. No figure is affected. `docs/build/README.md` names this error; the build note itself is kept
  as written.

## E9. Three guards in the lock and score code go beyond the preregistered text (dated 2026-11-11)

- **Where:** `docs/PREREGISTRATION.md` section 3.6 and `src/gdn/live.py`, `src/gdn/gitops.py`.
- **What differs:** section 3.6 says a run "recomputes the prediction from the newest snapshot that has a stored
  subset" and scores a quarter "when the quarter's results 8-K appears". The code now adds three conditions the
  text does not state.
  1. No lock is made from a subset dated on or before the quarter's fiscal end. Before, if every download in the
     lock window failed, the job could have locked a part-quarter count from an older subset.
  2. A quarter is not scored when its lock's release was published at or after the time the SEC accepted GD's
     8-K. The release date in `config/calendar.json` is typed by hand; the acceptance time is the check on it.
  3. The lock record is written only when `predictions/<quarter>.json` equals the file at the release tag.
- **Affects:** no figure. None of the three would have changed the 2026Q3 lock or its score: that lock read a
  subset dated 2026-10-29, after the 2026-10-04 fiscal end, and was published about 30 hours before the SEC
  accepted the 8-K. Each guard can only stop a lock or a score, never make or alter one.
- **Why made:** each closes a way for a lock or a score to be wrong. Each has a test.

## E10. The dashboard's lead says "registry estimate" where the preregistered sentence says "registry count"

- **Where:** `docs/PREREGISTRATION.md` section 3.4, headline rule, and `site/app.js`.
- **What differs:** the rule fixes the sentence "Over 26 held-out quarters the registry count was off by X jets a
  quarter on average, against Y for <baseline>." The README, the note and the post carry it word for word, each
  with a sentence saying that "registry count" there means the scaled estimate. The dashboard's lead says "the
  registry estimate" and adds how many jets GD delivers in a typical quarter.
- **Affects:** no figure: both name the same 5.5.
