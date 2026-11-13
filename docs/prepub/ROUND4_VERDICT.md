# Round 4 verdict: eleven auditors

## After the fix pass (2026-11-12, at `2393a18`)

**Still NO-GO, and every item left is the owner's.** The fix pass closed everything the audit could close.

- The two new blocking findings that sat in code and text are fixed: the note's XBRL sentence (F109) and the late-lock guard that failed open (F124).
- Seventeen of the eighteen new S2 findings are fixed. That includes the cold read's one finding (F130) and all seven first-screen findings: F113 to F117, F123 and F130.
- The private name and the home paths are gone from the tracked files (F110, F111). They remain in history.

What stops the post now is only what the owner must decide or do:

1. **Decision A**, the email address on 62 commits of `main` (F015, F112).
2. **Decision B**, the home paths in the 16 build briefs and in history (F016, F111).
3. **The private name in the branch history** (F110, A.3 below): a local squash merge, with `origin/prepub-audit` deleted before the flip, keeps it off `main`.
4. **`GO_PUBLIC.md` step 1**, dating the position statement (F081).

After those, `GO_PUBLIC.md` steps 2 to 8 make the repository public. The new step 4b protects the record on GitHub (F129).

| # | Criterion | Holds | Measurement at `2393a18` (`BASELINE.md`, Round 4 final) |
|---|---|---|---|
| 1 | Zero open S1 | **no** | F015 and F016, and the history half of F110 and F111. All four are the owner's. F109 and F124 are fixed. |
| 2 | Zero open S2 on the five first screens | **no** | F081 only, which is the owner's. F113 to F117, F123 and F130 are fixed. |
| 3 | Ledger clean after its plants | yes | `rows 2923  flagged 0`; 9 of 9 plants caught at `2393a18`. |
| 4 | Recompute matches | yes | Round 4's blind recompute matched every headline figure. The fix pass computed no new figure; it showed existing ones in more places, each traced by the ledger. The cold read matched every figure it checked. |
| 5 | Lock checks pass | yes | As in the round 4 table below. |
| 6 | Post links resolve after a named step | yes | Unchanged. |
| 7 | Tests, gate and determinism on a fresh clone | yes, with logged gate failures | Fresh clone without `data/raw/`: `196 passed, 2 skipped`. Main tree: `198 passed`, `identical (50 files)`, `make all` leaves the tree clean. Gate: `42 assertions, 4 failing`, the same IDs as D18 (D24). |
| 8 | Interview notes and resume state the scored record | yes | The ledger traces both files with 0 flagged. |
| 9 | Round 3 found no S1 | yes, superseded | Of round 4's four new S1, two are fixed. The other two are fixed at the tip and wait on the owner for history. |
| 10 | Source rows verified or closed | yes | `SOURCES_CLAIMS.csv:55` now carries F109, fixed, in place of F043's wrong refutation. |
| 11 | Record hashes match | yes by D3, **no** literally | 59 of 61, as in D20. The protected-path diff from `4388294` is empty. |
| 12 | P3.5 found nothing open | **no** | F015, F016, and the history half of F110 and F111. |
| 13 | Every required item finished | yes | `PLAN.md`, R4.0 to R4.10. |

**What the fix pass changed on the public surfaces:**

- **The post.** The band's coverage is beside the band, and the pace is called mine. It is 1,282 characters.
- **The README.** The first screen calls the pace mine. The hero image draws the lock with its band. The coverage sentence names its unit. The guard sentence counts four guards.
- **The dashboard.**
  - The lead, the live card and the legends call the pace mine.
  - The live card gives the band's coverage.
  - A phone keeps the baseline that won.
  - The scope sentence no longer says "every jet".
- **The note.**
  - The XBRL sentence is corrected.
  - The first page glosses the preregistered sentence and says where the edge comes from.
  - The key point and the locked-quarter paragraph give the band's coverage.
  - GD's own "third quarter among the highest" and the 40.5 even split sit beside the scored pace.
  - The after-the-fact readings are labelled, with the combined reading.
  - "Every Gulfstream jet" is gone, and a scope and holder limitation is added.
  - The risks carry the mid-cabin supplier delay from GD's 10-Q.
