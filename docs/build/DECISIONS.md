# Decisions

Preflight passed, 2026-10-19 11:33 EDT (15:33 UTC). It runs once; never rerun it.

## Preflight

```
## sec_ua
non-empty: ok
## gdn_disclosure
non-empty: ok
## gh auth status
github.com
  ✓ Logged in to github.com account rishabbshankar226 (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
## origin
https://github.com/rishabbshankar226/gulfstream-delivery-nowcast.git
## status
## main...origin/main
## rev-list count
1
## ls-files
.gitattributes
## github private, default branch
true
main
## exclude lines
absent (hook blocked writing .git/info/exclude; see below)
## gate
-rw-r--r--  1 rishabbshankar  staff  154801 Oct 19 09:49 .../prompt library/gulfstream-delivery-nowcast/gate/jetgate.py
## date ET
Mon Oct 19 11:33:32 EDT 2026
## actions enabled
true
```

- `~/.gdn_disclosure` was missing at the start. The owner answered "No position in GD" in chat, so I wrote Part A's example sentence: "The author holds no position in General Dynamics."
- Part A step 7's second block had not run. With the owner's approval I wrote `.claude/settings.local.json` with Part A's exact allowlist. A PreToolUse hook from the `claude-seo-ai` plugin blocked the shell write to `.git/info/exclude` ("VCS internals"). I did not route around the hook. Instead, `.gitignore` lists `/CLAUDE.md` and `.claude/`, which keeps both off GitHub and keeps P2's tree clean. The owner's global `~/.config/git/ignore` already ignores `**/.claude/settings.local.json`.
- The session runs in the Claude desktop app (Code tab), not under `caffeinate -is claude`. The app's keep-awake hold is on (`session_idle`). The reference folders were readable without `--add-dir`.
- GitHub Actions is enabled on the repository (`true`), so Phase 5 runs and watches the workflow.

## Permission smoke test (Phase 0, first action)

All passed with exit 0, and no prompt came up:
- `ls ~/Downloads | head -3`: listed three entries.
- `curl` of the FAA download page with the full Chrome header set: HTTP 200, 113,511 bytes.
- `curl` of `https://data.sec.gov/submissions/CIK0000040533.json` with the `~/.sec_ua` User-Agent: HTTP 200, 155,154 bytes.
- `gh api user`: `rishabbshankar226`.
- `open -g -a "Google Chrome" about:blank`: exit 0.
- A write and delete under `/tmp` and `~/.cache/gdn-smoke`: ok.
- `git init`, commit, push to a bare repository and `git reset --hard` in `/tmp/gdn-smoke`: ok.
- `git ls-remote origin` showed `dba3e3a` on `refs/heads/main`. `git push --dry-run origin main` printed "Everything up-to-date".
- Headless Chrome: `Google Chrome 155.0.8059.82`.

## Environments

- Project: `.venv` on CPython 3.11.16 (uv 0.12.5) with openpyxl 3.1.5, matplotlib 3.9.2, pytest 8.3.3, playwright 1.64.0 and Playwright's Chromium. Frozen in `requirements.lock`, 20 lines.
- Gate: `~/.cache/jetgate/venv`, CPython 3.11, openpyxl 3.1.5 and formulas 1.3.4. `--selftest`: "mutants: 64 of 64 killed", "selftest PASS in 38s".

## Backtest snapshot

- §3.3's first route worked: `curl` with the full Chrome headers, 15:34 UTC, 72,927,535 bytes, first bytes `PK`. Saved as `data/raw/faa/ReleasableAircraft-2026-10-19.zip` (America/Chicago date 2026-10-19). That date is the backtest snapshot.

## Tool routing

- Present: `dataviz`, Impeccable (`impeccable:impeccable`), `vectorlab-ux-skills:viewports`, `anthropic-skills:citation-integrity-skill`, `anthropic-skills:anti-hallucination`, `superpowers:systematic-debugging`, `anthropic-skills:root-cause-debugging`.
- Absent: a skill named `pdf-reading`. Fallback: the Read tool reads PDF pages directly, with `sips` or `qlmanage` to PNG for page images.
- Left alone, though installed: `design-taste-frontend` and `redesign-existing-projects`. The rest of the prompt's leave-alone list (`gpt-taste`, `high-end-visual-design`, `stitch-design-taste`, `minimalist-ui`, `industrial-brutalist-ui`, `brandkit`, `image-to-code`, `imagegen-frontend-web`, `imagegen-frontend-mobile`, `full-output-enforcement`, `find-skills`) is not installed in this session. They direct marketing pages or generate images, and this is a data product that matches the backlog dashboard.
- Subagent types available: `general-purpose`, `Explore`, `Plan`, `claude`. Checkers and reviewers run as `general-purpose` from briefs in `docs/build/briefs/`.

