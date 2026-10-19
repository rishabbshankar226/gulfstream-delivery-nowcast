# Fact check, review round 1

Reviewer: fresh fact-checker, built nothing here. Brief: `docs/build/briefs/review1_factcheck.md`. Date: 2026-10-19.

## Result

- 32 of 32 entries in `report/claims.json` resolve by sha256 to a cached file under `data/raw/sources/`.
- 32 of 32 quotes are verbatim in the source text and none is over 40 words (the longest is 39).
- 30 of 32 texts are supported as written. 2 are not: `pc-g300-entry-timing` and `pc-g300-announced`. Both are minor.
- 1 more entry, `risk-tariffs`, is supported by the filing it cites, but a newer cached GD filing has replaced that statement. It is a minor finding and is not counted as unsupported.

## Method

1. I hashed every file under `data/raw/sources/` with sha256 and matched each entry's `sha256` to a file. Hash `0200d601…` matches two byte-identical copies of the FY2025 10-K (`outlook/` and `product/`), so either copy is the source.
2. I turned each source into text with the same steps as `src/gdn/claims.py` `page_text`: drop script and style blocks, strip tags, unescape HTML, collapse whitespace. I normalised each quote with `norm` and checked it is a contiguous substring. I counted words with `split()`.
3. For each entry I read about 2,500 characters of source on each side of the quote and checked every fact, number, date and attribution in `text` against it. I also checked the speaker, the segment and the period for each call-transcript claim.
4. Attribution checks: each `url_or_accn` matches its file. The accession number is the file's prefix, and `dei:DocumentType` and the period agree (10-K FY2025, 10-K FY2024, 10-Q Q1 2025, 10-Q Q3 2025, 10-Q Q2 2026, and 8-K Ex. 99.1 dated July 29, 2026). The fool.com transcript's `<link rel="canonical">` equals the claimed URL, and the page reads "DATE Wednesday, July 29, 2026 at 9:00 a.m. ET". The Wayback page embeds the original `gulfstreamnews.com/news/gulfstream-g280-certified-by-…` URL and is dated September 04, 2012.
5. Cross-checks: the Aerospace segment's operating margin was 15.0% in Q1 2026 (10-Q 0000040533-26-000012) and 14.5% in Q2 2026 (10-Q 0000040533-26-000032). That confirms "down sequentially" in `os-aero-margin-q2`. I also checked the G650, G800 and G300 statements in the Q3 2025 10-Q and the FY2025 10-K against the product claims. They agree.

## Per-entry results

Line = the `"id"` line in `report/claims.json`. Source paths are under `data/raw/sources/`.

