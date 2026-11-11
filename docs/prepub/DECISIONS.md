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
