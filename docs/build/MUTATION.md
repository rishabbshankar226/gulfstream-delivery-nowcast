# Tests of the tests

`tools/mutate.py` copies the tree, confirms the clean copy passes, then breaks one rule at a time with a one-line edit and runs `pytest` (the browser test aside). **12 of 12 caught.**

| Rule | File | Original | Mutant | Failing tests |
|---|---|---|---|---|
| Header normalization | `src/gdn/faa.py` | `return re.sub(r"[^A-Z0-9]", "", h.replace("\ufeff", "").upper())` | `return h.replace("\ufeff", "").upper()` | tests/test_faa.py::test_header_normalization<br>tests/test_faa.py::test_headers_read_by_name_in_any_order<br>tests/test_faa.py::test_missing_column_is_named<br>tests/test_faa.py::test_comma_inside_a_name_falls_back_to_header_positions (+14 more) |
| Comma fallback | `src/gdn/faa.py` | `if len(row) != len(header):` | `if False:` | tests/test_faa.py::test_comma_inside_a_name_falls_back_to_header_positions<br>tests/test_faa.py::test_airframes<br>tests/test_faa.py::test_window_edges<br>tests/test_model.py::test_truncation_edge |
| Scope by model name | `src/gdn/faa.py` | `if ("GULFSTREAM" in mfr or "GULFSTREAM" in model) and` | `if ("GULFSTREAM" in mfr) and` | tests/test_faa.py::test_scope_keeps_iai_g280_and_drops_turboprop_piston_and_cessna<br>tests/test_faa.py::test_subset_is_header_plus_in_scope_rows_byte_for_byte<br>tests/test_faa.py::test_airframes<br>tests/test_faa.py::test_bound_drops_a_renewed_certificate |
| IAI cabin rule | `src/gdn/faa.py` | `cabin = "mid" if MID.search(model) or mfr.startswith(("IAI", "ISRAEL")) else "large"` | `cabin = "mid" if MID.search(model) else "large"` | tests/test_faa.py::test_scope_keeps_iai_g280_and_drops_turboprop_piston_and_cessna |
| Gulfstream-held prefix | `src/gdn/events.py` | `return name.strip().upper().startswith("GULFSTREAM AEROSPACE")` | `return name.strip().upper().startswith("GULFSTREAM AEROSPACE CORP")` | tests/test_faa.py::test_airframes |
| The bound | `src/gdn/events.py` | `timedelta(days=365)` | `timedelta(days=3650)` | tests/test_faa.py::test_airframes<br>tests/test_faa.py::test_bound_drops_a_renewed_certificate |
| Earliest date in E1 and E2 | `src/gdn/events.py` | `return min(xs) if xs else None` | `return max(xs) if xs else None` | tests/test_faa.py::test_airframes<br>tests/test_faa.py::test_window_edges |
| Window edge | `src/gdn/events.py` | `lo < r[key] <= top` | `lo <= r[key] < top` | tests/test_faa.py::test_window_edges<br>tests/test_model.py::test_truncation_edge |
| Zero rule | `src/gdn/model.py` | `return sum(y_lags) / len(y_lags)` | `return 0.0` | tests/test_model.py::test_ratio_zero_rule_uses_trailing_mean |
| Nearest rank | `src/gdn/stats.py` | `return s[math.ceil(p * len(s)) - 1] if s else None` | `return s[max(0, int(p * len(s)) - 1)] if s else None` | tests/test_model.py::test_nearest_rank_on_26 |
| Eve boundary | `src/gdn/live.py` | `return newest_snapshot == eve.isoformat() or t.hour >= LOCK_HOUR_ET` | `return newest_snapshot == eve.isoformat() or t.hour > LOCK_HOUR_ET` | tests/test_live.py::test_lock_due_rule<br>tests/test_live.py::test_eve_at_seven_pm_with_older_snapshot_locks<br>tests/test_live.py::test_no_second_lock<br>tests/test_live.py::test_rejected_push_resets_and_retries (+7 more) |
| Second lock | `src/gdn/live.py` | `if ops.release_view(tag):` | `if False:` | tests/test_live.py::test_existing_release_blocks_a_new_lock |
