"""Release parsing and filing selection (§3.2, §3.7) on synthetic release text."""
import pytest

from conftest import FIXTURES
from gdn import sec


def text(name):
    return sec.plain((FIXTURES / "releases" / name).read_bytes())


def test_release_with_sentence():
    d = sec.parse_deliveries(text("with_sentence.htm"))
    assert (d["large"], d["mid"], d["total"]) == (25, 5, 30)
    assert (d["prior_large"], d["prior_mid"]) == (16, 4)
    assert d["sentence"] == {"total": 30, "large": 25}


def test_release_without_sentence_one_cell_per_line():
    d = sec.parse_deliveries(text("without_sentence.htm"))
    assert (d["large"], d["mid"], d["total"], d["prior_large"], d["prior_mid"]) == (23, 6, 29, 19, 8)
    assert d["sentence"] is None


def test_sentence_must_agree_with_table():
    t = text("with_sentence.htm").replace("of which 25 were", "of which 24 were")
    with pytest.raises(ValueError, match="disagrees"):
        sec.parse_deliveries(t)


def test_exhibit_name():
    assert sec.exhibit_name(["gd-20251024.htm", "gd-20250928exhibit9911.htm", "R1.htm"]) == "gd-20250928exhibit9911.htm"
    assert sec.exhibit_name(["gd-201704028k.htm", "gd20170402exhibit991.htm"]) == "gd20170402exhibit991.htm"
    assert sec.exhibit_name(["gd-20260729.htm", "FilingSummary.xml"]) is None


def test_results_8k_is_first_202_within_70_days():
    fs = [
        {"form": "8-K", "accn": "a", "filed": "2026-07-05", "report": "", "items": "2.02,9.01"},   # on the end: no
        {"form": "8-K", "accn": "b", "filed": "2026-07-20", "report": "", "items": "8.01"},
        {"form": "8-K", "accn": "c", "filed": "2026-07-29", "report": "", "items": "2.02,9.01"},
        {"form": "8-K", "accn": "d", "filed": "2026-08-01", "report": "", "items": "2.02"},
    ]
    assert sec.results_8k(fs, "2026-07-05")["accn"] == "c"
    assert sec.results_8k(fs, "2026-05-15")["accn"] == "a"
    assert sec.results_8k(fs, "2026-04-01") is None


def test_segments_and_backlog():
    seg = """REVENUE AND OPERATING EARNINGS BY SEGMENT - (UNAUDITED)
Revenue:
Aerospace $ 3,000 $ 2,900 $ 100 3.4 %
Marine Systems 4,000 3,900 100 2.6 %
Combat Systems 2,000 2,100 (100) (4.8) %
Technologies 3,500 3,400 100 2.9 %
Total $ 12,500 $ 12,300 $ 200 1.6 %
Operating earnings:
Aerospace $ 400 $ 380 $ 20 5.3 %
Marine Systems 300 280 20 7.1 %
Combat Systems 280 290 (10) (3.4) %
Technologies 330 320 10 3.1 %
Corporate (40) (35) (5) (14.3) %
Total $ 1,270 $ 1,235 $ 35 2.8 %
Operating margin:
Aerospace 13.3 % 13.1 %
"""
    s = sec.parse_segments(seg)
    assert s["Aerospace"] == (3000, 400) and s["Combat Systems"] == (2000, 280)
    bl = """BACKLOG - (UNAUDITED)
Second Quarter 2030:
Aerospace $ 20,000 $ 1,000 $ 21,000 $ 1,100 $ 22,100
Marine Systems 40,000 20,000 60,000 7,000 67,000
Combat Systems 25,000 2,000 27,000 10,000 37,000
Technologies 10,000 6,000 16,000 30,000 46,000
Total $ 95,000 $ 29,000 $ 124,000 $ 48,100 $ 172,100
First Quarter 2030:
Aerospace $ 1 $ 1 $ 2 $ 1 $ 3
"""
    assert sec.parse_backlog(bl, "Second Quarter 2030") == {"Aerospace": 21000, "Marine Systems": 60000,
                                                             "Combat Systems": 27000, "Technologies": 16000}


def test_offline_client_never_fetches(tmp_path):
    c = sec.Client(tmp_path, network=False)
    with pytest.raises(sec.SECUnavailable):
        c.get("https://www.sec.gov/x", "x.htm")


def test_a_dropped_connection_is_sec_unavailable(tmp_path, monkeypatch):
    import http.client

    class Dropped:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            raise http.client.IncompleteRead(b"partial")

    monkeypatch.setattr(sec, "user_agent", lambda: "test test@example.com")
    monkeypatch.setattr(sec.urllib.request, "urlopen", lambda *a, **k: Dropped())
    c = sec.Client(tmp_path, network=True)
    with pytest.raises(sec.SECUnavailable):
        c._fetch("https://www.sec.gov/x")
    assert c.failed
