# Round 4: exposure, privacy and the owner's runbook

Verdict: NO-GO. The owner's private name for themself sits in a tracked file at the tip and in 12 committed versions of it, and the decision on the personal email address in 121 commits is still unrecorded.

Counts: S1 2, S2 4, S3 7

Trees read: the bare mirror `~/gdn-prepub/round4_mirror.git` (all refs) and the owner's checkout at `e7b9d3d` (`prepub-audit`, with `docs/prepub/DECISIONS.md` modified and uncommitted). Every count below was printed by a command or by a script in `~/gdn-prepub/agents/round4_exposure/`; the scripts print kinds, counts, commits and paths, never values. In this file, "the repository URL" stands for the GitHub address, because the GitHub account name contains the macOS account name.

## Answers

**1. History scan** (`scan_history.py`, `blobs.py`, `msgscan.py`: `git log -p --all`, every one of the 927 blobs in the mirror, and every commit message)

- Author and committer identities, 168 commits on all refs: a personal email address with a name containing the account name, on 121 commits as both author and committer; GitHub's Actions bot noreply address on 47. No other identity. By ref: `main` 62 personal and 47 bot; `prepub-audit` 121 and 47; `main..prepub-audit` 59 and 0. Of the 62 personal commits on `main`, 58 are ancestors of the lock commit `a44e5ac`.
- Emails in commit messages: 98 `Co-Authored-By` trailers, all with an Anthropic noreply address (55 and 43 under two model names). No other address.
- Emails in file content: placeholders only (four distinct addresses on the `.invalid` test domain, one on `example.com`), in `tests/`, `tools/rehearsal.py`, `docs/prepub/EXPOSURE.md` and `docs/prepub/reviews/compliance.md`. Two further "hits" are the `@pytest.fixture` and `@pytest.mark` decorators at the start of added lines.
- Tokens and keys: 0 real ones in any blob. `ghp_`, `github_pat_`, `AKIA`, `-----BEGIN`, `password=` occur only as pattern names in `docs/prepub/EXPOSURE.md` (commit `aa273cb`) and in this round's brief (`e7b9d3d`). All 52 key-shaped `sk-` hits are claim ids that contain `risk-`.
- The SEC user-agent string: 0 occurrences, whole, in any blob or commit message. Its email part: 0 in content. But the email part is the same address as the commit author address (hash match), and the name part is the owner's public name, which `LICENSE`, `README.md`, the note, the dashboard and the workbook print by design. Accepting Decision A therefore publishes both parts of the string, though not the string itself.
- Home-folder paths: 150 diff lines (added or removed) in 21 commits across 57 paths. With the account name in the path, 54 files on `prepub-audit` ever received one. 18 still hold one at the tip: 16 under `docs/build/briefs/` (commits `5c84d36`, `6bef306`, `9b84384`, `cf0657a`, `ea0a555`, all ancestors of the lock) and 2 under `docs/prepub/` (`9945499`). The other 36 hold one only in history, all in commits of `main..prepub-audit`, none an ancestor of the lock. The bare account name without a path: `docs/build/DECISIONS.md:32` (`09c16a9`), the owner column of an `ls -l` line. Commit messages: 0 home paths, 0 account names.

**2. Refs** (`git for-each-ref`, `git log A..B`)

| Ref | Tip | Public after the flip | Commits `main` lacks | Commits `prepub-audit` lacks |
|---|---|---|---|---|
| `origin/main` = `main` | `8c7692f` | yes | 0 | 0 |
| `origin/prepub-audit` | `4388294` | yes, already on GitHub | 58 | 0 |
| `origin/codex/fix-daily-merge-and-lock-integrity` | `163eac0` | yes | 2 (`163eac0`, `44b3715`: lock verification against the tag, merge-history guard; placeholder emails in tests only) | 0 |
| tag `lock-2026Q3` (lightweight) | `a44e5ac` | yes | 0 | 0 |
| `prepub-audit` (local) | `e7b9d3d` | only by push | 59 | n/a |
| `prepub-mergecheck`, `prepub-mergecheck2` (local) | `048dbb3`, `bbf88fd` | only by push | 36, 51 | 0, 0 |

