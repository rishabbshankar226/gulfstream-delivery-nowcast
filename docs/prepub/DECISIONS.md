# Pre-publication audit: decisions

Each entry: what the spec left open or what blocked the plain reading, the reading I took, and why.

## D1. `OUTCOME_SELF.md` is kept out of commits through `.gitignore`, not `.git/info/exclude` (2026-11-11)
The spec says to add `OUTCOME_SELF.md` to `.git/info/exclude`. A session hook from an unrelated plugin (`claude-seo-ai`) refuses any write to `.git/info/exclude`, by shell redirect and by the Edit tool. I did not route around the hook. I added `/OUTCOME_SELF.md` to the tracked `.gitignore` instead, which keeps the file out of every commit and keeps the tree clean for the gate's `repo` family. Cost: one extra line in a public file.

## D2. P2, P3 and P4 subagents start as soon as P0 is done, while the main thread builds the ledger (2026-11-11)
§4 says the order of items is the order to run them, and only says P2, P3 and P4 run in parallel with each other. The subagents take hours of wall clock and touch nothing P1 touches (each writes only its own file under `docs/prepub/reviews/` or `docs/prepub/recompute/`). Running them behind the ledger build saves that time with no shared state. No detector output is used before its §5 plant result is in `DETECTORS.md`. The gate is not run while a subagent is writing, because the `repo` family fails on an uncommitted file.

## D3. How criterion 11 reads when the daily workflow commits during the run (2026-11-11)
The workflow commits to `origin/main` twice a night and rewrites `results/live/2026Q4_*`, `data/snapshots/MANIFEST.json`, new files under `data/snapshots/daily/` and generated outputs. Criterion 11 exempts only `.github/`. Reading taken:
- The 2026Q3 files in `results/live/`, everything in `predictions/`, `docs/PREREGISTRATION.md` and every snapshot file that existed at P0.1 must match their P0.1 hash exactly.
- Any other hashed file that differs must equal the version in a named `origin/main` commit merged at P8.5.
- `VERDICT.md` states the literal result (which hashes differ) as well as this reading.

## D4. Scratch copies (2026-11-11)
`rm` and `mv` are denied, so every scratch copy goes into a new numbered directory under `$HOME/gdn-prepub/` made with `git archive | tar -x`. None is reused or deleted.

## D5. The codex branch is tested in a scratch clone, and merged only after the reviewers finish (2026-11-11)
P5.1 says to run the branch's tests on a scratch branch. Switching branches in the working tree would change `src/gdn/daily.py`, `gitops.py` and `live.py` under the reviewers still reading them. I cloned the repository to `~/gdn-prepub/scratch/codex`, cut `codex-test` from `prepub-audit` there and merged `origin/codex/fix-daily-merge-and-lock-integrity` with `git merge --no-ff`. It merged with no conflict. `make test` there printed `6 failed, 132 passed, 2 skipped` (the same six failures as the baseline, 18 more tests passing), and `pytest tests/test_gitops.py tests/test_daily.py tests/test_live.py` printed `56 passed`.

Verdict per commit:
- `44b3715` "Preserve daily merge history and fail safely on lock publication errors": merge. It keeps both machines' path rows where the old code dropped the local ones, reads conflict markers from the staged blob, and returns 1 when a lock record cannot be pushed. One part is too strict: `merge_manifests` refuses two entries for the same date that differ only in `downloaded_utc`, which two machines that download the same zip will always produce. That turns a harmless race into a failed run inside the lock window. I fix that on top with its own test (finding F014).
- `163eac0` "Verify locked prediction against its release tag and guard merge commits": merge. Before it, `write_lock_json` recorded the local file's hash without checking the file against the tag. Its test `test_lock_record_refuses_prediction_that_differs_from_the_release_tag` covers the hazard "a lock whose hash does not match its release".

The merge into `prepub-audit` waits until the P4 reviewers have written their reports, so their `file:line` references stay true to the tree they read.

## D6. No WebFetch tool in the main thread (2026-11-11)
§5 says to find the link check's 200-with-not-found page with WebFetch. The main thread has no WebFetch tool (ToolSearch found none), and P3.4 allows Python `urllib`. I found and recorded the page with `urllib`. Subagents that have WebFetch use it for non-SEC pages.

## D7. `docs/build/` and the ledger (2026-11-11)
`docs/build/` holds v1's dated build logs, 28 files with hundreds of build-time figures. The ledger does not trace those figures one by one. It gives the folder one row, which passes only when a `docs/build/README.md` says the files are dated logs whose figures are as of their date. A stale claim in them that reads as current is still a finding when a reviewer or I find it by reading.

## D8. Owner's name in tracked files (2026-11-11)
The spec calls the owner [private name]. Tracked files under `docs/prepub/` say "the owner", because the public author name on every surface is Rishabb Shankar and these files become public with the merge.

