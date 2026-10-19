"""The registry rules of §3.3 on hand-built FAA text (tests/fixtures/faa)."""
import gzip
import socket

import pytest

from gdn import events, faa
from gdn.fiscal import Calendar


def by_key(rows):
    return {(r["mfr_code"], r["serial"]): r for r in rows}


def test_network_is_blocked():
    with pytest.raises(RuntimeError):
        socket.create_connection(("example.com", 80), timeout=1)


def test_header_normalization():
    assert faa.norm_header("﻿MFR MDL CODE") == "MFRMDLCODE"
    assert faa.norm_header("MFR-MDL-CODE") == "MFRMDLCODE"
    assert faa.norm_header("air worth date") == "AIRWORTHDATE"
    assert faa.norm_header(" KIT MODEL") == "KITMODEL"


def test_headers_read_by_name_in_any_order(faa_texts):
    faa.check_columns(faa_texts)
    d = faa.read_table(faa_texts["DEREG"], "DEREG")
    assert d[1]["EXPCOUNTRY"] == "QA" and d[1]["CANCELDATE"] == "2024-06-30"


def test_missing_column_is_named(faa_texts):
    broken = dict(faa_texts, MASTER=faa_texts["MASTER"].replace("CERT ISSUE DATE", "ISSUED ON      ", 1))
    with pytest.raises(faa.MissingColumn, match="CERTISSUEDATE"):
        faa.check_columns(broken)


def test_comma_inside_a_name_falls_back_to_header_positions(faa_texts):
    rows = faa.read_table(faa_texts["MASTER"], "MASTER")
    sky = [r for r in rows if r["NNUMBER"] == "N700AA"][0]
    assert sky["NAME"] == "SKY JETS, INC"
    assert sky["CERTISSUEDATE"] == "20240515" and sky["AIRWORTHDATE"] == "20240301"


def test_blank_lines_are_skipped(faa_texts):
    rows = faa.read_table(faa_texts["MASTER"], "MASTER")
    assert len(rows) == 8 and all(r["NNUMBER"] for r in rows)


def test_scope_keeps_iai_g280_and_drops_turboprop_piston_and_cessna(faa_texts):
    s = faa.scope(faa.read_table(faa_texts["ACFTREF"], "ACFTREF"))
    assert set(s) == {"3980221", "4500314", "3980209"}
    assert s["4500314"]["cabin"] == "mid"      # IAI LTD, model GULFSTREAM G280
    assert s["3980209"]["cabin"] == "mid"      # G150 by model name
    assert s["3980221"]["cabin"] == "large"


def test_date_rule():
    assert faa.parse_date("20240515") == "2024-05-15"
    assert faa.parse_date("2024/05/15") == "2024-05-15"
    assert faa.parse_date("2024-05-15") == "2024-05-15"
    assert faa.parse_date("2024/05-15") is None
    assert faa.parse_date("20240231") is None
    assert faa.parse_date("2024515") is None
    assert faa.parse_date("") is None and faa.parse_date("        ") is None


def test_subset_is_header_plus_in_scope_rows_byte_for_byte(faa_texts):
    sub = faa.subset(faa_texts)
    m = sub["MASTER"].splitlines(keepends=True)
    src = faa_texts["MASTER"].splitlines(keepends=True)
    assert m[0] == src[0] and m[0].startswith("﻿") and m[0].endswith("\r\n")
    assert all(ln in src for ln in m)
    assert [ln.split(",")[0].strip() for ln in m[1:]] == ["N700AA", "N280ZZ", "N703GD", "N280RN", "N704GA", "N999ZZ"]
    assert len(sub["ACFTREF"].splitlines()) == 4
    assert len(sub["DEREG"].splitlines()) == 7


