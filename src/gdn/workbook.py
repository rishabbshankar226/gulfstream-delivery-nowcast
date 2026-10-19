"""output/gd_gulfstream_model.xlsx (§3.8): typed inputs in blue, every other figure a live formula."""
import re
import zipfile
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from . import model, stats
from .estimates import SEGMENTS, basis_path
from .fiscal import qidx, qrange
from .files import read_csv, read_json, sha256, write_text

BLUE = Font(color="FF0000FF")
BLACK = Font(color="FF000000")
BOLD = Font(bold=True)
F_USD, F_AIR, F_PCT, F_RATIO = "#,##0", "0.0", "0.0%", "0.00"
QUARTERS = qrange("2016Q1", "2026Q2")
SEG_Q = qrange("2024Q3", "2026Q2")
OUT = Path("output/gd_gulfstream_model.xlsx")
INPUTS = Path("output/gd_gulfstream_model.inputs.sha256")
HEAD = ["Quarter", "Fiscal end", "Reported large", "Reported mid", "Reported total", "Registry large", "Registry mid",
        "Ratio large", "Ratio mid", "Ratio total", "Raw total", "Seasonal", "Last", "AE ratio", "AE raw",
        "AE seasonal", "AE last", "Window"]


def put(ws, ref, value, fmt=None, typed=False):
    c = ws[ref]
    c.value = value
    c.font = BLUE if typed else BLACK
    if fmt:
        c.number_format = fmt
    return c


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w


def header(ws, names):
    for i, n in enumerate(names):
        c = ws.cell(row=1, column=i + 1, value=n)
        c.font = BOLD
        c.alignment = Alignment(wrap_text=True)


def about(wb, snap, chosen):
    ws = wb.active
    ws.title = "About"
    lines = [
        ("General Dynamics (GD): Gulfstream delivery tracker, model workbook", BOLD),
        ("Question: how closely do FAA registrations track the Gulfstream deliveries GD reports, and can they "
         "estimate the count before GD reports it?", None),
        ("", None),
        ("Method", BOLD),
        (f"1. Each Gulfstream airframe in the FAA registry snapshot of {snap} gets a delivery date ({chosen}): the "
         "earlier of a customer's registration and an export cancellation, within a year of first airworthiness.", None),
        ("2. Registry events are counted in GD's fiscal quarter windows, by cabin (large, mid).", None),
        ("3. Ratio estimate = this quarter's events x reported deliveries over the last four quarters / registry "
         "events over the same four quarters, by cabin.", None),
        ("4. Design window 2017Q1 to 2019Q4 chose the event definition; the 26 quarters 2020Q1 to 2026Q2 are held "
         "out and scored against seasonal, last-quarter and GD guidance baselines.", None),
        ("5. Segment estimates: the delivery estimate x trailing Aerospace revenue per delivery, services included: "
         "a mechanical estimate; defense segments use the seasonal naive with drift.", None),
        ("", None),
        ("Colour key", BOLD),
        ("Blue: typed input from a source file. Black: formula.", None),
        ("Counts are aircraft; dollars are $M.", None),
        ("", None),
        ("Sources", BOLD),
        ("GD earnings releases (Exhibit 99.1 to the results 8-K) on SEC EDGAR, CIK 40533: deliveries, segment "
         "revenue and operating earnings, backlog.", None),
        (f"FAA Releasable Aircraft database (ReleasableAircraft.zip), snapshot {snap}.", None),
        ("Repository: https://github.com/rishabbshankar226/gulfstream-delivery-nowcast", None),
        ("", None),
        ("Previewers that do not calculate (Quick Look, some web viewers) show formula cells blank until Excel "
         "calculates them. The file asks Excel to recalculate on open.", None),
    ]
    for i, (text, font) in enumerate(lines, start=1):
        c = ws.cell(row=i, column=1, value=text or None)
        if font:
            c.font = font
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 110


def quarters(wb, Y, N, chosen, ends):
    ws = wb.create_sheet("Quarters")
    header(ws, HEAD)
    for i, q in enumerate(QUARTERS):
        r = i + 2
        put(ws, f"A{r}", q)
        put(ws, f"B{r}", ends[q])
        put(ws, f"C{r}", Y[q]["large"], F_AIR, typed=True)
        put(ws, f"D{r}", Y[q]["mid"], F_AIR, typed=True)
        put(ws, f"E{r}", f"=C{r}+D{r}", F_AIR)
        put(ws, f"F{r}", N[q][chosen]["large"], F_AIR, typed=True)
        put(ws, f"G{r}", N[q][chosen]["mid"], F_AIR, typed=True)
        if r >= 6:
            a, b = r - 4, r - 1
            put(ws, f"H{r}", f"=IF(SUM(F{a}:F{b})=0,AVERAGE(C{a}:C{b}),F{r}*SUM(C{a}:C{b})/SUM(F{a}:F{b}))", F_AIR)
            put(ws, f"I{r}", f"=IF(SUM(G{a}:G{b})=0,AVERAGE(D{a}:D{b}),G{r}*SUM(D{a}:D{b})/SUM(G{a}:G{b}))", F_AIR)
            put(ws, f"J{r}", f"=H{r}+I{r}", F_AIR)
            put(ws, f"K{r}", f"=F{r}+G{r}", F_AIR)
            put(ws, f"L{r}", f"=E{r - 4}", F_AIR)
            put(ws, f"M{r}", f"=E{r - 1}", F_AIR)
            for col, src in zip("NOPQ", "JKLM"):
                put(ws, f"{col}{r}", f"=ABS({src}{r}-E{r})", F_AIR)
            put(ws, f"R{r}", "design" if qidx(q) <= qidx("2019Q4") else "holdout")
    ws.freeze_panes = "B2"
    widths(ws, [9, 11] + [10] * 15 + [9])
    return ws


