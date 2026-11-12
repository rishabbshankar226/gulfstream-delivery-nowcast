# Pre-publication audit: plan and status

Spec: `~/Desktop/prompt library/gulfstream-prepub-audit/GULFSTREAM_PREPUB_PROMPT.md`, Part B.
Branch: `prepub-audit`, cut from `origin/main` at `36fed31` on 2026-11-11.

## Clock (ET)

| Phase | Start | End | Budget | Note |
|---|---|---|---|---|
| P0 | 2026-11-11 18:44 | 19:02 | 45 min | on budget |
| P1 | 2026-11-11 19:02 | 19:32 | 2 h | P1.3 mapping finished with P4.6 |
| P2 to P4 | 2026-11-11 19:03 (subagents launched) | | 3 h | run behind P1 per D2 |
| P5 | | | 2 h | |
| P6 | | | 2 h | |
| P7 | | | 1 h | |
| P8 | | | 2.5 h | |

## Items

| ID | Item | Status | Done test |
|---|---|---|---|
| P0.1 | Branch and record hashes | done | `git status -sb` = prepub-audit, HEAD = origin/main = 36fed31, `RECORD_HASHES.txt` has 61 lines |
| P0.2 | New CLAUDE.md | done | `head -5 CLAUDE.md` names the spec path; v1 kept at `.build/CLAUDE_v1.md` |
| P0.3 | Baseline: tests, gate, make all, determinism | done | `BASELINE.md`: tests 6 failed 114 passed; gate 42 assertions 1 failing 2 warning; make all changed one chart; determinism identical |
| P0.4 | SURFACE.md | done | `SURFACE.md` has a row per §3 file, the `public` readers and the rounding rules |
| P1.0 | Tools venv | done | `~/gdn-prepub/venv` imports pypdf, openpyxl, formulas (pip exit 0) |
| P1.1 | ledger.py | done | `tools/prepub/ledger.py` writes `LEDGER.csv` (2405 rows) |
| P1.2 | Nine plants | done | `LEDGER_SELFTEST.md`: 9 caught, 0 missed; clean copy 0 mismatch, 0 untraced on post and README |
| P1.3 | Ledger on real tree | in progress | 25 flagged rows on the real tree, each mapped to F002, F006 to F010 in `FINDINGS.md` |
| P2.1 | Recompute subagent | running (subagent) | |
| P2.2 | Recompute diff | todo | |
| P2.3 | Lock check | todo | |
| P3.1 | Deliveries vs exhibits | running (subagent) | |
| P3.2 | Guidance vs transcripts | running (subagent) | |
| P3.3 | Claims vs filings | running (subagent) | |
| P3.4 | Links | todo | |
| P3.5 | Exposure scan | todo | |
| P4.1 | Sell-side reviewer | running (subagent) | |
| P4.2 | Buy-side reviewer | report in | `docs/prepub/reviews/buyside.md` written; NO-GO; S1 6, S2 13, S3 8; to verify in P4.6 |
| P4.3 | Statistician | running (subagent) | |
| P4.4 | Registry engineer | running (subagent) | |
| P4.5 | Compliance reviewer | running (subagent) | |
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

Subagents launched 2026-11-11 19:03 ET (briefs in `docs/prepub/briefs/`, outputs in `docs/prepub/reviews/`):

- `recompute` (P2.1): running
- `sellside` (P4.1): running
- `buyside` (P4.2): finished 19:22 ET
- `statistician` (P4.3): running
- `registry` (P4.4): running
- `compliance` (P4.5): running
- `sources_deliveries` (P3.1): running
- `sources_guidance` (P3.2): running
- `sources_claims` (P3.3): running

No background shell command is running.

## Cut items

(none)
