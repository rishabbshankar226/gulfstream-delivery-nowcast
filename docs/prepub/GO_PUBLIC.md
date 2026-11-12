# Going public: the owner's checklist

Written 2026-11-11 by the pre-publication audit. Nothing here has been done. The audit pushed nothing, changed nothing on GitHub and ran no daily job, lock or score. Every step below is yours, in this order. Each has its check.

Read `VERDICT.md` first. If it says NO-GO, the list of what remains is there, and most of it is the decisions in part 1.

## Part 1. Decisions only you can make (before any step in part 2)

**A. Your email address in the commit history (finding F015).** `git log --format='%ae' | sort | uniq -c` on `main` shows your personal address as the author of 124 commits. A public repository shows it to anyone who clones. It cannot be removed without rewriting history, and a rewrite changes the hash of the lock commit (`a44e5ac`), which the `lock-2026Q3` release and its notes point at. So the choice is: accept it, or do not make this repository public.
- Check after you decide: none. Write your decision in `docs/prepub/DECISIONS.md`.

**B. Home-folder paths in the build notes and in history (F016).** `git grep -c "/Users/" -- docs/build` lists 16 files under `docs/build/briefs/`. The folder name in them is your macOS account name. Same choice as A for history. For the tree, you can leave the build notes as written (the README says they are kept as written) or replace the prefix with `~`.

**C. The G700 type code the scope rule drops (F056, `ERRATA.md` E5).** The FAA files G700 code `3980222` under engine-type code 2, and the preregistered rule keeps 4 and 5. In the FAA file of 2026-10-30, 17 G700s registered to Gulfstream sat under that code. None had been delivered. When they are, the count will miss them. Before the 2026Q4 window closes on 2026-12-31, either amend the rule in `src/gdn/faa.py` (name the code, date the change in the README and in a new section of `ERRATA.md`, never in the preregistration, and expect every later stored subset to hold those rows) or keep the rule and keep the README's Holder and scope limitation.
- Check if you amend: `make test` passes, and the dashboard's count of G700s on Gulfstream's own registration rises by the number of rows under that code.

**D. The stored FAA subsets hold registrants' names and street addresses (F070).** They are the FAA's public file as released, and the README's Data section now says so. Decide whether you are content to republish them.

**E. What goes public with the merge (F071).** `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md` and this audit's folder `docs/prepub/` become public. The README says the audit notes are there. The remote branch `origin/codex/fix-daily-merge-and-lock-integrity` also becomes public; its two commits are merged, so you can delete it after the merge with `git push origin --delete codex/fix-daily-merge-and-lock-integrity`.

## Part 2. Steps, in order

### 1. Confirm you hold no position in General Dynamics (F081)

The README (line 15) says "I hold no position in General Dynamics". The note says "The author holds no position in General Dynamics." on page 1 and in every page footer. The build copies that sentence forward; it carries no date. Only you can state it.

If it is true today, date it:

```
printf '%s\n' "The author holds no position in General Dynamics as of $(date +%F)." > ~/.gdn_disclosure
PYTHONPATH=src .venv/bin/python -m gdn note && make pdf
```

If it is not true, write the true sentence into `~/.gdn_disclosure` and into `README.md` line 15 before anything else, then run the same two commands.

- Check: `grep -o '<p id="disclosure">[^<]*' report/note.html` prints your sentence, and `shasum -a 256 report/note.html | cut -c1-64` equals `cut -c1-64 output/GD_research_note.inputs.sha256`.
- Commit by path: `git add report/note.html output/GD_research_note.pdf site/GD_research_note.pdf output/GD_research_note.inputs.sha256 && git commit -m "Date the position disclosure"`.

### 2. Merge `prepub-audit` into `main`

```
git switch main && git pull --ff-only
git merge --no-ff prepub-audit
```

When the audit ended, `origin/main` was still at `36fed31`, the commit `prepub-audit` was cut from, so the merge was clean. The daily workflow commits to `main` twice a day. If it has committed since, the merge will stop on files both sides rewrote. Every such file is a generated output (`README.md`, `report/note.html`, `site/data.json`, `docs/LINKEDIN_POST.md`, the workbook, the PDFs and their stamps). For each one take either side, then rebuild them all from the merged data and code:

```
git checkout --theirs -- <each conflicted file>
make all && make claims && PYTHONPATH=src .venv/bin/python -m gdn note && make pdf
git add <the same files> && git commit
```

