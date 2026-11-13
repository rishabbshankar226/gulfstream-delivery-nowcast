# Going public: the owner's checklist

Written 2026-11-11 by the pre-publication audit. Nothing here has been done. The audit pushed nothing, changed nothing on GitHub and ran no daily job, lock or score. Every step below is yours, in this order. Each has its check.

Read `ROUND4_VERDICT.md` first; `VERDICT.md` is the earlier verdict. If it says NO-GO, the list of what remains is there, and most of it is the decisions in part 1.

## Part 0. The privacy route (chosen 2026-11-12)

You chose a public repository with no personal data in it, its history included (DECISIONS D25). That settles decisions A and B, and the private name in the branch history (F110). The way to do it is to rewrite the history once, before the repository is ever public, and push the rewritten history over the old one.

What the rewrite keeps and changes:

- Every record file stays byte for byte: `predictions/`, `results/live/`, `data/snapshots/`, `docs/PREREGISTRATION.md` and `.github/`.
- `predictions/2026Q3.json` keeps its sha256, so it still matches the `lock-2026Q3` release notes.
- The lock commit keeps its date (2026-10-29 05:51:22 UTC) and its author (`github-actions[bot]`).
- The release itself is not edited. Step 0 checks, on a throwaway repository, that moving a release's tag leaves the release published with the same `published_at`.
- What changes: every commit hash, the lock commit's included (`a44e5ac` becomes a new hash), and so the `lock-2026Q3` tag moves to the new commit.
- The release's `targetCommitish` still names `a44e5ac`. ERRATA E11 says so.

A rehearsal on 2026-11-12, in this runbook's order (no-reply email set, `prepub-audit` merged into `main`, then the script), found:

| Across all 193 commits | Before | After |
|---|---|---|
| Commit emails that are not a no-reply or bot address | 290 | 0 |
| Home-folder prefix | 177 | 0 |
| Account name in an `ls -l` owner column | 2 | 0 |
| Private name | 4 | 0 |
| Words naming the old address's mail provider | 16 | 0 |
| Phrases narrowing the account name | 1 | 0 |

It also found every record file identical at every branch tip and tag, and the lock file's hash unchanged. No binary file in history (83 PDFs, workbooks, PNGs and compressed snapshots) holds any of these values (`DECISIONS.md` D25).

Do these steps in order. They replace decisions A and B below, and they replace steps 2 and 2b of part 2.

0. **Try the tag move on a throwaway repository first.** This audit could not check how GitHub treats a release whose tag is force-moved, and the release's `published_at` is the one thing that cannot be made again.
   - Make a private test repository with two commits, A and B. Tag A as `t1`, and publish a release on `t1`.
   - Note the release's `publishedAt` with `gh release view t1 --json publishedAt,isDraft,targetCommitish`.
   - Run `git tag -f t1 B && git push --force origin t1`, then the same `gh release view`.
   - Go on only if the release is still published (`isDraft` false) and `publishedAt` is unchanged. If not, stop: see "If this route fails" below. Delete the test repository afterwards.
1. **Stop the workflow.** On GitHub, open Actions, then the nowcast workflow, and choose "Disable workflow". Nothing must commit while you rewrite.
   - Check: the workflow shows as disabled.
2. **Hide your email from now on.**
   - Settings (your account), Emails: turn on "Keep my email addresses private" and "Block command line pushes that expose my email". Copy the no-reply address shown there.
   - In this checkout: `git config user.email <that no-reply address>`.
3. **Date the position statement:** step 1 of part 2, on `prepub-audit`.
4. **Bring `main` up to date, then merge:** `git fetch && git switch main && git pull --ff-only && git merge --no-ff prepub-audit`.
   - Check: `git merge-base --is-ancestor origin/main main && echo ok` prints ok.
   - Check: `make test` passes, and `make all` then `git status --short` prints nothing.
