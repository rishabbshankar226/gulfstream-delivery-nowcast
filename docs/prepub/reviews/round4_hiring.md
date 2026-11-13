# Round 4: hiring

Verdict: NO-GO. Sixteen tracked build briefs carry an absolute home-folder path that names the owner's macOS account, which the go-public rules count as personal data; the rest of what I found is wording and layout the owner can fix in an afternoon.

Counts: S1 1, S2 3, S3 9

Tree read: the cold copy at `~/gdn-prepub/round4/` (no git history). Scratch: `~/gdn-prepub/agents/round4_hiring/`. I reconstructed the dashboard's first screen from `site/index.html`, `site/app.js` and `site/data.json`, and checked it against `output/charts/dashboard.png`, which is a 1280 by 900 screenshot of the page. `site/preview.png` is not a screenshot: it is the track-record chart used as the link-card image. I did not render the page.

## Answers

**1. What the project claims, and is it true?**
It claims that FAA registrations, scaled by a trailing ratio, track GD's reported Gulfstream deliveries about as well as simple baselines on 26 past quarters (5.5 against 6.9 for a guidance pace, not distinguishable, with the same quarter last year closer at 4.6), and that it locks a live estimate before each release, the first of which (32.0 for 2026Q3) missed GD's 40 by 8.0, outside its band. Each part checks out. I recomputed the averages from `site/data.json` (5.523, 6.917, 4.615). The lock file `predictions/2026Q3.json` hashes to the sha256 in the GitHub release notes, and the release was published by `github-actions[bot]` at 2026-10-29T05:51:24Z (01:51 ET). GD's Exhibit 99.1 (accession 0000040533-26-000036) prints 40 deliveries (35 large, 5 mid) against 39 a year earlier. Two qualifications: "held out" rests only on commit order, which README.md:119 says plainly, and "every Gulfstream jet" overstates the scope (HIRING-3).

**2. Would I invite the author to interview?**
After 90 seconds (post, README top), as the research director: yes, to a first-round screen. The author pulls primary data from SEC filings and a government registry and publishes an estimate before the print. The miss and the baseline that won are both on the first screen. Against that, the opening is hedged and full of terms like "guidance pace" and "past-miss band" that a recruiter has to decode.
As the PM: yes, out of curiosity. A registry-based delivery nowcast is a real buy-side technique, and a candidate who reports a miss outside the band plainly shows judgment I would pay for.
After 10 minutes: still yes, with two questions ready. The error analysis by year, the as-of study, the G280 filed under IAI, and the sign tests with Holm's correction show care beyond student norm. But the README repeats itself, and the note spends two pages on boilerplate. README.md:180 says Claude Code built the project, while the resume says "Built" and "Wrote", so the first interview question will be about authorship. The only GD view is a mechanical revenue figure, which missed by 23.4% (note Exhibit 8).

