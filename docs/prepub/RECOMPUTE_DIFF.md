# Recompute against the repository (P2.2)

The independent recompute is `docs/prepub/reviews/recompute.txt`, written by a subagent that read only the processed inputs, the stored registry subsets, the locked prediction, the preregistration and the README's Method text. It is copied here unchanged. This file is written by `tools/prepub/recompute_diff.py`.

A figure is `match` when the repository's value, printed to 6 decimals, equals the recomputed text. Every public surface shows at most 3 decimals, so a match at 6 is a match at the displayed precision.

| Figure group | Compared | Match | Result |
|---|---|---|---|
| 1 ratio estimate per quarter | 150 | 150 | match |
| 2 design window | 8 | 8 | match |
| 3 held-out summary | 31 | 31 | match |
| 4 held-out MAE by year | 35 | 35 | match |
| 5 sign tests and Holm | 18 | 18 | match |
| 6 lag-1 autocorrelation | 3 | 3 | match |
| 7 guidance pace per quarter | 84 | 84 | match |
| 8 past-miss band | 121 | 121 | match |
| 9 deliveries per registry event | 67 | 67 | match |
| 10 five largest misses | 10 | 10 | match |
| 11 the 2026Q3 score | 14 | 14 | match |
| 12 GD averages | 2 | 2 | match |
| 16 truncation table (extra) | 4 | 4 | match |

Total: 547 figures compared, 547 match, 0 differ.


## Repository figures the recompute file has no key for

None.
