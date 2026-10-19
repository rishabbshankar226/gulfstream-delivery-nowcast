"""The live nowcast (§3.5), the lock and the score (§3.6).

Every function that depends on the time takes `now` (an aware UTC datetime) so tests and the
lock rehearsal can fix the clock."""
import csv
import datetime as dt
import gzip
import io
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from . import events, faa, model, sec, stats
from .fiscal import LIVE_FIRST, Calendar, qidx, shift
from .files import csv_text, read_csv, read_json, sha256, write_json, write_text
from .gitops import GitError, Ops

ET = ZoneInfo("America/New_York")
PATH_COLS = ["date", "events_large", "events_mid", "trailing_registry_large", "trailing_registry_mid",
             "nowcast_large", "nowcast_mid", "nowcast_total"]
CABINS = ("large", "mid")
LOCK_HOUR_ET = 19
LOCK_WINDOW_DAYS = 7


# ---------- time ----------
def utcnow():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def parse_now(s=None):
    if s is None or isinstance(s, dt.datetime):
        return (s or utcnow()).astimezone(dt.timezone.utc)
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)


def stamp(now):
    return now.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def et_date(now):
    return now.astimezone(ET).date()


# ---------- files ----------
def live_dir(root):
    return Path(root) / "results/live"


def config(root):
    return read_json(Path(root) / "config/calendar.json")


def scores(root):
    out = {}
    for p in sorted(live_dir(root).glob("*_score.json")):
        out[p.name.split("_")[0]] = read_json(p)
    return out


def reported_history(root):
    """Reported counts: §3.2's series, then each scored live quarter."""
    Y = model.load_reported(root)
    for q, s in scores(root).items():
        Y[q] = {c: int(s["reported"][c]) for c in ("large", "mid", "total")}
    return Y


def live_quarter(root):
    """The earliest quarter from 2026Q3 that is not scored and whose four lags are all reported."""
    Y, done = reported_history(root), scores(root)
    q = LIVE_FIRST
    while q in done:
        q = shift(q, 1)
    return q if all(shift(q, -k) in Y for k in range(1, 5)) else None


def unscored_quarters(root):
    q = live_quarter(root)
    return [q] if q else []


def daily_dir(root):
    return Path(root) / "data/snapshots/daily"


def table_path(root, date):
    return daily_dir(root) / f"{date}.serials.csv.gz"


def table_dates(root):
    return sorted(p.name.split(".")[0] for p in daily_dir(root).glob("*.serials.csv.gz"))


def write_table(root, date, rows):
    p = table_path(root, date)
    p.parent.mkdir(parents=True, exist_ok=True)
    gz = events.serials_gz(rows)
    if not p.exists() or p.read_bytes() != gz:
        p.write_bytes(gz)


def read_table(root, date):
    text = gzip.decompress(table_path(root, date).read_bytes()).decode("utf-8")
    return events.read_serials_rows(csv.DictReader(io.StringIO(text)))


def definition(root):
    return read_json(Path(root) / "results/metrics.json")["definition"]


def band_errors(root):
    """Every signed error to date: design and holdout from metrics.json, then each scored live
    quarter's locked error, in quarter order."""
    errs = list(read_json(Path(root) / "results/metrics.json")["band_errors"])
    for q, s in sorted(scores(root).items(), key=lambda kv: qidx(kv[0])):
        if s.get("locked") and s.get("nowcast"):
            errs.append(s["nowcast"]["total"] - s["reported"]["total"])
    return errs


