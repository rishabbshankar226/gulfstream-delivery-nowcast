# Lock rehearsal

Run by `tools/rehearsal.py` on 2026-10-19 from commit 1d7df03. Origin is a bare copy at `/tmp/gdn-rehearsal/github.com/rishabbshankar226/gulfstream-delivery-nowcast.git` and `gh` is a shim first on PATH that answers from `/tmp/gdn-rehearsal/gh_state.json`. Times are ET; the release date is 2026-10-30. Nothing here reached GitHub.

| Case | Command | Exit | Expected | Observed | Result |
|---|---|---|---|---|---|
| Eve 18:00 ET, older snapshot | `gdn lock --now 2026-10-29 18:00 ET` | 0 | no lock | no release, no prediction | pass |
| Eve 19:00 ET, older snapshot | `gdn lock --now 2026-10-29 19:00 ET` | 0 | lock from 2026-10-28 | release published 2026-10-29T23:00:00Z, snapshot 2026-10-28, sha256 in notes | pass |
| Second lock | `gdn lock --now 2026-10-29 21:00 ET` | 0 | refused, one lock per quarter | still one release | pass |
| Release without _lock.json | `gdn lock --now 2026-10-30 07:00 ET` | 0 | writes _lock.json from the release | lock record restored, no new release | pass |
| Score on a fixture 8-K | `gdn score --offline --now 2026-10-30 12:00 ET` | 0 | score with the lock | locked True, reported {'large': 33, 'mid': 7, 'total': 40}, AE 8.868220015278837 | pass |
| Gate `live` on the work clone | `jetgate.py --only live, shim on PATH` | 0 | no failing code | 5 assertions, 0 failing, 1 warning / WARN L4 [('2026Q3', 'release not parsed; score checked for arithmetic only')] | each released quarter is scored against GD's reported count | pass |
| Eve 08:00 ET, same-day snapshot | `gdn lock --now 2026-10-29 08:00 ET` | 0 | lock from 2026-10-29 | snapshot 2026-10-29 | pass |
| Eve 23:59 ET | `gdn lock --now 2026-10-29 23:59 ET` | 0 | lock | release at 03:59 UTC | pass |
| Release date 00:00 ET | `gdn lock --now 2026-10-30 00:00 ET` | 0 | no lock | 2026Q3 missed its lock window (release 2026-10-30); no late lock | pass |
| Rejected push | `gdn lock --now 2026-10-29 19:30 ET, second clone pushes first` | 0 | reset to upstream, lock on retry | attempt 1 rejected and reset; competing commit kept; lock target on main | pass |
| make daily-core on the eve | `gdn daily --core --offline --now 2026-10-29 19:05 ET` | 0 | daily outputs pushed, then the lock | release and lock record on main | pass |
