"""The number ledger (P1): every figure on the public surface, bound to its label and traced to a source field.

Run with the tools venv, from anywhere:

    ~/gdn-prepub/venv/bin/python tools/prepub/ledger.py --root . --out docs/prepub/LEDGER.csv

How it binds and traces
- A table cell's label is its row header and column header (and the table's header signature). A prose
  number's label is the sentence around it. A rule (ledger_rules.py) names the label first: a table rule by
  header signature, row label and column header, a prose rule by a sentence template with typed slots. Only
  then is the value compared with the one source field the rule names, at the precision shown. A number that
  no rule's label claims is `untraced`. Value-only matching is never used for a figure.
- Status: `traced` (the displayed text is the source value correctly rounded), `rounding` (it is the source
  value rounded the wrong way: floor or ceiling, not nearest), `mismatch` (anything else, or a unit named in
  the label that the value does not carry), `untraced` (no label rule), `stale` (a sentence about a lock or a
  score that does not agree with results/live/, or a built file older than its input).
- Identifiers (quarter labels, ISO dates, clock times, hashes, accession numbers, URLs, code spans, model
  names, document names such as 8-K or ASC 606) are not figures. Quarters, dates, hashes and accession
  numbers are checked for membership in the source set and listed with class `id`. Dates inside a
  live-record template are bound by label like any figure.
"""
import argparse
import csv
import datetime as dt
import decimal
import hashlib
import html.parser
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12}
NUM = r"[-−+]?\$?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:%|B\b|M\b)?"
NUM_RE = re.compile(r"(?<![\w.$,])(?P<sign>[-−+])?(?P<cur>\$)?(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
                    r"(?P<unit>%|B\b|M\b)?(?![\w]|\.\d|,\d{3})")
WORD_RE = re.compile(r"(?<![\w-])(" + "|".join(WORDS) + r")(?![\w-])", re.I)
ONE_OK = re.compile(r"one (locked quarter|quarter (shows|will show|is one data point)|snapshot|decimal|source\b|lock per"
                    r"|standard error above|airframe in \d{4}Q|G700 type code)", re.I)

