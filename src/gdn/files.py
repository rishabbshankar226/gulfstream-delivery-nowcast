"""Small file helpers. Every text file is written with LF line endings."""
import csv
import hashlib
import io
import json
import os
import zlib
from pathlib import Path


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def _replace(path, data):
    """Write through a sibling temp file (ignored by .gitignore) so a reader never sees half a file."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    if path.exists() and path.read_bytes() == data:
        return False
    _replace(path, data)
    return True


def write_json(path, obj):
    return write_text(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def read_json(path):
    return json.loads(Path(path).read_text())


def cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, float):
        return repr(v)
    return str(v)


def csv_text(cols, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for r in rows:
        w.writerow([cell(r.get(c)) for c in cols])
    return buf.getvalue()


def write_csv(path, cols, rows):
    return write_text(path, csv_text(cols, rows))


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def gz_bytes(data):
    """gzip with mtime 0 and the header's OS byte set to 255 (unknown), so macOS and Linux write the same bytes."""
    import gzip as _gzip
    b = bytearray(_gzip.compress(data, mtime=0))
    b[9] = 255
    return bytes(b)


def write_gz(path, data):
    """Write gzip-compressed data unless the file already holds exactly this content. Returns the file's bytes."""
    import gzip as _gzip
    path = Path(path)
    if path.exists():
        old = path.read_bytes()
        try:
            if _gzip.decompress(old) == data:
                return old
        except (OSError, EOFError, zlib.error):  # a write that died halfway: replace it
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    new = gz_bytes(data)
    _replace(path, new)
    return new
