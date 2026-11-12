# Round 4 brief: FAA registry and data engineer (`registry`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You have built pipelines on the FAA's releasable aircraft database. You know its MASTER, DEREG and ACFTREF files and how their fields go wrong.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history. You read the code in `src/gdn/`, the data in `data/` (the stored snapshot subsets in `data/snapshots/` included) and the tests in `tests/`. You may import the project's code read-only in scripts in your scratch folder, and run it on the stored subsets. Never on a download: never fetch the FAA zip.

**Read:** the README's `## Method`, `## Data` and `## Limitations`, `docs/PREREGISTRATION.md`, then `src/gdn/faa.py`, `events.py`, `data.py`, `fiscal.py`, `model.py` and `files.py`, and wherever else snapshot storage and hashing live (`grep -rn sha256 src/gdn`).

**Answer each by number, with `file:line` evidence of presence or absence:**

1. The airframe key: the first three characters of the maker-model code plus the serial. Can two airframes collide, or one airframe split into two keys? Test it on the stored subsets.
2. The E1 and E2 dates and the 365-day airworthiness window. Are they computed as the README and the preregistration state? Are the edge cases handled: a missing airworthiness date, the year-of-manufacture fallback, the one-sided bound?
3. Used-jet leakage: how many counted events are on airframes old enough to be used jets? Is that size stated where the count is shown?
4. The serials mapping and cabin classes: is any airframe filed under the wrong cabin, and does any such case change a count?
5. MASTER and DEREG: can one airframe be counted twice across them? How do deregistration reasons (exports, destroyed, sold) move the count?
6. The holder rule (registrant names starting `GULFSTREAM AEROSPACE`) and the scope rule (engine-type codes). What do they miss? Are those misses disclosed with their size?
7. Snapshot integrity: are the stored subsets hashed and reproducible from what the README says? Does the manifest match the files?
8. Fiscal quarter mapping for GD's quarter ends, and timezone and DST handling in the date logic. Is there an off-by-one at a quarter boundary?
9. Silent `except` blocks, broad catches, or fallbacks that could change a count without a trace.
