# Round 4: compliance

Verdict: NO-GO. The tracked build notes publish the owner's home-folder paths and macOS account name, and the disclosures differ from one surface to the next.

Counts: S1 1, S2 6, S3 6

Tree read: the cold copy at `~/gdn-prepub/round4/`, plus `gh repo view` (description, topics, homepage) and `gh release view lock-2026Q3`. Scratch scripts are in `~/gdn-prepub/agents/round4_compliance/`.

## Answers

**1. Advice, rating, price target, initiation.** Nothing gives a recommendation, a rating or a target. A grep for buy, sell, upside, downside, overweight, outperform, recommend, bullish, bearish, stock and shares found no hits on the post, README, dashboard, note, resume or interview notes. Every hit for "price target" or "rating" is a negation: the note's footer on all 8 pages says "No rating or price target", and INTERVIEW_NOTES.md:27 explains why there is none. Several things still look like sell-side research, though none of them gives advice:
- The note's title follows the coverage format "General Dynamics (GD): Gulfstream delivery tracker" (note.py:20), with sections called "Business overview", "Risks" and "Model page".
- Exhibit 8 gives "2026Q3 revenue by segment: the estimates made before the release". Its footnote gives "Segment operating earnings at trailing margins: $1.4B".
- The workbook's Segments sheet has rows for "Aerospace operating earnings from nowcast" and "Operating earnings total".
- The dashboard section is headed "What it means for GD" (index.html:88).
- The post uses #EquityResearch.
Every estimate the pages show is for 2026Q3, which GD has already reported. `site/data.json` has `estimates.target = 2026Q3`, and the dashboard renders the newest quarter with a lock or a score, which is 2026Q3. The served `site/data.json` still holds an open-quarter figure, though: `live[1]` for 2026Q4 has a `nowcast` total of 14.307 with a band of 3.59 to 21.11 from the 2026-11-12 snapshot, and a `guidance_pace` of 41.0. It also has a 14-row `path['2026Q4']`. The page does not show any of it. See COMPLIANCE-10 and COMPLIANCE-13.

**2. Disclaimers.** I checked each surface for three things: a student project, not investment advice, and no affiliation with GD, Gulfstream or the FAA. The table below comes from `matrix.py`.

| Surface | Student | Not advice | Not affiliated: GD | Gulfstream | FAA | Position |
|---|---|---|---|---|---|---|
| Post | Y | Y | Y | Y | **missing** | **missing** |
| README | Y | Y | Y | Y | Y | Y (undated) |
| Dashboard (index.html) | Y | Y | Y | Y | Y (footer only) | **missing** |
| Note, PDF pages 1 to 8 | Y | Y | Y | Y | **missing on all 8** | Y (undated) |
| Workbook About sheet | Y | Y | Y | Y | Y | **missing** |
| Workbook, the other five sheets | missing | missing | missing | missing | missing | missing |
| preview.png and the charts | no disclaimer; source line only | | | | | |

These surfaces lack an element:
- The post lacks the FAA.
- Every PDF page lacks the FAA, in both the footer and the page 1 box.
- The dashboard's eyebrow (index.html:27) lacks the FAA and "not investment advice", but its footer (index.html:112) carries all three.
- In the workbook, only About!A3 carries the disclaimers. The file opens on About (`wb.active` is About).

See COMPLIANCE-3.

**3. Position statement.** It appears at README:15 ("I hold no position in General Dynamics") and in the note's page 1 box and every page footer ("The author holds no position in General Dynamics."). Neither is dated. The note carries no publication or revision date at all: a grep of its text for "2026-11", "published" or "as of 20" finds only data dates. The post, the dashboard and the workbook carry no position statement. The two wordings say the same thing. The note's sentence is not in the code: note.py:69-78 reads it from a private file in the home folder, or carries it over from the earlier note. See COMPLIANCE-2.

