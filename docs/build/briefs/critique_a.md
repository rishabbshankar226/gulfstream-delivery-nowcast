# Brief: Impeccable critique, Assessment A (design review)

You are a design director reviewing a data dashboard. Write only your output file, `docs/build/critique_a.md`; never edit the repository.

Read `~/.claude/plugins/cache/impeccable/impeccable/4.5.2/skills/impeccable/reference/critique.md` sections "Assessment A: Design Review" and the reference material below it (cognitive load, heuristics, personas). Do not run the detector and do not read any detector output.

Inputs:
- Source: `site/index.html`, `site/style.css`, `site/app.js`. The figures come from `site/data.json`.
- Screenshots: `.build/shots/desktop_light.png` and `desktop_dark.png` (1280 px wide) and `phone_light.png` and `phone_dark.png` (390 px wide). Read them with the Read tool. The page is also served at http://127.0.0.1:8766/ if you want to load it in a browser tab of your own.

The rubric is the project's specification for this page, which you must judge against and never ask to change:
- Audience: a recruiter with two minutes. No definition codes, and never the words "MAE", "nowcast" or "backtest": say "average miss", "estimate" and "test on past quarters". Every figure stands beside a comparator, a baseline or GD's typical quarterly count.
- Top to bottom: header question and one-sentence result under the headline rule, with links; the live quarter (status provisional, locked with time in ET, or scored; big estimate with its band; registrations so far by cabin; GD's guidance pace; release date; after scoring GD's count and the miss); the estimate's path chart; the track record chart with five average-miss tiles (the lowest gets the accent only when a test allows the word "beat"); how it was tested; jets on Gulfstream's own registration as horizontal bars; what it means for GD (estimates and sensitivity tables); a five-line method.
- Look: the defense backlog dashboard's tokens and IBM Plex Sans (fixed), one ink colour, one accent, tabular figures, thin rules, no gradients, glass, heavy shadows, emoji or decorative icons. Dark mode through prefers-color-scheme. Reduced motion turns animation off. 1280 and 390 px both work with no sideways scroll. Every chart is a canvas with role="img", a label, and a table of the same figures beside it.

Return in your file: design-specificity verdict, Nielsen heuristic scores (0 to 4, with n/a where one cannot apply), cognitive load, emotional journey, 2 to 3 strengths, 3 to 5 priority issues tagged P0 to P3 with a concrete fix each (within the rubric: no font or colour changes), persona red flags (Alex, Sam, and a recruiter skimming for two minutes), minor observations. Time box: 25 minutes.
