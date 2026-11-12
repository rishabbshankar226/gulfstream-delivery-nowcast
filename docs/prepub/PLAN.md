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
| P8 | 20:48 (round 2 launched) | | 2.5 h | |

## Items

| ID | Item | Status | Done test |
|---|---|---|---|
| P0.1 | Branch and record hashes | done | `prepub-audit` cut from `origin/main` `36fed31`; `RECORD_HASHES.txt` has 61 lines |
| P0.2 | New CLAUDE.md | done | `head -5 CLAUDE.md` names the spec path |
| P0.3 | Baseline | done | `BASELINE.md`, Before |
| P0.4 | SURFACE.md | done | a row per §3 file, the `public` readers, the rounding rules |
| P1.0 | Tools venv | done | imports pypdf, openpyxl, formulas |
| P1.1 | ledger.py | done | `LEDGER.csv`, 2,800 rows on the final tree |
| P1.2 | Nine plants | done | `LEDGER_SELFTEST.md`: 9 caught, 0 missed; rerun on the final tree, 9 caught |
| P1.3 | Ledger on real tree | done | 25 flagged rows mapped in `FINDINGS.md` section 3; final ledger 0 flagged |
| P2.1 | Recompute subagent | done | `reviews/recompute.txt` |
| P2.2 | Recompute diff | done | `RECOMPUTE_DIFF.md`: 547 figures, 547 match |
| P2.3 | Lock check | done | `LOCK_CHECK.md`: all checks pass |
| P3.1 | Deliveries vs exhibits | done | `SOURCES_DELIVERIES.csv`: 43 verified |
| P3.2 | Guidance vs transcripts | done | `SOURCES_GUIDANCE.csv`: 24 verified, 3 verified elsewhere, 1 call not in the file (F054) |
| P3.3 | Claims vs filings | done | `SOURCES_CLAIMS.csv`: 227 rows, 204 verified, 23 with a closed finding |
| P3.4 | Links | done | `LINKS.csv`: 187 links on the final tree |
| P3.5 | Exposure scan | done | `EXPOSURE.md`; F015 and F016 open for the owner |
| P4.1 to P4.5 | Five reviewers | done | five files under `reviews/` |
| P4.6 | Merge reviews into FINDINGS | done | `FINDINGS.md` section 2: every reviewer finding has a status |
| P4.7 | Finance checks | done | `FINANCE_CHECKS.md` |
| P5.1 | Codex branch review | done | DECISIONS D5; merged in `e778e23` |
| P5.2 | Lock, score, post-score paths | done | `DEFECT_TRACE.md`; F017, F018 |
| P5.3 | Data and model paths | done | `DEFECT_TRACE.md` |
| P5.4 | T9 direct tests | done | `tests/test_daily.py` (the `run` fixture) and `tests/test_model_direct.py` (6 tests pass); DECISIONS D15 |
| P5.5 | After-state tests, gate, determinism | done | `BASELINE.md`, After |
| P6.1 | Fix S1 and S2 | done | `FINDINGS.md`; open rows are the owner's (F015, F016, F081) |
| P6.2 | L1 and L2 by hand | done | F006, F007 |
| P6.3 | S3 under 15 min | done | the rest open with reasons |
| P6.4 | Rebuild, ledger, tests, gate | done | ledger 0 flagged; 170 tests pass; gate 4 failing, logged in D10 |
| P7.1 | Post rewrite in generator | done | `src/gdn/report.py` (`post`), 1,284 characters |
| P7.2 | Two alternates | done | `POST_ALTERNATES.md` |
| P7.3 | Post check | done | `POST_CHECK.md` |
| P8.1 | Round 2 (three fresh reviewers) | done | `reviews/round2_*.md`: three NO-GO, 4 S1 in all, every one a sentence; fixed in `a354170` (F083 to F098) |
| P8.2 | Round 3 (one attacker) | running | launched 21:32 ET |
| P8.3 | Fix rounds 2 and 3 | todo | |
| P8.4 | Fresh clone check | todo | |
| P8.5 | Merge check | todo | |
| P8.6 | Hash recheck and VERDICT.md | todo | |
| P8.7 | GO_PUBLIC.md | todo | |
| Finish | OUTCOME_SELF.md and final message | todo | |

## Running

- `round3` (P8.2): launched 21:32 ET, brief `docs/prepub/briefs/round3_attacker.md`, output `docs/prepub/reviews/round3.md`.
- Background shell: the fresh clone battery in `~/gdn-prepub/clone2` (log `.build/logs/clone_check2.log`).

## Cut items

(none)

## Overruns

- P2 to P4 ran to 20:35, inside the 3 hour budget. No phase is over budget so far.