**4. Trademarks.** "Gulfstream", "General Dynamics" and the model names (G280, G300, G400, G500, G600, G650, G700, G800, G150) appear only as plain words naming the company and its products. I found no logo or brand styling:
- The favicon is a generic line-chart glyph.
- The charts are plain matplotlib.
- I viewed all 8 PDF pages. They carry no brand imagery.
- The palette is generic: the most common colours in `site/style.css` are `#8fb0dc`, `#1d3f6e` and `#1c1a17`, and the only typeface is IBM Plex Sans.
Every surface says it is not affiliated, so I found nothing that implies endorsement. Still, no surface says "not endorsed", and none attributes the trademarks: a grep for trademark, endorse, ® and ™ found 0 hits. The repository and Pages paths contain "gulfstream" as a descriptive word. See COMPLIANCE-8.

**5. Self-descriptions.**
- "I locked". `gh release view lock-2026Q3` shows the release was published 2026-10-29T05:51:24Z by `github-actions[bot]`, and its notes carry the sha256 `3c4cdbd0...6f23`. `shasum -a 256 predictions/2026Q3.json` prints the same hash. README:121 and INTERVIEW_NOTES.md:30 both say the workflow made the lock, which matches the release author. The release shows `immutable: false`, and README:121 says the absence of later edits cannot be checked.
- "Preregistered" and "held out". README:119 says the commit order is all that backs both words, and that the rules went in two minutes before scoring with the data already in the repository. The post says "rules set minutes before scoring". The two say the same thing.
- "Built with the coding agent". README:180 says so, and INTERVIEW_NOTES.md:36 says the same. The resume bullets do not. See COMPLIANCE-7.
- "I checked 30 airframes" (README:161). This is covered by the README:180 convention that "I" means work done in the the coding agent sessions.

**6. The post as a LinkedIn post.**
- **Length.** `post.py` prints 1,280 characters after stripping, with 1,280 UTF-16 units. It has no em or en dashes and no characters outside ASCII.
- **First 140 characters:** `My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40.\nMy tracker scales FAA regist`
- **First 210 characters:** `My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40.\nMy tracker scales FAA registrations into an estimate of the Gulfstream jets General Dynamics (GD) `
- **Opening.** The post opens with the miss, which is the right register for compliance.
- **Hashtags.** #EquityResearch and #Aerospace. There is no ticker hashtag and no cashtag.
- **Links.** The post has two links. "Dashboard:" points to the Pages URL, which matches `og:url` (index.html:11) and the repository's `homepageUrl`. "Code:" points to the repository. Both are 404 while the repository is private, which the brief says is expected. COMPLIANCE-6 covers whether Pages will deploy and stay current.
- **Preview of the dashboard link.** The page has 6 `og:` tags and 0 `twitter:` tags. The title is "How closely do FAA registrations track Gulfstream deliveries?". The description begins "A student project:". The image is `preview.png`, 1600x900, with the same sha256 as `output/charts/track_record.png`. It shows the backtest through 2026Q2 and not the locked quarter the post leads with.
- **Preview of the repository link.** GitHub's description is "Gulfstream deliveries estimated from FAA registrations, tested on 26 held-out GD quarters, each live estimate locked". It does not say it is a student project, and it does not need to. See COMPLIANCE-11.

**7. Data and copyright.**
- **Registrant names and addresses.** Their republication is disclosed: README:144 says the stored rows carry "the registrant names and addresses the FAA publishes". It fits the licence. The README calls the FAA registry data a U.S. government work, and nothing restricts republishing it. But the stored subsets keep whole rows, street addresses included, while the code reads only NAME (faa.py:25-29). Each of the 8 MASTER subsets holds 18 or 19 rows for individual registrants. See COMPLIANCE-5.
- **Transcript and article text.** None of the files I scanned holds transcript or article text beyond short quotes:
  - `data/guidance.csv` has 28 rows, each with a link (25 to fool.com, 3 to marketbeat.com). The longest quote is 47 words.
  - `data/quarter_plans.csv`: longest quote 25 words.
  - `report/claims.json`: 27 claims, longest `quote` field 39 words.
  - `docs/build/` audit and claims files: longest quoted span 48 words, in FACT_CHECK.md.
  - `report/note.html`: longest quoted span 41 words.
  - The cached sources are not in the tree.