def summary(wb):
    ws = wb.create_sheet("Summary")
    header(ws, ["Metric", "Design", "Holdout"])
    for i, (label, col) in enumerate((("MAE ratio", "N"), ("MAE raw", "O"), ("MAE seasonal", "P"), ("MAE last", "Q"))):
        r = i + 2
        put(ws, f"A{r}", label)
        put(ws, f"B{r}", f"=AVERAGE(Quarters!{col}6:{col}17)", F_AIR)
        put(ws, f"C{r}", f"=AVERAGE(Quarters!{col}18:{col}43)", F_AIR)
    ws.freeze_panes = "B2"
    widths(ws, [16, 12, 12])


def band_percentiles(root, q):
    errs = list(read_json(Path(root) / "results/metrics.json")["band_errors"])
    for p in sorted(Path(root).glob("results/live/*_score.json")):
        s = read_json(p)
        if qidx(s["quarter"]) < qidx(q) and s.get("locked") and s.get("nowcast"):
            errs.append(s["nowcast"]["total"] - s["reported"]["total"])
    return stats.nearest_rank(errs, 0.1), stats.nearest_rank(errs, 0.9)


def live_sheet(wb, root, pred):
    ws = wb.create_sheet("Live")
    labels = ["Quarter", "Snapshot", "Registry large", "Registry mid", "Trailing reported large",
              "Trailing reported mid", "Trailing registry large", "Trailing registry mid", "Nowcast large",
              "Nowcast mid", "Nowcast total", "Past-miss P10", "Past-miss P90", "Band low", "Band high"]
    for i, lab in enumerate(labels, start=1):
        ws.cell(row=i, column=1, value=lab).font = BOLD
    q = pred["quarter"]
    last = 2 + QUARTERS.index("2026Q2")          # row of the quarter before 2026Q3
    first = last - 3
    p10, p90 = band_percentiles(root, q)
    put(ws, "B1", q)
    put(ws, "B2", pred["snapshot"])
    put(ws, "B3", pred["events"]["large"], F_AIR, typed=True)
    put(ws, "B4", pred["events"]["mid"], F_AIR, typed=True)
    put(ws, "B5", f"=SUM(Quarters!C{first}:C{last})", F_AIR)
    put(ws, "B6", f"=SUM(Quarters!D{first}:D{last})", F_AIR)
    put(ws, "B7", pred["trailing"]["registry"]["large"], F_AIR, typed=True)
    put(ws, "B8", pred["trailing"]["registry"]["mid"], F_AIR, typed=True)
    put(ws, "B9", "=IF(B7=0,B5/4,B3*B5/B7)", F_AIR)
    put(ws, "B10", "=IF(B8=0,B6/4,B4*B6/B8)", F_AIR)
    put(ws, "B11", "=B9+B10", F_AIR)
    put(ws, "B12", p10, F_AIR, typed=True)
    put(ws, "B13", p90, F_AIR, typed=True)
    put(ws, "B14", "=B11-B13", F_AIR)
    put(ws, "B15", "=B11-B12", F_AIR)
    ws.freeze_panes = "B2"
    widths(ws, [24, 14])


