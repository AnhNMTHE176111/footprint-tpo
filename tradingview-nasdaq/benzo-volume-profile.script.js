// Benzo Volume Profile — Settings: Overlay ON (main chart), Precision = symbol's.
// Session volume profile (built from lower-timeframe bars so the POC is the same on M1 / M15)
// plus an anchored VWAP with three optional standard-deviation bands.

const ANCHOR_TF = { '1h': '60', '4h': '240', '1D': '1D', '1W': '1W', '1M': '1M' };
const RES_MS = { '1m': 60000, '5m': 300000, '15m': 900000, '30m': 1800000, '1h': 3600000 };
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

function priceSource(name) {
  switch (name) {
    case 'close': return (b) => b.close;
    case 'open': return (b) => b.open;
    case 'high': return (b) => b.high;
    case 'low': return (b) => b.low;
    case 'hl2': return (b) => (b.high + b.low) / 2;
    case 'ohlc4': return (b) => (b.open + b.high + b.low + b.close) / 4;
    case 'hlcc4': return (b) => (b.high + b.low + b.close + b.close) / 4;
    default: return (b) => (b.high + b.low + b.close) / 3;
  }
}

// First chart-bar index of every anchor period (Pine timeframe.change), from the
// timestamp of the higher-timeframe bar that contains each chart bar.
function periodStarts(keys, n) {
  const starts = [0];
  let last = keys[0];
  for (let i = 1; i < n; i++) {
    const k = keys[i];
    if (k === undefined || k === null) continue;
    if (last !== undefined && last !== null && k !== last) starts.push(i);
    last = k;
  }
  return starts;
}

function anchorKeys(label) {
  return bv.security({ timeframe: ANCHOR_TF[label] || '1D', lookahead: true }, (bars) => bars.map((b) => b.timestamp));
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

function buildProfile(dataList, ltf, s, e, o) {
  // Pass 1: session high / low from the profile-resolution bars.
  let top = -Infinity;
  let bot = Infinity;
  for (let i = s; i <= e; i++) {
    const intra = ltf ? ltf[i] : null;
    if (intra && intra.length) {
      for (let k = 0; k < intra.length; k++) {
        if (intra[k].high > top) top = intra[k].high;
        if (intra[k].low < bot) bot = intra[k].low;
      }
    } else {
      if (dataList[i].high > top) top = dataList[i].high;
      if (dataList[i].low < bot) bot = dataList[i].low;
    }
  }
  if (!Number.isFinite(top) || !Number.isFinite(bot)) return null;

  // Pass 2: spread each bar's volume evenly over the rows its high-low range touches.
  const rows = o.rows;
  const rh = (top - bot) / rows;
  const vr = new Float64Array(rows);
  const dr = new Float64Array(rows);
  const addBar = (b) => {
    const v = b.volume;
    if (!Number.isFinite(v)) return;
    // Clamp into [0, rows-1]: a bar touching the session top maps to bin == rows.
    const rB = Math.min(rows - 1, Math.max(0, Math.floor((b.low - bot) / rh)));
    const rT = Math.min(rows - 1, Math.max(0, Math.floor((b.high - bot) / rh)));
    const ve = v / (rT - rB + 1);
    const isDown = b.close < b.open;
    for (let r = rB; r <= rT; r++) {
      vr[r] += ve;
      if (isDown) dr[r] += ve;
    }
  };
  if (rh > 0) {
    for (let i = s; i <= e; i++) {
      const intra = ltf ? ltf[i] : null;
      if (intra && intra.length) {
        for (let k = 0; k < intra.length; k++) addBar(intra[k]);
      } else {
        addBar(dataList[i]);
      }
    }
  }

  const { pIdx, up, dn } = valueAreaOf(vr, o.valueArea);
  const maxV = vr[pIdx];
  const nBars = e - s + 1;
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
        sellFill: rgba(o.sellRgb, alpha),
        buyFill: rgba(o.buyRgb, alpha),
      });
    }
  }
  const poc = bot + (pIdx + 0.5) * rh;
  return { from: s, to: e, right: Math.max(e, s + wMax), wMax, rows: rowList, poc, pocTop: poc + rh * 0.5, pocBot: poc - rh * 0.5 };
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

