"""The FAA aircraft registry (§3.3): download, read, scope and the stored subset."""
import csv
import datetime as dt
import gzip
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

from .files import read_json, sha256, write_gz, write_json

URL = "https://registry.faa.gov/database/ReleasableAircraft.zip"
REFERER = "https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download"
CHROME_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
CHICAGO = ZoneInfo("America/Chicago")
FILES = ("ACFTREF", "MASTER", "DEREG")

# Normalized header names of the fields §3.3 reads. YEARMFR may be absent.
FIELDS = {
    "ACFTREF": ("CODE", "MFR", "MODEL", "TYPEENG"),
    "MASTER": ("NNUMBER", "SERIALNUMBER", "MFRMDLCODE", "NAME", "CERTISSUEDATE", "AIRWORTHDATE", "YEARMFR"),
    "DEREG": ("NNUMBER", "SERIALNUMBER", "MFRMDLCODE", "NAME", "CERTISSUEDATE", "AIRWORTHDATE", "YEARMFR",
              "CANCELDATE", "EXPCOUNTRY"),
}
OPTIONAL = {"YEARMFR"}
MID = re.compile(r"G280|G150|G200|G100")


class MissingColumn(KeyError):
    pass


# ---------- download ----------
def snapshot_date(now_utc):
    return now_utc.astimezone(CHICAGO).date().isoformat()


def is_zip(p):
    p = Path(p)
    if not p.exists() or p.stat().st_size < 4:
        return False
    with open(p, "rb") as f:
        return f.read(2) == b"PK"


