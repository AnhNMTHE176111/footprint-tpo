"""Dung chung cho do bong CORVEN: detect nen (wick) tren anh, calib, tra data."""
import numpy as np, pandas as pd
from PIL import Image
ROOT = r"C:\Users\anhla\OneDrive\Documents\footprint-tpo"
BARS = ROOT + r"\data-export\data-footprint\fp_GCZ26_XCEC_Time_20260811-20261109_90d_bars.csv"
LVL = ROOT + r"\data-export\data-footprint\fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv"

def load_bars():
    b = pd.read_csv(BARS, parse_dates=['datetime'])
    b = b[(b.datetime >= '2026-11-04') & (b.datetime < '2026-11-08')].reset_index(drop=True)
    return b

def candles(im, x0, x1, y0, y1, gap=14, minlen=8):
    """tra ve list (xc, ytop, ybot) cua cac nen (dark vertical structures)."""
    a = np.asarray(im.convert('RGB')).astype(int)[y0:y1, x0:x1]
    dark = (a.max(axis=2) < 95)
    H, W = dark.shape
    cols = []
    for x in range(W):
        ys = np.where(dark[:, x])[0]
        if len(ys) == 0: cols.append(None); continue
        # runs merged by gap
        runs = []; s = ys[0]; p = ys[0]
        for y in ys[1:]:
            if y - p > gap: runs.append((s, p)); s = y
            p = y
        runs.append((s, p))
        runs = [r for r in runs if r[1] - r[0] + 1 >= minlen]
        cols.append(runs if runs else None)
    # cluster adjacent columns having runs overlapping
    out = []; cur = None
    for x, r in enumerate(cols):
        if r is None:
            if cur: out.append(cur); cur = None
            continue
        top = min(q[0] for q in r); bot = max(q[1] for q in r)
        if cur is None: cur = [x, x, top, bot]
        else:
            cur[1] = x; cur[2] = min(cur[2], top); cur[3] = max(cur[3], bot)
    if cur: out.append(cur)
    res = [((c[0] + c[1]) / 2 + x0, c[2] + y0, c[3] + y0, c[1] - c[0] + 1) for c in out]
    return res

def slots(c, s_lo=8, s_hi=25):
    """x0, s tu thong ke vong tren tam nen (R-max), roi gan nen vao o (slot)."""
    xs = np.array([q[0] for q in c])
    best = None
    for s in np.arange(s_lo, s_hi, 0.01):
        z = np.exp(2j * np.pi * xs / s).mean()
        if best is None or abs(z) > best[0]: best = (abs(z), s, np.angle(z) / (2 * np.pi) * s)
    R, s, ph = best
    x0 = ph + s * np.floor((xs.min() - ph) / s)
    k = np.round((xs - x0) / s)
    # tinh chinh s, x0 bang hoi quy tren inlier
    for _ in range(3):
        m = abs(xs - (x0 + s * k)) < 3
        A = np.vstack([k[m], np.ones(m.sum())]).T
        sol = np.linalg.lstsq(A, xs[m], rcond=None)[0]
        s, x0 = sol; k = np.round((xs - x0) / s)
    d = {}
    for q, kk in zip(c, k):
        if abs(q[0] - (x0 + s * kk)) > 3.5: continue
        kk = int(kk)
        if kk in d: d[kk] = (min(d[kk][0], q[1]), max(d[kk][1], q[2]))
        else: d[kk] = (q[1], q[2])
    return x0, s, d

def minute_grid(bars):
    """mang theo phut lien tuc (NaN o phut thieu trong data) - Sierra co du nen, data thi mat vai nen."""
    t0 = bars.datetime.iloc[0]
    m = ((bars.datetime - t0).dt.total_seconds() // 60).astype(int).values
    n = m.max() + 1
    H = np.full(n, np.nan); L = np.full(n, np.nan); row = np.full(n, -1)
    H[m] = bars.high.values; L[m] = bars.low.values; row[m] = np.arange(len(bars))
    return t0, H, L, row

def fit(d, bars, y0=275, y1=712):
    ks = np.array(sorted(d)); top = np.array([d[k][0] for k in ks], float); bot = np.array([d[k][1] for k in ks], float)
    top[top <= y0 + 2] = np.nan; bot[bot >= y1 - 3] = np.nan
    kmin = ks.min(); ks0 = ks - kmin
    t0, H, L, row = minute_grid(bars)
    n = len(H); span = ks0.max()
    best = []
    for m0 in range(0, n - span - 1):
        idx = m0 + ks0
        P = np.concatenate([H[idx], L[idx]]); Y = np.concatenate([top, bot])
        ok = ~np.isnan(Y) & ~np.isnan(P); P = P[ok]; Y = Y[ok]
        if len(P) < 12: continue
        m = np.ones(len(P), bool)
        for _ in range(4):
            if m.sum() < 8: break
            A = np.vstack([P[m], np.ones(m.sum())]).T
            sol = np.linalg.lstsq(A, Y[m], rcond=None)[0]
            r = abs(Y - (sol[1] + sol[0] * P))
            thr = max(np.percentile(r, 60), 3)
            m = r <= thr
        cost = np.sort(r)[:int(len(r) * .6)].mean()
        best.append((cost, m0, sol[1], sol[0]))
    best.sort()
    return best[:5], kmin

def slot_row(c, k, bars_row):
    """slot k (theo calib c) -> chi so dong trong bars, hoac None neu data thieu nen do."""
    m = c['n0'] + k - c['kmin']
    if m < 0 or m >= len(bars_row): return None
    r = bars_row[m]
    return None if r < 0 else int(r)
