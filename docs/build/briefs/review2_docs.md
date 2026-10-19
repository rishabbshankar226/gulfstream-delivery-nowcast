# Brief: review round 2, document closures

Repository: `~/Desktop/projects/gulfstream-delivery-nowcast`. Output: `docs/build/review2_docs.md`. Write only your output file; never edit the repository, never commit, push or run `make` targets that write tracked files. Never touch `~/.sec_ua`, the gate or its cache.

A finding has an id (R2D-1, R2D-2, ...), a file and line, a severity (blocking, major or minor), evidence (a quote or command output), and a concrete fix. No evidence, no finding. Default to wrong under doubt.

You get two inputs:
1. `docs/build/REVIEW.md`: round 1's findings and how each was closed. Your rows are the fact-checker's (FC-F1 to FC-F3), the analyst's (A, C and O ids) and the numbers checker's (N ids). The original reports are `docs/build/FACT_CHECK.md`, `docs/build/review1_analyst.md` and `docs/build/review1_numbers.md`.
2. The diff since round 1: `git diff 062e00e..HEAD -- README.md docs report site src/gdn/note.py src/gdn/report.py results`.

For every row, say whether the closure holds in every place the row names: `README.md`, `report/note.html` and the PDF `output/GD_research_note.pdf` (render its pages to PNG with `swift tools/pdfpages.swift output/GD_research_note.pdf <your scratch dir>` and read them), `docs/LINKEDIN_POST.md`, `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md`, and the captions `site/app.js` builds from `site/data.json`. For each "open" or "no change" row, say whether the reasoning holds.

Then look for regressions in the new text. Recompute every figure the round 1 fixes added (for example the 5.3 and 4.6 on the 22 sourced quarters, the coverage ratios 0.69, 0.69 and 0.72 against the 1.18 mean, the lag-event counts 206 against 203 and 146 against 63, the 79 first-half deliveries and the 47 best quarter, the yearly table's two-decimal means, and "within a few jets" for mid cabin since 2022) from `results/`, `data/processed/` and `results/exploratory/`. Check that the headline rule still holds everywhere (§3.4 of `~/Desktop/prompt library/gulfstream-delivery-nowcast/GULFSTREAM_NOWCAST_PROMPT.md`), that §2's framing sentence still appears where it did, that nothing says the project counts jets before GD reports them, that the note is still 4 to 8 pages, and that no em dash appeared. Time box: 45 minutes.
