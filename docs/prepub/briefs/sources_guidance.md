# Brief: source check of GD's guidance rows (P3.2)

Read `docs/prepub/briefs/_common.md` first and follow it. Your name is `sources_guidance`. Output file: `docs/prepub/reviews/sources_guidance.csv`. Scratch folder: `~/gdn-prepub/agents/sources_guidance/`.

## Goal

Check every row of `data/guidance.csv` against the earnings call transcript it cites. The file has the columns `call_date,year,outlook,quote,speaker,url`, one row per GD earnings call from 2020-01-29 to 2026-07-29 (27 rows). `outlook` is the full-year Gulfstream delivery number the project read from the call, blank when the call stated none. The project's "guidance pace" baseline is built from these numbers, so a wrong number, a wrong date or a missed outlook changes a headline figure.

The reading rules the project fixed in advance (from `docs/PREREGISTRATION.md` §3.4): "About 160" reads 160; a range reads its midpoint; a stated change from a figure named in the same sentence applies to that figure ("five to six fewer than the 145" reads 139.5). A call that confirms the outlook without a number, or gives only a quarter's plan, states none. The 2025-07-23 call's transcripts read "$150 million to $155 million"; the project reads it as 150 to 155 aircraft, 152.5.

## For each row

1. Open the transcript at `url` with WebFetch. If it does not load or does not contain the call, find another transcript of the same call (Motley Fool, MarketBeat, Seeking Alpha, Yahoo Finance, Investing.com, GD's own investor site at `investorrelations.gd.com`, or a search) and record both URLs.
2. Is the quote in the transcript, word for word or close to it? Record `exact`, `close` (say what differs) or `absent`.
3. Is the speaker right (name and title at the time of the call)?
4. Is `call_date` the date the call was held? Check it against the transcript's own date line or GD's press release.
5. Is `outlook` the number the quote supports under the reading rules above? Is `year` the year the outlook covers?
6. For a row with a blank `outlook`: read the transcript's prepared remarks and the Q&A for any full-year Gulfstream delivery number (search the text for "deliver", "aircraft", "units", "this year", "full year", "for the year"). If the call did state a full-year delivery number that the project left blank, that is a finding: quote it. This matters most for the four 2021 calls, where the project says no call stated a full-year number, and for 2020 after the pandemic cut.
7. For a row with a number: was there a later or more specific number on the same call (for example in Q&A) that the project should have used instead?
8. The 2025-07-23 "$150 million to $155 million" reading: quote the sentence from two different transcripts if you can, and say whether reading it as 150 to 155 aircraft is the only sensible reading.

Also check the gaps: list GD's earnings call dates from 2020-01 to 2026-10 (GD holds four a year, in late January, April, July and October) and confirm every call up to 2026-07-29 has a row. The 2026-10-30 call (third quarter 2026) is after the project's data: say whether it stated a full-year delivery outlook and quote it, because the next live quarter (2026Q4) will need it.

## Output

`docs/prepub/reviews/sources_guidance.csv` with the header:

`call_date,year,outlook_csv,url_csv,url_loaded,other_url,quote_found,speaker_ok,date_ok,outlook_supported,other_number_on_call,status,note`

One row per row of `data/guidance.csv`, in the same order, then one extra row for the 2026-10-30 call with `status` `not in file`. `status` is `verified`, `verified elsewhere: <url>`, `mismatch: <what>` or `unverified: <why>`. Use `lineterminator="\n"`. Begin the file with comment lines (starting `#`) that give how you fetched.

Never paste more than 25 words of any transcript into the file. In your final reply give: the count by status, every mismatch in one line each, and what the 2021 calls said about full-year deliveries.
