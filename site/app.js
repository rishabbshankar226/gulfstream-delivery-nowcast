/* Gulfstream delivery tracker. Every figure on the page comes from data.json at runtime. */
(function () {
  "use strict";

  var MODELS = ["ratio", "raw", "guidance", "seasonal", "last"];
  var NAME = {
    reported: "GD reported",
    ratio: "Registry estimate",
    raw: "Raw registry count",
    guidance: "Pace built from GD's outlook",
    seasonal: "Same quarter last year",
    last: "Last quarter"
  };
  var BASE = { guidance: "the pace I built from GD's outlook", seasonal: "the same quarter last year", last: "last quarter" };
  var DASH = { reported: [], ratio: [], raw: [7, 4], guidance: [10, 4, 2, 4], seasonal: [5, 4], last: [2, 3] };
  var WIDTH = { reported: 3, ratio: 2.4, raw: 1.6, guidance: 1.6, seasonal: 1.6, last: 1.8 };
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var narrow = window.matchMedia("(max-width: 760px)");
  var dark = window.matchMedia("(prefers-color-scheme: dark)");
  var charts = [];
  var data = null;

  function $(id) { return document.getElementById(id); }
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function f1(x) { return (Math.round(x * 10) / 10).toFixed(1); }
  function whole(x) { return String(Math.round(x)); }
  function usdB(x) { return (x < 0 ? "-$" : "$") + (Math.abs(x) / 1e9).toFixed(1) + "B"; }
  function usdM(x) { return (x < 0 ? "-$" : "$") + Math.round(Math.abs(x) / 1e6).toLocaleString("en-US") + "M"; }
  function pct(x, d) { return x.toFixed(d === undefined ? 1 : d) + "%"; }
  function signed(x) { return (x > 0 ? "+" : x < 0 ? "-" : "") + f1(Math.abs(x)); }
  function mean(xs) { var s = 0; xs.forEach(function (v) { s += v; }); return s / xs.length; }
  function text(el, s) { el.textContent = s; }
  function el(tag, cls, s) { var e = document.createElement(tag); if (cls) e.className = cls; if (s !== undefined) e.textContent = s; return e; }

  function etTime(iso) {
    var d = new Date(iso);
    var parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hour12: false
    }).formatToParts(d);
    var p = {};
    parts.forEach(function (x) { p[x.type] = x.value; });
    return p.year + "-" + p.month + "-" + p.day + " at " + p.hour.replace("24", "00") + ":" + p.minute + " ET";
  }

  function table(id, caption, head, rows) {
    var t = $(id);
    t.textContent = "";
    var cap = el("caption", null, caption);
    t.appendChild(cap);
    var thead = el("thead"), tr = el("tr");
    head.forEach(function (h) { var th = el("th", null, h); th.scope = "col"; tr.appendChild(th); });
    thead.appendChild(tr);
    t.appendChild(thead);
    var tb = el("tbody");
    rows.forEach(function (r) {
      var row = el("tr", r.cls || null);
      r.cells.forEach(function (c, i) {
        var cell = el(i === 0 ? "th" : "td", null, c);
        if (i === 0) { cell.scope = "row"; cell.style.fontWeight = "inherit"; cell.style.textAlign = "left"; cell.style.borderBottom = "1px solid var(--line-soft)"; }
        row.appendChild(cell);
      });
      tb.appendChild(row);
    });
    t.appendChild(tb);
  }

  /* ---------- the headline rule ---------- */
  function beats(h) {
    return ["guidance", "seasonal", "last"].filter(function (b) {
      return h.tests[b].holm_reject && h.rel_mae[b] < 1;
    });
  }

  function typicalCount() {
    var q = data.quarters, out = [];
    q.forEach(function (x, i) { if (x >= "2020Q1") out.push(data.reported.total[i]); });
    return mean(out);
  }

  function lead() {
    var h = data.metrics.holdout;
    var b = beats(h);
    var base = h.guidance.headline ? "guidance" : "seasonal";
    var s;
    var low = ["guidance", "seasonal", "last"].reduce(function (a, x) { return h.mae[x] < h.mae[a] ? x : a; }, base);
    if (b.length) {
      s = "The registry estimate beat " + b.map(function (x) { return BASE[x]; }).join(" and ") +
        ": off by " + f1(h.mae.ratio) + " jets a quarter on average, when GD delivers about " +
        whole(typicalCount()) + ", against " + f1(h.mae[b[0]]) + " for " + BASE[b[0]] + ".";
    } else {
      s = "Over " + h.n + " held-out quarters the registry estimate was off by " + f1(h.mae.ratio) +
        " jets a quarter on average, when GD delivers about " +
        whole(typicalCount()) + ", against " + f1(h.mae[base]) + " for " + BASE[base] +
        ". The difference is not statistically distinguishable.";
    }
    text($("lead"), s);
    var f = "";
    if (low !== base && h.mae[low] < h.mae.ratio) {
      f += "Simply repeating " + BASE[low] + " missed by less, " + f1(h.mae[low]) + ". ";
    }
    f += "All of this is a test on past quarters, read from a registry copy of " + data.snapshot +
      " that had months or years to fill in. Only the locked quarters test whether the registry counts deliveries in time.";
    text($("framing"), f);
  }

  /* ---------- the live quarter ---------- */
  // The newest quarter with a lock or a score, so a scored quarter stays up until the next one locks; else the newest.
  function current() {
    for (var i = data.live.length - 1; i >= 0; i--) if (data.live[i].lock || data.live[i].score) return data.live[i];
    return data.live.length ? data.live[data.live.length - 1] : null;
  }

  // A lock is public only if the repository was already public on the day its release was published.
  function lockWords(L) {
    return (data.public && data.public_since && L.lock.published_at.slice(0, 10) >= data.public_since) ?
      "public GitHub release" : "timestamped GitHub release, made while the repository was private";
  }

  function dayAfter(d) {
    return new Date(new Date(d + "T12:00:00Z").getTime() + 86400000).toISOString().slice(0, 10);
  }

  function liveCard() {
    var L = current();
    if (!L) { text($("live-status"), "No live quarter"); return; }
    var pred = L.locked || L.latest || L.build;
    var status;
    var scoredLock = !!(L.score && L.score.locked && L.lock);
    var band = scoredLock ? (L.score.inside_band ? "inside" : "outside") + " the band" : "";
    if (scoredLock) status = "Scored: missed by " + f1(L.score.ae_total) + ", " + band;
    else if (L.score) status = "Scored";
    else if (L.lock) status = "Locked " + etTime(L.lock.published_at);
    else status = "Provisional";
    text($("live-status"), L.quarter + " · " + status);
    text($("live-figure"), f1(pred.nowcast.total));
    if ($("live-unit")) text($("live-unit"), L.lock ? "deliveries, locked estimate" : "deliveries, estimated");
    var hb = data.metrics.holdout.band;
    text($("live-band"), "Band of past misses: " + f1(pred.band[0]) + " to " + f1(pred.band[1]) + " deliveries. " +
      "It held GD's count in " + hb.hits + " of " + hb.n + " held-out quarters, against a nominal 80%.");
    var facts = $("live-facts");
    facts.textContent = "";
    function fact(k, v) { facts.appendChild(el("dt", null, k)); facts.appendChild(el("dd", null, v)); }
    var latest = L.latest || pred;
    fact(L.score ? "Registrations in the quarter" : "Registrations so far",
      latest.events.large + " large-cabin, " + latest.events.mid + " mid-cabin (snapshot " + latest.snapshot + ")");
    // The window opens the day after the last quarter's fiscal end.
    fact("Quarter window", dayAfter(latest.window_start) + " to " + latest.window_end);
    if (L.guidance_pace !== null) fact("Pace I built from GD's outlook", f1(L.guidance_pace) + " deliveries" +
      (L.score && L.score.guidance_ae !== null ? " (missed by " + f1(L.score.guidance_ae) + ")" : ""));
    fact("GD's typical quarter", "about " + whole(typicalCount()) + " deliveries since 2020");
    var qi = data.quarters.indexOf(L.quarter);
    var yago = data.quarters.indexOf(String(Number(L.quarter.slice(0, 4)) - 1) + L.quarter.slice(4));
    if (yago >= 0) fact("Same quarter last year", data.reported.total[yago] + " deliveries" +
      (L.score ? " (missed by " + Math.abs(data.reported.total[yago] - L.score.reported.total) + ")" : ""));
    if (L.release_date) {
      fact(L.score ? "GD reported on" : "GD reports", L.release_date);
      if (!L.lock && L.score) fact("Lock", "none: the quarter missed its lock window");
      else if (!L.lock) {
        var eve = new Date(L.release_date + "T12:00:00Z");
        eve = new Date(eve.getTime() - 86400000).toISOString().slice(0, 10);
        fact("Locks", eve + ", the day before GD reports");
      }
    }
    if (L.score) {
      fact("GD reported", String(L.score.reported.total) + " deliveries");
      if (scoredLock) fact("Miss of the locked estimate", f1(L.score.ae_total) + " deliveries (" + Math.round(L.score.ape_pct) + "%), " + band);
    }
    var note = L.lock ? "Locked as a " + lockWords(L) + ", on " + etTime(L.lock.published_at) + "; the file's sha256 is in the release notes." :
      L.score ? "Not locked: the quarter missed its lock window, so this is the build estimate, shown beside GD's count." :
      "Provisional: the estimate locks on GitHub the day before GD reports, from the newest stored registry snapshot, and stays on this page whether it hits or misses.";
    note += " The band comes from misses measured on a finished registry file, so it may not fit a live quarter.";
    text($("live-note"), note);
  }

  /* ---------- charts ---------- */
  function baseOptions(ylabel, xlabel) {
    var grid = css("--grid"), ink = css("--ink"), muted = css("--muted");
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: reduced.matches ? false : { duration: 300 },
      interaction: { mode: "index", intersect: false },
      layout: { padding: { right: 8 } },
      plugins: {
        legend: { position: "top", align: "start", labels: { color: ink, boxWidth: 28, boxHeight: 2, usePointStyle: false, font: { family: css("--font"), size: 12 } } },
        tooltip: { backgroundColor: css("--surface"), titleColor: ink, bodyColor: ink, borderColor: css("--line"), borderWidth: 1, padding: 10, titleFont: { family: css("--font") }, bodyFont: { family: css("--font") } }
      },
      scales: {
        x: { title: { display: true, text: xlabel, color: muted, font: { family: css("--font") } }, grid: { display: false }, ticks: { color: ink, autoSkip: true, maxRotation: 0, font: { family: css("--font"), size: 11 } }, border: { color: css("--axis") } },
        y: { title: { display: true, text: ylabel, color: muted, font: { family: css("--font") } }, beginAtZero: true, grid: { color: grid }, ticks: { color: ink, font: { family: css("--font"), size: 11 } }, border: { display: false } }
      }
    };
  }

  var shade = {
    id: "shade",
    beforeDatasetsDraw: function (chart, args, opts) {
      if (!opts || opts.from === undefined) return;
      var x = chart.scales.x, a = chart.chartArea, ctx = chart.ctx;
      var x0 = x.getPixelForValue(opts.from) - (x.getPixelForValue(1) - x.getPixelForValue(0)) / 2;
      var x1 = x.getPixelForValue(opts.to) + (x.getPixelForValue(1) - x.getPixelForValue(0)) / 2;
      ctx.save();
      ctx.fillStyle = css("--wash");
      ctx.fillRect(x0, a.top, x1 - x0, a.bottom - a.top);
      ctx.fillStyle = css("--muted");
      ctx.font = "12px " + css("--font");
      ctx.fillText(opts.label, x0 + 6, a.bottom - 8);
      ctx.restore();
    }
  };

  function trackChart() {
    var q = data.quarters, rep = data.reported.total;
    var sets = [{
      label: NAME.reported, data: rep, borderColor: css("--s-reported"), backgroundColor: css("--s-reported"),
      borderWidth: WIDTH.reported, pointRadius: 0, pointHitRadius: 8, tension: 0, order: 0
    }];
    MODELS.forEach(function (m, i) {
      sets.push({
        label: NAME[m], data: data.backtest[m], borderColor: css("--s-" + m), backgroundColor: css("--s-" + m),
        borderWidth: WIDTH[m], borderDash: DASH[m], pointRadius: 0, pointHitRadius: 8, tension: 0, spanGaps: false, order: i + 1,
        hidden: narrow.matches && (m === "raw" || m === "last")
      });
    });
    var opts = baseOptions("Aircraft delivered per quarter", "Fiscal quarter");
    opts.plugins.shade = { from: q.indexOf("2017Q1"), to: q.indexOf("2019Q4"), label: "Quarters that set the rule" };
    opts.plugins.tooltip.callbacks = {
      label: function (ctx) {
        var v = ctx.parsed.y;
        if (v === null || v === undefined) return null;
        var line = ctx.dataset.label + ": " + (ctx.datasetIndex === 0 ? whole(v) : f1(v));
        if (ctx.datasetIndex > 0) line += " (miss " + signed(v - rep[ctx.dataIndex]) + ")";
        return line;
      }
    };
    opts.scales.x.ticks.callback = function (v, i) { var l = q[i]; return l.slice(4) === "Q1" ? l.slice(0, 4) : ""; };
    opts.scales.x.ticks.autoSkip = false;
    charts.push(new Chart($("c-track"), { type: "line", data: { labels: q, datasets: sets }, options: opts, plugins: [shade] }));
    $("c-track").setAttribute("aria-label", "Line chart of GD's reported Gulfstream deliveries by quarter from " + q[0] +
      " to " + q[q.length - 1] + " against five estimates. The registry estimate missed by " + f1(data.metrics.holdout.mae.ratio) +
      " deliveries a quarter on average over the quarters held out for the test. The table below lists every value.");
  }

  function trackTable() {
    var q = data.quarters, rows = [];
    q.forEach(function (x, i) {
      var cells = [x, whole(data.reported.total[i])];
      MODELS.forEach(function (m) { var v = data.backtest[m][i]; cells.push(v === null ? "" : f1(v)); });
      rows.push({ cells: cells });
    });
    table("t-track", "Deliveries by quarter: GD reported and the five estimates",
      ["Quarter", "GD reported"].concat(MODELS.map(function (m) { return NAME[m]; })), rows);
  }

  function tiles() {
    var h = data.metrics.holdout, b = beats(h), ul = $("tiles");
    ul.textContent = "";
    var low = MODELS.reduce(function (a, m) { return h.mae[m] < h.mae[a] ? m : a; }, MODELS[0]);
    MODELS.forEach(function (m) {
      var li = el("li", b.length && m === low ? "best" : null);
      li.appendChild(el("span", "t-name", NAME[m]));
      li.appendChild(el("span", "t-fig", f1(h.mae[m])));
      var d = h.mae[m] - h.mae.ratio;
      li.appendChild(el("span", "t-cmp", m === "ratio" ? "this project's estimate" :
        f1(Math.abs(d)) + (d < 0 ? " less than" : " more than") + " the registry estimate"));
      ul.appendChild(li);
    });
  }

  function days(a, b) {
    var out = [], d = new Date(a + "T12:00:00Z"), end = new Date(b + "T12:00:00Z");
    while (d <= end) { out.push(d.toISOString().slice(0, 10)); d = new Date(d.getTime() + 86400000); }
    return out;
  }

  function pathChart() {
    var L = current();
    var box = $("c-path").parentNode;
    if (!L || !data.path || !data.path[L.quarter]) { box.hidden = true; return; }
    var rows = data.path[L.quarter];
    box.classList.toggle("tall", rows.length >= 3);
    text($("path-sub"), (rows.length === 1 ? "One snapshot so far (" + rows[0].date + ")." :
      rows.length + (L.score ? " snapshots, " : " snapshots so far, ") + rows[0].date + " to " + rows[rows.length - 1].date + ".") +
      " A point posts with each day's registry snapshot, with the band of past misses around it" +
      (L.lock ? "; the diamond marks the locked estimate." : L.score ? "; the quarter missed its lock window." :
        "; the estimate locks the day before GD reports."));
    var pred = L.locked || L.latest || L.build;
    var below = pred.nowcast.total - pred.band[0], above = pred.band[1] - pred.nowcast.total;
    var last = rows[rows.length - 1].date;
    var labels = days(rows[0].date, L.release_date && L.release_date > last ? L.release_date : last);
    var at = {};
    rows.forEach(function (r) { at[r.date] = r; });
    var tot = labels.map(function (d) { return at[d] ? at[d].nowcast_total : null; });
    var sets = [
      { type: "bar", label: "Band of past misses", data: labels.map(function (d, i) { return tot[i] === null ? null : [tot[i] - below, tot[i] + above]; }),
        backgroundColor: css("--band"), borderWidth: 0, barPercentage: 1, categoryPercentage: 0.9, order: 3 },
      { type: "line", label: "Estimate", data: tot, borderColor: css("--s-ratio"), backgroundColor: css("--s-ratio"), borderWidth: 2.4,
        pointRadius: 4, pointHoverRadius: 6, tension: 0, spanGaps: true, order: 1 }
    ];
    if (L.guidance_pace !== null) {
      sets.push({ type: "line", label: "Pace built from GD's outlook", data: labels.map(function () { return L.guidance_pace; }), borderColor: css("--s-guidance"),
        borderDash: DASH.guidance, borderWidth: 1.6, pointRadius: 0, order: 2 });
    }
    if (L.locked && L.lock) {
      sets.push({ type: "line", label: "Locked estimate", data: labels.map(function (d) { return d === L.locked.snapshot ? L.locked.nowcast.total : null; }),
        borderColor: css("--ink"), backgroundColor: css("--ink"), pointStyle: "rectRot", pointRadius: 8, showLine: false, order: 0 });
    }
    if (L.score) {
      sets.push({ type: "line", label: "GD reported", data: labels.map(function () { return L.score.reported.total; }), borderColor: css("--s-reported"),
        borderWidth: 3, pointRadius: 0, order: 0 });
    }
    var opts = baseOptions("Estimated deliveries", "Registry snapshot date");
    opts.plugins.tooltip.filter = function (item) { return item.raw !== null; };
    opts.plugins.tooltip.callbacks = { label: function (ctx) {
      var v = ctx.raw;
      return Array.isArray(v) ? "Band of past misses: " + f1(v[0]) + " to " + f1(v[1]) : ctx.dataset.label + ": " + f1(v);
    } };
    opts.scales.x.ticks.autoSkip = true;
    opts.scales.x.ticks.maxTicksLimit = 6;
    var top = Math.max.apply(null, tot.filter(function (t) { return t !== null; }).map(function (t) { return t + above; }).concat(L.guidance_pace || 0));
    opts.scales.y.suggestedMax = Math.ceil(top * 1.15);
    charts.push(new Chart($("c-path"), { data: { labels: labels, datasets: sets }, options: opts }));
    var lastTot = rows[rows.length - 1].nowcast_total;
    $("c-path").setAttribute("aria-label", "Chart of the " + L.quarter + " estimate by registry snapshot date: latest " + f1(lastTot) +
      " deliveries with a band of past misses from " + f1(lastTot - below) + " to " + f1(lastTot + above) +
      (L.guidance_pace !== null ? ", against the pace I built from GD's outlook, " + f1(L.guidance_pace) : "") + ". The table below lists every snapshot.");
    table("t-path", "The " + L.quarter + " estimate by snapshot date", ["Snapshot", "Large-cabin registrations", "Mid-cabin registrations", "Estimate", "Band low", "Band high"],
      rows.map(function (r) {
        return { cells: [r.date, String(r.events_large), String(r.events_mid), f1(r.nowcast_total), f1(r.nowcast_total - below), f1(r.nowcast_total + above)] };
      }));
  }

  function pipeChart() {
    var raw = data.pipeline, p = {};
    Object.keys(raw).forEach(function (n) {
      var m = n.match(/G\d{3}/), k = m ? m[0] : (n === "550" ? "Other" : n === "GVI" ? "G650" : n);
      p[k] = (p[k] || 0) + raw[n];
    });
    var names = Object.keys(p).sort(function (a, b) { return p[b] - p[a] || (a < b ? -1 : 1); });
    var all = names.reduce(function (s, n) { return s + p[n]; }, 0);
    text($("pipe-sub"), "Jets registered to Gulfstream itself with no delivery event yet, at the " + data.pipeline_snapshot +
      " snapshot: " + all + " in all. They include aircraft in flight test, in completion and taken back for resale, " +
      "and registrations Gulfstream holds for jets with no airworthiness date yet, so this is not a count of jets awaiting delivery. " +
      "It leaves out the G700s the FAA files under a type code my scope rule does not keep.");
    $("pipe-box").style.height = Math.max(220, names.length * 30 + 90) + "px";
    var opts = baseOptions("Aircraft", "Aircraft on Gulfstream's own registration");
    opts.indexAxis = "y";
    opts.plugins.legend.display = false;
    opts.interaction = { mode: "nearest", intersect: true, axis: "y" };
    opts.scales.x.grid = { color: css("--grid") };
    opts.scales.x.beginAtZero = true;
    opts.scales.y.title.display = false;
    opts.scales.y.grid = { display: false };
    opts.scales.y.beginAtZero = false;
    opts.plugins.tooltip.callbacks = { label: function (ctx) { return ctx.parsed.x + " aircraft"; } };
    charts.push(new Chart($("c-pipe"), {
      type: "bar",
      data: { labels: names, datasets: [{ label: "Aircraft", data: names.map(function (n) { return p[n]; }), backgroundColor: css("--s-ratio"), borderRadius: 2, barPercentage: 0.7 }] },
      options: opts
    }));
    var total = all;
    $("c-pipe").setAttribute("aria-label", "Bar chart of " + total + " jets on Gulfstream's own registration with no delivery event, by model, at the " + data.pipeline_snapshot + " snapshot.");
    table("t-pipe", "Jets on Gulfstream's own registration, " + data.pipeline_snapshot, ["Model", "Aircraft"],
      names.map(function (n) { return { cells: [n, String(p[n])] }; }));
  }

  /* ---------- tests ---------- */
  function tests() {
    var h = data.metrics.holdout, ul = $("tests");
    ul.textContent = "";
    ["guidance", "seasonal", "last"].forEach(function (b) {
      var t = h.tests[b], ac = h.autocorr_lag1[b];
      var s = "Against " + BASE[b] + ", the registry estimate was closer in " + t.wins + " of " + h.n +
        " quarters and further off in " + t.losses + (t.ties ? " (" + t.ties + " ties)" : "") +
        ". Its average miss was " + f1(h.mae.ratio) + " against " + f1(h.mae[b]) + ". A one-sided sign test gives p = " +
        t.p_one_sided.toFixed(3) + "; after Holm's correction for three comparisons it " +
        (t.holm_reject ? "is significant." : "is not significant.");
      if (ac !== null && ac > 0) s += " The quarter-to-quarter differences are positively correlated (" + ac.toFixed(2) + "), which makes the sign test less reliable.";
      ul.appendChild(el("li", null, s));
    });
    var g = h.guidance;
    ul.appendChild(el("li", null, "GD stated a numeric delivery outlook covering " + g.sourced + " of the " + h.n +
      " test quarters; the other " + g.fallback_quarters.length + " (" + g.fallback_quarters.join(", ") +
      ") fall back to the same quarter last year. The guidance pace is my construction from GD's full-year outlook, not a figure GD publishes; the README gives two other readings of GD's calls and what each does to this comparison."));
    var band = h.band;
    ul.appendChild(el("li", null, "The band of past misses held GD's count in " + band.hits + " of " + band.n +
      " test quarters (" + pct(band.coverage_pct) + ", against a nominal 80%; 95% interval " + pct(band.cp95_pct[0]) + " to " + pct(band.cp95_pct[1]) + ")."));
    var cr = h.coverage_ratio;
    var recent = ["2025Q4", "2026Q1", "2026Q2"].map(function (q) { return cr.by_quarter[q]; });
    var below = recent.every(function (x) { return typeof x === "number" && x < cr.mean; });
    ul.appendChild(el("li", null, (cr.flags.length ?
      "Recent quarters where the registry counted unusually few jets per GD delivery: " + cr.flags.join(", ") + "." :
      "The preregistered check looks for quarters from 2025Q3 to 2026Q2 where the registry counted unusually few jets per GD delivery; none is flagged.") +
      (below ? " The drift runs the other way: GD delivered " + recent.map(function (x) { return x.toFixed(2); }).join(", ") +
        " jets per registry event in the last three held-out quarters, against an average of " + cr.mean.toFixed(2) +
        ", so the registry is counting more registrations per delivery than usual." : "")));
    var tr = h.truncation_mae;
    table("t-trunc", "Average miss when each test quarter's registrations are cut early, against " + f1(h.mae.guidance) +
      " for the pace I built from GD's outlook on the same quarters", ["Days cut before the quarter ends", "Average miss, deliveries"],
      ["0", "30", "60", "90"].map(function (d) { return { cells: [d, f1(tr[d])] }; }));
  }

  /* ---------- estimates ---------- */
  function estimates() {
    var e = data.estimates, S = e.segments;
    var rows = [];
    var SEGS = ["Aerospace", "Marine Systems", "Combat Systems", "Technologies"];
    // What GD reported for the target quarter, once it has: the estimates were made before the release.
    var R = (data.reported_segments || {})[e.target] || null;
    function row(name, actual, est, rep, cls) {
      rows.push({ cls: cls, cells: R ?
        [name, usdB(actual), usdB(est), usdB(rep), usdM(est - rep), pct((est - rep) / rep * 100)] :
        [name, usdB(actual), usdB(est), usdM(est - actual), pct((est - actual) / actual * 100)] });
    }
    function q3(s) { return S[s].drift_usd * S[s].ttm_revenue_prior_usd / S[s].ttm_revenue_usd; }
    function rep(s) { return R ? R[s].revenue_usd : null; }
    row("Aerospace, delivery estimate", q3("Aerospace"), e.aerospace_from_nowcast_usd, rep("Aerospace"), "emph");
    row("Aerospace, growth rule", q3("Aerospace"), S.Aerospace.drift_usd, rep("Aerospace"));
    ["Marine Systems", "Combat Systems", "Technologies"].forEach(function (s) { row(s, q3(s), S[s].drift_usd, rep(s)); });
    var a = SEGS.reduce(function (t, s) { return t + q3(s); }, 0);
    row("Total, four segments", a, e.revenue_total_usd, R ? SEGS.reduce(function (t, s) { return t + rep(s); }, 0) : null, "emph");
    if (R) table("t-est", e.target + " revenue by segment: the estimates made before the release, and what GD reported",
      ["Segment", "Year-ago quarter", "Estimate", "GD reported", "Estimate less reported", "Miss, %"], rows);
    else table("t-est", e.target + " revenue by segment against the year-ago quarter", ["Segment", "Year-ago quarter", "Estimate", "Change", "Change, %"], rows);
    var yq = String(Number(e.target.slice(0, 4)) - 1) + e.target.slice(4);
    var yi = data.quarters.indexOf(yq);
    var below = yi < 0 || e.nowcast_total < data.reported.total[yi];
    var why = R ?
      "Before GD reported, the delivery estimate of " + f1(e.nowcast_total) + (below ? " sat below the " : " sat above the ") +
      (yi >= 0 ? data.reported.total[yi] + " " : "") + "deliveries of " + yq + ", and each delivery carried about " +
      usdM(e.revenue_per_delivery_usd) + " of Aerospace revenue, so the delivery-based figure " + (below ? "fell" : "rose") +
      ". GD reported " + usdB(R.Aerospace.revenue_usd) + " of Aerospace revenue. That " :
      "The delivery estimate of " + f1(e.nowcast_total) + (below ? " sits below the " : " sits above the ") +
      (yi >= 0 ? data.reported.total[yi] + " " : "") + "deliveries of " + yq + ", and each delivery carries about " +
      usdM(e.revenue_per_delivery_usd) + " of Aerospace revenue, so the delivery-based figure " + (below ? "falls" : "rises") +
      ". That ";
    text($("est-why"), why + usdM(e.revenue_per_delivery_usd) + " includes services and Jet Aviation revenue, which a delivery " +
      "count does not measure. The growth row instead scales " +
      yq + "'s Aerospace revenue by the last four quarters' growth.");
    var ya = q3("Aerospace");
    table("t-sens", "Made before the release: Aerospace revenue for each delivery count, at " + usdM(e.revenue_per_delivery_usd) + " a delivery, against " +
      usdB(ya) + " in the year-ago quarter", ["Deliveries", "Aerospace revenue", "Change on the year-ago quarter"],
      e.sensitivity.map(function (s) {
        return { cls: s.deliveries_change === 0 ? "emph" : null, cells: [f1(s.deliveries), usdB(s.aerospace_revenue_usd), usdM(s.aerospace_revenue_usd - ya)] };
      }));
  }

  /* ---------- start ---------- */
  function draw() {
    charts.forEach(function (c) { c.destroy(); });
    charts = [];
    Chart.defaults.font.family = css("--font");
    Chart.defaults.color = css("--ink");
    trackChart();
    pathChart();
    pipeChart();
  }

  function render() {
    lead();
    liveCard();
    tiles();
    trackTable();
    tests();
    estimates();
    draw();
    document.documentElement.classList.add("ready");
  }

  function fail(err) {
    var e = $("error");
    e.hidden = false;
    e.textContent = "The figures could not load. Reload the page, or read the same results in the ";
    var a = document.createElement("a");
    a.href = "https://github.com/rishabbshankar226/gulfstream-delivery-nowcast#results";
    a.textContent = "README on GitHub";
    e.appendChild(a);
    e.appendChild(document.createTextNode(". (" + err + ")"));
    text($("lead"), "The figures could not load.");
  }

  fetch("data.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function (d) { data = d; render(); })
    .catch(function (err) { fail(err.message || String(err)); });

  if (dark.addEventListener) dark.addEventListener("change", function () { if (data) draw(); });
})();
