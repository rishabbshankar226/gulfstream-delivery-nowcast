"""report/claims.json: the claims registry (§3.9) and the check of each quote against its cached source.

A claim's cached source is the file under data/raw/sources/ whose sha256 is the claim's sha256. The
cache stays out of git, so a clone cannot check quotes; the test skips there."""
import html
import json
import re
from pathlib import Path

from .files import sha256, write_text

KEYS = ["id", "text", "source_type", "url_or_accn", "quote", "retrieved_on", "sha256"]
TYPES = {"filing", "call", "faa", "press"}


def page_text(path):
    t = Path(path).read_bytes().decode("utf-8", errors="replace")
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def source_index(root="."):
    """{sha256: path} for every cached source file."""
    out = {}
    base = Path(root) / "data/raw/sources"
    for p in sorted(base.rglob("*")):
        if p.is_file():
            out.setdefault(sha256(p.read_bytes()), p)
    return out


def problems(claims, index):
    """[(id, reason)] for claims whose shape or quote fails."""
    bad = []
    seen = set()
    for c in claims:
        cid = c.get("id")
        if list(c) != KEYS:
            bad.append((cid, f"keys {list(c)}"))
        if cid in seen:
            bad.append((cid, "duplicate id"))
        seen.add(cid)
        if c.get("source_type") not in TYPES:
            bad.append((cid, f"source_type {c.get('source_type')}"))
        if len(norm(c.get("quote", "")).split()) > 40:
            bad.append((cid, "quote over 40 words"))
        p = index.get(c.get("sha256"))
        if p is None:
            bad.append((cid, "no cached source with this sha256"))
        elif norm(c["quote"]) not in page_text(p):
            bad.append((cid, f"quote not in {p.name}"))
    return bad


def build(paths, root="."):
    """Merge topic files into report/claims.json, keeping only claims that pass."""
    root = Path(root)
    index = source_index(root)
    out, seen = [], set()
    for f in paths:
        for c in json.loads(Path(f).read_text()):
            if sorted(c) != sorted(KEYS):
                print(f"dropped {c.get('id')}: keys {list(c)}")
                continue
            c = {k: (norm(c[k]) if k in ("text", "quote") else c[k]) for k in KEYS}
            # problems() sees one claim at a time here, so the repeated id is caught across files instead.
            b = [(c["id"], "duplicate id")] if c["id"] in seen else problems([c], index)
            if b:
                print(f"dropped {c['id']}: {b[0][1]}")
                continue
            seen.add(c["id"])
            out.append(c)
    out.sort(key=lambda c: c["id"])
    write_text(root / "report/claims.json", json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"report/claims.json: {len(out)} claims")
    return out


def run(root="."):
    """`make claims`: merge every docs/build/claims_*.json topic file."""
    build(sorted((Path(root) / "docs/build").glob("claims_*.json")), root)
    return 0


def load(root="."):
    p = Path(root) / "report/claims.json"
    return json.loads(p.read_text()) if p.exists() else []
