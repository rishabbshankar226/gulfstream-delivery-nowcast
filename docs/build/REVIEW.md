# Review

§7's review: three rounds at most, each finding with an id, a file and line, a severity, evidence, a fix, the commit that fixes it and the regression test that fails when the fix is reverted. Round 1 ran five fresh reviewers from briefs in `docs/build/briefs/review1_*.md`, launched together.

## Round 1

### Fact-checker (`docs/build/FACT_CHECK.md`)

All 32 claims resolve to a cached source by sha256, every quote is verbatim and at most 40 words, and 30 of 32 texts are supported as written.

| Id | File and line | Severity | Evidence | Fix | Commit | Regression test |
|---|---|---|---|---|---|---|
| FC-F1 | `docs/build/claims_product.json` (pc-g300-entry-timing) | minor | Text "the G300 should start in late '27 or early '28"; source "the onset of the 300, which late '27, early '28, somewhere in that", after the CEO says she no longer estimates entry into service | Deleted the claim and its sentence in the note, as §7 says; not softened | fact-check commit | `tests/test_claims.py::test_claims_the_fact_check_removed_stay_out` |
| FC-F2 | `docs/build/claims_product.json` (pc-g300-announced) | minor | Text "Gulfstream announced"; GD's 10-Q says "we announced", the filer being General Dynamics | Deleted the claim and its sentence | fact-check commit | same test |
| FC-F3 | `docs/build/claims_risks.json` (risk-tariffs) | minor | Supported by the FY2025 10-K, but the 2026Q2 10-Q reports tariff refunds after a February 2026 court ruling, so the present tense "continue to evolve" is stale | Dated the text to its filing: "In its 2025 annual report, GD said tariffs had not had a material impact on its results but reduced Aerospace operating margins by 30 basis points in 2025." Still supported by the same quote | fact-check commit | `tests/test_claims.py::test_claims_quotes_are_in_their_sources` keeps the quote tied to the cited filing |