**3. What reads as amateur, defensive, padded, repetitive or machine-written**
- docs/LINKEDIN_POST.md:6: "(Registry count: my scaled estimate; the pace: mine.)" This reads machine-written and needs decoding.
- docs/LINKEDIN_POST.md:6: "Backtest (rules set minutes before scoring):" This is defensive and cryptic in a feed. It answers a question the reader has not asked yet.
- docs/LINKEDIN_POST.md:2: "...General Dynamics (GD) reports each quarter, locked on GitHub the day before GD reports." "Reports" appears twice in one sentence.
- docs/LINKEDIN_POST.md:4 and :6 name one baseline two ways: "A pace I derived from GD's own full-year outlook" and then "GD's guidance pace".
- README.md:23: "In that sentence the registry count is the scaled registry estimate, the table's first row, not the raw registry count in its second." This is a gloss the headline forces on itself (HIRING-5).
- README.md:8 and README.md:21 give the same backtest result twice, 13 lines apart, and the table at :29 to :33 gives it a third time.
- README.md:49: "One reading matters here." and "A second one:". This is roughly 300 words of variants inside Results.
- README.md:71 to :79: the "Average miss by cabin" table repeats the Large cabin and Mid cabin columns of the Results table at :27 to :33 exactly.
- README.md:119: "The commit order is all that backs the words "held out" and "preregistered" here". This is honest, but it undercuts the section's own heading. Keep the fact and drop the self-rebuttal tone.
- README.md:121: "The job now refuses three things the preregistered text does not mention". This is insider language that points to an erratum ID.
- README.md:136, note page 3, INTERVIEW_NOTES.md:42: "four quarters prove nothing" appears on three surfaces.
- Note page 1 box: "The key points above, the locked-quarter paragraph and Exhibit 8 now carry what GD reported, and I have revised other wording since." This is a revision log on the first page.
- Note page 6: nine consecutive "GD says ..." risk bullets restate 10-K boilerplate. This is padding.
- Note page 5, Exhibit 10 footnote: "so this table is not current." A stale table that announces it is stale.
- INTERVIEW_NOTES.md:39: "GitHub's runner downloaded the registry even though it was expected to be blocked". This is engineering trivia in a finance interview.
- Across surfaces, "Simply repeating the same quarter last year missed by less" recurs word for word in the post, README, dashboard and note. The repeated template is what reads machine-made, more than any single sentence.
No stock words (robust, leverage, insights and the rest) and no em or en dashes appear in the post, README, dashboard, note text, resume bullets or interview notes. I checked with grep.

**4. Do the live miss and the winning baseline come early and plainly? Does the framing undersell?**
The miss comes early and plainly in the post (first 110 characters) and in README.md:6. On the dashboard, the desktop first screen (output/charts/dashboard.png) shows "2026Q3 · Scored: missed by 8.0, outside the band". However, the biggest number is the 32.0 estimate, and GD's 40 is the seventh fact (HIRING-6). In the note, the miss is key point 2, after the backtest. The winning baseline (same quarter last year, 4.6) is in post paragraph 3, README.md:8, the dashboard framing line (app.js:100) and note key point 1, so it is plain enough.
The framing undersells. Post paragraph 3 stacks five hedges in about 90 words, and the first 140 characters show only "I missed" and "My tracker scales FAA regist". Nothing the author built is visible before "see more". Defensible stronger versions, all true on the tree:
- Post opening (136 characters, checked): "I estimate Gulfstream deliveries from FAA registrations and lock each one on GitHub before GD reports. First lock: 32.0. GD reported 40."
- "I set the test up so it could fail, and the first live quarter did: the lock missed by 8.0, outside its band." This rests on INTERVIEW_NOTES.md:33 and README.md:106.
- README: "I date each delivery airframe by airframe from the FAA's current and cancelled registrations, including the G280 the registry files under IAI." This rests on README.md:111.
None of these says the project counts jets before GD reports, or beats GD or the market.

**5. Could anything read as a trading signal, rating or advice?**
Nothing is a rating, target or recommendation. Every surface carries "not investment advice", and the note adds "No rating or price target." The nearest thing is the dashboard's "What it means for GD" (site/index.html:88). It sits over a segment revenue table with a "Change, %" column against the year-ago quarter. Before a score, the page says "so the delivery-based figure falls" (site/app.js:432 to :435), which reads like an earnings-preview call (HIRING-11). Note Exhibit 9, "Aerospace revenue for each delivery count", is labelled mechanical and is fine.

