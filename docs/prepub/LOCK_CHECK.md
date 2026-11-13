# Lock check, end to end (P2.3)

Run 2026-11-11, about 19:40 ET, on `prepub-audit`. Every line below was printed by the command named.

| # | Check | Command | Printed | Result |
|---|---|---|---|---|
| 1 | sha256 of the locked file in the tree | `shasum -a 256 predictions/2026Q3.json` | `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23` | |
| 2 | sha256 of the file at the tag | `git show lock-2026Q3:predictions/2026Q3.json \| shasum -a 256` | `3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23` | equals 1: pass |
| 3 | hash in the release notes | `gh release view lock-2026Q3 --json body` | `"body":"sha256 3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23"` | equals 1: pass |
| 4 | hash in `results/live/2026Q3_lock.json` | `cat results/live/2026Q3_lock.json` | `"sha256": "3c4cdbd01b8a5c6928b83b4d8cbcf32964c680a46af1a4bd8b5207296b406f23"` | equals 1: pass |
| 5 | tag commit | `git rev-parse 'lock-2026Q3^{commit}'` | `a44e5aca3756941a075150d9e381020826f3fb81` | equals the release's `targetCommitish` and `lock.json` `commit`: pass |
| 6 | the locked file's commit is an ancestor of `origin/main` | `git merge-base --is-ancestor a44e5aca... origin/main` | `yes` | pass |
| 7 | the file was committed once | `git log --format='%h %ad %s' --date=iso-strict -- predictions/2026Q3.json` | one line: `a44e5ac 2026-10-29T05:51:22+00:00 Lock the 2026Q3 nowcast` | never changed: pass |
| 8 | who made the lock | `git log --diff-filter=A --format='%an' -- predictions/2026Q3.json` and `gh release view lock-2026Q3 --json author` | `github-actions[bot]` for both the commit and the release | the GitHub workflow made the lock, not the owner's Mac |
| 9 | release publication time | `gh release view lock-2026Q3 --json publishedAt,createdAt` | `"publishedAt":"2026-10-29T05:51:24Z"`, `"createdAt":"2026-10-29T05:51:22Z"` | 2026-10-29 01:51:24 ET (EDT, UTC-4) |
| 10 | GD's 2026Q3 release time | `python3 sec_get.py https://www.sec.gov/Archives/edgar/data/40533/000004053326000036/0000040533-26-000036-index.htm` (urllib, declared user agent) | `Filing Date 2026-10-30 Accepted 2026-10-30 08:09:27 ... Item 2.02: Results of Operations and Financial Condition` | EDGAR shows acceptance in US Eastern time: 2026-10-30 08:09:27 ET, which is 12:09:27 UTC |
| 11 | lock before the release | 9 against 10 | 2026-10-29T05:51:24Z against 2026-10-30T12:09:27Z | the release was published 30 hours 18 minutes before SEC accepted GD's 8-K: pass |
| 12 | lock before 00:00 ET on the release date (the preregistered rule) | 9 | 01:51 ET on 2026-10-29, the eve | pass, with 22 hours 8 minutes to spare |
| 13 | GD's count in the filing | Exhibit 99.1, `gd-20261004exhibit991.htm`, table "Gulfstream Aircraft Deliveries (units)", three months ended October 4, 2026 | `Large-cabin aircraft \| 35`, `Mid-cabin aircraft \| 5`, `Total \| 40` | equals `results/live/2026Q3_score.json` `reported` (35, 5, 40): pass |
| 14 | the score's arithmetic | `predictions/2026Q3.json` total 31.953208556149733, band 21.233380969942836 to 37.24108734402852; GD 40 | miss 8.046791443850267; 20.11697860962567% of 40; 40 is above 37.24 | equals `score.json` `ae_total`, `ape_pct`, `inside_band: false`: pass |

Displayed times, converted: the README and the note say "01:51 ET on 2026-10-29". 05:51:24 UTC on 2026-10-29 is 01:51:24 EDT. Daylight saving ended on 2026-11-01, so UTC-4 applies. Pass.

## What an outsider can and cannot check

Can check, once the repository is public:
- The release `lock-2026Q3` exists, its `published_at` is 2026-10-29T05:51:24Z, and its author is `github-actions[bot]`. GitHub sets `published_at` when a release is published. An owner cannot type a past date into it.
- The release notes carry a sha256, and the file `predictions/2026Q3.json` at the tag's commit hashes to it.
- SEC accepted GD's 8-K at 08:09:27 ET on 2026-10-30, a day later.
- The Actions tab lists the workflow run that made the release, with GitHub's own start time, for as long as GitHub keeps that run.

Cannot check:
- That the release notes were not edited after GD reported. GitHub shows no edit history for release notes, and a tag can be moved to another commit. The repository was private until after the release, so nobody outside saw the hash before GD's count was public.
- The push history. It needs `gh api`, which this audit may not call.
- Commit dates. Git records whatever date the committing machine reports.

So the honest claim is: "The estimate was locked by a GitHub workflow as a timestamped release in a repository that was private at the time. The timestamp is GitHub's. Nobody outside could see it before GD reported." It is not a public, third-party-verifiable lock. From the next quarter on, with the repository public, the lock is visible before GD reports.

## Not verified here

Nothing in this list failed. `gh release view` worked on the first call.