def segments_sheet(wb, root):
    ws = wb.create_sheet("Segments")
    header(ws, ["Segment"] + SEG_Q + ["TTM 2026Q2", "TTM 2025Q2", "Drift 2026Q3", "TTM margin", "Backlog 2026Q2",
                                      "Coverage (years)"])
    seg = {}
    for r in read_csv(Path(root) / "data/processed/segments.csv"):
        seg.setdefault(r["segment"], {})[r["quarter"]] = (int(r["revenue_usd"]), int(r["operating_earnings_usd"]))
    backlog = {r["segment"]: int(r["total_backlog_usd"])
               for r in read_csv(Path(root) / "data/processed/backlog_2026Q2.csv")}
    cols = [get_column_letter(i + 2) for i in range(len(SEG_Q))]          # B..I
    for i, s in enumerate(SEGMENTS):
        r, ro = i + 2, i + 7
        put(ws, f"A{r}", s)
        put(ws, f"A{ro}", f"{s} operating earnings")
        for col, q in zip(cols, SEG_Q):
            put(ws, f"{col}{r}", seg[s][q][0] / 1e6, F_USD, typed=True)
            put(ws, f"{col}{ro}", seg[s][q][1] / 1e6, F_USD, typed=True)
        put(ws, f"J{r}", f"=SUM(F{r}:I{r})", F_USD)
        put(ws, f"K{r}", f"=SUM(B{r}:E{r})", F_USD)
        put(ws, f"L{r}", f"=F{r}*J{r}/K{r}", F_USD)
        put(ws, f"M{r}", f"=SUM(F{ro}:I{ro})/J{r}", F_PCT)
        put(ws, f"N{r}", backlog[s] / 1e6, F_USD, typed=True)
        put(ws, f"O{r}", f"=N{r}/J{r}", F_RATIO)
    last = 2 + QUARTERS.index("2026Q2")
    rows = [("TTM deliveries", f"=SUM(Quarters!E{last - 3}:E{last})", F_AIR),
            ("Revenue per delivery", "=J2/B12", F_USD),
            ("Nowcast deliveries", "=Live!B11", F_AIR),
            ("Aerospace from nowcast", "=B14*B13", F_USD),
            ("Aerospace operating earnings from nowcast", "=B15*M2", F_USD),
            ("Revenue total", "=B15+L3+L4+L5", F_USD),
            ("Operating earnings total", "=B16+L3*M3+L4*M4+L5*M5", F_USD)]
    for i, (lab, f, fmt) in enumerate(rows):
        put(ws, f"A{12 + i}", lab)
        put(ws, f"B{12 + i}", f, fmt)
    put(ws, "A20", "Aerospace from nowcast is the delivery estimate x trailing Aerospace revenue per delivery, "
                   "services included: a mechanical estimate. Segment operating earnings exclude Corporate.")
    ws.freeze_panes = "B2"
    widths(ws, [40] + [10] * 8 + [12, 12, 12, 11, 14, 12])


def sensitivity(wb):
    ws = wb.create_sheet("Sensitivity")
    header(ws, ["Deliveries change", "Deliveries", "Aerospace revenue"])
    for i, k in enumerate(range(-4, 5)):
        r = i + 2
        put(ws, f"A{r}", k, F_AIR, typed=True)
        put(ws, f"B{r}", f"=Live!$B$11+A{r}", F_AIR)
        put(ws, f"C{r}", f"=B{r}*Segments!$B$13", F_USD)
    ws.freeze_panes = "B2"
    widths(ws, [18, 12, 18])


def pin(path, date):
    """Pin the document dates and every zip entry's time so a rebuild writes identical bytes."""
    stamp = f"{date}T00:00:00Z"
    y, m, d = (int(x) for x in date.split("-"))
    with zipfile.ZipFile(path) as z:
        entries = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, body in entries:
            if name == "docProps/core.xml":
                body = re.sub(rb"(<dcterms:(created|modified)[^>]*>)[^<]*", lambda mm: mm.group(1) + stamp.encode(), body)
            info = zipfile.ZipInfo(name, date_time=(y, m, d, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, body)


def input_digest(root):
    root = Path(root)
    lines = []
    # The builder's own source counts as an input, so a change to a formula or a format rebuilds the file.
    for p in (basis_path(root), root / "results/metrics.json", root / "data/processed/segments.csv",
              root / "src/gdn/workbook.py"):
        lines.append(f"{sha256(p.read_bytes())}  {p.relative_to(root)}")
    return "\n".join(lines) + "\n"


def build(root="."):
    root = Path(root)
    Y, N = model.load_reported(root), model.load_registry(root)
    chosen = read_json(root / "results/metrics.json")["definition"]
    ends = {r["quarter"]: r["fiscal_end"] for r in read_csv(root / "data/processed/gd_deliveries.csv")}
    snap = read_json(root / "data/snapshots/MANIFEST.json")["backtest"]
    pred = read_json(basis_path(root))
    wb = Workbook()
    about(wb, snap, chosen)
    quarters(wb, Y, N, chosen, ends)
    summary(wb)
    live_sheet(wb, root, pred)
    segments_sheet(wb, root)
    sensitivity(wb)
    wb.calculation.fullCalcOnLoad = True
    out = root / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.properties.creator = "Rishabb Shankar"
    wb.save(out)
    pin(out, snap)
    write_text(root / INPUTS, input_digest(root))


def run(root=".", force=False):
    root = Path(root)
    if not basis_path(root).exists():
        print("skip workbook: no basis prediction yet")
        return 0
    if not force and (root / OUT).exists() and (root / INPUTS).exists() and \
            (root / INPUTS).read_text() == input_digest(root):
        print("workbook inputs unchanged; kept")
        return 0
    build(root)
    print(f"wrote {OUT}")
    return 0