# ---------- the nowcast ----------
def predict(root, q, rows, snapshot, now):
    cal = Calendar.load(root)
    lo, hi = cal.window(q)
    if lo is None or hi is None:
        raise ValueError(f"{q} has no fiscal end: add it under fiscal_ends in config/calendar.json")
    chosen = definition(root)
    Y = reported_history(root)
    lags = [shift(q, -k) for k in range(1, 5)]
    ev = {c: events.count(rows, chosen, c, lo, hi) for c in CABINS}
    n_lags = {c: [events.count(rows, chosen, c, *cal.window(x)) for x in lags] for c in CABINS}
    y_lags = {c: [Y[x][c] for x in lags] for c in CABINS}
    now_c = {c: model.ratio(ev[c], n_lags[c], y_lags[c]) for c in CABINS}
    total = now_c["large"] + now_c["mid"]
    errs = band_errors(root)
    band = [total - stats.nearest_rank(errs, 0.9), total - stats.nearest_rank(errs, 0.1)]
    return {"quarter": q, "window_start": lo, "window_end": hi, "snapshot": snapshot, "definition": chosen,
            "events": ev,
            "trailing": {"reported": {c: sum(y_lags[c]) for c in CABINS},
                         "registry": {c: sum(n_lags[c]) for c in CABINS}},
            "nowcast": {"large": now_c["large"], "mid": now_c["mid"], "total": total},
            "band": band, "made_utc": stamp(now)}


def path_row(pred):
    return {"date": pred["snapshot"], "events_large": pred["events"]["large"], "events_mid": pred["events"]["mid"],
            "trailing_registry_large": pred["trailing"]["registry"]["large"],
            "trailing_registry_mid": pred["trailing"]["registry"]["mid"],
            "nowcast_large": pred["nowcast"]["large"], "nowcast_mid": pred["nowcast"]["mid"],
            "nowcast_total": pred["nowcast"]["total"]}


def update_path(root, q, pred):
    p = live_dir(root) / f"{q}_path.csv"
    rows = [r for r in (read_csv(p) if p.exists() else []) if r["date"] != pred["snapshot"]]
    rows.append({k: v for k, v in path_row(pred).items()})
    rows.sort(key=lambda r: r["date"])
    write_text(p, csv_text(PATH_COLS, rows))


def same_but_time(a, b):
    return {k: v for k, v in a.items() if k != "made_utc"} == {k: v for k, v in b.items() if k != "made_utc"}


def update_latest(root, now, log=print):
    """Rewrite <Q>_latest.json and its path row from the newest daily airframe table."""
    q = live_quarter(root)
    dates = table_dates(root)
    if not q or not dates:
        log("no live quarter or no daily airframe table")
        return None
    snap = dates[-1]
    pred = predict(root, q, read_table(root, snap), snap, now)
    p = live_dir(root) / f"{q}_latest.json"
    if not (p.exists() and same_but_time(read_json(p), pred)):
        write_json(p, pred)
    update_path(root, q, pred)
    log(f"{q} estimate from {snap}: {pred['nowcast']['total']:.1f} "
        f"(band {pred['band'][0]:.1f} to {pred['band'][1]:.1f})")
    return pred


def in_lock_window(root, date):
    """True when a snapshot date falls within seven days before an unscored quarter's release date."""
    rel = config(root).get("releases", {})
    d = dt.date.fromisoformat(date)
    for q in unscored_quarters(root):
        r = rel.get(q)
        if r and dt.date.fromisoformat(r) - dt.timedelta(days=LOCK_WINDOW_DAYS) <= d < dt.date.fromisoformat(r):
            return True
    return False


def ingest(root, date, log=print):
    """From a downloaded zip: the daily airframe table, and the full subset inside a lock window."""
    z = faa.zip_path(root, date)
    texts = faa.zip_texts(z)
    sub = faa.subset(texts)
    write_table(root, date, events.airframes(sub))
    if in_lock_window(root, date):
        faa.store_subset(root, date, sub, z)
        log(f"stored the full subset for {date} (lock window)")


def run_snapshot(now=None, offline=False, root="."):
    now = parse_now(now)
    if offline:
        print("offline: no download")
        return 0
    date = faa.download(root, now)
    if date:
        ingest(root, date)
    return 0


def run_nowcast(now=None, offline=False, root="."):
    update_latest(root, parse_now(now))
    return 0


