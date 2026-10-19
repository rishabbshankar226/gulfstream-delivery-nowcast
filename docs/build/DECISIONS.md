# Decisions

Preflight passed, 2026-10-19 11:33 EDT (15:33 UTC). It runs once; never rerun it.

## Preflight

```
## sec_ua
non-empty: ok
## gdn_disclosure
non-empty: ok
## gh auth status
github.com
  ✓ Logged in to github.com account rishabbshankar226 (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
## origin
https://github.com/rishabbshankar226/gulfstream-delivery-nowcast.git
## status
## main...origin/main
## rev-list count
1
## ls-files
.gitattributes
## github private, default branch
true
main
## exclude lines
absent (hook blocked writing .git/info/exclude; see below)
## gate
-rw-r--r--  1 owner  staff  154801 Oct 19 09:49 .../prompt library/gulfstream-delivery-nowcast/gate/jetgate.py
## date ET
Mon Oct 19 11:33:32 EDT 2026
## actions enabled
true
```

- `~/.gdn_disclosure` was missing at the start. The owner answered "No position in GD" in chat, so I wrote Part A's example sentence: "The author holds no position in General Dynamics."
- Part A step 7's second block had not run. With the owner's approval I wrote `.claude/settings.local.json` with Part A's exact allowlist. A PreToolUse hook from the `claude-seo-ai` plugin blocked the shell write to `.git/info/exclude` ("VCS internals"). I did not route around the hook. Instead, `.gitignore` lists `/CLAUDE.md` and `.claude/`, which keeps both off GitHub and keeps P2's tree clean. The owner's global `~/.config/git/ignore` already ignores `**/.claude/settings.local.json`.
- The session runs in the Claude desktop app (Code tab), not under `caffeinate -is claude`. The app's keep-awake hold is on (`session_idle`). The reference folders were readable without `--add-dir`.
- GitHub Actions is enabled on the repository (`true`), so Phase 5 runs and watches the workflow.

## Permission smoke test (Phase 0, first action)

All passed with exit 0, and no prompt came up:
- `ls ~/Downloads | head -3`: listed three entries.
- `curl` of the FAA download page with the full Chrome header set: HTTP 200, 113,511 bytes.
- `curl` of `https://data.sec.gov/submissions/CIK0000040533.json` with the `~/.sec_ua` User-Agent: HTTP 200, 155,154 bytes.
- `gh api user`: `rishabbshankar226`.
- `open -g -a "Google Chrome" about:blank`: exit 0.
- A write and delete under `/tmp` and `~/.cache/gdn-smoke`: ok.
- `git init`, commit, push to a bare repository and `git reset --hard` in `/tmp/gdn-smoke`: ok.
- `git ls-remote origin` showed `dba3e3a` on `refs/heads/main`. `git push --dry-run origin main` printed "Everything up-to-date".
- Headless Chrome: `Google Chrome 155.0.8059.82`.

## Environments

- Project: `.venv` on CPython 3.11.16 (uv 0.12.5) with openpyxl 3.1.5, matplotlib 3.9.2, pytest 8.3.3, playwright 1.64.0 and Playwright's Chromium. Frozen in `requirements.lock`, 20 lines.
- Gate: `~/.cache/jetgate/venv`, CPython 3.11, openpyxl 3.1.5 and formulas 1.3.4. `--selftest`: "mutants: 64 of 64 killed", "selftest PASS in 38s".

## Backtest snapshot

- §3.3's first route worked: `curl` with the full Chrome headers, 15:34 UTC, 72,927,535 bytes, first bytes `PK`. Saved as `data/raw/faa/ReleasableAircraft-2026-10-19.zip` (America/Chicago date 2026-10-19). That date is the backtest snapshot.

## Tool routing

- Present: `dataviz`, Impeccable (`impeccable:impeccable`), `vectorlab-ux-skills:viewports`, `anthropic-skills:citation-integrity-skill`, `anthropic-skills:anti-hallucination`, `superpowers:systematic-debugging`, `anthropic-skills:root-cause-debugging`.
- Absent: a skill named `pdf-reading`. Fallback: the Read tool reads PDF pages directly, with `sips` or `qlmanage` to PNG for page images.
- Left alone, though installed: `design-taste-frontend` and `redesign-existing-projects`. The rest of the prompt's leave-alone list (`gpt-taste`, `high-end-visual-design`, `stitch-design-taste`, `minimalist-ui`, `industrial-brutalist-ui`, `brandkit`, `image-to-code`, `imagegen-frontend-web`, `imagegen-frontend-mobile`, `full-output-enforcement`, `find-skills`) is not installed in this session. They direct marketing pages or generate images, and this is a data product that matches the backlog dashboard.
- Subagent types available: `general-purpose`, `Explore`, `Plan`, `claude`. Checkers and reviewers run as `general-purpose` from briefs in `docs/build/briefs/`.

## Limitations (collected for the README)
