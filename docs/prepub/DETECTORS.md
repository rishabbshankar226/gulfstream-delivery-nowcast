# Detectors: plant results before use (§5)

No detector's output is used before its row here says its plants were caught.

| Detector | Plants | Result | Recorded | Ready to use |
|---|---|---|---|---|
| `ledger.py` (P1) | nine in P1.2 | 9 caught, 0 missed on the rerun. Plants 5 and 6 were missed on the first run; the ledger was fixed and all nine rerun. Detail in `LEDGER_SELFTEST.md` | 2026-11-11 19:30 ET | yes |
| Staleness check (part of the ledger) | plant 3 (future-tense verb) and plant 9 (no number, no future-tense verb) | both caught. Plant 9 is caught because the check admits a lock or score sentence only when a reviewed pattern matches it and that pattern's state holds in `results/live/` | 2026-11-11 19:30 ET | yes |
| Recompute (P2) | a five-quarter toy file, `docs/prepub/recompute/toy/` | pending the subagent's toy figure. Main thread's hand value for the ratio MAE over 2002Q1 to 2003Q1: 3.535991 (per-quarter absolute errors 5.777778, 7.350000, 0.769424, 1.276486, 2.506266) | hand value 2026-11-11 19:05 ET | no, until compared |
| Link check (P3.4) | an in-repo link to `docs/_missing.md`, a link to a missing GitHub page, a page that returns 200 with a not-found body | pending | | no |

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
