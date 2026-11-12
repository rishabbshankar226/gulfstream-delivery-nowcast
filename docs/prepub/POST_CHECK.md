# Post check (P7.3)

Measured 2026-11-11 on `docs/LINKEDIN_POST.md` as `src/gdn/report.py` writes it (the generator refuses a post over 1,300 characters).

## Length

`len(open("docs/LINKEDIN_POST.md").read())` prints `1280` with the final newline, `1279` without. LinkedIn's limit is 3,000.

## What the feed shows before "see more"

First 210 characters (the desktop feed's cut):

> My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40. / My tracker scales FAA registrations into an estimate of the Gulfstream jets General Dynamics (GD) 

First 140 characters (the mobile feed's cut):

> My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40. / My tracker scales FAA regist

Both cuts carry the live result in full (32.0 against 40) and start the sentence that says what the project is. " / " marks a line break.

## Links

From `LINKS.csv`, rerun on the final tree:

| Link | Now | After |
|---|---|---|
| `https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/` | status 404: the repository is private and Pages is off | resolves after `GO_PUBLIC.md` steps 4 (make public) and 5 (enable Pages and run the pages workflow); the check is step 6, from a logged-out browser |
| `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast` | status 404: the repository is private | resolves after `GO_PUBLIC.md` step 4; same check |

## Content against P7.1

| Rule | Result |
|---|---|
| Under 1,300 characters | 1280 |
| First two lines carry the live result and what the project is | line 1: the miss, 32.0 against 40; line 2: what the tracker does and that it is locked the day before GD reports |
| Plain first person | yes |
| Names the baseline that beat the model | "Simply repeating the same quarter last year missed by less on average, 4.6", and "last year's same quarter (39) by 1" for the live quarter |
| Says what its two names mean | "(Registry count: my scaled estimate; the pace: mine.)", because the preregistered headline sentence says "registry count" and "GD's guidance pace" |
| Says the backtest reads a finished registry | "That test reads a registry copy that had months or years to fill in, so only locked quarters show whether it counts jets in time." |
| One disclaimer line | "Student project, not investment advice. I am not affiliated with General Dynamics or Gulfstream." |
| No hashtag names a ticker | `#EquityResearch #Aerospace` |
| Every figure traced | ledger, surface `post`: 12 rows, 0 flagged |