// Volume clusters of one profile window. The profile is cut into clusters at its LVN valleys;
// a cluster counts as an HVN when it is a well-formed auction: a large share of the week's
// volume, price accepted there for a good part of the week, and a D-shaped bulge (peak in the
// body, volume tapering to both sides). The zone drawn is the cluster's dense core.
// The POC cluster is always kept (CORVEN: the POC is an HVN too).
function detectHvnZones(h, l, v, from, to, unit, rowFrac = HVN.rowFrac, minRows = HVN.minRows) {
  if (to - from < 30 || !(unit > 0)) return [];
  let top = -Infinity;
  let bot = Infinity;
  for (let k = from; k < to; k++) {
    if (h[k] > top) top = h[k];
    if (l[k] < bot) bot = l[k];
  }
  if (!(top > bot)) return [];
  let rowSize = Math.min(unit * rowFrac, (top - bot) / minRows);
  let rows = Math.ceil((top - bot) / rowSize);
  if (rows > HVN.maxRows) { rows = HVN.maxRows; rowSize = (top - bot) / rows; }
  // Rows sit on a fixed price grid, so a new week low does not shift every row.
  bot = Math.floor(bot / rowSize) * rowSize;
  rows = Math.ceil((top - bot) / rowSize);
  if (rows < 8) return [];

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
  if (!(total > 0)) return [];
  const sm = smoothProfile(vr, HVN.smoothSigma);
  let pocRow = 0;
  for (let r = 1; r < rows; r++) if (sm[r] > sm[pocRow]) pocRow = r;

  // 1. Cluster peaks: local maxima with a real dip (LVN) on both sides.
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

  // 2. Cut the profile at the lowest row between neighbouring peaks.
  const cuts = [0];
  for (let i = 1; i < peaks.length; i++) {
    let m = peaks[i - 1];
    for (let j = peaks[i - 1]; j <= peaks[i]; j++) if (sm[j] < sm[m]) m = j;
    cuts.push(m);
  }
  cuts.push(rows - 1);

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
      lo: bot + a * rowSize, hi: bot + (b + 1) * rowSize, peak: bot + (r + 0.5) * rowSize,
      vol: segVol, volShare: segVol / total, shape: segVol > 0 ? below / segVol : 0.5, isPoc: r === pocRow, timeShare: 0,
      peakOfPoc: p / sm[pocRow], peakedness: p / (bodySum / bodyRows), coreOfBody: coreRows / bodyRows,
      taper: Math.min(r - ba, bb - r) / Math.max(1, r - ba, bb - r),
    });
  }

  // 3. Time accepted inside each core (share of the window's bars that traded there).
  const bars = to - from;
  for (let k = from; k < to; k++) {
    for (const z of cands) if (l[k] <= z.hi && h[k] >= z.lo) z.timeShare += 1 / bars;
  }

  for (const z of cands) z.score = z.volShare + z.timeShare;
  // Every cluster, the POC one included, must be a finished D-shaped auction to be drawn.
  return cands.filter((z) => isDShaped(z) && (z.isPoc || (
    z.volShare >= HVN.minVolShare && z.timeShare >= HVN.minTimeShare && z.peakOfPoc >= HVN.minPeakOfPoc
  )));
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
// ==HVN-CORE-END==

