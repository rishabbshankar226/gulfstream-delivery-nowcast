"""Write docs/PREREGISTRATION.md: §3.3 to §3.6 cut from the prompt file, never retyped.

Usage: python tools/preregister.py <prompt file> <date>
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gdn import model  # noqa: E402
from gdn.files import read_csv, write_text  # noqa: E402


def cut(prompt_text):
    lines = prompt_text.splitlines(keepends=True)
    start = next(i for i, ln in enumerate(lines) if ln.startswith("### 3.3 "))
    end = next(i for i, ln in enumerate(lines) if ln.startswith("### 3.7 "))
    return "".join(lines[start:end]).rstrip("\n") + "\n"


def main(prompt, date):
    spec = cut(Path(prompt).read_text())
    rows = [dict(r, ae=float(r["ae"])) for r in read_csv(ROOT / "results/design.csv")]
    chosen, m1, m2 = model.choose(rows)
    text = f"""# Preregistration

Committed on {date}, before any holdout figure, live estimate or prediction exists. The text from "### 3.3" to the end of §3.6 is cut by `tools/preregister.py` from the build prompt, word for word. No definition, window or rule below changes after a result is seen; a variant goes to `results/exploratory/` and is labelled as tried after the fact.

{spec}
## Chosen definition

The design window, 2017Q1 to 2019Q4 (12 quarters), selects **{chosen}**. The ratio model's design MAE is {m1!r} aircraft under E1 and {m2!r} under E2; the lower wins, E1 on a tie. The holdout scores ratio and raw under {chosen} only.

## Secondary analyses

- **As-of study.** Wayback Machine captures of `ReleasableAircraft.zip` taken 20 to 30 days after past fiscal ends, found through the CDX API at `https://web.archive.org/cdx/search/cdx?url=registry.faa.gov/database/ReleasableAircraft.zip&output=json`, are scored with ratio as each capture would have read it. `results/exploratory/asof.csv` is written whether or not captures exist, with a line saying which. It is secondary: it never changes the headline.
- The truncation table and the coverage-drift flag are part of §3.4 above.
"""
    write_text(ROOT / "docs/PREREGISTRATION.md", text)
    print(f"wrote docs/PREREGISTRATION.md: {len(spec.splitlines())} spec lines, chosen {chosen}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
