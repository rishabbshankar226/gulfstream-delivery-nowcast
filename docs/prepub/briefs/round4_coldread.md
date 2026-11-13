# Round 4 brief: cold read of the changed first screens (`coldread`)

Read `round4_common.md` in this folder first. Its rules bind you, with two changes:

- Your tree is `~/gdn-prepub/round4b/`, a plain copy of the files with no git history.
- Your budget is 35 minutes.

**Who you are.** You are an equity research analyst who reads a junior colleague's work before it goes out. A round of fixes has just changed the text and figures below. You have not seen the earlier version, and you will not. Read what is there now.

**Read, in this order:**

1. `docs/LINKEDIN_POST.md`, all of it.
2. `README.md`, from the top to the end of `## Results`. Open its first image, `output/charts/track_record.png`, with the Read tool.
3. The dashboard's first screen. Use `site/index.html`, `site/app.js` and `site/data.json`. If you have browser tools for local pages, serve the copy with `~/Desktop/projects/gulfstream-delivery-nowcast/.venv/bin/python -m http.server 8767 --bind 127.0.0.1 --directory ~/gdn-prepub/round4b/site`, run in the background, and open it at a desktop width and at 375 px.
4. `output/GD_research_note.pdf`, pages 1 to 3 and the Risks and Limitations pages. Use the Read tool with `pages`.
5. The workbook `output/gd_gulfstream_model.xlsx`: the Summary and Live sheets. Recompute them with `formulas` in the tools environment.
6. `docs/RESUME_BULLETS.md` and `docs/INTERVIEW_NOTES.md`.

**Answer each by number:**

1. Is any figure on these screens wrong, or does any two surfaces' figures disagree? Check each figure against `results/`, `results/live/`, `predictions/2026Q3.json` and `data/`, by a command.
2. Is any sentence false, stale on 2026-11-12, contradictory, or misleading about who built the guidance pace or how well the band held?
3. Does the first chart show the 2026Q3 lock, its band and GD's count correctly? Is anything in it clipped or unreadable?
4. Do the post's first 140 and 210 characters carry the live result? Is the post under 1,300 characters?
5. Is anything on these screens a claim the evidence does not support, or a trading signal?

Write to `~/Desktop/projects/gulfstream-delivery-nowcast/docs/prepub/reviews/round4_coldread.md`, in the format `round4_common.md` gives.