- **The workbook.** The Summary no longer says "beat", and the Live sheet gives the band's coverage.
- **The owner's material.** The interview notes and resume bullets carry the coverage and qualify "held-out".
- **Behind the surfaces.**
  - The score step refuses a locked quarter when the SEC gives no acceptance time (ERRATA E9 is amended).
  - Tests no longer pin today's live state.
  - New tests cover the neither-date bound and the old-airframe counts.
  - `docs/prepub/` has an index.
  - The runbook protects the record and cleans up branches.

**Still open at S3, and not blocking:** the round 4 S3 rows in `FINDINGS.md` 5.4 and 5.7 that the fix pass did not touch.

**Who has read the fixed tree:** one cold reader (`reviews/round4_coldread.md`) read the changed first screens and said GO. Its one S2 is fixed (F130). Nobody has read the F130 fix itself except through its test, the ledger and this battery.

---

The rest of this file is the verdict as round 4 wrote it, before the fix pass.

**NO-GO.** Five of the spec's 13 criteria fail (1, 2, 10, 11 literally, 12). Round 4 found four new S1 findings:

- a false sentence in the note about GD's filings (F109);
- two items of personal data that the earlier audit missed or counted short (F110, F111);
- a guard on the score path that fails open (F124).

It also found six new S2 findings on first screens that the earlier verdict called clean. No figure is wrong: a blind recompute matched every headline number on all seven surfaces. What blocks posting is framing, disclosure and exposure, and most of it can be fixed in one fix pass. The rest are decisions only the owner can make.

Written 2026-11-12, after a round 4 audit of the frozen commit `4388294` (DECISIONS D23). Round 4 was an audit only: it changed no public surface. The measurements below were printed by commands run after the last commit that could change them. The battery is in `BASELINE.md`, section Round 4. The findings are in `FINDINGS.md`, section 5.

## The 13 criteria, re-measured

| # | Criterion | Holds | Measurement |
|---|---|---|---|
| 1 | Zero open S1 | **no** | Six open: F015 and F016 (owner decisions A and B), plus four new ones. F109 is the note's XBRL sentence, which SEC's `companyconcept` data contradicts. F110 is the owner's private name in `DECISIONS.md:36` and in branch history from `aa273cb`. F111 is home paths at the tip, in two of the audit's own files and one build note. F124 is the late-lock guard in `live.py:468`, which is skipped when SEC gives no acceptance time. |
| 2 | Zero open S2 on the five first screens | **no** | Seven distinct findings open, six of them new. On the post: F113 (the band named without its 18 of 26 coverage). On the dashboard's first screen: F114 ("GD's guidance pace" with no sign it is my construction). On the note's first page: F114, F115 (GD's own "Q3 and Q4 highest" statement and the 40.5 even split are absent), F116 (the 5.5 against 6.9 edge comes from 2023 and 2024, unsaid) and F081. On the README's first screen: F117 (the hero image, also the post's link card, stops at 2026Q2 and leaves out the live quarter) and F081. On the workbook's Summary sheet: F123 ("beat"). |
| 3 | Ledger: zero `mismatch`, `untraced`, `stale` after its plants | yes | `rows 2864  flagged 0`, byte-identical to the committed `LEDGER.csv`. The nine plants were not rerun this round; the public surfaces have not changed since they last passed. The ledger checks numbers against labels. It cannot see the round 4 findings, which are omissions and framing. |
| 4 | Recompute matches at displayed precision | yes | Round 4's blind recompute (`reviews/round4_recompute.md`) matched every headline figure on all seven surfaces. It covered 615 `data.json` values and 414 workbook values, and gave the design averages to every digit (E1 5.472548294344893, E2 5.5807858422376135). |
| 5 | Lock checks pass | yes | `gh release view lock-2026Q3` prints `publishedAt` 2026-10-29T05:51:24Z, and its notes hold `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`. That equals `shasum -a 256 predictions/2026Q3.json`. The tag points at `a44e5ac`. SEC's submissions data, refetched this round, gives GD's 8-K `0000040533-26-000036` an `acceptanceDateTime` of 2026-10-30T12:09:27Z (08:09:27 ET), 30 hours after the lock. |
| 6 | Post links resolve, or will after a named step | yes | No change since `POST_CHECK.md`. Both links return 404 until `GO_PUBLIC.md` steps 4 and 5. |
| 7 | Tests, gate and determinism on a fresh clone | yes, with logged gate failures | Checked in two places. In the `code` auditor's fresh clone, with no `data/raw/`: `make all` then `git status --short` printed nothing, `make test` printed `176 passed, 2 skipped`, and `make check-determinism` printed `identical (50 files)`. On the owner's checkout: `make test` printed `178 passed`. The gate printed `42 assertions, 4 failing, 3 warning`; the failures are `R2`, `K1`, `N1` and `Y1`, the same as in D18, and were logged under R11. |
| 8 | Interview notes and resume bullets state the scored record | yes | The recompute matched their figures. F120 (an unqualified "held-out" in a bullet) is a framing finding; no figure differs. |
| 9 | Round 3 found no S1 | yes, but superseded | Round 3 found none. Round 4 found four new S1, all verified, so the record behind this criterion no longer reads clean. |
| 10 | Every source row verified or carrying a closed finding | **no** | `SOURCES_CLAIMS.csv:55`, the XBRL sentence, reads "not checked" and was closed by F043 as "refuted: matches the study's README". The filings contradict the sentence (F109). The closing ID is a wrong refutation, and the row now carries an open S1. |
| 11 | Every hash in `RECORD_HASHES.txt` matches | yes by D3's reading, **no** literally | `shasum -c` gives 59 of 61. The two that miss are `results/live/2026Q4_latest.json` and `results/live/2026Q4_path.csv`, the open quarter's working files, as in D20. `git diff --stat 4388294..HEAD` on every protected path prints nothing. |
| 12 | P3.5 found nothing open | **no** | F015 and F016, plus F110 and F111. |
| 13 | Every required item finished | yes | Every spec item in `PLAN.md`, and every round 4 item, is done. |

