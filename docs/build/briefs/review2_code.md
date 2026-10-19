# Brief: review round 2, code closures

Repository: `/Users/rishabbshankar/Desktop/projects/gulfstream-delivery-nowcast`. Output: `docs/build/review2_code.md`. Write only your output file; never edit the repository, never commit, push, pull, run `gh release` or `gh workflow`, and never run `make daily`, `make daily-core`, `gdn lock`, `gdn score` or `tools/rehearsal.py` in this folder (it rewrites a tracked file). Never touch `~/.sec_ua`, the gate or its cache. For anything that needs git or `gh`, work in throwaway clones and bare repositories under your own scratchpad, with a `gh` shim, as round 1's spec auditor did.

A finding has an id (R2C-1, R2C-2, ...), a file and line, a severity (blocking, major or minor), evidence (a quote or command output), and a concrete fix. No evidence, no finding. Default to wrong under doubt.

You get two inputs:
1. `docs/build/REVIEW.md`: round 1's findings and how each was closed. Your rows are the lock-path operator's (OPS-1 to OPS-8) and the spec auditor's (S1 to S12, T1 to T9). The original reports are `docs/build/review1_ops.md` and `docs/build/review1_spec.md`.
2. The diff since round 1: `git diff 062e00e..HEAD -- src tests tools Makefile .github`.

For every OPS and S row, say whether the closure holds: the fix does what the row says, the named regression test exists and fails when the fix is reverted (check at least the blocking and major rows by reverting in a copy), and the row's "open" or "no change" reasoning is sound. Then look for regressions the diff introduced: a path that now locks late, locks twice, rewrites a committed prediction, replaces a subset a lock depends on, loses a score, swallows an error that should stop the run, or breaks `make all`'s offline, byte-identical rebuild. Read §3.5, §3.6 and §3.11 of `/Users/rishabbshankar/Desktop/prompt library/gulfstream-delivery-nowcast/GULFSTREAM_NOWCAST_PROMPT.md` (in windows of 120 lines or less) for the rules. `.venv/bin/python -m pytest -q -p no:cacheprovider tests` must pass. Time box: 45 minutes.
