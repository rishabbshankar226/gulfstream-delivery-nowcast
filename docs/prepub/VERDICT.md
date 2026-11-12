# Verdict

**NO-GO.** Three of the 13 criteria fail (1, 2 and 12), each on something only the owner can do: decide about the email address and the home paths that the commit history would expose (F015, F016), and confirm and date the no-position sentence (F081). Every other S1 and S2 finding is fixed, refuted or an erratum.

Written 2026-11-11 at the end of the pre-publication audit, on branch `prepub-audit`. The final battery ran at commit `8d07bf5`; later commits change only files under `docs/prepub/`. Every figure below was printed by a command run after the last edit that could change it; the commands and their logs are in `BASELINE.md`.

## What remains before GO

1. **Decision A** in `GO_PUBLIC.md` (F015, S1): the personal email address on 124 commits.
2. **Decision B** (F016, S1): home-folder paths in the build notes and in history.
3. **Step 1** in `GO_PUBLIC.md` (F081, S2): confirm and date "I hold no position in General Dynamics", on the README and the note.

Neither A nor B can be removed from the history without rewriting it, and a rewrite would change the hash of the lock commit that the `lock-2026Q3` release points at. So each is a choice between accepting the exposure and not making this repository public. When the owner has made the two choices and done step 1, criteria 1, 2 and 12 hold and the rest of `GO_PUBLIC.md` is the path to the post. This audit cannot make those calls for the owner, so the verdict today is NO-GO.

Not blocking, and due before the next lock: decision C (the G700 type code), the calendar entries in step 10, and step 3b (one run of the merged daily job while the repository is still private).

## The 13 criteria

| # | Criterion | Holds | Measurement |
|---|---|---|---|
| 1 | Zero open S1 findings | **no** | Two: F015 and F016, both from the exposure scan (P3.5), both the owner's to decide. Of the other S1 findings, 19 are fixed and 3 refuted. |
| 2 | Zero open S2 on the post, the README's first screen, the dashboard's first screen, the note's first page and the workbook's Summary sheet | **no** | One: F081. "I hold no position in General Dynamics" sits on `README.md` line 15 and on the note's first page and footer. It is undated and carried forward by the build, and only the owner can state it. `GO_PUBLIC.md` step 1 dates it. No other S2 is open on those five surfaces. |
| 3 | The ledger shows zero `mismatch`, `untraced` and `stale` rows on the post, README, dashboard, note and workbook, after its nine plants were caught | yes | `rows 2864  flagged 0` on the final tree, every surface. The nine plants were rerun on that tree: 9 planted, 9 caught, 0 missed. (`LEDGER_SELFTEST.md`). |
| 4 | Every recomputed figure in P2.2 matches at its displayed precision, or differs with an erratum | yes | `RECOMPUTE_DIFF.md`: 547 figures, 547 match. `git diff --stat 36fed31..HEAD -- results data/processed` lists only files the audit added (`segments_reported.csv`, `results/exploratory/sensitivity.*`), so the figures the recompute matched are the figures in the final tree. |
| 5 | P2.3's lock checks all pass | yes | `LOCK_CHECK.md`: the file's sha256 `3c4cdbd0...6f23` equals the hash in the tree, at the tag, in the release notes and in `2026Q3_lock.json`; the release was published 2026-10-29T05:51:24Z (01:51 ET) and the SEC accepted GD's 8-K at 2026-10-30 08:09:27 ET; the lock commit `a44e5ac` is an ancestor of `main`. |
| 6 | Every link in the post resolves, or resolves after a step in `GO_PUBLIC.md` that names it and its check | yes | `POST_CHECK.md`: both links return 404 while the repository is private; `GO_PUBLIC.md` steps 4 and 5 make them resolve and step 6 checks them from a logged-out browser. |
| 7 | `make test`, the full gate (or each failing family with a logged reason under R11) and `make check-determinism` pass on the fresh clone | yes, with logged gate failures | Fresh clone at `8d07bf5` with Python 3.11 (`BASELINE.md`, Fresh clone): `make all` exit 0 with an empty `git status`; `make test` `176 passed, 14 warnings in 31.68s`; `make check-determinism` `identical (50 files)`; gate `42 assertions, 4 failing, 3 warning`. The four failing assertions (`R2`, `K1`, `N1`, `Y1`, in the `docs` and `site` families) are logged with their reasons in DECISIONS D10 and D18; the other eight families pass. A first clone with the system `python3` (3.9.6) could not install the requirements, which was a finding against the README (F099, fixed). |
| 8 | `INTERVIEW_NOTES.md` and `RESUME_BULLETS.md` state the scored live record | yes | F006, F007, F083: the lock (32.0, band 21.2 to 37.2, 01:51 ET on 2026-10-29), GD's 40, the miss of 8.0 outside the band, the guidance pace's 6.2 and last year's quarter. Ledger: 0 flagged rows on either file. |
| 9 | Round 3 found no S1 | yes | `reviews/round3.md`: S1 0, S2 4, S3 6. Its four S2 are fixed (F101 to F104), and it confirmed the lock file's hash and an empty diff on the protected paths. One of its S2, the post's unqualified "held out", it flagged as a severity call; it is graded S2 on the precedent of F027 and fixed (F104). |
| 10 | Every row of the three source files reads verified, or carries a closed finding ID | yes | `SOURCES_DELIVERIES.csv`: 43 of 43 verified. `SOURCES_GUIDANCE.csv`: 24 verified, 3 verified elsewhere, and the one call the reviewer found missing was added (F054, fixed). `SOURCES_CLAIMS.csv`: 204 verified or verified elsewhere, 23 with a closed finding (F004, F013, F035, F036, F043, F052, F065, F066). |
| 11 | Every hash in `RECORD_HASHES.txt` matches | yes | 61 of 61 hashes recomputed and equal, at `8d07bf5`. `git diff --stat 36fed31..HEAD` over `predictions/`, `results/live/`, `data/snapshots/`, `docs/PREREGISTRATION.md` and `.github/` prints nothing. |
| 12 | P3.5 found nothing open | **no** | F015 and F016, the two rows criterion 1 fails on. |
| 13 | Every required item is finished | yes | `PLAN.md`: every item done, P5.4 included (DECISIONS D15). No item is cut. |

