"""The dashboard in a real browser: axe-core at 1280 and 390 px, light and dark, plus layout and wording checks.

site/ is served from a local server and loaded in Playwright's headless Chromium. axe-core is
vendored in tests/vendor, so the check needs no network. Without Playwright or its Chromium the
module skips, as the backlog project's does.
"""
import functools
import http.server
import json
import re
import threading
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AXE = (ROOT / "tests" / "vendor" / "axe.min.js").read_text()
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
SIZES = [(1280, 900), (390, 844)]
SCHEMES = ["light", "dark"]


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def base_url():
    handler = functools.partial(_Quiet, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # browser binaries not installed
            pytest.skip(f"Chromium not available: {e}")
        yield b
        b.close()


def open_page(browser, base_url, width, height, scheme):
    ctx = browser.new_context(viewport={"width": width, "height": height})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.emulate_media(color_scheme=scheme, reduced_motion="reduce")
    page.goto(base_url)
    page.wait_for_selector("html.ready")
    page.errors = errors
    return page


def axe(page):
    page.add_script_tag(content=AXE)
    result = page.evaluate("tags => axe.run(document, { runOnly: { type: 'tag', values: tags } })", TAGS)
    return [f"{v['id']}: {v['help']} -> " + ", ".join(n["target"][0] for n in v["nodes"][:4])
            for v in result["violations"]]


@pytest.mark.parametrize("scheme", SCHEMES)
@pytest.mark.parametrize("size", SIZES, ids=["1280", "390"])
def test_axe_and_layout(browser, base_url, size, scheme):
    page = open_page(browser, base_url, *size, scheme)
    assert page.errors == []
    # Open every figures table so axe checks them too.
    page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
    assert axe(page) == []
    over = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert over <= 0, f"{over}px of sideways scroll at {size[0]}px"
    page.context.close()


def test_every_chart_has_a_label_and_a_table(browser, base_url):
    page = open_page(browser, base_url, 1280, 900, "light")
    for cid, tid in (("c-path", "t-path"), ("c-track", "t-track"), ("c-pipe", "t-pipe")):
        assert page.get_attribute(f"#{cid}", "role") == "img"
        assert len(page.get_attribute(f"#{cid}", "aria-label")) > 40
        assert page.locator(f"#{tid} tbody tr").count() > 0
    page.context.close()


def test_page_wording(browser, base_url):
    page = open_page(browser, base_url, 1280, 900, "light")
    text = page.inner_text("body")
    for word in ("MAE", "nowcast", "backtest"):
        assert not re.search(rf"\b{word}\b", text, re.I), word
    data = json.loads((SITE / "data.json").read_text())
    h = data["metrics"]["holdout"]
    lead = page.inner_text("#lead")
    assert f"{h['mae']['ratio']:.1f}" in lead
    rejects = any(h["tests"][b]["holm_reject"] and h["rel_mae"][b] < 1 for b in ("guidance", "seasonal", "last"))
    assert ("not statistically distinguishable" in lead) == (not rejects)
    assert ("beat" in lead.lower()) == rejects
    page.context.close()


def test_static_html_holds_no_figures():
    html = (SITE / "index.html").read_text()
    body = re.sub(r"(?s)<head>.*?</head>", "", html)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    body = re.sub(r"\b\d{4}Q[1-4]\b", " ", body)
    assert re.findall(r"\d+(?:\.\d+)?", body) == ["26"]


def test_site_under_900_kb():
    total = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file() and p.suffix != ".pdf")
    assert total < 900 * 1024, total


def test_failed_data_shows_a_linked_error(browser, base_url):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.route("**/data.json", lambda route: route.fulfill(status=404, body="missing"))
    page.goto(base_url)
    page.wait_for_selector("#error:not([hidden])")
    assert "could not load" in page.inner_text("#error")
    assert page.get_attribute("#error a", "href").endswith("#results")
    assert axe(page) == []
    ctx.close()


def test_missing_path_hides_the_path_chart(browser, base_url):
    data = json.loads((SITE / "data.json").read_text())
    data.pop("path", None)
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.route("**/data.json", lambda route: route.fulfill(status=200, content_type="application/json",
                                                          body=json.dumps(data)))
    page.goto(base_url)
    page.wait_for_selector("html.ready")
    assert page.is_hidden("#c-path")
    ctx.close()


def _live_page(browser, base_url, data):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.route("**/data.json", lambda route: route.fulfill(status=200, content_type="application/json",
                                                          body=json.dumps(data)))
    page.goto(base_url)
    page.wait_for_selector("html.ready")
    return page


def _next_quarter(L):
    q4 = json.loads(json.dumps(L))
    q4.update({"quarter": "2026Q4", "build": None, "locked": None, "lock": None, "score": None,
               "guidance_pace": None, "release_date": None})
    q4["latest"]["quarter"] = "2026Q4"
    return q4


def test_a_scored_quarter_stays_featured_after_the_next_one_starts(browser, base_url):
    # On the score day the same run writes 2026Q4's first files; the page must still show 2026Q3's result.
    data = json.loads((SITE / "data.json").read_text())
    q3 = data["live"][-1]
    pred = q3["latest"] or q3["build"]
    q3["locked"] = pred
    q3["lock"] = {"tag": "lock-2026Q3", "published_at": "2026-10-29T23:20:00Z", "sha256": "0" * 64, "commit": "0" * 40}
    q3["score"] = {"quarter": "2026Q3", "reported": {"large": 30, "mid": 5, "total": 35}, "accn": "0000040533-26-000040",
                   "locked": True, "nowcast": pred["nowcast"], "ae_total": abs(pred["nowcast"]["total"] - 35),
                   "ape_pct": abs(pred["nowcast"]["total"] - 35) / 35 * 100, "inside_band": True,
                   "guidance_pace": None, "guidance_ae": None}
    data["live"].append(_next_quarter(q3))
    data.setdefault("path", {})["2026Q4"] = data.get("path", {}).get("2026Q3", [])
    page = _live_page(browser, base_url, data)
    assert page.inner_text("#live-status").startswith("2026Q3")
    assert "Scored" in page.text_content("#live-status")
    assert "GD reported" in page.inner_text("#live-facts")
    page.context.close()


def test_without_a_lock_or_score_the_newest_quarter_is_featured(browser, base_url):
    data = json.loads((SITE / "data.json").read_text())
    data["live"].append(_next_quarter(data["live"][-1]))
    page = _live_page(browser, base_url, data)
    assert page.inner_text("#live-status").startswith("2026Q4")
    page.context.close()
