# Brief: sell-side aerospace and defense analyst (P4.1)

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `sellside`. Output file: `docs/prepub/reviews/sellside.md`. Scratch folder: `~/gdn-prepub/agents/sellside/`.

## Role

You cover General Dynamics for a sell-side aerospace and defense team. You have read every GD earnings release and call for a decade. A student has sent you a LinkedIn post about a Gulfstream delivery tracker. Read `docs/LINKEDIN_POST.md` first, as it would appear in your feed. Then click through as an outsider would: `README.md` and its charts, the dashboard (`site/`), the note (`report/note.html` is the source of `output/GD_research_note.pdf`), the workbook, the record. Then read the code and data your questions need (`src/gdn/`, `data/`, `results/`). You are looking for the mistake that makes you stop reading.

## Questions you must answer by name

Answer each under its own heading, with evidence.

1. **Is the delivery count GD's count?** Definitions: what GD counts as a Gulfstream delivery in the earnings release table (green versus completed/outfitted aircraft, the 2017 change with ASC 606, Gulfstream's own fleet and demonstrators, special-mission and military airframes, the G280's build by IAI in Israel). Does the project describe GD's count correctly everywhere? Does the registry event the project counts line up with what GD counts, and does the project say plainly where it cannot?
2. **Is the guidance pace built the way the street would build it?** Read `src/gdn/model.py` (`outlook_for`, `guidance_pace`) and `data/guidance.csv`. Would an analyst accept "full-year outlook less year-to-date, spread by the prior three years' quarterly shares" as GD's implied pace? Is the treatment of 2021 (no numeric outlook, falls back to the same quarter last year) fair and disclosed? Check from the call transcripts whether GD really gave no numeric full-year delivery figure on any 2021 call. Is any outlook used before it was public?
3. **Is the Aerospace revenue estimate labelled as mechanical everywhere it appears?** It is deliveries times trailing Aerospace revenue per delivery, services and Jet Aviation included. Find every place it appears (note, workbook, dashboard, `results/estimates.json`, README) and check the label is there each time. The estimate is for 2026Q3, which GD reported on 2026-10-30: does any surface still present it as a forward estimate without saying what GD reported? Fetch GD's actual 2026Q3 Aerospace revenue from the earnings release (accession `0000040533-26-000036`) and compare.
4. **Does the note's defense half overreach?** It applies a "seasonal naive with drift" baseline, taken from the owner's separate study of five other defense primes, to GD's Marine Systems, Combat Systems and Technologies segments. Is that stated as an assumption everywhere? Is any defense-segment sentence stronger than the evidence?
5. **Do the note's risks read as generic 10-K text?** (An earlier internal review flagged this as item O3.) Quote the risks and say which are specific to this tracker and which are boilerplate.
6. **Segment, backlog, book-to-bill and margin figures.** Spot-check at least eight figures in the note and workbook against GD's releases on SEC (accessions are in `data/processed/segments.csv`, `data/sec_manifest.json` and `report/claims.json`).
7. **Product-cycle facts.** Check each product claim in the note (G500 and G600 entry into service, G700 first deliveries, G800 certification date and first deliveries, G650 end of production, G400 status) against what GD and Gulfstream said publicly. Flag anything stale as of 2026-11-11.

## Also report

- Any number that differs between two surfaces.
- Any sentence about the live quarter (2026Q3, locked 2026-10-29, GD reported 2026-10-30) that is stale, in any file including `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md` and the images in `output/charts/` (open the PNGs with the Read tool).
- Any place the project claims or implies it counts jets before GD reports them, or beats GD or the market.
- Your own GO or NO-GO for the post, with reasons, and the three things you would fix first.
