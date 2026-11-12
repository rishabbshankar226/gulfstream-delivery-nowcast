"""Review round 1's wording fixes stay fixed: each test reads the tracked documents and fails if a corrected
phrase comes back or a correction goes missing. Ids refer to docs/build/REVIEW.md."""
import re
from html import unescape

import pytest

from conftest import ROOT


def text(rel):
    s = (ROOT / rel).read_text()
    if rel.endswith(".html"):
        s = unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s)


README, NOTE, POST = "README.md", "report/note.html", "docs/LINKEDIN_POST.md"
NOTES, BULLETS, APP, INDEX = "docs/INTERVIEW_NOTES.md", "docs/RESUME_BULLETS.md", "site/app.js", "site/index.html"


def absent(rel, *phrases):
    t = text(rel)
    assert [p for p in phrases if p in t] == []


def present(rel, *phrases):
    t = text(rel)
    assert [p for p in phrases if p not in t] == []


@pytest.mark.parametrize("rel", [README, NOTE, NOTES, BULLETS, APP, INDEX])
def test_lock_timing_says_the_day_before(rel):
    # N7, N8: the lock can fire at any hour of the eve once a snapshot dated the eve exists.
    absent(rel, "evening", "the eve of the release")


def test_as_of_mechanism_is_stated_as_measured():
    # N1, C2: the archived copies held more lag-quarter events, so the later file lost records.
    absent(README, "unfinished file", "has not posted, which")
    absent(NOTE, "because they read the lag quarters")
    absent("results/exploratory/asof.md", "harsher test")
    present(README, "held more events for the same lag quarters", "In three of the four",
            "came out slightly higher")
    present("results/exploratory/asof.md", "it came out higher")
    present(NOTE, "They held more events for the same past quarters")


def test_audit_breakdown_matches_the_audit_file():
    # N2, C9: four fresh-date used jets, one undated, two earlier deliveries, three unconfirmed; one release source.
    absent(README, "Every source", "four could not be confirmed")
    absent(NOTE, "every source was")
    present(README, "one with no airworthiness date or year at all", "All but one source")
    present(NOTE, "All but one source", "every event the audit could date fell between 2000 and 2019")
    present(README, "Every event the audit could date fell between 2000 and 2019")


def test_coverage_drift_reads_both_sides():
    # A1, N3, N10: the preregistered flag is one-sided; recent ratios sit below the mean.
    absent(README, "show no sign")
    absent(NOTES, "fairly steady")
    present(README, "The drift runs the other way")
    present(NOTE, "The drift runs the other way", "re-entered the US registry")
    present(APP, "The drift runs the other way")


def test_baseline_wording():
    # A3, N9, N12, N14, C8: name the baseline that missed by less, without claiming a test supports it.
    absent(POST, "never saw", "did a little better", "own guidance pace")
    absent(NOTES, "did better")
    absent(README, "hardest to beat")
    absent(NOTE, "hardest to beat")
    present(NOTE, "missed by less on average", "for the registry estimate and")
    present(POST, "held out from setting the rules", "missed by less on average")


def test_band_is_set_against_its_nominal_coverage():
    # C7
    for rel in (README, NOTE, APP):
        present(rel, "against a nominal 80%")


def test_yearly_tables_print_two_decimals_and_label_the_half_year():
    # N5, N6
    for rel in (README, NOTE):
        present(rel, "2026, first half")
    assert re.search(r"\| 2020 \| \d+\.\d\d \|", (ROOT / README).read_text())


def test_dashboard_labels():
    # C1, C3, N13
    absent(APP, "quarters of deliveries at GD's typical", "own guidance pace", '"550" ? "G550"')
    absent(NOTES, "own guidance pace")
    present(INDEX, "spread by each quarter's usual share of the year")


def test_exports_sources_and_claims():
    # C4, C5, C6, C10, C11, N4
    absent(README, "Many G280s", "Gulfstream test registration")
    absent(NOTE, "Many G280s", "daily snapshots since.", "whipped")
    present(NOTE, "GD Form 10-K for 2025")
    # F019: the release-date claim is cited only while the release is ahead. Once the quarter is scored the note
    # does not print it, and report/claims.json must not keep a claim the note does not cite.
    scored = (ROOT / "results/live/2026Q3_score.json").exists()
    cited = 'data-claim="os-release-date"' in (ROOT / NOTE).read_text()
    kept = '"os-release-date"' in (ROOT / "report/claims.json").read_text()
    assert cited == (not scored) and kept == cited
    absent(BULLETS, "Locked each")
