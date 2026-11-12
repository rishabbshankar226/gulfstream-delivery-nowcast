# Post alternates (P7.2)

The post itself is `docs/LINKEDIN_POST.md`, written by `src/gdn/report.py` (`post`). These two alternates are not generated. Each uses only figures that the generated post carries and the ledger traces (32.0, 40, 8.0, 80%, 6.2, 39, 1, 26, 5.5, 6.9, 4.6); a script checked that neither holds a number the generated post lacks. Character counts are Python `len`, with the final newline.

## Alternate A: leads with the question, then the miss

Leads with what the project asks and does; the second line is the live miss with its comparisons. 1197 characters.

```
Do FAA aircraft registrations track the Gulfstream jets General Dynamics (GD) reports each quarter? I built a tracker to test that, and it locks an estimate on GitHub the day before GD reports.
The first locked quarter missed. For 2026Q3 I said 32.0 and GD reported 40: off by 8.0 jets, outside my 80% band of past misses. A pace I derived from GD's own full-year outlook missed by 6.2, and last year's same quarter (39) by 1. The repository was private then; the timestamp is GitHub's.

On 26 past quarters held out from setting the rules, the tracker was off by 5.5 jets a quarter on average, against 6.9 for that guidance pace. The difference is not statistically distinguishable, and simply repeating the same quarter last year missed by less, 4.6. That test reads a registry copy that had months or years to fill in, so only locked quarters show whether it counts jets in time. One quarter is one data point.

Dashboard: https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/
Code and data: https://github.com/rishabbshankar226/gulfstream-delivery-nowcast

Student project, not investment advice. I am not affiliated with General Dynamics or Gulfstream.

#EquityResearch #Aerospace
```

## Alternate B: leads with the baseline that won

Leads with the fact a reader will hold against the project: the same quarter last year was closer, live and on the backtest. 1252 characters.

```
The simplest rule beat my model: for 2026Q3 I locked an estimate of 32.0 Gulfstream deliveries, General Dynamics (GD) reported 40, and last year's same quarter was 39.
The model is a tracker I built that scales FAA aircraft registrations into an estimate of the jets GD reports each quarter, and locks it on GitHub the day before GD reports.

The miss was 8.0 jets, outside my 80% band of past misses. A pace I derived from GD's own full-year outlook missed by 6.2. The repository was private at the lock; the timestamp is GitHub's.

The same held on 26 past quarters held out from setting the rules: the tracker was off by 5.5 jets a quarter on average, against 6.9 for the guidance pace, a difference that is not statistically distinguishable, and repeating the same quarter last year missed by less, 4.6. That test reads a registry copy that had months or years to fill in, so only locked quarters show whether it counts jets in time. One quarter is one data point.

Dashboard: https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/
Code and data: https://github.com/rishabbshankar226/gulfstream-delivery-nowcast

Student project, not investment advice. I am not affiliated with General Dynamics or Gulfstream.

#EquityResearch #Aerospace
```

## Check against P7.1

| Rule | A | B |
|---|---|---|
| Under 1,300 characters | 1197 | 1252 |
| First two lines carry the live result and what the project is | yes: line 1 what it is, line 2 the result | yes: line 1 the result, line 2 what it is |
| Names the baseline that beat the model | "repeating the same quarter last year missed by less, 4.6" | first line, and again in the backtest paragraph |
| Says the backtest reads a finished registry | "reads a registry copy that had months or years to fill in" | same sentence |
| One disclaimer line | yes | yes |
| Links resolve once public | the same two links as the post (`POST_CHECK.md`) | same |
| No hashtag names a ticker | `#EquityResearch #Aerospace` | same |
| Every figure traced | all figures are in the generated post | same |

## One caution

The preregistration fixes the headline sentence word for word ("Over 26 held-out quarters the registry count was off by X jets a quarter on average, against Y for <baseline>. The difference is not statistically distinguishable."). The generated post carries it and adds a clause saying what "registry count" and the pace mean. Both alternates reword it ("the tracker", "that guidance pace"). If you post either one, add an entry to `ERRATA.md` saying so, as E10 does for the dashboard's lead.
