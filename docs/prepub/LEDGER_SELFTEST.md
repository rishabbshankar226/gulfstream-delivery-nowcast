# Ledger self-test (P1.2)

Run 2026-11-11, about 19:30 ET. The ledger is `tools/prepub/ledger.py` with its rules in `tools/prepub/ledger_rules.py`, the dashboard renderer in `tools/prepub/render_site.py` and the hand-listed chart figures in `tools/prepub/chart_numbers.csv`.

## Copies

Both copies were made with `git archive prepub-audit | tar -x -C <dir>` from commit `7b3ba7e`, outside the repository. Each got `data/raw/wayback/cdx.json` copied in (an untracked raw file the as-of capture count is traced to), a `.venv` link to the project's environment, and `make pdf`, so the PDF in each copy is printed from that copy's `report/note.html`.

- Clean: `~/gdn-prepub/plant0/`, ledger at `plant0/LEDGER_clean.csv`.
- Planted: `~/gdn-prepub/plant1/`, ledger at `plant1/LEDGER_planted.csv`.

Commands:

```
~/gdn-prepub/venv/bin/python tools/prepub/ledger.py --root ~/gdn-prepub/plant0 --out ~/gdn-prepub/plant0/LEDGER_clean.csv
~/gdn-prepub/venv/bin/python tools/prepub/ledger.py --root ~/gdn-prepub/plant1 --out ~/gdn-prepub/plant1/LEDGER_planted.csv
```

## The nine plants and what caught each

All nine were planted in one copy. A row counts as the catch when it is flagged in the planted ledger and not in the clean one.

| # | Plant | Caught by (surface, place, status, shown, expected) |
|---|---|---|
| 1 | Post: `32.0` changed to `32.1` | `post`, `docs/LINKEDIN_POST.md:1`, `mismatch`, shown 32.1, expected 32.0 (`results/live/2026Q3_score.json nowcast.total`) |
| 2 | README: `69.2%` changed to `69.3%` | `readme`, `README.md:41`, `rounding`, shown 69.3%, expected 69.2 (`results/metrics.json holdout.band.coverage_pct`) |
| 3 | README: added "The 2026Q3 lock will be scored when GD reports." | `readme`, `README.md:93`, `stale`: pending wording ('will be scored') but results/live shows the quarter scored |
| 4 | README table: "Same quarter last year" average miss `4.6` changed to `5.5` (5.5 is the ratio model's figure) | `readme`, `README.md:22`, `mismatch`, label "Same quarter last year / Average miss", shown 5.5, expected 4.6 (`results/metrics.json holdout.mae.seasonal`) |
| 5 | README: "GD deliveries per registry event averaged 1.18" changed to "Registry events per delivery averaged 1.18" | `readme`, `README.md:69`, `mismatch`, shown 1.18, expected 0.91 (mean of registry events over GD deliveries, 2017Q1 to 2025Q2) |
| 6 | Workbook: `Summary!C2` formula given `+0.1` | `workbook`, `Summary!C2`, `mismatch`, computed 5.623395319586227, expected 5.523395319586225 |
| 7 | Note: Exhibit 2 "Same quarter last year" `4.6` changed to `4.7` in `report/note.html`, PDF rebuilt with `make pdf` | `note-pdf`, `output/GD_research_note.pdf:p2`, `rounding`, shown 4.7 (bound through `report/note.html`, where the same cell is flagged with expected 4.6) |
| 8 | `site/data.json`: the locked 2026Q3 total raised by 0.1 | `dashboard`, rendered first screen, `mismatch`, shown "32.1 deliveries, estimated", expected 32.0 (`predictions/2026Q3.json nowcast.total`); 26 more dashboard rows that derive from the same field |
| 9 | README: added "The first lock is still ahead." | `readme`, `README.md:108`, `stale`: no reviewed pattern admits this sentence about a lock or score under the state in results/live |

Nine planted, nine caught, zero missed. Plant 7 is labelled `rounding` and not `mismatch` because 4.7 is the source value 4.615 rounded up; the ledger still flags it.

### Two plants were missed on the first run, and the ledger was fixed

- Plant 5 passed at first. The unit rule then accepted a number when it equalled any quarter's inverse ratio, and one quarter's inverse rounds to 1.18. That was value matching. The rule now only flags, and a ratio is traced only by a template that names its unit and its window.
- Plant 6 passed at first. The reader took `formulas`' `to_dict()` for computed values, but it returns formula text, and cells with text were skipped without a row, so no formula cell was checked. The reader now takes values from the solution object, a formula that does not compute to a number is a `mismatch`, and a numeric cell with no rule is `untraced`. A check against `openpyxl` confirms all 482 formula cells have a ledger row.

All nine plants were rerun after both fixes. The table above is that rerun.

## The clean copy

`rows 2405  flagged 24`. Zero `mismatch` rows on any surface. Zero `untraced` rows on the post (12 traced) and the README (267 traced).

The 24 flagged rows on the clean copy are real defects in the tree, not ledger faults, so they stay flagged and each becomes a finding in P1.3:

| Surface | Rows | What |
|---|---|---|
| `interview` | 5 stale, 9 untraced | `docs/INTERVIEW_NOTES.md` still describes 2026Q3 as unlocked and unscored (lead L1) |
| `resume` | 1 stale | `docs/RESUME_BULLETS.md:2` "is scored on 2026-10-30" (lead L2) |
| `chart` | 7 stale | `output/charts/dashboard.png`, the README's first image, shows the 2026-10-19 page |
| `dashboard` | 1 stale | the live card labels the past release date "GD reports" |
| `build-notes` | 1 stale | `docs/build/` has no notice that its files are dated build logs |

The real tree also carries a stale PDF (lead L13). The clean copy does not show it because the copy's PDF was rebuilt.

## What the ledger does not do

- Dates, quarter labels, hashes and accession numbers are identifiers. Outside a live-record template they are bound by membership in the source set, not by label.
- A calendar year standing alone (2000 to 2027) is an identifier bound by range, unless a template slots it.
- A number word inside the fixed text of a matched template is bound by that template's text.
- Figures inside a sentence printed from `report/claims.json` are traced to the claim. Whether the claim is true is P3.3's job.
- Figures quoted from the external defense backlog study are traced to constants marked `external`; P3.3 checks them against the study.
- Numbers drawn inside chart images are listed by hand in `tools/prepub/chart_numbers.csv`. Values read off an axis are marked "read by eye".
- `docs/build/` is handled as one row: dated build logs, which need a notice saying so.
- The staleness check covers sentences about a lock or a score. Other stale claims (who runs the daily job, what a site blocks) are found by reading, in P4 and P5.
