// Benzo Volume Profile — Settings: Overlay ON (main chart), Precision = symbol's.
// Week / Day volume profiles (or both at once), HVN / LVN zones and an anchored VWAP with three σ bands, all built from
// one 1-minute series fetched independently of the chart, so every timeframe draws the same.

const RES_MS = { '1m': 60000, '5m': 300000, '15m': 900000, '30m': 1800000, '1h': 3600000 };
const DAY_MS = 86400000;
const HOUR_MS_ = 3600000;
const ANCHOR_SPAN_MIN = { '1h': 60, '4h': 240, '1D': 1440, '1W': 10080, '1M': 44640 };
const MAX_HISTORY_BARS = 120000;   // the platform allows 200k lower-timeframe bars per script
const TRANSPARENT = 'rgba(0, 0, 0, 0)';
// Row transparency (Pine 0..100) runs from G_EDGE (lowest volume) to G_PEAK (POC).
const G_PEAK = 3;
const G_EDGE = 68;

function parseRgb(c, fallback) {
  const s = typeof c === 'string' ? c.trim() : '';
  if (s[0] === '#') {
    let h = s.slice(1);
    if (h.length === 3 || h.length === 4) h = h.split('').map((x) => x + x).join('');
    if (h.length === 6 || h.length === 8) {
      const v = parseInt(h.slice(0, 6), 16);
      if (Number.isFinite(v)) return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
    }
  }
  const m = /rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)/i.exec(s);
  if (m) return [+m[1], +m[2], +m[3]];
  return fallback;
}

