"""Link check (P3.4): every link on the public surface, whether it resolves now, and whether it will only after
the repository is public and Pages is on.

    ~/gdn-prepub/venv/bin/python tools/prepub/links.py --root . --out docs/prepub/LINKS.csv

Extractors: Markdown links and bare URLs (.md), href and src attributes (.html), URL string literals in
site/app.js, link annotations in the PDF (pypdf), hyperlinks and URL text in the workbook (openpyxl), the url
columns of data/guidance.csv and docs/build/AIRFRAME_AUDIT.csv, and url_or_accn in report/claims.json.

A link passes only when the page's status is 200 AND its title and body do not read as a not-found page. A
status-only check would pass a page that answers 200 with "page not found" in it.
sec.gov is fetched with the declared user agent from ~/.sec_ua (never printed); every other host gets a generic one.
"""
import argparse
import csv
import html
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = "https://github.com/rishabbshankar226/gulfstream-delivery-nowcast"
PAGES = "https://rishabbshankar226.github.io/gulfstream-delivery-nowcast"
GENERIC_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
NOT_FOUND = re.compile(r"\b(page not found|not found|404|does(n't| not) exist|no longer available|can(no|')t (be found|find)"
                       r"|couldn(')?t find|no matching|nothing here|page (is )?(missing|unavailable)|we can't seem to find"
                       r"|unknown aircraft|add aircraft)\b", re.I)
CHALLENGE = re.compile(r"client challenge|just a moment|attention required|access denied|are you a robot|captcha|"
                       r"verify you are human|pardon our interruption", re.I)
URL_RE = re.compile(r"https?://[^\s<>\"'`)\]]+")
MD_FILES = ["docs/LINKEDIN_POST.md", "README.md", "docs/INTERVIEW_NOTES.md", "docs/RESUME_BULLETS.md",
            "docs/PREREGISTRATION.md", "results/error_analysis.md", "results/exploratory/asof.md"]
HTML_FILES = ["site/index.html", "report/note.html"]


def clean(u):
    return u.rstrip(".,;:")