No ref holds a commit that `prepub-audit` lacks, so after the planned merge every pushed ref is a subset of `main`. `origin/prepub-audit` is at `4388294`, one commit (`e7b9d3d`) behind the local branch; `GO_PUBLIC.md` says `f14a400` (EXPOSURE-7). The locked file hashes to `3c4cdbd0...6f23` at the tag, on `main` and on `prepub-audit`, matching the release notes.

**3. Tracked files** (299, `git ls-files`)

- Dotfiles: `.gitattributes`, `.gitignore`, the three workflows. All belong in public. `.gitignore` names `CLAUDE.md`, `OUTCOME_SELF.md`, `.claude/` and `.impeccable/`; none is tracked, and no path was ever added and later removed.
- Agent or editor configs, logs, caches: none tracked.
- Large or binary files: none over 1 MB. The largest are the note PDF (749,375 bytes, twice: `output/` and `site/`), `tests/vendor/axe.min.js` (553,446, MPL-2.0 header kept), `docs/prepub/LEDGER.csv` (529,921) and `data/processed/serials.csv`. Metadata (`meta_scan.py`): the PDFs carry a HeadlessChrome creator and no name or path; the workbook's `docProps/core.xml` creator is the owner's public name (deliberate, as in `LICENSE`); the PNGs carry no text chunks. Hits of the account name in the PDF and workbook are all the repository URL.
- Personal: `docs/INTERVIEW_NOTES.md` and `docs/RESUME_BULLETS.md` are career documents about the project only. Publishing them is the owner's choice (Decision E); they hold no contact or private detail.

**4. `docs/prepub/` and `docs/build/` as public text**

- Personal details: the private name at `docs/prepub/DECISIONS.md:36` (EXPOSURE-1). Home-folder paths in 18 tip files and the account name at `docs/build/DECISIONS.md:32` (EXPOSURE-3).
- Internal tool paths: "prompt library" (the private spec folder) in 10 tip files, the private gate in 5, `.claude/` in 6, `gdn-prepub` scratch paths in 42; `tools/rehearsal.py:179` hard-codes the gate's path (EXPOSURE-13).
- Reads badly next to the post: `VERDICT.md:3` opens "**NO-GO.**"; eight of the nine earlier Markdown reviews in `reviews/` open with a NO-GO verdict (the ninth, `round3.md`, reports no S1); the round 4 briefs, tracked since `e7b9d3d`, describe this as "a harsh go-public audit" aimed at recruiters. No index tells a reader which files are current (EXPOSURE-5).
- Contradicts the final surfaces or the facts: the "124 commits" count (EXPOSURE-4); "the final tree of this branch is scrubbed" (EXPOSURE-3); `origin/prepub-audit` at `f14a400` (EXPOSURE-7); `docs/build/README.md:3` saying no file changed after 2026-10-19 (EXPOSURE-11).
- Options, none of which moves the record. `docs/build/`: publish, after fixing the README's date sentence; replacing the home prefix with `~` in the 16 briefs and line 32 is optional, since those commits are ancestors of the lock and stay in history either way. `docs/prepub/`: publish with an index and a dated final addendum to `VERDICT.md`, and remove the private name. Or trim the agent working files (`briefs/`, `PLAN.md`, `LEDGER*.csv`, `recompute/`) from the tree in a new commit, keeping `ERRATA.md` (linked from the README and part of the record), `LOCK_CHECK.md`, `RECORD_HASHES.txt`, `FINDINGS.md`, `VERDICT.md` and `GO_PUBLIC.md`. A trim does not remove history. The only way to keep the 59 `prepub-audit` commits out of public history without rewriting `main` is a squash merge plus deleting `origin/prepub-audit` before the flip. It has two costs. `FINDINGS.md` cites `prepub-audit` commits (for example `e778e23`) that would then not be public. And the branch is already on GitHub. GitHub's page "Removing sensitive data from a repository" warns that such commits "may still be accessible elsewhere", including cached views reached by commit hash. A normal merge is the defensible default.

**5. `GO_PUBLIC.md` as a runbook.** I walked it in order without running a step.

