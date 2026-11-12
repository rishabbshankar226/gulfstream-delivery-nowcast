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