**6. Is each surface the right length? What to cut**
- Post (1,281 characters): the length is right. Cut the parenthetical and "rules set minutes before scoring". Use the space for the band's coverage (HIRING-2).
- README (186 lines): too long above the fold. To the end of Results it carries two large tables and a 300-word variant paragraph. Cut README.md:21 to :23 (a repeat of :8 plus the gloss), cut README.md:49 to two sentences ending on "both readings together: 5.7 against 5.5", move README.md:53 to Method, and delete the duplicate cabin table at :71 to :79.
- Dashboard: the density is right. "On Gulfstream's own registration" (258 jets, a count that the page itself says is not a delivery queue) can move below "What it means for GD".
- Note (8 pages): cut to about 6. Replace the 38 EDGAR folder links in source 9 with one line pointing to `data/processed/gd_deliveries.csv`, which holds every accession number. Cut the risk section to the Gulfstream-specific items. Drop Exhibit 10 or refresh it.
- Resume bullets: bullet 1 is about 40 words; trim it. Interview notes: 42 lines is fine for private prep (HIRING-12 on whether they belong in the public tree).

**7. Do the resume bullets and interview notes claim what the repository does not back? Would any of them hurt?**
The numbers in all three bullets check out (5.5, 6.9, 4.6, 32.0, 40, 8.0, outside the band). The score file carries accession 0000040533-26-000036, which supports "scores it from GD's SEC filing". The problems:
- "Built" (bullets 1 and 2) and "Wrote" (bullet 3) sit against README.md:180, which says the project was built with Claude Code in sessions the author directed. An interviewer who reads both will probe authorship first. INTERVIEW_NOTES.md:35 to :36 gives a one-line answer, which will not hold up (HIRING-4).
- Bullet 1 says "26 held-out quarters" with no hint that the rules were committed two minutes before scoring, with the data already in the repository (README.md:119). The question is answerable from INTERVIEW_NOTES.md:7, but the bullet invites it.
- INTERVIEW_NOTES.md:5: "I read every Gulfstream jet in the FAA's public registry". README.md:159 says 17 G700s are outside the count (HIRING-3). An interviewer who read the limitations will catch it.
- INTERVIEW_NOTES.md:13: the drift from "about two deliveries per event in 2016 to 0.72 in 2026Q2" checks against README.md:156 (1.92) and data.json (0.7193).
- The notes would help the author in interview. They give the losing baseline, where the lead came from (2023 and 2024), and the six quarter plans. The risk lies in what they omit: which decisions were the author's.

**8. The three changes that would most raise standing, best first**
1. Rewrite the post's first two lines to say what was built while keeping the miss (the 136-character version in answer 4). Put the band's 18 of 26 coverage into the post.
2. Cut the README top to one screen: the live record, one backtest table, the three-sentence framing and links. Move the variants, the design-window detail and the duplicate cabin table into `results/`.
3. Make authorship concrete. Resume bullets should say "with an AI coding agent". The interview notes should name the decisions the author made, and the prep files should stay out of the public tree.

## Findings

### HIRING-1 (S1): Home-folder paths naming the owner's macOS account in 16 public build briefs
- Surface: `docs/build/briefs/`, 24 lines in 16 files. They include review1_analyst.md:3,5; airframe_audit_1.md:3; airframe_audit_2.md:3; airframe_audit_3.md:3; guidance_check_1.md:3; guidance_check_2.md:3; guidance_check_3.md:3; critique_a.md:5; critique_b.md:5,6,7; _claims_common.md:3; review1_factcheck.md:3; review1_ops.md:3,5; review1_spec.md:3,5; review1_numbers.md:3,5; review2_docs.md:3,13; review2_code.md:3,11. Hand-written (agent briefs); nothing under `src/gdn` writes them.
- Evidence: `grep -rIc "<home-folder prefix>" . | grep -v ":0$"` in the cold tree lists exactly these 16 files and no others. Each hit is an absolute path that begins at the macOS home folder and names the account. Some hits also expose the layout of a private prompt library and a plugin cache (critique_b.md:5 to :7, review1_spec.md:5). The cold tree has no history, so I cannot cite a commit.
- Fix: replace each path with `<repo>` or `~`, or leave `docs/build/briefs/` out of the public tree. If these lines are in git history, a new commit does not remove them from history. The owner must decide whether that is acceptable before the repository goes public, since history may not be rewritten under this audit's rules. An informed auditor should check this with `git log -S`.

