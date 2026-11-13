# Round 4 brief: rendered artifacts and accessibility (`rendered`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You check what a reader actually sees: pixels, pages and cells, not source text. Earlier checks read the dashboard through a script standing in for `app.js`, and read the charts' numbers from their source. You look at the images themselves.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history.

**Look at:**

- Every PNG in `output/charts/`, and `site/preview.png`. Open each one with the Read tool.
- Every page of `output/GD_research_note.pdf` and `site/GD_research_note.pdf`. Use the Read tool with `pages`. Use `pypdf` in the tools environment for link annotations, fonts and page count.
- The workbook `output/gd_gulfstream_model.xlsx`. It stores formulas with no cached values. Recompute it with the `formulas` package in the tools environment, and list every cell that evaluates to an error.
- The dashboard. If you have browser tools for local pages, serve the copy with `~/Desktop/projects/gulfstream-delivery-nowcast/.venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory ~/gdn-prepub/round4/site`, run in the background. Then open `http://127.0.0.1:8765/` at a desktop width and at a 375 px phone width. If you have no such tools, say so under "Could not check". Then read `site/index.html`, `site/app.js` and `site/style.css` and work out what renders.

**Answer each by number:**

1. Every number drawn in each chart and in `site/preview.png`. Does it match its source in `results/`, `site/data.json` or `results/live/`? Give a table: image, number as drawn, source file and field, and match.
2. Are the charts current? Does the README's hero image show the scored 2026Q3 lock and GD's count? Are the legends, axis labels, units and dates right? Does any legend call the project's own guidance pace "GD's guidance"?
3. Does any chart, page or screen show the open 2026Q4 quarter's partial figure as if it were an estimate or a forecast?
4. The PDFs. Does every page carry its disclaimer in the footer? Do the link annotations go where their text says? Is there broken layout, clipped text, an overflowing table or a missing font? Are `output/` and `site/` the same file?
5. The workbook. List cells with errors. Does the Summary sheet show the same figures as the README and the note?
6. The dashboard.
   - Does the first screen show the live result honestly?
   - Does it work and stay readable at 375 px?
   - Are there console errors?
   - Do colour contrast, alt text on images and charts, and keyboard focus meet basic accessibility?
   - Does `og:image` point at an image that exists and is current?
7. What would a recruiter on a phone see first, and is it the right thing?
