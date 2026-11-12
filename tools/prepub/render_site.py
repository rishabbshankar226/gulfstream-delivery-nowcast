"""Render site/ in headless Chromium and dump every text block with its label, as app.js draws it.

Usage: .venv/bin/python tools/prepub/render_site.py <repo root> <out.json>

Each item: {"id": nearest element id, "kind": p|li|h|dt|cell|title|meta, "label": row and column header for a
table cell or the dt for a dd, "text": the text}. Run with the project's venv, which has Playwright."""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

JS = r"""
() => {
  const out = [];
  const near = (e) => { while (e) { if (e.id) return e.id; e = e.parentElement; } return ""; };
  const sect = (e) => { const s = e.closest("section"); const h = s && s.querySelector("h2"); return h ? h.textContent.trim() : ""; };
  out.push({id: "title", kind: "title", label: "", section: "", text: document.title});
  const md = document.querySelector('meta[name="description"]');
  if (md) out.push({id: "meta-description", kind: "meta", label: "", section: "", text: md.content});
  document.querySelectorAll("header p, header h1, main p, main li, main h2, main h3, main summary, footer p, noscript p").forEach((e) => {
    if (e.closest("table")) return;
    const t = (e.innerText || e.textContent).replace(/\s+/g, " ").trim();
    if (t) out.push({id: near(e), kind: e.tagName.toLowerCase(), label: "", section: sect(e), text: t});
  });
  document.querySelectorAll("dl").forEach((dl) => {
    let dt = "";
    dl.querySelectorAll("dt, dd").forEach((e) => {
      if (e.tagName === "DT") dt = e.textContent.trim();
      else out.push({id: near(e), kind: "dd", label: dt, section: sect(e), text: e.textContent.replace(/\s+/g, " ").trim()});
    });
  });
  document.querySelectorAll("table").forEach((tb) => {
    const cap = tb.querySelector("caption");
    const head = Array.from(tb.querySelectorAll("thead th")).map((th) => th.textContent.trim());
    tb.querySelectorAll("tbody tr").forEach((tr) => {
      const cells = Array.from(tr.children).map((c) => c.textContent.replace(/\s+/g, " ").trim());
      cells.forEach((c, i) => {
        if (i === 0) return;
        out.push({id: tb.id, kind: "cell", label: cells[0] + " | " + (head[i] || ""), section: sect(tb),
                  caption: cap ? cap.textContent.trim() : "", text: c});
      });
    });
  });
  document.querySelectorAll("canvas").forEach((c) => {
    out.push({id: c.id, kind: "aria", label: "", section: sect(c), text: c.getAttribute("aria-label") || ""});
  });
  return out;
}
"""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def render(root):
    site = Path(root) / "site"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_context(viewport={"width": 1280, "height": 900}).new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{server.server_address[1]}/")
            page.wait_for_selector("html.ready")
            items = page.evaluate(JS)
            # what the first screen shows at 1280 x 900: every block whose top edge is above the fold
            first = page.evaluate("""() => Array.from(document.querySelectorAll('header *, main *')).filter(e =>
                e.children.length === 0 && e.textContent.trim() && e.getBoundingClientRect().top < 900 &&
                e.getBoundingClientRect().height > 0).map(e => e.textContent.replace(/\\s+/g, ' ').trim())""")
            b.close()
    finally:
        server.shutdown()
    return {"items": items, "first_screen": first, "errors": errors}


if __name__ == "__main__":
    out = render(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(out['items'])} items, {len(out['first_screen'])} first-screen blocks, {len(out['errors'])} page errors")
