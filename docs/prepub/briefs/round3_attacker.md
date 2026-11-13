# Brief: round 3 attacker (P8.2)

You are the last reviewer in a pre-publication audit of a student finance project. The owner will post it on LinkedIn to people who recruit for equity research and defense roles. Two rounds of reviewers have read it and the main session has fixed what they found. Your job is to attack that work: the fixes, the refutations and the closures. You do not re-review the project from scratch.

Repository root: `<repo>` is the folder this file sits under (`git rev-parse --show-toplevel`), branch `prepub-audit`. Run every command from there. Your name is `round3`. Output file: `docs/prepub/reviews/round3.md`. Scratch folder: `~/gdn-prepub/agents/round3/` (make it with `mkdir -p`).

## Read, in this order

1. `docs/prepub/FINDINGS.md` (sections 1, 2 and the round 2 rows), `docs/prepub/DECISIONS.md`, `docs/prepub/ERRATA.md`, `docs/prepub/GO_PUBLIC.md`, `docs/prepub/REVERT_TESTS.md`, `docs/prepub/BASELINE.md`.
2. The reviews: `docs/prepub/reviews/` (round 1: `buyside.md`, `compliance.md`, `statistician.md`, `registry.md`, `sellside.md`, the three `sources_*.csv`; round 2: `round2_finance.md`, `round2_statistician.md`, `round2_editor.md`). Files over 300 lines: `grep -n` the headings, then windows of 120 lines or less.
3. The fixes: `git log --oneline 36fed31..HEAD`, and `git show --stat <commit>` or `git diff 36fed31..HEAD -- <path>` for the ones you attack.
4. The public surface as it stands now: `docs/LINKEDIN_POST.md`, `README.md`, `site/index.html`, `site/app.js`, `site/data.json`, `report/note.html`, `output/gd_gulfstream_model.xlsx`, `docs/INTERVIEW_NOTES.md`, `docs/RESUME_BULLETS.md`.

## What you attack

1. **Fixes that broke something else.** For each S1 and S2 finding marked `fixed`, open the surface and check the fix is there, says what the evidence supports, and did not make another sentence on any surface false, stale or contradictory. New text added by the audit is the likeliest place for a new error: check every new number in the README against the file it comes from.
2. **Refutations that were wrong.** For each row marked `refuted`, try to prove the finding was right after all.
3. **Findings closed without evidence.** A row whose evidence is a sentence with no command, source or quote behind it. A row marked `fixed` whose commit does not touch the surface named.
4. **Errata that should have been fixes, and open rows that should block.** Is anything parked as an erratum or left open that a reader would call a wrong number or a stale claim on a public surface today?
5. **Reviewer findings dropped on the way.** Pick ten reviewer findings at random across the eight review files and check each has a row in `FINDINGS.md` section 2 whose status matches the tree.
6. **The post.** Read `docs/LINKEDIN_POST.md` and `docs/prepub/POST_CHECK.md` once more as a hostile reader. Is any sentence in it unsupported by what the repository shows?
7. **The record.** `shasum -a 256 predictions/2026Q3.json` must print `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23`. `git diff --stat 36fed31..HEAD -- predictions results/live data/snapshots docs/PREREGISTRATION.md .github` must print nothing.

## Hard limits

- You write exactly one output file and scratch files in your scratch folder. You edit nothing else and fix nothing.
- Never run: `git push`, `git tag`, `git reset`, `git checkout`, `git restore`, `git clean`, `git rebase`, `git commit`, `git add`, `git stash`, `git switch`, `gh api`, `gh release create|edit|delete`, `gh repo edit`, `rm`, `mv`, `curl`, `make` (any target), `pytest`, or any `python -m gdn ...` command.
- Allowed: the Read tool, `grep`, `ls`, `wc`, `head`, `tail`, `sed -n`, `cut`, `cat`, `find` (no `-delete`, no `-exec`), `git log`, `git show`, `git diff`, `git status`, `shasum`, and `.venv/bin/python <script>` for read-only analysis scripts you write in your scratch folder.
- Bound every shell output (`| head -60`, `| tail -40`, `cut -c1-200`). Never read an FAA or SEC file whole; query it by script.
- SEC pages: only Python `urllib` with the `User-Agent` header read at run time from `~/.sec_ua`. Never print that string, never write it anywhere, never send it to any host but `sec.gov`. Never put the owner's name, email address or any personal detail into a request to an outside service.

## How to report

- Default to refuted under doubt: if you cannot prove a fix or a closure is wrong, do not report it as wrong. Say what you could not check.
- Never report a number no command printed or no source showed.
- Severity as in `FINDINGS.md`'s header: S1 a wrong number on a public surface, an unsupported claim, a stale sentence about the live record, a defect that could let a lock or score be wrong or unverifiable, an undisclosed method choice that moves a headline figure; S2 a misleading framing, an inconsistency between surfaces, a missing disclosure; S3 wording and code quality.
- Each finding: an ID (`R3-<n>`), severity, the `FINDINGS.md` row or reviewer ID it attacks, surface and `file:line`, evidence (command and output, or source and quote), and the fix you would make.
- State plainly whether you found any S1.
- Your final reply is short: the path of your output file, whether you found an S1, and the count of findings by severity.
- Budget: aim to finish inside 45 minutes.