def write_build(root=".", now=None):
    """results/live/2026Q3_build.json from the backtest snapshot, once."""
    p = live_dir(root) / f"{LIVE_FIRST}_build.json"
    if p.exists():
        print(f"{p} exists; never rewritten")
        return read_json(p)
    bt = faa.manifest(root)["backtest"]
    rows = events.airframes(faa.read_subset(root, bt))
    write_table(root, bt, rows)
    pred = predict(root, LIVE_FIRST, rows, bt, parse_now(now))
    write_json(p, pred)
    return pred


# ---------- the lock ----------
def lock_due(now, release_date, newest_snapshot):
    """On the release date's eve (ET), with a snapshot dated the eve or at 19:00 ET or later."""
    eve = dt.date.fromisoformat(release_date) - dt.timedelta(days=1)
    t = now.astimezone(ET)
    if t.date() != eve:
        return False
    return newest_snapshot == eve.isoformat() or t.hour >= LOCK_HOUR_ET


def before_release(now, release_date):
    return now.astimezone(ET).date() < dt.date.fromisoformat(release_date)


def newest_stored(root):
    snaps = sorted(faa.manifest(root)["snapshots"])
    return snaps[-1] if snaps else None


def newest_snapshot(root):
    dates = table_dates(root)
    return dates[-1] if dates else None


def prediction_path(root, q):
    return Path(root) / "predictions" / f"{q}.json"


def lock_json_path(root, q):
    return live_dir(root) / f"{q}_lock.json"


def write_lock_json(root, q, ops):
    tag = f"lock-{q}"
    ops.fetch_tag(tag)
    info = ops.release_view(tag)
    body = prediction_path(root, q).read_bytes()
    obj = {"tag": info["tagName"], "published_at": info["publishedAt"], "sha256": sha256(body),
           "commit": ops.tag_commit(tag)}
    write_json(lock_json_path(root, q), obj)
    return obj


def push_with_merge(ops, log=print, on_conflict=None):
    """Pull, then push; on a rejected push pull again. Conflicts go to on_conflict(paths)."""
    for _ in range(3):
        conflicted = ops.pull()
        if conflicted:
            if on_conflict is None or not on_conflict(conflicted):
                ops.abort_merge()
                raise GitError(f"merge conflict in {conflicted}; resolve by hand")
        if ops.push():
            return True
    return False


