# Pre-publication audit

Before making this repository public, I ran a pre-publication audit of it, in agent-assisted sessions. Every file in this folder is the audit's own work: its rules, findings, reviews and checks. The project's results are in the [main README](../../README.md).

**Start here:** [`ROUND4_VERDICT.md`](ROUND4_VERDICT.md) is the current verdict, with what is still open and who must close it. [`VERDICT.md`](VERDICT.md) is the earlier verdict, kept as written; its header points to round 4.

**The files a skeptical reader will want:**

- [`ERRATA.md`](ERRATA.md): every place the code or the record departs from the preregistration, dated.
- [`LOCK_CHECK.md`](LOCK_CHECK.md) and [`RECORD_HASHES.txt`](RECORD_HASHES.txt): the 2026Q3 lock checked against its release, and the hash of every file in the record.
- [`FINDINGS.md`](FINDINGS.md): one row per finding, with its evidence, fix, commit and status.
- [`DECISIONS.md`](DECISIONS.md): each reading the audit took where its rules left a choice.
- [`GO_PUBLIC.md`](GO_PUBLIC.md): the steps I take myself to make the repository public.

**How to read the rest:**

- The reviews in `reviews/` are dated and superseded. Each one judged the tree as it stood that day. Many open with NO-GO, and most of what they found has since been fixed; `FINDINGS.md` gives each finding's status.
- `briefs/` holds the instructions each reviewer was given.
- `recompute/`, the `SOURCES_*.csv` files, `LEDGER.csv` and `LINKS.csv` are the raw checks behind the findings.