// Profile-resolution bars of chart bars [s, e) as flat arrays (chart bar when no intrabars).
// dropLast leaves out the newest (still forming) bar, so HVN zones are built from closed
// 1-minute bars only and come out the same on M1, M5, M15...
function flattenBars(dataList, ib, s, e, dropLast = false) {
  let size = 0;
  for (let i = s; i < e; i++) size += ib && ib[i] && ib[i].length ? ib[i].length : 1;
  if (dropLast && size > 0) size--;
  const f = { h: new Float64Array(size), l: new Float64Array(size), v: new Float64Array(size), t: new Float64Array(size), chartStart: new Int32Array(Math.max(1, e - s)) };
  let k = 0;
  const put = (b) => { if (k < size) { f.h[k] = b.high; f.l[k] = b.low; f.v[k] = b.volume; f.t[k] = b.timestamp; k++; } };
  for (let i = s; i < e; i++) {
    f.chartStart[i - s] = k;
    const intra = ib ? ib[i] : null;
    if (intra && intra.length) for (let j = 0; j < intra.length; j++) put(intra[j]);
    else put(dataList[i]);
  }
  return f;
}

// Open time of the newest closed profile-resolution bar.
function lastClosedTime(dataList, ib) {
  const n = dataList.length;
  const last = ib ? ib[n - 1] : null;
  if (last && last.length > 1) return last[last.length - 2].timestamp;
  if (n < 2) return 0;
  const prev = ib ? ib[n - 2] : null;
  return prev && prev.length ? prev[prev.length - 1].timestamp : dataList[n - 2].timestamp;
}

function intrabarCount(ib, s, e) {
  let c = 0;
  for (let i = s; i < e; i++) c += ib && ib[i] ? ib[i].length : 0;
  return c;
}

// Intrabars of chart bars [from, n). A closed bar keeps the intrabars it had once loaded, so a
// momentary gap in the lower-timeframe feed does not reshape the profile for one tick.
function stableIntrabars(dataList, ltf, from, cache) {
  const n = dataList.length;
  const out = new Array(n);
  for (let i = from; i < n; i++) {
    const ts = dataList[i].timestamp;
    const a = ltf[i];
    if (a && a.length) {
      out[i] = a;
      if (i < n - 1) cache.set(ts, a);
    } else if (cache.has(ts)) {
      out[i] = cache.get(ts);
    }
  }
  if (cache.size > 2 * (n - from) + 100) {
    const keepFrom = dataList[from].timestamp;
    for (const ts of cache.keys()) if (ts < keepFrom) cache.delete(ts);
  }
  return out;
}

// HVN zones of the current and the previous week, merged. They are rebuilt only when a chart bar
// closes (the forming bar is left out), on one row grid sized from the finished previous week,
// so they do not jitter tick by tick. Side follows the live price: zone above price = sell,
// below = buy, price inside = not tradable yet (CORVEN).
function buildHvn(dataList, ib, weekKeys, cache) {
  const n = dataList.length;
  const starts = periodStarts(weekKeys, n);
  const curStart = starts[starts.length - 1];
  const prevStart = starts.length > 1 ? starts[starts.length - 2] : curStart;
  const key = `W|${dataList[prevStart].timestamp}|${lastClosedTime(dataList, ib)}|${intrabarCount(ib, prevStart, n)}`;
  if (cache.hvnKey !== key) {
    const f = flattenBars(dataList, ib, prevStart, n, true);
    const total = f.h.length;
    const curFrom = Math.min(total, f.chartStart[curStart - prevStart]);
    const unit = hourlyRangeUnit(f.h, f.l, f.t, 0, curFrom > 0 ? curFrom : total);
    const zones = [];
    // fromIndex holds 0 = previous week, 1 = current week until mapped to chart bars below.
    if (curFrom > 0) for (const z of detectHvnZones(f.h, f.l, f.v, 0, curFrom, unit)) zones.push({ ...z, fromIndex: 0 });
    for (const z of detectHvnZones(f.h, f.l, f.v, curFrom, total, unit)) zones.push({ ...z, fromIndex: 1 });
    cache.hvnKey = key;
    cache.hvnZones = mergeHvnZones(zones, unit);
  }
  const price = dataList[n - 1].close;
  return cache.hvnZones.map((z) => ({
    ...z,
    fromIndex: z.fromIndex === 0 ? prevStart : curStart,
    side: z.hi < price ? 1 : z.lo > price ? -1 : 0,
  }));
}

