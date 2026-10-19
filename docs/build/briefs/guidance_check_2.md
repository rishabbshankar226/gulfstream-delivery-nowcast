# Brief: guidance check 2

You are a checker for a research project in `/Users/rishabbshankar/Desktop/projects/gulfstream-delivery-nowcast`. Write only your output file and cached pages; never edit anything else in the repository.

## Task

For each of these General Dynamics (GD) quarterly earnings calls, find the full-year Gulfstream aircraft delivery outlook GD stated on that call for the call's own calendar year:

2022-04-27, 2022-07-27, 2022-10-26, 2023-01-25, 2023-04-26, 2023-07-26, 2023-10-25, 2024-01-24, 2024-04-24

(Each date is the day GD released results and held its call. In January GD gives the outlook for the new year.)

## Reading rules (from the project's specification, §3.4)

- "About 160" reads 160. A range reads its midpoint. A stated change from a figure named in the same sentence applies to that figure ("five to six fewer than the 145" reads 139.5).
- A call that confirms the outlook without a number, or gives only a quarter's plan, states none: leave `outlook` blank.
- The 2025-07-23 call's transcripts read "$150 million to $155 million"; that reads as 150 to 155 aircraft, 152.5.
- `year` is the call's calendar year for every call here.
- Only GD's own speakers count (chairman and CEO, CFO, other executives), not analysts' questions. A figure an analyst states and the executive merely does not contradict is not GD's statement.
- Read the whole transcript, prepared remarks and Q&A. The operative statement is GD's latest full-year delivery number on that call. If two figures appear (for example a total and a large-cabin subset), the outlook is total Gulfstream new-aircraft deliveries for the year.

## Method

1. Find a transcript for each call with WebSearch (Motley Fool's fool.com transcripts, GD's investor relations site, Investing.com, Nasdaq, Yahoo Finance, Seeking Alpha and similar). When a page will not load, use another transcript of the same call.
2. Save each page you rely on with curl, never from a fetch tool's rendering:
   `curl -sSL --max-time 60 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36" -o data/raw/sources/calls/<call_date>-<site>.html "<url>"`
3. Convert to text and search it with grep:
   `python3 -c "import html,re,sys; t=open(sys.argv[1],errors='replace').read(); t=re.sub(r'(?is)<(script|style).*?</\\1>',' ',t); t=re.sub(r'<[^>]+>',' ',t); print(re.sub(r'\\s+',' ',html.unescape(t)))" data/raw/sources/calls/<file>.html > data/raw/sources/calls/<file>.txt`
   then `grep -o -i ".\{0,300\}deliver.\{0,300\}" data/raw/sources/calls/<file>.txt | head -40`, and also grep for "aircraft", "airplanes", "planes", "units", "G700", "outlook", "guidance".
4. Copy the operative quote exactly as it appears in the .txt file, whitespace collapsed, at most 60 words. Then confirm it with `grep -F -c "<quote>" <file>.txt` and record yes or no.

## Output

`docs/build/guidance_check_2.csv`, one row per call, written with Python's csv module and `lineterminator="\n"`, columns:

`call_date,year,outlook,quote,speaker,url,cached_file,grep_found,note`

- `outlook`: the number by the rules above, blank when the call states none.
- `quote`: the operative statement; for a call with no number, the statement that comes closest (a confirmation or a quarter's plan), or blank if deliveries never come up.
- `speaker`: name and title as the transcript gives them.
- `grep_found`: `yes` only when `grep -F` finds the exact quote in the cached .txt.
- `note`: how you read the number (for example "range 150 to 155, midpoint 152.5"), any other delivery figures on the call, and for a call with no transcript, every URL you tried.

Default to wrong under doubt: when a reading is uncertain, say so in `note` rather than smoothing it over. Time box: 45 minutes. Report in your final message the nine outlooks you recorded.