### HIRING-2 (S2): The post calls the band "my 80% band" with no coverage figure
- Surface: docs/LINKEDIN_POST.md:4, generated by `src/gdn/report.py:565`.
- Evidence: the post says "The 2026Q3 miss was 8.0, outside my 80% band of past misses." `site/data.json` metrics.holdout.band gives hits 18, n 26, coverage_pct 69.23, cp95 48.2 to 85.7. README.md:6 and :51 disclose "whose nominal level is 80% and which held 18 of 26". The post does not. Read alone, the post suggests a 1-in-5 event, while the band missed about 1 in 3 past quarters.
- Fix: "The 2026Q3 miss was 8.0, outside my band of past misses, which held 18 of 26 past quarters against a nominal 80%."

### HIRING-3 (S2): "Every Gulfstream jet" on three surfaces, while the README says 17 G700s are outside the count; the note's limitations omit the scope and holder gaps
- Surfaces: note page 2, "I read every Gulfstream jet in the FAA's aircraft registry" (report/note.html:67, generated by `src/gdn/note.py:373`). site/index.html:100, "Each Gulfstream jet in the FAA registry gets a delivery date" (hand-written). docs/INTERVIEW_NOTES.md:5 (hand-written).
- Evidence: README.md:159 says the FAA files one G700 type code under an engine-type code the scope rule drops, "so the 17 G700s registered to Gulfstream under it on 2026-10-30 are outside the count". It also says the holder rule misses a leasing registrant. `grep -n -i "G700\|engine\|LEASING"` on the note text finds only the product-cycle line on page 2. The note's "Limitations of the method" (page 6) has nine bullets and none on scope or holder, although README.md:159 says the amendment is to be decided before the next lock. The two surfaces disagree, and no past figure changes (README: "no past count is short").
- Fix: "I read the Gulfstream jet types in the FAA registry that my scope rule keeps, including the G280..." Apply the same change on the dashboard and in the interview notes. Add a "Scope and holder" bullet to the note's limitations that matches README.md:159.

### HIRING-4 (S2): Resume bullets claim sole authorship that the README qualifies
- Surface: docs/RESUME_BULLETS.md:1 to :3 (hand-written).
- Evidence: the bullets begin "Built a Python pipeline", "Built a daily job" and "Wrote a cited research note". README.md:180 says the project was built with Claude Code, "in sessions I ran and directed", and that many commits carry a `Co-Authored-By: Claude` trailer. A recruiter who reads the resume and then the README sees the gap. Bullet 1 also says "26 held-out quarters", while README.md:119 says only the locked quarters are out of sample in the strict sense.
- Fix: "Designed and directed, using an AI coding agent, a Python pipeline that..." For bullet 1, write "on 26 backtest quarters scored after the rules were committed". Expand INTERVIEW_NOTES.md:35 to :36 to say which choices were the author's.

### HIRING-5 (S3): "Registry count" names the scaled estimate, so three surfaces need a gloss
- Surfaces: README.md:21 and :23, docs/LINKEDIN_POST.md:6, note pages 1 and 2. Generated by `src/gdn/report.py:42`, `:47` and `:583`, and by `src/gdn/note.py:384`.
- Evidence: the headline says "the registry count was off by 5.5". The table's "Raw registry count" row says 6.2. README.md:23 then explains that "registry count" means the first row. The dashboard lead (site/app.js:92) says "registry estimate" for the same 5.5. The post adds "(Registry count: my scaled estimate; the pace: mine.)" and names the guidance pace two ways in one post.
- Fix: say "registry estimate" in the headline sentence on every surface and delete the glosses. In the post, use one name for the pace.

### HIRING-6 (S3): The dashboard's largest figure after a score is the estimate, not the result
- Surface: site/app.js:136 (big figure), :164 to :165 (GD reported, seventh fact). Hand-written.
- Evidence: output/charts/dashboard.png shows "32.0 deliveries, locked estimate" in the large type. "GD reported 40 deliveries" is seventh in the facts list, below the quarter window and "GD's typical quarter".
- Fix: once a quarter is scored, show "32.0 locked · 40 reported · missed by 8.0" as the large line, with GD's count first in the facts.

