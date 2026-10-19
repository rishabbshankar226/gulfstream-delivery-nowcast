"""Small file helpers. Every text file is written with LF line endings."""
import csv
import hashlib
import io
import json
from pathlib import Path


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    if path.exists() and path.read_bytes() == data:
        return False
    path.write_bytes(data)
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