## Findings

`FINDINGS.md` holds 106 findings (F001 to F107; F019 is an unused number). They come from the spec's 16 leads, the first ledger, five round 1 reviewers, three source checkers, the recompute, three round 2 reviewers, one round 3 reviewer and the main thread's own checks.

| Severity | Fixed | Erratum | Refuted | Open | All |
|---|---|---|---|---|---|
| S1 | 19 | 0 | 3 | 2 | 24 |
| S2 | 47 | 5 | 2 | 1 | 55 |
| S3 | 18 | 1 | 1 | 7 | 27 |
| All | 84 | 6 | 6 | 10 | 106 |

### Open, by severity

**S1**

- **F015.** The owner's personal email address is the author address on 124 commits of `main`. A public repository shows it. It cannot be removed without rewriting history, which would change the lock commit's hash. Decision A in `GO_PUBLIC.md`.
- **F016.** Home-folder paths in 16 build-note files and in history. Decision B.

**S2**

- **F081.** The no-position sentence, undated. `GO_PUBLIC.md` step 1.

**S3**

- **F053.** No `og:image` on the dashboard.
- **F063.** Four latent points in the registry parse and the lock path that change no figure today.
- **F064.** The note's risks are general 10-K factors.
- **F068.** "nowcast" survives in the repository's name, the release title and chart legends.
- **F074, F098.** Statistics a referee would add (an interval on the difference in average miss, a test against the winning baseline) and wording points from round 2.
- **F076.** The G700 sentence copies GD's 10-K, which puts EASA certification before first deliveries.
- **F107.** The transcript of GD's 2026-10-30 call, the source of the newest row in `data/guidance.csv`, is not cached with the others.

## Errata

`ERRATA.md` holds ten entries. None changes a preregistered figure.

- E1. Pages does not redeploy after the workflow's own commits.
- E2. The workflow's runs land four to seven hours after their cron time.
- E3. CI cannot build the note's PDF.
- E4. No release date for 2026Q4 and no fiscal end for 2027Q1 in the calendar.
- E5. The scope rule drops one G700 type code: 17 airframes, none delivered yet (decision C).
- E6. The holder rule counts four registrations to Gulfstream's own leasing company as deliveries.
- E7. One stored subset's gzip header differs from what the current code writes.
- E8. A build note states the wrong nearest-rank position.
- E9. Three guards in the lock and score code go beyond the preregistered text.
- E10. The dashboard's lead says "registry estimate" where the preregistered sentence says "registry count".

