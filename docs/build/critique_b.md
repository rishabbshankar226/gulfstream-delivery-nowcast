# Critique, Assessment B: detector and browser evidence

Target: `site/index.html`, served at http://127.0.0.1:8766/ (that server was already running as pid 98723; this assessment did not start or stop it).
Detector: impeccable 4.5.2 skill, engine 0.1.14. Run on 2026-10-19, 11:30 to 11:39 local time.
I worked from this brief alone. I did not read Assessment A.

## 1. CLI scan (brief step 1)

```
"<skill>/scripts/impeccable" detect --json site/index.html
```

- Exit code **0** (clean). stdout was `[]`, so there were **0 findings and 0 advisories**.
- The scan with `--no-config` gave the same result: exit 0, `[]`. No project config, no `DESIGN.md` and no inline `impeccable-disable` comments exist, so nothing was hidden by an ignore. The `.impeccable/` folder holds only `hook.cache.json`, and that cache also records `[]` for `index.html`, `style.css` and `app.js`.
- Limitation: the static scan reads the HTML and its linked CSS. It does not run `app.js`. Most of the page's text, including `#live-note`, the `#tests` list and the table bodies, is written into the page by `app.js` from `data.json`. The static scan therefore never saw the text that the rendered scans below flag. A clean static result does not mean the rendered page is clean.

JSON summary:

```json
{"target": "site/index.html", "exit": 0, "findings": 0, "advisories": 0, "rules": [], "locations": []}
```

## 2. Rendered URL scans (extra, not in the brief)

These ran the same detector against the live URL in its own headless Chromium. They are reported apart from step 1.

| Viewport | Command | Exit | Findings |
|---|---|---|---|
| 1280x800 | `detect --json http://127.0.0.1:8766/` | **2** | 5, all `line-length` (warning, category quality) |
| 390x844 | `detect --json --viewport 390x844 http://127.0.0.1:8766/` | **0** | 0 |

The five findings at 1280. The `file` field is the URL and `line` is 0 for every one.

| # | Rule | Selector | Section | Detector snippet |
|---|---|---|---|---|
| 1 | line-length | `#live-note` (`p.note`) | h-live | ~95 chars on 2 of 3 rendered lines |
| 2 | line-length | `#tests > li:nth-of-type(1)` | h-tested ("Against GD's own guidance pace...") | ~106 chars on 3 of 4 lines |
| 3 | line-length | `#tests > li:nth-of-type(2)` | h-tested ("Against the same quarter last year...") | ~109 chars on 2 of 3 lines |
| 4 | line-length | `#tests > li:nth-of-type(3)` | h-tested ("Against last quarter...") | ~109 chars on 3 of 4 lines |
| 5 | line-length | `section.panel:nth-of-type(6) > p.sub` | h-gd ("What it means for GD"; resolved in the browser) | ~96 chars on 2 of 3 lines |

The 390 result is clean because of the narrow width. A 358 px column at 14 px cannot fit long lines, so it says nothing about the 1280 problem.

## 3. Browser evidence (brief steps 2 and 3)

### Method

- I used the project's Playwright (`.venv/bin/python`, playwright 1.64.0, headless Chromium). The page was loaded in four fresh contexts: 1280x900 light, 1280x900 dark, 390x844 light and 390x844 dark. Each context opened a new page with no shared state. Console, `pageerror` and `requestfailed` listeners were attached before `goto(..., wait_until="networkidle")`. After that the script waited for `document.fonts.ready`.
- Dark mode was emulated with `color_scheme="dark"`. That covers the site completely, because `style.css` switches themes only through `@media (prefers-color-scheme: dark)` at line 65. It has no `data-theme` hook. `matchMedia('(prefers-color-scheme: dark)')` returned true in both dark contexts and false in both light contexts.
- In all four contexts the page returned HTTP 200, and the `IBM Plex Sans Var` font (weights 100 to 700) loaded.

### Live-server and detect.js injection

