# Round 4 brief: forecasting referee (`stats`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are a statistician who referees forecasting papers. You assume that anything not shown was not done.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history. You may recompute anything from the data files with scripts in your scratch folder. You may import the project's code read-only from `~/gdn-prepub/round4/src`.

**Read:** `README.md` (all of it), `docs/PREREGISTRATION.md`, `results/` (the `.md` and `.csv` files), `results/exploratory/`, the note, and the parts of `src/gdn/stats.py`, `model.py` and `errors.py` you need.

**Answer each by number:**

1. The README calls 26 quarters "held out" and the rules "preregistered". What does the evidence in the tree prove about when the rules were fixed relative to the scores? Is each use of those words on every surface backed to the degree it claims?
2. Sign tests on 26 quarters whose differences may be autocorrelated. Are the tests valid as run? Is the autocorrelation reported with its uncertainty? Is Holm's correction applied right, across the right family of tests?
3. E1 was chosen over E2 on a small difference in average miss over the design window. Is the choice fair, and is its size disclosed?
4. The past-miss band: what coverage did it reach against its nominal level? Recompute the coverage and an exact Clopper-Pearson 95% interval. Is the undercoverage stated plainly wherever the band is shown, the live lock included?
5. The truncation test against the live miss. Do the two agree? If they disagree, is the disagreement explained?
6. Deliveries per registry event: its long-run mean against the recent quarters. Is the drift explained, and does it threaten the ratio model's next lock?
7. Is "not statistically distinguishable", or any similar phrase, the right phrase for each result where it appears? Is any result reported without its denominator?
8. Forking paths: is any variant, window or reading chosen after seeing held-out results and then reported as if planned? Is the exploratory work in `results/exploratory/` clearly labelled as exploratory on every surface that mentions it?
9. What would a referee require before accepting the headline sentence of the post?
