"""§3.4's models and statistics on hand-computed fixture numbers."""
import pytest

from gdn import events, faa, model, stats
from gdn.fiscal import Calendar


def test_ratio_by_hand():
    # 9 x (10 + 12 + 14 + 16) / (5 + 6 + 7 + 8) = 9 x 52 / 26 = 18
    assert model.ratio(9, [5, 6, 7, 8], [10, 12, 14, 16]) == pytest.approx(18.0)


def test_ratio_zero_rule_uses_trailing_mean():
    assert model.ratio(4, [0, 0, 0, 0], [10, 12, 14, 16]) == pytest.approx(13.0)


def fixture_reported():
    Y = {}
    for y in (2017, 2018, 2019):
        for j, t in zip(range(1, 5), (20, 30, 20, 30)):
            Y[f"{y}Q{j}"] = {"large": t - 5, "mid": 5, "total": t}
    Y["2019Q3"] = {"large": 16, "mid": 4, "total": 20}
    Y["2019Q4"] = {"large": 24, "mid": 6, "total": 30}
    Y["2020Q1"] = {"large": 20, "mid": 5, "total": 25}
    Y["2020Q2"] = {"large": 28, "mid": 7, "total": 35}
    Y["2019Q3"]["total"], Y["2019Q4"]["total"] = 20, 30
    return Y


def test_guidance_by_hand():
    Y = fixture_reported()
    cal = Calendar({"2020Q2": "2020-06-28", "2020Q3": "2020-09-27"})
    calls = [{"call_date": "2020-01-29", "year": 2020, "outlook": 150.0},
             {"call_date": "2020-04-29", "year": 2020, "outlook": 130.0},
             {"call_date": "2020-07-29", "year": 2020, "outlook": None},     # confirms without a number
             {"call_date": "2020-10-28", "year": 2020, "outlook": 999.0}]    # after the fiscal end
    p = model.guidance_pace("2020Q3", Y, calls, cal)
    # w = 0.2, 0.3, 0.2, 0.3; YTD = 25 + 35 = 60; (130 - 60) x 0.2 / 0.5 = 28
    assert p["outlook"] == 130.0 and p["total"] == pytest.approx(28.0)
    # large share over 2020Q2 to 2019Q3: (28 + 20 + 24 + 16) / (35 + 25 + 30 + 20) = 88 / 110 = 0.8
    assert p["large"] == pytest.approx(22.4) and p["mid"] == pytest.approx(5.6)


def test_guidance_falls_back_to_seasonal():
    Y = fixture_reported()
    cal = Calendar({"2020Q3": "2020-09-27"})
    f, sourced = model.guidance_forecast("2020Q3", Y, [{"call_date": "2020-01-29", "year": 2019,
                                                        "outlook": 150.0}], cal)
    assert not sourced and f == {"large": Y["2019Q3"]["large"], "mid": Y["2019Q3"]["mid"]}


def test_guidance_never_negative():
    Y = fixture_reported()
    cal = Calendar({"2020Q3": "2020-09-27"})
    p = model.guidance_pace("2020Q3", Y, [{"call_date": "2020-01-29", "year": 2020, "outlook": 40.0}], cal)
    assert p["total"] == 0.0


def test_nearest_rank_on_26():
    xs = list(range(26, 0, -1))
    assert stats.nearest_rank(xs, 0.1) == 3 and stats.nearest_rank(xs, 0.9) == 24


def test_sign_test_hand_cases():
    assert stats.sign_test([3] * 10, [1] * 9 + [5]) == (9, 1, 0, 11 / 1024)
    assert stats.sign_test([5, 5, 5], [4, 5, 6]) == (1, 1, 1, 0.75)


def test_holm_hand_cases():
    assert stats.holm({"a": 0.01, "b": 0.04, "c": 0.03}) == {"a": True, "b": False, "c": False}
    assert stats.holm({"a": 0.01, "b": 0.02, "c": 0.03}) == {"a": True, "b": True, "c": True}
    assert stats.holm({"a": 0.2, "b": 0.01, "c": 0.5}) == {"a": False, "b": True, "c": False}


def test_clopper_pearson_against_reference_table():
    lo, hi = stats.clopper_pearson(5, 10)
    assert (round(lo, 4), round(hi, 4)) == (0.1871, 0.8129)
    lo, hi = stats.clopper_pearson(21, 26)
    assert (round(lo, 4), round(hi, 4)) == (0.6065, 0.9345)
    assert stats.clopper_pearson(0, 10)[0] == 0.0 and stats.clopper_pearson(10, 10)[1] == 1.0


def test_lag1():
    assert stats.lag1([1, 2]) is None
    assert stats.lag1([1, 2, 3]) == pytest.approx(0.0)
    assert stats.lag1([1, 3, 1, 3]) == pytest.approx(-0.75)


def test_truncation_edge(faa_texts):
    rows = events.airframes(faa.subset(faa_texts))
    lo, hi = "2024-03-31", "2024-06-30"
    # A's E1 is 2024-05-15: 2024-06-30 minus 46 days keeps it, minus 47 days drops it.
    assert events.count(rows, "E1", "large", lo, hi, cutoff="2024-05-15") == 1
    assert events.count(rows, "E1", "large", lo, hi, cutoff="2024-05-14") == 0
