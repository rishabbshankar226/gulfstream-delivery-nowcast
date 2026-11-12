# Round 4 brief: exposure, privacy and the owner's runbook (`exposure`)

Read `round4_common.md` in this folder first. Its rules bind you.

**Who you are.** You are a security and privacy reviewer. A public repository shows its whole history, every branch, every tag and every tracked file. Your question: what does a stranger learn, and what can go wrong on the day the owner flips it public?

**Your trees (informed):**

- `~/gdn-prepub/round4_mirror.git`: a bare mirror of the owner's repository, holding every local branch, every tag, and the remote-tracking refs as of today's fetch. Its push URL is disabled. Use the read-only git commands in `round4_common.md` with `git -C ~/gdn-prepub/round4_mirror.git ...`.
- `<repo>` (the owner's checkout), read-only: tracked files only. This includes `docs/prepub/` and `docs/build/`, which you are told to read. The earlier rounds' reviews under `docs/prepub/reviews/` are in scope for you. Any file named `round4_*` is not. Run no git command in `<repo>` except `git ls-files`, `git log` and `git show`.

**Rule for anything sensitive you find:** cite the commit SHA, path and line, and the kind of thing ("personal email address", "home-folder path", "the SEC user-agent string"). Never its value. To search for the SEC user-agent string or the account name, read them inside your script (`~/.sec_ua`, and `os.path.basename(os.path.expanduser("~"))`) and print only counts and locations.

**Answer each by number:**

1. **History scan.** Search `git log -p --all` on the mirror, by script, for each of these:
   - Email addresses: count them by kind (personal, `noreply`, bot), and list the author and committer identities by kind.
   - Tokens and keys: patterns such as `ghp_`, `github_pat_`, `AKIA`, `sk-`, `-----BEGIN`, and `password=`.
   - The SEC user-agent string.
   - `/Users/` paths, and the account name.

   Give counts, commits and paths.
2. **Refs.** List every branch, tag and remote-tracking ref that will be public on GitHub (the `origin/*` refs and tags). Which hold commits that `main` and `prepub-audit` lack, and what is in them?
3. **Tracked files.** From `git ls-files`: dotfiles, agent or editor configs, logs, caches, large binaries, anything personal. Should each one be public?
4. **`docs/prepub/` and `docs/build/` as public text.** Look for:
   - personal details, or the owner's private name for themself;
   - internal tool paths;
   - statements that would read badly next to the post (a NO-GO verdict, harsh self-assessment);
   - claims that contradict the final public surfaces.

   For each folder: publish as is, trim, or move out? Give the defensible options, without moving the record.
5. **`docs/prepub/GO_PUBLIC.md` as a runbook.** Walk every step in order, as if you were the owner. Check:
   - Is each command correct, safe and in the right order?
   - Does each check prove what it says?
   - Is any step missing? For example: deleting stale branches, local throwaway branches, Pages settings, branch protection, the repository description and topics, rotating anything.
   - Could any step damage the record (`predictions/`, `results/live/2026Q3_*`, `docs/PREREGISTRATION.md`, the `lock-2026Q3` release)?
6. **GitHub Actions on a public repository.** Read `.github/workflows/*.yml`:
   - `permissions:`;
   - token scope;
   - secrets and what is echoed to logs;
   - fork pull-request triggers;
   - unpinned third-party actions.
7. **Licensing and data.**
   - FAA registrants' names and addresses in `data/snapshots/`.
   - Any transcript or article text stored beyond short quotes: grep `data/` and `docs/`.
   - Does `LICENSE` cover what the README says it covers?
8. Anything else a stranger who clones the public repository learns about the owner that the owner may not want known.
