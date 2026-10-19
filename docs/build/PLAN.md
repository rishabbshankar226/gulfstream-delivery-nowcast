# Plan

Backtest snapshot: 2026-10-19. Critical path (Phases 0 to 5) due 2026-10-28 18:00 ET; done 2026-10-19 12:35 EDT.

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
| 2 | coverage_design.csv and the 0.5 to 1.5 check | done | - | 5c84d36 |
| 2 | guidance.csv from three checkers | done | T3 | 5c84d36 |
| 2 | design.csv, chosen definition | done | M1 | 5c84d36 |
| 2 | PREREGISTRATION.md, committed alone | done | Q1 Q2 | 2c62ad3 |
| 3 | holdout.csv, metrics.json, tests | done | M2 M3 | 48c1ea0 |
| 3 | error_analysis.md | done | - | 48c1ea0 |
| 4 | calendar.json, live.py, build nowcast, path, latest, daily table | done | L1 L2 | 3d94197 |
| 4 | estimates.json | done | S2 | 3d94197 |
| 4 | Lock and score tests with fixed clocks, limitations notes | done | - | 3d94197 |
| 5 | make daily-core / daily, workflows, LICENSE, SEC_UA secret | done | Y4 | 9b3176e |
| 5 | Workflow run and watch | done | - | runs 39283382067, 39283387767 |
| 5 | Lock rehearsal, REHEARSAL.md | done | L1 to L4 | 81ceefb |
| 5 | Critical path ready | done | faa truth model prereg segments live | see log |
| 6 | Workbook | done | W1 to W5 | phase 6 commit |
| 6 | Charts, VISUAL_QA rows | done | - | phase 6 commit |
| 6 | claims.json, test_claims.py | done | N4 | phase 6 commit |
| 6 | note.html and PDF | done | N1 to N3 | phase 6 commit |
| 7 | site_data.py, page, a11y test | done | Y1 to Y3 | phase 7 commit |
| 7 | Impeccable critique, audit, polish; shots | done | site | phase 7 commit |
| 8 | README, LINKEDIN_POST, INTERVIEW_NOTES, RESUME_BULLETS | done | R1 to R4 K1 K2 V1 | phase 8 commit |
| 8 | Full gate | todo | all | |
| 9 | Airframe audit | done; 25-non-mirror requirement open | - | phase 9 audit commit |
| 9 | Mutation pass | done | - | phase 9 commit |
| 9 | check-determinism | done | - | phase 9 commit |
| 9 | As-of study | done | - | 9b84384 |
| 10 | Fresh clone build and gate | done (early run; repeat at the end) | all but repo | 6bef306 |
| R | Review round 1 | done; findings and open items in REVIEW.md | docs | 1a02088, 47af692, a2f8e76, f3f1471 |
| R | Review rounds 2 and 3 | todo | - | |
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

- http.server on 127.0.0.1:8766 serving site/ (background); stop with `pkill -f "http.server 8766"`
- CronCreate job 8599714f: morning daily-job reminder at 06:43 local, session-only