### HIRING-7 (S3): "Track record" omits the only live quarter
- Surface: site/index.html:64 to :66 (hand-written). The README chart at README.md:11 and the link-card image site/preview.png are drawn by the chart generator under `src/gdn/charts.py`.
- Evidence: `site/data.json` quarters run from 2016Q1 to 2026Q2 (42 quarters). The 2026Q3 lock and GD's 40 are not on the track-record chart.
- Fix: rename the section "Backtest, 2016Q1 to 2026Q2", or add the 2026Q3 locked point and GD's count, marked as live.

### HIRING-8 (S3): The workbook's Summary sheet shows blanks in any viewer that does not calculate
- Surface: output/gd_gulfstream_model.xlsx, sheet Summary, B2:C6. Generated by `src/gdn/workbook.py` (line 304 sets `fullCalcOnLoad`).
- Evidence: `openpyxl` with `data_only=True` returns no values for Summary B2:C6. With `data_only=False` it returns formulas such as `=AVERAGE(Quarters!N18:N43)`. About!A21 discloses this, but at row 21 of the first sheet.
- Fix: run a headless recalculation in the build so the file carries cached values next to its formulas. Otherwise, move the About!A21 sentence to row 2.

### HIRING-9 (S3): Note Exhibit 11, "The workbook's Summary ... sheets", drops the guidance row
- Surface: note page 7. Generated by `src/gdn/note.py:584` to `:597`.
- Evidence: the exhibit lists four rows: ratio 5.5, raw 6.2, same quarter last year 4.6, last quarter 8.8. The workbook's Summary has a fifth, A6 "MAE guidance" with C6 `=AVERAGE(Quarters!T18:T43)`, and A9 tells the reader to "Read rows 2 to 6 before anything else". No figure differs. The 6.9 appears in Exhibit 2.
- Fix: add the row "Average miss, GD guidance pace" (design blank, held out 6.9).

### HIRING-10 (S3): Repetition and density above the fold in the README and on note page 1
- Surface: README.md:8, :21, :23, :49, :53, :71 to :79, generated by `src/gdn/report.py`. Note pages 1 and 2 repeat key point 1 word for word (`src/gdn/note.py`).
- Evidence: the five Large cabin and Mid cabin pairs in the Results table (README.md:29 to :33) match the "Average miss by cabin" table (README.md:75 to :79) exactly. The answers to questions 3 and 6 quote the rest.
- Fix: the cuts in answer 6.

### HIRING-11 (S3): "What it means for GD" frames mechanical arithmetic as an investment read
- Surface: site/index.html:88 (hand-written); the pre-release wording is at site/app.js:432 to :435.
- Evidence: under that heading, before a score, the page says the delivery-based figure "falls" against the year-ago quarter. The section's own text calls it "a mechanical estimate" (site/index.html:89).
- Fix: rename the section "Revenue arithmetic from the delivery estimate".

### HIRING-12 (S3): Interview prep and resume bullets sit in the public tree
- Surface: docs/INTERVIEW_NOTES.md (title "Interview notes", section "Questions I expect"), docs/RESUME_BULLETS.md. Hand-written.
- Evidence: the files are in the cold copy, so they will be public. A hiring manager who finds the candidate's scripted answers reads them as coached.
- Fix: keep both out of the repository. Alternatively, rename the interview notes `docs/FAQ.md` and drop the interview framing.

### HIRING-13 (S3): A stale dashboard screenshot is tracked
- Surface: output/charts/dashboard.png. It is not written by `src/gdn`; `tools/determinism.py:15` skips it, and no README, site or note file references it.
- Evidence: the screenshot's live note ends "so it is likely too narrow for a live quarter". site/app.js:170 now writes "so it may not fit a live quarter".
- Fix: regenerate it or leave it out of the public tree.

