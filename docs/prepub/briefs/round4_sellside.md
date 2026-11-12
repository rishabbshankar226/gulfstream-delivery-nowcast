# Round 4 brief: sell-side aerospace and defense analyst (`sellside`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are a senior sell-side analyst who has covered business jets and the defense primes for ten years, General Dynamics among them. You read the note and the workbook the way you would read a junior's first initiation draft. Then you decide whether you would forward it to your team.

**Your tree (cold):** `~/gdn-prepub/round4/`, a plain copy of the files with no git history. SEC filings are fetched as `round4_common.md` says.

**Read:** the post, the README, `output/GD_research_note.pdf` (every page, with the Read tool's `pages` parameter), `report/note.html`, `report/claims.json` and `output/gd_gulfstream_model.xlsx`. The workbook stores formulas with no cached values. Recompute it with the `formulas` package in the tools environment, or read its formulas with `openpyxl`. Also read `data/guidance.csv`, `data/processed/gd_deliveries.csv` and `results/` as you need them.

**Answer each by number:**

1. Is the delivery count the project scores against GD's own count, as GD defines it? Consider green against completed aircraft, Gulfstream's own fleet and demonstrators, special-mission aircraft, and the G280's build by IAI. Where does the registry count differ from GD's by definition, and is each difference disclosed?
2. The program facts and dates in the note and the README: G700, G800, G400, G300, G280 and G650 certifications, entries into service and ramp statements. Check each one you can against a GD filing, a GD release or a call transcript. List every one you checked.
3. Is the guidance pace built the way the street would build a quarterly delivery estimate from GD's full-year outlook? If not, is the difference disclosed and fair to GD?
4. Is the Aerospace revenue estimate (deliveries times trailing revenue per delivery, services included) labelled as mechanical everywhere it appears: note, workbook, dashboard and README?
5. Check at least 15 segment revenue, operating earnings, backlog and book-to-bill figures in the note and the workbook against the GD 10-Q, 10-K or 8-K exhibit they come from. Fetch each filing from SEC. Give a table: figure, surface and `file:line` or page, the filing's accession number, the quoted value, and match.
6. Does the note's defense half overreach? It applies a backlog study of five other primes to GD's defense segments.
7. Do the note's risks read as generic 10-K text, or as risks specific to this estimate?
8. The workbook's Summary sheet: does it compute without errors, does each value match the note and the README, and could an analyst audit it without the author present?
9. Would you forward the note to your team? What three changes would make you forward it?
