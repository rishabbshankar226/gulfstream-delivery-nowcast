"""Writes tests/fixtures/faa/*.txt: fixed-width FAA text, a comma after each field, BOM, CRLF."""
import sys
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

def table(names, rows, blank_lines=()):
    w = [max([len(n)] + [len(r[i]) for r in rows]) for i, n in enumerate(names)]
    def line(vals):
        return "".join(v.ljust(w[i]) + "," for i, v in enumerate(vals))
    lines = [line(names)] + [line(r) for r in rows]
    for i in blank_lines:
        lines.insert(i, "".join(" " * x + "," for x in w))
    return ("﻿" + "\r\n".join(lines) + "\r\n\r\n").encode("utf-8")

acft = [
    ["3980221", "GULFSTREAM AEROSPACE CORP", "GVIII-G700", "6", "5"],
    ["4500314", "IAI LTD", "GULFSTREAM G280", "6", "5"],
    ["4500308", "ISRAEL AIRCRAFT INDUSTRIES", "GULFSTREAM 200", "6", "5"],
    ["3980209", "GULFSTREAM AEROSPACE LP", "G150", "6", "5"],
    ["3980700", "GULFSTREAM AEROSPACE", "695A", "6", "2"],
    ["3980999", "GULFSTREAM AMERICAN CORP", "GA-7 COUGAR", "4", "1"],
    ["1234567", "CESSNA", "560XL", "6", "5"],
]
(out / "ACFTREF.txt").write_bytes(table(["CODE", "MFR", "MODEL", "TYPE-ACFT", "TYPE-ENG"], acft))

master = [
    ["N700AA", "75001", "3980221", "2024", "SKY JETS, INC", "20240515", "20240301"],
    ["N280ZZ", "2101", "4500314", "2016", "GULFSTREAM AEROSPACE CORP", "20230301", "20170110"],
    ["N703GD", "75003", "3980221", "2024", "GULFSTREAM AEROSPACE CORP", "20250105", "20241201"],
    ["N280RN", "2050", "4500314", "2016", "RENEWAL HOLDINGS LLC", "20240301", "20160301"],
    ["N704GA", "75004", "3980221", "2026", "GULFSTREAM AEROSPACE CORP", "", ""],
    ["N69PT", "695001", "3980700", "1981", "PROP OWNER", "19900101", "19810101"],
    ["N560X", "75001", "1234567", "2005", "CESSNA OWNER", "20050101", "20050101"],
    ["N999ZZ", "", "3980221", "2024", "NO SERIAL LLC", "20240101", "20240101"],
]
(out / "MASTER.txt").write_bytes(table(
    ["N-NUMBER", "SERIAL NUMBER", "MFR MDL CODE", "YEAR MFR", "NAME", "CERT ISSUE DATE", "AIR WORTH DATE"],
    master, blank_lines=(4,)))

dereg = [
    ["N751GA", "75001", "3980221", "GULFSTREAM AEROSPACE CORP", "2024", "20240301", "20240331", "", "20240305"],
    ["N752GA", "75002", "3980221", "GULFSTREAM AEROSPACE CORP", "2024", "20240501", "2024-06-30", "QA", "20240505"],
    ["N280AC", "2101", "4500314", "ACME AIR LLC", "2016", "20170110", "20230301", "", "20170201"],
    ["N753GA", "75003", "3980221", "GULFSTREAM AEROSPACE CORP", "2024", "20241201", "20250105", "", "20241205"],
    ["N280GA", "2101", "4500314", "GULFSTREAM AEROSPACE LP", "2016", "20170110", "20170125", "", "20161220"],
    ["N752GD", "75002", "3980221", "GULFSTREAM AEROSPACE CORP", "2024", "20240501", "20240610", "", "20240502"],
]
(out / "DEREG.txt").write_bytes(table(
    ["N-NUMBER", "SERIAL-NUMBER", "MFR-MDL-CODE", "NAME", "YEAR-MFR", "AIR-WORTH-DATE", "CANCEL-DATE",
     "EXP-COUNTRY", "CERT-ISSUE-DATE"], dereg))
print("wrote", sorted(p.name for p in out.iterdir()))