- **LICENSE.** `LICENSE` is a plain MIT licence over "this software and associated documentation files". README:184 says only the code is MIT, and that the FAA data and GD's material belong to others. The LICENSE text does not carry that limit, and it does not name the vendored components. See COMPLIANCE-9.

**8. The owner's material.**
- **Figures.** I recomputed each figure in the resume bullets and interview notes against the tree, and none fails. The checks:
  - 1,251 events, 246 aged three years or more, and 76 with no year, from `data/processed/serials.csv`.
  - 5 of 42 in the 2026Q3 window of the 2026-10-29 snapshot.
  - 163 / 215 = 0.758 and 40 / 42 = 0.952.
  - A 2026Q2 coverage ratio of 0.719 in `results/metrics.json`.
  - From `results/exploratory/sensitivity.md`: 12.51 against 3.48, 4.43 against 6.43, and 6.02 with 12 of 26.
  - 42 events in every daily snapshot from 2026-10-29 to 2026-11-12.
  - `data/processed/*.csv` has no row without an accession number, and `data/guidance.csv` and `data/quarter_plans.csv` have no row without a URL.
  - The workbook has live formulas: 448 in Quarters, 9 in Summary, 11 in Live, 27 in Segments and 18 in Sensitivity, with `fullCalcOnLoad` set.
- **Claims that go beyond the repository.**
  - The resume bullets say "Built" and "Wrote" and do not name the coding agent (COMPLIANCE-7).
  - INTERVIEW_NOTES.md:33 says every registry figure traces "to a stored FAA snapshot". The as-of study's figures come from Wayback captures that are not stored.
  - INTERVIEW_NOTES.md:30 says the count "has not changed" since the lock, without a date.
  See COMPLIANCE-12.

**9. What must change before posting.**
- Replace the home-folder paths in `docs/build/` with `~` (COMPLIANCE-1).
- Make one disclosure set match on the post, the note, the dashboard, the workbook and the README. It should name the FAA and include a dated position statement, and the note should carry a publication date (COMPLIANCE-2, COMPLIANCE-3).
- In the post, say the band is nominally 80% and held 18 of 26 backtest quarters (COMPLIANCE-4).
- Name the coding agent in the resume bullets (COMPLIANCE-7).
- Give Pages a deploy path that runs after the workflow's commits, and confirm the dashboard URL returns 200 before posting (COMPLIANCE-6).
- Decide on the stored registrant addresses and record the decision (COMPLIANCE-5).

## Findings

### COMPLIANCE-1 (S1): the build notes carry the owner's home-folder paths and macOS account name
- **Surface:** `docs/build/`, which README:180 links to.
- **Locations:** 25 lines in 17 files:
  - `docs/build/DECISIONS.md:32`
  - `docs/build/briefs/_claims_common.md:3`
  - `airframe_audit_1.md:3`, `airframe_audit_2.md:3`, `airframe_audit_3.md:3`
  - `critique_a.md:5`, `critique_b.md:5,6,7`
  - `guidance_check_1.md:3`, `guidance_check_2.md:3`, `guidance_check_3.md:3`
  - `review1_analyst.md:3,5`, `review1_factcheck.md:3`, `review1_numbers.md:3,5`, `review1_ops.md:3,5`, `review1_spec.md:3,5`
  - `review2_code.md:3,11`, `review2_docs.md:3,13`
- **Evidence:** a recursive grep of the tree, outside `.venv`, for the macOS home-folder root and for the account name, keeping only file and line, prints the list above. The values are described here, not quoted:
  - absolute home-folder paths to the project checkout
  - absolute home-folder paths to a coding tool's plugin cache
  - a line of `ls -l` output whose owner column is the account name, next to a path into a folder outside the repository
- **Why S1:** the common brief lists the macOS account name and any absolute home-folder path as things that must not be published. The build notes are not part of the post, which limits the harm, but they are tracked and the README links to them.
- **Fix:** replace each one with `~` or `<repo>` in the hand-written briefs and in DECISIONS.md. None of these files is generated under `src/gdn/`. The cold tree has no history, so I could not check whether earlier commits hold the same text. If they do, whether to rewrite history is the owner's call; record the decision in the go-public notes.