| id | line | source file | quote words | quote verbatim | text supported |
|---|---|---|---|---|---|
| bo-aerospace | 3 | outlook/0000040533-26-000006-gd-20251231.htm | 39 | yes | yes |
| bo-combat | 12 | outlook/0000040533-26-000006-gd-20251231.htm | 26 | yes | yes |
| bo-marine | 21 | outlook/0000040533-26-000006-gd-20251231.htm | 29 | yes | yes |
| bo-technologies | 30 | outlook/0000040533-26-000006-gd-20251231.htm | 39 | yes | yes |
| os-aero-margin-learning | 39 | calls/2026-07-29-fool.html | 36 | yes | yes (Danny Deep, Aerospace Q&A) |
| os-aero-margin-q2 | 48 | calls/2026-07-29-fool.html | 37 | yes | yes (Aerospace section; 15.0% to 14.5% confirms it) |
| os-btb | 57 | outlook/0000040533-26-000029-gd-20260705exhibit991.htm | 28 | yes | yes (Q2 2026 release) |
| os-del | 66 | calls/2026-07-29-fool.html | 18 | yes | yes |
| os-margin | 75 | calls/2026-07-29-fool.html | 34 | yes | yes ("Aerospace" comes from the sentence just before the quote) |
| os-marine-drivers | 84 | calls/2026-07-29-fool.html | 39 | yes | yes (Marine Q&A) |
| os-marine-outlook | 93 | outlook/0000040533-26-000032-gd-20260705.htm | 19 | yes | yes |
| os-rev | 102 | calls/2026-07-29-fool.html | 11 | yes | yes |
| os-upside | 111 | calls/2026-07-29-fool.html | 25 | yes | yes ("the 280" means the G280 in context) |
| pc-g280-iai | 120 | product/gulfstreamnews-2012-09-04-g280-certified-wayback.html | 28 | yes | yes |
| pc-g280-israel-supplier | 129 | outlook/0000040533-26-000032-gd-20260705.htm | 20 | yes | yes |
| pc-g280-mid-cabin | 138 | product/0000040533-25-000008-gd-20241231.htm | 22 | yes | yes (FY2025 10-K now says "The midsize aircraft are assembled by a non-U.S. partner"; still consistent) |
| pc-g300-announced | 147 | product/0000040533-25-000045-gd-20250928.htm | 16 | yes | **no**: see F2 |
| pc-g300-entry-timing | 156 | calls/2026-07-29-fool.html | 35 | yes | **no**: see F1 |
| pc-g400-timing-update | 165 | calls/2026-07-29-fool.html | 31 | yes | yes |
| pc-g500-g600-entry-into-service | 174 | outlook/0000040533-26-000006-gd-20251231.htm | 11 | yes | yes |
| pc-g650-end-of-production | 183 | product/0000040533-25-000014-gd-20250330.htm | 19 | yes | yes |
| pc-g700-first-deliveries | 192 | product/0000040533-25-000008-gd-20241231.htm | 29 | yes | yes |
| pc-g800-certification | 201 | product/0000040533-25-000014-gd-20250330.htm | 31 | yes | yes |
| pc-g800-first-deliveries | 210 | outlook/0000040533-26-000006-gd-20251231.htm | 16 | yes | yes |
| risk-aerospace-customer-defaults | 219 | outlook/0000040533-26-000006-gd-20251231.htm | 24 | yes | yes (Aerospace risk factor) |
| risk-bizjet-demand-economy | 228 | outlook/0000040533-26-000006-gd-20251231.htm | 30 | yes | yes (Aerospace risk factor) |
| risk-fixed-price-contracts | 237 | outlook/0000040533-26-000006-gd-20251231.htm | 26 | yes | yes |
| risk-international-fx | 246 | outlook/0000040533-26-000006-gd-20251231.htm | 37 | yes | yes |
| risk-new-product-regulatory-delays | 255 | outlook/0000040533-26-000006-gd-20251231.htm | 24 | yes | yes |
| risk-supply-chain-disruption | 264 | outlook/0000040533-26-000006-gd-20251231.htm | 31 | yes | yes |
| risk-tariffs | 273 | outlook/0000040533-26-000006-gd-20251231.htm | 36 | yes | yes, but newer filing replaces it: see F3 |
| risk-us-government-spending | 282 | outlook/0000040533-26-000006-gd-20251231.htm | 35 | yes | yes |

## Findings

`build()` in `src/gdn/claims.py` rebuilds `report/claims.json` from the topic files in `docs/build/`, so each fix belongs in the topic file. `report/note.html` prints each `text` word for word, so a rebuild carries the fix into the note.

### F1. pc-g300-entry-timing makes the G300 timing firmer than the source and gives a relative date

- File and line: `docs/build/claims_product.json:130` (text). Built copy at `report/claims.json:157`, printed in `report/note.html:62`.
- Severity: minor.
- Text: "GD said the final G280 ought to deliver in the second quarter of next year and the G300 should start in late '27 or early '28, leaving a planned production break."
- Evidence (`calls/2026-07-29-fool.html`, page text):
  - Just before the quote, Phebe Novakovic says: "as you know, I'm no longer in the business of estimating EIS given that the regulators set the pace."
  - The quote reads: "the onset of the 300, which late '27, early '28, somewhere in that."
  - The page's date line reads: "DATE Wednesday, July 29, 2026 at 9:00 a.m. ET".