## Limitations (collected for the README)

## Phase 1: data

Real FAA header lines of the 2026-10-19 zip (each starts with a UTF-8 byte-order mark and ends `,\r\n`):
- `ACFTREF.txt`: `CODE,MFR,MODEL,TYPE-ACFT,TYPE-ENG,AC-CAT,BUILD-CERT-IND,NO-ENG,NO-SEATS,AC-WEIGHT,SPEED,TC-DATA-SHEET,TC-DATA-HOLDER,`
- `MASTER.txt`: `N-NUMBER,SERIAL NUMBER,MFR MDL CODE,ENG MFR MDL,YEAR MFR,TYPE REGISTRANT,NAME,STREET,STREET2,CITY,STATE,ZIP CODE,REGION,COUNTY,COUNTRY,LAST ACTION DATE,CERT ISSUE DATE,CERTIFICATION,TYPE AIRCRAFT,TYPE ENGINE,STATUS CODE,MODE S CODE,FRACT OWNER,AIR WORTH DATE,OTHER NAMES(1),OTHER NAMES(2),OTHER NAMES(3),OTHER NAMES(4),OTHER NAMES(5),EXPIRATION DATE,UNIQUE ID,KIT MFR, KIT MODEL,MODE S CODE HEX,`
- `DEREG.txt`: `N-NUMBER,SERIAL-NUMBER,MFR-MDL-CODE,STATUS-CODE,NAME,STREET-MAIL,STREET2-MAIL,CITY-MAIL,STATE-ABBREV-MAIL,ZIP-CODE-MAIL,ENG-MFR-MDL,YEAR-MFR,CERTIFICATION,REGION,COUNTY-MAIL,COUNTRY-MAIL,AIR-WORTH-DATE,CANCEL-DATE,MODE-S-CODE,INDICATOR-GROUP,EXP-COUNTRY,LAST-ACT-DATE,CERT-ISSUE-DATE,STREET-PHYSICAL,STREET2-PHYSICAL,CITY-PHYSICAL,STATE-ABBREV-PHYSICAL,ZIP-CODE-PHYSICAL,COUNTY-PHYSICAL,COUNTRY-PHYSICAL,OTHER-NAMES(1),OTHER-NAMES(2),OTHER-NAMES(3),OTHER-NAMES(4),OTHER-NAMES(5),KIT MFR, KIT MODEL,MODE S CODE HEX,`
- Every field §3.3 names is present after normalization, `YEARMFR` included.
- Every file decodes as strict UTF-8, so the stored subset, written as the decoded text re-encoded, is the zip's own bytes.
- In the real files, the header line is not aligned with the fixed-width data, so "cut at the header line's comma positions" would garble a row. No in-scope row needs the fallback: every one splits into the header's field count (14, 35 and 39), and none holds a double quote. The fallback is implemented as written, and the gate does the same; the fixtures align their header with the data so a test can exercise it.
- Scope: 54 ACFTREF codes, including the G280 under `IAI LTD` (codes 3980218 and 4500314). Subset: 2,821 MASTER and 1,296 DEREG rows; 4,053 airframes.
- The model "GULFSTREAM 200" under the maker "GULFSTREAM AEROSPACE" (codes 3980202, 3980211) reads `large` by §3.3's cabin rule, since it contains no `G200` and its maker is not IAI or Israel. Gulfstream's own G200 files under the IAI codes, which read `mid`. I kept the rule as written.
- SEC: all 38 results releases, 2017Q1 to 2026Q2, parsed. Fiscal ends come from the 10-Q report dates and match the gate's pins. The sentence check ran where a release has the sentence: 2020Q2 (total only), 2024Q2, 2024Q3 and 2024Q4, all agreeing. Every prior-year column matches the year-earlier release.
- Gate `--only faa,truth`: F1 to F4, T1 and T2 pass with no warning, so T2 read every release from SEC's text. T3 fails until Phase 2 writes `data/guidance.csv`.
- I added `data/processed/book_to_bill.csv` (the 2026Q2 orders paragraph: defense 1.4, Aerospace 1.5, company 1.4) so the note can quote it on an offline rebuild.

