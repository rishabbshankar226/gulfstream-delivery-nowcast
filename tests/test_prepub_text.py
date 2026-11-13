"""Sentences and tables added in the pre-publication audit, each checked against the files it is built from.

Every figure here is recomputed in the test from results/holdout.csv, data/processed or results/live, never copied
from the text under test."""
import csv
import json
import subprocess

import pytest

from conftest import ROOT
from gdn import live, note, report, sensitivity
from gdn.files import write_json


def holdout_ae():
    chosen = json.loads((ROOT / "results/metrics.json").read_text())["definition"]
    ae = {}
    for r in csv.DictReader((ROOT / "results/holdout.csv").open()):
        if r["definition"] in ("none", chosen):
            ae.setdefault(r["quarter"], {})[r["model"]] = float(r["ae"])
    return ae


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def test_sensitivity_variants_recompute_from_the_holdout_file():
    # F022, F023, F050
    s = sensitivity.compute(ROOT)
    v = {x["key"]: x for x in s["variants"]}
    ae = holdout_ae()
    m = json.loads((ROOT / "results/metrics.json").read_text())["holdout"]
    for model in sensitivity.MODELS:
        assert v["preregistered"]["mae"][model] == pytest.approx(m["mae"][model], abs=1e-12)
    rest = [q for q in ae if q[:4] not in ("2023", "2024")]
    assert v["without_2023_2024"]["n"] == len(rest) == 18
    assert v["without_2023_2024"]["mae"]["guidance"] == pytest.approx(mean(ae[q]["guidance"] for q in rest))
    assert v["without_2023_2024"]["mae"]["ratio"] == pytest.approx(mean(ae[q]["ratio"] for q in rest))
    assert v["without_2020"]["mae"]["ratio"] == pytest.approx(m["mae_ex_2020"]["ratio"])
    # the 2021 reading changes only the guidance pace, and only in 2021
    alt = v["outlook_2021_as_117"]
    assert s["sourced_quarters_with_2021_as_117"] == 26 and alt["n"] == 26
    assert alt["mae"]["ratio"] == pytest.approx(m["mae"]["ratio"]) and alt["mae"]["guidance"] != m["mae"]["guidance"]
    t = alt["ratio_vs_guidance"]
    assert t["wins"] + t["losses"] + t["ties"] == 26
    # the other definition is scored on the same 26 quarters
    assert v["definition_E2"]["n"] == 26 and v["definition_E2"]["mae"]["seasonal"] == pytest.approx(m["mae"]["seasonal"])


def test_the_split_sentence_names_the_years_that_carry_the_lead():
    # F023. The registry estimate's lower average miss than the guidance pace comes from two years.
    ae = holdout_ae()
    s = report.split_sentence(ROOT)
    inside = [q for q in ae if q[:4] in ("2023", "2024")]
    rest = [q for q in ae if q[:4] not in ("2023", "2024")]
    assert "comes from 2023 and 2024" in s
    assert f"guidance pace missed by {mean(ae[q]['guidance'] for q in inside):.1f} on average" in s
    assert f"In the other {len(rest)} held-out quarters the guidance pace missed by {mean(ae[q]['guidance'] for q in rest):.1f}" in s
    assert f"registry estimate by {mean(ae[q]['ratio'] for q in rest):.1f}." in s


def test_the_2021_reading_is_disclosed_with_its_effect_on_the_headline():
    # F022. One reading of one call moves a headline figure; the README says so and gives both values.
    s = report.reading_2021(ROOT)
    v = {x["key"]: x for x in sensitivity.compute(ROOT)["variants"]}
    assert '"10 fewer aircraft"' in s and "Read as 117" in s
    assert f"misses by {v['outlook_2021_as_117']['mae']['guidance']:.1f} on average, not {v['preregistered']['mae']['guidance']:.1f}" in s
    assert "results/exploratory/sensitivity.md" in s
    assert s in report.results(ROOT)


def test_the_design_choice_sentence_counts_the_quarters_where_the_definitions_differ():
    # F050
    m = json.loads((ROOT / "results/metrics.json").read_text())
    rows = {r["quarter"]: r for r in csv.DictReader((ROOT / "data/processed/registry_quarterly.csv").open())}
    design = [q for q in rows if "2017Q1" <= q <= "2019Q4"]
    differ = [q for q in design if (rows[q]["e1_large"], rows[q]["e1_mid"]) != (rows[q]["e2_large"], rows[q]["e2_mid"])]
    s = report.definition_choice(ROOT, m)
    assert f"count the same in {len(design) - len(differ)} of the {len(design)} design quarters" in s
    assert all(q in s for q in differ) and f"against {m['holdout']['mae']['ratio']:.2f} under {m['definition']}" in s