def extract(root, extra_md=()):
    """[(source file, link, kind)]"""
    root = Path(root)
    out = []
    for rel in list(MD_FILES) + list(extra_md):
        p = root / rel
        if not p.exists():
            continue
        t = p.read_text()
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", t):
            out.append((rel, m.group(1), "markdown link"))
        linked = {m.group(1) for m in re.finditer(r"\]\(([^)\s]+)\)", t)}
        for m in URL_RE.finditer(t):
            u = clean(m.group(0))
            if u not in linked:
                out.append((rel, u, "bare URL"))
    for rel in HTML_FILES:
        p = root / rel
        if not p.exists():
            continue
        t = p.read_text()
        for m in re.finditer(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", t):
            out.append((rel, html.unescape(m.group(1)), "href/src"))
        for m in re.finditer(r"url\(([^)]+)\)", t):
            out.append((rel, m.group(1).strip("\"'"), "css url"))
        attr = {html.unescape(m.group(1)) for m in re.finditer(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", t)}
        for m in URL_RE.finditer(re.sub(r"<[^>]+>", " ", t)):
            u = clean(html.unescape(m.group(0)))
            if u not in attr:
                out.append((rel, u, "URL in text"))
    for rel in ("site/app.js", "site/style.css"):
        p = root / rel
        if p.exists():
            t = p.read_text()
            for m in URL_RE.finditer(t):
                out.append((rel, clean(m.group(0)), "URL literal"))
            for m in re.finditer(r"""fetch\(\s*["']([^"']+)["']""", t):
                out.append((rel, m.group(1), "fetch"))
            for m in re.finditer(r"url\(([^)]+)\)", t):
                out.append((rel, m.group(1).strip("\"'"), "css url"))
    pdf = root / "output/GD_research_note.pdf"
    if pdf.exists():
        import pypdf
        r = pypdf.PdfReader(str(pdf))
        for n, page in enumerate(r.pages):
            for a in page.get("/Annots") or []:
                a = a.get_object()
                act = a.get("/A")
                if act and act.get("/URI"):
                    out.append((f"output/GD_research_note.pdf:p{n + 1}", str(act["/URI"]), "pdf annotation"))
    wbp = root / "output/gd_gulfstream_model.xlsx"
    if wbp.exists():
        import openpyxl
        wb = openpyxl.load_workbook(wbp)
        for ws in wb:
            for row in ws.iter_rows():
                for c in row:
                    if c.hyperlink and c.hyperlink.target:
                        out.append((f"workbook:{ws.title}!{c.coordinate}", c.hyperlink.target, "hyperlink"))
                    if isinstance(c.value, str):
                        for m in URL_RE.finditer(c.value):
                            out.append((f"workbook:{ws.title}!{c.coordinate}", clean(m.group(0)), "URL in cell"))
    for rel, col in (("data/guidance.csv", "url"), ("docs/build/AIRFRAME_AUDIT.csv", "source_url")):
        p = root / rel
        if p.exists():
            for n, r in enumerate(csv.DictReader(p.open()), start=2):
                if r.get(col):
                    out.append((f"{rel}:{n}", r[col], "csv url"))
    cj = root / "report/claims.json"
    if cj.exists():
        for c in json.loads(cj.read_text()):
            u = c.get("url_or_accn", "")
            if u.startswith("http"):
                out.append((f"report/claims.json:{c['id']}", u, "claim source"))
            elif re.fullmatch(r"\d{10}-\d{2}-\d{6}", u):
                out.append((f"report/claims.json:{c['id']}",
                            f"https://www.sec.gov/Archives/edgar/data/40533/{u.replace('-', '')}/", "claim accession"))
    return out


def fetch(url, sec_ua, _hops=0):
    host = urllib.parse.urlsplit(url).netloc.lower()
    ua = sec_ua if host.endswith("sec.gov") else GENERIC_UA
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                                               "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context()) as r:
            body = r.read(400000)
            return r.status, r.geturl(), r.headers.get("Content-Type", ""), body
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location") if e.headers else None
        if e.code in (301, 302, 303, 307, 308) and loc and _hops < 4:   # older Pythons do not follow a 308
            return fetch(urllib.parse.urljoin(url, loc), sec_ua, _hops + 1)
        try:
            body = e.read(200000)
        except Exception:  # noqa: BLE001
            body = b""
        return e.code, url, e.headers.get("Content-Type", "") if e.headers else "", body
    except Exception as e:  # noqa: BLE001
        return f"error: {type(e).__name__}: {str(e)[:80]}", url, "", b""


def judge(status, ctype, body):
    """(verdict, title). A 200 passes only when the title and the top of the body do not read as not-found."""
    if status != 200:
        return f"fails: status {status}", ""
    if "html" not in ctype.lower():
        return "resolves", f"({ctype.split(';')[0]}, {len(body)} bytes read)"
    text = body.decode("utf-8", errors="replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    title = html.unescape(" ".join(m.group(1).split())) if m else ""
    vis = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    h1 = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", x)) for x in re.findall(r"<h1[^>]*>(.*?)</h1>", vis, re.S | re.I))
    vis = html.unescape(" ".join(re.sub(r"<[^>]+>", " ", vis).split()))
    if CHALLENGE.search(title):
        return "blocked: 200 with a bot challenge page (check by hand)", title[:120]
    if NOT_FOUND.search(title) or NOT_FOUND.search(h1):
        return "fails: 200 with a not-found title or heading", title[:120]
    if len(vis) < 400 and NOT_FOUND.search(vis):
        return "fails: 200 with a not-found body", title[:120]
    return "resolves", title[:120]


def local(root, src, link):
    """An in-repo relative link, resolved against the file that holds it."""
    root = Path(root)
    base = Path(src.split(":")[0]).parent if not src.startswith("workbook") else Path(".")
    target, _, frag = link.partition("#")
    p = (root / base / target).resolve() if target else (root / src.split(":")[0])
    if not p.exists():
        return "fails: no such file in the tree"
    if frag and p.suffix == ".md":
        heads = [re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-")
                 for h in re.findall(r"^#+\s+(.*)$", p.read_text(), re.M)]
        if frag.lower() not in heads:
            return f"fails: no heading for #{frag}"
    return "resolves in the tree"


def after_public(root, url):
    """What a repository or Pages URL will serve once public, checked against the tree."""
    root = Path(root)
    if url.startswith(PAGES):
        rest = url[len(PAGES):].lstrip("/").split("#")[0].split("?")[0]
        p = root / "site" / (rest or "index.html")
        return "will resolve once the repository is public and Pages is on" if p.exists() else "fails: site/ has no such file"
    rest = url[len(REPO):]
    path, _, frag = rest.partition("#")
    if path in ("", "/"):
        if frag:
            heads = [re.sub(r"[^a-z0-9 -]", "", h.lower()).strip().replace(" ", "-")
                     for h in re.findall(r"^#+\s+(.*)$", (root / "README.md").read_text(), re.M)]
            if frag.lower() not in heads:
                return f"fails: README has no heading for #{frag}"
        return "will resolve once the repository is public"
    m = re.match(r"/(?:blob|tree)/main/(.+)$", path)
    if m:
        return "will resolve once the repository is public" if (root / m.group(1)).exists() else "fails: no such file in the tree"
    m = re.match(r"/releases/tag/(.+)$", path)
    if m:
        import subprocess
        r = subprocess.run(["git", "-C", str(root), "tag", "--list", m.group(1)], capture_output=True, text=True)
        return ("will resolve once the repository is public (tag exists locally; the release is confirmed by "
                "gh release view)") if r.stdout.strip() else "fails: no such tag"
    return "unknown repository path: check by hand"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="docs/prepub/LINKS.csv")
    ap.add_argument("--extra-md", default="")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--only-src", default="", help="keep only links whose source starts with this (for the plant test)")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    sec_ua = (Path.home() / ".sec_ua").read_text().strip()
    links = extract(root, [x for x in a.extra_md.split(",") if x])
    if a.only_src:
        links = [x for x in links if x[0].startswith(a.only_src)]
    seen, rows = {}, []
    for src, link, kind in links:
        if link.startswith(("mailto:", "data:", "javascript:")) or link.startswith("#") and not src.endswith(".md"):
            continue
        if link.startswith("http"):
            url = link
            if url.startswith(REPO) or url.startswith(PAGES):
                now = seen.get(url)
                if now is None and not a.no_fetch:
                    st, final, ctype, body = fetch(url, sec_ua)
                    now = seen[url] = (f"status {st}", "")
                    time.sleep(0.2)
                rows.append([src, link, kind, "own repository or Pages", (now or ("not fetched", ""))[0],
                             after_public(root, url), ""])
                continue
            if url not in seen and not a.no_fetch:
                st, final, ctype, body = fetch(url.replace("https://sec.gov/", "https://www.sec.gov/"), sec_ua)
                verdict, title = judge(st, ctype, body)
                seen[url] = (verdict, title)
                time.sleep(0.25)
            verdict, title = seen.get(url, ("not fetched", ""))
            rows.append([src, link, kind, "external", verdict, "same", title])
        else:
            rows.append([src, link, kind, "in-repo relative", local(root, src, link), "same (also on GitHub once public)", ""])
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        f.write("# Link check. Extraction and fetch: ~/gdn-prepub/venv/bin/python tools/prepub/links.py "
                f"--root {a.root} --out {a.out}\n")
        f.write("# Extractors: Markdown links and bare URLs; href, src and css url() in HTML; URL literals and fetch() in "
                "site/app.js and style.css; PDF link annotations (pypdf); workbook hyperlinks and URL text (openpyxl); "
                "url columns of data/guidance.csv and docs/build/AIRFRAME_AUDIT.csv; report/claims.json sources.\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["source", "link", "kind", "class", "now", "after_public", "title_or_note"])
        w.writerows(rows)
    tally = {}
    for r in rows:
        k = (r[3], r[4].split(":")[0] if r[4].startswith("fails") else r[4].split(" (")[0])
        tally[k] = tally.get(k, 0) + 1
    for k in sorted(tally):
        print(k, tally[k])
    print("rows", len(rows), "distinct fetched", len(seen))


if __name__ == "__main__":
    main()
