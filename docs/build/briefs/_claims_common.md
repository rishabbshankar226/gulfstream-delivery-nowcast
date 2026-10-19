## Common rules for every claims sourcing brief

You work in `~/Desktop/projects/gulfstream-delivery-nowcast`. Write only your output JSON file and cached source files under your topic folder in `data/raw/sources/`; never edit anything else in the repository. Other checkers work in parallel in sibling folders; never touch theirs.

**Output.** A JSON list, written with `json.dump(..., indent=2, ensure_ascii=False)` and a trailing newline, of objects with exactly these keys:
`{"id", "text", "source_type", "url_or_accn", "quote", "retrieved_on", "sha256"}`
- `id`: short, stable, kebab-case with your topic's prefix (for example `pc-g700-first-delivery`).
- `text`: the sentence the research note will print. Plain, active voice, at most 35 words, no em dashes, none of these words: delve, leverage, elevate, seamless, robust, unlock, cutting-edge, game-changer, synergy, thrilled, "excited to share". Dates as YYYY-MM-DD. State only what the quote supports; every number in `text` must appear in `quote`. No cause unless the source states it.
- `source_type`: `filing` (SEC filing), `call` (an earnings call transcript), `press` (a GD or Gulfstream press release or news page), or `faa`.
- `url_or_accn`: the accession number (`0000040533-YY-NNNNNN`) for a filing, else the page URL.
- `quote`: verbatim from the source, 40 words or fewer, exactly as it appears in the cached text after the conversion below (whitespace collapsed to single spaces). Never paraphrase, never join two places with "...".
- `retrieved_on`: `2026-10-19`.
- `sha256`: the sha256 of the cached file's bytes (`shasum -a 256 <file>`), the .html or .htm you fetched, not the .txt.

**Fetching.** Save every source with curl into your topic folder and quote only from what you saved:
- SEC: `curl -sS --max-time 30 -A "$(head -1 ~/.sec_ua)" -o data/raw/sources/<topic>/<accn>-<file> "https://www.sec.gov/Archives/edgar/data/40533/<accn without dashes>/<file>"`. At most 5 SEC requests a second. Find a filing's files from `https://www.sec.gov/Archives/edgar/data/40533/<accn without dashes>/index.json`. GD's 2025 10-K is accession 0000040533-26-000006, file `gd-20251231.htm`.
- Other pages: `curl -sSL --max-time 60 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36" -o data/raw/sources/<topic>/<name>.html "<url>"`.
- Call transcripts already cached in `data/raw/sources/calls/` (Motley Fool and MarketBeat pages for GD's calls from 2020-01-29 to 2026-07-29, named `<call date>-<site>.html`) may be used as they are: cite their URL from `data/guidance.csv` or the page itself, and hash the existing file. Do not rewrite those files.
- Use WebSearch only to find URLs; never take a quote from a fetch tool's rendering.

**Converting and checking.** Text of a cached page:
`python3 -c "import html,re,sys; t=open(sys.argv[1],errors='replace').read(); t=re.sub(r'(?is)<(script|style).*?</\\1>',' ',t); t=re.sub(r'<[^>]+>',' ',t); print(re.sub(r'\\s+',' ',html.unescape(t)))" <file> > <file>.txt`
Confirm each quote with `/usr/bin/grep -F -c "<quote>" <file>.txt` (the shell's `grep` is a ugrep wrapper; use `/usr/bin/grep`). Only entries whose quote is found go in the output.

**Default to wrong under doubt.** If a source does not plainly support a claim, leave the claim out and say so in your final report. A missing claim is fine; an unsupported one is not. Time box: 45 minutes. Your final message lists the ids you wrote and any claim you could not source.