## Gate failures caused by honest fixes (R11)

The gate prints `42 assertions, 4 failing, 3 warning` on the fresh clone. The four failures are `R2`, `K1`, `N1` (a number on a surface that the gate did not compute) and `Y1` (keys in `site/data.json` the gate does not know). DECISIONS D10 names the numbers the gate printed and where each comes from. The gate prints at most eight numbers per line, so more of the audit's new figures sit behind those eight; the ledger traces every one of them. The baseline's one failure, `N4`, passes.

## What an outsider can and cannot check

**Can check, once the repository is public:**

- That `predictions/2026Q3.json` hashes to the value in the `lock-2026Q3` release notes, and that the tag points at commit `a44e5ac`, an ancestor of `main`.
- That GitHub shows the release as published at 2026-10-29T05:51:24Z by `github-actions[bot]`, and that the SEC shows GD's 8-K (0000040533-26-000036) accepted at 2026-10-30 08:09:27 ET.
- Every backtest figure, from the tracked data files with `make all`, and that the build is deterministic.
- Every delivery count against GD's releases by accession number, and every guidance quote against its transcript link.

**Cannot check:**

- That the release notes and the release's `published_at` were never edited. GitHub lets an owner edit a release, and the push history that would show it needs `gh api`, which this audit was not allowed to call.
- That nobody saw the estimate before GD reported. The repository was private at the lock, so there was no public timestamp anyone else could have saved. The README, the note and the post say so.
- That the rules were fixed before the held-out results were seen. The commits put the rules 2 minutes before the scores, in one session, with all the data already in the repository. The README says the commit order is all that backs "held out".
- That the merged daily job runs end to end on GitHub. Its tests pass and it has not run there in its merged form. `GO_PUBLIC.md` step 3b runs it once while the repository is still private.

**What the ledger does not prove.** It traces each number to a source field by label and value. Some of its "sources" are constants typed into `tools/prepub/ledger_rules.py` from a document read once: GD's 2026Q3 Marine Systems backlog ($146.9B, from the 8-K exhibit), the "about 11" demonstrators (a 2022 call), the two years 2027 and 2028 (a 2026 call), the study's as-of date, and the engine-type codes. The 17 G700s are counted from the raw FAA zip when it is present. Each constant carries its source in the rules file.

## What a hostile reader will still ask

**"Your model lost to copying last year's number. Why publish it?"** Because that is the result. On 26 held-out quarters the estimate missed by 5.5 jets a quarter and the same quarter last year by 4.6. The first live lock missed by 8.0, outside its band, and last year's quarter missed by 1. The post, the README's first screen, the dashboard and the note each say so before anything else.

**"You beat GD's guidance, 5.5 against 6.9?"** No. None of the three preregistered sign tests separates them. The lead comes from 2023 and 2024, when G700 deliveries slipped. On the other 18 quarters the guidance pace missed by 4.4 and my estimate by 6.4. The pace is my construction from GD's full-year outlook. On six calls GD gave the quarter's own number, and with those in place the baseline misses by 6.0, and by 5.7 if GD's January 2021 statement is also read as a number. The guidance pace was closer in each of the last five quarters.

**"Was it really preregistered?"** The rules were committed before the held-out scores, 2 minutes before, in the same session, with every count already in the repository, and the rules for reading GD's calls quote two of the transcripts. Only the locked quarters are out of sample in the strict sense. There is one.

**"Who made the lock, and could you have changed it?"** A GitHub workflow made it at 01:51 ET on 2026-10-29, 30 hours before the SEC accepted GD's filing, while the repository was private. The file's hash is in the release notes and matches. I cannot prove the release was never edited, and I say so.

**"Does the registry count deliveries?"** It counts registration events. About one counted event in five is on an airframe at least three years old (246 of 1,251), 5 of the 42 in the locked quarter. The registry keeps only an airframe's current certificate, so old quarters lose events over time. Four registrations to Gulfstream's own leasing company count as deliveries, and one G700 type code is outside the scope rule. Each is in the README's Limitations with its size.

**"Did an AI write this?"** I built it with Claude Code, an AI coding agent, in sessions I ran and directed, and the README says so. The build notes and this audit's notes are in the repository.

**"Is this investment advice? Do you own the stock?"** No. Every surface says it is a student project and not investment advice, and the note carries no rating or target. The position statement is mine to confirm and date before posting.
