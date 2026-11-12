# The public surface (P0.4)

Built 2026-11-11 from `prepub-audit` at `9c05aeb`. "Daily rewrites" is read from `src/gdn/daily.py:19-25` (`LIVE_PATHS`, `REBUILD_PATHS`, `LOCK_PATHS`) and `daily.py:40-47` (`rebuild`: estimates, workbook, note, PDF on a Mac outside CI, site data, report). Generator evidence is the `grep -rn '<path>' src/gdn tools/*.py Makefile` line.

| File | Generator (grep evidence) | Daily rewrites it? |
|---|---|---|
| `docs/LINKEDIN_POST.md` | `src/gdn/report.py:263: write_text(root / "docs/LINKEDIN_POST.md", p)` | yes (`REBUILD_PATHS`) |
| `README.md`, sections `## Results`, `## Error analysis`, `## Live record` | `src/gdn/report.py:250-256` (`replace_section`) | yes (`REBUILD_PATHS`) |
| `README.md`, everything else (title, lead, Method, Data, Limitations, Reproduce, footer) | hand-written: `report.py` replaces only the three sections | no |
| `output/charts/track_record.png`, `coverage.png`, `signed_errors.png`, `nowcast_path.png` | `src/gdn/charts.py:66: p = Path(root) / "output/charts" / name` | no. `make all` runs `charts`; `daily.rebuild` does not (L12) |
| `output/charts/dashboard.png` (README hero image) | none. A screenshot made with `tools/shoot.py`; `tools/determinism.py:15` skips it | no |
| GitHub description, topics, homepage | set on GitHub by hand; read with `gh repo view --json description,repositoryTopics,homepageUrl` | no |
| `site/index.html` | hand-written (no hit in `src/gdn`) | no |
| `site/app.js` | hand-written (only docstring mentions: `charts.py:163`, `site_data.py:1`) | no |
| `site/style.css` | hand-written (no hit) | no |
| `site/data.json` | `src/gdn/site_data.py:81: write_json(root / "site/data.json", data)` | yes |
| `site/GD_research_note.pdf` | `src/gdn/note.py:602` (`run_pdf`, a copy of the output PDF) | only on a Mac outside CI (`daily.py:44`) |
| `output/GD_research_note.pdf` | `src/gdn/note.py:602` (`run_pdf`, headless Chrome) | only on a Mac outside CI |
| `output/GD_research_note.inputs.sha256` | `note.py` `run_pdf` | only on a Mac outside CI |
| `report/note.html` | `src/gdn/note.py:553: write_text(root / "report/note.html", text)` | yes |
| `report/claims.json` | `src/gdn/claims.py:79` (`make claims`, from `docs/build/claims_*.json`) | no. `make all` omits `claims` |
| `output/gd_gulfstream_model.xlsx` | `src/gdn/workbook.py:21: OUT = Path("output/gd_gulfstream_model.xlsx")` | yes |
| `docs/PREREGISTRATION.md` | `tools/preregister.py:1` (cut from v1's prompt file, once). Immutable (R7) | no |
| `results/design.csv` | `src/gdn/model.py:85` | no (`make all` only) |
| `results/holdout.csv`, `results/metrics.json` | `src/gdn/model.py:261`, `:266` | no (`make all` only) |
| `results/error_analysis.md` | `src/gdn/errors.py:65` | no (`make all` only) |
| `results/estimates.json` | `src/gdn/estimates.py:67` | yes |
| `results/diagnostics/*` | `src/gdn/diagnostics.py:47` | no (`make all` only) |
| `results/exploratory/asof.csv`, `asof.md` | `tools/asof.py:89`, `:115` (run by hand) | no |
| `results/live/*` | `src/gdn/live.py` (`update_latest`, `write_lock_json`, `run_score`, `write_build`) | yes (`LIVE_PATHS`). Immutable for 2026Q3 (R7) |
| `predictions/2026Q3.json` | `src/gdn/live.py:376` (`run_lock`). Immutable (R7) | only at a lock (`LOCK_PATHS`) |
| `lock-2026Q3` release notes | `src/gdn/gitops.py:144` (`release_create`, notes `sha256 <digest>`) | only at a lock |
| `data/processed/*.csv` | `src/gdn/data.py` (`make data`) | no |
| `data/guidance.csv` | `tools/build_guidance.py` (run by hand) | no |
| `data/snapshots/*` | `src/gdn/faa.py:232` (`store_subset`), `live.py:97` (`write_table`) | yes (`LIVE_PATHS`) |
| `docs/INTERVIEW_NOTES.md` | hand-written (no hit) | no |
| `docs/RESUME_BULLETS.md` | hand-written (no hit) | no |
| `docs/build/*` | v1's build notes, hand-written; `claims_*.json` feed `make claims` (`claims.py:85`); `audit_sample.csv` from `tools/audit_pick.py` | no |
| `LICENSE` | hand-written | no |

## What `"public"` in `config/calendar.json` changes

Readers found with `grep -rn 'public' src/gdn .github/workflows`:

| Reader | Effect when `true` |
|---|---|
| `src/gdn/report.py:147` | README `## Live record` calls every lock a "public lock" in place of a "timestamped GitHub release" |
| `src/gdn/note.py:243-244` | The note's key point 2 and tracker section say "I locked it as a public lock" in place of "timestamped GitHub release" |
| `src/gdn/live.py:398-401` | Only the log line printed when a new lock is made |
| `.github/workflows/pages.yml:16` | Not the key: Pages deploys when `github.event.repository.private == false`, on a push that touches `site/**` or by manual dispatch |

`site/app.js` and `site_data.py` do not read the key. Consequence (finding F005): the key is global, so setting it `true` would call the 2026Q3 lock a "public lock" although the repository was private when that release was published. The wording must follow each lock's own state.

## GitHub metadata (read 2026-11-11)

`gh repo view --json description,repositoryTopics,homepageUrl` printed: description "Gulfstream deliveries estimated from FAA registrations, tested on 26 held-out GD quarters, each live estimate locked"; homepage `https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/`; topics `equity-research`, `faa-registry`, `general-dynamics`, `gulfstream`, `python`.

## Rounding conventions

| Surface | Code | Rule |
|---|---|---|
| README generated sections, post | `report.py:18-23` `f"{x:.1f}"`, `f"{x:.2f}"`; p-values `:.3f` | Python format: the binary value rounded half-to-even at the stated decimals |
| Note | `note.py:43-64` `f1`, `f2`, `bn` (`$x.xB`), `mn` (`$x,xxxM`), `pct` | same Python rule |
| `results/error_analysis.md` | `errors.py:22` `f"{x:.1f}"` | same Python rule |
| Dashboard | `site/app.js:25-29`: `f1` is `(Math.round(x*10)/10).toFixed(1)`, `whole` is `Math.round`, `usdB` `.toFixed(1)`, `usdM` `Math.round`, `pct` `.toFixed(d)`; p-values `.toFixed(3)`, ratios `.toFixed(2)` | JavaScript: `Math.round` rounds half up; `toFixed` rounds the binary value |
| Workbook | `workbook.py:18` number formats `#,##0`, `0.0`, `0.0%`, `0.00`; some cells use `ROUND(` | Excel display rounding, half away from zero |
| Charts | matplotlib tick labels; no figure labels beyond axis ticks and legend text | n/a |

The three rules can disagree only on a value that sits exactly on a half at the displayed decimal (for example 6.25 shown to one decimal: Python gives 6.2, JavaScript and Excel give 6.3). The ledger compares each displayed figure with its source at the displayed precision under both rules and labels a half-case `rounding`. The README's by-year table uses two decimals for this reason (`report.py:107`).

Percentage misses: `model.py:56` and `live.py:420` both divide the absolute miss by GD's reported count.