// Daily HVN zones from the last `nDays` finished days plus today (closed bars only), rebuilt
// when a chart bar closes. One row grid sized from the finished days keeps them steady.
function buildHvnDay(dataList, ib, dayStarts, nDays, cache) {
  const n = dataList.length;
  const first = Math.max(0, dayStarts.length - 1 - nDays);
  const base = dayStarts[first];
  const curStart = dayStarts[dayStarts.length - 1];
  const key = `D|${dataList[base].timestamp}|${lastClosedTime(dataList, ib)}|${intrabarCount(ib, base, n)}`;
  if (cache.hvnKey !== key) {
    const f = flattenBars(dataList, ib, base, n, true);
    const total = f.h.length;
    const at = (i) => Math.min(total, f.chartStart[i - base]);
    const doneEnd = at(curStart);
    const unit = hourlyRangeUnit(f.h, f.l, f.t, 0, doneEnd > 0 ? doneEnd : total);
    const zones = [];
    // fromIndex holds the day's offset from `first` until mapped to chart bars below.
    for (let d = first; d < dayStarts.length; d++) {
      const a = at(dayStarts[d]);
      const b = d + 1 < dayStarts.length ? at(dayStarts[d + 1]) : total;
      for (const z of detectHvnZones(f.h, f.l, f.v, a, b, unit, HVN.dayRowFrac, HVN.dayMinRows)) zones.push({ ...z, fromIndex: d - first });
    }
    cache.hvnKey = key;
    cache.hvnZones = pickReputableZones(zones, unit);
  }
  const price = dataList[n - 1].close;
  return cache.hvnZones.map((z) => ({
    ...z,
    fromIndex: dayStarts[Math.min(dayStarts.length - 1, first + z.fromIndex)],
    side: z.hi < price ? 1 : z.lo > price ? -1 : 0,
  }));
}