Never resolve a conflict in `predictions/`, `results/live/`, `data/snapshots/` or `docs/PREREGISTRATION.md` by hand: the audit did not touch them, so `main`'s side is the only side.

- Use the project's environment: Python 3.11 with `requirements.lock` installed (the README's Reproduce section). The system `python3` on this Mac is 3.9.6 and cannot install the pinned requirements.
- Check: `make test` ends with no failure (176 tests passed when the audit ended). `make all` then `git status --short` prints nothing. `shasum -a 256 predictions/2026Q3.json` prints `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`.

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
git pull --ff-only
shasum -a 256 predictions/2026Q3.json results/live/2026Q3_lock.json results/live/2026Q3_score.json
grep -E "predictions/2026Q3.json|results/live/2026Q3_lock.json|results/live/2026Q3_score.json" docs/prepub/RECORD_HASHES.txt
```

- Check: the run ends `completed  success`; the three hashes printed by `shasum` equal the three lines printed by `grep`; `git log -3 --format='%an %s'` shows the workflow's daily commits and no commit that touches `predictions/`.
- If the run fails, do not go on. Read its log (`gh run view --log-failed`), and keep the repository private until a run is green.

### 4. Make the repository public

GitHub, the repository's Settings, General, Danger Zone, Change repository visibility, Public.

- Check: in a logged-out browser window, `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast` opens and the README's first image shows the card "SCORED: MISSED BY 8.0 OUTSIDE THE BAND".

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

### 7. Check the lock as an outsider would

- Open `https://github.com/rishabbshankar226/gulfstream-delivery-nowcast/releases/tag/lock-2026Q3` logged out. The notes carry `sha256 3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`.
- `gh release view lock-2026Q3 --json publishedAt,author` prints `2026-10-29T05:51:24Z` and `github-actions[bot]`.
- `shasum -a 256 predictions/2026Q3.json` prints the same hash.
- GD's 8-K (accession 0000040533-26-000036) was accepted by the SEC at 2026-10-30 08:09:27 ET, 30 hours later (`LOCK_CHECK.md`).

### 8. Post

Paste this text. It is `docs/LINKEDIN_POST.md` as the generator writes it, 1,280 characters. If step 2 or 3 rebuilt the post, paste the file as it stands then, and check `wc -m docs/LINKEDIN_POST.md` is under 1,300.

```
My first locked estimate of Gulfstream deliveries missed: I said 32.0 for 2026Q3, General Dynamics reported 40.
My tracker scales FAA registrations into an estimate of the Gulfstream jets General Dynamics (GD) reports each quarter, locked on GitHub the day before GD reports.

The 2026Q3 miss was 8.0, outside my 80% band of past misses. A pace I derived from GD's own full-year outlook missed by 6.2, and last year's same quarter (39) by 1. The repository was private then; the timestamp is GitHub's.

Backtest, held out from setting the rules: Over 26 held-out quarters the registry count was off by 5.5 jets a quarter on average, against 6.9 for GD's guidance pace. The difference is not statistically distinguishable. Simply repeating the same quarter last year missed by less on average, 4.6. (Registry count: my scaled estimate; the pace: mine.) It reads a registry copy that had months or years to fill in, so only locked quarters show whether it counts jets in time. One quarter is one data point.

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

Retake `output/charts/dashboard.png` from the live dashboard, commit both by path, push, then `gh workflow run pages`.

- Check: `shasum -a 256 report/note.html | cut -c1-64` equals `cut -c1-64 output/GD_research_note.inputs.sha256`, and the dashboard shows the new state logged out.

### 10. Before the 2026Q4 lock

- When GD announces its fourth-quarter release date, add it to `config/calendar.json` under `releases` as `"2026Q4": "YYYY-MM-DD"`. Without it no lock is made (`ERRATA.md` E4). Check: the README's Live record no longer says "No release date is set".
- Add 2027Q1's fiscal quarter end under `fiscal_ends` from GD's filings.
- The 2026-10-30 call is in `data/guidance.csv` with a blank outlook (GD said "We do not plan to update segment guidance."), so the 2026Q4 pace still rests on the 160 of 2026-07-29. Add each later call the same way, with its quote, speaker and link. Check: `make all` changes no held-out figure.
- Decide C above.
- On the release date's eve, check by noon ET that the release `lock-2026Q4` exists (`gh release view lock-2026Q4`). The workflow's runs land four to seven hours after their cron time (`ERRATA.md` E2). If there is no lock, run `make daily` on the Mac before midnight ET.
