# Round 4 brief: attacker of the earlier audit (`attacker`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** An earlier audit ran three review rounds and many fix commits. It ended NO-GO, on three items it says only the owner can settle: F015, F016 and F081. Your job is to attack that audit's work. Find what it got wrong, what it closed without proof, and what changed after its last outside review.

**Your tree (informed):** `~/gdn-prepub/round4_clone_attack`, a clone of branch `prepub-audit` made for you. Its push URL is disabled. Use the read-only git commands in `round4_common.md` there. In this clone you read `docs/prepub/`, except any file named `round4_*`.

**Read first:**

- `docs/prepub/VERDICT.md`, `FINDINGS.md`, `DECISIONS.md`, `ERRATA.md`, `GO_PUBLIC.md`, `BASELINE.md`, `REVERT_TESTS.md` and `LEDGER_SELFTEST.md`.
- The `SOURCES_*.csv` files.
- The round 1 to 3 reviews in `docs/prepub/reviews/` (`grep -n` their headings, then read in windows).

**Answer each by number:**

1. **The verdict's measurements.** For each of the 13 rows in `VERDICT.md`'s criteria table, re-check what a read-only command can re-check at `HEAD`:
   - `shasum`;
   - `git diff --stat`;
   - status counts in `FINDINGS.md` by severity;
   - presence of the files and lines it cites.

   Mark each row `confirmed`, `wrong` (with evidence) or `cannot check by read-only command`.
2. **The unread delta.** No outside reviewer has read anything after `4ca7d35`. List every public sentence and figure that `git diff 4ca7d35..HEAD` changed in `README.md`, `docs/LINKEDIN_POST.md`, `report/note.html`, `site/` and the workbook. Check each against its source.
3. **Figures the audit itself added, against primary sources.**
   - The figures named in `DECISIONS.md` D10 and D18 (the gate lists), each checked against its source file or filing.
   - The hand-typed constants in `tools/prepub/ledger_rules.py`: the Marine Systems backlog, the "about 11" demonstrators, the years 2027 and 2028, the study's as-of date, the engine-type codes.
   - The newest row of `data/guidance.csv`, from GD's 2026-10-30 call, whose transcript is not cached. Check the quote, the speaker, the date and the number against a public transcript, read with WebFetch.

   SEC filings come by Python `urllib` only, as `round4_common.md` says.
4. **Wrong closures.** Look for fixes that broke something else, refutations that were wrong, rows marked `fixed` whose commit does not touch the surface named, and errata that should have been fixes. Pick 10 rows marked `fixed` at severity S1 or S2 at random, with a seeded random draw (record the seed), and re-verify each on the tree.
5. **The NO-GO.** Is it right? Does anything beyond F015, F016 and F081 block? Is any `fixed` row in fact still open? Is any open S3 really an S2 on a first-screen surface (the post, the README to the end of `## Results`, the dashboard's first screen, the note's first page, the workbook's Summary sheet)?
6. **The record.**
   - `shasum -a 256 predictions/2026Q3.json` must print `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`.
   - Run `git diff --stat 36fed31..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github`.
   - Check that every file it lists is explained by `DECISIONS.md` D20.