- Mutation preflight passed in all four contexts. Appending `[Human]` to `document.title` worked, and an inline `<script>` ran and logged its marker.
- I started the live server with `"<skill>/scripts/impeccable" live-server --background` from the repository root. It returned `{"pid":1749,"port":8400,...}`, and `/health` reported ok. `/detect.js` returned 200 with 2,787,395 bytes. It was injected into each page with `page.add_script_tag(url="http://localhost:8400/detect.js")`, then the script waited 3 s and read the console.
- Console output prefixed `[impeccable]`:
  - 1280 light and 1280 dark: `[impeccable] 5 anti-patterns found`. The group held five `line-length` entries, the same five elements as section 2: `#live-note`, the three `#tests` items and the h-gd `p.sub`, with the same character counts. I resolved each entry to its element through its console argument handle.
  - 390 light and 390 dark: `[impeccable] No anti-patterns found.`
  - There were no `[impeccable] scan failed` or `visual contrast scan failed` warnings, and no page errors after injection.
- The live server was stopped with `"<skill>/scripts/impeccable" live-server stop --keep-inject`, which printed `Stopped live server on port 8400.` Afterwards nothing listened on port 8400, pid 1749 was gone and `/health` did not answer. I used `--keep-inject` on purpose: plain `stop` also runs `live-inject --remove` against the HTML entry, and nothing had been injected into any file. The overlay existed only inside the headless pages.
- **No overlay is visible to the user.** The pages were headless Playwright contexts, so there is no `[Human]` tab in the user's browser.

### Console errors, at both widths

| Context | Console messages before injection | Page errors | Failed requests |
|---|---|---|---|
| 1280 light | none | none | none |
| 1280 dark | none | none | none |
| 390 light | none | none | none |
| 390 dark | none | none | none |

### Sideways scroll

| Context | `documentElement` scrollWidth / clientWidth | `body` scrollWidth / clientWidth | scrollX after `scrollTo(10000, y)` | Unclipped elements past the viewport |
|---|---|---|---|---|
| 1280 light / dark | 1280 / 1280 | 1280 / 1280 | 0 | none |
| 390 light / dark | 390 / 390 | 390 / 390 | 0 | none |

The document does not scroll sideways at either width. At 390, two table wrappers scroll inside themselves: "Table of the estimate by snapshot date" (scrollWidth 422 against clientWidth 358) and "Table of deliveries and estimates by quarter" (457 against 358). Both are `.scroll` regions with `tabindex="0"` and an `aria-label`, so keyboard users can reach and scroll them. This is contained scrolling, not page overflow. The other four table wrappers fit, and at 1280 none of the six overflows.

### Contrast, computed from rendered elements

For each element I resolved the background by walking up its ancestors to the first opaque `background-color`. Ratios follow the WCAG 2.x formula. The results were the same at 1280 and 390, so the table is per theme.

| Text | Light: fg on bg | Light ratio | Dark: fg on bg | Dark ratio | Size / weight |
|---|---|---|---|---|---|
| Body text (`body`, panel `p`, `#tests li`) on `--bg` | #1c1a17 on #f5f4f1 | **15.79:1** | #ebe7df on #161412 | **14.90:1** | 14px / 400 |
| `.facts dd` on `--bg` | #1c1a17 on #f5f4f1 | 15.79:1 | #ebe7df on #161412 | 14.90:1 | 14px / 500 |
| `.lead` (`--ink-3`) on hero `--surface` | #423e38 on #fbfaf8 | 10.18:1 | #c6c0b5 on #1d1b18 | 9.50:1 | 18px / 400 |
| Muted `.sub`, `.facts dt` on `--bg` | #5f5a52 on #f5f4f1 | **6.22:1** | #a39c90 on #161412 | **6.75:1** | 14px / 400 |
| Muted `.note`, `.foot` on `--bg` | #5f5a52 on #f5f4f1 | 6.22:1 | #a39c90 on #161412 | 6.75:1 | 13px / 400 |
| Muted `.tiles .t-cmp` on `--bg` | #5f5a52 on #f5f4f1 | 6.22:1 | #a39c90 on #161412 | 6.75:1 | 12px / 400 |
| Muted `.eyebrow` on hero `--surface` | #5f5a52 on #fbfaf8 | 6.56:1 | #a39c90 on #1d1b18 | 6.31:1 | 13px / 500 |

