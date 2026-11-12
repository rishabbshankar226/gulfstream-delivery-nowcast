"""`make check-determinism`: run `make all` twice and compare the sha256 of every file it writes (the PDF aside).

The workbook's input stamp is removed before each run so the workbook is rebuilt, not skipped."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOBS = ["data/snapshots/MANIFEST.json", "data/snapshots/*/*.txt.gz", "data/processed/*.csv", "data/sec_manifest.json",
         "results/*.csv", "results/*.json", "results/*.md", "results/diagnostics/*", "output/*.xlsx",
         "output/*.sha256", "output/charts/*.png", "report/note.html", "report/claims.json", "site/data.json",
         "README.md", "docs/LINKEDIN_POST.md"]
SKIP = {"output/charts/dashboard.png", "output/GD_research_note.inputs.sha256"}


def digest():
    out = {}
    for g in GLOBS:
        for p in sorted(ROOT.glob(g)):
            rel = str(p.relative_to(ROOT))
            if rel not in SKIP and p.is_file():
                out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def make_all():
    (ROOT / "output/gd_gulfstream_model.inputs.sha256").unlink(missing_ok=True)
    (ROOT / "output/charts/inputs.sha256").unlink(missing_ok=True)      # so the charts are redrawn, not skipped
    py = os.environ.get("PY", str(ROOT / ".venv/bin/python"))
    r = subprocess.run(["make", "all", f"PY={py}"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"make all failed:\n{(r.stdout + r.stderr)[-2000:]}")


def main():
    make_all()
    a = digest()
    make_all()
    b = digest()
    diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    if diff:
        print("differ:")
        for k in diff:
            print("  " + k)
        return 1
    print(f"identical ({len(a)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
