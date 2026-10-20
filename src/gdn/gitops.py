"""git and gh calls for the daily job and the lock. Every call goes through `run` so a rehearsal can
put a gh shim first on PATH and a test can replace the whole object."""
import json
import re
import subprocess
import sys
from pathlib import Path


class GitError(RuntimeError):
    pass


class Ops:
    def __init__(self, root=".", log=print):
        self.root = Path(root).resolve()
        self.log = log

    def run(self, *cmd, check=True):
        r = subprocess.run(list(cmd), cwd=self.root, capture_output=True, text=True)
        if check and r.returncode != 0:
            raise GitError(f"{' '.join(cmd)} failed ({r.returncode}): {(r.stderr or r.stdout).strip()[:400]}")
        return r

    def git(self, *a, check=True):
        return self.run("git", *a, check=check)

    # ---- repository ----
    def slug(self):
        """owner/name of the GitHub repository, from origin's URL or path."""
        url = self.git("remote", "get-url", "origin").stdout.strip()
        m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
        if not m:
            raise GitError(f"origin does not name a GitHub repository: {url}")
        return f"{m[1]}/{m[2]}"

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.strip()

    def dirty_tracked(self):
        """Tracked paths with uncommitted changes."""
        out = self.git("status", "--porcelain", "--untracked-files=no").stdout.splitlines()
        return [ln[3:].split(" -> ")[-1] for ln in out if ln.strip()]

    def tracked(self, path):
        return bool(self.git("ls-files", "--", str(path)).stdout.strip())

    def merging(self):
        """True while a merge is in progress (MERGE_HEAD exists)."""
        return self.git("rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0

    def ahead(self):
        r = self.git("rev-list", "--count", "@{u}..HEAD", check=False)
        return int(r.stdout.strip() or 0) if r.returncode == 0 else 0

    def pull(self):
        """git pull --no-rebase --tags. Returns the conflicted paths ([] on a clean merge)."""
        r = self.git("pull", "--no-rebase", "--tags", "--no-edit", check=False)
        if r.returncode == 0:
            return []
        conflicted = self.git("diff", "--name-only", "--diff-filter=U", check=False).stdout.split()
        if not conflicted:
            raise GitError(f"git pull failed: {(r.stderr or r.stdout).strip()[:400]}")
        return conflicted

    def take_theirs(self, paths):
        for p in paths:
            self.git("checkout", "--theirs", "--", p)
            self.git("add", "--", p)

    def finish_merge(self):
        self.refuse_markers()
        self.git("commit", "--no-edit")

    def abort_merge(self):
        self.git("merge", "--abort", check=False)

    def commit(self, paths, message):
        """Stage the given paths (only those that exist or are tracked) and commit if anything changed."""
        paths = [str(p) for p in paths if (self.root / p).exists() or self.tracked(p)]
        if not paths:
            return False
        self.git("add", "-A", "--", *paths)
        if self.git("diff", "--cached", "--quiet", check=False).returncode == 0:
            return False
        self.refuse_markers()
        self.git("commit", "-m", message)
        return True

    def refuse_markers(self):
        """Raise when a staged text file still holds merge conflict markers."""
        staged = self.git("diff", "--cached", "--name-only", "--diff-filter=AM", "-z").stdout.split("\0")
        bad = []
        for f in staged:
            if not f:
                continue
            # Read the index, which is what commit writes, rather than potentially newer working text.
            blob = subprocess.run(["git", "show", f":{f}"], cwd=self.root, capture_output=True, check=True).stdout
            if b"\0" not in blob and any(re.match(rb"^(?:<{7,}|>{7,})(?: |$)", ln)
                                         for ln in blob.splitlines()):
                bad.append(f)
        if bad:
            raise GitError(f"conflict markers in {bad}; not committing")

    def stage_version(self, path, stage):
        """The text of a conflicted path at a merge stage (2 ours, 3 theirs), or None."""
        r = self.git("show", f":{stage}:{path}", check=False)
        return r.stdout if r.returncode == 0 else None

    def add(self, path):
        self.git("add", "--", str(path))

    def commit_only(self, path, message):
        self.git("add", "--", str(path))
        self.refuse_markers()
        self.git("commit", "-m", message, "--", str(path))
        return self.head()

    def push(self):
        """True when the push lands, False when it is rejected."""
        r = self.git("push", "origin", "HEAD", check=False)
        if r.returncode != 0:
            self.log(f"push rejected: {(r.stderr or r.stdout).strip()[:300]}")
        return r.returncode == 0

    def reset_to_upstream(self):
        self.git("fetch", "origin")
        self.git("reset", "--hard", "@{u}")

    def first_commit(self, path):
        out = self.git("log", "--diff-filter=A", "--format=%H", "--", str(path)).stdout.split()
        return out[-1] if out else None

    # ---- releases ----
    def release_view(self, tag):
        """{"publishedAt", "tagName"} of the release, or None when it does not exist."""
        for attempt in range(2):
            r = self.run("gh", "release", "view", tag, "-R", self.slug(), "--json", "publishedAt,tagName", check=False)
            if r.returncode == 0 or re.search(r"not found|could not find|HTTP 404", (r.stderr + r.stdout), re.I):
                break
        if r.returncode != 0:
            if re.search(r"not found|could not find|HTTP 404", (r.stderr + r.stdout), re.I):
                return None
            raise GitError(f"gh release view {tag} failed: {(r.stderr or r.stdout).strip()[:300]}")
        return json.loads(r.stdout)

    def release_create(self, tag, target, title, notes):
        self.run("gh", "release", "create", tag, "-R", self.slug(), "--target", target, "--title", title,
                 "--notes", notes)

    def fetch_tag(self, tag):
        self.git("fetch", "origin", f"refs/tags/{tag}:refs/tags/{tag}")

    def tag_commit(self, tag):
        return self.git("rev-list", "-n", "1", tag).stdout.strip()

    def file_at_ref(self, ref, path):
        """Exact bytes of a repository-relative path at a commit or tag."""
        r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=self.root, capture_output=True)
        if r.returncode != 0:
            raise GitError(f"cannot read {path} at {ref}: {r.stderr.decode('utf-8', errors='replace').strip()[:400]}")
        return r.stdout


def warn(msg):
    print(msg, file=sys.stderr)