- Part 1 A: the reasoning holds for the 58 lock-ancestor commits. The count "124 commits on `main`" is wrong; the command it gives prints 62 (EXPOSURE-4). B: its check finds 16 files and misses three tip files (EXPOSURE-3). C, D: no record risk; C changes later subsets only. E: correct, but the branch deletions never appear as an ordered step (EXPOSURE-10).
- Step 1: the check commands work today. `grep -o '<p id="disclosure">...'` prints the undated sentence, and the note's sha256 equals the stamp (`e0b89a40...5c3d` both). It never names the branch, and "line 15" is the disclosure only on `prepub-audit` (EXPOSURE-9).
- Step 2: safe. `git diff --stat main prepub-audit -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` prints nothing, so no conflict can arise on the protected paths. `make all` is the offline target (`Makefile:66`). The stated hash matches. The `f14a400` paragraph is stale (EXPOSURE-7).
- Step 3: its checks hold today (`made while the repository was private` count 1; `public lock` 0 in the README and the note).
- Step 3b: the order is right, but the commands pull before the run can finish, and the check cannot show what it claims (EXPOSURE-8). The three hashes in `RECORD_HASHES.txt` match the files today.
- Steps 4 and 5: order correct. `pages.yml` deploys only when `github.event.repository.private == false`, and `gh workflow run pages` matches its `name: pages`.
- Step 7: the release shows published `2026-10-29T05:51:24Z`, author the Actions bot, notes `sha256 3c4cdbd0...6f23`. All match. The file check reads the working copy, not the tag (EXPOSURE-12).
- Step 8: the block is byte-identical to `docs/LINKEDIN_POST.md` on `prepub-audit` (`diff` prints nothing; 1,281 characters).
- Missing: protection of the record on GitHub (EXPOSURE-6); an ordered step to delete stale branches and the two local throwaway branches (EXPOSURE-10); a step to update `VERDICT.md` once the decisions are made (EXPOSURE-5); setting future commits to the GitHub noreply address (EXPOSURE-2). The description and topics are already set (5 topics; homepage is the Pages URL). Rotation: nothing to rotate; no secret is in any blob, and the `SEC_UA` repository secret holds a contact string.
- Damage to the record: no step writes `predictions/`, `results/live/2026Q3_*`, `docs/PREREGISTRATION.md` or the release. One trap is not mentioned. Enabling immutable releases does not cover `lock-2026Q3`: GitHub's page "Preventing changes to your releases" says "immutability will only apply to future releases." Republishing that release to make it immutable would replace the published timestamp the record rests on. Warn against it.

**6. GitHub Actions on a public repository**

- `nowcast.yml`: `schedule` and `workflow_dispatch` only, so no fork can trigger it. Workflow-level `permissions: contents: write`. `SEC_UA` comes from a repository secret, and `GH_TOKEN` is the job token. Neither is echoed: `src/gdn/sec.py:31-38,68-79` puts the UA only in the request header and prints the URL and error on failure. `gitops.py:121,148` does a plain `git push` and `gh release create --target`. No force push.
- `pages.yml`: `contents: read`, `pages: write`, `id-token: write`; the deploy job runs only when the repository is public.
- `test.yml`: `push` and `pull_request` with `contents: read` and no secrets. A fork pull request runs `make test` with a read-only token, which is the safe trigger (no `pull_request_target`).
- Actions: all five are GitHub-owned (`actions/checkout@v4`, `setup-python@v5`, `configure-pages@v5`, `upload-pages-artifact@v3`, `deploy-pages@v4`), pinned to major tags. No third-party action. `requirements.lock` pins 20 versions without hashes, and the job that installs them holds a write token (EXPOSURE-6).

**7. Licensing and data**

- FAA subsets: the newest stored `MASTER.txt.gz` has 2,822 in-scope rows with `NAME`, `STREET`, `CITY`, `STATE`, `ZIP CODE` columns. `TYPE REGISTRANT` is code 1 on 18 rows and code 4 on 114. I could not confirm the FAA's meaning of the codes: its layout PDF returned 403. `DEREG.txt.gz` has 1,298 rows with mail and physical address columns. The README's Data section says so, and `GO_PUBLIC.md` D leaves it to the owner. The daily `serials.csv.gz` files carry no names. Not a finding: the FAA publishes these rows, and the disclosure is there.
- Stored third-party text: `data/guidance.csv` holds 28 quotes, longest 47 words; `data/quarter_plans.csv` 6, longest 25; `report/claims.json` 27, longest 39; `docs/build/claims_*.json` at most 40. Every quoted string of 80 words or more under `docs/` is the project's own text. No transcript or article is stored whole.
- `LICENSE` is MIT with the owner's public name, and GitHub detects it as MIT. The README says "The code is under the MIT license", which `LICENSE` covers. The vendored Chart.js (MIT), axe-core (MPL-2.0, tests only) and IBM Plex (`site/fonts/OFL.txt`) keep their own notices.