def test_the_lock_timing_sentence_reads_the_lock_and_the_later_snapshots():
    # F034. The truncation table is not a model of a live lock: the sentence gives the lock's own facts.
    q = report.locked_scores(ROOT)[-1][0]          # the latest scored lock, whichever quarter that is
    p = json.loads((ROOT / f"predictions/{q}.json").read_text())
    s = json.loads((ROOT / f"results/live/{q}_score.json").read_text())
    at_lock = p["events"]["large"] + p["events"]["mid"]
    days = (live.dt.date.fromisoformat(p["snapshot"]) - live.dt.date.fromisoformat(p["window_end"])).days
    scale = (p["trailing"]["reported"]["large"] + p["trailing"]["reported"]["mid"]) / \
        (p["trailing"]["registry"]["large"] + p["trailing"]["registry"]["mid"])
    text = report.lock_timing(ROOT)
    assert f"taken {days} days after the quarter ended, when the quarter's count stood at {at_lock}" in text
    assert f"gave {scale:.2f} deliveries per registry event" in text
    assert f"came in at {s['reported']['total'] / at_lock:.2f}" in text
    assert text in report.error_analysis(ROOT)


def test_the_readme_headline_names_the_baseline_that_won_and_explains_its_terms():
    # F012, F024, F029
    r = report.results(ROOT)
    m = json.loads((ROOT / "results/metrics.json").read_text())["holdout"]
    bold = next(ln for ln in r.splitlines() if ln.startswith("**Over"))
    assert "Simply repeating the same quarter last year missed by less on average" in bold
    assert f"{m['mae']['seasonal']:.1f}" in bold and m["mae"]["seasonal"] < m["mae"]["ratio"]
    assert "the registry count is the scaled registry estimate" in r
    assert "GD's guidance pace is my construction, not a figure GD publishes" in r


@pytest.fixture
def clone(tmp_path):
    root = tmp_path / "repo"
    subprocess.run(["git", "clone", "-q", str(ROOT), str(root)], check=True)
    return root


def test_the_release_date_claim_is_cited_only_while_the_release_is_ahead(clone):
    # F004. Before a score the note cites GD's announced call date; after it, the note does not, and
    # report/claims.json must not keep a claim the note no longer cites (the gate's N4).
    claim = next(c for c in json.loads((ROOT / "docs/build/claims_outlook.json").read_text())
                 if c["id"] == "os-release-date")
    pool = json.loads((clone / "report/claims.json").read_text())
    if all(c["id"] != claim["id"] for c in pool):
        pool.append(claim)
    cj = clone / "report/claims.json"
    cj.write_text(json.dumps(sorted(pool, key=lambda c: c["id"]), indent=2, ensure_ascii=False) + "\n")
    # with the tracked state (2026Q3 scored) the claim is not cited and is pruned
    note.build(clone)
    assert 'data-claim="os-release-date"' not in (clone / "report/note.html").read_text()
    assert all(c["id"] != "os-release-date" for c in json.loads(cj.read_text()))
    # put the quarter back to the day before its score: the claim is cited and kept
    cj.write_text(json.dumps(sorted(pool, key=lambda c: c["id"]), indent=2, ensure_ascii=False) + "\n")
    for rel in ("results/live/2026Q3_score.json", "results/live/2026Q4_latest.json", "results/live/2026Q4_path.csv",
                "data/processed/segments_reported.csv"):
        (clone / rel).unlink(missing_ok=True)
    note.build(clone)
    assert 'data-claim="os-release-date"' in (clone / "report/note.html").read_text()
    assert any(c["id"] == "os-release-date" for c in json.loads(cj.read_text()))