def run_lock(now=None, offline=False, root=".", ops=None, log=print, before_prediction=None):
    """Lock the live quarter on its release date's eve (§3.6). Returns 0, or 1 when the lock failed."""
    now = parse_now(now)
    ops = ops or Ops(root, log)
    q = live_quarter(root)
    rel = config(root).get("releases", {}).get(q) if q else None
    if not q or not rel:
        log(f"no release date for {q}; nothing to lock")
        return 0
    tag = f"lock-{q}"
    pred_p, lock_p = prediction_path(root, q), lock_json_path(root, q)
    if pred_p.exists() and not lock_p.exists() and ops.release_view(tag):
        log(f"{tag} exists without {lock_p.name}: writing it from the release")
        write_lock_json(root, q, ops)
        ops.commit([lock_p], f"Record the {q} lock")
        push_with_merge(ops, log)
        return 0
    if lock_p.exists():
        return 0
    if not lock_due(now, rel, newest_snapshot(root)):
        if not before_release(now, rel) and not pred_p.exists():
            log(f"{q} missed its lock window (release {rel}); no late lock")
        return 0
    for attempt in range(1, 4):
        ops.pull()
        if ops.release_view(tag):
            if not lock_p.exists():
                write_lock_json(root, q, ops)
                ops.commit([lock_p], f"Record the {q} lock")
                push_with_merge(ops, log)
            log(f"{tag} already exists; one lock per quarter")
            return 0
        if not before_release(now, rel):
            log("past 00:00 ET on the release date; no late lock")
            return 1
        if before_prediction:
            before_prediction()
        if ops.ahead():
            log("daily outputs are not pushed yet; retrying")
            if not push_with_merge(ops, log):
                continue
        if ops.tracked(pred_p):
            # Committed and pushed by an earlier attempt that failed before the release: never rewrite it.
            target = ops.first_commit(pred_p)
        else:
            snap = newest_stored(root)
            if snap is None or snap >= rel:
                log(f"no stored subset dated before {rel}")
                return 1
            rows = events.airframes(faa.read_subset(root, snap))
            pred = predict(root, q, rows, snap, now)
            write_json(pred_p, pred)
            target = ops.commit_only(pred_p, f"Lock the {q} nowcast")
            if not ops.push():
                log(f"lock push rejected (attempt {attempt}); resetting to upstream")
                ops.reset_to_upstream()
                continue
        digest = sha256(pred_p.read_bytes())
        ops.release_create(tag, target, f"Locked nowcast {q}", f"sha256 {digest}")
        obj = write_lock_json(root, q, ops)
        ops.commit([lock_p], f"Record the {q} lock")
        push_with_merge(ops, log)
        published = parse_now(obj["published_at"])
        if not before_release(published, rel):
            log(f"WARNING: {tag} published at {obj['published_at']}, on or after the release date")
        public = config(root).get("public")
        log(f"Locked {q} as a {'public lock' if public else 'timestamped GitHub release'}: sha256 `{digest}`")
        log("Post this sha256 somewhere public (or publish the repository) before midnight ET, "
            "then set \"public\": true in config/calendar.json.")
        return 0
    log(f"{q}: three lock attempts failed")
    return 1


# ---------- the score ----------
def score_quarter(root, q, d, accn):
    """The score object for quarter q from the release's parsed counts d."""
    cal = Calendar.load(root)
    rep = {"large": d["large"], "mid": d["mid"], "total": d["total"]}
    lock_p, pred_p = lock_json_path(root, q), prediction_path(root, q)
    locked = lock_p.exists() and pred_p.exists()
    out = {"quarter": q, "reported": rep, "accn": accn, "locked": locked, "nowcast": None, "ae_total": None,
           "ape_pct": None, "inside_band": None}
    if locked:
        pred = read_json(pred_p)
        out["nowcast"] = dict(pred["nowcast"])
        out["ae_total"] = abs(pred["nowcast"]["total"] - rep["total"])
        out["ape_pct"] = out["ae_total"] / rep["total"] * 100
        out["inside_band"] = pred["band"][0] <= rep["total"] <= pred["band"][1]
    pace = model.guidance_pace(q, reported_history(root), model.load_guidance(root), cal)
    out["guidance_pace"] = pace["total"] if pace else None
    out["guidance_ae"] = abs(pace["total"] - rep["total"]) if pace else None
    return out


def run_score(now=None, offline=False, root=".", log=print):
    now = parse_now(now)
    q = live_quarter(root)
    if not q:
        return 0
    rel = config(root).get("releases", {}).get(q)
    end = Calendar.load(root).end(q)
    if not end or not rel or et_date(now) < dt.date.fromisoformat(rel):
        return 0
    c = sec.Client(root, network=not offline)
    try:
        f = sec.results_8k(c.filings(refresh=not offline), end)
        if f is None:
            log(f"{q}: results 8-K not filed yet")
            return 0
        name, body = c.exhibit_991(f["accn"])
    except sec.SECUnavailable as e:
        log(f"{q}: SEC not read ({e})")
        return 0
    finally:
        c.save_manifest()
    d = sec.parse_deliveries(sec.plain(body))
    s = score_quarter(root, q, d, f["accn"])
    write_json(live_dir(root) / f"{q}_score.json", s)
    log(f"scored {q}: GD reported {d['total']}" + (f", locked {s['nowcast']['total']:.1f}" if s["locked"] else ""))
    return 0
