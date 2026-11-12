# Round 4 brief: line editor (`editor`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are a financial publication's line editor. You read every public sentence once, slowly. You trust no sentence that a file in the tree contradicts.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history.

**Read every sentence of:**

- `docs/LINKEDIN_POST.md` and `README.md`.
- The dashboard's text: `site/index.html`, every user-facing string in `site/app.js`, and every text field in `site/data.json`.
- The note: `report/note.html`, plus the PDF's text if it differs (read `output/GD_research_note.pdf` with the Read tool).
- The workbook's text cells (sheet names, headers, notes), read with `openpyxl`.
- `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md`, `docs/PREREGISTRATION.md`, `docs/prepub/ERRATA.md`, `results/*.md`.
- The index or README of `docs/build/`, and a sample of its files.

**Answer each by number:**

1. **Staleness.** Today is 2026-11-12 and the 2026Q3 lock is scored. Find every sentence that is false or stale on that date: a future tense about a past event, an "as of" date that is out of date, or a claim about the live record that `results/live/` contradicts. Read the scored state in `results/live/2026Q3_score.json` and `results/live/2026Q3_lock.json` first.
2. **Contradictions between surfaces.** One fact told two ways: a figure, a date, a count, a name for the same thing (for example, what the guidance baseline is called on each surface). List each pair with both `file:line` locations.
3. **Units and rounding.** Deliveries per registry event against registry events per delivery. Percent of what. A figure rounded one way on one surface and another way elsewhere.
4. **Style rules the owner set.**
   - First person.
   - Plain active sentences.
   - No em dashes or en dashes in prose; a range uses "to".
   - None of these words: elevate, seamless, leverage, robust, cutting-edge, game-changer, delve, unlock, harness, journey, landscape, powerful, insights.
   - No claim of cause unless a filing or a GD call states it, cited.

   Grep for the words and the dash characters (U+2014, U+2013) on every surface, and report each hit with `file:line`.
5. **Framing rules the owner set.**
   - The backtest reads a registry copy that had months or years to fill in.
   - Only locked quarters test whether the registry counts jets in time.
   - No sentence may say the project counts jets before GD reports them, or that it beats GD or the market.

   Find every sentence that breaks one of these rules, or comes close.
6. **Jargon.** Which terms would a recruiter with a finance degree, but no statistics or FAA background, fail to parse on the post and the README's first screen? Is each one defined where it first appears?
7. **Leftovers.** TODOs, placeholder text, internal codes or finding numbers, or notes to self that a public reader would see.