// Pine color.new(c, transp): keeps the RGB, replaces the transparency.
function rgba(rgb, alpha) {
  return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${alpha})`;
}

// Value area grown outward from the POC one row at a time (higher side wins ties).
function valueAreaOf(vr, valueArea) {
  const rows = vr.length;
  let pIdx = 0;
  let total = 0;
  for (let r = 0; r < rows; r++) {
    if (vr[r] > vr[pIdx]) pIdx = r;
    total += vr[r];
  }
  const target = total * valueArea / 100;
  let vaVol = vr[pIdx];
  let up = pIdx;
  let dn = pIdx;
  while (vaVol < target && (up < rows - 1 || dn > 0)) {
    const uV = up < rows - 1 ? vr[up + 1] : -1;
    const dV = dn > 0 ? vr[dn - 1] : -1;
    if (uV >= dV) { up += 1; vaVol += uV; } else { dn -= 1; vaVol += dV; }
  }
  return { pIdx, up, dn };
}

// Profile of base bars [a, b), drawn over chart bars from..to.
function buildProfile(B, a, b, from, to, o) {
  let top = -Infinity;
  let bot = Infinity;
  for (let k = a; k < b; k++) {
    if (B.h[k] > top) top = B.h[k];
    if (B.l[k] < bot) bot = B.l[k];
  }
  if (!Number.isFinite(top) || !Number.isFinite(bot)) return null;

  // Spread each bar's volume evenly over the rows its high-low range touches.
  const rows = o.rows;
  const rh = (top - bot) / rows;
  const vr = new Float64Array(rows);
  const dr = new Float64Array(rows);
  if (rh > 0) {
    for (let k = a; k < b; k++) {
      const v = B.v[k];
      if (!Number.isFinite(v)) continue;
      // Clamp into [0, rows-1]: a bar touching the session top maps to bin == rows.
      const rB = Math.min(rows - 1, Math.max(0, Math.floor((B.l[k] - bot) / rh)));
      const rT = Math.min(rows - 1, Math.max(0, Math.floor((B.h[k] - bot) / rh)));
      const ve = v / (rT - rB + 1);
      const isDown = B.c[k] < B.o[k];
      for (let r = rB; r <= rT; r++) {
        vr[r] += ve;
        if (isDown) dr[r] += ve;
      }
    }
  }

  const { pIdx, up, dn } = valueAreaOf(vr, o.valueArea);
  const maxV = vr[pIdx];
  const nBars = to - from + 1;
  const wMax = Math.min(o.maxWidthBar, Math.max(3, Math.trunc(nBars * o.widthPct)));
  const rowList = [];
  if (maxV > 0 && rh > 0) {
    for (let r = 0; r < rows; r++) {
      const tv = vr[r];
      if (!(tv > 0)) continue;
      const w = Math.max(1, Math.trunc(tv / maxV * wMax));
      const dW = Math.trunc(dr[r] / tv * w);
      const inVA = r >= dn && r <= up;
      const shr = Math.min(1, (tv / maxV) * (inVA ? o.vaBoost : 1));
      const alpha = 1 - Math.trunc(G_EDGE - shr * (G_EDGE - G_PEAK)) / 100;
      rowList.push({
        top: bot + (r + 1) * rh,
        bottom: bot + r * rh,
        dW,
        uW: w - dW,
        vol: tv,
        sellVol: dr[r],
        sellFill: rgba(o.sellRgb, alpha),
        buyFill: rgba(o.buyRgb, alpha),
      });
    }
  }
  const poc = bot + (pIdx + 0.5) * rh;
  return {
    from, to, right: Math.max(to, from + wMax), wMax, rows: rowList, poc, pocTop: poc + rh * 0.5, pocBot: poc - rh * 0.5,
    vah: bot + (up + 1) * rh, val: bot + dn * rh, rh,
  };
}

// Volume as TradingView's format.volume shows it: 950, 1.23K, 4.5M.
function volumeText(v) {
  const a = Math.abs(v);
  const short = (x, s) => `${Number(x.toFixed(x < 10 ? 2 : x < 100 ? 1 : 0))}${s}`;
  if (a >= 1e9) return short(v / 1e9, 'B');
  if (a >= 1e6) return short(v / 1e6, 'M');
  if (a >= 1e3) return short(v / 1e3, 'K');
  return String(Math.round(v));
}

function paneHeight(b, canvas) {
  const cands = [
    b && b.height,
    b && b.bottom - b.top,
    canvas && canvas.clientHeight,
    canvas && canvas.height / ((typeof window !== 'undefined' && window.devicePixelRatio) || 1),
  ];
  for (const h of cands) if (Number.isFinite(h) && h > 0) return h;
  return 700;
}

// Font size of the row numbers from how many profile rows fit on screen (Pine: large / normal /
// small / tiny); null = zoomed out too far, numbers hidden.
function rowNumberPx(rowsOnScreen, maxRows) {
  if (!(rowsOnScreen > 0) || rowsOnScreen > maxRows) return null;
  return rowsOnScreen <= 15 ? 16 : rowsOnScreen <= 25 ? 12 : rowsOnScreen <= 40 ? 10 : 8;
}

// Font size from the row height in pixels: about 70% of it, 9..16 px.
function rowNumberFont(rowPx) {
  return Math.max(9, Math.min(16, Math.floor(rowPx * 0.7)));
}

// ==HVN-CORE-BEGIN==
// HVN (high volume node / volume cluster) detection on a flat series of profile-resolution bars.
// Arrays h, l, v, t are parallel; [from, to) is one profile window (a week).
// Everything is sized by `unit` (mean 1-hour range), so it adapts to NAS100, gold, FX alike.
const HOUR_MS = 3600000;
const HVN = {
  rowFrac: 0.25,     // row height = 0.25 x mean 1h range (weekly profile; daily uses dayRowFrac)
  dayRowFrac: 0.15,  // a day spans fewer 1h ranges, so its rows are finer
  minRows: 100,      // at least this many rows over the window: after a volatile week the 1h range
                     // is large, and coarse rows would smooth away the LVN gap between two clusters
  dayMinRows: 40,
  maxRows: 400,
  smoothSigma: 1.5,  // Gaussian smoothing, in rows, for finding clusters
  promOwn: 0.3,      // a cluster peak dips >= 30% to the valley on each side (an LVN between clusters)
  edgeFrac: 0.7,     // zone = the cluster's dense core: rows holding >= 70% of its peak
  minVolShare: 0.12, // a cluster holds >= 12% of the week's volume (a real auction, not a spike)
  minTimeShare: 0.05,// price traded inside its core >= 5% of the week's bars (accepted over time)
  shapeLo: 0.15,     // D shape: 15%..85% of the cluster's volume sits below its peak,
  shapeHi: 0.85,     //   i.e. it bulges in the middle instead of ramping to one edge
  bodyFrac: 0.3,     // the cluster's body = rows >= 30% of its peak around the peak
  minPeakedness: 1.25,// D, not a rectangle: peak >= 1.25 x the body's mean row (flat block ~1.0)
  maxCoreOfBody: 0.7,// and the dense core (>= 70% of peak) covers <= 70% of the body's height
  minTaper: 0.25,    // the body extends on both sides of the peak (shorter side >= 25% of the longer)
  minPeakOfPoc: 0.35,// low-volume clusters: the peak row holds >= 35% of the POC row
  nearGapU: 0.5,     // zones closer than 0.5 x 1h range: keep the bigger one
};

function hourlyRangeUnit(h, l, t, from, to) {
  let sum = 0;
  let count = 0;
  let key = NaN;
  let hi = -Infinity;
  let lo = Infinity;
  for (let k = from; k < to; k++) {
    const kk = Math.floor(t[k] / HOUR_MS);
    if (kk !== key) {
      if (hi > lo) { sum += hi - lo; count++; }
      key = kk; hi = -Infinity; lo = Infinity;
    }
    if (h[k] > hi) hi = h[k];
    if (l[k] < lo) lo = l[k];
  }
  if (hi > lo) { sum += hi - lo; count++; }
  return count ? sum / count : 0;
}

function smoothProfile(vr, sigma) {
  const rows = vr.length;
  const radius = Math.max(1, Math.ceil(sigma * 3));
  const w = new Float64Array(radius * 2 + 1);
  for (let k = -radius; k <= radius; k++) w[k + radius] = Math.exp(-(k * k) / (2 * sigma * sigma));
  const sm = new Float64Array(rows);
  for (let r = 0; r < rows; r++) {
    let acc = 0;
    let wsum = 0;
    for (let k = -radius; k <= radius; k++) {
      const j = r + k;
      if (j < 0 || j >= rows) continue;
      acc += vr[j] * w[k + radius];
      wsum += w[k + radius];
    }
    sm[r] = acc / wsum;
  }
  return sm;
}

// LVN (low volume node): the thin valley between two volume clusters, where price moved fast.
const LVN = {
  maxValley: 0.5,         // the valley holds <= 50% of the smaller neighbouring peak (a gap, not a dent)
  edgeFrac: 0.25,         // zone = rows below valley + 25% of the way up to the smaller peak
  minSideShare: 0.08,     // both neighbouring clusters hold >= 8% of the window's volume
  minSidePeakOfPoc: 0.25, //   and peak >= 25% of the POC row: the LVN separates two real auctions
  minWidthU: 0.1,         // after clipping by HVN zones, slivers thinner than 0.1 x 1h range are dropped
};

// Profile of one window on a fixed price grid, smoothed, with its cluster peaks and the lowest
// row (the cut) between each pair of neighbouring peaks. Shared by HVN and LVN detection.
function nodeProfile(h, l, v, from, to, unit, rowFrac, minRows) {
  if (to - from < 30 || !(unit > 0)) return null;
  let top = -Infinity;
  let bot = Infinity;
  for (let k = from; k < to; k++) {
    if (h[k] > top) top = h[k];
    if (l[k] < bot) bot = l[k];
  }
  if (!(top > bot)) return null;
  let rowSize = Math.min(unit * rowFrac, (top - bot) / minRows);
  let rows = Math.ceil((top - bot) / rowSize);
  if (rows > HVN.maxRows) { rows = HVN.maxRows; rowSize = (top - bot) / rows; }
  // Rows sit on a fixed price grid, so a new week low does not shift every row.
  bot = Math.floor(bot / rowSize) * rowSize;
  rows = Math.ceil((top - bot) / rowSize);
  if (rows < 8) return null;

  const vr = new Float64Array(rows);
  let total = 0;
  for (let k = from; k < to; k++) {
    const vol = v[k];
    if (!(vol > 0)) continue;
    const rB = Math.min(rows - 1, Math.max(0, Math.floor((l[k] - bot) / rowSize)));
    const rT = Math.min(rows - 1, Math.max(0, Math.floor((h[k] - bot) / rowSize)));
    const ve = vol / (rT - rB + 1);
    for (let r = rB; r <= rT; r++) vr[r] += ve;
    total += vol;
  }
  if (!(total > 0)) return null;
  const sm = smoothProfile(vr, HVN.smoothSigma);
  let pocRow = 0;
  for (let r = 1; r < rows; r++) if (sm[r] > sm[pocRow]) pocRow = r;

  // Cluster peaks: local maxima with a real dip (LVN) on both sides.
  const peaks = [];
  for (let r = 0; r < rows; r++) {
    const p = sm[r];
    if (r > 0 && !(p > sm[r - 1])) continue;
    if (r < rows - 1 && sm[r + 1] > p) continue;
    let lMin = p;
    for (let j = r - 1; j >= 0 && sm[j] <= p; j--) if (sm[j] < lMin) lMin = sm[j];
    let rMin = p;
    for (let j = r + 1; j < rows && sm[j] <= p; j++) if (sm[j] < rMin) rMin = sm[j];
    if (r === pocRow || p - Math.max(lMin, rMin) >= HVN.promOwn * p) peaks.push(r);
  }
  // cuts[i] (0 < i < peaks.length) is the lowest row between peaks[i - 1] and peaks[i].
  const cuts = [0];
  for (let i = 1; i < peaks.length; i++) {
    let m = peaks[i - 1];
    for (let j = peaks[i - 1]; j <= peaks[i]; j++) if (sm[j] < sm[m]) m = j;
    cuts.push(m);
  }
  cuts.push(rows - 1);
  return { bot, rowSize, rows, vr, sm, total, pocRow, peaks, cuts };
}

// Every volume cluster of the window (one per peak, bounded by the cuts), with its dense core and
// the measures that tell a finished D-shaped auction from a flat block or a ramp.
function clustersOf(P, h, l, from, to) {
  const { bot, rowSize, vr, sm, total, pocRow, peaks, cuts } = P;
  const cands = [];
  for (let i = 0; i < peaks.length; i++) {
    const r = peaks[i];
    const s0 = cuts[i];
    const s1 = cuts[i + 1];
    let segVol = 0;
    let below = 0;
    for (let j = s0; j <= s1; j++) { segVol += vr[j]; if (j < r) below += vr[j]; }
    // Dense core: rows around the peak holding >= edgeFrac of it.
    const thr = sm[r] * HVN.edgeFrac;
    let a = r;
    while (a - 1 >= s0 && sm[a - 1] >= thr) a--;
    let b = r;
    while (b + 1 <= s1 && sm[b + 1] >= thr) b++;
    // Body (rows >= 30% of the peak) and its shape on the smoothed profile: a finished auction
    // bulges (peak well above the body's mean, a core narrower than the body); a flat block does not.
    const p = sm[r];
    let ba = r;
    while (ba - 1 >= s0 && sm[ba - 1] >= p * HVN.bodyFrac) ba--;
    let bb = r;
    while (bb + 1 <= s1 && sm[bb + 1] >= p * HVN.bodyFrac) bb++;
    let bodySum = 0;
    let coreRows = 0;
    for (let j = ba; j <= bb; j++) { bodySum += sm[j]; if (sm[j] >= p * HVN.edgeFrac) coreRows++; }
    const bodyRows = bb - ba + 1;
    cands.push({
      lo: bot + a * rowSize, hi: bot + (b + 1) * rowSize, peak: bot + (r + 0.5) * rowSize, peakRow: r,
      vol: segVol, volShare: segVol / total, shape: segVol > 0 ? below / segVol : 0.5, isPoc: r === pocRow, timeShare: 0,
      peakOfPoc: p / sm[pocRow], peakedness: p / (bodySum / bodyRows), coreOfBody: coreRows / bodyRows,
      taper: Math.min(r - ba, bb - r) / Math.max(1, r - ba, bb - r),
    });
  }
  // Time accepted inside each core (share of the window's bars that traded there).
  const bars = to - from;
  for (let k = from; k < to; k++) {
    for (const z of cands) if (l[k] <= z.hi && h[k] >= z.lo) z.timeShare += 1 / bars;
  }
  for (const z of cands) z.score = z.volShare + z.timeShare;
  return cands;
}

// A cluster counts as an HVN when it is a well-formed auction: a large share of the window's
// volume, price accepted there for a good part of it, and a D-shaped bulge. The POC cluster is
// exempt from the size tests (CORVEN: the POC is an HVN too) but must still be D-shaped.
function isHvnCluster(z) {
  return isDShaped(z) && (z.isPoc || (
    z.volShare >= HVN.minVolShare && z.timeShare >= HVN.minTimeShare && z.peakOfPoc >= HVN.minPeakOfPoc
  ));
}

// LVNs of the window: the valley between two neighbouring real clusters, when it is deep enough;
// the zone is its thinnest part.
function lvnOf(P, clusters) {
  const { bot, rowSize, sm, cuts } = P;
  const isSide = (z) => z.volShare >= LVN.minSideShare && z.peakOfPoc >= LVN.minSidePeakOfPoc;
  const out = [];
  for (let i = 1; i < clusters.length; i++) {
    const L = clusters[i - 1];
    const R = clusters[i];
    if (!isSide(L) || !isSide(R)) continue;
    const m = cuts[i];
    const low = Math.min(sm[L.peakRow], sm[R.peakRow]);
    const val = sm[m];
    if (!(val <= LVN.maxValley * low)) continue;
    const thr = val + LVN.edgeFrac * (low - val);
    let a = m;
    while (a - 1 > L.peakRow && sm[a - 1] <= thr) a--;
    let b = m;
    while (b + 1 < R.peakRow && sm[b + 1] <= thr) b++;
    out.push({ lo: bot + a * rowSize, hi: bot + (b + 1) * rowSize, depth: val / low });
  }
  return out;
}

// HVN zones, LVN zones and the cores of every sizeable cluster (areas price has filled) of one
// profile window. Arrays h, l, v are parallel; [from, to) is the window.
function detectVolumeNodes(h, l, v, from, to, unit, rowFrac = HVN.rowFrac, minRows = HVN.minRows) {
  const P = nodeProfile(h, l, v, from, to, unit, rowFrac, minRows);
  if (!P) return { hvn: [], lvn: [], cores: [] };
  const clusters = clustersOf(P, h, l, from, to);
  return {
    hvn: clusters.filter(isHvnCluster),
    lvn: lvnOf(P, clusters),
    cores: clusters.filter((z) => z.peakOfPoc >= HVN.minPeakOfPoc),
  };
}

function detectHvnZones(h, l, v, from, to, unit, rowFrac = HVN.rowFrac, minRows = HVN.minRows) {
  return detectVolumeNodes(h, l, v, from, to, unit, rowFrac, minRows).hvn;
}

function isDShaped(z) {
  return z.shape >= HVN.shapeLo && z.shape <= HVN.shapeHi &&
    z.peakedness >= HVN.minPeakedness && z.coreOfBody <= HVN.maxCoreOfBody && z.taper >= HVN.minTaper;
}

// CORVEN: overlapping zones (this week / last week) merge into one; zones packed close together
// keep only the biggest. Input zones carry `fromIndex` (chart bar where their week starts).
function mergeHvnZones(zones, unit) {
  const sorted = zones.slice().sort((x, y) => x.lo - y.lo);
  const out = [];
  for (const z of sorted) {
    const last = out[out.length - 1];
    if (last && z.lo <= last.hi) {
      last.hi = Math.max(last.hi, z.hi);
      last.vol = Math.max(last.vol, z.vol);
      last.fromIndex = Math.min(last.fromIndex, z.fromIndex);
      last.isPoc = last.isPoc || z.isPoc;
    } else if (last && z.lo - last.hi < HVN.nearGapU * unit) {
      if (z.vol > last.vol) out[out.length - 1] = { ...z };
    } else {
      out.push({ ...z });
    }
  }
  return out;
}
// Daily clusters from several days: overlapping ones (any chain of overlaps) are one area and
// only its most convincing zone is kept (highest volume + time share), tagged with how many days
// built a cluster there. Areas closer than nearGapU x unit keep the stronger one.
function pickReputableZones(zones, unit) {
  const sorted = zones.slice().sort((x, y) => x.lo - y.lo);
  const groups = [];
  for (const z of sorted) {
    const g = groups[groups.length - 1];
    if (g && z.lo <= g.hi) {
      g.hi = Math.max(g.hi, z.hi);
      g.days.add(z.fromIndex);
      if (z.score > g.best.score) g.best = z;
    } else {
      groups.push({ hi: z.hi, best: z, days: new Set([z.fromIndex]) });
    }
  }
  const out = [];
  for (const g of groups) {
    const z = { ...g.best, days: g.days.size };
    const last = out[out.length - 1];
    if (last && z.lo - last.hi < HVN.nearGapU * unit) {
      if (z.score + 0.05 * z.days > last.score + 0.05 * last.days) out[out.length - 1] = z;
    } else {
      out.push(z);
    }
  }
  return out;
}
// Zone z trimmed where a blocking range overlaps its edge. A blocker inside it (splitting it in two)
// means price has built volume in the middle of the gap, so the zone is gone; so are slivers under minW.
function clipZone(z, blockers, minW) {
  let pieces = [[z.lo, z.hi]];
  for (const b of blockers) {
    const next = [];
    for (const [lo, hi] of pieces) {
      if (b.hi <= lo || b.lo >= hi) { next.push([lo, hi]); continue; }
      if (b.lo > lo) next.push([lo, b.lo]);
      if (b.hi < hi) next.push([b.hi, hi]);
    }
    if (next.length > pieces.length) return [];
    pieces = next;
  }
  return pieces.filter(([lo, hi]) => hi - lo >= minW).map(([lo, hi]) => ({ ...z, lo, hi }));
}

// LVNs of the current and the previous period. An old LVN that the current period has since
// filled with a cluster is gone; overlapping LVNs merge into one zone spanning both; an HVN
// wins over an LVN where they overlap. `periods` counts the periods that found an LVN there.
function mergeLvnZones(prevLvn, curLvn, curCores, hvnZones, unit) {
  const minW = LVN.minWidthU * unit;
  const zones = [];
  for (const z of prevLvn) for (const piece of clipZone(z, curCores, minW)) zones.push({ ...piece, periods: new Set([z.fromIndex]) });
  for (const z of curLvn) zones.push({ ...z, periods: new Set([z.fromIndex]) });
  zones.sort((x, y) => x.lo - y.lo);
  const merged = [];
  for (const z of zones) {
    const last = merged[merged.length - 1];
    if (last && z.lo <= last.hi) {
      last.hi = Math.max(last.hi, z.hi);
      last.fromIndex = Math.min(last.fromIndex, z.fromIndex);
      for (const p of z.periods) last.periods.add(p);
    } else {
      merged.push(z);
    }
  }
  const out = [];
  for (const z of merged) for (const piece of clipZone(z, hvnZones, minW)) out.push({ ...piece, periods: z.periods.size });
  return out;
}
// ==HVN-CORE-END==

// ---------------------------------------------------------------------------------------------
// Base data. The chart only holds the bars scrolled into view (a few hours on M1, weeks on M30),
// so building from chart bars draws something different on every timeframe. Profiles, HVN and
// VWAP are built instead from one series of profile-resolution bars covering the whole look-back,
// fetched independently of the chart: the same input on M1, M5, M15...

// History: `count` bars of `res`, captured from the requested series itself (bv.security hands
// the expression every requested bar, including those older than the chart's first bar).
function requestHistory(res, count, cache) {
  let got = null;
  const r = bv.security({ timeframe: res, calcBarsCount: count }, (bars) => {
    got = bars;
    // The values are not used; one shared array avoids a 100k allocation on every tick.
    if (!cache.zeros || cache.zeros.length !== bars.length) cache.zeros = new Array(bars.length).fill(0);
    return cache.zeros;
  });
  if (got && got.length) cache.hist = got;
  return r !== undefined || cache.hist !== null;
}

// Newest bars from the chart itself (live): its own bars on a chart of the profile resolution,
// otherwise the intrabars of the last couple of days of chart bars.
function liveBars(dataList, ltf) {
  if (!ltf) return dataList;
  const out = [];
  for (let i = 0; i < dataList.length; i++) {
    const a = ltf[i];
    if (a) for (let k = 0; k < a.length; k++) out.push(a[k]);
  }
  return out;
}

// Both series merged by time into flat arrays (oldest first); on the same timestamp the live
// copy wins because it is the freshest.
function mergeBars(hist, live) {
  const cap = hist.length + live.length;
  const B = { t: new Float64Array(cap), o: new Float64Array(cap), h: new Float64Array(cap), l: new Float64Array(cap), c: new Float64Array(cap), v: new Float64Array(cap), n: 0 };
  const put = (x) => {
    const k = B.n++;
    B.t[k] = x.timestamp; B.o[k] = x.open; B.h[k] = x.high; B.l[k] = x.low; B.c[k] = x.close; B.v[k] = x.volume;
  };
  let i = 0;
  let j = 0;
  while (i < hist.length || j < live.length) {
    const ti = i < hist.length ? hist[i].timestamp : Infinity;
    const tj = j < live.length ? live[j].timestamp : Infinity;
    if (tj <= ti) {
      put(live[j++]);
      if (tj === ti) i++;
    } else {
      put(hist[i++]);
    }
  }
  return B;
}

// Trading day (Pine time_tradingday) and session start of every base bar, from the symbol's
// exchange session, so a day / week starts where the chart's own D / W bars start.
function sessionDays(B, cache) {
  const key = `${B.n}|${B.t[0]}|${B.t[B.n - 1]}`;
  if (cache.dayKey === key) return cache.days;
  const info = bv.syminfo() || {};
  const sess = info.session || '24x7';
  const tz = info.timezone || 'UTC';
  const day = new Float64Array(B.n);
  const start = new Float64Array(B.n);
  let ok = 0;
  for (let k = 0; k < B.n; k++) {
    const s = bv.session(B.t[k], sess, tz);
    if (s) { day[k] = s.tradingDay; start[k] = s.start; ok++; } else { day[k] = NaN; start[k] = NaN; }
  }
  if (ok < B.n / 2) {
    // No usable session: roll the day at 22:00 UTC, the FX / CME daily break.
    for (let k = 0; k < B.n; k++) {
      day[k] = Math.floor((B.t[k] + 2 * HOUR_MS_) / DAY_MS) * DAY_MS;
      start[k] = day[k] - 2 * HOUR_MS_;
    }
  } else {
    // A bar outside the session (e.g. in the daily break) keeps the previous bar's day.
    let first = 0;
    while (first < B.n && !Number.isFinite(day[first])) first++;
    for (let k = 0; k < B.n; k++) {
      if (Number.isFinite(day[k])) continue;
      const from = k < first ? first : k - 1;
      day[k] = day[from];
      start[k] = start[from];
    }
  }
  cache.dayKey = key;
  cache.days = { day, start };
  return cache.days;
}

function periodKey(days, B, k, anchor) {
  const d = days.day[k];
  switch (anchor) {
    case '1W': return Math.floor((d / DAY_MS + 3) / 7);   // weeks start on Monday's trading day
    case '1M': { const dt = new Date(d); return dt.getUTCFullYear() * 12 + dt.getUTCMonth(); }
    case '1h':
    case '4h': {
      const p = ANCHOR_SPAN_MIN[anchor] * 60000;
      return days.start[k] + Math.floor((B.t[k] - days.start[k]) / p) * p;
    }
    default: return d;
  }
}

// Base-bar ranges [a, b) of every anchor period, oldest first.
function periodsOf(B, days, anchor) {
  const out = [];
  if (!B.n) return out;
  let a = 0;
  let key = periodKey(days, B, 0, anchor);
  for (let k = 1; k < B.n; k++) {
    const kk = periodKey(days, B, k, anchor);
    if (kk !== key) { out.push([a, k]); a = k; key = kk; }
  }
  out.push([a, B.n]);
  return out;
}

// Chart bar holding time t (the last bar opened at or before t), or -1 before the first bar.
function chartIndexAt(dataList, t) {
  let lo = 0;
  let hi = dataList.length - 1;
  if (hi < 0 || t < dataList[0].timestamp) return -1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (dataList[mid].timestamp <= t) lo = mid; else hi = mid - 1;
  }
  return lo;
}

// Chart span [from, to] of a period; from is clamped to the first loaded bar, null if the whole
// period lies before the loaded chart.
function chartSpan(dataList, tStart, tEnd) {
  const to = chartIndexAt(dataList, tEnd);
  if (to < 0) return null;
  return { from: Math.max(0, chartIndexAt(dataList, tStart)), to };
}

// HVN and LVN zones of the current and the previous week, merged (CORVEN). Built from closed base
// bars only (the forming one is left out) and rebuilt only when a new bar closes, on one row grid
// sized from the finished previous week, so they do not jitter. Side follows the live price:
// above = sell, below = buy, price inside = not tradable yet.
function buildZonesWeek(B, weeks, cache) {
  const cur = weeks[weeks.length - 1];
  const prev = weeks.length > 1 ? weeks[weeks.length - 2] : null;
  const end = B.n - 1;
  const key = `W|${B.t[(prev || cur)[0]]}|${B.t[end - 1]}|${end}`;
  if (cache.zoneKey !== key) {
    const unit = prev ? hourlyRangeUnit(B.h, B.l, B.t, prev[0], prev[1]) : hourlyRangeUnit(B.h, B.l, B.t, cur[0], end);
    // fromIndex carries the session start time until it is mapped to a chart bar in calc;
    // merged zones keep the earliest one.
    const tag = (zs, from) => zs.map((z) => ({ ...z, fromIndex: from }));
    const p = prev ? detectVolumeNodes(B.h, B.l, B.v, prev[0], prev[1], unit) : { hvn: [], lvn: [] };
    const c = detectVolumeNodes(B.h, B.l, B.v, cur[0], Math.min(cur[1], end), unit);
    const pFrom = prev ? B.t[prev[0]] : 0;
    const cFrom = B.t[cur[0]];
    const hvn = mergeHvnZones([...tag(p.hvn, pFrom), ...tag(c.hvn, cFrom)], unit);
    cache.zoneKey = key;
    cache.zones = { hvn, lvn: mergeLvnZones(tag(p.lvn, pFrom), tag(c.lvn, cFrom), c.cores, hvn, unit) };
  }
  return cache.zones;
}

// Daily HVN zones from the last nDays finished days plus today (closed bars only); overlapping
// days keep their most convincing zone. Daily LVNs from yesterday and today, merged like weekly ones.
function buildZonesDay(B, days, nDays, cache) {
  const first = Math.max(0, days.length - 1 - nDays);
  const end = B.n - 1;
  const key = `D|${B.t[days[first][0]]}|${B.t[end - 1]}|${end}`;
  if (cache.zoneKey !== key) {
    const cur = days[days.length - 1];
    const doneEnd = first < days.length - 1 ? cur[0] : end;
    const unit = hourlyRangeUnit(B.h, B.l, B.t, days[first][0], doneEnd > days[first][0] ? doneEnd : end);
    const hvnAll = [];
    const lvnByDay = [];
    let todayCores = [];
    for (let d = first; d < days.length; d++) {
      const [a, b] = days[d];
      const nodes = detectVolumeNodes(B.h, B.l, B.v, a, Math.min(b, end), unit, HVN.dayRowFrac, HVN.dayMinRows);
      // the day's start time identifies the day
      for (const z of nodes.hvn) hvnAll.push({ ...z, fromIndex: B.t[a] });
      lvnByDay.push(nodes.lvn.map((z) => ({ ...z, fromIndex: B.t[a] })));
      if (d === days.length - 1) todayCores = nodes.cores;
    }
    const hvn = pickReputableZones(hvnAll, unit);
    const today = lvnByDay[lvnByDay.length - 1] || [];
    const yesterday = lvnByDay.length > 1 ? lvnByDay[lvnByDay.length - 2] : [];
    cache.zoneKey = key;
    cache.zones = { hvn, lvn: mergeLvnZones(yesterday, today, todayCores, hvn, unit) };
  }
  return cache.zones;
}

function priceOf(name, B) {
  switch (name) {
    case 'close': return (k) => B.c[k];
    case 'open': return (k) => B.o[k];
    case 'high': return (k) => B.h[k];
    case 'low': return (k) => B.l[k];
    case 'hl2': return (k) => (B.h[k] + B.l[k]) / 2;
    case 'ohlc4': return (k) => (B.o[k] + B.h[k] + B.l[k] + B.c[k]) / 4;
    case 'hlcc4': return (k) => (B.h[k] + B.l[k] + B.c[k] + B.c[k]) / 4;
    default: return (k) => (B.h[k] + B.l[k] + B.c[k]) / 3;
  }
}

// Anchored VWAP and its standard deviation over the base bars. Between bar closes only the forming
// (last) bar changes, so the series is kept and just its last value is recomputed.
function vwapSeries(B, days, o, cache, sameBars) {
  const key = `${o.vwapAnchor}|${o.vwapSrc}`;
  const src = priceOf(o.vwapSrc, B);
  const last = B.n - 1;
  let vs = cache.vwapSeries;
  if (sameBars && vs && vs.key === key) {
    const p = src(last);
    const v = B.v[last];
    let { sV, sPV, sP2V } = vs.before;
    if (Number.isFinite(p) && Number.isFinite(v)) { sV += v; sPV += p * v; sP2V += p * p * v; }
    if (sV > 0) {
      vs.w[last] = sPV / sV;
      vs.sdv[last] = Math.sqrt(Math.max(0, sP2V / sV - vs.w[last] * vs.w[last]));
    }
    return vs;
  }
  const periods = periodsOf(B, days, o.vwapAnchor);
  const w = new Float64Array(B.n).fill(NaN);
  const sdv = new Float64Array(B.n).fill(NaN);
  let before = { sV: 0, sPV: 0, sP2V: 0 };
  for (const [a, b] of periods) {
    let sV = 0;
    let sPV = 0;
    let sP2V = 0;
    for (let k = a; k < b; k++) {
      if (k === last) before = { sV, sPV, sP2V };   // sums the forming bar is added to
      const p = src(k);
      const v = B.v[k];
      if (Number.isFinite(p) && Number.isFinite(v)) { sV += v; sPV += p * v; sP2V += p * p * v; }
      if (sV > 0) {
        w[k] = sPV / sV;
        sdv[k] = Math.sqrt(Math.max(0, sP2V / sV - w[k] * w[k]));   // Pine ta.vwap stdev
      }
    }
  }
  vs = { key, periods, w, sdv, before };
  cache.vwapSeries = vs;
  return vs;
}

// Each chart bar takes the VWAP of its own last base bar, so the line is the same on every
// timeframe. Only the last vwapKeep finished periods plus the current one are drawn.
function vwapOnChart(dataList, B, vs, o, res, barMs) {
  const n = dataList.length;
  const firstKept = Math.max(0, vs.periods.length - 1 - o.vwapKeep);
  const spans = [];
  for (let p = firstKept; p < vs.periods.length; p++) {
    const [a, b] = vs.periods[p];
    const span = chartSpan(dataList, B.t[a], B.t[b - 1]);
    if (span) spans.push([span.from, span.to]);
  }
  const base = spans.length ? spans[0][0] : n;
  const m = new Float64Array(n - base).fill(NaN);
  const sd = new Float64Array(n - base).fill(NaN);
  let k = -1;
  for (let i = 0; i < n; i++) {
    const end = dataList[i].timestamp + barMs;
    while (k + 1 < B.n && B.t[k + 1] < end) k++;
    if (k >= 0 && Number.isFinite(vs.w[k])) {
      res[i] = { vwap: vs.w[k] };
      if (i >= base) { m[i - base] = vs.w[k]; sd[i - base] = vs.sdv[k]; }
    }
  }
  return { base, m, sd, periods: spans };
}

// The merged base series, rebuilt only when a bar is added; on a tick only the forming bar is
// patched in place.
function baseSeries(hist, live, cache) {
  const newest = live.length ? live[live.length - 1] : hist[hist.length - 1];
  const key = `${hist.length}|${hist.length ? `${hist[0].timestamp}|${hist[hist.length - 1].timestamp}` : ''}|${live.length}|${live.length ? `${live[0].timestamp}|${newest.timestamp}` : ''}`;
  const B = cache.B;
  if (cache.bKey === key && B && newest && B.t[B.n - 1] === newest.timestamp) {
    const k = B.n - 1;
    B.o[k] = newest.open; B.h[k] = newest.high; B.l[k] = newest.low; B.c[k] = newest.close; B.v[k] = newest.volume;
    return { B, sameBars: true };
  }
  cache.B = mergeBars(hist, live);
  cache.bKey = key;
  return { B: cache.B, sameBars: false };
}

// Per-indicator caches live here, not on the indicator object: the platform can hand calc() the
// indicator wrapped in a Proxy, and a Map reached through a Proxy throws "incompatible receiver".
// The indicator only carries the cache's id (a string survives any wrapping).
const CACHES = {};
const CACHE_IDS = [];
const MAX_CACHES = 6;
let lastDiag = '';
function newCache() {
  return { series: {}, profiles: {}, res: null };
}
// Everything derived from one base series (one bar timeframe): its bars, trading days, sessions,
// zones and VWAP. Switching the timeframe starts a fresh one.
function newSeriesCache() {
  return { hist: null, zeros: null, B: null, bKey: '', dayKey: '', days: null, sessBy: null, zoneKey: '', zones: null, vwapSeries: null };
}
function cacheOf(indicator) {
  let id = indicator._benzoCacheId;
  if (typeof id !== 'string' || !CACHES[id]) {
    id = `benzo-${Math.random().toString(36).slice(2)}-${Date.now()}`;
    indicator._benzoCacheId = id;
    CACHES[id] = newCache();
    CACHE_IDS.push(id);
    while (CACHE_IDS.length > MAX_CACHES) delete CACHES[CACHE_IDS.shift()];
  }
  return CACHES[id];
}

return {
  figures: [
    {
      key: 'vwap',
      type: 'line',
      title: 'VWAP: ',
      styles: ({ indicator }) => ({
        color: indicator?.extendData?.inputs?.colVWAP || '#ab47bc',
        size: indicator?.extendData?.inputs?.vwapWidth || 2,
      }),
    },
  ],

  calc(dataList, indicator) {
    const {
      hideCandles = false, showWeekProfile = true, showDayProfile = true, profileRows = 200, valueArea = 70, maxSessions = 5, widthPct = 1,
      maxWidthBar = 90, showLive = true, profileRes = '1m', vaBoost = 1.18,
      colBuy = '#90bff9', colSell = '#b39ddb', colDayBuy = '#c9a43c', colDaySell = '#2f5fd8', colPOC = '#5b6472', colVWAP = '#ab47bc', vwapWidth = 2,
      showVWAP = true, vwapSrc = 'hlc3', vwapAnchor = '1D', vwapKeep = 5,
      showBand1 = true, bandMult1 = 1.0, bandLine1 = '#ab47bca6', bandFill1 = '#ab47bc1a',
      showBand2 = false, bandMult2 = 2.0, bandLine2 = '#ab47bc80', bandFill2 = '#ab47bc12',
      showBand3 = false, bandMult3 = 3.0, bandLine3 = '#ab47bc59', bandFill3 = '#ab47bc0d',
      showHVN = true, hvnBuyColor = '#26a69a', hvnSellColor = '#ef5350', hvnInsideColor = '#9e9e9e',
      showLVN = true, lvnBuyColor = '#29b6f6', lvnSellColor = '#ffa726',
      showWeekVA = true, showDayVA = true, colWeekVA = '#4a90e2', colDayVA = '#c9a43c',
      rowNumbersMode: rowNumbersOn = 'Auto', rowNumbersAll = true, rowNumberColor = '#d1d4dc', rowNumberMax = 70,
    } =indicator.extendData?.inputs || {};
    const n = dataList.length;
    const res = new Array(n);
    for (let i = 0; i < n; i++) res[i] = {};
    if (n === 0) return res;
    const cache = cacheOf(indicator);
    // While a data request is in flight, keep showing the last result instead of a blank frame.
    // Hide-candles mode: the chart paints every candle in a transparent colour (barColor), so only
    // the indicator's drawings stay; the rows are reused across calls, so the colour is also cleared.
    const withCandleColor = (rows) => {
      for (const row of rows) {
        if (hideCandles) row.barColor = TRANSPARENT;
        else if (row.barColor) delete row.barColor;
      }
      return rows;
    };
    const keepLast = () => {
      const prev = cache.res;
      if (prev) for (let i = 0; i < n && i < prev.length; i++) res[i] = prev[i];
      return withCandleColor(res);
    };

    // HVN / LVN zones come from the week profile while it is shown, otherwise from the day profile.
    const isDay = showDayProfile && !showWeekProfile;
    const barMs = bv.detectBarMs(dataList);
    const resKey = RES_MS[profileRes] ? profileRes : '1m';
    // Look-back each base series must cover: kept sessions (+ the week before, for weekly HVN) and
    // the kept VWAP periods. Counted in calendar minutes, so it over-covers weekends and breaks.
    const sessions = Math.max(1, Math.trunc(maxSessions));
    const profileMin = (sessions + 2) * (showWeekProfile || !showDayProfile ? 10080 : 1440);
    const vwapMin = showVWAP ? (Math.max(1, Math.trunc(vwapKeep)) + 1) * (ANCHOR_SPAN_MIN[vwapAnchor] || 1440) : 0;
    // One base series of `res` bars: history fetched independently of the chart plus the newest
    // bars live from the chart (its own bars on a chart of that timeframe, otherwise two days of
    // intrabars). null while the data is still loading.
    const usedSeries = new Set();
    const loadSeries = (res, minutes) => {
      usedSeries.add(res);
      const ms = RES_MS[res];
      const c = cache.series[res] || (cache.series[res] = newSeriesCache());
      const ready = requestHistory(res, Math.min(MAX_HISTORY_BARS, Math.ceil(minutes * 60000 / ms)), c);
      const useLowerTf = ms < barMs;
      const ltf = useLowerTf ? bv.securityLowerTf({ timeframe: res, calcBarsCount: 2 * 1440 * 60000 / ms }, (bars) => bars) : null;
      if (!ready || (useLowerTf && !ltf)) return null;
      const { B, sameBars } = baseSeries(c.hist || [], ms <= barMs ? liveBars(dataList, ltf) : [], c);
      if (B.n < 2) return null;
      return { B, sameBars, days: sessionDays(B, c), c };
    };
    // Profiles and zones use the chosen data timeframe; the VWAP always runs on 1m bars, so the line
    // is smooth and exact whatever that timeframe is.
    const main = loadSeries(resKey, resKey === '1m' ? Math.max(profileMin, vwapMin) : profileMin);
    const vw1m = !showVWAP || resKey === '1m' ? main : loadSeries('1m', vwapMin);
    for (const key of Object.keys(cache.series)) if (!usedSeries.has(key)) delete cache.series[key];
    if (!main || !vw1m) return keepLast();
    const { B, sameBars, days } = main;
    const sc = main.c;

    const o = {
      rows: Math.max(1, Math.trunc(profileRows)), valueArea, widthPct, maxWidthBar, vaBoost,
      vwapSrc, vwapAnchor, vwapKeep: Math.max(1, Math.trunc(vwapKeep)),
    };
    const weekRgb = { buyRgb: parseRgb(colBuy, [144, 191, 249]), sellRgb: parseRgb(colSell, [179, 157, 219]) };
    const dayRgb = { buyRgb: parseRgb(colDayBuy, [201, 164, 60]), sellRgb: parseRgb(colDaySell, [47, 95, 216]) };

    // Session ranges per anchor ('1W' / '1D'), recomputed only when a base bar is added.
    if (!sameBars || !sc.sessBy) sc.sessBy = {};
    const sessionsOf = (anchor) => sc.sessBy[anchor] || (sc.sessBy[anchor] = periodsOf(B, days, anchor));
    const sess = sessionsOf(isDay ? '1D' : '1W');

    // Completed sessions (last maxSessions) plus the developing one. A finished session never
    // changes: its profile is built once and reused on every tick.
    const profKey = [profileRows, valueArea, widthPct, maxWidthBar, vaBoost, colBuy, colSell, colDayBuy, colDaySell, profileRes].join('|');
    const usedKeys = new Set();
    // Auto: numbers on the day profile when it is shown (it overrides the week's), else on the week's.
    const numbersOn = rowNumbersOn === 'Auto' ? (showDayProfile ? 'Day' : 'Week') : rowNumbersOn;
    const sessionProfiles = (anchor, rgb) => {
      const ps = sessionsOf(anchor);
      const po = { ...o, ...rgb };
      const wantNumbers = numbersOn === 'Both' || (anchor === '1D' ? numbersOn === 'Day' : numbersOn === 'Week');
      const out = [];
      for (let k = Math.max(0, ps.length - 1 - sessions); k < ps.length; k++) {
        const isLive = k === ps.length - 1;
        if (isLive && !showLive) continue;
        const [a, b] = ps[k];
        const span = chartSpan(dataList, B.t[a], B.t[b - 1]);
        if (!span) continue;
        if (isLive) {
          const p = buildProfile(B, a, b, span.from, span.to, po);
          if (p) {
            p.numbers = wantNumbers;
            out.push(p);
          }
          continue;
        }
        const key = `${anchor}|${B.t[a]}|${B.t[b - 1]}|${b - a}|${span.from}|${span.to}|${profKey}`;
        usedKeys.add(key);
        let p = cache.profiles[key];
        if (p === undefined) {
          p = buildProfile(B, a, b, span.from, span.to, po);
          cache.profiles[key] = p;
        }
        if (p) {
          p.numbers = wantNumbers && rowNumbersAll;
          out.push(p);
        }
      }
      return out;
    };
    // Day profiles first: draw paints the list top-most first, so they sit above the week's.
    const profiles = [];
    const vaLines = [];
    const addProfiles = (anchor, rgb, showVA, color) => {
      for (const p of sessionProfiles(anchor, rgb)) {
        profiles.push(p);
        if (showVA) vaLines.push({ from: p.from, to: p.to, vah: p.vah, val: p.val, color });
      }
    };
    if (showDayProfile) addProfiles('1D', dayRgb, showDayVA, colDayVA);
    if (showWeekProfile) addProfiles('1W', weekRgb, showWeekVA, colWeekVA);
    for (const key of Object.keys(cache.profiles)) if (!usedKeys.has(key)) delete cache.profiles[key];

    const vwap = showVWAP ? vwapOnChart(dataList, vw1m.B, vwapSeries(vw1m.B, vw1m.days, o, vw1m.c, vw1m.sameBars), o, res, barMs) : null;
    // HVN and LVN zones, each across the pane from its session's start. Above the live price =
    // sell, below = buy, price inside = gray (not tradable yet).
    const zones = [];
    if (showHVN || showLVN) {
      const found = isDay ? buildZonesDay(B, sess, sessions, sc) : buildZonesWeek(B, sess, sc);
      const price = dataList[n - 1].close;
      const insideRgb = parseRgb(hvnInsideColor, [158, 158, 158]);
      const kinds = [];
      if (showHVN) kinds.push({ list: found.hvn, kind: 'HVN', buy: parseRgb(hvnBuyColor, [38, 166, 154]), sell: parseRgb(hvnSellColor, [239, 83, 80]) });
      if (showLVN) kinds.push({ list: found.lvn, kind: 'LVN', buy: parseRgb(lvnBuyColor, [41, 182, 246]), sell: parseRgb(lvnSellColor, [255, 167, 38]) });
      const unitName = isDay ? 'ngày' : 'tuần';
      for (const { list, kind, buy, sell } of kinds) {
        for (const z of list) {
          const side = z.hi < price ? 1 : z.lo > price ? -1 : 0;
          const rgb = side > 0 ? buy : side < 0 ? sell : insideRgb;
          const count = kind === 'HVN' ? z.days || 0 : z.periods || 0;
          zones.push({
            lo: z.lo,
            hi: z.hi,
            fromIndex: Math.max(0, chartIndexAt(dataList, z.fromIndex)),   // zone's session start, on the chart
            side,
            fill: rgba(rgb, side ? 0.18 : 0.10),
            line: rgba(rgb, side ? 0.95 : 0.6),
            // HVN edges solid, LVN edges dashed; price inside: dotted
            dash: side === 0 ? [2, 3] : kind === 'LVN' ? [6, 4] : [],
            label: `${kind}${side > 0 ? ' Buy' : side < 0 ? ' Sell' : ' (giá đang trong vùng)'}`,
            suffix: count > 1 ? ` · ${count} ${unitName}` : '',
          });
        }
      }
    }

    const pocRgb = parseRgb(colPOC, [91, 100, 114]);
    const bands = [];
    if (showBand1) bands.push({ mult: bandMult1, line: bandLine1, fill: bandFill1 });
    if (showBand2) bands.push({ mult: bandMult2, line: bandLine2, fill: bandFill2 });
    if (showBand3) bands.push({ mult: bandMult3, line: bandLine3, fill: bandFill3 });

    indicator._benzoVP = {
      profiles,
      vaLines,
      pocFill: rgba(pocRgb, 0.38),
      pocLine: rgba(pocRgb, 0.85),
      vwap,
      vwapColor: colVWAP,
      vwapWidth,
      bands,
      zones,
      rowNumberColor,
      rowNumberMax: Math.max(1, Number(rowNumberMax) || 70),
      rowNumbersMode: numbersOn,
    };
    cache.res = res;
    return withCandleColor(res);
  },

  draw(args) {
    const st = args.indicator._benzoVP;
    if (!st) return true;
    const { ctx } = args;
    const { from, to } = bv.visible(args);
    const X = (i) => bv.xOfIndex(args, i);
    const Y = (p) => bv.yOfPrice(args, p);

    ctx.save();
    ctx.setLineDash([]);
    ctx.lineJoin = 'round';
    // Everything sits behind the candles (Pine behind_chart). With destination-over each new
    // shape goes UNDER what is already painted, so layers are painted top-most first.
    ctx.globalCompositeOperation = 'destination-over';

    const visProfiles = [];
    for (const p of st.profiles) {
      if (p.right < from - 1 || p.from > to + 1) continue;
      visProfiles.push(p);
    }

    // 1. POC lines.
    ctx.strokeStyle = st.pocLine;
    ctx.lineWidth = 4;
    ctx.beginPath();
    for (const p of visProfiles) {
      const y = Y(p.poc);
      ctx.moveTo(X(p.from), y);
      ctx.lineTo(X(p.to), y);
    }
    ctx.stroke();

    // VAH / VAL: dashed, no fill.
    ctx.lineWidth = 1.5;
    ctx.setLineDash([6, 4]);
    for (const l of st.vaLines || []) {
      if (l.to < from - 1 || l.from > to + 1) continue;
      ctx.strokeStyle = l.color;
      ctx.beginPath();
      for (const price of [l.vah, l.val]) {
        const y = Y(price);
        ctx.moveTo(X(l.from), y);
        ctx.lineTo(X(l.to), y);
      }
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // 2. VWAP line and band lines.
    const vw = st.vwap;
    const ranges = [];
    if (vw) {
      for (const [pf, pt] of vw.periods) {
        const lo = Math.max(pf, from - 1);
        const hi = Math.min(pt, to + 1);
        if (lo <= hi) ranges.push([lo, hi]);
      }
    }
    const tracePath = (lo, hi, k) => {
      let started = false;
      for (let i = lo; i <= hi; i++) {
        const j = i - vw.base;
        const mv = vw.m[j];
        if (!Number.isFinite(mv)) continue;
        const x = X(i);
        const y = Y(mv + k * vw.sd[j]);
        if (started) ctx.lineTo(x, y); else { ctx.moveTo(x, y); started = true; }
      }
    };
    const traceRing = (lo, hi, kOut, kIn) => {
      let started = false;
      for (let i = lo; i <= hi; i++) {
        const j = i - vw.base;
        const mv = vw.m[j];
        if (!Number.isFinite(mv)) continue;
        const x = X(i);
        const y = Y(mv + kOut * vw.sd[j]);
        if (started) ctx.lineTo(x, y); else { ctx.moveTo(x, y); started = true; }
      }
      if (!started) return;
      for (let i = hi; i >= lo; i--) {
        const j = i - vw.base;
        const mv = vw.m[j];
        if (!Number.isFinite(mv)) continue;
        ctx.lineTo(X(i), Y(mv + kIn * vw.sd[j]));
      }
      ctx.closePath();
    };

    if (ranges.length) {
      ctx.strokeStyle = st.vwapColor;
      ctx.lineWidth = st.vwapWidth;
      ctx.beginPath();
      for (const [lo, hi] of ranges) tracePath(lo, hi, 0);
      ctx.stroke();

      ctx.lineWidth = 1;
      for (let b = st.bands.length - 1; b >= 0; b--) {
        const band = st.bands[b];
        ctx.strokeStyle = band.line;
        ctx.beginPath();
        for (const [lo, hi] of ranges) {
          tracePath(lo, hi, band.mult);
          tracePath(lo, hi, -band.mult);
        }
        ctx.stroke();
      }
    }

    // 3. POC boxes, then profile rows.
    ctx.fillStyle = st.pocFill;
    for (const p of visProfiles) {
      const x1 = X(p.from);
      const y1 = Y(p.pocTop);
      ctx.fillRect(x1, y1, X(p.to) - x1, Y(p.pocBot) - y1);
    }
    for (const p of visProfiles) {
      const xs = X(p.from);
      for (const r of p.rows) {
        const yT = Y(r.top);
        const h = Y(r.bottom) - yT;
        const xm = X(p.from + r.dW);
        if (r.dW > 0) {
          ctx.fillStyle = r.sellFill;
          ctx.fillRect(xs, yT, xm - xs, h);
        }
        if (r.uW > 0) {
          ctx.fillStyle = r.buyFill;
          ctx.fillRect(xm, yT, X(p.from + r.dW + r.uW) - xm, h);
        }
      }
    }

    // 4. HVN / LVN bands across the whole pane (below the profile, above the VWAP zones).
    const { width: paneW } = bv.bounds(args);
    for (const z of st.zones) {
      const y1 = Y(z.hi);
      const y2 = Y(z.lo);
      const x0 = Math.max(0, X(z.fromIndex) - bv.halfBar(args, z.fromIndex));
      if (!Number.isFinite(y1) || !Number.isFinite(y2) || !Number.isFinite(x0) || x0 >= paneW) continue;
      ctx.fillStyle = z.fill;
      ctx.fillRect(x0, y1, paneW - x0, y2 - y1);
    }

    // 5. Band zones (bottom layer). Each zone runs from its band to the next enabled band
    // inside it, or to the VWAP.
    if (ranges.length) {
      let inner = 0;
      for (const band of st.bands) {
        ctx.fillStyle = band.fill;
        ctx.beginPath();
        for (const [lo, hi] of ranges) {
          traceRing(lo, hi, band.mult, inner);
          traceRing(lo, hi, -band.mult, -inner);
        }
        ctx.fill();
        inner = band.mult;
      }
    }

    // Zone edge lines and labels on top of the candles, so the levels stay easy to find.
    ctx.globalCompositeOperation = 'source-over';
    // Row numbers on top of everything (candles included), so they stay readable: the total volume
    // of each row, in one column at the profile's start. Shown while rows on screen (pane height /
    // row height) <= rowNumberMax; the font follows the row height. Dark outline for contrast.
    const paneH = paneHeight(bv.bounds(args), ctx.canvas);
    const diag = [];
    for (const p of visProfiles) {
      if (!p.numbers || !p.rows.length) continue;
      const rowPx = Math.abs(Y(p.rows[0].bottom) - Y(p.rows[0].top));
      const px = rowNumberPx(rowPx > 0 ? paneH / rowPx : NaN, st.rowNumberMax) ? rowNumberFont(rowPx) : null;
      diag.push(`row ${Math.round(rowPx)}px -> ${rowPx > 0 ? Math.round(paneH / rowPx) : '?'} rows on screen, font ${px || 'hidden'}`);
      if (!px) continue;
      ctx.font = bv.font(args, { size: px }).css;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.lineJoin = 'round';
      ctx.lineWidth = 3;
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.75)';
      ctx.fillStyle = st.rowNumberColor;
      // Pinned to the pane's left edge once the profile's start scrolls off screen.
      const x = Math.max(X(p.from), 0) + 3;
      for (const r of p.rows) {
        const y = Y(r.bottom + p.rh * 0.5);
        if (!Number.isFinite(y) || y < -px || y > paneH + px) continue;
        const txt = volumeText(r.vol);
        ctx.strokeText(txt, x, y);
        ctx.fillText(txt, x, y);
      }
    }
    // One line in the indicator's Log tab whenever the row-number state changes.
    const diagText = `[Benzo VP] row numbers: mode ${st.rowNumbersMode}, pane ${Math.round(paneH)}px, ${visProfiles.length} profile(s) in view, ${diag.length} numbered${diag.length ? ` (${diag.join('; ')})` : ''}`;
    if (diagText !== lastDiag) {
      lastDiag = diagText;
      try { console.log(diagText); } catch (e) { /* no console */ }
    }

    if (st.zones.length) {
      ctx.lineWidth = 1;
      ctx.font = bv.font(args, { size: 10 }).css;
      ctx.textAlign = 'right';
      ctx.textBaseline = 'bottom';
      for (const z of st.zones) {
        const y1 = Math.round(Y(z.hi)) + 0.5;
        const y2 = Math.round(Y(z.lo)) + 0.5;
        const x0 = Math.max(0, X(z.fromIndex) - bv.halfBar(args, z.fromIndex));
        if (!Number.isFinite(y1) || !Number.isFinite(y2) || !Number.isFinite(x0) || x0 >= paneW) continue;
        ctx.strokeStyle = z.line;
        ctx.setLineDash(z.dash);
        ctx.beginPath();
        ctx.moveTo(x0, y1);
        ctx.lineTo(paneW, y1);
        ctx.moveTo(x0, y2);
        ctx.lineTo(paneW, y2);
        ctx.stroke();
        ctx.fillStyle = z.line;
        ctx.fillText(`${z.label} ${bv.priceText(args, z.lo)} – ${bv.priceText(args, z.hi)}${z.suffix}`, paneW - 6, y1 - 2);
      }
      ctx.setLineDash([]);
    }

    ctx.restore();
    return true;   // VWAP figure is painted above; keep it only for the legend and price tag
  },
};
