# Brief: statistician (P4.3)

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `statistician`. Output file: `docs/prepub/reviews/statistician.md`. Scratch folder: `~/gdn-prepub/agents/statistician/`.

## Role

You are an applied statistician who referees forecasting papers. You read the post (`docs/LINKEDIN_POST.md`), then the README's Results, Error analysis and Method sections, then `docs/PREREGISTRATION.md`, then the code (`src/gdn/model.py`, `stats.py`, `events.py`, `live.py`, `fiscal.py`) and the data (`results/holdout.csv`, `results/design.csv`, `results/metrics.json`, `data/processed/`, `results/live/`, `results/exploratory/`). Recompute what you doubt with your own scripts.

## Questions you must answer by name

1. **Sign tests on 26 autocorrelated quarters.** Is a one-sided exact sign test the right test here? What does the reported lag-1 autocorrelation of the difference series do to it? Is the direction of the README's caveat correct for each baseline (one of the three autocorrelations is negative)? Would a Diebold-Mariano test with a small-sample correction, or a block or permutation approach, say anything different? Compute at least one alternative and report it.
2. **Holm across three tests.** Is the family right? Is anything gained or hidden by the correction when no raw p-value is below 0.05?
3. **E1 against E2 chosen on a 0.11 MAE gap over 12 quarters.** Is the choice meaningful? What do the held-out results look like under E2 (compute them from `data/processed/registry_quarterly.csv`)? Does the project say how fragile the choice is? Was anything else chosen in the design window that is not disclosed?
4. **A band that covers 69% against a nominal 80%, built from a finished registry file and applied at a live lock.** Is "past-miss band" described honestly everywhere? Is the Clopper-Pearson interval computed correctly (check the code and recompute)? Does any surface call it or imply it is a confidence or prediction interval? Is the live band for 2026Q3 (see `predictions/2026Q3.json`) built the way the preregistration says?
5. **Reconcile the truncation test with the live miss.** The truncation table's 30-day row gives an average miss of about 13.5, far worse than the live 2026Q3 miss of about 8.05, although the live lock was made 25 days after the quarter ended. Work out exactly what each number measures (read `truncated_mae` and `live.predict`), explain why they differ, and say whether the README's description of the truncation test could mislead a reader about live accuracy in either direction.
6. **Deliveries per event at 0.69 to 0.72 against a 1.18 mean.** What does this drift mean for the ratio model's validity? The registry now shows roughly 1.4 events per reported delivery where it showed fewer than 1 before. Is that explained anywhere with evidence? Does the README state the same quantity in inverse units elsewhere (registry events per delivery, in the Limitations)? Is the "mean plus two standard deviations" flag a meaningful check when the drift runs the other way?
7. **Is "not statistically distinguishable" the right phrase for each result?** For guidance pace (ratio better on average, p about 0.42), for the same quarter last year (ratio worse on average), for last quarter (ratio better, p about 0.16). Does the headline's wording hide that the model lost to a naive baseline?
8. **Is anything p-hacked, forked after the fact, or reported without its denominator?** Check the git history order (`git log --format='%h %ad %s' --date=iso -- docs/PREREGISTRATION.md results/metrics.json results/holdout.csv | tail -20`) to see whether the preregistration was committed before the held-out results. Check `results/exploratory/` and the README's as-of study: four quarters, three held out. Is "in all four the copy from a few weeks after the quarter missed by less" a fair sentence?
9. **The live record of one.** Is "One quarter shows how it works live, not whether it works" the right thing to say about n = 1? The miss fell outside an 80% nominal band whose realised coverage was 69%: what can and cannot be said?
10. **Averages and rounding.** Are any figures averages of rounded values, or percentages of the wrong base? Is the mean absolute percentage error the mean of per-quarter percentages (say so) and is it labelled so a reader does not take it for MAE over mean deliveries?

## Also report

- Any figure in the README, note (`report/note.html`), dashboard data (`site/data.json`) or post that your recomputation does not reproduce at the precision shown.
- Your own GO or NO-GO for the post, with reasons, and the three things you would fix first.
