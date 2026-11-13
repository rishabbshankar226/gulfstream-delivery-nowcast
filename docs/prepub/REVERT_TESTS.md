# Regression tests against reverted fixes (R6)

Scratch clone: `~/gdn-prepub/scratch/revert_round4b`. Written by `tools/prepub/revert_check.py`. For each fix the old behaviour is put back in the clone (one targeted edit, or the whole file as it stood at `origin/main` `36fed31`), the test is run, the file is restored from this repository, and the test is run again.

| Finding | File reverted | Test | With the fix reverted | With the fix restored |
|---|---|---|---|---|
| F001 | `src/gdn/daily.py`, one edit | `tests/test_daily.py::test_the_daily_rebuild_redraws_the_charts` | FAIL: `1 failed in 0.37s` | PASS: `1 passed in 0.08s` |
| F004 | `src/gdn/note.py`, one edit | `tests/test_prepub_text.py::test_the_release_date_claim_is_cited_only_while_the_release_is_ahead` | FAIL: `1 failed in 1.91s` | PASS: `1 passed in 1.70s` |
| F005 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_a_lock_is_called_public_only_if_the_repository_was_public_that_day` | FAIL: `2 failed, 2 passed in 7.91s` | PASS: `4 passed in 7.00s` |
| F009 F013 (dashboard) | `site/app.js` as at `36fed31` | `tests/test_site_a11y.py::test_a_scored_lock_states_its_miss_and_its_band_in_the_past_tense` | FAIL: `1 failed in 1.67s` | PASS: `1 passed in 1.26s` |
| F013 (note) | `src/gdn/note.py`, one edit | `tests/test_prepub_text.py::test_the_note_sets_gd_reported_revenue_beside_each_estimate` | FAIL: `1 failed in 2.02s` | PASS: `1 passed in 2.25s` |
| F013 (data) | `src/gdn/live.py`, one edit | `tests/test_live.py::test_what_gd_reported_by_segment_is_kept_for_a_scored_quarter` | FAIL: `1 failed in 0.12s` | PASS: `1 passed in 0.20s` |
| F014 | `src/gdn/daily.py`, one edit | `tests/test_daily.py::test_a_manifest_merge_accepts_the_same_zip_downloaded_at_two_times` | FAIL: `1 failed in 0.11s` | PASS: `1 passed in 0.09s` |
| F017 | `src/gdn/live.py`, one edit | `tests/test_live.py::test_no_lock_from_a_subset_that_predates_the_quarter_end` | FAIL: `1 failed in 0.12s` | PASS: `1 passed in 0.12s` |
| F018 | `src/gdn/live.py`, one edit | `tests/test_live.py::test_a_lock_published_after_the_filing_is_not_scored` | FAIL: `1 failed, 1 passed in 0.18s` | PASS: `2 passed in 0.13s` |
| F020 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_the_post_counts_its_locked_quarters` | FAIL: `1 failed in 2.64s` | PASS: `1 passed in 2.02s` |
| F022 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_2021_reading_is_disclosed_with_its_effect_on_the_headline` | FAIL: `1 failed in 0.16s` | PASS: `1 passed in 0.16s` |
| F023 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_split_sentence_names_the_years_that_carry_the_lead` | FAIL: `1 failed in 0.18s` | PASS: `1 passed in 0.10s` |
| F012 F024 F029 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_readme_headline_names_the_baseline_that_won_and_explains_its_terms` | FAIL: `1 failed in 0.12s` | PASS: `1 passed in 0.10s` |
| F025 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_the_live_record_sets_the_lock_beside_the_other_misses` | FAIL: `1 failed in 1.89s` | PASS: `1 passed in 1.90s` |
| F030 | `src/gdn/note.py`, one edit | `tests/test_prepub_text.py::test_the_note_footer_carries_the_disclaimer_on_every_printed_page` | FAIL: `1 failed in 1.99s` | PASS: `1 passed in 2.01s` |
| F031 | `src/gdn/workbook.py` as at `36fed31` | `tests/test_outputs.py::test_the_workbook_carries_the_guidance_baseline_and_the_live_result` | FAIL: `1 failed in 0.68s` | PASS: `1 passed in 0.56s` |
| F034 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_lock_timing_sentence_reads_the_lock_and_the_later_snapshots` | FAIL: `1 failed in 0.15s` | PASS: `1 passed in 0.51s` |
| F050 | `src/gdn/report.py`, one edit | `tests/test_prepub_text.py::test_the_design_choice_sentence_counts_the_quarters_where_the_definitions_differ` | FAIL: `1 failed in 0.10s` | PASS: `1 passed in 0.10s` |
| F053 | `src/gdn/charts.py`, one edit | `tests/test_prepub_text.py::test_the_dashboard_link_preview_image_follows_the_chart` | FAIL: `1 failed, 14 warnings in 1.06s` | PASS: `1 passed, 14 warnings in 0.91s` |
| F068 | `src/gdn/charts.py`, one edit | `tests/test_prepub_text.py::test_no_chart_legend_calls_the_pace_gds` | FAIL: `1 failed, 14 warnings in 0.90s` | PASS: `1 passed, 14 warnings in 1.00s` |
| F108 | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_the_post_counts_its_locked_quarters` | FAIL: `1 failed in 1.75s` | PASS: `1 passed in 1.74s` |
| F058 | `src/gdn/sensitivity.py`, one edit | `tests/test_prepub_text.py::test_gd_stated_quarter_plans_are_scored_beside_the_guidance_pace` | FAIL: `1 failed in 0.11s` | PASS: `1 passed in 0.13s` |
| F124 | `src/gdn/live.py`, one edit | `tests/test_live.py::test_a_lock_is_not_scored_when_sec_gives_no_acceptance_time` | FAIL: `2 failed in 0.21s` | PASS: `2 passed in 0.21s` |
| F109 | `src/gdn/note.py`, one edit | `tests/test_round4.py::test_the_note_states_why_gd_left_the_defense_study_as_the_filings_allow` | FAIL: `1 failed, 14 warnings in 3.28s` | PASS: `1 passed, 14 warnings in 2.87s` |
| F113 (post) | `src/gdn/report.py`, one edit | `tests/test_after_score.py::test_a_locked_and_scored_quarter_keeps_its_text` | FAIL: `1 failed in 1.40s` | PASS: `1 passed in 1.53s` |
| F113 (note) | `src/gdn/note.py`, one edit | `tests/test_round4.py::test_the_band_is_shown_with_its_coverage_in_the_note_and_the_workbook` | FAIL: `1 failed, 14 warnings in 2.65s` | PASS: `1 passed, 14 warnings in 2.49s` |
| F113 (workbook) | `src/gdn/workbook.py`, one edit | `tests/test_round4.py::test_the_band_is_shown_with_its_coverage_in_the_note_and_the_workbook` | FAIL: `1 failed, 14 warnings in 2.46s` | PASS: `1 passed, 14 warnings in 2.48s` |
| F113 (dashboard) | `site/app.js`, one edit | `tests/test_site_a11y.py::test_the_live_card_states_the_band_coverage_and_names_the_pace_as_mine` | FAIL: `1 failed in 1.57s` | PASS: `1 passed in 1.21s` |
| F114 (dashboard) | `site/app.js`, one edit | `tests/test_site_a11y.py::test_the_live_card_states_the_band_coverage_and_names_the_pace_as_mine` | FAIL: `1 failed in 1.22s` | PASS: `1 passed in 1.21s` |
| F114 F116 (note) | `src/gdn/note.py`, one edit | `tests/test_round4.py::test_the_notes_first_page_glosses_its_terms_and_says_where_the_edge_comes_from` | FAIL: `1 failed, 14 warnings in 3.13s` | PASS: `1 passed, 14 warnings in 3.29s` |
| F115 | `src/gdn/note.py`, one edit | `tests/test_round4.py::test_gds_stated_shape_of_the_year_and_the_even_split_sit_beside_the_pace` | FAIL: `1 failed, 14 warnings in 3.24s` | PASS: `1 passed, 14 warnings in 3.42s` |
| F117 | `src/gdn/charts.py`, one edit | `tests/test_round4.py::test_the_track_chart_draws_each_scored_lock_after_the_backtest` | FAIL: `3 failed, 2 passed, 14 warnings in 1.16s` | PASS: `5 passed, 14 warnings in 1.19s` |
| F118 | `site/app.js`, one edit | `tests/test_site_a11y.py::test_a_phone_keeps_the_baseline_that_won_on_the_track_chart` | FAIL: `1 failed in 1.82s` | PASS: `1 passed in 1.17s` |
| F119 | `src/gdn/note.py`, one edit | `tests/test_round4.py::test_the_note_does_not_say_it_reads_every_gulfstream_jet` | FAIL: `1 failed, 14 warnings in 3.31s` | PASS: `1 passed, 14 warnings in 3.40s` |
| F122 | `src/gdn/note.py`, one edit | `tests/test_round4.py::test_the_notes_risks_carry_the_mid_cabin_supplier_delay` | FAIL: `1 failed, 14 warnings in 3.22s` | PASS: `1 passed, 14 warnings in 3.25s` |
| F123 | `src/gdn/workbook.py`, one edit | `tests/test_round4.py::test_the_workbook_summary_does_not_say_a_baseline_beat_the_estimate` | FAIL: `1 failed, 14 warnings in 3.71s` | PASS: `1 passed, 14 warnings in 6.78s` |
| F130 | `src/gdn/report.py`, one edit | `tests/test_round4.py::test_the_readmes_first_screen_says_whose_pace_it_is` | FAIL: `1 failed, 14 warnings in 1.16s` | PASS: `1 passed, 14 warnings in 1.82s` |

37 fixes checked, 37 with FAIL when reverted and PASS when restored, 0 otherwise.

Not in this table: F003 is a repair of six tests, whose failing state is the baseline run in `BASELINE.md` (`6 failed, 114 passed`) and whose passing state is the current suite. F048 corrects a comment, not code; its test (`tests/test_model.py::test_nearest_rank_positions_match_exact_arithmetic`) pins the behaviour the comment now describes. Round 4's F125, F126 and F127 change tests only: F125 and F127 add direct tests of code that was already right (the neither-date bound and the old-airframe counts), and F126 moves tests off the tracked live files; F126's check against a 2026Q4-locked tree is in DECISIONS.md D24.