**8. What a stranger learns about the owner**

- The personal email address, from any clone (EXPOSURE-2).
- The private name (EXPOSURE-1).
- Commit time-zone offsets: 64 commits at -0500 and 57 at -0600. The commit times also show working hours.
- That AI agents built the project (disclosed at `README.md:180`, 98 co-author trailers).
- The audit and build briefs, including the recruiting purpose stated in this round's briefs.
- A private spec folder and a private gate script the public cannot run.
- The owner's Mac setup: a Chrome fallback that downloads into `~/Downloads`, and dotfiles for the SEC user agent and the disclosure sentence. Their contents are not public, only that they exist.
- Interview answers and resume bullets.
- The macOS account name, which is effectively the GitHub account name already.

## Findings

**EXPOSURE-1. S1.** `docs/prepub/DECISIONS.md:36` (hand-written; also line 36 of the uncommitted working copy). The owner's private name for themself.
- Evidence: `git log --all --format=%h -S"<private name>"` prints one commit, `aa273cb` (2026-11-11). 12 of the file's 13 committed versions carry the line, through `e7b9d3d`. Redacted, the line reads: `The spec calls the owner <private name>. Tracked files under docs/prepub/ say "the owner", because ... these files become public with the merge.`
- So decision D8, which exists to keep the name out of public files, is the one place it appears. `aa273cb` is not an ancestor of the lock (`git log --format=%h a44e5ac | grep -c aa273cb` prints 0), and it is on `origin/prepub-audit`, already on GitHub.
- Fix: in the tree, rewrite D8 without the name, in a new commit. For history: accept it with a normal merge, or take the squash route under Answer 4 with its costs.

**EXPOSURE-2. S1.** Commit metadata on all refs. The personal email address is author and committer on 121 commits: 62 on `main`, of which 58 are ancestors of `a44e5ac`, and 59 on `main..prepub-audit`. Decision A is still open; `VERDICT.md:9` lists it as remaining.
- Evidence: `git log --format='%ae' main | sort | uniq -c`, redacted: `47 <Actions bot noreply>`, `62 <personal email>`. On `prepub-audit`: 47 and 121. The same address is the email part of the SEC user agent (`scan_history.py`, hash match).
- Fix: the owner records Decision A in `DECISIONS.md` (accept, or stay private). If accepted, set `git config user.email` to the GitHub noreply address for later commits. A rewrite is not available for the 58 lock ancestors. Defensible version: "62 commits on `main` (58 before the lock) and 121 after the merge carry the address; it cannot be removed without breaking the lock."

**EXPOSURE-3. S2.** Home paths at the tip beyond what Decision B names, and a false "scrubbed" claim. Affected files: `docs/prepub/recompute/notes_head.txt:9`, `docs/prepub/reviews/recompute.txt:9` (both from `9945499`; `recompute.txt` is generated by `docs/prepub/recompute/assemble.py`, which writes `notes_head.txt` at its top, lines 51 and 86-87), `docs/build/DECISIONS.md:32` (hand-written; account name as file owner), and `docs/prepub/EXPOSURE.md:11` (hand-written). `grep -rn "docs/prepub" src/gdn` prints nothing, so no project generator writes these files.
- Evidence: `git grep -c "<home prefix>" prepub-audit -- docs/build` (the grep `GO_PUBLIC.md:12` gives, run on the mirror) lists 16 files, as `GO_PUBLIC.md:12` says. The same grep on `docs/prepub` lists `recompute/notes_head.txt:2` and `reviews/recompute.txt:2`, whose lines carry the account name (`homepaths.py`). `EXPOSURE.md:11` says "the final tree of this branch is scrubbed in P8".
- 36 further files hold home paths only in `prepub-audit` history.
- S2, not S1: the account name is already visible in the repository URL, so the paths add the folder layout, not a new identifier.
- Fix: replace the prefix with `~` in `notes_head.txt` line 9 and rerun `assemble.py`, or make the same one-line edit at line 9 of both files. I found no stored hash of `recompute.txt` (`grep` for `recompute.txt` in `RECORD_HASHES.txt` and the top-level `docs/prepub/*.md` names it only in `PLAN.md` and `RECOMPUTE_DIFF.md`, without a hash). Widen B's check to a script that reads the account name at run time and greps the whole tree for the home prefix or the bare account name, printing paths only. Correct `EXPOSURE.md:11` to say which tip files still hold paths.