## Improvements that would raise the project's standing

1. Open the post with what was built, keeping the miss in the first 140 characters: "I estimate Gulfstream deliveries from FAA registrations and lock each one on GitHub before GD reports. First lock: 32.0. GD reported 40."
2. Make the README's first screen self-sufficient: the live record, one table, the three-sentence framing. Everything else goes one click down.
3. Add one line to the README's live record on the revenue result that the note (Exhibit 8) and dashboard already show. The delivery-based Aerospace figure, $2.7B, missed GD's $3.5B by 23.4%, while the growth rule missed by 2.7%. Showing the losing method here, as with deliveries, adds credibility.
4. Add a short "Before the next lock" paragraph naming the G700 scope amendment and the holder rule from README.md:159. It shows judgment about the method's known gaps.
5. Trim the note to about six pages: one line for the EDGAR sources, the Gulfstream-specific risks only, and no stale exhibit.

## Checked and clean

- Lock integrity: `shasum -a 256 predictions/2026Q3.json` gives 3c4cdbd0...6f23, which equals the release notes (`gh release view lock-2026Q3`), README.md:106 and data.json. The release was published 2026-10-29T05:51:24Z by `github-actions[bot]`, which is 01:51 ET as stated.
- GD's 2026Q3 release (accession 0000040533-26-000036, fetched from SEC by urllib) gives deliveries 35 large and 5 mid (total 40), 39 a year earlier, Aerospace revenue $3,536M against $3,234M, and Marine Systems total backlog $146,865M. These match the post, README, dashboard data and note Exhibits 8 and 10.
- Backtest averages recomputed from data.json: ratio 5.523, raw 6.192, guidance 6.917, same quarter last year 4.615, last quarter 8.808.
- Note page 3 on the 22 sourced quarters: 5.250326, 7.356760 and 4.636364 round to the printed 5.3, 7.4 and 4.6.
- README.md:69: in 2023 and 2024, guidance 12.51 and ratio 3.48; in the other 18 quarters, ratio 6.43, guidance 4.43, seasonal 4.44. The guidance pace was closer in each of the last five quarters, the locked one included.
- README.md:92: the 2026Q3 window holds 35 large and 7 mid events in every daily snapshot from 2026-10-27 to 2026-11-12. I counted from `data/snapshots/daily/*.serials.csv.gz`.
- Sign tests 14/12, 11/15 and 16/10 with no Holm rejection; band 18 of 26 (69.2%, 48.2% to 85.7%); "about 33" deliveries a quarter (32.69). All match data.json.
- README.md:106: 160 minus (38 + 41) = 81 jets, and an even split gives 40.5.
- Every relative link in README.md resolves in the cold tree.
- Disclaimers appear on every surface. The note says "No rating or price target." No stock words and no em or en dashes appear on the public surfaces.
- Email-like strings in the tree are only `example.com` and `example.invalid` placeholders in tests and tools.

## Suspicions, not proven

- On a phone, the hero probably fills the first screen, so the live miss sits below the fold. I inferred this from style.css and did not render it. A 375-pixel render would settle it.
- Note source 6 is a transcript URL dated 2026/08/07 for a 2026-07-29 call. That may be the page's own publication date. Opening the page would settle it.
- `docs/build/` holds 30 entries of agent working files (critiques, review briefs, plans). I read only the grep hits. Other content there may read badly to a recruiter even where it exposes nothing.
- I cannot confirm from tracked data that the dropped G700 type code exists, because the stored ACFTREF rows are in scope only. The finding rests on the README's own statement.

## Could not check, and refused commands

- The Pages dashboard and the repository pages, which are private today (known).
- The defense backlog study page and the author's personal site. I did not fetch them, because both host names carry the owner's account or personal name.
- Workbook formula values. I did not recalculate the file; I only read its formulas and confirmed it has no cached values.
- No command was refused or blocked.