### COMPLIANCE-2 (S2): the position statement is undated and missing from three surfaces, and the note is undated
- **Surfaces:**
  - `docs/LINKEDIN_POST.md:11`, generated by `src/gdn/report.py:53`
  - `site/index.html:112`, hand-written
  - `output/gd_gulfstream_model.xlsx` About sheet, generated by `src/gdn/workbook.py:59`
  - `README.md:15`, hand-written
  - every page of the note, generated by `src/gdn/note.py:69-78` and `:272`
- **Evidence:** the `matrix.py` output gives the position column as "-" for the post, index.html, app.js, data.json and all six workbook sheets. It gives "Y" for the README and PDF pages 1 to 8, and "-" for a dated position on every surface. A grep of the note's text for "2026-11", "published" and "as of 20" finds only data dates (lines 205 and 213 of the extracted text).
- **Fix:** write one sentence, for example "As of 2026-11-12 I hold no position in General Dynamics securities." Put it in the post, the dashboard footer, the workbook's About sheet, README:15 and the note. Add a "Published" and "Revised" date line under the note's title. Refresh the date at each lock.

### COMPLIANCE-3 (S2): "not affiliated with the FAA" is missing from the post and from all 8 PDF pages
- **Surfaces:**
  - `docs/LINKEDIN_POST.md:11`, from `src/gdn/report.py:53`: "I am not affiliated with General Dynamics or Gulfstream."
  - the note's footer and page 1 box, from `src/gdn/note.py:21-22`: "Not affiliated with General Dynamics or Gulfstream."
  - Also, on the dashboard the eyebrow (`site/index.html:27`, hand-written) omits it, though the footer has it, and five of the six workbook sheets carry no disclaimer.
- **Evidence:** `matrix.py` gives aff_FAA as "-" for the post and PDF pages 1 to 8, and "Y" for the README, index.html and the workbook's About sheet. The README, dashboard footer and workbook each name the FAA, so the surfaces disagree.
- **Fix:** add "or the FAA" to the two constants. Then rebuild the note and the post. The note change needs `make claims` and `make pdf` in the main session.

### COMPLIANCE-4 (S2): the post calls the band "my 80% band" without saying it held 18 of 26 backtest quarters
- **Surface:** `docs/LINKEDIN_POST.md:4`, "outside my 80% band of past misses". The post is generated by `src/gdn/report.py`, which writes the file at line 608.
- **Evidence:** README:6 says the band's "nominal level is 80% and which held 18 of 26 held-out quarters". README:51 gives "69.2%, against a nominal 80%". The common brief lists the band's undercoverage as a disclosure a professional expects. Without it, a miss outside the band reads as rarer than the backtest suggests.
- **Fix:** write "outside my band of past misses (nominally 80%; it held 18 of 26 backtest quarters)". The post is 1,280 characters, so there is room.

### COMPLIANCE-5 (S2): stored FAA subsets keep individual registrants' street addresses that the code never reads
- **Surface:** `data/snapshots/<date>/MASTER.txt.gz` and `DEREG.txt.gz`, 8 dated folders. They are written by `src/gdn/faa.py:203-209` (`subset` keeps whole lines).
- **Evidence:**
  - `faa.py:25-29` lists the fields the method reads: NNUMBER, SERIALNUMBER, MFRMDLCODE, NAME, the date fields, YEARMFR, CANCELDATE and EXPCOUNTRY. No address field is among them.
  - `regtype.py`, run over all 8 MASTER subsets, prints 18 or 19 rows with registrant type 1 (individual) in each, of which 17 or 18 carry a street address. For example:
    - 2026-10-19: 2821 rows; 19 individuals; 18 with a street address.
    - 2026-10-29: 2822 rows; 18 individuals; 17 with a street address.
  - The DEREG header also carries mailing and physical address columns.
  - The Federal Register notice of 2025-04-03 (2025-05738) cites 49 U.S.C. 44114 (section 803 of the FAA Reauthorization Act of 2024). It says the FAA "shall withhold from broad dissemination or display by the FAA" owners' personal information, on request. The notice does not say whether that covers the downloadable file.
  - README:144 discloses that the rows carry names and addresses.
