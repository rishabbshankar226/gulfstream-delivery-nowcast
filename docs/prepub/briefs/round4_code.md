# Round 4 brief: code, CI, the live path and reproduction (`code`)

Read `round4_common.md` in this folder first. Its rules bind you, except where this brief names a command it allows.

**Who you are.** You are a senior engineer, and you are hiring. You clone the repository the way a public reader will, build it, and then read the parts that keep the live record honest once nobody is watching.

**Your tree (informed):** `~/gdn-prepub/round4_clone_code`, a clone of branch `prepub-audit` made for you. Its push URL is disabled. Do not open `docs/prepub/` in it. You may use the read-only git commands in `round4_common.md` there.

**Allowed in that clone only, beyond `round4_common.md`:**

- `python3.11 -m venv .venv`
- `.venv/bin/python -m pip install -r requirements.lock`
- `make all`, `make test`, `make check-determinism`
- `git status --short`

Run anything over 2 minutes in the background, with its log in your scratch folder. Never run `make daily`, `make daily-core`, `make lock`, `make score`, `make snapshot` or `make nowcast`. Never run any `python -m gdn` command. Never call any function that touches the network, git or GitHub (`daily.run`, the lock, score and publish functions in `live.py`, anything in `gitops.py`, SEC or FAA fetchers). You may import modules read-only in scripts to read constants and pure functions.

**Answer each by number, with `file:line` evidence:**

1. **Reproduce as a public reader.** Follow the README's `## Reproduce` section literally, in the clone, with no `data/raw/`. Then run `make all`, `git status --short` (it must print nothing), `make test` and `make check-determinism`. For each command, give it and the tail of its output. Does the README tell a stranger everything needed, the Python version included?
2. **The first run after going public.** What does `"public": true` in `config/calendar.json` change? Grep every reader of it. When the daily workflow commits with the default token, does Pages redeploy (`.github/workflows/pages.yml`)? What does the dashboard show on the morning after the owner flips the flag?
3. **The next lock.** GD reports 2026Q4 in late January. `config/calendar.json` has no 2026Q4 release date. Trace what the daily job does: does it lock, skip quietly, or warn? What would a public reader see if no lock fires? What else in `config/calendar.json` is missing for 2027?
4. **Lock and score integrity.** Read `src/gdn/live.py`, `daily.py` and `gitops.py`. Could the job do any of these?
   - Write a lock after the release time.
   - Publish a lock whose hash differs from its release.
   - Write a second lock in one quarter.
   - Score from the wrong exhibit or the wrong quarter.
   - Print a lock on the missed-lock path.
   - Get a date wrong at the DST end (2026-11-01) or at the late-January release.

   Give presence or absence of each, with `file:line`.
5. **Tests that will turn CI red in public.** Which tests pin today's text or today's values in files the daily job rewrites (`README.md`, `site/data.json`, `results/live/2026Q4_*`, `docs/LINKEDIN_POST.md`)? Will the next daily commits break `test.yml` on a public repository? Name each test and the change that would break it.
6. **Workflows on a public repository.**
   - The `permissions:` blocks and the token's scope.
   - Are the actions pinned by tag or by SHA?
   - `pull_request` against `pull_request_target`.
   - Secrets in logs.
   - What a fork's pull request can trigger.
   - Concurrency between two runs.
   - The cron drift.
7. **The unreviewed delta.** No outside reviewer has read `git diff 4ca7d35..HEAD -- src tests`. Read every hunk. Look for bugs, untested paths that feed a public number, and charts or text drawn from the wrong field.
8. **Code quality a hiring engineer would notice.**
   - Structure, dead code and duplicated logic.
   - Comments that carry internal finding numbers (`F0xx`).
   - Broad `except` blocks.
   - Whether the developer docs are enough to contribute.