## D9. Round 2 reads `round2_clean`, a copy without `tools/prepub/` (2026-11-11)
P8.1 says the copy sits at `$HOME/gdn-prepub/round2/` with `docs/prepub/` removed. `rm` is denied, so I left the folder out at extraction: `git archive prepub-audit | tar -x -C <dir> --exclude 'docs/prepub'`. That first copy still held `tools/prepub/`, whose `revert_check.py` lists finding IDs. So the reviewers read a second copy, `~/gdn-prepub/round2_clean/`, extracted with `--exclude 'tools/prepub'` as well. `docs/prepub/ERRATA.md` is copied in, because the README links to it and a reader can open it. The copy has no `.git`.

## D10. Gate failures caused by honest fixes (R11) (2026-11-11)
The full gate on the final tree prints `42 assertions, 4 failing, 2 warning` (`BASELINE.md`, After). The baseline printed `1 failing` (`N4`), which now passes. Each of the four failures is a check that every printed number is one the gate itself computes, or that `site/data.json` holds only the keys the gate knows. The audit added true figures the gate has no rule for. I did not weaken a sentence to pass, and the gate was not edited.

| Gate line | Numbers it names | Where they come from | Finding |
|---|---|---|---|
| `R2` | `0.20` | one standard error of an autocorrelation at n = 26, in the README's sign-test paragraph | F050 group (STAT-12) |
| `R2` | `117`, `6.7` | GD's January 2021 statement read as 117, and the guidance pace's average miss under that reading | F022 |
| `R2` | `43.1` | the guidance pace for 2023Q3, set beside GD's stated plan of 27 | F058 |
| `R2`, `K1` | `12.5`, `3.5`, `6.4` | the 2023 to 2024 split of the held-out comparison | F023 |
| `R2`, `K1`, `N1` | `0.76`, `0.95` | deliveries per registry event behind the 2026Q3 lock, and the realised figure | F034 |
| `K1` | `246`, `1,251` | counted events on airframes at least three years old | F033 |
| `N1` | `$826M`, `23.4%`, `$95M`, `2.7%`, `$5.0B`, `$185M`, `3.7%` | what GD reported by segment for 2026Q3 against the note's estimates | F013 |
| `Y1` | keys `public`, `public_since`, `reported_segments` | fields the dashboard needs to label the lock and to show GD's reported revenue | F005, F013 |

The gate caps each list at eight items, so later numbers of the same kinds may be hidden behind these. Every number on those surfaces is traced by the ledger (`LEDGER.csv`, 0 flagged), which is the check that covers them now.

