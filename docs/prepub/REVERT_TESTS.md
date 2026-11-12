# Regression tests against reverted fixes (R6)

Scratch clone: `~/gdn-prepub/scratch/revert5`. Written by `tools/prepub/revert_check.py`. For each fix the old behaviour is put back in the clone (one targeted edit, or the whole file as it stood at `origin/main` `36fed31`), the test is run, the file is restored from this repository, and the test is run again.

| Finding | File reverted | Test | With the fix reverted | With the fix restored |
|---|---|---|---|---|
| F001 | `src/gdn/daily.py`, one edit | `tests/test_daily.py::test_the_daily_rebuild_redraws_the_charts` | FAIL: `1 failed in 0.12s` | PASS: `1 passed in 0.08s` |
| F004 | `src/gdn/note.py`, one edit | `tests/test_prepub_text.py::test_the_release_date_claim_is_cited_only_while_the_release_is_ahead` | FAIL: `1 failed in 1.32s` | PASS: `1 passed in 1.40s` |
| F005 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_a_lock_is_called_public_only_if_the_repository_was_public_that_day` | FAIL: `2 failed, 2 passed in 5.88s` | PASS: `4 passed in 6.10s` |
| F009 F013 (dashboard) | `site/app.js` as at `36fed31` | `tests/test_site_a11y.py::test_a_scored_lock_states_its_miss_and_its_band_in_the_past_tense` | FAIL: `1 failed in 3.31s` | PASS: `1 passed in 1.31s` |
| F013 (note) | `src/gdn/note.py`, one edit | `tests/test_prepub_text.py::test_the_note_sets_gd_reported_revenue_beside_each_estimate` | FAIL: `1 failed in 4.36s` | PASS: `1 passed in 2.06s` |
| F013 (data) | `src/gdn/live.py`, one edit | `tests/test_live.py::test_what_gd_reported_by_segment_is_kept_for_a_scored_quarter` | FAIL: `1 failed in 0.14s` | PASS: `1 passed in 0.20s` |
| F014 | `src/gdn/daily.py`, one edit | `tests/test_daily.py::test_a_manifest_merge_accepts_the_same_zip_downloaded_at_two_times` | FAIL: `1 failed in 0.09s` | PASS: `1 passed in 0.08s` |
| F017 | `src/gdn/live.py`, one edit | `tests/test_live.py::test_no_lock_from_a_subset_that_predates_the_quarter_end` | FAIL: `1 failed in 0.13s` | PASS: `1 passed in 0.11s` |
| F018 | `src/gdn/live.py`, one edit | `tests/test_live.py::test_a_lock_published_after_the_filing_is_not_scored` | FAIL: `1 failed, 1 passed in 0.13s` | PASS: `2 passed in 0.13s` |
| F020 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_the_post_counts_its_locked_quarters` | FAIL: `1 failed in 1.57s` | PASS: `1 passed in 1.73s` |
| F022 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_2021_reading_is_disclosed_with_its_effect_on_the_headline` | FAIL: `1 failed in 0.10s` | PASS: `1 passed in 0.10s` |
| F023 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_split_sentence_names_the_years_that_carry_the_lead` | FAIL: `1 failed in 0.11s` | PASS: `1 passed in 0.10s` |
| F012 F024 F029 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_readme_headline_names_the_baseline_that_won_and_explains_its_terms` | FAIL: `1 failed in 0.09s` | PASS: `1 passed in 0.09s` |
| F025 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_the_live_record_sets_the_lock_beside_the_other_misses` | FAIL: `1 failed in 1.24s` | PASS: `1 passed in 1.40s` |
| F030 | `src/gdn/note.py`, one edit | `tests/test_prepub_text.py::test_the_note_footer_carries_the_disclaimer_on_every_printed_page` | FAIL: `1 failed in 1.50s` | PASS: `1 passed in 1.39s` |
| F031 | `src/gdn/workbook.py` as at `36fed31` | `tests/test_outputs.py::test_the_workbook_carries_the_guidance_baseline_and_the_live_result` | FAIL: `1 failed in 0.66s` | PASS: `1 passed in 0.62s` |
| F034 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_lock_timing_sentence_reads_the_lock_and_the_later_snapshots` | FAIL: `1 failed in 0.11s` | PASS: `1 passed in 0.67s` |
| F050 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_design_choice_sentence_counts_the_quarters_where_the_definitions_differ` | FAIL: `1 failed in 0.15s` | PASS: `1 passed in 0.10s` |
| F108 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_the_post_counts_its_locked_quarters` | FAIL: `1 failed in 1.32s` | PASS: `1 passed in 1.37s` |
| F058 | `src/gdn/sensitivity.py`, one edit | `tests/test_prepub_text.py::test_gd_stated_quarter_plans_are_scored_beside_the_guidance_pace` | FAIL: `1 failed in 0.13s` | PASS: `1 passed in 0.14s` |

20 fixes checked, 20 with FAIL when reverted and PASS when restored, 0 otherwise.

Not in this table: F003 is a repair of six tests, whose failing state is the baseline run in `BASELINE.md` (`6 failed, 114 passed`) and whose passing state is the current suite. F048 corrects a comment, not code; its test (`tests/test_model.py::test_nearest_rank_positions_match_exact_arithmetic`) pins the behaviour the comment now describes.
