# Errata

Dated 2026-11-11. Each entry is a fault the pre-publication audit found in something this run may not change: the
2026Q3 lock, its score, the predictions file, the preregistration, a stored snapshot, or a workflow under `.github/`.
The record stays as it is. Each entry says what is wrong, what it affects, and what the owner must decide.

No preregistered figure changed in this audit. The independent recompute matched all 547 figures it produced
(`docs/prepub/RECOMPUTE_DIFF.md`), so there is no erratum of the "old value, new value" kind.

## E1. Pages does not redeploy after the workflow's own commits

- **Where:** `.github/workflows/pages.yml` (push to `main` touching `site/**`, or manual dispatch) and
  `.github/workflows/nowcast.yml` (commits with the built-in `GITHUB_TOKEN`).
- **Fault:** GitHub does not start a workflow from a push made with `GITHUB_TOKEN`. The daily job's commits to
  `site/data.json` therefore do not redeploy the dashboard. Once Pages is on, the dashboard shows the last state a
  person pushed or dispatched.
- **Affects:** the dashboard's freshness after every lock and every score. No figure in the repository.
- **Not fixed here because:** `.github/` is outside this run's edits.
- **Owner:** run `gh workflow run pages` after making the repository public, after each lock and after each score
  (`GO_PUBLIC.md`), or add a dispatch step to `nowcast.yml`.

## E2. The workflow's runs land hours after their cron time

- **Where:** `.github/workflows/nowcast.yml`, cron `17 0,12 * * *` (UTC).
- **Fault:** by committer time in `git log`, the 00:17 UTC run's commits landed between 04:44 and 07:21 UTC and the
  12:17 UTC run's between 15:58 and 18:42 UTC. The 2026Q3 lock was made by the first of these at 05:51 UTC
  (01:51 ET) on the eve, from a snapshot dated the eve.
- **Affects:** a lock can be missed, never made late: `live.before_release` refuses a lock on or after the release
  date. A run that lands after midnight ET on the eve needs an eve-dated download to lock; the 19:00 ET rule is
  out of the workflow's reach at these delays.
- **Owner:** on each release eve, check by noon ET that the lock release exists; if not, run `make daily` on the
  Mac before midnight ET (`GO_PUBLIC.md`).

## E3. CI cannot build the note's PDF

- **Where:** `src/gdn/daily.py` (`rebuild` builds the PDF only on a Mac outside CI), `src/gdn/note.py` (`run_pdf`).
- **Fault:** the workflow rewrites `report/note.html` daily and after each lock and score, and leaves
  `output/GD_research_note.pdf` and `site/GD_research_note.pdf` as they were. The PDF's input stamp
  (`output/GD_research_note.inputs.sha256`) then no longer equals `sha256(report/note.html)`.
- **Affects:** the PDF linked from the dashboard and the README can lag the HTML note by one or more days.
- **Owner:** run `make pdf` on the Mac after each lock and each score and push it (`GO_PUBLIC.md`).

## E4. No release date for 2026Q4 and no fiscal end for 2027Q1

- **Where:** `config/calendar.json` (`releases` holds only 2026Q3; `fiscal_ends` is empty).
- **Fault:** with no 2026Q4 release date the job logs "no release date" and makes no lock. 2027Q1's window end
  also needs GD's fiscal quarter end.
- **Affects:** the next lock. Nothing in the record.
- **Owner:** add the 2026Q4 release date the day GD announces it, and 2027Q1's fiscal end from GD's filings
  (`GO_PUBLIC.md`).

## E5. The scope rule drops one G700 type code

- **Where:** `docs/PREREGISTRATION.md` section 3, rule 1 (`TYPEENG` is `4` or `5`) and `src/gdn/faa.py` (`scope`).
- **Fault:** the FAA's ACFTREF file of 2026-10-30 holds the row
  `3980222,GULFSTREAM AEROSPACE CORP,GVIII-G700,5,2`: a G700 type code with engine-type code 2. The rule drops it.
  That day's MASTER file has 17 rows under the code, all registered to `GULFSTREAM AEROSPACE CORP`, none with a
  certificate date, and DEREG has none (serials 87171, 87172, 87174, 87176 to 87182, 87184 to 87187, 87191 to
  87193). Command: a script over `data/raw/faa/ReleasableAircraft-2026-10-30.zip`, run 2026-11-11.
- **Affects:** no past count, since none of the 17 has a delivery event. The dashboard's chart of jets on
  Gulfstream's own registration leaves them out. When these jets are registered to customers or exported, the
  count will miss them unless the rule is amended.
- **Not fixed here because:** the rule is preregistered, and the stored snapshot subsets were filtered by it, so an
  amendment changes what every later subset holds. That is a dated deviation the owner must make and state.
- **Owner:** before the 2026Q4 window closes on 2026-12-31, either amend the rule (name the code, date the change in
  the README and in a new section of this file, never in the preregistration) or keep it and keep the README's
  Holder and scope limitation.

## E6. The holder rule misses `GULFSTREAM LEASING LLC`

- **Where:** `docs/PREREGISTRATION.md` section 3 and `src/gdn/events.py` (`gulfstream_held`: names that start
  `GULFSTREAM AEROSPACE`).
- **Fault:** four certificates issued to `GULFSTREAM LEASING LLC` count as customer deliveries: serials 72001 and
  73002 on 2020-11-13 (2020Q4), and 87001 and 88001 on 2025-10-07 (2025Q4). Source:
  `data/snapshots/2026-10-19/MASTER.txt.gz` joined to `data/processed/serials.csv`.
- **Affects:** the 2020Q4 and 2025Q4 large-cabin counts, by two events each, under the preregistered rule. The
  figures stand as preregistered.
- **Owner:** none required. A wider holder rule belongs in `results/exploratory/`, labelled as tried after the fact.

## E7. The 2026-10-19 subset's gzip header

- **Where:** `data/snapshots/2026-10-19/*.gz`.
- **Fault:** reported by the registry reviewer (`reviews/registry.md`, REGISTRY-10): byte 9 of the stored gzip
  header differs from what the current `files.write_gz` writes; the decompressed bytes are identical. The manifest
  hashes are right for the stored files but the current code would not rebuild those exact compressed bytes from
  the zip. Not re-measured by the main thread.
- **Affects:** nothing computed. A reader who rebuilds the subset should compare decompressed content.

## E8. A build note states the wrong nearest-rank position

- **Where:** `docs/build/DECISIONS.md:110` says the 2024Q3 band uses nearest-rank position 4.
- **Fault:** the code uses position 3, as the preregistered formula gives, because `0.1 * 30` is exactly `3.0` in
  floating point. No figure is affected. `docs/build/README.md` names this error; the build note itself is kept
  as written.
