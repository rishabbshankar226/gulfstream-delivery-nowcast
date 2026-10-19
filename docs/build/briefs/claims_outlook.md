# Brief: claims, GD's outlook, what the street watches, and the business overview (prefixes `os-` and `bo-`)

Output: `docs/build/claims_outlook.json`. Cache folder: `data/raw/sources/outlook/`.

From GD's 2026-07-29 earnings call (cached at `data/raw/sources/calls/2026-07-29-fool.html`) and GD's filings:
1. `os-del`: GD's 2026 outlook of about 160 Gulfstream deliveries, as stated on the 2026-07-29 call.
2. `os-rev`: Aerospace revenue around $13.8 billion for 2026, as stated on that call.
3. `os-margin`: an Aerospace operating margin of 14.7% for 2026, as stated on that call.
4. `os-upside`: any stated upside or risk to the delivery outlook on that call (for example large-cabin upside, risk on the G280), with no number GD did not state.
5. `os-btb`: the book-to-bill sentence of GD's 2026Q2 earnings release (accession 0000040533-26-000029, Exhibit 99.1, file `gd-20260705exhibit991.htm`).
6. `os-marine-*`: what GD said on the 2026-04-29 or 2026-07-29 call, or in the 2026Q2 10-Q, about Marine Systems margins or what drives them (supply chain, labor, shipbuilding volume). Up to two claims.
7. `os-aero-margin-*`: what GD said about the drivers of Aerospace margin in 2026 (mix, G700 or G800 learning, costs). Up to two claims.
8. `bo-*`: from GD's 2025 10-K (accession 0000040533-26-000006, Item 1), one claim per segment saying what it does: Aerospace (Gulfstream aircraft and Jet Aviation services), Marine Systems, Combat Systems, Technologies.

Then read `docs/build/briefs/_claims_common.md` and follow it exactly.