- **Why S2 and not S1:** the FAA publishes these rows, and the README discloses them. Read literally, though, this meets the S1 wording, so the main session may re-rate it.
- **Fix:** have future snapshots keep only the fields in `FIELDS`, or blank the address columns. The stored snapshots, 2026-10-29 included, are part of the lock's record and are hashed in `MANIFEST.json`, so leave them. Add to README:144 that the method never reads the addresses, and give a contact for registrants. Do not promise removal, because the stored snapshots are part of the record.

### COMPLIANCE-6 (S2): after going public, the dashboard will not redeploy when the workflow commits a lock or a score
- **Surface:** the post's dashboard link and `.github/workflows/pages.yml`, hand-written.
- **Evidence:**
  - `pages.yml:2-5` runs only on a push to main that touches `site/**`, or on a manual dispatch. `:16` skips the job while the repository is private.
  - `nowcast.yml` commits with the job's own token (`GH_TOKEN: ${{ github.token }}`, with the credentials `actions/checkout` keeps).
  - `daily.py:23-25` rewrites `site/data.json`, `site/preview.png`, `site/GD_research_note.pdf`, `README.md` and `docs/LINKEDIN_POST.md`.
  - GitHub's documentation (docs.github.com, "GITHUB_TOKEN") says "events triggered by the `GITHUB_TOKEN` will not create a new workflow run", with `workflow_dispatch` among the exceptions.
- **Consequence:** making the repository public fires no push, so the first deploy needs a manual dispatch. Later, a workflow-made 2026Q4 lock or score would show in the README on GitHub, but the dashboard would keep the older `data.json`. Meanwhile the dashboard says the estimate "stays on this page whether it hits or misses" (app.js:169).
- **Fix:** before posting, dispatch `pages.yml` by hand and confirm the dashboard URL returns 200. Then give the nowcast job a deploy step, or have it dispatch `pages.yml` after any commit that touches `site/`. The job needs permission to dispatch workflows.

### COMPLIANCE-7 (S2): the resume bullets claim the build without naming the coding agent, while the README does
- **Surface:** `docs/RESUME_BULLETS.md:1-3`, hand-written: "Built a Python pipeline", "Built a daily job", "Wrote a cited research note and an Excel model".
- **Evidence:** README:180 says "I built this project with the coding agent, an AI coding agent, in sessions I ran and directed." The note's prose is produced by `src/gdn/note.py`. A recruiter who reads both files sees two accounts of the same work.
- **Fix:** add one clause, for example "Built, with the coding agent (an AI coding agent I directed), a Python pipeline that ...". Keep the figures as they are; they match the tree.

### COMPLIANCE-8 (S3): no trademark attribution or "not endorsed" line
- **Surfaces:** README `## License and data`, the note's footer and the dashboard footer.
- **Evidence:** a grep for trademark, endorse, ® and ™ across the README, post, index.html, app.js, LICENSE, the note's text and the workbook's About sheet prints 0.
- **Fix:** add one line: "Gulfstream, General Dynamics and the aircraft model names are trademarks of their owners, used only to identify them; this project is not endorsed by them."

### COMPLIANCE-9 (S3): LICENSE does not limit itself to code as README:184 says
- **Surface:** `LICENSE`, hand-written.
- **Evidence:** LICENSE grants MIT over "this software and associated documentation files". README:184 says "The code is under the MIT license" and that GD's material and call quotes "belong to their owners". The tree ships Chart.js v4.4.1 (MIT banner), axe 4.10.3 (MPL-2.0 banner) and IBM Plex (`site/fonts/OFL.txt`) under their own licences.
- **Fix:** add a short scope paragraph to LICENSE or a NOTICE file. MIT would cover the project's own code and text. FAA rows would be public-domain U.S. government data. GD's figures and quotes would remain their owners'. The vendored files would keep their own licences.

### COMPLIANCE-10 (S3): the note and one dashboard heading take the form of initiation research
- **Surfaces:**
  - the note's title, from `src/gdn/note.py:20`: "General Dynamics (GD): Gulfstream delivery tracker"
  - the note's section names "Business overview", "Risks" and "Model page"
  - `site/index.html:88`, "What it means for GD"