## Phase 2: §8 stop on design-year coverage (2026-10-19 11:58 EDT)

`results/diagnostics/coverage_design.csv`, registry events over reported deliveries by year (E1 and E2 agree to the airframe except 2019 large, 96 against 97):

| Year | Large | Mid | Total |
|---|---|---|---|
| 2016 | 53 / 94 = 0.564 | 10 / 27 = 0.370 | 63 / 121 = 0.521 |
| 2017 | 64 / 90 = 0.711 | 14 / 30 = 0.467 | 78 / 120 = 0.650 |
| 2018 | 63 / 92 = 0.685 | 17 / 29 = 0.586 | 80 / 121 = 0.661 |
| 2019 | 96 / 114 = 0.842 (E2 97) | 21 / 33 = 0.636 | 117 / 147 = 0.796 (E2 118) |

Mid cabin falls below 0.5 in 2016 and 2017 under both definitions, which is §8's Phase 2 stop. F3 and F4 pass, so the gate's own implementation of §3.3 gets the same airframes and counts: this is the rule meeting the real registry, not a code bug.

What the airframe table shows: of the G280s built in 2016 and 2017 that have no E1, all 26 carry no Gulfstream-held record and no export record. Their only date is a current customer certificate a median 2,537 days (about seven years) after first airworthiness, so the bound drops them. That fits MASTER keeping only the current certificate once a jet is resold or its registration renewed. Large cabin shows the same pattern (70 airframes built 2016 to 2017 without E1, median 2,743 days). Coverage rises toward the snapshot year, as fewer of the newer jets have changed hands. G280s exported without any US registration leave no record at all and cannot be counted here.

Asked the owner how to proceed; the guidance checkers kept running meanwhile.
- Owner's answer (11:59 EDT): "Keep §3, continue". The definitions stay as preregistered. The low and rising design-year coverage goes into Limitations (the `coverage` limitation) and the error analysis, and §3.4's coverage-drift flag watches the holdout's end. `python -m gdn diagnostics` still prints the flagged cabin-years but exits 0, so `make all` runs.

## Phase 2 to 3: numerics

- Nearest rank is `sorted(xs)[math.ceil(p * n) - 1]` with p the float 0.1 or 0.9. The float 0.1 is slightly above one tenth, so at n = 30 the P10 position is 4, not 3; exact arithmetic on that float gives 4 too. The gate computes it the same way. Among the holdout bands, only 2024Q3's uses 30 past errors.
- Clopper–Pearson by bisection on the binomial CDF: 21 of 26 gives 0.6065 to 0.9345, and 5 of 10 gives 0.1871 to 0.8129, matching published tables.

## Phase 2: guidance and the design window

- `data/guidance.csv`: three checker subagents, nine calls each, from briefs in `docs/build/briefs/`. I re-derived each cached page's text from its HTML and found every one of the 27 quotes verbatim (`.build/verify_quotes.py`, then `tools/build_guidance.py`, which refuses a quote it cannot find). 17 calls state a number; T3 passes against the gate's 27 pinned calls.
- Sources: Motley Fool transcripts for 23 calls. MarketBeat for 2023-04-26, 2025-04-23 and 2025-10-24, where no Fool page loaded; 2023-04-26 has an AllMind copy and the 2025 calls a Bullfincher copy as backups. All of them are cached under `data/raw/sources/calls/`, out of git.
- Readings worth recording:
  - 2021-01-27: "So all up, 10 fewer aircraft." names no base figure in the sentence, so by §3.4 the call states none. No 2021 call states a full-year number, so 2021's four quarters fall back to seasonal.
  - 2023-07-26: "five to six fewer aircraft than the 145" reads 139.5. 2023-10-25: "10 to 12 fewer aircraft this year than the 145" reads 134.
  - 2024-10-23: "150 versus 160" reads 150. 2025-07-23: the cached Fool text reads "150 to 155", not the "$150 million to $155 million" the prompt cites; either way it reads 152.5. 2026-01-28: "160 with a little upside" reads 160.
  - 2022-04-27, 2022-10-26, 2024-04-24, 2025-04-23, 2025-10-24 and 2026-04-29 give only a quarter's plan or a confirmation without a number, so they state none, and the latest numeric call of the year carries forward.
