"""SEC EDGAR access for GD (CIK 40533): submissions, results 8-Ks and their Exhibit 99.1.

Raw files go to data/raw/sec/, out of git; data/sec_manifest.json records each file's
sha256 and byte count. A file is fetched only when missing. After one network failure
the client stops reading SEC for the rest of the run.
"""
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

from .files import read_json, sha256, write_json

CIK = "0000040533"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data/40533/"
SUBMISSIONS = f"https://data.sec.gov/submissions/CIK{CIK}.json"
SUBMISSIONS_PAGE = "https://data.sec.gov/submissions/{name}"


class SECUnavailable(Exception):
    pass


def user_agent():
    ua = os.environ.get("SEC_UA", "").strip()
    if ua:
        return ua
    p = Path.home() / ".sec_ua"
    if p.exists():
        lines = p.read_text().splitlines()
        return lines[0].strip() if lines else ""
    return ""


class Client:
    def __init__(self, root=".", network=True):
        self.root = Path(root)
        self.raw = self.root / "data/raw/sec"
        self.manifest_path = self.root / "data/sec_manifest.json"
        self.manifest = read_json(self.manifest_path) if self.manifest_path.exists() else {}
        self.network = network
        self.failed = False
        self.last = 0.0

    def get(self, url, name, refresh=False):
        p = self.raw / name
        if p.exists() and not refresh:
            data = p.read_bytes()
        else:
            data = self._fetch(url)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        self.manifest[name] = {"sha256": sha256(data), "bytes": len(data)}
        return data

    def _fetch(self, url):
        if not self.network:
            raise SECUnavailable("offline run")
        if self.failed:
            raise SECUnavailable("SEC failed earlier in this run")
        ua = user_agent()
        if not ua:
            raise SECUnavailable("no SEC User-Agent: set SEC_UA or write ~/.sec_ua")
        wait = 0.21 - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except (urllib.error.URLError, OSError, ValueError) as e:
            self.failed = True
            print(f"SEC read failed for {url}: {e}. Not reading SEC again this run.", file=sys.stderr)
            raise SECUnavailable(str(e)) from e
        finally:
            self.last = time.monotonic()

    def save_manifest(self):
        write_json(self.manifest_path, dict(sorted(self.manifest.items())))

    # ---- submissions ----
    def filings(self, refresh=False):
        """Every filing as a dict with form, accn, filed, report and items, oldest pages included."""
        main = json.loads(self.get(SUBMISSIONS, f"submissions/CIK{CIK}.json", refresh=refresh))
        pages = [main["filings"]["recent"]]
        for f in main["filings"].get("files", []):
            pages.append(json.loads(self.get(SUBMISSIONS_PAGE.format(name=f["name"]), f"submissions/{f['name']}")))
        out = {}
        for pg in pages:
            for i, accn in enumerate(pg["accessionNumber"]):
                out[accn] = {"form": pg["form"][i], "accn": accn, "filed": pg["filingDate"][i],
                             "report": pg["reportDate"][i], "items": pg.get("items", [""] * len(pg["form"]))[i] or ""}
        return sorted(out.values(), key=lambda r: (r["filed"], r["accn"]))

    def index(self, accn):
        folder = accn.replace("-", "")
        return json.loads(self.get(f"{ARCHIVE}{folder}/index.json", f"{accn}/index.json"))

    def exhibit_991(self, accn):
        """(file name, bytes) of the earnings release exhibit in the 8-K's folder."""
        name = exhibit_name([it["name"] for it in self.index(accn)["directory"]["item"]])
        if not name:
            raise SECUnavailable(f"no Exhibit 99.1 in {accn}")
        folder = accn.replace("-", "")
        return name, self.get(f"{ARCHIVE}{folder}/{name}", f"{accn}/{name}")