**EXPOSURE-4. S2.** Hand-written count in `docs/prepub/GO_PUBLIC.md:9`, `VERDICT.md:9`, `VERDICT.md:50`, `FINDINGS.md:28` and `EXPOSURE.md:10`: "124 commits" of `main` (EXPOSURE.md: "124 commits of origin/main (140 across all refs)").
- Evidence: the runbook's own command on `main` prints 62 for the personal address (see EXPOSURE-2). `main` has 109 commits in all, fewer than 124. 124 is exactly 2 × 62, consistent with counting author and committer lines separately in the scan's `%ae | %ce` header.
- S2 rather than S1: a wrong number in a public file, but about the exposure count, not a figure about GD or the model.
- Fix: "62 commits on `main` (58 of them before the lock), 121 after the merge".

**EXPOSURE-5. S2.** `docs/prepub/` as a stranger first sees it. All files named are hand-written (no generator under `src/gdn` writes `docs/prepub`).
- Evidence: `VERDICT.md:3` "**NO-GO.** Three of the 13 criteria fail". Verdict lines of `reviews/buyside.md`, `registry.md`, `compliance.md`, `round2_editor.md`, `round2_finance.md`, `round2_statistician.md`, `sellside.md` and `statistician.md` read NO-GO (as of their dates). `ls docs/prepub` shows no README or index. No `GO_PUBLIC.md` step updates `VERDICT.md` after Decisions A and B and step 1.
- `README.md:180` sends readers to this folder, so on posting day the first verdict a recruiter reads will be a stale NO-GO.
- Fix: add `docs/prepub/README.md` stating that files are dated working records and naming the current ones. Add a GO_PUBLIC step to append a dated final section to `VERDICT.md` after the decisions, leaving the earlier text as written.

**EXPOSURE-6. S2.** Missing runbook steps to protect the record on GitHub (`GO_PUBLIC.md`, Part 2, hand-written; `.github/workflows/nowcast.yml:6-7`, hand-written).
- Evidence: `gh release view lock-2026Q3` prints `immutable: false`. Nothing in the runbook blocks moving or deleting `lock-*` tags or force-pushing `main`. `nowcast.yml` grants `contents: write` to a job that runs `pip install -r requirements.lock` (20 pinned versions, 0 hashes) twice a day. The lock verifies today; this is hardening a professional would expect, not a present error.
- Fix, after step 4:
  - A tag ruleset on `lock-*` with Restrict updates and Restrict deletions only. GitHub's page "Available rules for rulesets" says that with Restrict deletions "only users with bypass permissions can delete branches or tags" matching the pattern. Do not select Restrict creations: `gitops.py:148` creates the tag through `gh release create --target`.
  - A branch ruleset on `main` that blocks force pushes and deletion only. Do not require pull requests: the bot pushes directly, `gitops.py:121`.
  - Enable immutable releases before the 2026Q4 lock. "Preventing changes to your releases" says "immutability will only apply to future releases", and the page "Immutable releases" says "Only the assets and tag are locked." Never republish `lock-2026Q3`.

**EXPOSURE-7. S3.** `docs/prepub/GO_PUBLIC.md:47` and `:19` (hand-written). The step 2 paragraph says `origin/prepub-audit` "sits at `f14a400`" and that a pull request from it would leave out "the chart legends, the preview image and the final records".
- Evidence: `git for-each-ref` on the mirror: `refs/remotes/origin/prepub-audit 4388294`. `git log --oneline refs/remotes/origin/prepub-audit..prepub-audit` prints only `e7b9d3d`. `daf25c1` (legends, preview image) is in `4388294`.
- Fix: name `4388294` and say only the round 4 records are missing, or say "run the `git log` below" without naming a SHA.

