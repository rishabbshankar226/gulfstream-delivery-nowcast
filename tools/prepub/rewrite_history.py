"""Rewrite this repository's history so it can go public with no personal data in it (GO_PUBLIC.md, part 0).

    PRIVATE_NAME='<your private name>' python3 tools/prepub/rewrite_history.py \
        --old-email '<the personal address to remove>' \
        --new-email '<id>+<handle>@users.noreply.github.com' --out ~/gdn-rewrite.git

What it does, on a NEW mirror clone at --out (this checkout is never touched, and nothing is pushed):

0. It refuses to run unless refs/remotes/origin/main is an ancestor of main (fetch and pull first), so no commit the
   daily workflow pushed is lost when the rewritten main is force-pushed.
1. Every commit's author and committer email that equals --old-email becomes --new-email.
2. In every file of every commit, and in every commit message, the home-folder prefix (/Users/<account>) becomes `~`,
   the account name in an `ls -l` owner column becomes `owner`, PRIVATE_NAME becomes `[private name]`, and the
   phrases that name the old address's mail provider (round 4 found ten) or narrow the account name are reworded.
   Only blobs holding one of those patterns are rewritten; every other file keeps its exact bytes.
3. Tags are rewritten onto the new commits (lock-2026Q3 included). Author and commit dates are kept.

Then it checks its own work and prints a report: the counts of each pattern before and after, that every record file
(predictions/, results/live/, data/snapshots/, docs/PREREGISTRATION.md, .github/) is byte-identical at every branch
tip, that predictions/2026Q3.json at the new lock tag hashes to the value in the lock-2026Q3 release notes, and that the
lock commit keeps its date and author. It writes commit_map.csv (old SHA, new SHA, date, subject) next to the mirror
and prints the push commands for the owner to run. It exits non-zero if any check fails.

No personal value is written into this file: the email comes from --old-email, the account from the home folder, and
the private name from the environment. After the rewrite every author and committer email on the rewritten refs must be
a no-reply or bot address, whatever --old-email was.
"""
import argparse
import csv
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LOCK_TAG = "lock-2026Q3"
LOCK_FILE = "predictions/2026Q3.json"
LOCK_SHA256 = "3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23"
RECORD = ["predictions", "results/live", "data/snapshots", "docs/PREREGISTRATION.md", ".github"]
REPO_URL = "https://github.com/rishabbshankar226/gulfstream-delivery-nowcast.git"

# The patterns are assembled at run time, so this file never holds them verbatim: the rewrite then leaves the current
# version of this file alone, and the file itself says nothing about the address it removes.
MAIL = "g" + "mail"
CAP = MAIL[0].upper() + MAIL[1:]
NARROW = "prefix" + " of it"
SED = (' -e "s|$OLD_HOME|~|g" -e "s|$ACCT  staff|owner  staff|g" -e "s|$PRIV|[private name]|g"'
       f' -e "s|personal {CAP} address|personal email address|g" -e "s|personal {MAIL} address|personal email address|g"'
       f' -e "s|{CAP} address|email address|g" -e "s|<personal {MAIL}>|<personal email>|g"'
       f' -e "s|{MAIL}\\.com|a personal domain|g" -e "s#@{MAIL}|@uic#@<personal domains>#g"'
       f' -e "s|; it is a {NARROW}|; it does not|g" -e "s|{NARROW}|narrowing phrase|g"'
       f' -e "s|[{CAP[0]}{MAIL[0]}]{MAIL[1:]}|email|g"')

INDEX_FILTER = r"""#!/bin/sh
git grep --cached -l -I -i -e "$OLD_HOME" -e "$ACCT  staff" -e "$PRIV" -e "$MAILWORD" -e "$NARROW" 2>/dev/null | \
while IFS= read -r path; do
  entry=$(git ls-files -s -- "$path")
  mode=$(printf '%s' "$entry" | cut -d' ' -f1)
  sha=$(printf '%s' "$entry" | cut -d' ' -f2)
  new=$(git cat-file -p "$sha" | sed SEDEXPR | git hash-object -w --stdin)
  git update-index --cacheinfo "$mode,$new,$path"
done
"""


def git(repo, *args, env=None, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, errors="replace", env=env)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args[:2])} failed: {r.stderr.strip()[-300:]}")
    return r.stdout


def refs(repo, original=False):
    out = git(repo, "for-each-ref", "--format=%(refname)").split()
    return [r for r in out if r.startswith("refs/original/") == original]


def scan(repo, rs, email, home, acct, priv):
    meta = git(repo, "log", "--format=%ae%n%ce", *rs)
    body = git(repo, "log", "-p", "--format=%B", *rs)
    personal = [e for e in meta.split() if "noreply" not in e and "[bot]" not in e]
    return {"commits": len(git(repo, "rev-list", *rs).split()), "old email in metadata": meta.count(email),
            "any non-noreply email in metadata": len(personal),
            "old email in files or messages": body.count(email), "home prefix": body.count(home),
            "account in ls owner column": body.count(acct + "  staff"), "private name": body.lower().count(priv.lower()),
            "mail-provider word": body.lower().count(MAIL), "account-narrowing phrase": body.count(NARROW)}