## The eleven auditors

| Auditor | Tree | Own verdict | Reported S1 / S2 / S3 | Verified S1 and S2 in the register |
|---|---|---|---|---|
| `hiring` | cold | NO-GO | 1 / 3 / 9 | F016 (known), F113, F119, F120 |
| `sellside` | cold | NO-GO | 1 / 4 / 3 | F109, F115, F116, F122, F119 |
| `stats` | cold | GO | 0 / 3 / 7 | F113, F116, F123 |
| `registry` | cold | GO | 0 / 1 / 5 | F125 |
| `editor` | cold | NO-GO | 1 / 5 / 11 | F016 (known), F113, F114, F121; two regraded to S3 |
| `compliance` | cold | NO-GO | 1 / 6 / 6 | F016, F081, F070 and E1 (known), F113, F120; one regraded to S3 |
| `recompute` | data only, then cold | GO | 0 / 1 / 1 | F113 |
| `rendered` | cold | NO-GO | 0 / 3 / 10 | F114, F117, F118 |
| `code` | own clone | GO | 0 / 6 / 6 | E1, E2, E4 (known), F126, F127; one regraded to S3 |
| `exposure` | mirror and tracked files | NO-GO | 2 / 4 / 7 | F110, F111, F112, F128, F129, F015 (known) |
| `attacker` | own clone and audit notes | NO-GO | 0 / 3 / 5 | F112, F114, F124 |

Seven said NO-GO and four said GO. The four GO verdicts came from the auditors who check numbers and code paths (`stats`, `registry`, `recompute`, `code`), and none of them found a wrong figure. The NO-GO verdicts rest on framing, disclosure and exposure.

## Improvements, ranked

### A. Only the owner can do these

1. **Decision A, the email address (F015, F112).** It is on 62 commits of `main`, 58 of them under the lock commit. At `e9095ce`, `prepub-audit` holds 62 more, the four round 4 commits among them. A normal merge would put 124 on `main`; a squash merge adds 1. Rewriting history is not an option: it changes the lock commit's hash. Either accept the exposure or keep the repository private.
2. **Decision B, the home paths (F016, F111).** The same choice for history. At the tip, the fix pass can replace them with `~`.
3. **The private name in history (F110).** It entered in `aa273cb`, which is not under the lock. A normal merge publishes it. A local `git merge --squash`, with `origin/prepub-audit` deleted before the repository goes public, keeps it off `main`'s history. That is not a full removal. GitHub's "Removing sensitive data from a repository" says commits can stay "accessible" by SHA in cached views until GitHub Support removes them, and pull-request refs keep them too, so do not merge through a pull request. The cost: the fix commits that the audit's records cite would not be on `main`, so a reader could not open them.
4. **Step 1, the position line (F081).** Date it. Decide whether the post carries a short form; the post is at 1,281 of its 1,300-character cap.
5. **Protect the record on GitHub (F129).** After going public, add a ruleset on `lock-*` tags (no update, no deletion) and branch protection on `main` (no force-push, no deletion). Before 2026Q4, turn on immutable releases. Never edit or republish `lock-2026Q3`.
6. **Pages redeploy (E1).** This needs a `.github/` edit, so the dashboard can redeploy after the workflow's own commits. Until then, the dashboard goes stale the day after its first deploy (CODE-1).
7. **The next lock (E4, step 10).** Add GD's 2026Q4 release date as soon as GD announces it, and 2027Q1's fiscal end. Without them, no lock fires, and the README and dashboard will say the quarter "missed its lock window".
8. **Decisions C, D and E** as in `GO_PUBLIC.md`. C, the G700 type code, is due before 2026-12-31.

