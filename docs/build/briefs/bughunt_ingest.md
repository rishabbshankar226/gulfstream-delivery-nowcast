# Bug hunt: data ingest modules (read-only reader, 2026-10-19)

Scope: `src/gdn/faa.py`, `sec.py`, `data.py`, `events.py`, `fiscal.py`, `files.py` and `tests/test_faa.py`, `tests/test_sec.py`. Edit nothing and write no file.

Read every function in full, in windows of 120 lines. Look for real correctness defects: date and quarter boundary errors, fiscal-quarter edges, timezone mistakes, regexes that miss or over-match, wrong dedup keys, csv writers without `lineterminator="\n"`, non-atomic writes of tracked data, swallowed exceptions, mutable defaults, string-against-date comparisons, unstable sorts, encoding issues, HTTP retry and timeout gaps, None handling.

Report only defects you can justify by quoting the code: file and line, the quoted lines, a concrete input that gives wrong output or a crash, and whether you traced it or only judge it plausible. List what you ruled out in one line each. Under 600 words, no style issues.
