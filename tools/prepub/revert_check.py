"""R6: each code fix has a test that fails with the fix reverted and passes with it.

    .venv/bin/python tools/prepub/revert_check.py <scratch clone> > docs/prepub/REVERT_TESTS.md

The scratch clone is a `git clone` of this repository's `prepub-audit` under ~/gdn-prepub/scratch/. For each fix the
script puts back the old behaviour in the clone's working tree (one targeted edit, or the file as it stood at
origin/main), runs the named test there and records the result, then restores the file from this repository and
runs the test again. Nothing in this repository is touched.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path(sys.argv[1]).resolve()
PY = str(ROOT / ".venv/bin/python")
BASE = "36fed31"   # origin/main when the audit began

# (finding, file, fixed text, reverted text or None for "the whole file as at origin/main", test)
CASES = [
    ("F001", "src/gdn/daily.py", '    _stage("charts", "run", root=root)\n', "",
     "tests/test_daily.py::test_the_daily_rebuild_redraws_the_charts"),
    ("F004", "src/gdn/note.py",
     'rel_cite = C.sup("os-release-date") if (C.has("os-release-date") and rel and not score) else ""',
     'rel_cite = C.sup("os-release-date") if C.has("os-release-date") else ""',
     "tests/test_prepub_text.py::test_the_release_date_claim_is_cited_only_while_the_release_is_ahead"),
    ("F005", "src/gdn/report.py",
     '    if cfg.get("public") and since and published_at[:10] >= since:\n        return "public GitHub release"\n    return PRIVATE',
     '    return "public GitHub release" if cfg.get("public") else PRIVATE',
     "tests/test_after_score.py::test_a_lock_is_called_public_only_if_the_repository_was_public_that_day"),
    ("F009 F013 (dashboard)", "site/app.js", None, None,
     "tests/test_site_a11y.py::test_a_scored_lock_states_its_miss_and_its_band_in_the_past_tense"),
    ("F013 (note)", "src/gdn/note.py", "    rseg = live.reported_segments(root).get(q) if score else None",
     "    rseg = None",
     "tests/test_prepub_text.py::test_the_note_sets_gd_reported_revenue_beside_each_estimate"),
    ("F013 (data)", "src/gdn/live.py",
     '    try:\n        seg = sec.parse_segments(release_text)\n    except ValueError as e:',
     '    return False\n    try:\n        seg = sec.parse_segments(release_text)\n    except ValueError as e:',
     "tests/test_live.py::test_what_gd_reported_by_segment_is_kept_for_a_scored_quarter"),
    ("F014", "src/gdn/daily.py", "        if date in snaps and content(snaps[date]) != content(entry):",
     "        if date in snaps and snaps[date] != entry:",
     "tests/test_daily.py::test_a_manifest_merge_accepts_the_same_zip_downloaded_at_two_times"),
    ("F017", "src/gdn/live.py", "            if end is None or snap <= end:", "            if False:",
     "tests/test_live.py::test_no_lock_from_a_subset_that_predates_the_quarter_end"),
    ("F018", "src/gdn/live.py", '        if parse_now(published) >= parse_now(f["accepted"]):', "        if False:",
     "tests/test_live.py::test_a_lock_published_after_the_filing_is_not_scored"),
    ("F020", "src/gdn/report.py", "        if len(ls) == 1:\n            verb =", "        if True:\n            verb =",
     "tests/test_after_score.py::test_the_post_counts_its_locked_quarters"),
    ("F022", "src/gdn/report.py",
     '    a, b = v.get("outlook_2021_as_117"), v.get("preregistered")\n    if not a or not b:\n        return ""',
     '    a, b = v.get("outlook_2021_as_117"), v.get("preregistered")\n    if True:\n        return ""',
     "tests/test_prepub_text.py::test_the_2021_reading_is_disclosed_with_its_effect_on_the_headline"),
    ("F023", "src/gdn/report.py", "    if not won or not rest or len(won) > len(years) / 2", "    if True or not won or not rest or len(won) > len(years) / 2",
     "tests/test_prepub_text.py::test_the_split_sentence_names_the_years_that_carry_the_lead"),
    ("F012 F024 F029", "src/gdn/report.py", '        f"**{headline(m)}{low_line(m)}**", "",\n        CLARIFY, "",',
     '        f"**{headline(m)}**", "",',
     "tests/test_prepub_text.py::test_the_readme_headline_names_the_baseline_that_won_and_explains_its_terms"),
    ("F025", "src/gdn/report.py", "                cmp_ = comparators(root, q, score, p)\n                if cmp_:",
     "                cmp_ = comparators(root, q, score, p)\n                if False:",
     "tests/test_after_score.py::test_the_live_record_sets_the_lock_beside_the_other_misses"),
    ("F030", "src/gdn/note.py", '  @bottom-center { content: "PAGEFOOT";', '  @bottom-left-corner { content: "";',
     "tests/test_prepub_text.py::test_the_note_footer_carries_the_disclaimer_on_every_printed_page"),
    ("F031", "src/gdn/workbook.py", None, None,
     "tests/test_outputs.py::test_the_workbook_carries_the_guidance_baseline_and_the_live_result"),
    ("F034", "src/gdn/report.py", "    ls = locked_scores(root)\n    if not ls:\n        return \"\"\n    q, s, p, lock = ls[-1]\n    days =",
     "    return \"\"\n    ls = locked_scores(root)\n    q, s, p, lock = ls[-1]\n    days =",
     "tests/test_prepub_text.py::test_the_lock_timing_sentence_reads_the_lock_and_the_later_snapshots"),
    ("F050", "src/gdn/report.py", "    if not v or len(diff) > 2:\n        return \"\"", "    if True:\n        return \"\"",
     "tests/test_prepub_text.py::test_the_design_choice_sentence_counts_the_quarters_where_the_definitions_differ"),
    ("F053", "src/gdn/charts.py", "        dst.write_bytes(src.read_bytes())", "        pass",
     "tests/test_prepub_text.py::test_the_dashboard_link_preview_image_follows_the_chart"),
    ("F068", "src/gdn/charts.py", '"guidance": "Pace built from GD\'s outlook"', '"guidance": "GD guidance pace"',
     "tests/test_prepub_text.py::test_no_chart_legend_calls_the_pace_gds"),
    ("F108", "src/gdn/report.py", 'lines.append(f"{len(ls)} locked estimates so far: off by {f1(avg)} jets on "',
     'lines.append(f"{len(ls)} locked estimates of Gulfstream deliveries so far: off by {f1(avg)} jets on "',
     "tests/test_after_score.py::test_the_post_counts_its_locked_quarters"),
    ("F058", "src/gdn/sensitivity.py", "    if plans:\n        variants += [", "    if False:\n        variants += [",
     "tests/test_prepub_text.py::test_gd_stated_quarter_plans_are_scored_beside_the_guidance_pace"),
    # round 4 (docs/prepub/ROUND4_VERDICT.md)
    ("F124", "src/gdn/live.py", '        if not f.get("accepted"):\n', '        if False:\n',
     "tests/test_live.py::test_a_lock_is_not_scored_when_sec_gives_no_acceptance_time"),
    ("F109", "src/gdn/note.py",
     "GD was left out because the SEC's XBRL company-facts data holds no \"\n        \"quarterly GD backlog after 2018Q3.",
     "GD was left out because it stopped tagging backlog in XBRL in 2018.",
     "tests/test_round4.py::test_the_note_states_why_gd_left_the_defense_study_as_the_filings_allow"),
    ("F113 (post)", "src/gdn/report.py",
     "my 80% band of past misses (it held {hb['hits']} of \"\n                  f\"{hb['n']} past quarters).\")",
     "my 80% band of past misses.\")",
     "tests/test_after_score.py::test_a_locked_and_scored_quarter_keeps_its_text"),
    ("F113 (note)", "src/gdn/note.py",
     "    return f\", which held GD's count in {b['hits']} of {b['n']} held-out quarters against a nominal 80%\"",
     "    return \"\"",
     "tests/test_round4.py::test_the_band_is_shown_with_its_coverage_in_the_note_and_the_workbook"),
    ("F113 (workbook)", "src/gdn/workbook.py", '    put(ws, "C14", f"The band held GD', '    pass  # put(ws, "C14", f"The band held GD',
     "tests/test_round4.py::test_the_band_is_shown_with_its_coverage_in_the_note_and_the_workbook"),
    ("F113 (dashboard)", "site/app.js",
     "\" deliveries. \" +\n      \"It held GD's count in \" + hb.hits + \" of \" + hb.n + \" held-out quarters, against a nominal 80%.\");",
     "\" deliveries.\");",
     "tests/test_site_a11y.py::test_the_live_card_states_the_band_coverage_and_names_the_pace_as_mine"),
    ("F114 (dashboard)", "site/app.js", "fact(\"Pace I built from GD's outlook\",", "fact(\"GD's guidance pace\",",
     "tests/test_site_a11y.py::test_the_live_card_states_the_band_coverage_and_names_the_pace_as_mine"),
    ("F114 F116 (note)", "src/gdn/note.py",
     '{esc(low_line(m))} {esc(GLOSS)}" + (f" {esc(split)}" if split else "")', '{esc(low_line(m))}"',
     "tests/test_round4.py::test_the_notes_first_page_glosses_its_terms_and_says_where_the_edge_comes_from"),
    ("F115", "src/gdn/note.py", "            live_point += stated_shape(root, q) + even_split(root, q, score)\n",
     "            pass\n",
     "tests/test_round4.py::test_gds_stated_shape_of_the_year_and_the_even_split_sit_beside_the_pace"),
    ("F117", "src/gdn/charts.py",
     '        if s.get("locked") and s.get("nowcast") and p.exists() and qidx(q) > qidx(QS[-1]):', "        if False:",
     "tests/test_round4.py::test_the_track_chart_draws_each_scored_lock_after_the_backtest"),
    ("F118", "site/app.js", '(m === "raw" || m === "last")', '(m === "raw" || m === "seasonal" || m === "last")',
     "tests/test_site_a11y.py::test_a_phone_keeps_the_baseline_that_won_on_the_track_chart"),
    ("F119", "src/gdn/note.py",
     "I read the FAA's aircraft registry for every Gulfstream jet type my scope rule keeps, including the \"\n        \"G280,",
     "I read every Gulfstream jet in the FAA's aircraft registry, including the \"\n        \"G280,",
     "tests/test_round4.py::test_the_note_does_not_say_it_reads_every_gulfstream_jet"),
    ("F122", "src/gdn/note.py",
     '(f" A third bears on the mid-cabin count directly: {C.say(own)}" if C.has(own) else "")', '""',
     "tests/test_round4.py::test_the_notes_risks_carry_the_mid_cabin_supplier_delay"),
    ("F123", "src/gdn/workbook.py",
     'before anything else. A baseline with a lower holdout figure than MAE ratio missed by "',
     'before anything else: a baseline with a lower holdout figure than MAE ratio beat the "',
     "tests/test_round4.py::test_the_workbook_summary_does_not_say_a_baseline_beat_the_estimate"),
    ("F130", "src/gdn/report.py", 'f"quarter on average, my pace from GD\'s outlook by {f1(h[\'mae\'][\'guidance\'])}',
     'f"quarter on average, GD\'s guidance pace by {f1(h[\'mae\'][\'guidance\'])}',
     "tests/test_round4.py::test_the_readmes_first_screen_says_whose_pace_it_is"),
]


def run(test):
    # A fresh bytecode cache for every run: a revert that keeps the file's size and lands in the same second as the
    # restore would otherwise be served from the stale .pyc, and the restored run would test the reverted code.
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONPYCACHEPREFIX": tempfile.mkdtemp(prefix="pyc")}
    r = subprocess.run([PY, "-m", "pytest", "-q", "--tb=no", "-p", "no:cacheprovider", test], cwd=SCRATCH,
                       capture_output=True, text=True, env=env)
    last = [ln for ln in r.stdout.strip().splitlines() if ln.strip()][-1] if r.stdout.strip() else r.stderr.strip()[-120:]
    return ("PASS" if r.returncode == 0 else "FAIL"), last


print("# Regression tests against reverted fixes (R6)\n")
print(f"Scratch clone: `{str(SCRATCH).replace(str(Path.home()), '~')}`. Written by `tools/prepub/revert_check.py`. For each "
      "fix the old behaviour is put back in the clone (one targeted edit, or the whole file as it stood at `origin/main` "
      f"`{BASE}`), the test is run, the file is restored from this repository, and the test is run again.\n")
print("| Finding | File reverted | Test | With the fix reverted | With the fix restored |")
print("|---|---|---|---|---|")
bad = 0
for finding, rel, fixed, reverted, test in CASES:
    src, dst = ROOT / rel, SCRATCH / rel
    shutil.copyfile(src, dst)
    if fixed is None:
        old = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:{rel}"], capture_output=True).stdout
        dst.write_bytes(old)
        how = f"`{rel}` as at `{BASE}`"
    else:
        text = dst.read_text()
        if fixed not in text:
            print(f"| {finding} | `{rel}` | `{test}` | REVERT NOT APPLIED: anchor text missing | |")
            bad += 1
            continue
        dst.write_text(text.replace(fixed, reverted, 1))
        how = f"`{rel}`, one edit"
    a, la = run(test)
    shutil.copyfile(src, dst)
    b, lb = run(test)
    if (a, b) != ("FAIL", "PASS"):
        bad += 1
    print(f"| {finding} | {how} | `{test}` | {a}: `{la}` | {b}: `{lb}` |")
print(f"\n{len(CASES)} fixes checked, {len(CASES) - bad} with FAIL when reverted and PASS when restored, {bad} otherwise.")
print("\nNot in this table: F003 is a repair of six tests, whose failing state is the baseline run in `BASELINE.md` "
      "(`6 failed, 114 passed`) and whose passing state is the current suite. F048 corrects a comment, not code; its "
      "test (`tests/test_model.py::test_nearest_rank_positions_match_exact_arithmetic`) pins the behaviour the comment "
      "now describes. Round 4's F125, F126 and F127 change tests only: F125 and F127 add direct tests of code that was "
      "already right (the neither-date bound and the old-airframe counts), and F126 moves tests off the tracked live "
      "files; F126's check against a 2026Q4-locked tree is in DECISIONS.md D24.")
sys.exit(1 if bad else 0)
