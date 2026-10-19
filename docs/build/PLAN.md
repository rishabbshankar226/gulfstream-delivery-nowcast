# Plan

Backtest snapshot: 2026-10-19. Critical path (Phases 0 to 5) due 2026-10-28 18:00 ET.

| Phase | Task | State | Gate codes | Commit |
|---|---|---|---|---|
| 0 | Smoke test, preflight, .gitignore, .gitattributes | done | - |  09c16a9 |
| 0 | FAA backtest zip, project venv, gate venv, selftest | done | selftest |  09c16a9 |
| 0 | PLAN.md, DECISIONS.md, CLAUDE.md | done | - |  09c16a9 |
| 1 | Makefile, faa.py, sec.py, events.py, __main__.py | done | - | 6725184 |
| 1 | Backtest subset and manifest | done | F1 F2 | 6725184 |
| 1 | SEC releases, gd_deliveries.csv, segments.csv, backlog | done | T1 T2 S1 S3 | 6725184 |
| 1 | serials.csv, registry_quarterly.csv | done | F3 F4 | 6725184 |
| 1 | Fixture tests | done | - | 6725184 |
| 2 | coverage_design.csv and the 0.5 to 1.5 check | done | - | |
| 2 | guidance.csv from three checkers | done | T3 | |
| 2 | design.csv, chosen definition | done | M1 | |
| 2 | PREREGISTRATION.md, committed alone | todo | Q1 Q2 | |
| 3 | holdout.csv, metrics.json, tests | todo | M2 M3 | |
| 3 | error_analysis.md | todo | - | |
| 4 | calendar.json, live.py, build nowcast, path, latest, daily table | todo | L1 L2 | |
| 4 | estimates.json | todo | S2 | |
| 4 | Lock and score tests with fixed clocks, limitations notes | todo | - | |
| 5 | make daily-core / daily, workflows, LICENSE, SEC_UA secret | todo | Y4 | |
| 5 | Workflow run and watch | todo | - | |
| 5 | Lock rehearsal, REHEARSAL.md | todo | L1 to L4 | |
| 5 | Critical path ready | todo | faa truth model prereg segments live | |
| 6 | Workbook | todo | W1 to W5 | |
| 6 | Charts, VISUAL_QA rows | todo | - | |
| 6 | claims.json, test_claims.py | todo | N4 | |
| 6 | note.html and PDF | todo | N1 to N3 | |
| 7 | site_data.py, page, a11y test | todo | Y1 to Y3 | |
| 7 | Impeccable critique, audit, polish; shots | todo | site | |
| 8 | README, LINKEDIN_POST, INTERVIEW_NOTES, RESUME_BULLETS | todo | R1 to R4 K1 K2 V1 | |
| 8 | Full gate | todo | all | |
| 9 | Airframe audit | todo | - | |
| 9 | Mutation pass | todo | - | |
| 9 | check-determinism | todo | - | |
| 9 | As-of study | todo | - | |
| 10 | Fresh clone build and gate | todo | all but repo | |
| R | Review rounds 1 to 3 | todo | - | |
| R | Final gate, push, report | todo | all | |

## Tool routing

| Job | Phase | First choice | Fallback | Present |
|---|---|---|---|---|
| Charts: chart form and marks, never the palette | 6, 7 | `dataviz` | §3.10 and the backlog project's chart colours | yes |
| Dashboard critique, technical audit, final polish | 7 | Impeccable (`/impeccable critique`, `audit`, `polish`), answered from §3.10; the font and colours stay the backlog project's; never its per-edit hooks | a critic subagent with §3.10 as its rubric | yes |
| Narrow widths | 7 | `vectorlab-ux-skills` viewports | the 390 px shots | yes |
| Reading the note's PDF pages | 6 | `pdf-reading` | `sips` or `qlmanage` to PNG, then Read | no (fallback, plus Read on PDF pages) |
| Sourcing and checking claims | 6, review | `citation-integrity-skill` or `anti-hallucination` | §3.9's rules | yes |
| Debugging a failing test or gate code | any | `systematic-debugging` or `root-cause-debugging` | read the failure, form one hypothesis, test it | yes |

## Running

(none)