MASKS = [
    ("url", re.compile(r"https?://[^\s)>\]\"']+")),
    ("code", re.compile(r"`[^`\n]*`")),
    ("accn", re.compile(r"\b\d{10}-\d{2}-\d{6}\b")),
    ("hash", re.compile(r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{32,64}\b")),
    ("datetime", re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b")),
    ("date", re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")),
    ("date8", re.compile(r"\b20\d{6}\b")),
    ("time", re.compile(r"\b\d{2}:\d{2}\b")),
    ("quarter", re.compile(r"\b(?:19|20)\d{2}Q[1-4]\b")),
    ("model", re.compile(r"\bG(?:V?I{1,3}|IV|V)[- ]?(?:X|SP)?(?:[- ]G\d{3})?\b|\bG[- ]?\d{3}(?:ER)?\b|\bGULFSTREAM \d{3}\b"
                         r"|\bC-(?:20|37)[A-Z]?\b|\bGV(?:I{1,3})?-G\d{3}\b", re.I)),
    ("doc", re.compile(r"\b(?:8|10)-[KQ]\b|\bExhibit 99\.1\b|\bExhibit \d+\b|\b99\.1\b|\bASC 606\b|\bForm \d+(?:-[KQ])?\b|§\s?\d+(?:\.\d+)*"
                       r"|\bCIK \d+\b|\bWCAG \d\.\d\b|\bChart\.js [\d.]+\b|\bPython \d\.\d+\b|\b[EPSHQLTNO]\d{1,2}\b"
                       r"|\blag-1\b|\bLag-1\b|\b4Q\b|\b1600 x 900\b|\b60-second\b|\"### \d\.\d\"|\bsha256\b")),
]


class Tok:
    __slots__ = ("start", "end", "text", "kind", "value", "decimals", "unit", "cur")

    def __init__(self, start, end, text, kind, value=None, decimals=0, unit="", cur=""):
        self.start, self.end, self.text, self.kind = start, end, text, kind
        self.value, self.decimals, self.unit, self.cur = value, decimals, unit, cur


def mask(text):
    """Identifier spans [(start, end, kind, text)] and the text with them blanked (same length)."""
    spans, out = [], list(text)
    for kind, rx in MASKS:
        for m in rx.finditer("".join(out)):
            spans.append((m.start(), m.end(), kind, m.group(0)))
            for i in range(m.start(), m.end()):
                out[i] = "\x00"
    return spans, "".join(out)


def tokens(text):
    """Every figure and identifier in a text, in order."""
    spans, masked = mask(text)
    toks = [Tok(s, e, t, "id:" + k) for s, e, k, t in spans]
    for m in NUM_RE.finditer(masked):
        raw = m.group("num").replace(",", "")
        dec = len(raw.split(".")[1]) if "." in raw else 0
        v = float(raw)
        if m.group("sign") in ("-", "−"):
            # a minus glued to a word or digit before it is a hyphen, not a sign
            before = masked[m.start() - 1] if m.start() else " "
            if not (before.isalnum()):
                v = -v
        toks.append(Tok(m.start(), m.end(), m.group(0), "num", v, dec, m.group("unit") or "", m.group("cur") or ""))
    for m in WORD_RE.finditer(masked):
        w = m.group(1).lower()
        if w == "one" and not ONE_OK.match(masked[m.start():m.start() + 40]):
            continue
        toks.append(Tok(m.start(), m.end(), m.group(0), "word", float(WORDS[w]), 0))
    toks.sort(key=lambda t: t.start)
    return toks


# ---------- formats ----------
def _dec(x):
    return decimal.Decimal(repr(float(x))) if not isinstance(x, decimal.Decimal) else x


def fmt_python(x, d):
    return f"{x:.{d}f}"


def round_half_up(x, d):
    q = decimal.Decimal(1).scaleb(-d)
    return str(decimal.Decimal(x).quantize(q, rounding=decimal.ROUND_HALF_UP))


def js_f1(x):
    """site/app.js f1: (Math.round(x * 10) / 10).toFixed(1). Math.round rounds half toward +infinity."""
    import math
    return f"{math.floor(x * 10 + 0.5) / 10:.1f}"


def compare(tok, expected, fmt, js=False):
    """(status, expected_text). fmt: int f1 f2 f3 pct0 pct1 usdB usdM usdM1 whole word ratio2 x1 any<d>."""
    if expected is None:
        return "untraced", ""
    scale = 1.0
    d = tok.decimals
    if fmt == "usdB":
        scale, want_unit = 1e9, "B"
    elif fmt == "usdM":
        scale, want_unit = 1e6, "M"
    elif fmt.startswith("pct"):
        want_unit = "%"
    else:
        want_unit = None
    if want_unit is not None and tok.unit != want_unit:
        return "mismatch", f"unit {want_unit} expected, {tok.unit or 'none'} shown"
    if want_unit is None and tok.unit in ("%", "B", "M") and fmt not in ("any",):
        return "mismatch", f"no unit expected, {tok.unit} shown"
    x = float(expected) / scale
    shown = decimal.Decimal(tok.text.replace(",", "").replace("$", "").replace("%", "").replace("−", "-")
                            .replace("+", "").rstrip("BM")) if tok.kind == "num" else decimal.Decimal(int(tok.value))
    if tok.kind == "num" and tok.value is not None and tok.value < 0 and shown > 0:
        shown = -shown
    need = {"int": 0, "whole": 0, "word": 0, "f1": 1, "f2": 2, "f3": 3, "pct0": 0, "pct1": 1, "usdB": 1, "usdM": 0,
            "ratio2": 2, "x1": 1}.get(fmt)
    if need is not None and d != need and not (fmt in ("int", "whole", "word") and d == 0):
        return "mismatch", f"{need} decimals expected, {d} shown"
    if fmt in ("int", "word") and abs(x - round(x)) > 1e-9:
        return "mismatch", f"source {x!r} is not a whole number"
    right = decimal.Decimal(js_f1(x)) if (js and d == 1 and fmt in ("f1",)) else decimal.Decimal(fmt_python(x, d))
    if shown == right or (shown == 0 and right == 0):
        return "traced", str(right)
    q = decimal.Decimal(1).scaleb(-d)
    exact = decimal.Decimal(repr(x))
    lo = exact.quantize(q, rounding=decimal.ROUND_FLOOR)
    hi = exact.quantize(q, rounding=decimal.ROUND_CEILING)
    if shown in (lo, hi):
        return "rounding", str(right)
    return "mismatch", str(right)


# ---------- surface readers ----------
class Block:
    """One labelled piece of a surface: a prose block, or a table cell with its row and column header."""

    def __init__(self, surface, file, line, kind, text, row="", col="", table="", section="", ident=""):
        self.surface, self.file, self.line, self.kind, self.text = surface, file, line, kind, text
        self.row, self.col, self.table, self.section, self.ident = row, col, table, section, ident

    def label(self, tok=None):
        if self.kind == "cell":
            return f"{self.row} | {self.col}"
        if tok is None:
            return self.text[:160]
        s = self.text.rfind(". ", 0, tok.start) + 1
        e = self.text.find(". ", tok.end)
        e = len(self.text) if e < 0 else e + 1
        return self.text[s:e].strip()[:200]


def md_blocks(surface, file, text):
    out, section, para, start = [], "", [], 0
    lines = text.split("\n")
    i = 0

    def flush():
        nonlocal para
        if para:
            out.append(Block(surface, file, start, "prose", " ".join(x.strip() for x in para), section=section))
            para = []

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            flush()
            section = ln.lstrip("#").strip()
            out.append(Block(surface, file, i + 1, "heading", section, section=section))
        elif ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[-| :]+\|\s*$", lines[i + 1]):
            flush()
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            sig = " | ".join(head)
            for c in head:
                out.append(Block(surface, file, i + 1, "colhead", c, table=sig, section=section))
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                for k, c in enumerate(cells):
                    if k == 0:
                        out.append(Block(surface, file, j + 1, "rowhead", c, table=sig, section=section))
                        continue
                    out.append(Block(surface, file, j + 1, "cell", c, row=cells[0], col=head[k] if k < len(head) else "",
                                     table=sig, section=section))
                j += 1
            i = j
            continue
        elif not ln.strip():
            flush()
        elif re.match(r"^\s*([-*]|\d+\.)\s", ln):
            flush()
            start = i + 1
            para = [re.sub(r"^\s*([-*]|\d+\.)\s", "", ln)]
        elif ln.startswith("```"):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            i = j
        else:
            if not para:
                start = i + 1
            para.append(ln)
        i += 1
    flush()
    return out


class _Note(html.parser.HTMLParser):
    BLOCK = {"p", "li", "h1", "h2", "h3"}

    def __init__(self, surface, file):
        super().__init__(convert_charrefs=True)
        self.surface, self.file, self.out = surface, file, []
        self.stack, self.buf, self.pos = [], None, None
        self.section, self.skip = "", 0
        self.table, self.cap, self.rows, self.row, self.cell, self.in_head = None, "", [], None, None, False
        self.lists, self.cites, self.olitems = [], [], []   # for the PDF: citation marks and list numbers Chrome prints

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("style", "script"):
            self.skip += 1
        if tag in ("ol", "ul"):
            self.lists.append(0 if tag == "ol" else None)
        if tag == "li" and self.lists and self.lists[-1] is not None:
            self.lists[-1] += 1
        if tag == "sup" and a.get("data-n") and self.buf is not None:
            self.cites.append((" ".join("".join(self.buf).split())[-24:], a["data-n"]))
        if tag == "table":
            self.table, self.rows = True, []
        elif tag == "thead":
            self.in_head = True
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell, self.pos = [], self.getpos()
        elif tag in self.BLOCK or (tag == "div" and a.get("class") in ("cap", "src", "byline")) or \
                (tag == "p" and True):
            if self.cell is None and self.buf is None:
                self.buf, self.pos, self.kindtag, self.buftag = [], self.getpos(), (a.get("class") or tag), tag

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip -= 1
        if tag in ("ol", "ul") and self.lists:
            self.lists.pop()
        if tag == "li" and self.lists and self.lists[-1] is not None and self.buf is not None:
            self.olitems.append((self.lists[-1], " ".join("".join(self.buf).split())[:24]))
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(("th" if tag == "th" else "td", " ".join("".join(self.cell).split()), self.pos))
            self.cell = None
        elif tag == "thead":
            self.in_head = False
        elif tag == "tr" and self.row is not None:
            self.rows.append((self.in_head, self.row))
            self.row = None
        elif tag == "table" and self.table:
            self._table()
            self.table = None
        elif self.buf is not None and self.cell is None and tag == getattr(self, "buftag", None):
            text = " ".join("".join(self.buf).split())
            if text:
                kind = "heading" if tag in ("h1", "h2", "h3") else ("caption" if self.kindtag == "cap" else "prose")
                if kind == "heading":
                    self.section = text
                if kind == "caption":
                    self.cap = text
                self.out.append(Block(self.surface, self.file, f"{self.pos[0]}:{self.pos[1]}", kind, text,
                                      section=self.section))
            self.buf = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.cell is not None:
            self.cell.append(data)
        elif self.buf is not None:
            self.buf.append(data)

    def _table(self):
        head = []
        for is_head, row in self.rows:
            if is_head:
                head = [c[1] for c in row]
                for c in row:
                    self.out.append(Block(self.surface, self.file, f"{c[2][0]}:{c[2][1]}", "colhead", c[1],
                                          table=" | ".join(head), section=self.section, ident=self.cap))
                continue
            cells = [c[1] for c in row]
            sig = " | ".join(head)
            for k, c in enumerate(row):
                pos = f"{c[2][0]}:{c[2][1]}"
                if k == 0:
                    self.out.append(Block(self.surface, self.file, pos, "rowhead", c[1], table=sig, section=self.section,
                                          ident=self.cap))
                else:
                    self.out.append(Block(self.surface, self.file, pos, "cell", c[1], row=cells[0],
                                          col=head[k] if k < len(head) else "", table=sig, section=self.section,
                                          ident=self.cap))


PDF_MARKS = {"cites": [], "olitems": []}


def html_blocks(surface, file, text):
    p = _Note(surface, file)
    p.feed(text)
    if surface == "note":
        PDF_MARKS["cites"], PDF_MARKS["olitems"] = p.cites, p.olitems
    return p.out


def strip_pdf_marks(text):
    """Drop what Chrome prints but note.html's text does not hold: citation numbers and ordered-list numbers."""
    def flex(s):
        return r"\s*".join(re.escape(w) for w in s.split())
    pos = 0
    for n, head in PDF_MARKS["olitems"]:
        m = re.compile(r"(?<![\w.])" + re.escape(str(n)) + r"\.\s+(?=" + flex(head) + ")").search(text, pos)
        if m:
            text = text[:m.start()] + text[m.end():]
            pos = m.start()
    pos = 0
    for tail, n in PDF_MARKS["cites"]:
        m = re.compile("(" + flex(tail) + r")\s*" + re.escape(n) + r"(?!\d)").search(text, pos)
        if m:
            text = text[:m.end(1)] + " " + text[m.end():]
            pos = m.end(1)
    return text


def site_blocks(root, venv_py):
    out_json = Path(root) / ".build/ledger/site_render.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([venv_py, str(HERE / "render_site.py"), str(root), str(out_json)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"site render failed: {r.stderr[-800:]}")
    d = json.loads(out_json.read_text())
    out = []
    for n, it in enumerate(d["items"]):
        if it["kind"] == "cell":
            row, _, col = it["label"].partition(" | ")
            out.append(Block("dashboard", f"site(rendered)#{it['id']}", n, "cell", it["text"], row=row, col=col,
                             table=it["id"], section=it.get("section", ""), ident=it["id"]))
        elif it["kind"] == "dd":
            out.append(Block("dashboard", f"site(rendered)#{it['id']}", n, "cell", it["text"], row=it["label"], col="value",
                             table=it["id"], section=it.get("section", ""), ident=it["id"]))
        else:
            out.append(Block("dashboard", f"site(rendered)#{it['id'] or it['kind']}", n, "prose", it["text"],
                             section=it.get("section", ""), ident=it["id"]))
    return out, d


def workbook_cells(path):
    """{(sheet, coord): value} with every formula recalculated by the `formulas` package; plus labels."""
    import formulas
    import openpyxl
    model = formulas.ExcelModel().loads(str(path)).finish()
    sol = model.calculate()   # the solution holds each cell's computed value; to_dict() holds the formula text
    vals = {}
    for k, v in sol.items():
        m = re.match(r"'\[[^\]]+\](.+)'!([A-Z]+\d+)$", str(k))
        if not m or not hasattr(v, "value"):
            continue
        x = v.value[0, 0]
        vals[(m.group(1).upper(), m.group(2))] = x.item() if hasattr(x, "item") else x
    wb = openpyxl.load_workbook(path)
    cells = []
    for ws in wb:
        head = {c.column_letter: c.value for c in ws[1]}
        for row in ws.iter_rows():
            rowlab = row[0].value
            for c in row:
                if c.value is None:
                    continue
                is_formula = isinstance(c.value, str) and c.value.startswith("=")
                # a formula the package could not compute stays None, and the ledger flags it: never the formula text
                v = vals.get((ws.title.upper(), c.coordinate)) if is_formula else c.value
                cells.append({"sheet": ws.title, "coord": c.coordinate, "row": rowlab, "col": head.get(c.column_letter),
                              "value": v, "formula": c.value if is_formula else None, "fmt": c.number_format})
    return cells


def pdf_text(path):
    import pypdf
    r = pypdf.PdfReader(str(path))
    return [p.extract_text() or "" for p in r.pages]


# ---------- the run ----------
def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


COLS = ["surface", "file_line", "value", "label", "traced_field", "expected", "status", "note"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="docs/prepub/LEDGER.csv")
    ap.add_argument("--venv-py", default=str(HERE.parents[1] / ".venv/bin/python"))
    ap.add_argument("--skip", default="", help="comma list of surfaces to skip: dashboard,pdf,workbook,build")
    ap.add_argument("--charts", default=str(HERE / "chart_numbers.csv"))
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    skip = set(filter(None, a.skip.split(",")))
    import ledger_rules as R
    F = R.load_facts(root)
    rows = []

    def emit(surface, file_line, value, label, field, expected, status, note=""):
        rows.append({"surface": surface, "file_line": file_line, "value": value, "label": " ".join(str(label).split())[:220],
                     "traced_field": field, "expected": expected, "status": status, "note": note})

    blocks = []
    for surface, rel in R.TEXT_SURFACES:
        p = root / rel
        if not p.exists():
            emit(surface, rel, "", "file", "", "", "mismatch", "file missing")
            continue
        text = p.read_text()
        blocks += html_blocks(surface, rel, text) if rel.endswith(".html") else md_blocks(surface, rel, text)
    site_data = None
    if "dashboard" not in skip:
        sb, site_data = site_blocks(root, a.venv_py)
        blocks += sb
        for e in site_data["errors"]:
            emit("dashboard", "site(rendered)", "", "page error", "", "", "mismatch", e[:200])

    note_tokens = []  # (text, status, field, label) of every figure in the note, in order, for the PDF
    for b in blocks:
        if b.kind == "rowhead":
            # a row's own label (a year, a day count, a quarter): it names the row, it is not a figure of its own
            for tok in tokens(R.normalize(b.text)):
                if tok.kind in ("num", "word"):
                    emit(b.surface, f"{b.file}:{b.line}", tok.text, f"row label in table [{b.table[:60]}]", "row label", "",
                         "traced", "class id (row label)")
                    if b.surface == "note":
                        note_tokens.append((tok.text, "traced", "row label", b.text[:80]))
            continue
        res = sorted(R.trace_block(b, F, tokens, compare), key=lambda r: r[0].start)
        for tok, field, expected, status, note in res:
            fl = f"{b.file}:{b.line}"
            emit(b.surface, fl, tok.text, b.label(tok), field, expected, status, note)
            if b.surface == "note" and (tok.kind in ("num", "word")):
                note_tokens.append((tok.text, status, field, b.label(tok)))
        if b.kind in ("prose", "heading", "caption", "cell"):
            for sent, verdict, why in R.stale_check(b, F):
                emit(b.surface, f"{b.file}:{b.line}", "", sent, "results/live state", "", verdict, why)

    # the PDF: its text layer must carry the note's figures, in order; each inherits the note's binding
    if "pdf" not in skip:
        pdf = root / "output/GD_research_note.pdf"
        stamp = root / "output/GD_research_note.inputs.sha256"
        note = root / "report/note.html"
        if pdf.exists():
            import difflib
            pages = pdf_text(pdf)
            ptoks = []
            joined = strip_pdf_marks("\f".join(R.pdf_normalize(t) for t in pages))
            for n, t in enumerate(joined.split("\f")):
                ptoks += [(tk.text, n + 1) for tk in tokens(t) if tk.kind in ("num", "word")]
            a_seq, b_seq = [t[0] for t in note_tokens], [t[0] for t in ptoks]
            sm = difflib.SequenceMatcher(None, a_seq, b_seq, autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal":
                    for k in range(i2 - i1):
                        txt, st, field, lab = note_tokens[i1 + k]
                        emit("note-pdf", f"output/GD_research_note.pdf:p{ptoks[j1 + k][1]}", txt, lab, field, "", st,
                             "bound through report/note.html")
                else:
                    for k in range(j1, j2):
                        emit("note-pdf", f"output/GD_research_note.pdf:p{ptoks[k][1]}", ptoks[k][0], "figure in the PDF text "
                             "that report/note.html does not carry at this position", "", "", "mismatch", "PDF differs from note.html")
                    for k in range(i1, i2):
                        emit("note-pdf", "output/GD_research_note.pdf", note_tokens[k][0], note_tokens[k][3], note_tokens[k][2],
                             "", "mismatch", "figure in note.html missing from the PDF text at this position")
            if stamp.exists() and note.exists():
                want, have = stamp.read_text().split()[0], R.pdf_input_hash(root)
                emit("note-pdf", "output/GD_research_note.inputs.sha256", want[:16], "PDF input stamp against sha256 of its inputs",
                     "sha256(report/note.html inputs)", have[:16], "traced" if want == have else "stale",
                     "" if want == have else "the PDF was printed from an older note.html")
            site_pdf = root / "site/GD_research_note.pdf"
            if site_pdf.exists():
                same = sha256_file(site_pdf) == sha256_file(pdf)
                emit("note-pdf", "site/GD_research_note.pdf", sha256_file(site_pdf)[:16], "site copy of the PDF",
                     "output/GD_research_note.pdf", sha256_file(pdf)[:16], "traced" if same else "stale",
                     "" if same else "site copy differs from output copy")
        else:
            emit("note-pdf", "output/GD_research_note.pdf", "", "file", "", "", "mismatch", "file missing")

    if "workbook" not in skip:
        wbp = root / "output/gd_gulfstream_model.xlsx"
        for c in workbook_cells(wbp):
            for field, expected, status, note, value, label in R.trace_workbook_cell(c, F, tokens, compare):
                emit("workbook", f"output/gd_gulfstream_model.xlsx:{c['sheet']}!{c['coord']}", value, label, field,
                     expected, status, note)

    # numbers drawn inside chart images are listed by hand
    cp = Path(a.charts)
    if cp.exists():
        for r in csv.DictReader(cp.open()):
            field, expected, status, note = R.trace_chart_row(r, F)
            emit("chart", r["file"], r["value"], r["label"], field, expected, status, note)

    for r in R.extra_checks(root, F):
        emit(*r)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tally = {}
    for r in rows:
        tally.setdefault(r["surface"], {}).setdefault(r["status"], 0)
        tally[r["surface"]][r["status"]] += 1
    for s in sorted(tally):
        print(f"{s:12s} " + "  ".join(f"{k}={v}" for k, v in sorted(tally[s].items())))
    bad = [r for r in rows if r["status"] in ("mismatch", "untraced", "stale", "rounding")]
    print(f"rows {len(rows)}  flagged {len(bad)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