5. **Rewrite into a new mirror.** Use the personal address you are removing as the old email, and the no-reply address as the new one:

   ```
   PRIVATE_NAME='<your private name>' python3 tools/prepub/rewrite_history.py --old-email '<the personal address>' --new-email '<your no-reply address>' --out ~/gdn-rewrite.git
   ```

   - It refuses to run if `main` lacks any commit of `origin/main`.
   - It ends with `ALL CHECKS PASSED` only when every "After" count is 0. That includes "any non-noreply email in metadata", which catches a wrong `--old-email`.
   - It writes `~/gdn-rewrite.git.commit_map.csv` (old SHA, new SHA) and prints the push commands.
   - The audit ran it in this order on 2026-11-12: `ALL CHECKS PASSED` (DECISIONS D25).
6. **Push the rewritten history.** Push to the repository's URL, not to the mirror's `origin`: a mirror clone refuses named refspecs on its own remote. Run the commands it printed, with `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast.git` in place of `origin`: force-push `main`, force-push the tag `lock-2026Q3`, then delete `prepub-audit` and `codex/fix-daily-merge-and-lock-integrity` on GitHub.
   - Check: `git ls-remote --heads origin` lists `main` only.
   - Check: `git ls-remote --tags origin` shows `lock-2026Q3` at the new lock hash the script printed.
   - Check: `gh release view lock-2026Q3 --json publishedAt,isDraft` still prints `2026-10-29T05:51:24Z` and `false`.
7. **Retire this checkout and set up a fresh one.** This checkout still holds the old history.
   - Rename its folder, then `git clone` a fresh copy from GitHub. Never push from the old folder again: a push from it would bring the old commits back.
   - In the fresh clone:
     - copy `data/raw/` across from the old folder (it is untracked; without it `make claims` drops every claim);
     - make the environment with `python3.11 -m venv .venv && .venv/bin/python -m pip install -r requirements.lock`;
     - copy the untracked `CLAUDE.md` across if you use it;
     - run `git config user.email <your no-reply address>`.
   - Check: `make claims` prints `report/claims.json: 44 claims`, and `make test` passes.
8. **Ask GitHub to purge the old commits, while the repository is still private.**
   - At support.github.com, ask GitHub to "remove cached views and unreachable commits" for this repository, after a history rewrite to remove personal data. Attach the old SHAs from the commit map.
   - Ask them as well to remove pull request #1. Its ref, `refs/pull/1/head` at `163eac0` (the merged codex branch), cannot be force-updated and keeps old commits reachable.
   - Wait for their reply.
   - Check, still private and logged in: `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast/commit/a44e5aca3756941a075150d9e381020826f3fb81` returns 404, and `git ls-remote origin 'refs/pull/*'` prints nothing.
9. **Record it, in the fresh clone, once the purge is confirmed.**
   - Add `docs/prepub/COMMIT_MAP.csv` (copy `~/gdn-rewrite.git.commit_map.csv`) so that every SHA the audit notes cite can be looked up. Add it only after step 8's checks pass, because it lists every old SHA.
   - Add ERRATA E11: "History rewritten on <date> to remove personal data. Every commit hash changed. The lock commit `a44e5ac` is now `<new>`, and the `lock-2026Q3` tag points at it. `predictions/2026Q3.json` is byte-identical, and its sha256 still equals the release notes. The release and its `published_at` are unchanged. Its `targetCommitish` still names `a44e5ac`, and so does the `commit` field of `results/live/2026Q3_lock.json` (and of `site/data.json`, which copies it). That file is part of the record and stays as written; nothing in the code reads the field back."
   - Add one sentence to the README's `## Method`, at the end of the **Live.** paragraph: "On <date> I rewrote this repository's history to remove personal data; the `lock-2026Q3` tag now points at the rewritten lock commit, and the locked file and its sha256 are unchanged ([ERRATA](docs/prepub/ERRATA.md) E11)."
   - Add one line to `LOCK_CHECK.md` naming the new lock hash.
   - Commit and push.
10. **Expect one new gate failure.** v1's gate (`L3`) compares that `commit` field with the tag's commit, so it fails after the rewrite for this reason alone. Log it in `DECISIONS.md` under R11 with E11.
11. **Restart the workflow** (Actions, nowcast, Enable workflow). Then carry on from step 3 of part 2. Steps 2 and 2b of part 2 are done.

**If this route fails** (step 0 shows the release changes, or GitHub Support declines step 8), do not make this repository public: its old commits would stay reachable. There are two ways to go:

- **Keep this repository private.** The lock stays checkable by its owner only.
- **Push the rewritten mirror to a new, empty repository and make that one public.** It has no old objects and no pull request refs. The cost is real: the new repository has no `lock-2026Q3` release, so the 2026Q3 lock's GitHub timestamp stays in the private one. The README must then say that the first lock can be checked only against the file's sha256, not against a public release.

**Security settings for the public repository** (do them with step 4b of part 2):

- Settings, Code security: turn on secret scanning with push protection, Dependabot alerts, and private vulnerability reporting. `SECURITY.md` points reporters to private vulnerability reporting.
- Settings, Actions, General: require approval to run workflows from fork pull requests. Set the default workflow permissions to read.
- The `SEC_UA` Actions secret holds the email address the SEC user agent carries. It is masked in logs and sent to sec.gov only. If you want that address kept private as well, use a separate address in the secret.

What stays public by design: your name, `rshankar.dev` and your GitHub handle, in the README, the note and the links. The FAA's own public file, with registrants' names and addresses, is in the stored snapshots (decision D); they are part of the record and cannot change.

## Part 1. Decisions only you can make (before any step in part 2)

**A. Your email address in the commit history (finding F015). Decided 2026-11-12: removed by the rewrite in part 0.** The text below is how the choice stood before. `git log --format='%ae' | sort | uniq -c` on `main` shows your personal address as the author of 62 commits, 58 of them under the lock commit `a44e5ac`. Every commit on `prepub-audit` that `main` lacks carries it too: a normal merge in step 2 adds all of them, and `git merge --squash` adds one (round 4, F112). A public repository shows it to anyone who clones. It cannot be removed without rewriting history, and a rewrite changes the hash of the lock commit (`a44e5ac`), which the `lock-2026Q3` release and its notes point at. So the choice is: accept it, or do not make this repository public.
- Check after you decide: none. Write your decision in `docs/prepub/DECISIONS.md`.

**B. Home-folder paths in the build notes and in history (F016). Decided 2026-11-12: removed by the rewrite in part 0.** The text below is how the choice stood before. `git grep -c "/Users/" -- docs/build` lists 16 files under `docs/build/briefs/`. The folder name in them is your macOS account name. Same choice as A for history. For the tree, you can leave the build notes as written (the README says they are kept as written) or replace the prefix with `~`.

**C. The G700 type code the scope rule drops (F056, `ERRATA.md` E5).** The FAA files G700 code `3980222` under engine-type code 2, and the preregistered rule keeps 4 and 5. In the FAA file of 2026-10-30, 17 G700s registered to Gulfstream sat under that code. None had been delivered. When they are, the count will miss them. Before the 2026Q4 window closes on 2026-12-31, either amend the rule in `src/gdn/faa.py` (name the code, date the change in the README and in a new section of `ERRATA.md`, never in the preregistration, and expect every later stored subset to hold those rows) or keep the rule and keep the README's Holder and scope limitation.
- Check if you amend: `make test` passes, and the dashboard's count of G700s on Gulfstream's own registration rises by the number of rows under that code.

**D. The stored FAA subsets hold registrants' names and street addresses (F070).** They are the FAA's public file as released, and the README's Data section now says so. Decide whether you are content to republish them.

**E. What goes public with the merge (F071).** `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md` and this audit's folder `docs/prepub/` become public. The README says the audit notes are there. The remote branch `origin/codex/fix-daily-merge-and-lock-integrity` also becomes public; its two commits are merged, so you can delete it after the merge with `git push origin --delete codex/fix-daily-merge-and-lock-integrity`. So does `origin/prepub-audit`, which appeared on GitHub on 2026-11-12 (the audit did not push it); delete it the same way once `main` holds the merge, or keep it.

## Part 2. Steps, in order

### 1. Confirm you hold no position in General Dynamics (F081)

On `prepub-audit`, before step 2, the README says "I hold no position in General Dynamics" (find it with `grep -n "I hold no position" README.md`). The note says "The author holds no position in General Dynamics." on page 1 and in every page footer. The build copies that sentence forward; it carries no date. Only you can state it.