def exhibit_name(names):
    """The Exhibit 99.1 file among a filing folder's names."""
    pat = re.compile(r"ex(hibit)?[-_]?99[-_.]?0?1(?!\d)|ex(hibit)?[-_]?991", re.I)
    hits = sorted(n for n in names if n.lower().endswith((".htm", ".html")) and pat.search(n))
    return hits[0] if hits else None


def results_8k(filings, fiscal_end):
    """The first 8-K carrying item 2.02 filed within 70 days after the fiscal end, or None."""
    lo = dt.date.fromisoformat(fiscal_end)
    hi = lo + dt.timedelta(days=70)
    for f in filings:
        if f["form"] == "8-K" and "2.02" in f["items"].split(",") and lo < dt.date.fromisoformat(f["filed"]) <= hi:
            return f
    return None


def quarter_ends_from_10q(filings):
    """{quarter: fiscal end} for Q1 to Q3 from 10-Q report dates; Q4 is December 31."""
    out = {}
    for f in filings:
        if f["form"] == "10-Q" and f["report"]:
            r = dt.date.fromisoformat(f["report"])
            # GD's Q1 can end in early April, so assign by the nearest calendar quarter end.
            n = min(range(1, 4), key=lambda k: abs((dt.date(r.year, 3 * k, 28) - r).days))
            out[f"{r.year}Q{n}"] = r.isoformat()
    return out


