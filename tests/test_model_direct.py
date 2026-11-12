"""Direct tests of three model functions the first review left without one (its item T9): `truncated_mae`,
`coverage_drift` and `holdout_metrics`. Each expected value is rebuilt here from the data files with plain
arithmetic, never read from results/."""
import csv
import datetime as dt

import pytest

from conftest import ROOT
from gdn import events, model
from gdn.files import read_csv
from gdn.fiscal import HOLDOUT, Calendar, qrange, shift


@pytest.fixture(scope="module")
def data():
    Y, N = model.load_reported(ROOT), model.load_registry(ROOT)
    cal = Calendar.load(ROOT)
    chosen = model.choose(model.design_rows(Y, N))[0]
    rows_air = events.read_serials_rows(read_csv(ROOT / "data/processed/serials.csv"))
    return Y, N, cal, chosen, rows_air


def by_hand(Y, N, cal, chosen, serials, q, days):
    """The ratio estimate for q with its own events cut `days` before the window's end, summed over the cabins."""
    lo, hi = cal.window(q)
    cut = (dt.date.fromisoformat(hi) - dt.timedelta(days=days)).isoformat()
    key = chosen.lower()
    total = 0.0
    for cabin in ("large", "mid"):
        own = sum(1 for r in serials if r["cabin"] == cabin and r[key] and lo < r[key] <= cut)
        lags = [shift(q, -k) for k in range(1, 5)]
        reg = sum(N[x][chosen][cabin] for x in lags)
        rep = sum(Y[x][cabin] for x in lags)
        total += own * rep / reg if reg else 0.0
    return total


@pytest.mark.parametrize("days", [0, 30, 90])
def test_truncated_mae_is_the_mean_miss_with_each_quarters_events_cut_early(data, days):
    Y, N, cal, chosen, rows_air = data
    serials = list(csv.DictReader((ROOT / "data/processed/serials.csv").open()))
    qs = qrange(*HOLDOUT)
    want = sum(abs(by_hand(Y, N, cal, chosen, serials, q, days) - Y[q]["total"]) for q in qs) / len(qs)
    assert model.truncated_mae(rows_air, Y, N, chosen, cal, days) == pytest.approx(want, abs=1e-9)


def test_truncating_by_zero_days_is_the_untruncated_holdout_miss(data):
    Y, N, cal, chosen, rows_air = data
    hold = model.holdout_rows(Y, N, chosen, model.load_guidance(ROOT), cal)
    ratio = [r["ae"] for r in hold if r["model"] == "ratio"]
    assert model.truncated_mae(rows_air, Y, N, chosen, cal, 0) == pytest.approx(sum(ratio) / len(ratio), abs=1e-9)


def test_coverage_drift_is_deliveries_per_registry_event_and_flags_only_a_rise(data):
    Y, N, cal, chosen, _ = data
    cr = model.coverage_drift(Y, N, chosen)
    q = "2026Q2"
    assert cr["by_quarter"][q] == pytest.approx(Y[q]["total"] / (N[q][chosen]["large"] + N[q][chosen]["mid"]))
    base = [cr["by_quarter"][x] for x in qrange("2017Q1", "2025Q2")]
    mean = sum(base) / len(base)
    sd = (sum((x - mean) ** 2 for x in base) / (len(base) - 1)) ** 0.5
    assert cr["mean"] == pytest.approx(mean) and cr["sd"] == pytest.approx(sd)
    recent = qrange("2025Q3", HOLDOUT[1])
    assert cr["flags"] == [x for x in recent if cr["by_quarter"][x] > mean + 2 * sd]
    # the flag is one-sided: a quarter far below the mean is never flagged
    low = dict(Y)
    low["2026Q2"] = {"large": 1, "mid": 0, "total": 1}
    assert "2026Q2" not in model.coverage_drift(low, N, chosen)["flags"]
    # and a quarter far above it is
    high = dict(Y)
    high["2026Q2"] = {"large": 400, "mid": 0, "total": 400}
    assert "2026Q2" in model.coverage_drift(high, N, chosen)["flags"]


def test_holdout_metrics_average_the_rows_they_are_given(data):
    Y, N, cal, chosen, rows_air = data
    calls = model.load_guidance(ROOT)
    design, hold = model.design_rows(Y, N), model.holdout_rows(Y, N, chosen, calls, cal)
    h = model.holdout_metrics(design, hold, Y, N, chosen, calls, cal, rows_air)
    assert h["n"] == len(qrange(*HOLDOUT)) == 26
    for name in ("ratio", "raw", "guidance", "seasonal", "last"):
        ae = [r["ae"] for r in hold if r["model"] == name]
        assert len(ae) == 26
        assert h["mae"][name] == pytest.approx(sum(ae) / 26, abs=1e-12)
    # the sign test against a baseline counts the quarters where the ratio estimate was strictly closer
    for b in ("guidance", "seasonal", "last"):
        a = {r["quarter"]: r["ae"] for r in hold if r["model"] == "ratio"}
        o = {r["quarter"]: r["ae"] for r in hold if r["model"] == b}
        assert h["tests"][b]["wins"] == sum(1 for q in a if a[q] < o[q])
        assert h["tests"][b]["losses"] == sum(1 for q in a if a[q] > o[q])
    assert h["band"]["hits"] == sum(1 for r in h["band"]["by_quarter"] if r["hit"])