def blobs(repo, ref):
    out = {}
    for line in git(repo, "ls-tree", "-r", ref, "--", *RECORD).splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[2]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-email", required=True, help="the personal address to remove from commit metadata")
    ap.add_argument("--new-email", required=True, help="your GitHub no-reply address, from Settings, Emails")
    ap.add_argument("--out", required=True, help="a new directory for the rewritten mirror")
    ap.add_argument("--source", default=str(Path(__file__).resolve().parents[2]))
    a = ap.parse_args()
    priv = os.environ.get("PRIVATE_NAME", "").strip()
    if not priv:
        sys.exit("set PRIVATE_NAME in the environment")
    if "noreply" not in a.new_email:
        sys.exit("--new-email should be your GitHub no-reply address")
    src, out = Path(a.source).resolve(), Path(a.out).expanduser().resolve()
    if out.exists():
        sys.exit(f"{out} exists; give a new directory")
    email = a.old_email.strip()
    if subprocess.run(["git", "-C", str(src), "merge-base", "--is-ancestor", "refs/remotes/origin/main",
                       "refs/heads/main"]).returncode:
        sys.exit("origin/main has commits that main lacks: git fetch, then git switch main && git pull --ff-only, "
                 "then merge prepub-audit, before you rewrite")
    home = str(Path.home())
    acct = Path.home().name

    git(src, "clone", "-q", "--mirror", str(src), str(out))
    git(out, "remote", "set-url", "--push", "origin", "DISABLED")
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
        f.write(INDEX_FILTER.replace("SEDEXPR", SED))
    os.chmod(f.name, 0o755)
    env = dict(os.environ, OLD_EMAIL=email, NEW_EMAIL=a.new_email, OLD_HOME=home, ACCT=acct, PRIV=priv,
               MAILWORD=MAIL, NARROW=NARROW,
               FILTER_BRANCH_SQUELCH_WARNING="1")
    print("rewriting (a few minutes)...", flush=True)
    git(out, "filter-branch", "-f",
        "--env-filter", 'if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]; then export GIT_AUTHOR_EMAIL="$NEW_EMAIL"; fi; '
                        'if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]; then export GIT_COMMITTER_EMAIL="$NEW_EMAIL"; fi',
        "--index-filter", f.name,
        "--msg-filter", "sed" + SED,
        "--tag-name-filter", "cat", "--", "--all", env=env)

    before, after = refs(out, True), refs(out)
    b, n = scan(out, before, email, home, acct, priv), scan(out, after, email, home, acct, priv)
    ok = True
    print("\n| Check | Before | After |\n|---|---|---|")
    for k in b:
        print(f"| {k} | {b[k]} | {n[k]} |")
        if k != "commits" and n[k]:
            ok = False
    if b["commits"] != n["commits"]:
        ok = False
    for r in before:
        new = r.replace("refs/original/", "", 1)
        same = blobs(out, r) == blobs(out, new)
        ok &= same
        print(f"record files identical at {new}: {same}")
    data = subprocess.run(["git", "-C", str(out), "show", f"{LOCK_TAG}:{LOCK_FILE}"], capture_output=True).stdout
    lock_ok = hashlib.sha256(data).hexdigest() == LOCK_SHA256
    old_lock, new_lock = (git(out, "rev-parse", f"refs/original/refs/tags/{LOCK_TAG}").strip(),
                          git(out, "rev-parse", f"refs/tags/{LOCK_TAG}").strip())
    same_meta = (git(out, "log", "-1", "--format=%an|%ad|%cd", old_lock) == git(out, "log", "-1", "--format=%an|%ad|%cd", new_lock))
    ok &= lock_ok and same_meta
    print(f"{LOCK_FILE} at the new {LOCK_TAG} hashes to the release notes' value: {lock_ok}")
    print(f"lock commit keeps its author and dates: {same_meta}; old {old_lock[:12]}, new {new_lock[:12]}")

    # old -> new commit map: the rewrite keeps the graph, so the two topological orders line up; checked by date.
    rows = []
    for r in before:
        o = git(out, "rev-list", "--topo-order", "--reverse", "--format=%H|%ad|%s", "--date=iso", r).splitlines()
        nw = git(out, "rev-list", "--topo-order", "--reverse", "--format=%H|%ad|%s", "--date=iso",
                 r.replace("refs/original/", "", 1)).splitlines()
        o, nw = [x for x in o if "|" in x], [x for x in nw if "|" in x]
        for x, y in zip(o, nw):
            xo, yo = x.split("|", 2), y.split("|", 2)
            if xo[1] != yo[1]:
                ok = False
            rows.append((xo[0], yo[0], xo[1], yo[2]))
    seen, mp = set(), out.parent / (out.name + ".commit_map.csv")
    with mp.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["old_sha", "new_sha", "date", "subject"])
        for row in rows:
            if row[0] not in seen:
                seen.add(row[0])
                w.writerow(row)
    print(f"commit map: {mp} ({len(seen)} commits)")
    print("\nIf every check above passed, the owner pushes (GO_PUBLIC.md, part 0):\n")
    print(f"  git -C {out} remote set-url --push origin {REPO_URL}")
    print(f"  git -C {out} push --force origin refs/heads/main:refs/heads/main")
    print(f"  git -C {out} push --force origin refs/tags/{LOCK_TAG}:refs/tags/{LOCK_TAG}")
    print("  git -C <out> push origin --delete prepub-audit codex/fix-daily-merge-and-lock-integrity")
    print(f"\n{'ALL CHECKS PASSED' if ok else 'A CHECK FAILED: do not push'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