def _curl(dest, max_time):
    cmd = ["curl", "-sSfL", "--max-time", str(max_time), "--retry", "2", "-A", CHROME_UA,
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: en-US,en;q=0.9", "-H", f"Referer: {REFERER}", "-o", str(dest), URL]
    return subprocess.run(cmd, capture_output=True, text=True).returncode


def _chrome(dest, downloads, wait_s=300):
    """Download through the owner's own Chrome, then move the new zip from ~/Downloads."""
    before = {p: p.stat().st_mtime for p in downloads.glob("ReleasableAircraft*.zip")}
    start = time.time()
    subprocess.run(["open", "-g", "-a", "Google Chrome", URL], capture_output=True)
    while time.time() - start < wait_s:
        time.sleep(5)
        for p in sorted(downloads.glob("ReleasableAircraft*.zip")):
            if p in before and p.stat().st_mtime <= before[p]:
                continue
            size = -1
            while size != p.stat().st_size:
                size = p.stat().st_size
                time.sleep(3)
            if is_zip(p):
                shutil.move(str(p), dest)
                return True
    return False


def download(root, now_utc=None, log=print):
    """§3.3's chain. Returns the snapshot date, or None when no new snapshot came."""
    root = Path(root)
    now_utc = now_utc or dt.datetime.now(dt.timezone.utc)
    date = snapshot_date(now_utc)
    out = root / "data/raw/faa" / f"ReleasableAircraft-{date}.zip"
    man = manifest(root)
    if date in ({man.get("backtest")} | locked_dates(root)) and date in man["snapshots"] and is_zip(out):
        # The backtest's subset and a subset a lock read are never replaced by a second download on the
        # same Chicago date. Any other date's second run downloads again and replaces its files (§3.11).
        log(f"FAA snapshot {date} backs the backtest or a lock; keeping it")
        return date
    out.parent.mkdir(parents=True, exist_ok=True)
    part = out.with_suffix(f".{os.getpid()}.part")
    ci = bool(os.environ.get("CI"))
    rc = _curl(part, 120 if ci else 600)
    if rc == 0 and is_zip(part):
        part.replace(out)
        log(f"FAA snapshot {date} by curl, {out.stat().st_size} bytes")
        return date
    part.unlink(missing_ok=True)
    log(f"FAA curl gave no zip (exit {rc})")
    if sys.platform == "darwin" and not ci and shutil.which("open"):
        if _chrome(out, Path.home() / "Downloads"):
            log(f"FAA snapshot {date} through Chrome, {out.stat().st_size} bytes")
            return date
        log("Chrome gave no zip within five minutes")
    log("No new FAA snapshot; carrying on with the newest one stored.")
    return None


# ---------- reading ----------
def norm_header(h):
    return re.sub(r"[^A-Z0-9]", "", h.replace("\ufeff", "").upper())


def parse_date(s):
    """YYYYMMDD, or the same with one separator (/ or -) between both pairs; else None."""
    m = re.fullmatch(r"(\d{4})([/-]?)(\d{2})\2(\d{2})", (s or "").strip())
    if not m:
        return None
    try:
        return dt.date(int(m[1]), int(m[3]), int(m[4])).isoformat()
    except ValueError:
        return None


def zip_texts(zpath):
    """{kind: text} of ACFTREF, MASTER and DEREG, names matched without regard to case."""
    with zipfile.ZipFile(zpath) as z:
        names = {Path(n).stem.upper(): n for n in z.namelist()}
        missing = [k for k in FILES if k not in names]
        if missing:
            raise MissingColumn(f"zip has no {missing}")
        return {k: z.read(names[k]).decode("utf-8", errors="replace") for k in FILES}


def header_of(text):
    lines = text.lstrip("\ufeff").splitlines()
    return [norm_header(h) for h in next(csv.reader([lines[0]]))] if lines else []


def check_columns(texts):
    """Raise MissingColumn naming any field §3.3 needs that a file lacks."""
    for k in FILES:
        hdr = header_of(texts[k])
        miss = [f for f in FIELDS[k] if f not in hdr and f not in OPTIONAL]
        if miss:
            raise MissingColumn(f"{k} has no {miss}; header {hdr}")


def read_table(text, kind):
    """Rows of one FAA file as dicts keyed by normalized header name, cells trimmed.

    Lines split with the csv reader; when that gives a different field count from the
    header's, the line is cut at the header line's comma positions instead."""
    text = text.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines:
        return []
    head = lines[0]
    header = [norm_header(h) for h in next(csv.reader([head]))]
    cuts = [-1] + [i for i, ch in enumerate(head) if ch == ","]
    want = [f for f in FIELDS[kind] if f in header]
    pos = {f: header.index(f) for f in want}
    out = []
    for ln in lines[1:]:
        if not ln.strip(" ,"):
            continue
        row = next(csv.reader([ln]), [])
        if len(row) != len(header):
            row = [ln[cuts[j] + 1:cuts[j + 1]] if j + 1 < len(cuts) else ln[cuts[j] + 1:] for j in range(len(cuts))]
        rec = {f: (row[i].strip() if i < len(row) else "") for f, i in pos.items()}
        for f in FIELDS[kind]:
            rec.setdefault(f, "")
        out.append(rec)
    return out


# ---------- scope ----------
def scope(acftref_rows):
    """{code: {"model", "mfr", "cabin"}} for Gulfstream jets (§3.3 Scope 1 and 2)."""
    out = {}
    for r in acftref_rows:
        mfr, model = r["MFR"].upper(), r["MODEL"].upper()
        if ("GULFSTREAM" in mfr or "GULFSTREAM" in model) and r["TYPEENG"].strip() in ("4", "5"):
            cabin = "mid" if MID.search(model) or mfr.startswith(("IAI", "ISRAEL")) else "large"
            out[r["CODE"]] = {"model": r["MODEL"], "mfr": r["MFR"], "cabin": cabin}
    return out


def _keep(text, field, wanted):
    lines = text.splitlines(keepends=True)
    if not lines:
        return ""
    idx = header_of(text).index(field)
    keep = [lines[0]]
    for ln in lines[1:]:
        cells = next(csv.reader([ln]), [])
        if len(cells) > idx and cells[idx].strip() in wanted:
            keep.append(ln)
    return "".join(keep)


def subset(texts):
    """Each file's header line plus its in-scope rows, in file order."""
    check_columns(texts)
    codes = set(scope(read_table(texts["ACFTREF"], "ACFTREF")))
    return {"ACFTREF": _keep(texts["ACFTREF"], "CODE", codes),
            "MASTER": _keep(texts["MASTER"], "MFRMDLCODE", codes),
            "DEREG": _keep(texts["DEREG"], "MFRMDLCODE", codes)}


# ---------- stored snapshots ----------
def snap_dir(root):
    return Path(root) / "data/snapshots"


def manifest(root):
    p = snap_dir(root) / "MANIFEST.json"
    return read_json(p) if p.exists() else {"backtest": None, "snapshots": {}}


def save_manifest(root, man):
    man = {"backtest": man["backtest"], "snapshots": dict(sorted(man["snapshots"].items()))}
    return write_json(snap_dir(root) / "MANIFEST.json", man)


def read_subset(root, date):
    d = snap_dir(root) / date
    return {k: gzip.decompress((d / f"{k}.txt.gz").read_bytes()).decode("utf-8", errors="replace") for k in FILES}


def store_subset(root, date, sub, zpath, backtest=False):
    """Write data/snapshots/<date>/<FILE>.txt.gz and the manifest entry."""
    d = snap_dir(root) / date
    d.mkdir(parents=True, exist_ok=True)
    files = {}
    for k in FILES:
        gz = write_gz(d / f"{k}.txt.gz", sub[k].encode("utf-8"))
        files[f"{k}.txt.gz"] = sha256(gz)
    zb = Path(zpath).read_bytes()
    when = dt.datetime.fromtimestamp(Path(zpath).stat().st_mtime, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    man = manifest(root)
    old = man["snapshots"].get(date, {})
    entry = {"downloaded_utc": old.get("downloaded_utc", when) if old.get("zip_sha256") == sha256(zb) else when,
             "zip_sha256": sha256(zb), "zip_bytes": len(zb), "files": files}
    man["snapshots"][date] = entry
    if backtest:
        man["backtest"] = date
    save_manifest(root, man)
    return entry


def locked_dates(root):
    """Snapshot dates that a committed or pending prediction file names."""
    return {read_json(p).get("snapshot") for p in (Path(root) / "predictions").glob("*.json")}


def zip_path(root, date):
    return Path(root) / "data/raw/faa" / f"ReleasableAircraft-{date}.zip"


def raw_dates(root):
    return sorted(p.stem.split("-", 1)[1] for p in (Path(root) / "data/raw/faa").glob("ReleasableAircraft-*.zip"))


def lossless(zpath):
    """True when every file decodes as strict UTF-8, so the re-encoded subset is the zip's own bytes."""
    with zipfile.ZipFile(zpath) as z:
        names = {Path(n).stem.upper(): n for n in z.namelist()}
        for k in FILES:
            try:
                z.read(names[k]).decode("utf-8")
            except UnicodeDecodeError:
                return False
    return True
