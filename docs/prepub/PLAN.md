# Pre-publication audit: plan and status

Spec: `~/Desktop/prompt library/gulfstream-prepub-audit/GULFSTREAM_PREPUB_PROMPT.md`, Part B.
Branch: `prepub-audit`, cut from `origin/main` at `36fed31` on 2026-11-11.

## Clock (ET)

| Phase | Start | End | Budget | Note |
|---|---|---|---|---|
| P0 | 2026-11-11 18:44 | 19:02 | 45 min | on budget |
| P1 | 19:02 | 19:32 | 2 h | P1.3 mapping finished with P4.6 |
| P2 to P4 | 19:03 (subagents launched) | 20:35 (last reviewer in) | 3 h | reviewers ran behind P1 (D2) |
| P5 | with P2 to P4 | 20:13 | 2 h | codex review, defect trace, four code fixes in a scratch clone (D5) |
| P6 | 19:40 | 21:05 | 2 h | fix pass, merged in `e778e23`; registry and sell-side fixes after their reports |
| P7 | with P6 | 21:10 | 1 h | post rewritten in its generator; alternates and check |
| P8 | 20:48 (round 2 launched) | 22:13, then 2026-11-12 09:23 to 09:53 ET | 2.5 h | rounds 2 and 3, two fix rounds, fresh clone, final battery; after an overnight pause, the merge of the workflow's new commits and the battery again |

## Items

| ID | Item | Status | Done test |
|---|---|---|---|
| P0.1 | Branch and record hashes | done | `prepub-audit` cut from `origin/main` `36fed31`; `RECORD_HASHES.txt` has 61 lines |
| P0.2 | New AGENT.md | done | `head -5 AGENT.md` names the spec path |
| P0.3 | Baseline | done | `BASELINE.md`, Before |
| P0.4 | SURFACE.md | done | a row per §3 file, the `public` readers, the rounding rules |
| P1.0 | Tools venv | done | imports pypdf, openpyxl, formulas |
| P1.1 | ledger.py | done | `LEDGER.csv`, 2,864 rows on the final tree |
| P1.2 | Nine plants | done | `LEDGER_SELFTEST.md`: 9 caught, 0 missed; rerun on the final tree, 9 caught |
| P1.3 | Ledger on real tree | done | 25 flagged rows mapped in `FINDINGS.md` section 3; final ledger 0 flagged |
| P2.1 | Recompute subagent | done | `reviews/recompute.txt` |
| P2.2 | Recompute diff | done | `RECOMPUTE_DIFF.md`: 547 figures, 547 match |
| P2.3 | Lock check | done | `LOCK_CHECK.md`: all checks pass |
| P3.1 | Deliveries vs exhibits | done | `SOURCES_DELIVERIES.csv`: 43 verified |
| P3.2 | Guidance vs transcripts | done | `SOURCES_GUIDANCE.csv`: 24 verified, 3 verified elsewhere, and the one missing call added (F054) |
| P3.3 | Claims vs filings | done | `SOURCES_CLAIMS.csv`: 227 rows, 204 verified, 23 with a closed finding |
| P3.4 | Links | done | `LINKS.csv`: 191 links on the final tree |
| P3.5 | Exposure scan | done | `EXPOSURE.md`; F015 and F016 open for the owner |
| P4.1 to P4.5 | Five reviewers | done | five files under `reviews/` |
| P4.6 | Merge reviews into FINDINGS | done | `FINDINGS.md` section 2: every reviewer finding has a status |
| P4.7 | Finance checks | done | `FINANCE_CHECKS.md` |
| P5.1 | Codex branch review | done | DECISIONS D5; merged in `e778e23` |
| P5.2 | Lock, score, post-score paths | done | `DEFECT_TRACE.md`; F017, F018 |
| P5.3 | Data and model paths | done | `DEFECT_TRACE.md` |
| P5.4 | T9 direct tests | done | `tests/test_daily.py` (the `run` fixture) and `tests/test_model_direct.py` (6 tests pass); DECISIONS D15 |
| P5.5 | After-state tests, gate, determinism | done | `BASELINE.md`, After |
| P6.1 | Fix S1 and S2 | done | `FINDINGS.md` section 4; the three open S1 and S2 rows are the owner's (F015, F016, F081) |
| P6.2 | L1 and L2 by hand | done | F006, F007 |
| P6.3 | S3 under 15 min | done | the rest open with reasons |
| P6.4 | Rebuild, ledger, tests, gate | done | `rows 2864  flagged 0`; `178 passed`; gate 4 failing, logged in D10 and D18 |
| P7.1 | Post rewrite in generator | done | `src/gdn/report.py` (`post`), 1,284 characters |
| P7.2 | Two alternates | done | `POST_ALTERNATES.md` |
| P7.3 | Post check | done | `POST_CHECK.md` |
| P8.1 | Round 2 (three fresh reviewers) | done | `reviews/round2_*.md`: three NO-GO, 4 S1 in all, every one a sentence; fixed in `a354170` (F083 to F098) |
| P8.2 | Round 3 (one attacker) | done | `reviews/round3.md`: S1 0, S2 4, S3 6 |
| P8.3 | Fix rounds 2 and 3 | done | two fix rounds: `a354170` (round 2), `4ad3825` (round 3); no review round was repeated, since round 3 found no S1. One more code fix followed the advisor's last check (F108, `1e9a890`), and the whole battery was run again after it, again after the merge, and again after the continue pass (D21) |
| P8.4 | Fresh clone check | done | `BASELINE.md`, Fresh clone: builds, `178 passed`, deterministic, empty status after `make all` |
| P8.5 | Merge check | done | the workflow's 2026-11-12 commits merged with a real merge commit, `bbf88fd`; `git log prepub-audit..origin/main` is empty; P6.4 rerun after it |
| P8.6 | Hash recheck and VERDICT.md | done | 59 of 61 hashes match, the two others explained by the merge (D20); `VERDICT.md`: NO-GO on criteria 1, 2 and 12 |
| P8.7 | GO_PUBLIC.md | done | five decisions and ten steps, each with its check, and the post's text |
| Finish | OUTCOME_SELF.md and final message | done | `OUTCOME_SELF.md` in the project root, not tracked |