def test_the_note_sets_gd_reported_revenue_beside_each_estimate(clone):
    # F013. Once the quarter is scored and the release's segment table is on file, Exhibit 8 carries it.
    note.build(clone)
    html = (clone / "report/note.html").read_text()
    seg = live.reported_segments(clone)["2026Q3"]
    est = json.loads((clone / "results/estimates.json").read_text())
    assert "the estimates made before the release, and what GD reported" in html
    assert f"${seg['Aerospace'][0] / 1e9:.1f}B" in html
    miss = est["aerospace_from_nowcast_usd"] - seg["Aerospace"][0]
    assert f"-${abs(miss) / 1e6:,.0f}M" in html
    assert "What the street watches on the print" not in html          # a preview has no place after the print
    assert "I made the estimates in this note before GD reported 2026Q3" in html
    # without the reported file the exhibit goes back to the change on the year
    (clone / "data/processed/segments_reported.csv").unlink()
    note.build(clone)
    assert "Estimate less reported" not in (clone / "report/note.html").read_text()


def test_the_note_footer_carries_the_disclaimer_on_every_printed_page(clone):
    # F030. Chrome prints the @bottom-center margin box on every page.
    note.build(clone)
    html = (clone / "report/note.html").read_text()
    css = html[html.index("<style>"):html.index("</style>")]
    assert "@bottom-center" in css and "Not investment advice" in css and "Not affiliated with General Dynamics" in css
    assert "PAGEFOOT" not in css


def test_gd_stated_quarter_plans_are_scored_beside_the_guidance_pace(tmp_path):
    # F058. On six calls GD stated the quarter's own delivery plan. The preregistered pace ignores them; the
    # exploratory file scores them, and the README gives the result beside the headline.
    plans = {r["quarter"]: r for r in csv.DictReader((ROOT / "data/quarter_plans.csv").open())}
    ends = {r["quarter"]: r["fiscal_end"] for r in csv.DictReader((ROOT / "data/processed/gd_deliveries.csv").open())}
    reported = {r["quarter"]: int(r["total"]) for r in csv.DictReader((ROOT / "data/processed/gd_deliveries.csv").open())}
    assert all(plans[q]["call_date"] <= ends[q] for q in plans)          # stated before the quarter ended
    ae = holdout_ae()
    swapped = [abs(float(plans[q]["plan"]) - reported[q]) if q in plans else ae[q]["guidance"] for q in ae]
    s = sensitivity.compute(ROOT)
    v = {x["key"]: x for x in s["variants"]}["quarter_plans"]
    assert v["mae"]["guidance"] == pytest.approx(mean(swapped))
    assert v["mae"]["ratio"] == pytest.approx(mean(ae[q]["ratio"] for q in ae))
    closer = sum(1 for q, g in zip(ae, swapped) if ae[q]["ratio"] < g)
    assert v["ratio_vs_guidance"]["wins"] == closer
    text = report.results(ROOT)
    assert f"the baseline misses by {mean(swapped):.1f} on average" in text
    assert f"the registry estimate is closer in {closer} of {len(ae)} quarters" in text
    # a plan stated after its quarter's fiscal end is refused
    from gdn.fiscal import Calendar
    bad = tmp_path / "data"
    bad.mkdir()
    (bad / "quarter_plans.csv").write_text("quarter,call_date,plan,quote,speaker,url\n2023Q3,2023-10-25,27,q,s,u\n")
    with pytest.raises(ValueError):
        sensitivity.load_quarter_plans(tmp_path, Calendar.load(ROOT))


def test_the_dashboard_link_preview_image_follows_the_chart(tmp_path):
    # F053. The page a LinkedIn post links to needs an og:image that Pages serves and the daily job keeps current.
    from gdn import charts, daily
    (tmp_path / "output/charts").mkdir(parents=True)
    (tmp_path / "site").mkdir()
    (tmp_path / "output/charts/track_record.png").write_bytes(b"one")
    charts._preview(tmp_path)
    assert (tmp_path / "site/preview.png").read_bytes() == b"one"
    (tmp_path / "output/charts/track_record.png").write_bytes(b"two")
    charts._preview(tmp_path)
    assert (tmp_path / "site/preview.png").read_bytes() == b"two"
    page = (ROOT / "site/index.html").read_text()
    assert ('<meta property="og:image" content="https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/'
            'preview.png">') in page
    assert "site/preview.png" in daily.REBUILD_PATHS
    assert (ROOT / "site/preview.png").read_bytes() == (ROOT / "output/charts/track_record.png").read_bytes()


def test_no_chart_legend_calls_the_pace_gds():
    # F068, F029. The pace is my construction from GD's outlook; a legend that says "GD guidance pace" reads as GD's.
    from gdn import charts
    src = (ROOT / "src/gdn/charts.py").read_text()
    assert charts.NAMES["guidance"] == "Pace built from GD's outlook"
    assert "GD guidance pace" not in src