- **Evidence:** quoted in Answer 1. Every PDF page says "No rating or price target", and the only revenue and earnings estimates are for a quarter GD has already reported. So this reads as resemblance, not advice.
- **Fix:** rename the dashboard heading to "From deliveries to revenue". Optionally, add "A student research note, not coverage" under the note's title.

### COMPLIANCE-11 (S3): link-preview tags are incomplete, and the preview image omits the locked quarter
- **Surface:** `site/index.html:8-13`, hand-written, and `site/preview.png`, generated by `src/gdn/charts.py`.
- **Evidence:** `grep -c 'twitter:' site/index.html` prints 0, and the `og:` count is 6. `preview.png` is 1600x900, and its sha256 equals `output/charts/track_record.png`. The chart ends at 2026Q2.
- **Fix:** add `twitter:card` (`summary_large_image`) and `og:site_name`. Consider a preview image that marks the 2026Q3 lock against GD's 40, because that is the post's first line.

### COMPLIANCE-12 (S3): two interview-note sentences go beyond what the tree holds, or are undated
- **Surface:** `docs/INTERVIEW_NOTES.md:33` and `:30`, hand-written.
- **Evidence for line 33:** it says every registry figure traces "to a stored FAA snapshot". The as-of study's figures, which README:127-136 and the note's page 3 cite, come from Wayback captures dated 2017-04-27, 2025-10-21, 2026-05-01 and 2026-08-03 (`results/exploratory/asof.md`). `data/snapshots/` holds only the eight folders from 2026-10-19 to 2026-10-29, plus `daily/`.
- **Evidence for line 30:** it says the 42 "has not changed in the daily snapshots since the lock". That is true through 2026-11-12 by my count, but the sentence carries no date.
- **Fix:** for line 33, write "every backtest and live registry figure to a stored FAA snapshot, and the as-of study's to dated Wayback captures". For line 30, write "through 2026-11-12".

### COMPLIANCE-13 (S3): the served dashboard data labels a part-quarter count for the open quarter as a "nowcast"
- **Surface:** `site/data.json`, generated by `src/gdn/site_data.py` (line 60 builds the `live` entries from `results/live/<quarter>_latest.json`).
- **Evidence:** the dashboard serves this file publicly. Its `live[1]` holds `quarter: 2026Q4`, `nowcast.total` 14.307092198581561 and `band` [3.587264612374664, 21.108630660120024], from the 2026-11-12 snapshot, with `window_end` 2026-12-31 and `guidance_pace` 41.0. `results/live/2026Q4_latest.json` holds the same `nowcast` and `band`. README:107 says that file "holds that part count and is not an estimate of the quarter". But the key is named `nowcast`, it carries a band, and `site/data.json` has no caveat. The page renders 2026Q3, not this entry.
- **Fix:** in `site_data.py`, leave out `nowcast` and `band` for a quarter whose window is still open and has no lock. Or rename them and add a flag such as `"partial_count": true`. That way anyone reading the served file cannot mistake 14.3 for an estimate of GD's 2026Q4 deliveries.

## Improvements that would raise the project's standing

1. Keep one disclosure constant, and have the post, note, workbook, dashboard and README read it. It would carry: student project; not investment advice; no rating or price target; not affiliated with or endorsed by GD, Gulfstream or the FAA; and a dated position sentence. Each surface would then stay in step at every lock.
2. Add a dated revision line to the note, such as "Published 2026-11-12; estimates made before 2026-10-30, wording revised after". It shows that the "before the release" exhibits were not edited.
3. Have the workflow redeploy Pages after each lock and score (COMPLIANCE-6), so the public dashboard and the README never disagree.
4. Put a one-line "Data handling" note in README `## Data`: which FAA columns the method reads, that it never reads addresses, and a contact for registrants.
5. Point to `docs/INTERVIEW_NOTES.md`'s "How did you build it?" answer from the resume bullets, so the the coding agent disclosure travels with the claims.

## Checked and clean

