#!/usr/bin/env python3
"""Runs the recompute scripts and writes docs/prepub/reviews/recompute.txt.

Usage: python3 assemble.py <repo_root>

Runs parta.py (toy, then real), partb.py and partb_diag.py from this file's own
folder with the repository root as the working directory, joins their output
with notes_head.txt and notes_tail.txt, writes the review file with LF line
endings, and copies the scripts and notes into <repo_root>/docs/prepub/recompute/.
"""
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def run(root, script, *args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, os.path.join(HERE, script)] + list(args),
                       cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode("utf-8", "replace"))
        raise SystemExit("%s failed with exit code %d" % (script, p.returncode))
    return p.stdout.decode("utf-8")


def sections(text):
    """[(heading, [lines])] split at lines starting with '## '."""
    res, cur = [], None
    for ln in text.split("\n"):
        if ln.startswith("## "):
            cur = (ln, [])
            res.append(cur)
        elif cur is not None and ln.strip() != "":
            cur[1].append(ln)
    return res


def main():
    root = os.path.abspath(sys.argv[1])
    toy = run(root, "parta.py", "docs/prepub/recompute/toy")
    pa = run(root, "parta.py", "data/processed", "--guidance", "data/guidance.csv",
             "--prediction", "predictions/2026Q3.json", "--q3-reported", "35,5")
    pb = run(root, "partb.py", "data/snapshots", "2026-10-19", "2026-10-29",
             "data/processed", "predictions/2026Q3.json")
    pd = run(root, "partb_diag.py", "data/snapshots", "2026-10-19", "2026-10-29",
             "data/processed", "predictions/2026Q3.json")
    with open(os.path.join(HERE, "notes_head.txt")) as fh:
        head = fh.read().rstrip("\n")
    with open(os.path.join(HERE, "notes_tail.txt")) as fh:
        tail = fh.read().strip("\n")

    L = [head, ""]
    L.append("## Toy check (docs/prepub/recompute/toy, ratio under E1)")
    n = 0
    for ln in toy.split("\n"):
        if ln.startswith("check.E1.") and (".ratio_total" in ln or ".abs_error" in ln or ".reported_total" in ln):
            L.append("toy." + ln[len("check."):])
            n += 1
        elif ln.startswith("check.E1.mae_all_computable"):
            L.append("toy.E1.mae_2002Q1_to_2003Q1 = " + ln.split(" = ")[1])
        elif ln.startswith("check.E1.quarters") or ln.startswith("check.E1.n_quarters"):
            L.append("toy." + ln[len("check."):])
    L.append("")

    for h, lines in sections(pa):
        L.append(h)
        L.extend(lines)
        L.append("")

    sb = dict((h.split(".")[0].replace("## ", "").split(" ")[0], (h, lines)) for h, lines in sections(pb))
    sd = dict((h.split(".")[0].replace("## ", "").split(" ")[0], (h, lines)) for h, lines in sections(pd))
    for key, src in (("13", sb), ("14", sb), ("15", sb), ("15x", sb), ("22", sd), ("16", sb),
                     ("17", sd), ("18", sd), ("19", sd), ("20", sd), ("21", sd), ("23", sd)):
        h, lines = src[key]
        L.append(h)
        L.extend(lines)
        L.append("")
    L.append(tail)
    text = "\n".join(L) + "\n"

    outdir = os.path.join(root, "docs", "prepub", "reviews")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "recompute.txt"), "w", newline="\n") as fh:
        fh.write(text)
    copydir = os.path.join(root, "docs", "prepub", "recompute")
    os.makedirs(copydir, exist_ok=True)
    if os.path.abspath(copydir) != HERE:
        for name in ("parta.py", "partb.py", "partb_diag.py", "assemble.py",
                     "notes_head.txt", "notes_tail.txt"):
            shutil.copyfile(os.path.join(HERE, name), os.path.join(copydir, name))
    print("wrote %s (%d lines, %d bytes)" % (os.path.join(outdir, "recompute.txt"),
                                             text.count("\n"), len(text.encode("utf-8"))))
    print("copied scripts to %s" % copydir)


if __name__ == "__main__":
    main()