# ---- release text ----
def plain(html_bytes):
    """Visible text of an HTML exhibit, one line per block, whitespace collapsed."""
    t = html_bytes.decode("utf-8", errors="replace")
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|table)>", "\n", t)
    t = re.sub(r"(?i)</t[dh]>", " \t ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = unescape(t).replace("\xa0", " ").replace("​", "")
    lines = []
    for ln in t.split("\n"):
        ln = re.sub(r"[ \t]+", " ", ln).strip()
        if ln:
            lines.append(ln)
    return "\n".join(lines)


SEGMENTS = ("Aerospace", "Marine Systems", "Combat Systems", "Technologies")


def _ints(s):
    out = []
    for m in re.finditer(r"\(?\d[\d,]*(?:\.\d+)?\)?", s):
        v = m.group(0)
        neg = v.startswith("(") and v.endswith(")")
        x = float(v.strip("()").replace(",", ""))
        out.append(-x if neg else x)
    return out


def _until_text(s):
    m = re.search(r"[A-Za-z*]", s)
    return s[:m.start()] if m else s


def parse_deliveries(text):
    """Counts from the "Gulfstream Aircraft Deliveries (units)" table: the quarter's own
    column and the prior-year column, plus the delivery sentence when the release has one."""
    i = text.find("Gulfstream Aircraft Deliveries (units)")
    if i < 0:
        raise ValueError("no Gulfstream Aircraft Deliveries table")
    t = text[i:i + 1500]
    a, b = t.find("Large-cabin aircraft"), t.find("Mid-cabin aircraft")
    c = t.find("Total", b)
    if min(a, b, c) < 0:
        raise ValueError("delivery table rows not found")
    large = _ints(t[a + len("Large-cabin aircraft"):b])
    mid = _ints(t[b + len("Mid-cabin aircraft"):c])
    total = _ints(_until_text(t[c + len("Total"):]))
    if len(large) < 2 or len(mid) < 2 or len(total) < 2:
        raise ValueError(f"short delivery rows {large} {mid} {total}")
    out = {"large": int(large[0]), "mid": int(mid[0]), "total": int(total[0]),
           "prior_large": int(large[1]), "prior_mid": int(mid[1]), "prior_total": int(total[1])}
    for k in ("", "prior_"):
        if out[k + "large"] + out[k + "mid"] != out[k + "total"]:
            raise ValueError(f"table does not add up: {out}")
    m = re.search(r"delivered (\d+) aircraft (?:in|during) the quarter(?:, (?:of which (\d+) were|(\d+) of which were)"
                  r" large[- ]cabin)?", text)
    out["sentence"] = None
    if m:
        out["sentence"] = {"total": int(m[1]), "large": int(m[2] or m[3]) if (m[2] or m[3]) else None}
        if out["sentence"]["total"] != out["total"] or out["sentence"]["large"] not in (None, out["large"]):
            raise ValueError(f"sentence {m.group(0)!r} disagrees with the table {out}")
    return out


def parse_segments(text):
    """{segment: (revenue $M, operating earnings $M)} from the current-quarter column."""
    i = text.find("REVENUE AND OPERATING EARNINGS BY SEGMENT")
    if i < 0:
        raise ValueError("no segment exhibit")
    blk = text[i:i + 3000]
    r, o, m = blk.find("Revenue:"), blk.find("Operating earnings:"), blk.find("Operating margin:")
    if min(r, o, m) < 0:
        raise ValueError("segment blocks not found")
    out = {}
    for name, part in (("revenue", blk[r:o]), ("oe", blk[o:m])):
        vals = {}
        for seg in SEGMENTS + ("Total",):
            mm = re.search(rf"^{seg}\s+\$?\s*(\(?[\d,]+\)?)", part, re.M)
            if not mm:
                raise ValueError(f"no {seg} row in {name}")
            vals[seg] = _ints(mm.group(1))[0]
        corp = 0.0
        if name == "oe":
            mm = re.search(r"^Corporate\s+\$?\s*(\(?[\d,]+\)?)", part, re.M)
            corp = _ints(mm.group(1))[0] if mm else 0.0
        if abs(sum(vals[s] for s in SEGMENTS) + corp - vals["Total"]) > 0.5:
            raise ValueError(f"{name} does not add up: {vals}")
        for seg in SEGMENTS:
            out.setdefault(seg, {})[name] = vals[seg]
    return {s: (v["revenue"], v["oe"]) for s, v in out.items()}


def parse_backlog(text, label):
    """{segment: total backlog $M} from the backlog exhibit's block for `label`, e.g. "Second Quarter 2026"."""
    i = text.find("BACKLOG - (UNAUDITED)")
    j = text.find(label + ":", i)
    if i < 0 or j < 0:
        raise ValueError(f"no backlog block {label}")
    k = re.search(r"\n(First|Second|Third|Fourth) Quarter \d{4}:", text[j + len(label) + 1:])
    blk = text[j:j + len(label) + 1 + (k.start() if k else 1500)]
    out = {}
    for seg in SEGMENTS + ("Total",):
        mm = re.search(rf"^{seg}\s+(.*)$", blk, re.M)
        nums = _ints(mm.group(1)) if mm else []
        if len(nums) < 3:
            raise ValueError(f"no backlog row for {seg}")
        out[seg] = nums[2]
    if abs(sum(out[s] for s in SEGMENTS) - out["Total"]) > 0.5:
        raise ValueError(f"backlog does not add up: {out}")
    return {s: out[s] for s in SEGMENTS}


def book_to_bill(text):
    """The orders paragraph's book-to-bill ratios: {"defense", "aerospace", "company"}."""
    m = re.search(r"was ([\d.]+)-to-1 for the quarter for the defense segments, ([\d.]+)-to-1 for the Aerospace "
                  r"segment, and ([\d.]+)-to-1 on a company-wide basis", text)
    return {"defense": float(m[1]), "aerospace": float(m[2]), "company": float(m[3])} if m else None


def probe():
    """One read of GD's submissions index to report whether SEC is reachable; writes nothing."""
    ua = user_agent()
    if not ua:
        return "SEC not probed: no User-Agent"
    req = urllib.request.Request(SUBMISSIONS, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return f"SEC reachable: HTTP {r.status}, {len(r.read())} bytes"
    except urllib.error.HTTPError as e:
        return f"SEC refused: HTTP {e.code}"
    except (urllib.error.URLError, OSError, ValueError) as e:
        return f"SEC unreachable: {e}"
