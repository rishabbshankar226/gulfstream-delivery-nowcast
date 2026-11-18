"""Tests of the tests: break each of 12 rules with a one-line edit in a copy of the tree and check a test fails.

Usage: .venv/bin/python tools/mutate.py   (writes docs/build/MUTATION.md)
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / ".venv/bin/python"
SKIP = {".venv", ".git", ".build", "data/raw", "output", "__pycache__", ".pytest_cache", ".impeccable"}

# (rule, file, exact line fragment to replace, replacement)
MUTANTS = [
    ("Header normalization", "src/gdn/faa.py",
     'return re.sub(r"[^A-Z0-9]", "", h.replace("\\ufeff", "").upper())', 'return h.replace("\\ufeff", "").upper()'),
    ("Comma fallback", "src/gdn/faa.py", "if len(row) != len(header):", "if False:"),
    ("Scope by model name", "src/gdn/faa.py",
     'if ("GULFSTREAM" in mfr or "GULFSTREAM" in model) and', 'if ("GULFSTREAM" in mfr) and'),
    ("IAI cabin rule", "src/gdn/faa.py",
     'cabin = "mid" if MID.search(model) or mfr.startswith(("IAI", "ISRAEL")) else "large"',
     'cabin = "mid" if MID.search(model) else "large"'),
    ("Gulfstream-held prefix", "src/gdn/events.py",
     'return name.strip().upper().startswith("GULFSTREAM AEROSPACE")',
     'return name.strip().upper().startswith("GULFSTREAM AEROSPACE CORP")'),
    ("The bound", "src/gdn/events.py", "timedelta(days=365)", "timedelta(days=3650)"),
    ("Earliest date in E1 and E2", "src/gdn/events.py", "def _min(xs):\n    xs = [x for x in xs if x]\n    return min(xs) if xs else None",
     "def _min(xs):\n    xs = [x for x in xs if x]\n    return max(xs) if xs else None"),
    ("Window edge", "src/gdn/events.py", "lo < r[key] <= top", "lo <= r[key] < top"),
    ("Zero rule", "src/gdn/model.py", "return sum(y_lags) / len(y_lags)", "return 0.0"),
    ("Nearest rank", "src/gdn/stats.py", "return s[math.ceil(p * len(s)) - 1] if s else None",
     "return s[max(0, int(p * len(s)) - 1)] if s else None"),
    ("Eve boundary", "src/gdn/live.py", "return newest_snapshot == eve.isoformat() or t.hour >= LOCK_HOUR_ET",
     "return newest_snapshot == eve.isoformat() or t.hour > LOCK_HOUR_ET"),
    ("Second lock", "src/gdn/live.py", "        if ops.release_view(tag):\n            if not lock_p.exists() and pred_p.exists():",
     "        if False:\n            if not lock_p.exists() and pred_p.exists():"),
]


def copy_tree(dst):
    def ignore(d, names):
        rel = Path(d).relative_to(ROOT)
        return [n for n in names if str(rel / n).lstrip("./") in SKIP or n in SKIP]
    shutil.copytree(ROOT, dst, ignore=ignore, dirs_exist_ok=True)


def run_tests(tree):
    r = subprocess.run([str(PY), "-m", "pytest", "-q", "-rf", "-p", "no:cacheprovider", "--tb=no",
                        "--ignore=tests/test_site_a11y.py", "tests"], cwd=tree, capture_output=True, text=True,
                       env={"PYTHONPATH": str(Path(tree) / "src"), "PATH": "/usr/bin:/bin",
                            "PYTHONDONTWRITEBYTECODE": "1"})
    failed = re.findall(r"^FAILED (\S+)", r.stdout, re.M)
    return r.returncode, failed, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]


def main():
    rows, caught = [], 0
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / "tree"
        copy_tree(tree)
        rc, failed, last = run_tests(tree)
        if rc != 0:
            sys.exit(f"the clean copy does not pass: {last}")
        print(f"clean copy passes: {last}")
        for rule, f, old, new in MUTANTS:
            p = tree / f
            src = p.read_text()
            if src.count(old) != 1:
                sys.exit(f"{rule}: the line to break is not unique in {f}")
            p.write_text(src.replace(old, new))
            rc, failed, last = run_tests(tree)
            p.write_text(src)
            for cache in tree.rglob("__pycache__"):
                shutil.rmtree(cache)
            clean_rc, _, clean_last = run_tests(tree)
            if clean_rc != 0:
                sys.exit(f"after restoring {rule} the copy no longer passes: {clean_last}")
            ok = rc != 0 and failed
            caught += bool(ok)
            a, b = old.splitlines(), new.splitlines()
            i = next(i for i in range(len(a)) if a[i] != b[i])  # the line the mutant changes
            rows.append((rule, f, a[i].strip(), b[i].strip(), failed))
            print(f"{'caught' if ok else 'SURVIVED'}: {rule} ({len(failed)} failing)")
    lines = ["# Tests of the tests", "",
             f"`tools/mutate.py` copies the tree, confirms the clean copy passes, then breaks one rule at a time with a "
             f"one-line edit and runs `pytest` (the browser test aside). **{caught} of {len(MUTANTS)} caught.**", "",
             "| Rule | File | Original | Mutant | Failing tests |", "|---|---|---|---|---|"]
    for rule, f, old, new, failed in rows:
        tests = "<br>".join(failed[:4]) + (f" (+{len(failed) - 4} more)" if len(failed) > 4 else "") or "**none: survived**"
        lines.append(f"| {rule} | `{f}` | `{old}` | `{new}` | {tests} |")
    (ROOT / "docs/build/MUTATION.md").write_text("\n".join(lines) + "\n")
    return 0 if caught == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