All of this text is small, at 12 to 14 px, so the AA threshold is 4.5:1. Every pair passes AA. Body text and the lead also pass AAA (7:1). Muted text sits at 6.2 to 6.8:1, which passes AA and falls short of AAA. That is a reasonable result for secondary text. `--sunken` is not used as a text background anywhere in `style.css`. For reference only, muted on `--sunken` would be 5.85:1 light and 6.44:1 dark.

## 4. Classification of findings, including false positives

- **The 5 `line-length` findings are real but mild. The detector's suggested fix is the false part.** Each flagged element already has the cap the detector recommends. `.note` and `.sub` use `max-width: 72ch`, and `ul.plain` uses `80ch` (its items are 78.2ch wide). The detector advises "a max-width (65ch to 75ch)". But `ch` is the width of the glyph "0": 8.39 px at 14 px and 7.80 px at 13 px in Plex Sans. The average Plex glyph is narrower than that, so a 72 to 78ch box holds about 89 to 104 characters per line. I measured 89 for `#live-note`, 90 for the h-gd `.sub` and 101 to 104 for the `#tests` items. The detector counts characters, so it is right that lines run past 80. Following its advice to use 65 to 75ch would not get them under 80. To reach about 75 characters, the cap would need to be near 34 to 36em, or about 60ch, for this font. None of these is a defect the reader would notice at once. They are long-measure secondary paragraphs in a dense report.
- **Static scan clean, rendered scan at 1280 not clean: these do not conflict.** As section 1 explains, the flagged text is written by `app.js`.
- **I found no false positives in rule identity.** All five flagged elements exist, render where the detector says and break the measure the detector says.
- **Nothing found at 390.** This is not evidence of quality at that width. Lines cannot run long there.

## 5. Skipped or substituted steps

- **Native browser tab and `[Human]` presentation: replaced with headless Playwright.** The brief asked for the project's Playwright or a headless browser, and four isolated contexts with color-scheme emulation give cleaner evidence. Nothing ran in a browser the user can see, so the parent report must not claim a user-visible overlay.
- **Multi-view injection (3 to 5 pages): not applicable.** The target is one page. Instead, the script was injected at each of the two widths and both themes.
- **`critique-storage` slug and persistence: not run.** That belongs to the parent synthesis, and the brief permits this file as my only output.
- Nothing else was skipped. The CLI scan, injection, console capture, overflow check and contrast check all ran at both widths.

## 6. Side effects and repository integrity

- The live server wrote `.impeccable/live/server.json` while it ran, and `stop` removed it. `.impeccable/` is gitignored, and afterwards it holds only `hook.cache.json`, as it did before.
- I took SHA-1 hashes of every file under `site/` before starting the live server and again after stopping it. `index.html`, `style.css`, `app.js`, `data.json`, `favicon.svg`, `fonts/` and `vendor/` were byte-identical.
- **`site/GD_research_note.pdf` changed during the run, and this assessment did not change it.** Its new mtime is 11:38:42. `output/GD_research_note.pdf` and `output/GD_research_note.inputs.sha256` have the same mtime, so the change came from a note build running at the same time. That build also wrote `report/note.html` and `report/claims.json` at 11:38:31. Commit `64c7eec` ("Critical path ready", 11:35) and new untracked files (`README.md`, `docs/LINKEDIN_POST.md`, `src/gdn/report.py`, `docs/build/claims_product.json`) also appeared during the run. All of these came from other work on the repository, not from this assessment.
- The user's server on port 8766 (pid 98723) was left running.
- Scratch files (the probe scripts and raw JSON) are in the session scratchpad, outside the repository.