- Why it is not supported as written:
  - "should start in late '27 or early '28" turns a rough window ("somewhere in that") into a firm expectation with fixed bounds, and drops the speaker's own warning that she does not estimate entry into service.
  - "start" does not say what starts. The source sets the "onset of the 300" against the last G280 delivery.
  - "next year" only makes sense if the reader knows the call date. From a call on July 29, 2026, "next year" means 2027.
- Fix: "GD said the final G280 ought to deliver in the second quarter of 2027 and put the onset of the G300 somewhere around late 2027 or early 2028, leaving a planned production break; its CEO said she no longer estimates entry into service because regulators set the pace." The quote can stay as it is.

### F2. pc-g300-announced credits the announcement to Gulfstream, but the source credits "we", meaning GD

- File and line: `docs/build/claims_product.json:121` (text). Built copy at `report/claims.json:148`, printed in `report/note.html:62`.
- Severity: minor.
- Text: "Gulfstream announced the all-new super-midsize G300 in September 2025 to replace the G280."
- Evidence (`product/0000040533-25-000045-gd-20250928.htm`, the General Dynamics 10-Q for Q3 2025): "In September 2025, we announced our all-new super-midsize G300 aircraft, which will replace the G280 aircraft." The filer, and so the "we", is General Dynamics. The source never says Gulfstream made the announcement.
- Why it is not supported as written: the brief requires every attribution in the text to appear in the source. The model, the month and the replacement of the G280 are all supported. The announcer is not.
- Fix: "GD announced its all-new super-midsize G300 in September 2025 to replace the G280."

### F3. risk-tariffs is supported by its FY2025 10-K, but a newer cached GD filing has replaced it

- File and line: `docs/build/claims_risks.json:58` (text). Built copy at `report/claims.json:274`, printed in `report/note.html:86`.
- Severity: minor. This is a staleness finding, not a support failure. The cited source says exactly what the text says, so this entry is not on the unsupported list.
- Text: "GD says tariffs have not had a material impact on its results to date but reduced Aerospace operating margins by 30 basis points in 2025, and their duration and extent continue to evolve."
- Evidence: the cited FY2025 10-K (`outlook/0000040533-26-000006-gd-20251231.htm`) supports it: "The duration and extent of the tariffs continue to evolve." The Q2 2026 10-Q (`outlook/0000040533-26-000032-gd-20260705.htm`) is already cached and cited by `os-marine-outlook` and `pc-g280-israel-supplier`. It says: "In February 2026, the U.S. Supreme Court held that tariffs imposed under the International Emergency Economic Powers Act (IEEPA) were unauthorized, and a phased process was developed to refund the previously paid tariffs. To date, we have received refunds of some of these tariffs." It also says: "Overall, tariffs as applied in their current form and tariffs yet to be refunded are not material to our results of operations."
- Why it matters: the note goes out in October 2026 with the present tense "GD says … continue to evolve". GD's latest filing no longer says that, and it reports receiving refunds of some of those tariffs.
- Fix, either one:
  - (a) Date the claim to its filing: "In its 2025 annual report, GD said tariffs had not had a material impact on its results but reduced Aerospace operating margins by 30 basis points in 2025."
  - (b) Cite the Q2 2026 10-Q instead (accession 0000040533-26-000032, sha256 `09f79c28…`), quoting its sentence on refunds and materiality.

## Entries the sources do not support

1. `pc-g300-entry-timing` (F1, minor): "the G300 should start in late '27 or early '28" overstates the source's "the onset of the 300, which late '27, early '28, somewhere in that." It also drops the CEO's caveat that she no longer estimates entry into service, and it leaves "next year" (meaning 2027) without an anchor.
2. `pc-g300-announced` (F2, minor): the text says "Gulfstream announced". The source says "In September 2025, we announced our all-new super-midsize G300 aircraft", where "we" is General Dynamics, the 10-Q filer.

All 32 quotes are verbatim in their cached sources and none is over 40 words.