- Process note: the checkers shared `data/raw/sources/calls/` and each converted every `.html` there to `.txt`, so some `.txt` files were rewritten by more than one checker. I checked every quote against the HTML itself, so this does not affect any row.
- Design window (12 quarters, 2017Q1 to 2019Q4), MAE in aircraft: seasonal 5.0, last 3.83, raw E1 9.42, ratio E1 5.47, raw E2 9.33, ratio E2 5.58. The chosen definition is **E1** (ratio 5.472548294344893 against 5.5807858422376135). In the design window ratio did worse than last; that is recorded before any holdout figure exists.

## Phase 3: holdout

- Gate `--only faa,truth,model,prereg`: no failing code. Holdout MAE in aircraft: seasonal 4.6, last 8.8, guidance 6.9, raw 6.2, ratio 5.5. Sign tests of ratio against guidance 14 wins and 12 losses, against seasonal 11 and 15, against last 16 and 10; Holm rejects none. The headline therefore takes the null wording, with guidance named first, since 22 holdout quarters have a numeric outlook.
- `results/error_analysis.md` comes from `src/gdn/errors.py`. No filing or call states why the registry count differed from GD's count in any of the five largest misses, so none names a cause. Two carry GD's own statement about the quarter's deliveries as context, each tested against its cached source.

## Phase 4: live estimate

- `results/live/2026Q3_build.json` from the 2026-10-19 snapshot: 35 large and 6 mid events in the 2026Q3 window (2026-07-05 to 2026-10-04); trailing reported 140 and 23 against trailing registry 187 and 28; estimate 31.1 (26.2 large, 4.9 mid), past-miss band 20.4 to 36.4. It is written once and never edited. The first path row, the latest file and the daily airframe table for 2026-10-19 (identical to `serials.csv`) come from the same snapshot.
- `results/estimates.json` from the build file: Aerospace $2.6B from 31.1 deliveries at trailing revenue per delivery.
- Gate `--only live,segments`: no failing code. L3 warns "not locked yet". S3 warns that the gate could not parse the segment exhibit from SEC's text for some releases from 2024Q3 on. My own parser read all eight, S1 matches the gate's pins, and Phase 5 allows both warnings.

## Limitations for the README (each with R3's keyword)

1. **Export.** A jet exported to a foreign registry without a Gulfstream test registration leaves no US record, so the registry never sees that delivery. The G280, built by IAI in Israel, often leaves no Gulfstream-held record at all: none of the 26 G280s built in 2016 and 2017 that lack an E1 has one.
2. **Processing.** Registry processing can lag by months. The backtest reads events by their stamped date in a file that had years to fill in, while a live estimate sees only what has posted. The truncation table shows how fast the error grows when a quarter's own events are cut 30, 60 or 90 days before its end.
3. **Military.** Military and special-mission airframes may never reach the civil registry, though GD may count some of them as deliveries.
4. **Handover.** GD counts a delivery at its own handover. A registration or cancellation date only approximates that day, so an event can land in the quarter before or after.
5. **Coverage.** The ratio assumes the registry's coverage of GD's count holds steady from one year to the next. It does not: in the design years, registry events over reported deliveries rose from 0.52 (2016) to 0.80 (2019), and mid cabin sat at 0.37 and 0.47 in 2016 and 2017. MASTER keeps only an airframe's current certificate, so a resold or renewed jet loses its first owner's date.
6. **Used jet.** A used jet with no airworthiness date or year of manufacture, or one whose maker code changed between registrations, can read as a new delivery. Imported used jets that received a new US airworthiness date also pass the bound.
7. **Band.** The past-miss band comes from errors measured on a finished registry file, so it is likely too narrow at a live lock, when recent registrations have not posted.

Also for `## Data`: the G280 is filed under the maker `IAI LTD` (model `GULFSTREAM G280`); GD's counts use the delivered basis that came with ASC 606, adopted 2017-01-01 and applied back to 2016.

## Phase 5: critical path