def test_subset_gzip_is_deterministic(faa_texts, tmp_path):
    sub = faa.subset(faa_texts)
    z = tmp_path / "ReleasableAircraft-2030-01-01.zip"
    z.write_bytes(b"PK\x05\x06" + b"\0" * 18)
    a = faa.store_subset(tmp_path, "2030-01-01", sub, z, backtest=True)
    b = faa.store_subset(tmp_path, "2030-01-01", sub, z, backtest=True)
    assert a == b
    back = faa.read_subset(tmp_path, "2030-01-01")
    assert back == sub
    raw = (tmp_path / "data/snapshots/2030-01-01/MASTER.txt.gz").read_bytes()
    assert gzip.decompress(raw) == sub["MASTER"].encode("utf-8")


def test_airframes(faa_texts):
    rows = by_key(events.airframes(faa.subset(faa_texts)))
    assert set(rows) == {("398", "75001"), ("398", "75002"), ("398", "75003"), ("398", "75004"),
                         ("450", "2101"), ("450", "2050")}       # blank serial and out-of-scope rows dropped
    a = rows[("398", "75001")]            # domestic sale: customer certificate after Gulfstream cancels its test N-number
    assert (a["customer_cert"], a["gulfstream_cancel"], a["e1"], a["e2"]) == ("2024-05-15", "2024-03-31",
                                                                            "2024-05-15", "2024-03-31")
    assert a["bound"] == "2025-03-01" and a["held_by_gulfstream"] == 0
    b = rows[("398", "75002")]            # export: E1 reads the export cancel, E2 the earlier test cancel
    assert (b["export_cancel"], b["export_country"], b["gulfstream_cancel"]) == ("2024-06-30", "QA", "2024-06-10")
    assert (b["e1"], b["e2"]) == ("2024-06-30", "2024-06-10")
    c = rows[("450", "2101")]             # trade-in: the 2023 return to Gulfstream adds no event
    assert (c["customer_cert"], c["e1"], c["e2"], c["held_by_gulfstream"]) == ("2017-02-01", "2017-02-01",
                                                                              "2017-01-25", 1)
    assert c["model"] == "GULFSTREAM G280" and c["cabin"] == "mid"
    d = rows[("398", "75003")]            # N-number move: E2 fires, E1 does not
    assert (d["e1"], d["e2"], d["held_by_gulfstream"]) == (None, "2025-01-05", 1)


def test_bound_drops_a_renewed_certificate(faa_texts):
    e = by_key(events.airframes(faa.subset(faa_texts)))[("450", "2050")]
    assert e["customer_cert"] == "2024-03-01" and e["bound"] == "2017-03-01"
    assert e["e1"] is None and e["e2"] is None


def test_bound_from_year_when_no_airworthiness(faa_texts):
    g = by_key(events.airframes(faa.subset(faa_texts)))[("398", "75004")]
    assert g["first_airworthiness"] is None and g["year_mfr"] == "2026" and g["bound"] == "2027-12-31"


def test_pipeline_counts_held_airframes_with_no_event(faa_texts):
    assert events.pipeline(events.airframes(faa.subset(faa_texts))) == {"GVIII-G700": 1}


def test_window_edges(faa_texts):
    rows = events.airframes(faa.subset(faa_texts))
    cal = Calendar({"2024Q1": "2024-03-31", "2024Q2": "2024-06-30", "2023Q4": "2023-12-31"})
    q = {r["quarter"]: r for r in events.quarterly(rows, ["2024Q1", "2024Q2"], cal)}
    # E2 on 2024-03-31 (the 2024Q1 end) counts in 2024Q1, not 2024Q2; E1 on 2024-06-30 counts in 2024Q2.
    assert q["2024Q1"]["e2_large"] == 1 and q["2024Q1"]["e1_large"] == 0
    assert q["2024Q2"]["e1_large"] == 2 and q["2024Q2"]["e2_large"] == 1
    assert q["2024Q2"]["window_start"] == "2024-03-31" and q["2024Q2"]["window_end"] == "2024-06-30"


def test_serials_csv_has_lf_and_blank_dates(faa_texts):
    text = events.serials_text(events.airframes(faa.subset(faa_texts)))
    assert "\r" not in text
    assert text.splitlines()[0] == ",".join(events.SERIAL_COLS)
