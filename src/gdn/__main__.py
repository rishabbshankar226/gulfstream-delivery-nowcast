"""python -m gdn <stage> [--offline]"""
import argparse
import importlib
import importlib.util
import sys

# stage: (module, function)
STAGES = {
    "data": ("data", "run"),
    "diagnostics": ("diagnostics", "run"),
    "design": ("model", "run_design"),
    "holdout": ("model", "run_holdout"),
    "snapshot": ("live", "run_snapshot"),
    "nowcast": ("live", "run_nowcast"),
    "lock": ("live", "run_lock"),
    "score": ("live", "run_score"),
    "estimates": ("estimates", "run"),
    "workbook": ("workbook", "run"),
    "charts": ("charts", "run"),
    "claims": ("claims", "run"),
    "note": ("note", "run"),
    "pdf": ("note", "run_pdf"),
    "site": ("site_data", "run"),
    "report": ("report", "run"),
    "daily": ("daily", "run"),
}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gdn")
    ap.add_argument("stage", choices=sorted(STAGES))
    ap.add_argument("--offline", action="store_true", help="never download a snapshot or read SEC")
    ap.add_argument("--core", action="store_true", help="daily: skip the rebuilds")
    ap.add_argument("--now", help="ISO time in UTC to run as, for rehearsals")
    a = ap.parse_args(argv)
    mod, fn = STAGES[a.stage]
    if importlib.util.find_spec(f"gdn.{mod}") is None:
        print(f"skip {a.stage}: src/gdn/{mod}.py is not written yet")
        return 0
    f = getattr(importlib.import_module(f"gdn.{mod}"), fn)
    kw = {}
    if a.stage == "data":
        kw["network"] = not a.offline
    if a.stage in ("snapshot", "nowcast", "lock", "score", "daily"):
        kw["now"] = a.now
        kw["offline"] = a.offline
    if a.stage == "daily":
        kw["core"] = a.core
    r = f(**kw)
    return r if isinstance(r, int) else 0


if __name__ == "__main__":
    sys.exit(main())