### B. Must fix before posting (fixable in one fix pass)

Each code change follows R4 and R6: fix the generator, rebuild, run `make claims` and `make pdf`, check the stamp, and add a test that fails when the fix is reverted.

| Finding | What to change | Where | Rough effort |
|---|---|---|---|
| F109 (S1) | Correct the XBRL sentence; keep "because" only if the owner confirms the study's source | `src/gdn/note.py` | 15 min plus rebuild |
| F110, F111 (S1, tip) | Remove the private name from D8. Replace home prefixes with `~` in the two audit files and `docs/build/DECISIONS.md:32`. Correct `EXPOSURE.md:11` | `docs/prepub/`, `docs/build/` | 15 min |
| F113 | "which held 18 of 26 past quarters" beside the band. The post must stay under 1,300 characters, so another clause has to give | `report.py` (post), `note.py`, `site/app.js`, `workbook.py`, `INTERVIEW_NOTES.md` | 45 min |
| F114 | One name for the pace that says it is mine, on the dashboard and note page 1 ("Pace built from GD's outlook", as the PNGs say) | `site/app.js:10`, `:14`; `note.py` | 20 min |
| F115 | GD's "Q3 and Q4 highest" and the 40.5 even split, beside the scored 33.8 | `note.py`, `report.py` (post, if it fits) | 20 min |
| F116 | The 2023 and 2024 concentration, and the combined reading labelled as tried after the fact, on note page 1 | `note.py` | 20 min |
| F117 | Mark the scored lock on the track chart, or title it "Backtest, 2016Q1 to 2026Q2". The image is also the post's link card and note Exhibit 4 | `src/gdn/charts.py` | 10 min to retitle; about 1 h to draw the lock |
| F123 | Remove "beat" from the Summary sheet | `workbook.py:142` | 5 min |
| F124 (S1) | Fail closed when SEC gives no acceptance time; add a test that fails with the fix reverted (R6) | `src/gdn/live.py:468` | 30 min |
| F112 | Correct "124 commits" in five places | `GO_PUBLIC.md`, `VERDICT.md`, `FINDINGS.md`, `EXPOSURE.md` | 10 min |

### C. Should fix (S2 off the first screens)

| Finding | What to change | Where |
|---|---|---|
| F118 | On phones, keep "Same quarter last year" visible | `site/app.js:221` |
| F119 | Drop "every Gulfstream jet", and add a scope and holder limitation to the note | `note.py`, `site/index.html:100`, `INTERVIEW_NOTES.md:5` |
| F120 | Qualify "held-out" in the resume bullets | `docs/RESUME_BULLETS.md` |
| F121 | Name the unit at 0.69 to 0.72 | `README.md:156` |
| F122 | Add the mid-cabin supplier delay from GD's 10-Q to the risks | `note.py` |
| F125 | Fixture tests for the neither-date branch of the used-jet bound | `tests/test_faa.py`, fixtures |
| F126 | Pin the dashboard test to a frozen copy of `data.json`, so the 2026Q4 lock does not turn CI red | `tests/test_site_a11y.py:218-225` |
| F127 | Tests for the old-airframe counts (5 of 42, 246 of 1,251) | `tests/` |
| F128 | A one-screen `docs/prepub/README.md` that names the current verdict | `docs/prepub/` |
| F129 | The protection steps, written into the runbook | `GO_PUBLIC.md` |

Plus the runbook corrections in `FINDINGS.md` 5.4: the stale `f14a400`, the branch named in step 1, branch clean-up as an ordered step, and step 7 checking the tag rather than the working copy.