- Workflows: `pages.yml` word for word; `nowcast.yml` per §3.11; `test.yml` also installs Playwright's Chromium, as the backlog project's does, so the browser test runs in CI instead of skipping. MIT `LICENSE` copied from the backlog project (Rishabb Shankar). `SEC_UA` stored as a repository secret at 16:10 UTC.
- GitHub Actions was "degraded" on githubstatus.com and both runs sat queued about 17 minutes. While waiting I started Phase 6's workbook and charts; nothing from them was committed before this "Critical path ready" commit.
- **The runner reached both sources.** `nowcast` run 39283382067 (workflow_dispatch, 2026-10-19 16:10 UTC): "SEC reachable: HTTP 200, 155154 bytes" and "FAA snapshot 2026-10-19 by curl, 72927535 bytes", the same size as the Mac's download. Akamai did not refuse the runner this time, against eight refusals reported to 2026-10-18; it may refuse again, so the Mac stays the primary. The `test` run 39283387767 passed.
- The run pushed b205fbe, rewriting `data/snapshots/daily/2026-10-19.serials.csv.gz` with identical content but a different gzip header: Python 3.11's `gzip.compress(..., mtime=0)` goes through zlib, which stamps the OS (0x13 on macOS, 0x03 on Linux). Fixed: every `.gz` is written with the OS byte set to 255 and is never rewritten when its decompressed content is unchanged (`files.write_gz`), so the Mac and the runner no longer churn each other's files. Existing files keep their bytes.
- Same-date runs: a second download on a Chicago date replaces that date's zip, daily table and path row, as §3.11 says, and the stored subset too. Two dates are exempt: the backtest date and any date a prediction file names. For those the download is skipped and every stored file kept (`faa.download`, and `live.ingest` as a second guard), so the backtest and L1 can always rebuild from what they read. (Corrected in review round 1, S3: until then the download skipped every stored date.)
- Lock rehearsal (`tools/rehearsal.py`, `docs/build/REHEARSAL.md`): all 11 cases pass, including a push that loses a race to a second clone and is retried after `git reset --hard @{u}`. The gate's `live` family on the rehearsal clone: no failing code; L4 warns only that the fixture 8-K is not on SEC.
- Gate `--only faa,truth,model,prereg,segments,live` at 12:34 EDT: 20 assertions, 0 failing, warnings S3 and L3 ("not locked yet"), both allowed.

## Phases 6 to 8: notes

- **Gate N1 and accession numbers.** §4 says the number check skips accession numbers, but the gate strips dates first, and its date pattern `\d{4}-\d{2}-\d{2}` matches inside an accession ("0533-26-00"), so the accession pattern never fires and the leftovers fail as numbers. Rather than stop, the note prints each source accession as its EDGAR folder URL (`https://sec.gov/Archives/edgar/data/40533/<accession without dashes>`), which the URL rule skips and which is a working link. The README's checked sections carry no accession numbers.
- **The guidance pace before a score.** The gate accepts the live quarter's guidance pace (33.8 for 2026Q3) in the docs only once the quarter is scored, so the README's Live record and the note print it after the score. The dashboard shows it now, since runtime figures are not number-checked and §3.10 asks for it.
- **The claims registry** holds only the claims the note cites (32 of 41 sourced; N4 fails on unused entries). The three topic files in `docs/build/claims_*.json` keep all 41; the note's code picks which ten product claims to cite and prunes `report/claims.json` to match.
- **The defense study's MAPEs** are printed as the owner's own study with a link, not as claims, since `claims.json` admits only filing, call, faa and press sources.
- Full gate after Phase 8: 42 assertions, 0 failing, warnings S3 and L3 ("not locked yet").

## Phase 9: self-checks