- The post is 1,280 characters, with no ticker hashtag or cashtag, no dashes and no characters outside ASCII. Its two links match `og:url` and the repository's `homepageUrl`.
- No advice language appears on any public surface. Every "price target" or "rating" is a negation.
- Lock: the release was published 2026-10-29T05:51:24Z by `github-actions[bot]`, and its notes carry a sha256 equal to `predictions/2026Q3.json`. README:106 gives the same hash, the same time in ET and the same release URL.
- The 2026Q3 window holds 42 events in every daily snapshot from 2026-10-29 to 2026-11-12.
- I scanned the string literals in `site/app.js` lines 176 to 399 (tiles, tests, the path chart and the chart of jets on Gulfstream's own registration). They hold no advice language and no claim beyond the README's.
- The dashboard's headline branch: no Holm test rejects (`holm_reject` is false for all three), so the lead renders the "not statistically distinguishable" sentence. The live card keeps "made while the repository was private".
- All 20 relative links in the README resolve in the tree.
- The workbook opens on About, which has all three disclaimers. Its formulas are live.
- No logos or brand styling. I viewed the favicon, `preview.png`, `nowcast_path.png`, `coverage.png`, `dashboard.png` and all 8 note pages.
- The vendored code keeps its licence banners, and the font ships its `OFL.txt`.
- The emails in tests and tools use `example.com` or `example.invalid`. A scan for token patterns finds nothing. The workbook and PDF internals hold no absolute home-folder path and no `file://` URI.
- The test fixtures for FAA files and releases are synthetic.
- Transcript quotes are short and each carries a link. The longest is 47 words in `data/guidance.csv`. No cached source page is in the tree.
- Note source 6 (the Fool transcript URL) loads the Q2 2026 GD call and contains the quoted G280 phrase.
- `output/GD_research_note.pdf` and `site/GD_research_note.pdf` are byte-identical.

## Suspicions, not proven

- **Browser headers.** The FAA download sends a Chrome user agent and a Referer (`faa.py:19-20`, `:55`), and on the Mac it falls back to driving Chrome (`faa.py:59-63`). README:176 says the FAA "refuses some automated clients, so the job sends ordinary browser headers". A data-compliance reader may see that as getting around a block. Reading the FAA's site policy on automated access would settle it. The download page returned 403 to my fetch, so I could not open it.
- **Image crop.** LinkedIn may crop the 1600x900 `og:image` and clip the chart's source line. LinkedIn's Post Inspector would settle it once Pages is live.
- **Git history.** History may hold more home paths or personal data than the tip. The cold tree has no history. Settle it with a `git log -p` grep in an informed tree.
- **Statute coverage.** Whether 49 U.S.C. 44114 withholding reaches the releasable download, and so whether frozen copies could later hold rows an owner has asked to withhold. The Federal Register notice is silent on it.
- **Stale screenshot.** `output/charts/dashboard.png` shows older live-note wording ("likely too narrow") than `app.js` has now ("may not fit"). Nothing public links it, so it is not a finding unless it is used.

## Could not check, and refused commands

- I did not fetch the Pages site, the repository page, the owner's personal domain or the defense backlog dashboard. Each URL carries the owner's handle or name, and the brief bars putting those into outside requests. The first two are 404 until the repository is public anyway.
- The repository's social preview image. My brief's `gh repo view` fields do not include it.
- The FAA download page and its terms: my fetch returned HTTP 403. I did not retry with other headers.
- The README's "every daily commit since 2026-10-31 has come from the workflow". The cold tree has no history.
- I did not read `docs/prepub/ERRATA.md`. My instructions limit reads under `docs/prepub/` to my two briefs.
- I did not render the dashboard in a browser. I derived its text from `app.js` and `data.json`, and checked it against the `dashboard.png` screenshot.
- No command was refused. Besides the tools the brief lists, I ran these read-only utilities: `awk`, `sort`, `uniq`, `tr`, `du`, `which` and `node --version`. I did not run node on any file. I also ran an in-place `sed` edit on my own scratch script in `~/gdn-prepub/agents/round4_compliance/`. I wrote nothing in the tree.
