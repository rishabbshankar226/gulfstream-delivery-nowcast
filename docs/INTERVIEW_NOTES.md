# Interview notes: the Gulfstream delivery tracker

## The 60-second version

General Dynamics reports how many Gulfstream jets it delivered each quarter, and that count drives the Aerospace segment. I wanted to know how closely FAA registrations track it. I read every Gulfstream jet in the FAA's public registry, took the first sign that each one reached a customer, counted those dates in GD's fiscal quarters, and scaled the count by how many deliveries GD reported per registration over the four quarters before.

I fixed the rules on 12 design quarters and committed them before scoring 26 held-out quarters. Over those 26 quarters my registry estimate was off by 5.5 jets a quarter on average, against 6.9 for GD's guidance pace. The difference is not statistically distinguishable, and simply repeating the same quarter last year missed by less on average, 4.6. So I report it as a tracker, not as an edge.

The test that matters is live. On the day before each earnings release, the pipeline locks its estimate as a timestamped GitHub release with the file's sha256 in the notes, and scores it against GD's count when the filing lands. The first lock, for 2026Q3, said 32.0 with a band of 21.2 to 37.2. GD reported 40 on 2026-10-30: a miss of 8.0, outside the band, and further off than GD's guidance pace (a miss of 6.2) or the same quarter last year (a miss of 1). The research note, the Excel model and the dashboard all read from the same files.

## How the registry count works

The FAA publishes a zip of every US-registered aircraft, current and cancelled. I keep the Gulfstream jet types, including the G280, which the registry files under its Israeli builder, IAI. For each airframe I take the earlier of two dates: a customer's registration certificate, or the cancellation of Gulfstream's own registration because the jet was exported. The date must fall no later than 365 days after the jet's first airworthiness date, which keeps out renewals and most used jets, though not all. Counting those dates by quarter gives a number that tracks GD's count, though not one for one, and the gap drifted from about two deliveries per event in 2016 to 0.72 in 2026Q2. So I scale this quarter's count by the last four quarters' ratio, which follows the drift.

## Questions I expect

**Why is GD's guidance the benchmark?**
Because GD's full-year outlook is the delivery number it gives most often, and I had no consensus data. If public registrations cannot beat the company's own outlook, they add little. The pace is my construction, not a figure GD publishes: GD stated a numeric full-year outlook covering 22 of the 26 held-out quarters, and I spread what was left of it over the remaining quarters by each quarter's usual share. On six calls GD also said how many aircraft it planned to deliver in the quarter then under way. My preregistered pace does not use those plans. With them in its place the baseline misses by 6.0 on average, not 6.9, and the registry estimate is closer in 12 of 26 quarters. An analyst who used GD's quarter figures was closer than my baseline shows. I also test against two rules of thumb: the same quarter last year and last quarter.

**Where did the lead over the guidance pace come from?**
From two years. In 2023 and 2024 the guidance pace missed by 12.5 jets a quarter on average and my estimate by 3.5. In the other 18 held-out quarters the guidance pace missed by 4.4 and my estimate by 6.4. So I do not claim the registry beats guidance.

**What does the held-out result show, and what does it not?**
The backtest reads a registry copy from 2026-10-19, which had months or years to fill in. It shows how well the registry tracks Gulfstream deliveries after the fact. Only the locked quarters test whether it counts them in time. A band built from each quarter's earlier misses held GD's count in 18 of 26 quarters, but that band comes from a finished file, so it is likely too narrow live.

**Why no price target or rating?**
This is a delivery tracker, not a valuation, and it is a student project. The note turns the delivery estimate into Aerospace revenue only mechanically, at trailing revenue per delivery, and says so. A price target would need far more than one input I can measure.

**What did the locked quarter show?**
The first lock was for 2026Q3. The GitHub workflow locked 32.0 deliveries, with a band of 21.2 to 37.2, at 01:51 ET on 2026-10-29, while the repository was still private. GD reported 40 the next day. The lock missed by 8.0, or 20.1%, outside the band. GD's guidance pace was 33.8, a miss of 6.2, and the raw registry count for the quarter was 42, a miss of 2. So the registry had the quarter's jets in time: the count had settled at 42 by the lock. What missed was my scaling, which took 0.76 deliveries per registry event from the four quarters before when the quarter came in at 0.95. One quarter is one data point.

**Why publish a model that lost to the same quarter last year?**
Because the result is the finding. I fixed the rules before I scored the held-out quarters, and the answer came back plainly: scaling FAA registrations missed by 5.5 jets a quarter, repeating the same quarter last year missed by 4.6, and no test separates my estimate from any baseline. Then the first live lock missed by 8.0, outside its band. I would rather show a test that was set up so it could fail, and say so when it did, than tune a rule until it wins on 26 quarters. Every number in it traces to a filing or a registry file.

**How did you build it?**
With Claude Code, an AI coding agent, in sessions I ran and directed. The build notes and the notes of a pre-publication audit are in the repository.

**What failed or surprised you?**
Used jets. By the registry's own year of manufacture, 246 of the 1,251 events I counted (19.7%) are airframes at least three years old. A used jet that gets a new US airworthiness date passes my one-year check. The registry's coverage of GD's count was also lower in the early design years than my preregistered sanity check allowed, because the FAA keeps only an airframe's current certificate: a jet that changed hands loses its first owner's date. I stopped, checked the cause, and kept the rules as written rather than tuning them after the fact. I also learned that the G280 is filed under IAI, not Gulfstream, so a scope rule on the maker name would have dropped every mid-cabin jet. Two smaller surprises: GitHub's runner downloaded the registry even though it was expected to be blocked, and my Mac and the runner wrote different compressed bytes for identical data until I fixed the file header.

**What would you do next?**
Score more locked quarters before claiming anything. I found archived copies of the registry taken a few weeks after four past quarter ends; read as they stood then, they missed by less than the finished file, partly because a later file loses first-owner dates as jets change hands, but four quarters prove nothing, and I would want many more. I would also use flight-tracking data to date handovers more closely, and split the revenue estimate by model, since a G700 and a G280 carry very different prices.
