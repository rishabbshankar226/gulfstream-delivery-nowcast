"""Merge the checkers' files into data/guidance.csv (§3.4), after each quote is re-found in its cached page.

Usage: python tools/build_guidance.py docs/build/guidance_check_1.csv docs/build/guidance_check_2.csv ...
"""
import csv
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLS = ["call_date", "year", "outlook", "quote", "speaker", "url"]


def page_text(p):
    t = p.read_text(errors="replace")
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


def main(paths):
    rows = []
    for f in paths:
        for r in csv.DictReader(open(f, newline="")):
            q = re.sub(r"\s+", " ", r["quote"]).strip()
            page = ROOT / "data/raw/sources/calls" / Path(r["cached_file"].strip()).with_suffix(".html").name
            if q and not (page.exists() and q in page_text(page)):
                sys.exit(f"{r['call_date']}: quote not found in {page.name}")
            out = r["outlook"].strip()
            rows.append({"call_date": r["call_date"].strip(), "year": int(r["year"]),
                         "outlook": repr(float(out)).removesuffix(".0") if out else "", "quote": q,
                         "speaker": r["speaker"].strip(), "url": r["url"].strip()})
    rows.sort(key=lambda r: r["call_date"])
    with open(ROOT / "data/guidance.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"data/guidance.csv: {len(rows)} calls, {sum(1 for r in rows if r['outlook'])} with an outlook")


if __name__ == "__main__":
    main(sys.argv[1:])