## Round 4: eleven auditors (DECISIONS D23)

Started 2026-11-12 13:59 ET on the frozen commit `4388294`. Audit only.

| ID | Item | Status | Done test |
|---|---|---|---|
| R4.0 | Freeze and battery | done | `BASELINE.md`, Round 4 |
| R4.1 | Briefs | done | `briefs/round4_common.md` and 11 role briefs |
| R4.2 | Cold copy, data-only copy, clones, leak check | done | each tree exists; push URL disabled on the three git trees |
| R4.3 | Eleven auditors | done | 11 files `reviews/round4_*.md`, each with a verdict and counts |
| R4.4 | Dashboard in a browser (main session) | done | desktop and 375 px checked, console read |
| R4.5 | Verify and consolidate | done | `FINDINGS.md` Round 4 section, F109 onward; every S1 and S2 cites a command |
| R4.6 | Verdict and improvements | done | `ROUND4_VERDICT.md`; gate rerun after the last commit |
| R4.7 | Fix pass, lists B and C of `ROUND4_VERDICT.md` | done | F109, F112 to F128 fixed; F110, F111 fixed at the tip; F129 runbook step written (`FINDINGS.md` 5.6) |
| R4.8 | Battery after the fix pass | done | `BASELINE.md`, Round 4 fix pass: 197 passed, ledger 0 flagged, 9 of 9 plants, 36 of 36 revert pairs, gate 4 failing as D18 |
| R4.9 | Cold read of the changed first screens | done | `reviews/round4_coldread.md` |
| R4.10 | Verdict after the fix pass | done | `ROUND4_VERDICT.md`, top section |

## Running

Nothing is running. All eleven auditors reported between about 14:25 and 14:40 ET; their reports are committed in `1030d7a`. The verdict is `ROUND4_VERDICT.md`: NO-GO.

Fix pass: one cold reader (`coldread`) ran from about 20:50 ET on the tree at `b128144` and reported GO with one S2 (F130, fixed). Nothing is running now.

## Cut items

(none)

## Overruns

- No phase ran over its budget. The run worked from 18:44 to 22:13 ET on 2026-11-11, sat idle overnight, and worked again on 2026-11-12 from 09:23 ET for the merge and the last battery (DECISIONS D19).