- **Tests of the tests** (`tools/mutate.py`, `docs/build/MUTATION.md`): 12 of 12 rules caught. On the first pass the IAI cabin rule survived, because the fixture's IAI G280 also reads mid by its model name. The fixture gained an Israel Aircraft Industries "GULFSTREAM 200" type that only the maker rule makes mid-cabin (`tools/make_fixtures.py` regenerates the fixtures). Writing a test for the second-lock rule exposed a real bug: when a release existed but the clone had no prediction file, the lock crashed while recording it. It now records only when the prediction is present and otherwise stops without creating anything.
- Source files held literal U+FEFF characters where the escape `"﻿"` was meant (`faa.py`, `test_faa.py`); they now use the escape.
- **Determinism** (`make check-determinism`, `tools/determinism.py`): `make all` twice gives identical bytes for all 28 files it writes (the workbook rebuilt both times), and it reproduces the committed outputs exactly.
- **As-of study** (`tools/asof.py`, `results/exploratory/asof.csv` and `asof.md`): the Wayback Machine holds 75 successful captures; six quarters have one 20 to 30 days after the fiscal end, and four can be scored. In all four the as-of estimate missed by less than the 2026-10-19 copy (2017Q1 3.3 against 5.6; 2025Q3 6.6 against 6.8; 2026Q1 5.3 against 7.4; 2026Q2 1.7 against 3.8), and its band held two of three held-out quarters. Reading the lags from the same unfinished file seems to offset late posting, so the truncation table is the harsher test. Four quarters prove nothing; the result is reported as secondary in the README's Method and in one sentence of the note, and changes no definition.
- Fresh clone, run early while the audits ran: `make all` exit 0 with no tracked file changed; `make test` 58 passed and 2 skipped (claims and error statements, whose source cache stays out of git); gate on every family but `repo`, 40 assertions, 0 failing, warnings F2 (no raw zip in a clone), S3 and L3.
- **An audit agent deleted files outside its own set.** Auditor 1 ran `rm -f *-planephd.html` in the shared, gitignored cache `data/raw/sources/audit/` to clear its own empty Cloudflare challenge pages; the pattern was not limited to its serials, and auto mode flagged the report. No planephd file remains, and no audit row cites one, so nothing the audit relies on was lost. Later briefs say to delete nothing.
- **Airframe audit** (`docs/build/AIRFRAME_AUDIT.csv`, merged from three auditors' files; 30 airframes picked by `tools/audit_pick.py` with a fixed seed: 10 domestic sales, 10 exports, 5 counted only under E2, 5 the bound removed). 10 of 30 rows (33.3%) are `no`. I re-read the cached source of every `no` row myself:
  - Contradicted by a source (6): five used jets read as new deliveries, because a re-import or resale brought a fresh US airworthiness date that the one-year bound accepts (G450 4122, built 2008; G450 4076, built 2007; G550 5340, delivered as M-ATPS 2011-12-16; G550 5269, delivered as B-8122 2010-09-09) and one with no airworthiness date or year at all, so no bound applied (G-III 466, built 1985); and one military jet, USAF C-37A 571, delivered 2000-02-21, a quarter before its 2000-06-02 registry event.
  - Not confirmed (4): G650ER 6270 (an aircraft-history field gives 2017-09-22 against the 2018-03-09 certificate; untraced, so `no` under the doubt rule), and three airframes the bound removed (72023, 5467, 2177) for which no source dates a first delivery.
  - **Open:** §6 asks for at least 25 rows with a source other than a mirror. One has one: 571 cites GD's own release of 2000-02-21, as republished on globalsecurity.org. No Gulfstream or GD release, trade-press item or owner announcement naming these serials turned up, and gd.com, investorrelations.gd.com and gulfstream.com refuse scripted downloads. The audit therefore checks the registry reading (mirror dates agree wherever they cover the event) and exposes the used-jet weakness; it does not independently date deliveries. The rate goes into the README's and the note's Limitations, and no definition changes.

## Review round 1

The findings, fixes, commits and regression tests are in `docs/build/REVIEW.md`. Decisions taken there:

- **Audit corrections (N2).** Above, 466 is now counted as a used jet with no airworthiness date or year, not one let through by a fresh date, and one row (571) has a non-mirror source. The README and the note give the breakdown as four, one, two and three.
- **The runner will probably lock (OPS-3).** The runner's curl reached the FAA on 2026-10-19, so its 12:17 UTC run on 2026-10-29 (08:17 EDT) will likely download a snapshot dated the eve and lock from it, since `lock_due` accepts a same-day snapshot at any hour. That is the rule as preregistered, so it stays. On the eve the Mac runs nothing from 08:00 to 08:45 ET, and at 08:45 ET I check `gh release view lock-2026Q3` and `_lock.json` on origin. No scheduled run has happened yet (the first is due 2026-10-20 00:17 UTC); I check that one appears before counting on the runner.
- **One Mac trigger on the eve (OPS-2, OPS-5).** `tools/eve_waiter.sh 2026Q3 2026-10-29` runs `make daily-core` every 10 minutes from 19:05 ET until `_lock.json` is on origin/main, up to 23:30 ET, and logs each exit code. A refused run (dirty tree, failed `gh` call) is retried rather than lost. `daily.run` also takes a file lock, so two Mac runs cannot overlap.
- **Late locks (S1, OPS-4).** A real run re-reads the wall clock before it writes the prediction and again before `gh release create`, and refuses within 10 minutes of 00:00 ET on the release date. The prediction's `made_utc` is the time it is computed.
- **Owner step after going public (OPS-8).** A push from the runner's `GITHUB_TOKEN` starts no other workflow, so `pages.yml` will not redeploy after a runner lock or score. After making the repository public, run `gh workflow run pages` once after the lock and once after the score. `pages.yml` stays word for word.
- **Subset row selection (S5).** `faa._keep` selects rows with `csv` alone, as the gate's own `subset_lines` does. §3.3's comma-position fallback governs reading fields (`read_table`). The selecting field comes before every free-text field (`CODE` is ACFTREF's first, `MFR MDL CODE` the third in MASTER and DEREG), so a comma inside a name cannot move it. The one line in the 2026-10-19 zip where the two splits differ is out of scope either way. `faa.lossless()` now runs in `ingest` and `make data` and warns when a zip is not strict UTF-8, the only case where the stored subset would differ from the zip's bytes.
- **Gzip header (S6), accepted deviation.** Stored subsets follow §3.3's `gzip.compress(data, mtime=0)` except that the header's OS byte is 255, so the Mac and the runner write the same bytes for the lock-window subsets they may both store. The manifest hashes the bytes written, and the gate reads decompressed content (`jetgate.py:328`). The backtest subset keeps its original bytes (OS byte 0x13).
- **Offline rebuilds (S4).** `make data --offline`, and so `make all`, reads the tracked backtest subset. A networked `make data` re-stores it only when the raw zip's sha256 equals the manifest's.
- **The score (S7).** The job looks for the quarter's results 8-K once its fiscal end has passed, by §3.2's rule, and no longer waits for a calendar release date; an 8-K with no delivery table is logged and left unscored.

## Review round 2

- Two fresh reviewers, neither with a blocking or major finding, so the review ends after round 2 as §7's stop rule says, and no round 3 runs. The final `make all`, `make check-determinism` and full gate stand in for the refuter's questions; see `docs/build/REVIEW.md`.
- Round 2's minor findings were fixed where they were real defects (the broken mutation pass, a wrong as-of sentence, untested `daily.run` paths, exit codes). R2D-8 stays open because the gate's N1 rejects the Marine figures it needs.
- Final checks at b0927cc: `make all` exit 0 with no tracked file changed; `make check-determinism` identical (28 files); full gate 42 assertions, 0 failing, warnings S3 and L3. Fresh clone of origin in `/tmp/gdn-fresh`: `make all` clean, `make test` 104 passed and 2 skipped, gate on every family but `repo` 40 assertions, 0 failing, warnings F2, S3 and L3.

## Owner steps handed to me (2026-10-19)

The owner asked me to carry out §7's owner steps without making anything public.
- **Scheduled tasks replace the eve waiter.** A daily task runs `make daily` at 06:43 ET until 2026Q3 is scored. Its eve run takes a snapshot dated the eve and so may itself lock before 07:15 ET, ahead of the runner's 08:17 ET run; one lock per quarter holds either way. A task at 08:47 ET checks the lock; four tasks from 19:07 to 23:17 ET run `make daily-core` unless the lock is on origin; a task at 10:47 ET on 2026-10-30 scores; a task on 2026-11-04 adds GD's 2026Q4 release date if GD stated it. `tools/eve_waiter.sh` stays as a manual fallback. The session-only morning cron job was cancelled.
- **Not done, by the owner's instruction:** posting the sha256 publicly, making the repository public, enabling Pages and posting the LinkedIn text. `config/calendar.json` keeps `"public": false`, so the lock stays a timestamped release on a private repository: GitHub records its `published_at`, but no outsider can check it until the owner publishes.
- **The workbook in Excel:** opened in Microsoft Excel and closed without saving. Excel calculates Live!B11 = 31.13, the band 20.41 to 36.42, and Summary design and held-out MAE 5.47 and 5.52, matching the build; the file's bytes did not change.