function buildVwap(dataList, keys, o, res) {
  const n = dataList.length;
  const starts = periodStarts(keys, n);
  const firstKept = Math.max(0, starts.length - 1 - o.vwapKeep);
  const base = starts[firstKept];
  const m = new Float64Array(n - base).fill(NaN);
  const sd = new Float64Array(n - base).fill(NaN);
  const src = priceSource(o.vwapSrc);
  let next = 1;
  let sV = 0;
  let sPV = 0;
  let sP2V = 0;
  for (let i = 0; i < n; i++) {
    if (next < starts.length && starts[next] === i) { sV = 0; sPV = 0; sP2V = 0; next++; }
    const bar = dataList[i];
    const p = src(bar);
    const v = bar.volume;
    if (Number.isFinite(p) && Number.isFinite(v)) { sV += v; sPV += p * v; sP2V += p * p * v; }
    if (sV > 0) {
      const w = sPV / sV;
      res[i] = { vwap: w };
      if (i >= base) {
        m[i - base] = w;
        sd[i - base] = Math.sqrt(Math.max(0, sP2V / sV - w * w));   // Pine ta.vwap stdev
      }
    } else {
      res[i] = {};
    }
  }
  const periods = [];
  for (let k = firstKept; k < starts.length; k++) {
    periods.push([starts[k], k + 1 < starts.length ? starts[k + 1] - 1 : n - 1]);
  }
  return { base, m, sd, periods };
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
      profileMode = 'Week', profileRows = 200, valueArea = 70, maxSessions = 5, widthPct = 1,
      maxWidthBar = 90, showLive = true, profileRes = '1m', vaBoost = 1.18,
      colBuy = '#90bff9', colSell = '#b39ddb', colDayBuy = '#c9a43c', colDaySell = '#2f5fd8', colPOC = '#5b6472', colVWAP = '#ab47bc', vwapWidth = 2,
      showVWAP = true, vwapSrc = 'hlc3', vwapAnchor = '1D', vwapKeep = 5,
      showBand1 = true, bandMult1 = 1.0, bandLine1 = '#ab47bca6', bandFill1 = '#ab47bc1a',
      showBand2 = false, bandMult2 = 2.0, bandLine2 = '#ab47bc80', bandFill2 = '#ab47bc12',
      showBand3 = false, bandMult3 = 3.0, bandLine3 = '#ab47bc59', bandFill3 = '#ab47bc0d',
      showHVN = true, hvnBuyColor = '#26a69a', hvnSellColor = '#ef5350', hvnInsideColor = '#9e9e9e',
    } = indicator.extendData?.inputs || {};
    const n = dataList.length;
    const res = new Array(n);
    for (let i = 0; i < n; i++) res[i] = {};
    if (n === 0) return res;
    if (!indicator._benzoCache) indicator._benzoCache = { intrabars: new Map(), profiles: new Map(), hvnKey: '', hvnZones: [], res: null };
    const cache = indicator._benzoCache;
    // While a data request is in flight, keep showing the last result instead of a blank frame.
    const keepLast = () => {
      const prev = cache.res;
      if (!prev) return res;
      for (let i = 0; i < n && i < prev.length; i++) res[i] = prev[i];
      return res;
    };

    const isDay = profileMode === 'Day';
    const profKeys = anchorKeys(isDay ? '1D' : '1W');
    const vwapKeys = showVWAP ? anchorKeys(vwapAnchor) : null;
    const weekKeys = showHVN && !isDay ? profKeys : null;
    // Profile from lower-timeframe bars only when that timeframe is below the chart's.
    const useLowerTf = (RES_MS[profileRes] || 60000) < bv.detectBarMs(dataList);
    const ltf = useLowerTf ? bv.securityLowerTf({ timeframe: profileRes }, (bars) => bars) : null;
    if (!profKeys || (showVWAP && !vwapKeys) || (useLowerTf && !ltf)) return keepLast();

    const o = {
      rows: Math.max(1, Math.trunc(profileRows)), valueArea, widthPct, maxWidthBar, vaBoost,
      buyRgb: isDay ? parseRgb(colDayBuy, [201, 164, 60]) : parseRgb(colBuy, [144, 191, 249]),
      sellRgb: isDay ? parseRgb(colDaySell, [47, 95, 216]) : parseRgb(colSell, [179, 157, 219]),
      vwapSrc, vwapKeep: Math.max(1, Math.trunc(vwapKeep)),
    };

    // Completed sessions (last maxSessions) plus the developing one.
    const starts = periodStarts(profKeys, n);
    const nSess = starts.length;
    const firstSess = Math.max(0, nSess - 1 - maxSessions);
    // Weekly HVN needs the previous week even when fewer sessions are kept.
    const ibFrom = showHVN && !isDay ? Math.min(starts[firstSess], starts[Math.max(0, nSess - 2)]) : starts[firstSess];
    const ib = ltf ? stableIntrabars(dataList, ltf, ibFrom, cache.intrabars) : null;
    // A finished session never changes: its profile is built once and reused on every tick.
    const profKey = [profileMode, profileRows, valueArea, widthPct, maxWidthBar, vaBoost, colBuy, colSell, colDayBuy, colDaySell, profileRes].join('|');
    const usedKeys = new Set();
    const profiles = [];
    for (let k = firstSess; k < nSess; k++) {
      const isLive = k === nSess - 1;
      if (isLive && !showLive) continue;
      const s = starts[k];
      const e = isLive ? n - 1 : starts[k + 1] - 1;
      if (isLive) {
        const p = buildProfile(dataList, ib, s, e, o);
        if (p) profiles.push(p);
        continue;
      }
      // The intrabar count is in the key so a session whose history finished loading is rebuilt.
      const key = `${dataList[s].timestamp}|${dataList[e].timestamp}|${intrabarCount(ib, s, e + 1)}|${profKey}`;
      usedKeys.add(key);
      let p = cache.profiles.get(key);
      if (p === undefined) {
        p = buildProfile(dataList, ib, s, e, o);
        cache.profiles.set(key, p);
      }
      if (p) profiles.push({ ...p, from: s, to: e, right: Math.max(e, s + p.wMax) });
    }
    for (const key of cache.profiles.keys()) if (!usedKeys.has(key)) cache.profiles.delete(key);

    const vwap = showVWAP ? buildVwap(dataList, vwapKeys, o, res) : null;
    let hvn = [];
    if (showHVN) hvn = isDay ? buildHvnDay(dataList, ib, starts, Math.max(1, Math.trunc(maxSessions)), cache) : buildHvn(dataList, ib, weekKeys, cache);
    const hvnRgb = {
      1: parseRgb(hvnBuyColor, [38, 166, 154]),
      '-1': parseRgb(hvnSellColor, [239, 83, 80]),
      0: parseRgb(hvnInsideColor, [158, 158, 158]),
    };
    for (const z of hvn) {
      const rgb = hvnRgb[z.side];
      z.fill = rgba(rgb, z.side ? 0.18 : 0.10);
      z.line = rgba(rgb, z.side ? 0.95 : 0.6);
      z.name = z.side > 0 ? 'HVN Buy' : z.side < 0 ? 'HVN Sell' : 'HVN (giá đang trong vùng)';
      z.suffix = z.days > 1 ? ` · ${z.days} ngày` : '';
    }

    const pocRgb = parseRgb(colPOC, [91, 100, 114]);
    const bands = [];
    if (showBand1) bands.push({ mult: bandMult1, line: bandLine1, fill: bandFill1 });
    if (showBand2) bands.push({ mult: bandMult2, line: bandLine2, fill: bandFill2 });
    if (showBand3) bands.push({ mult: bandMult3, line: bandLine3, fill: bandFill3 });

    indicator._benzoVP = {
      profiles,
      pocFill: rgba(pocRgb, 0.38),
      pocLine: rgba(pocRgb, 0.85),
      vwap,
      vwapColor: colVWAP,
      vwapWidth,
      bands,
      hvn,
    };
    cache.res = res;
    return res;
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

    // 1. POC lines (top layer).
    ctx.strokeStyle = st.pocLine;
    ctx.lineWidth = 4;
    ctx.beginPath();
    for (const p of visProfiles) {
      const y = Y(p.poc);
      ctx.moveTo(X(p.from), y);
      ctx.lineTo(X(p.to), y);
    }
    ctx.stroke();

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

    // 4. HVN bands across the whole pane (below the profile, above the VWAP zones).
    const { width: paneW } = bv.bounds(args);
    for (const z of st.hvn) {
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

    // HVN edge lines and labels on top of the candles, so the levels stay easy to find.
    ctx.globalCompositeOperation = 'source-over';
    if (st.hvn.length) {
      ctx.lineWidth = 1;
      ctx.font = bv.font(args, { size: 10 }).css;
      ctx.textAlign = 'right';
      ctx.textBaseline = 'bottom';
      for (const z of st.hvn) {
        const y1 = Math.round(Y(z.hi)) + 0.5;
        const y2 = Math.round(Y(z.lo)) + 0.5;
        const x0 = Math.max(0, X(z.fromIndex) - bv.halfBar(args, z.fromIndex));
        if (!Number.isFinite(y1) || !Number.isFinite(y2) || !Number.isFinite(x0) || x0 >= paneW) continue;
        ctx.strokeStyle = z.line;
        ctx.setLineDash(z.side ? [] : [4, 4]);
        ctx.beginPath();
        ctx.moveTo(x0, y1);
        ctx.lineTo(paneW, y1);
        ctx.moveTo(x0, y2);
        ctx.lineTo(paneW, y2);
        ctx.stroke();
        ctx.fillStyle = z.line;
        ctx.fillText(`${z.name} ${bv.priceText(args, z.lo)} – ${bv.priceText(args, z.hi)}${z.suffix}`, paneW - 6, y1 - 2);
      }
      ctx.setLineDash([]);
    }

    ctx.restore();
    return true;   // VWAP figure is painted above; keep it only for the legend and price tag
  },
};
