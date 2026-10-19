"""Every claim's quote is in its cached source (§3.9). Skips when the cache is absent, as in a clone."""
import json

import pytest

from conftest import ROOT
from gdn import claims


def test_claims_quotes_are_in_their_sources():
    path = ROOT / "report/claims.json"
    if not path.exists():
        pytest.skip("no claims registry yet")
    cl = json.loads(path.read_text())
    if not (ROOT / "data/raw/sources").exists():
        pytest.skip("source cache absent, as in a clone")
    assert claims.problems(cl, claims.source_index(ROOT)) == []


def test_claims_shape_without_the_cache():
    path = ROOT / "report/claims.json"
    if not path.exists():
        pytest.skip("no claims registry yet")
    for c in json.loads(path.read_text()):
        assert list(c) == claims.KEYS
        assert c["source_type"] in claims.TYPES
        assert len(c["quote"].split()) <= 40 and len(c["sha256"]) == 64


def test_a_wrong_quote_is_caught(tmp_path):
    src = tmp_path / "data/raw/sources/x/page.html"
    src.parent.mkdir(parents=True)
    src.write_text("<p>Gulfstream delivered 41 aircraft.</p>")
    sha = claims.sha256(src.read_bytes())
    good = {"id": "t", "text": "t", "source_type": "press", "url_or_accn": "u",
            "quote": "Gulfstream delivered 41 aircraft.", "retrieved_on": "2026-10-19", "sha256": sha}
    idx = claims.source_index(tmp_path)
    assert claims.problems([good], idx) == []
    assert claims.problems([dict(good, quote="Gulfstream delivered 42 aircraft.")], idx)
