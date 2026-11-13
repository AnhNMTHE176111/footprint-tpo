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
  return { from: s, to: e, right: Math.max(e, s + wMax), rows: rowList, poc, pocTop: poc + rh * 0.5, pocBot: poc - rh * 0.5 };
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
      profileTF = '1D', profileRows = 20, valueArea = 70, maxSessions = 5, widthPct = 0.32,
      maxWidthBar = 90, showLive = true, profileRes = '1m', vaBoost = 1.18,
      colBuy = '#90bff9', colSell = '#b39ddb', colPOC = '#5b6472', colVWAP = '#ab47bc', vwapWidth = 2,
      showVWAP = true, vwapSrc = 'hlc3', vwapAnchor = '1D', vwapKeep = 5,
      showBand1 = true, bandMult1 = 1.0, bandLine1 = '#ab47bca6', bandFill1 = '#ab47bc1a',
      showBand2 = false, bandMult2 = 2.0, bandLine2 = '#ab47bc80', bandFill2 = '#ab47bc12',
      showBand3 = false, bandMult3 = 3.0, bandLine3 = '#ab47bc59', bandFill3 = '#ab47bc0d',
    } = indicator.extendData?.inputs || {};
    const n = dataList.length;
    const res = new Array(n);
    for (let i = 0; i < n; i++) res[i] = {};
    indicator._benzoVP = null;
    if (n === 0) return res;

    const profKeys = anchorKeys(profileTF);
    const vwapKeys = showVWAP ? anchorKeys(vwapAnchor) : null;
    // Profile from lower-timeframe bars only when that timeframe is below the chart's.
    const useLowerTf = (RES_MS[profileRes] || 60000) < bv.detectBarMs(dataList);
    const ltf = useLowerTf ? bv.securityLowerTf({ timeframe: profileRes }, (bars) => bars) : null;
    if (!profKeys || (showVWAP && !vwapKeys) || (useLowerTf && !ltf)) return res;   // still loading

    const o = {
      rows: Math.max(1, Math.trunc(profileRows)), valueArea, widthPct, maxWidthBar, vaBoost,
      buyRgb: parseRgb(colBuy, [144, 191, 249]), sellRgb: parseRgb(colSell, [179, 157, 219]),
      vwapSrc, vwapKeep: Math.max(1, Math.trunc(vwapKeep)),
    };

    // Completed sessions (last maxSessions) plus the developing one.
    const starts = periodStarts(profKeys, n);
    const nSess = starts.length;
    const profiles = [];
    for (let k = Math.max(0, nSess - 1 - maxSessions); k < nSess; k++) {
      const isLive = k === nSess - 1;
      if (isLive && !showLive) continue;
      const p = buildProfile(dataList, ltf, starts[k], isLive ? n - 1 : starts[k + 1] - 1, o);
      if (p) profiles.push(p);
    }

    const vwap = showVWAP ? buildVwap(dataList, vwapKeys, o, res) : null;

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
    };
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

    // 4. Band zones (bottom layer). Each zone runs from its band to the next enabled band
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

    ctx.restore();
    return true;   // VWAP figure is painted above; keep it only for the legend and price tag
  },
};
