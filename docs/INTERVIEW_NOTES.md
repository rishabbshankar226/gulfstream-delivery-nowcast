# Interview notes: the Gulfstream delivery tracker

## The 60-second version

General Dynamics reports how many Gulfstream jets it delivered each quarter, and that count drives the Aerospace segment. I wanted to know how closely FAA registrations track it. I read every Gulfstream jet in the FAA's public registry, took the first sign that each one reached a customer, counted those dates in GD's fiscal quarters, and scaled the count by how many deliveries GD reported per registration over the four quarters before.

I fixed the rules on 12 design quarters and committed them before scoring 26 held-out quarters. Over those 26 quarters the registry count was off by 5.5 jets a quarter on average, against 6.9 for GD's guidance pace. The difference is not statistically distinguishable, and simply repeating the same quarter last year missed by less on average, 4.6. So I report it as a tracker, not as an edge.

The test that matters is live. On the day before each earnings release, the pipeline locks its estimate as a timestamped GitHub release with the file's sha256 in the notes, and scores it against GD's count when the filing lands. The first lock is scored when GD reports on 2026-10-30. The research note, the Excel model and the dashboard all read from the same files.

## How the registry count works

The FAA publishes a zip of every US-registered aircraft, current and cancelled. I keep the Gulfstream jet types, including the G280, which the registry files under its Israeli builder, IAI. For each airframe I take the earlier of two dates: a customer's registration certificate, or the cancellation of Gulfstream's own registration because the jet was exported. The date must fall within a year of the jet's first airworthiness date, which keeps out renewals and most used jets. Counting those dates by quarter gives a number that tracks GD's count, though not one for one, and the gap drifted from about two deliveries per event in 2016 to 0.72 in 2026Q2. So I scale this quarter's count by the last four quarters' ratio, which follows the drift.

## Questions I expect

**Why is GD's guidance the benchmark?**
Because it is what the street anchors on. If public registrations cannot beat the company's own outlook, they add little. GD stated a numeric full-year outlook covering 22 of the 26 held-out quarters; I spread it over the remaining quarters by each quarter's usual share. I also test against two rules of thumb: the same quarter last year and last quarter.

**What does the held-out result show, and what does it not?**
The backtest reads a registry copy from 2026-10-19, which had months or years to fill in. It shows how well the registry tracks Gulfstream deliveries after the fact. Only the locked quarters test whether it counts them in time. A band built from each quarter's earlier misses held GD's count in 18 of 26 quarters, but that band comes from a finished file, so it is likely too narrow live.

**Why no price target or rating?**
This is a delivery tracker, not a valuation, and it is a student project. The note turns the delivery estimate into Aerospace revenue only mechanically, at trailing revenue per delivery, and says so. A price target would need far more than one input I can measure.

**What did the locked quarter show?**
The first lock is for 2026Q3. My build estimate is 31.1 deliveries, with a band of 20.4 to 36.4. It locks on 2026-10-29, the day before GD reports on 2026-10-30, and the score is written to the repository automatically. One quarter will show how the method behaves live, not whether it works.

**What failed or surprised you?**
The registry's coverage of GD's count was lower in the early design years than my preregistered sanity check allowed, because the FAA keeps only an airframe's current certificate: a jet that changed hands loses its first owner's date. I stopped, checked the cause, and kept the rules as written rather than tuning them after the fact. I also learned that the G280 is filed under IAI, not Gulfstream, so a scope rule on the maker name would have dropped every mid-cabin jet. Two smaller surprises: GitHub's runner downloaded the registry even though it was expected to be blocked, and my Mac and the runner wrote different compressed bytes for identical data until I fixed the file header.

**What would you do next?**
Score more locked quarters before claiming anything. I found archived copies of the registry taken a few weeks after four past quarter ends; read as they stood then, they missed by less than the finished file, partly because a later file loses first-owner dates as jets change hands, but four quarters prove nothing, and I would want many more. I would also use flight-tracking data to date handovers more closely, and split the revenue estimate by model, since a G700 and a G280 carry very different prices.
