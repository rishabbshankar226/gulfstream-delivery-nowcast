# Brief: airframe audit 2

You check ten Gulfstream airframes against independent sources for a research project in `~/Desktop/projects/gulfstream-delivery-nowcast`. Write only `docs/build/AIRFRAME_AUDIT_2.csv` and cached pages under `data/raw/sources/audit/`; never edit anything else.

## Your ten airframes

```
serial,mfr_code,model,event,our_date,first_airworthiness,bound,export_country,n_numbers
6380,398,GVI (G650),export (E1),2019-09-06,2019-03-23,2020-03-22,MEXICO,N680GA
4307,398,GIV-X (G450),export (E1),2014-06-27,2014-02-28,2015-02-28,AUSTRIA,N307GA
6139,398,GVI (G650),export (E1),2015-08-21,2015-04-04,2016-04-03,BRAZIL,N639GA
5434,398,GV-SP (G550),export (E1),2014-02-20,2013-06-25,2014-06-25,AUSTRIA,N834GA
4076,398,GIV-X (G450),export (E1),2016-06-30,2016-01-22,2017-01-21,MEXICO,N407GA
6216,398,GVI (G650ER),export (E1),2017-01-17,2016-06-30,2017-06-30,MALAYSIA,N616GA
5557,398,GV-SP (G550),export (E1),2017-09-27,2017-03-01,2018-03-01,SPAIN,N557GD
6250,398,GVI (G650),export (E1),2017-06-22,2017-01-10,2018-01-10,ISLE OF MAN,N625G
6381,398,GVI (G650ER),export (E1),2019-08-21,2019-04-09,2020-04-08,CAYMAN ISLANDS,N681GD
6121,398,GVI (G650),export (E1),2015-06-12,2014-12-02,2015-12-02,CAYMAN ISLANDS,N621GD
```

`our_date` is the date the project's registry reading assigns:
- **domestic sale (E1)**: the first customer's FAA registration certificate, taken as the delivery date;
- **export (E1)**: the date Gulfstream's own FAA registration was cancelled for export to `export_country`, taken as the delivery date;
- **only under E2**: the date Gulfstream cancelled its own registration with no customer registration or export recorded;
- **removed by the bound**: a later registry date the project discards because it falls more than a year after the jet's first airworthiness date (`bound` is that limit), so the project counts no delivery for it.

GD's fiscal quarters (a delivery counts in the quarter whose window ends on the date shown and starts the day after the previous end; Q4 ends December 31): 2016Q1 ends 2016-04-03; 2016Q2 ends 2016-07-03; 2016Q3 ends 2016-10-02; 2016Q4 ends 2016-12-31; 2017Q1 ends 2017-04-02; 2017Q2 ends 2017-07-02; 2017Q3 ends 2017-10-01; 2017Q4 ends 2017-12-31; 2018Q1 ends 2018-04-01; 2018Q2 ends 2018-07-01; 2018Q3 ends 2018-09-30; 2018Q4 ends 2018-12-31; 2019Q1 ends 2019-03-31; 2019Q2 ends 2019-06-30; 2019Q3 ends 2019-09-29; 2019Q4 ends 2019-12-31; 2020Q1 ends 2020-03-29; 2020Q2 ends 2020-06-28; 2020Q3 ends 2020-09-27; 2020Q4 ends 2020-12-31; 2021Q1 ends 2021-04-04; 2021Q2 ends 2021-07-04; 2021Q3 ends 2021-10-03; 2021Q4 ends 2021-12-31; 2022Q1 ends 2022-04-03; 2022Q2 ends 2022-07-03; 2022Q3 ends 2022-10-02; 2022Q4 ends 2022-12-31; 2023Q1 ends 2023-04-02; 2023Q2 ends 2023-07-02; 2023Q3 ends 2023-10-01; 2023Q4 ends 2023-12-31; 2024Q1 ends 2024-03-31; 2024Q2 ends 2024-06-30; 2024Q3 ends 2024-09-29; 2024Q4 ends 2024-12-31; 2025Q1 ends 2025-03-30; 2025Q2 ends 2025-06-29; 2025Q3 ends 2025-09-28; 2025Q4 ends 2025-12-31; 2026Q1 ends 2026-04-05; 2026Q2 ends 2026-07-05. Before 2016, quarters end on the Sunday nearest the calendar quarter end, and Q4 on December 31.

## What to find

For each airframe, the date Gulfstream delivered it new to its first customer, from the best independent source you can find, in this order of preference:
1. a Gulfstream or GD press release (`release`);
2. trade press such as AIN, Flight Global, Business Jet Traveler, Corporate Jet Investor, or a government or air-force announcement (`press`);
3. the owner's or operator's own announcement (`owner`);
4. a registry mirror or aircraft history site (FlightAware registration pages, planelogger, rzjets, airfleets, globalair, tailno, JetNet listings and similar) (`mirror`). A mirror checks the registry parsing, not a delivery date.

Search by serial number ("G650ER serial 6316", "s/n 6316 Gulfstream"), by the N-numbers listed, and by the operator's name once you know it. Save every page you rely on with
`curl -sSL --max-time 60 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36" -o data/raw/sources/audit/<serial>-<site>.html "<url>"`
and confirm the date in the saved file (`/usr/bin/grep`), never from a fetch tool's rendering.

## Agreement rule

- domestic sale, export, only under E2: `agree` is `yes` when the source's delivery date (or, for a mirror, the same registry event) falls in the same GD fiscal quarter as `our_date`; otherwise `no`.
- removed by the bound: `agree` is `yes` when the source shows the airframe was delivered new before `bound`, so the discarded date was not its delivery; `no` when the source shows a first delivery on or after `bound`.
- A row with no usable source at all gets the best mirror you can find. If even that fails, `source_kind` is `none`, `agree` is `no`, and `note` lists what you tried.
- Default to wrong under doubt: if a source's date is ambiguous (a month only, an announcement of a future delivery, a resale), record `no` unless it clearly supports the same quarter, and explain in `note`.

## Output

`docs/build/AIRFRAME_AUDIT_2.csv`, written with Python's csv module and `lineterminator="\n"`, one row per airframe in the order above, columns:
`serial,model,event,our_date,source_url,source_date,source_kind,agree,note`
`source_date` is YYYY-MM-DD, or YYYY-MM when the source gives a month only. `note` names the operator, the source's exact wording for the date (at most 25 words), and the cached file name.

Time box: 50 minutes. Your final message lists each serial with its source kind and agree value.
