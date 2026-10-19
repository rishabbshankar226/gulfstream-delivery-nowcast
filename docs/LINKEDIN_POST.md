How closely do FAA aircraft registrations track the Gulfstream deliveries General Dynamics reports? I built a tracker to find out. Its first real test comes on 2026-10-30, when GD reports 2026Q3 and I score the estimate I lock on GitHub the day before.

How I tested it: I counted each Gulfstream jet's first customer registration or export in a registry copy, scaled the count by the last four quarters, and checked it on 26 past quarters held out from setting the rules, against GD's guidance pace and two simple baselines.

Over 26 held-out quarters the registry count was off by 5.5 jets a quarter on average, against 6.9 for GD's guidance pace. The difference is not statistically distinguishable. Simply repeating the same quarter last year missed by less on average, 4.6. That test reads a registry that had years to fill in, so only the locked quarters show whether it counts jets in time.

Dashboard: https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/
Code, data and the research note: https://github.com/rishabbshankar226/gulfstream-delivery-nowcast

What public data would you add to sharpen a delivery estimate like this?

#GeneralDynamics #EquityResearch #Python
