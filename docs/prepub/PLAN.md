# Pre-publication audit: plan and status

Spec: `~/Desktop/prompt library/gulfstream-prepub-audit/GULFSTREAM_PREPUB_PROMPT.md`, Part B.
Branch: `prepub-audit`, cut from `origin/main` at `36fed31` on 2026-11-11.

## Clock (ET)

| Phase | Start | End | Budget | Note |
|---|---|---|---|---|
| P0 | 2026-11-11 18:44 | | 45 min | |
| P1 | | | 2 h | |
| P2 to P4 | | | 3 h | |
| P5 | | | 2 h | |
| P6 | | | 2 h | |
| P7 | | | 1 h | |
| P8 | | | 2.5 h | |

## Items

| ID | Item | Status | Done test |
|---|---|---|---|
| P0.1 | Branch and record hashes | done | `git status -sb` = prepub-audit, HEAD = origin/main = 36fed31, `RECORD_HASHES.txt` has 61 lines |
| P0.2 | New CLAUDE.md | done | `head -5 CLAUDE.md` names the spec path; v1 kept at `.build/CLAUDE_v1.md` |
| P0.3 | Baseline: tests, gate, make all, determinism | todo | |
| P0.4 | SURFACE.md | todo | |
| P1.0 | Tools venv | todo | |
| P1.1 | ledger.py | todo | |
| P1.2 | Nine plants | todo | |
| P1.3 | Ledger on real tree | todo | |
| P2.1 | Recompute subagent | todo | |
| P2.2 | Recompute diff | todo | |
| P2.3 | Lock check | todo | |
| P3.1 | Deliveries vs exhibits | todo | |
| P3.2 | Guidance vs transcripts | todo | |
| P3.3 | Claims vs filings | todo | |
| P3.4 | Links | todo | |
| P3.5 | Exposure scan | todo | |
| P4.1 | Sell-side reviewer | todo | |
| P4.2 | Buy-side reviewer | todo | |
| P4.3 | Statistician | todo | |
| P4.4 | Registry engineer | todo | |
| P4.5 | Compliance reviewer | todo | |
| P4.6 | Merge reviews into FINDINGS | todo | |
| P4.7 | Finance checks | todo | |
| P5.1 | Codex branch review | todo | |
| P5.2 | Lock, score, post-score paths | todo | |
| P5.3 | Data and model paths | todo | |
| P5.4 | T9 direct tests (may be cut) | todo | |
| P5.5 | After-state tests, gate, determinism | todo | |
| P6.1 | Fix S1 and S2 | todo | |
| P6.2 | L1 and L2 by hand | todo | |
| P6.3 | S3 under 15 min | todo | |
| P6.4 | Rebuild, ledger, tests, gate | todo | |
| P7.1 | Post rewrite in generator | todo | |
| P7.2 | Two alternates | todo | |
| P7.3 | Post check | todo | |
| P8.1 | Round 2 (three fresh reviewers) | todo | |
| P8.2 | Round 3 (one attacker) | todo | |
| P8.3 | Fix rounds 2 and 3 | todo | |
| P8.4 | Fresh clone check | todo | |
| P8.5 | Merge check | todo | |
| P8.6 | Hash recheck and VERDICT.md | todo | |
| P8.7 | GO_PUBLIC.md | todo | |
| Finish | OUTCOME_SELF.md and final message | todo | |

## Running

(none)

## Cut items

(none)
