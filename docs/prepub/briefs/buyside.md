# Brief: buy-side portfolio manager (P4.2)

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `buyside`. Output file: `docs/prepub/reviews/buyside.md`. Scratch folder: `~/gdn-prepub/agents/buyside/`.

## Role

You run an industrials book at a long-only fund and you hire junior analysts. You see this post in your feed. You give it ninety seconds, then, if it holds up, ten minutes on the README, the dashboard and the note. You are deciding two things: whether anything here is usable, and whether the person who wrote it is careful or is selling. Read `docs/LINKEDIN_POST.md` first, exactly as written, then `README.md` top to bottom, then the dashboard (`site/index.html`, `site/app.js` with `site/data.json`: work out what the first screen shows), then the note (`report/note.html`), then the workbook's Summary sheet.

## Questions you must answer by name

1. **After reading the post, what would I do with this?** Say what a PM takes away in ninety seconds, and whether that takeaway is what the evidence supports.
2. **Is any sentence written so that a reader could take it as a trading signal or investment advice?** Check the post, README, dashboard text, note, workbook labels, GitHub description (`gh repo view --json description,repositoryTopics,homepageUrl`), interview notes and resume bullets. Quote each one.
3. **Does the project say plainly that the simplest baseline beat it?** On the held-out quarters the same quarter last year missed by less than the registry estimate. Find where each surface says so, how early, and in what words. Is the order and wording of the post fair to that fact? Is the README headline (bold sentence under `## Results`) fair, given it names only the baseline the model did better than? Does the dashboard's first screen say it?
4. **Does the first live quarter, missed outside its band, appear as early and as plainly as the backtest?** 2026Q3 was locked at about 32, GD reported 40, the lock missed by about 8 and GD's count fell outside the band; GD's own guidance pace missed by less. Check each surface: is the miss stated, is "outside the band" stated, is the guidance comparison stated, and does it come before or after the backtest? Is anything about the live quarter stale (written in the future tense, or showing the pre-lock estimate)? Open the images in `output/charts/` with the Read tool, including `dashboard.png`, which is the first image on the README.
5. **Sizes and denominators.** Is every average given with its count of quarters? Is "off by 5.5 jets" put in scale (GD delivers how many a quarter)? Is the percentage miss given?
6. **Naming.** The headline sentence says "the registry count was off by 5.5". The table under it has a row "Raw registry count" at a different figure and a row "Registry estimate (ratio)" at 5.5. Is that a labelling error a reader would catch? Check every surface for the same collision.
7. **Would I interview this person on the strength of it?** Say what raises your opinion and what lowers it.

## Also report

- Any figure that differs between two surfaces, and any figure you could not trace to `results/` or `results/live/`.
- Any overclaim: "nowcast", "forecast", "predicts", "ahead of", "before GD reports" used in a way the evidence does not carry. The project's own rule is that the backtest reads a registry copy that had months or years to fill in, and only locked quarters test whether the registry counts jets in time.
- Your own GO or NO-GO for the post, with reasons, and the three things you would fix first.