**EXPOSURE-8. S3.** `GO_PUBLIC.md:77-85` (hand-written), step 3b.
- Evidence: the block runs `gh workflow run`, `gh run list`, then `git pull --ff-only` at once. A dispatched run is not finished by then, so the `shasum` check can pass on unchanged local files. `git log -3 --format='%an %s'` prints no paths, so it cannot show "no commit that touches `predictions/`".
- Fix: record `before=$(git rev-parse HEAD)` first; wait for the run to end before the pull (`gh run watch <id>`; I could not run `gh run` here, so its exit-status flag is unverified); then `git log --format='%h %an %s' "$before"..HEAD -- predictions results/live/2026Q3_lock.json results/live/2026Q3_score.json docs/PREREGISTRATION.md` must print nothing, and `git log --oneline "$before"..HEAD` must show the run's commits. `ORIG_HEAD` would be stale if the pull were a no-op.

**EXPOSURE-9. S3.** `GO_PUBLIC.md:27-38` (hand-written), step 1. It says to edit "`README.md` line 15" without naming a branch.
- Evidence: line 15 is the disclosure only on `prepub-audit`. `git show main:README.md | sed -n 15p` prints the table caption "Average miss in aircraft over the 26 held-out quarters".
- Fix: "on `prepub-audit`, before step 2", or locate the line by its text.

**EXPOSURE-10. S3.** Branch hygiene is not in the ordered steps (`GO_PUBLIC.md:19`, Part 2, hand-written).
- Evidence: deleting `origin/codex/fix-daily-merge-and-lock-integrity` and `origin/prepub-audit` appears only under Part 1 E, with no position before step 4. Local `prepub-mergecheck` and `prepub-mergecheck2` are not mentioned. GitHub's page "Removing sensitive data from a repository" says such commits "may still be accessible elsewhere", including cached views reached by commit hash, so deleting `origin/prepub-audit` may not hide its content.
- Fix: a step 3c after the push of `main`. Delete the two remote branches, delete the two local throwaway branches, and never push with `--all` or `--mirror`.

**EXPOSURE-11. S3.** `docs/build/README.md:3` (hand-written): "Every one was last changed on 2026-10-19, the build day, and they are kept as written."
- Evidence: `git log --format='%h %ad' --date=short prepub-audit -- docs/build` shows 5 commits on 2026-11-11. `claims_product.json` changed in `7c2a99f` and `4ad3825`, `claims_risks.json` in `37a72ea`. `src/gdn/claims.py:85-86` merges `docs/build/claims_*.json` on every `make claims`, so they are live inputs, not notes.
- Fix: "The notes were last changed on 2026-10-19. The three `claims_*.json` files are live inputs to `make claims` and change with the note."

**EXPOSURE-12. S3.** `GO_PUBLIC.md:115-120` (hand-written), step 7, "as an outsider would".
- Evidence: the file check is `shasum -a 256 predictions/2026Q3.json`, which reads the working copy. It proves the file today equals the hash, not that the release's tag points at that content. Both hold today: the hash at the tag `a44e5ac` is `3c4cdbd0...6f23`.
- Fix: `git fetch --tags && git rev-parse lock-2026Q3` (expect `a44e5ac...`) and `git show lock-2026Q3:predictions/2026Q3.json | shasum -a 256`.

**EXPOSURE-13. S3.** Hand-written `tools/rehearsal.py:179-180`, plus 10 tip files that mention the private spec folder and 5 the gate.
- Evidence: line 179 builds a path under the home folder to the private gate script, and line 180 one to the gate's virtual environment. Neither is in the repository.
- A public reader cannot run that part. The references show the build was checked against a tool the public cannot see.
- Fix: mark that rehearsal row as owner-only in the tool's docstring. Optionally say in `docs/build/README.md` that the gate and spec are private.

## Improvements that would raise the project's standing

