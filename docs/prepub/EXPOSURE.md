# What going public exposes (P3.5)

A public repository shows its whole history, every branch and every tracked file. Scans run 2026-11-11, about 20:00 ET. The scan script is `~/gdn-prepub/scratch/exposure.py`: it reads `git log -p --no-color --format='COMMIT %H %an <%ae> | %cn <%ce>' <range>` line by line and tests every added line, and every commit header, against the patterns below. It never prints the SEC user-agent string.

| # | Scan | Command | Result |
|---|---|---|---|
| 1 | The SEC user-agent string from `~/.sec_ua`, whole, and the email address inside it | `python3 exposure.py . ` (all refs) | `sec_ua_whole: 0 added lines`, `sec_ua_email: 0 added lines`. Clean |
| 2 | Tokens and keys: GitHub tokens (`ghp_`, `gho_`, `ghs_`, `github_pat_`), `sk-` keys, AWS `AKIA`, Slack `xox`, Google `AIza`, PEM private keys, and `api_key/secret/password/token = "..."` assignments | same | `token: 0 added lines, 0 distinct`. Clean. (A first pass matched `sk-` inside the claim ids `risk-...`, such as `risk-supply-chain-disruption`; the pattern now needs `sk-` to start a word.) |
| 3 | Email addresses in file content | same | 10 added lines, 5 distinct, all placeholders in tests and the rehearsal tool: `test@example.invalid`, `rehearsal@example.invalid`, `test@example.com`, `t@example.invalid`, `other@example.invalid`. Clean |
| 4 | Email addresses in commit metadata | same, commit headers | **Hit.** The owner's personal email address is the author and committer email on 124 commits of `origin/main` (140 across all refs, counting this branch). The workflow's commits carry GitHub's bot address |
| 5 | `/Users/` home paths | same | **Hit.** `~` on 24 added lines in 5 commits of `origin/main`, all in `docs/build/briefs/*.md` (first commits `5c84d36f`, `6bef3063`, `9b843848`). This branch adds more in `docs/prepub/` and `tools/prepub/`; the final tree of this branch is scrubbed in P8, but the branch's own earlier commits keep them |
| 6 | Remote branches | `git branch --list -r` | `origin/main`, `origin/codex/fix-daily-merge-and-lock-integrity`. The codex branch holds nothing sensitive (placeholder emails in tests only). Once its two commits are merged it is a stale public branch |
| 7 | Tags | `git log --tags --no-walk --format='%D %h %ad'` | `tag: lock-2026Q3 a44e5ac 2026-10-29`, the only tag |
| 8 | Tracked dotfiles | `git ls-files \| grep -E '(^\|/)\.[^/]+'` | `.gitattributes`, `.github/workflows/nowcast.yml`, `.github/workflows/pages.yml`, `.github/workflows/test.yml`, `.gitignore`. No `.env`, no editor or agent settings. `CLAUDE.md` and `.claude/` are ignored (`.gitignore`) |
| 9 | License | `head -4 LICENSE` | `MIT License`, `Copyright (c) 2026 Rishabb Shankar`. Present |
| 10 | Stored transcript or article text | word counts by script | `data/guidance.csv`: 27 quotes, longest 47 words, 643 words in all, none over 60. `report/claims.json`: 31 quotes, longest 39 words. `docs/build/claims_*.json`: longest 40 words. `docs/build/AIRFRAME_AUDIT.csv` notes: longest 74 words, the owner's own notes with short quoted fragments. No transcript or article is stored whole; `data/raw/` is ignored and `git ls-files` shows no file under it |
| 11 | Large files | sizes of `git ls-files` | none over 1 MB |
| 12 | Registrant names and addresses | by reading (COMPLIANCE review) | The stored FAA subsets under `data/snapshots/` keep each row byte for byte, so they carry the registrant name and street address the FAA publishes for each in-scope aircraft. The FAA releases this file to the public. It is still personal data for the few individual owners |

## Hits and what can be done

Each hit is S1 under the spec. History cannot be rewritten in this run, so each goes to `GO_PUBLIC.md` as a decision for the owner.

**Rewriting history is not a safe fix for either hit.** The lock's evidence is the commit `a44e5aca3756941a075150d9e381020826f3fb81`, which the tag `lock-2026Q3` and the release point at. Rewriting history changes that hash and breaks the record the project rests on.

- **F015, commit email (row 4).** The owner's email address is in the author field of his commits. Choices: accept it (many public repositories carry the author's address), or rewrite history and lose the lock. For future commits he can set `git config user.email` to his GitHub no-reply address.
- **F016, home path (row 5).** `~` shows the Mac's account name, which is the author's public name. Choices: accept it, or rewrite history and lose the lock.
- **Row 6.** After the merge, delete `origin/codex/fix-daily-merge-and-lock-integrity` on GitHub, or leave it. It exposes nothing.
- **Row 12.** The snapshots are part of the hashed record and the lock was computed from one of them. Accept, with a line in the README's Data section that the subsets are the FAA's public rows as released.
