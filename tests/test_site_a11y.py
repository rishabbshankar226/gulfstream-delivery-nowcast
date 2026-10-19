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