### D. Would raise the project's standing (optional, within R7 and R9)

1. **A purpose-built link card** (1200 x 630). Show the 2026Q3 lock, its band and GD's 40, with the backtest as an inset. Most readers see this image first. (`rendered`, `editor`, `attacker`.)
2. **One disclosure constant** that the post, note, workbook, dashboard and README all read. It would cover: student project, not advice, no rating, not affiliated with or endorsed by GD, Gulfstream or the FAA, and the dated position line. (`compliance`.)
3. **A "data as of" line on the dashboard's first screen**, and a red daily run when the next lock has no release date. Staleness then shows instead of hiding. (`code`.)
4. **The sign test's power beside the headline.** With 26 quarters it needs 19 wins to clear Holm, so "not distinguishable" reads as what the test could detect. (`stats`.)
5. **Split Aerospace revenue into manufacturing and services** as an exploratory figure beside the mechanical one. This is the first thing a sell-side reader would ask for. (`sellside`.)
6. **One plain-words line under the README's first screen** defining held-out quarter, the band and the sign test. (`editor`, `hiring`.)
7. **Cached values in the workbook**, so its Summary sheet shows numbers in a viewer that does not calculate. (`hiring`.)
8. **A test that reads the drawn values back from the chart PNGs** and compares them with `results/`. (`rendered`.)

### E. Not recommended

- **Rewriting history** to remove the email address or paths. It changes the lock commit's hash, and the `lock-2026Q3` release would no longer match its commit (R7).
- **Editing or republishing the `lock-2026Q3` release.** It would replace the timestamp that is the record.
- **Making the headline the even split, or GD's stated quarter plans, in place of the preregistered 33.8 pace.** They belong beside it, labelled as tried after the fact (R7).
- **Any sentence saying the registry estimate beats GD's pace or the market.** None of the sign tests separates them, and outside 2023 and 2024 the pace missed by less: 4.43 against 6.43 (R9).
- **Removing the interview notes and resume bullets from the repository to dodge HIRING-12.** That is the owner's call. Fixing F120 matters more than where the files live.

## What round 4 found about the earlier audit

- **Wrong closures.**
  - F043 refuted the XBRL sentence by matching the study's README; the filings contradict it (F109).
  - Criterion 2's measurement said the dashboard calls the pace my construction; it does so only several screens down (F114).
  - F015's 124 is author lines plus committer lines, not commits (F112).
  - `EXPOSURE.md:11` says the tree is scrubbed; it is not (F111).
  - D8 put into the record the very name it set out to keep out of public files (F110).
- **Re-checks that held.**
  - A seeded draw re-verified 10 of 10 fixed S1 and S2 rows (seed 20261112, `attacker`).
  - Every figure the audit itself added checked against its source: the D10 and D18 gate lists, the ledger's hand-typed constants, and the 2026-10-30 guidance row against its transcript.
- **The unread delta.** Every public sentence and figure changed since `4ca7d35` matches its source (`attacker`). The delta's one new framing problem is that the preview image added in F053 is the backtest-only chart (F117).

## What no command could check, and refused commands

- The defense backlog study's page and as-of date. Its URL carries the owner's handle, so no auditor fetched it (`sellside`, `attacker`).
- The FAA download page's terms, and the engine-type code of the dropped G700 row. The FAA returned 403 (`compliance`, `attacker`).
- The archived G280 certification release. WebFetch refused it (`sellside`).
- `code` was refused `gh release view lock-2026Q3` by the session's permission classifier. The main session and three other auditors ran it.
- `git log -p` on `nowcast.yml` was refused to `code`.
- Auditors used some read-only commands outside their briefs' lists, each disclosed in its report and none writing outside its scratch folder: `zcat`, `awk`, `sort`, `uniq`, `tr`, `gzip -dc`, inline Python, `git rev-list`, `git count-objects`, `git config --get` and `git grep`.
- The nine ledger plants and the 22 revert pairs were not rerun this round. No code changed since they last passed.
- **Independence.** Three auditors came near another's work, and all three disclosed it.
  - `recompute` ran `ls` on the reviews folder; it printed a count only.
  - `exposure`'s pattern scans matched other auditors' `round4_*` briefs; they printed counts and paths, and it did not open those files.
  - `stats` ran `sed -i` on its own scratch script.

  No report cites another's findings.
