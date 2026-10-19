# Impeccable on the dashboard (Phase 7)

Run as the routing table says: `/impeccable critique`, then `audit`, then `polish`, answered from §3.10, with the backlog project's font and colours fixed and its per-edit hook ignored. The skill asks the user to choose priorities after a critique. Per §1 ("When a skill asks a question, answer it from this prompt; never pass it to the owner"), I answered from §3.10: fix every P1 and P2 inside the rubric, change no font, colour or section order, and keep the page's figures runtime-only.

## Critique

Method: dual-agent (A: design review, `docs/build/critique_a.md`; B: detector and browser evidence, `docs/build/critique_b.md`), each from a brief in `docs/build/briefs/`, isolated from the other.

- Assessment A: heuristics 20/32 (two n/a, read-only page), Acceptable. Design specificity: authored for this project. Five priority issues.
- Assessment B: static scan of `site/index.html` 0 findings. A rendered scan at 1280 px found 5 `line-length` warnings on text that `app.js` writes; 390 px was clean. No console errors, no sideways scroll, and every text contrast passes AA in both themes (body 15.79:1 light, 14.90:1 dark; muted 6.22:1 and 6.75:1).

Where they agree: the long prose blocks (A's chunking failure, B's line-length warnings).

| # | Finding | Severity | What changed |
|---|---|---|---|
| 1 | The lead named only GD's guidance pace while the same quarter last year missed by less; three sentences | P1 | The lead keeps the headline rule's wording; the line under it says "Simply repeating the same quarter last year missed by less" with its figure, then the framing sentence. The tiles now say how each average compares with the registry estimate. |
| 2 | Aerospace −18.3% unexplained beside +12.3%; sensitivity had no comparator | P1 | A sentence under the tables explains the gap from figures in data.json. The sensitivity table gained a change-on-the-year-ago-quarter column. Row labels shortened. Kept $B to one decimal, which §3.10 fixes; A's $M suggestion was not taken. |
| 3 | The path chart: a full-height canvas with one point | P2 | Short until three snapshots exist; the caption says how many snapshots there are and when the estimate locks; the box hides if path data is missing. |
| 4 | Six series told apart by dash pattern, unreadable at 390 px | P2 | At phone width the raw count, same-quarter and last-quarter lines start hidden; the caption says to select a name in the key. All five stay visible at desktop width, as §3.10 lists them. |
| 5 | Pipeline and truncation figures without comparators | P2 | The pipeline caption gives the total and the quarters of deliveries it equals at GD's typical quarter; registry model names read as G800, G500 and so on. The truncation table's caption carries GD's guidance pace on the same quarters. |
| B | Five line-length warnings at 1280 px | P2 | Prose capped at 62ch (14 px) and 58ch (13 px). The rendered scan is now clean. |
| minor | Error state named the README without a link | P3 | It now links it. |
| minor | "the day before" against "the evening before" | P3 | Both say the evening before. |
| minor | "Raw registry count" undefined | P3 | Defined in the track record caption. |
| minor | The live card never gave the lock date | P3 | It now says "Locks: the evening of 2026-10-29". |

## Audit

| # | Dimension | Score | Key finding |
|---|---|---|---|
| 1 | Accessibility | 4 | axe (wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa) passes at 1280 and 390 px in light and dark; skip link, h1 to h3 in order, labelled canvases with tables, focusable scroll regions, AA contrast throughout. |
| 2 | Performance | 3 | 328 KB with Chart.js 4.4.1 and one variable font; no images; one fetch. Charts redraw on a colour-scheme change only. |
| 3 | Theming | 4 | Every colour a token on `:root` with a dark set; app.js reads the tokens at draw time. |
| 4 | Responsive | 4 | One breakpoint at 760 px; no page overflow at 390 px; wide tables scroll inside labelled regions; links at least 24 px tall. |
| 5 | Implementation integrity | 4 | Detector clean, static and rendered; no decoration; product-specific structure. |
| | **Total** | **19/20** | Excellent |

## Polish

After the fixes: `tests/test_site_a11y.py` passes (8 tests), the gate's `site` family passes (5 assertions), and the rendered detector scan is clean. I read the screenshots at both widths in both themes.
