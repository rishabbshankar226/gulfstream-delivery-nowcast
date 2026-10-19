"""Pick the 30 airframes of the Phase 9 audit, deterministically, and write docs/build/audit_sample.csv."""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gdn import events, faa  # noqa: E402
from gdn.files import read_csv, write_csv  # noqa: E402

GOV = {"QATAR", "KUWAIT", "SAUDI ARABIA", "ITALY", "KOREA REP OF (S)", "POLAND", "CZECH REPUBLIC", "MEXICO",
       "BRAZIL", "MALAYSIA", "SPAIN", "UNITED KINGDOM", "CANADA", "AUSTRIA"}


def yr(d):
    return d[:4] if d else ""


def main():
    rows = events.read_serials_rows(read_csv(ROOT / "data/processed/serials.csv"))
    sub = faa.read_subset(ROOT, faa.manifest(ROOT)["backtest"])
    regs = {}
    for kind in ("MASTER", "DEREG"):
        for r in faa.read_table(sub[kind], kind):
            regs.setdefault((r["MFRMDLCODE"][:3], r["SERIALNUMBER"].upper()), set()).add("N" + r["NNUMBER"])
    rng = random.Random(20261019)
    dom = [r for r in rows if r["e1"] and r["e1"] == r["customer_cert"] and not r["export_cancel"]
           and "2016" <= yr(r["e1"]) <= "2019"]
    exp = [r for r in rows if r["e1"] and r["export_cancel"] and r["e1"] == r["export_cancel"]
           and "2014" <= yr(r["e1"]) <= "2019"]
    exp_gov = [r for r in exp if r["export_country"] in GOV]
    exp_rest = [r for r in exp if r["export_country"] not in GOV]
    e2o = [r for r in rows if r["e2"] and not r["e1"] and yr(r["e2"]) <= "2019"]
    bnd = [r for r in rows if not r["e1"] and not r["e2"] and (r["customer_cert"] or r["export_cancel"] or r["gulfstream_cancel"])
           and r["first_airworthiness"] and "2014" <= yr(r["first_airworthiness"]) <= "2019"]
    picks = ([("domestic sale (E1)", r, r["e1"]) for r in rng.sample(dom, 10)]
             + [("export (E1)", r, r["e1"]) for r in rng.sample(exp_gov, 7) + rng.sample(exp_rest, 3)]
             + [("only under E2", r, r["e2"]) for r in rng.sample(e2o, 5)]
             + [("removed by the bound", r, r["customer_cert"] or r["export_cancel"] or r["gulfstream_cancel"])
                for r in rng.sample(bnd, 5)])
    out = []
    for event, r, d in picks:
        out.append({"serial": r["serial"], "mfr_code": r["mfr_code"], "model": r["model"], "event": event,
                    "our_date": d, "first_airworthiness": r["first_airworthiness"], "bound": r["bound"],
                    "export_country": r["export_country"], "n_numbers": " ".join(sorted(regs.get((r["mfr_code"], r["serial"]), [])))})
    write_csv(ROOT / "docs/build/audit_sample.csv", list(out[0]), out)
    for i, o in enumerate(out):
        print(i + 1, o["event"], o["model"], o["serial"], o["our_date"], o["export_country"], o["n_numbers"])


if __name__ == "__main__":
    main()