If it is true today, date it in both places. First edit that line of `README.md` so the sentence reads "I hold no position in General Dynamics as of <today's date>, and I am not affiliated with General Dynamics, Gulfstream or the FAA." Then:

```
printf '%s\n' "The author holds no position in General Dynamics as of $(date +%F)." > ~/.gdn_disclosure
PYTHONPATH=src .venv/bin/python -m gdn note && make pdf
```

If it is not true, write the true sentence into `~/.gdn_disclosure` and into that line of `README.md` before anything else, then run the same two commands.

- Check: `grep -o '<p id="disclosure">[^<]*' report/note.html` prints your sentence, and `shasum -a 256 report/note.html | cut -c1-64` equals `cut -c1-64 output/GD_research_note.inputs.sha256`.
- Check: `grep -n "I hold no position" README.md` shows the dated sentence.
- Commit by path: `git add README.md report/note.html output/GD_research_note.pdf site/GD_research_note.pdf output/GD_research_note.inputs.sha256 && git commit -m "Date the position disclosure"`.

### 2. Merge `prepub-audit` into `main`

```
git switch main && git pull --ff-only
git merge --no-ff prepub-audit
```

When the audit ended, `prepub-audit` already held every commit of `origin/main` (`8c7692f`, the workflow's 2026-11-12 run, merged in `bbf88fd`), so the merge was clean. Merge the local branch. `origin/prepub-audit` on GitHub may be behind it: `git log --oneline origin/prepub-audit..prepub-audit` lists what it lacks. Do not merge through a GitHub pull request: its `refs/pull/*/head` keeps every branch commit reachable after the branch is deleted. If you chose a squash merge in decision A or under `ROUND4_VERDICT.md` A.3, run `git merge --squash prepub-audit && git commit` in place of `git merge --no-ff prepub-audit`. The daily workflow commits to `main` twice a day. If it has committed since, the merge will stop on files both sides rewrote. Every such file is a generated output (`README.md`, `report/note.html`, `site/data.json`, `docs/LINKEDIN_POST.md`, the workbook, the PDFs, the charts under `output/charts/`, `site/preview.png`, and their stamps). For each one take either side, then rebuild them all from the merged data and code:

```
git checkout --theirs -- <each conflicted file>
make all && make claims && PYTHONPATH=src .venv/bin/python -m gdn note && make pdf
git add <the same files> && git commit
```

Never resolve a conflict in `predictions/`, `results/live/`, `data/snapshots/` or `docs/PREREGISTRATION.md` by hand: the audit did not touch them, so `main`'s side is the only side.

- Use the project's environment: Python 3.11 with `requirements.lock` installed (the README's Reproduce section). The system `python3` on this Mac is 3.9.6 and cannot install the pinned requirements.
- Check: `make test` ends with no failure (198 tests passed when round 4's fix pass ended; a clone without the untracked `data/raw/` folder prints 196 passed and 2 skipped). `make all` then `git status --short` prints nothing. `shasum -a 256 predictions/2026Q3.json` prints `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`.

### 2b. Clean up the branches that would go public

A public repository shows every branch on GitHub. `origin/codex/fix-daily-merge-and-lock-integrity` is merged and `origin/prepub-audit` is merged once step 2 is pushed. The local throwaway branches `prepub-mergecheck` and `prepub-mergecheck2` were never pushed and stay on this Mac only.

```
git push origin main
git push origin --delete codex/fix-daily-merge-and-lock-integrity
git push origin --delete prepub-audit
```

- Check: `git ls-remote --heads origin` lists `main` only, and `git ls-remote --tags origin` lists `lock-2026Q3` only.

### 3. Set the public flag

Edit `config/calendar.json`: set `"public": true` and add `"public_since": "<the date you will make the repository public, YYYY-MM-DD>"`. Then:

```
make all && make claims && PYTHONPATH=src .venv/bin/python -m gdn note && make pdf
```

What it changes: a lock published on or after `public_since` is called a "public GitHub release" on the README, the note and the dashboard. The 2026Q3 lock was published on 2026-10-29, before that date, so it keeps "made while the repository was private". In a scratch copy with `"public_since": "2026-11-12"` the rebuild changed two fields of `site/data.json` (`public`, `public_since`) and nothing in the README or the note.

- Check: `git diff --stat README.md report/note.html` prints nothing, and `git diff --stat` lists `config/calendar.json` and `site/data.json`. `grep -c "made while the repository was private" README.md` prints 1 or more. `grep -c "public lock" README.md report/note.html` prints 0 for both.
- Commit by path, then `git push origin main`.

### 3b. Run the merged daily job once, while the repository is still private

The merge changes the daily job (the two outside commits, the lock and score guards, the charts stage). Its tests pass, and the job has never run end to end on GitHub in its merged form. Run it once before anyone can see the result:

```
gh workflow run nowcast.yml
gh run list --workflow nowcast.yml -L 1
gh run watch "$(gh run list --workflow nowcast.yml -L 1 --json databaseId -q '.[0].databaseId')"
git pull --ff-only
shasum -a 256 predictions/2026Q3.json results/live/2026Q3_lock.json results/live/2026Q3_score.json
grep -E "predictions/2026Q3.json|results/live/2026Q3_lock.json|results/live/2026Q3_score.json" docs/prepub/RECORD_HASHES.txt
```

- Check: the run ends `completed  success`; the three hashes printed by `shasum` equal the three lines printed by `grep`; `git log --oneline -3 -- predictions/ results/live/2026Q3_lock.json results/live/2026Q3_score.json` shows no commit newer than the 2026Q3 lock and score.
- If the run fails, do not go on. Read its log (`gh run view --log-failed`), and keep the repository private until a run is green.

### 4. Make the repository public

GitHub, the repository's Settings, General, Danger Zone, Change repository visibility, Public.

- Check: in a logged-out browser window, `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast` opens, the README's live summary reads "one locked quarter, a miss outside its band", and its first chart (`output/charts/track_record.png`) renders.

### 4b. Protect the record on GitHub (round 4, F129)

Do this straight after step 4, before the post. Once the repository is public nothing else stops a moved tag or a force-push. The option names below are as I expect GitHub to show them; this audit did not open those settings pages. If the words differ, pick the rules that stop updates, deletions and force pushes.

- Settings, Rules, Rulesets, New tag ruleset: target `lock-*`, enforcement Active, and turn on "Restrict updates" and "Restrict deletions".
- Settings, Rules, Rulesets, New branch ruleset: target the default branch, and turn on "Block force pushes" and "Restrict deletions". The daily workflow pushes ordinary commits, which these rules allow.
- If Settings offers immutable releases, turn them on before the 2026Q4 lock. They apply to later releases only.
- Never edit, delete or republish the `lock-2026Q3` release: republishing would replace the timestamp that is the record.
- Check: `gh api repos/rishabbshankar226/gulfstream-delivery-nowcast/rulesets --jq '.[].name'` lists both rulesets.

### 5. Enable Pages and deploy

Settings, Pages, Source: GitHub Actions. Then:

```
gh workflow run pages
gh run list --workflow pages -L 1
```

The pages workflow runs on a push that touches `site/**` or by hand. The daily job's own pushes do not start it (`ERRATA.md` E1), so this command is also step 9's.

- Check: the run list shows `completed  success`.

### 6. Open everything from a logged-out browser

- `https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/`: the live card reads Scored, 32.0 against GD's 40, a miss of 8.0, outside the band; the lead says the same quarter last year missed by less.
- The research note link on the dashboard opens an 8-page PDF whose page footer starts "Student research project. Not investment advice."
- From the README: the dashboard link, the note, the workbook, `docs/PREREGISTRATION.md`, `docs/prepub/ERRATA.md`, `results/exploratory/sensitivity.md`, `data/quarter_plans.csv`.
- Both links in the post (`POST_CHECK.md`).
- `https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/preview.png` shows the track-record chart. It is the image LinkedIn will show for the dashboard link (`og:image`). LinkedIn's Post Inspector (`https://www.linkedin.com/post-inspector/`) shows the preview before you post. The link check does not read meta tags, so this URL is not in `LINKS.csv`.

### 7. Check the lock as an outsider would

- Open `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast/releases/tag/lock-2026Q3` logged out. The notes carry `sha256 3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`.
- `gh release view lock-2026Q3 --json publishedAt,author` prints `2026-10-29T05:51:24Z` and `github-actions[bot]`.
- `git show lock-2026Q3:predictions/2026Q3.json | shasum -a 256` prints the same hash: the file as the tag holds it, not the working copy.
- GD's 8-K (accession 0000040533-26-000036) was accepted by the SEC at 2026-10-30 08:09:27 ET, 30 hours later (`LOCK_CHECK.md`).

### 8. Post

Paste this text. It is `docs/LINKEDIN_POST.md` as the generator writes it, 1,282 characters (round 4 added the band's coverage and called the pace mine). If step 2 or 3 rebuilt the post, paste the file as it stands then, and check `wc -m docs/LINKEDIN_POST.md` is under 1,300.

```
My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics (GD) reported 40.
My tracker scales FAA registrations into an estimate of the Gulfstream jets GD reports each quarter, locked on GitHub the day before GD reports.

The 2026Q3 miss was 8.0, outside my 80% band of past misses (it held 18 of 26 past quarters). My pace from GD's full-year outlook missed by 6.2, and last year's same quarter (39) by 1. The repository was private then; the timestamp is GitHub's.

Backtest (rules set minutes before scoring): Over 26 held-out quarters the registry count was off by 5.5 jets a quarter on average, against 6.9 for GD's guidance pace. The difference is not statistically distinguishable. Repeating the same quarter last year missed by less on average, 4.6. (Registry count: my scaled estimate; the pace: mine.) The test reads a registry copy that had months or years to fill in, so only locked quarters show if it counts jets in time. One quarter is one data point.

Dashboard: https://rishabbshankar226.github.io/gulfstream-delivery-nowcast/
Code: https://github.com/rishabbshankar226/gulfstream-delivery-nowcast

Student project, not investment advice. I am not affiliated with General Dynamics or Gulfstream.

#EquityResearch #Aerospace
```

Two alternates with other openings are in `POST_ALTERNATES.md`.

The repository's description on GitHub reads "Gulfstream deliveries estimated from FAA registrations, tested on 26 held-out GD quarters, each live estimate locked". It is true. You may want it to carry the result as well.

## Part 3. After the post, and before the next lock

### 9. After every lock and every score

The workflow cannot build the PDF or retake the README's screenshot, and its pushes do not redeploy Pages (`ERRATA.md` E1, E3).

```
git switch main && git pull --ff-only
make pdf
```

Commit the PDFs and the stamp by path, push, then `gh workflow run pages`. `output/charts/dashboard.png` is a screenshot of the dashboard that no page links to any more; retake it with `tools/shoot.py` when the page changes, or delete it.

- Check: `shasum -a 256 report/note.html | cut -c1-64` equals `cut -c1-64 output/GD_research_note.inputs.sha256`, and the dashboard shows the new state logged out.

### 10. Before the 2026Q4 lock

- When GD announces its fourth-quarter release date, add it to `config/calendar.json` under `releases` as `"2026Q4": "YYYY-MM-DD"`. Without it no lock is made (`ERRATA.md` E4). Check: the README's Live record no longer says "No release date is set".
- Add 2027Q1's fiscal quarter end under `fiscal_ends` from GD's filings.
- The 2026-10-30 call is in `data/guidance.csv` with a blank outlook (GD said "We do not plan to update segment guidance."), so the 2026Q4 pace still rests on the 160 of 2026-07-29. Add each later call the same way, with its quote, speaker and link. Check: `make all` changes no held-out figure. `tools/build_guidance.py` is the build-time tool that first wrote the file from checker files and cached transcripts; no Makefile target or daily step runs it. If you ever rerun it, cache the 2026-10-30 transcript under `data/raw/sources/calls/` first and give it a checker row, or the tool will write the file without that call (F107).
- Decide C above.
- On the release date's eve, check by noon ET that the release `lock-2026Q4` exists (`gh release view lock-2026Q4`). The workflow's runs land four to seven hours after their cron time (`ERRATA.md` E2). If there is no lock, run `make daily` on the Mac before midnight ET.
