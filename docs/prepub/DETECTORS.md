# Detectors: plant results before use (§5)

No detector's output is used before its row here says its plants were caught.

| Detector | Plants | Result | Recorded | Ready to use |
|---|---|---|---|---|
| `ledger.py` (P1) | nine in P1.2 | 9 caught, 0 missed on the rerun. Plants 5 and 6 were missed on the first run; the ledger was fixed and all nine rerun. Detail in `LEDGER_SELFTEST.md` | 2026-11-11 19:30 ET | yes |
| Staleness check (part of the ledger) | plant 3 (future-tense verb) and plant 9 (no number, no future-tense verb) | both caught. Plant 9 is caught because the check admits a lock or score sentence only when a reviewed pattern matches it and that pattern's state holds in `results/live/` | 2026-11-11 19:30 ET | yes |
| Recompute (P2) | a five-quarter toy file, `docs/prepub/recompute/toy/` | match to 6 decimals. The subagent's script printed `toy.E1.mae_2002Q1_to_2003Q1 = 3.535991` and per-quarter absolute errors 5.777778, 7.350000, 0.769424, 1.276486, 2.506266; the main thread's hand value is 3.535991 with the same five errors (table below) | 2026-11-11 20:05 ET | yes |
| Link check (P3.4), `tools/prepub/links.py` | in `~/gdn-prepub/plant2/docs/PLANT_LINKS.md`: (1) an in-repo link to `_missing.md`; (2) `https://github.com/rishabbshankar226/this-repo-does-not-exist-xyz`; (3) `https://www.airport-data.com/aircraft/NZZZZZ.html`, which answers status 200 with the heading "Aircraft Not Found"; (4) control `https://rshankar.dev` | 3 caught, control passes. Printed: `_missing.md ... fails: no such file in the tree`; `this-repo-does-not-exist-xyz ... fails: status 404`; `NZZZZZ.html ... fails: 200 with a not-found title or heading`; `https://rshankar.dev ... resolves, "Rishabb Shankar \| Finance, software & AI"` | 2026-11-11 19:55 ET | yes |

## Recompute: the hand computation

Toy data (large, mid): GD deliveries 2001Q1 to 2003Q1 are (20,5) (22,6) (24,4) (30,7) (21,5) (25,5) (23,6) (31,8) (26,4). Registry E1 events are (16,4) (20,3) (18,5) (27,6) (15,2) (24,6) (20,4) (25,7) (22,5).

Ratio estimate per cabin is this quarter's events times the four prior quarters' deliveries over the four prior quarters' events.

| Quarter | Large | Mid | Total | GD | Absolute error |
|---|---|---|---|---|---|
| 2002Q1 | 15 x 96 / 81 = 17.777778 | 2 x 22 / 18 = 2.444444 | 20.222222 | 26 | 5.777778 |
| 2002Q2 | 24 x 97 / 80 = 29.100000 | 6 x 22 / 16 = 8.250000 | 37.350000 | 30 | 7.350000 |
| 2002Q3 | 20 x 100 / 84 = 23.809524 | 4 x 21 / 19 = 4.421053 | 28.230576 | 29 | 0.769424 |
| 2002Q4 | 25 x 99 / 86 = 28.779070 | 7 x 23 / 18 = 8.944444 | 37.723514 | 39 | 1.276486 |
| 2003Q1 | 22 x 100 / 84 = 26.190476 | 5 x 24 / 19 = 6.315789 | 32.506266 | 30 | 2.506266 |

Sum 17.679954, mean 3.535991. To four decimals: 3.5360. A plain arithmetic script printed `[5.777778, 7.35, 0.769424, 1.276486, 2.506266] 3.535991`.

## Link check: the 200 page

The page for plant 3 was found with Python `urllib`, not WebFetch: this session's main thread has no WebFetch tool of its own (logged in `DECISIONS.md` D6). The probe printed `status 200 | title: Add aircraft NZZZZZ`, `h1: ['Aircraft Not Found']`, and the body text "The aircraft with registration NZZZZZ was not found in our database." A status-only check passes it. The checker reads the title, the first headings and the visible body, and fails it.

The same probe showed a second kind of false 200: `https://pypi.org/project/this-package-does-not-exist-xyz-123/` answered 200 with the title "Client Challenge", a bot-check page. The checker marks such a page `blocked: 200 with a bot challenge page (check by hand)` and never `resolves`.

Limit: a registry mirror can answer 200 for an unknown tail number with a normal-looking page. `https://www.flightaware.com/resources/registration/NZZZZZ` answered 200 with the title "NZZZZZ (Unknown Aircraft) Aircraft Registration". The pattern list now names "unknown aircraft", but a site with different words would pass. The audit's mirror links are therefore also read for their title in `LINKS.csv`.