## D11. S2 findings against preregistered rules become errata, not code changes (2026-11-11)
P6.1 says to fix every S1 and S2. Four findings ask for a change to a preregistered rule or to a file under `.github/` (the holder rule, the scope rule, the Pages trigger, the workflow's schedule). R7 and §8 say such a finding becomes an erratum. Each has an entry in `ERRATA.md`, a disclosure on the README where a reader meets the affected figure, and a step in `GO_PUBLIC.md`. Their status in `FINDINGS.md` is `erratum`.

## D12. The six stated quarter plans are scored as exploratory, and the headline stays (2026-11-11)
The sell-side reviewer found that GD stated a delivery plan for the quarter under way on six calls, and that the preregistered guidance pace ignores them (SELL-1). I checked each quote in the cached transcripts and searched every cached call for others. Six calls give a number; three more describe the quarter in words and are not scored. The preregistered baseline is what it is, so 6.9 stays the headline figure (R7). The six plans are in `data/quarter_plans.csv`, scored in `results/exploratory/sensitivity.md` (6.02, and the registry estimate closer in 12 of 26), and stated in the README's Results beside the headline and in the interview notes. The post keeps the preregistered figure and calls the baseline a pace I derived.

## D13. A script of mine emptied `tools/prepub/ledger_rules.py`; restored from the last commit (2026-11-11)
A one-line write in a scratch script opened the file for writing before reading it and left it empty. The file had been committed in `9c0f7b8` minutes earlier. I restored it with `git show HEAD:tools/prepub/ledger_rules.py > tools/prepub/ledger_rules.py` and re-applied the one batch of rule edits made since. Nothing else was lost. The rerun ledger and the nine plants (`LEDGER_SELFTEST.md`) show the rules work as before.

## D14. The fresh clone check used a second clone with Python 3.11 (2026-11-11)
P8.4 says `python3 -m venv .venv` in `~/gdn-prepub/clone`. This Mac's `python3` is 3.9.6, and `pip install -r requirements.lock` failed there: `No matching distribution found for contourpy==1.3.3`. The project's own environment is Python 3.11.16 and the workflows pin 3.11. That is a finding against the README, which gave no setup step (F099, fixed). `rm` is denied, so the check ran in a second clone, `~/gdn-prepub/clone2`, with `python3.11 -m venv .venv`. Results are in `BASELINE.md` under "Fresh clone". The first clone's failure is kept in `.build/logs/clone_check1.log`.

## D15. P5.4 is done, not cut (2026-11-11)
The plan first listed P5.4 as cut. The spec allows that cut for time only, and the clock had hours left. `daily.run` has direct tests in `tests/test_daily.py` (the `run` fixture, 13 tests, most from the merged outside commits). `tests/test_model_direct.py` now tests `truncated_mae`, `coverage_drift` and `holdout_metrics` against values rebuilt in the test from the data files.

## D16. Two refusals, neither routed around (2026-11-11)
- A compound command that contained `git reset -q <file>` (to unstage one file) was denied whole, as the deny rule on `git reset` intends. Nothing had been staged. I staged files by explicit path from then on.
- A second `urllib` fetch of the Motley Fool transcript of GD's 2026-10-30 call was denied by the session's classifier with no reason given. I did not retry it. A fetch agent read the same public page once and reported the speaker of one sentence, which let me add that call to `data/guidance.csv` (F054).

## D17. Round 2's copy held test comments with finding numbers (2026-11-11)
The copy for round 2 (D9) left out `docs/prepub/` and `tools/prepub/`, but `tests/test_prepub_text.py` in it carries comments such as `# F022`. My check for that (a `grep` with `--include`) failed on a shell glob and I did not rerun it before launch. The comments name finding numbers and one-line reasons, not the findings' text or the reviews. No round 2 report cites them.

## D18. The gate on the final tree (R11) (2026-11-11)
The last full gate, at `7a70d9e` on the merged main tree and again on the fresh clone (and before that at `8d07bf5` and `89de502`, with the same lines), prints `42 assertions, 4 failing, 3 warning`. The four failures are the four in D10. The lists differ a little from D10's because round 2 and round 3 added figures: `R2` now names `0.20, 117, 6.7, 43.1, 5.7, 12.5, 3.5, 6.4`; `K1` `12.5, 3.5, 6.4, 0.76, 0.95, 246, 1,251`; `N1` `117, 6.7, 0.76, $826, 23.4%, $95, 2.7%, $5.0`. The new ones are `5.7` (the guidance pace's miss under both readings of GD's calls, F091) and `117`, `6.7` in the note's footnote (F094). There is one new warning, `T3`: the 2026-10-30 call added for F054 is later than the calls the gate pins. The gate caps each list at eight, so other figures of the same kinds sit behind these; the ledger traces every figure on those surfaces (`rows 2864  flagged 0`).

## D19. The session paused overnight; the workflow committed; a real merge followed (2026-11-12)
The battery in D18 finished at 22:13 ET on 2026-11-11. The session then sat idle until 09:23 ET on 2026-11-12 (the machine's clock; nothing ran in between). A `git fetch` then showed two new commits on `origin/main` from the daily workflow, `1481ce0` (Daily snapshot 2026-11-12) and `8c7692f` (Daily update 2026-11-12). P8.5 says to merge them with a real merge commit and rerun P6.4.

- Trial merge on a throwaway branch, `prepub-mergecheck2`: two conflicts, `README.md` (the open quarter's snapshot date) and `report/note.html` (a sources line). Both files are generated.
- `git merge --abort` failed there with `fatal: Could not reset index file to revision 'HEAD'`, and `git switch` refused to leave a merge in progress. `git reset` and `git checkout` are denied, so I did not force it. I finished the merge where it stood: regenerated both files from the merged data with the audit's generators (`python -m gdn report`, `python -m gdn note`, then `make all`, `make claims`, `make pdf`), checked that no conflict marker remained and that the README differs from the audit's only in the lines that carry the snapshot date, and committed the merge (`bbf88fd`). Then `git switch prepub-audit` and `git merge --ff-only prepub-mergecheck2`, so the merge commit is on `prepub-audit` and no history was rewritten. For a few minutes one commit existed only on the throwaway branch; R3's "all work on `prepub-audit`" was bent to that extent.
- The whole battery was then run again on the merged tree (`BASELINE.md`, After).

## D20. Criterion 11 after the merge (2026-11-12)
After the merge, 59 of the 61 hashes in `RECORD_HASHES.txt` match. Two differ: `results/live/2026Q4_latest.json` and `results/live/2026Q4_path.csv`, the open quarter's working files, which the daily job rewrites every day. Each equals its version in `origin/main` `8c7692f` byte for byte. Everything D3 said must match exactly does: `predictions/`, the 2026Q3 lock and score files, every snapshot file that existed at P0.1, `docs/PREREGISTRATION.md` and `.github/`. By the criterion's literal words, which exempt only `.github/`, two hashes miss. By the reading logged in D3 before any of this happened, the criterion holds. `VERDICT.md` states both.
