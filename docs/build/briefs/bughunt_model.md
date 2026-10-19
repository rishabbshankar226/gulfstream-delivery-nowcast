# Bug hunt: model and outputs (read-only reader, 2026-10-19)

Scope: `src/gdn/model.py`, `stats.py`, `errors.py`, `estimates.py`, `diagnostics.py`, `claims.py`, `site_data.py`, `report.py`, `workbook.py`, `site/app.js`, and `tests/test_model.py`, `test_outputs.py`, `test_site_a11y.py`, `test_claims.py`. Edit nothing and write no file.

Read every function in full, in windows of 120 lines. Look for real correctness defects: wrong statistics (Holm step-down, one- against two-sided p-values, ddof, a zero denominator), future data leaking into a held-out quarter, rolling-window off-by-ones, NaN propagation, rounding that changes a headline, misaligned joined series, JavaScript that breaks on null fields or an empty array, JavaScript dates parsed in local time, csv writers without `lineterminator="\n"`.

Report only defects you can justify by quoting the code: file and line, the quoted lines, a concrete input that gives wrong output or a crash, and whether you traced it or only judge it plausible. List what you ruled out in one line each. Under 600 words, no style issues.