1. Add `docs/prepub/README.md`: one screen, dated, naming `ERRATA.md`, `LOCK_CHECK.md`, `RECORD_HASHES.txt` and the final `VERDICT.md` section as the files that matter.
2. After going public, add the `lock-*` tag ruleset (no deletions, no updates). Before 2026Q4, enable immutable releases, so each new lock's tag cannot move.
3. A short `SECURITY.md` (`isSecurityPolicyEnabled` is false) saying how to report a problem with the record.
4. Install with `pip install --require-hashes` from a hash-pinned lock in `nowcast.yml`, since that job holds a write token.
5. Make the step 7 outsider check a script in `tools/` that anyone can run against the tag and the release. A stranger could then verify the lock in one command.

## Checked and clean

- No token, key, PEM block or the whole SEC user-agent string in any of 927 blobs or 168 commit messages.
- No tracked file was ever removed from history; no agent or editor config, log or cache is tracked.
- The record is intact. `predictions/2026Q3.json` hashes to `3c4cdbd0...6f23` at `lock-2026Q3`, `main` and `prepub-audit`. `results/live/2026Q3_lock.json` and `_score.json` match `RECORD_HASHES.txt`. `prepub-audit` changes nothing under `predictions/`, `results/live/`, `data/snapshots/`, `docs/PREREGISTRATION.md` or `.github/`.
- The release: published `2026-10-29T05:51:24Z` by the Actions bot, notes carry the hash.
- Workflows: explicit `permissions:` in all three, no `pull_request_target`, only GitHub-owned actions, secret not echoed.
- PDF and PNG metadata hold no name or path. Workbook creator is the public name, by design.
- Stored quotes are short (at most 47 words); no transcript is stored whole.
- `LICENSE` is MIT and matches the README. Vendored files keep their notices.
- The post block in `GO_PUBLIC.md` equals `docs/LINKEDIN_POST.md`. The step 1 and step 3 checks hold on today's files.
- `tools/prepub/links.py:126` selects the SEC user agent only for hosts ending in `sec.gov` (but see the redirect suspicion below).

## Suspicions, not proven

- Redirects. `src/gdn/sec.py:74-76` and `tools/prepub/links.py:124-130` call `urllib.request.urlopen`. Its default redirect handler copies the request headers to the new URL. A redirect from sec.gov to another host would therefore carry the SEC user agent. I saw no such redirect. Settled by logging the final URL of each SEC fetch for one run.
- `src/gdn/faa.py:19-20,53` sends a Chrome user-agent string to the FAA, and `README.md:176` says the job does so because the FAA "refuses some automated clients". A reader in the defense sector may read that as working around a federal site's bot control. Settled by the FAA registry download page's terms, which I could not open (its layout PDF returned 403).
- Past Actions run logs may become visible with the flip. The code prints no secret, and GitHub is known to mask secret values in logs (I did not open that page), but I could not read a single run.

## Could not check, and refused commands

- GitHub-side state beyond `gh repo view` and `gh release view`: refs created after today's fetch, `refs/pull/*`, issue and PR history, Actions settings (default token permission, fork approval), Pages settings, and whether the remote tag `lock-2026Q3` points at `a44e5ac`. `git ls-remote` and `gh api` are outside my allowed commands.
- Past workflow run logs (`gh run` is forbidden).
- The FAA's meaning of registrant type codes 1 and 4: the layout PDF at `registry.faa.gov` returned 403, and the one fallback layout file returned 404.
- Contradictions between `docs/prepub/`, `docs/build/` and the final surfaces: I compared only the statements named in Answer 4 and the findings (the commit count, the "scrubbed" claim, the remote SHA, the build-notes date, the verdict state). I did not compare every figure in the two folders with the README, note or dashboard; silence there is not a clean result.
- My history and tree scans (`scan_history.py`, `tree_scan.py`, `blobs.py`) pattern-matched every blob, including other auditors' `round4_*` briefs tracked in `e7b9d3d`. They printed only counts and paths for those files, and I did not open them.
- No command was refused. For the record, I ran some read-only commands outside the list in `round4_common.md`.
  - On the mirror: `git rev-list --all | wc -l`, `git count-objects -vH` and `git config --get` (reads only).
  - In the checkout: `git grep`, read-only, in two shell commands (about ten calls in loops), though my brief allows only `ls-files`, `log` and `show` there.
  - The system `python3` once, to read `report/claims.json`.
  - Nothing was written outside the scratch folder and this file.
