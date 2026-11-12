"""P1.2 and P6.4: plant the nine defects in a copy of the tree, so the ledger can be shown to catch each one.

    <tools venv python> plant_selftest.py plant <planted copy>
    <tools venv python> plant_selftest.py compare <clean ledger csv> <planted ledger csv>

The copy is made with `git archive prepub-audit | tar -x -C <dir>` outside the repository. After `plant`, rebuild the
PDF in the copy (`make pdf`, plant 7), then run tools/prepub/ledger.py on the clean and the planted copy and `compare`.
"""
import csv
import json
import re
import sys
from pathlib import Path


def sub(p, a, b, count=1):
    s = p.read_text()
    assert a in s, (str(p), a[:60])
    p.write_text(s.replace(a, b, count))


def plant(root):
    root = Path(root)
    # 1. one figure changed in one surface only
    sub(root / "docs/LINKEDIN_POST.md", "32.0", "32.1")
    # 2. a rounding fault
    sub(root / "README.md", "69.2%", "69.3%")
    # 4. a true value under a wrong label: 5.5 is the ratio model's average miss
    sub(root / "README.md", "| Same quarter last year | 4.6 |", "| Same quarter last year | 5.5 |")
    # 5. a unit swap
    sub(root / "README.md", "GD deliveries per registry event averaged 1.18", "Registry events per delivery averaged 1.18")
    # 3 and 9. stale claims, one with a future-tense verb and one with neither a number nor such a verb
    sub(root / "README.md", "\n## Method", "\nThe 2026Q3 lock will be scored when GD reports.\n\nThe first lock is still ahead.\n\n## Method")
    # 6. a workbook cell whose formula result differs by 0.1
    import openpyxl
    wp = root / "output/gd_gulfstream_model.xlsx"
    wb = openpyxl.load_workbook(wp)
    c = wb["Summary"]["C2"]
    assert str(c.value).startswith("="), c.value
    c.value = str(c.value) + "+0.1"
    wb.save(wp)
    # 7. a figure in the note changed by 0.1 (the PDF is rebuilt from this file afterwards)
    np = root / "report/note.html"
    s = np.read_text()
    m = re.search(r"(<td[^>]*>Same quarter last year</td><td[^>]*>)4\.6(</td>)", s)
    assert m, "note Exhibit 2 cell not found"
    np.write_text(s[:m.start()] + m.group(1) + "4.7" + m.group(2) + s[m.end():])
    # 8. a figure in site/data.json that app.js renders on the first screen
    dp = root / "site/data.json"
    d = json.loads(dp.read_text())
    d["live"][0]["locked"]["nowcast"]["total"] += 0.1      # the locked 2026Q3 estimate, shown on the live card
    hit = ["live[0].locked.nowcast.total"]
    dp.write_text(json.dumps(d, indent=1))
    print("planted nine defects;", "data.json fields changed:", hit[:4])


def compare(clean, planted):
    def flagged(p):
        return {(r["surface"], r["file_line"], r["status"], r["value"], r["label"][:90], r["expected"][:24], r["note"][:60])
                for r in csv.DictReader(open(p)) if r["status"] != "traced"}
    c, pl = flagged(clean), flagged(planted)
    new = sorted(pl - c)
    tests = [
        ("1 post 32.0 -> 32.1", lambda r: r[0] == "post" and "32.1" in r[3]),
        ("2 README 69.2% -> 69.3%", lambda r: r[0] == "readme" and "69.3" in r[3]),
        ("3 'will be scored' sentence", lambda r: r[0] == "readme" and r[2] == "stale" and "will be scored" in r[4] + r[6]),
        ("4 right value, wrong label (4.6 -> 5.5)", lambda r: r[0] == "readme" and r[2] == "mismatch" and r[3] == "5.5" and "Same quarter last year" in r[4]),
        ("5 unit swap on 1.18", lambda r: r[0] == "readme" and "1.18" in r[3] and "Registry events per delivery" in r[4]),
        ("6 workbook Summary!C2 +0.1", lambda r: r[0] == "workbook" and "Summary!C2" in r[1]),
        ("7 note PDF 4.6 -> 4.7", lambda r: r[0] == "note-pdf" and r[3] == "4.7"),
        ("8 site/data.json locked total +0.1", lambda r: r[0] == "dashboard" and "32.1" in r[3]),
        ("9 'The first lock is still ahead'", lambda r: r[0] == "readme" and r[2] == "stale" and "first lock is still ahead" in r[4]),
    ]
    print(f"clean copy: {len(c)} flagged rows; planted copy: {len(pl)} flagged rows; new in planted: {len(new)}\n")
    print("| # | Plant | Caught | By (surface, place, status, shown, expected) |")
    print("|---|---|---|---|")
    missed = 0
    for name, f in tests:
        hits = [r for r in new if f(r)]
        missed += not hits
        r = hits[0] if hits else None
        by = f"`{r[0]}`, `{r[1][-34:]}`, `{r[2]}`, shown {r[3]}, expected {r[5] or '(none)'}; {len(hits)} row(s)" if r else "MISSED"
        print(f"| {name.split(' ', 1)[0]} | {name.split(' ', 1)[1]} | {'yes' if hits else 'NO'} | {by} |")
    print(f"\n{len(tests)} planted, {len(tests) - missed} caught, {missed} missed.")
    for s in ("post", "readme", "dashboard", "note", "note-pdf", "workbook"):
        print(f"clean copy, {s}: {sum(1 for r in c if r[0] == s)} flagged")
    return missed


if __name__ == "__main__":
    if sys.argv[1] == "plant":
        plant(sys.argv[2])
    else:
        sys.exit(1 if compare(sys.argv[2], sys.argv[3]) else 0)
