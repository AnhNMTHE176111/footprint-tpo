"""Câu B: quét công thức chung cho chấm (mọi mã, mọi khung).
  nền: N nến trước, N = nbase(phút nến) = min(20, max(5, round(120 / phút)))   (cửa sổ nền ~2 giờ ở khung lớn)
  w = max(wmin, round(c x sqrt(R)))  [wmode='sqrt']   hoặc   max(wmin, round(R / D))  [wmode='lin']
  h = max(hmin, round(hmult x w));  ngưỡng = max(k x B, sàn)
Chạy: python dot_grid.py  -> out_dot_grid.csv"""
import sys, itertools, numpy as np, pandas as pd
from bt_common import ses_of, SES
from dot_measure import load, TFS
from dot_rule import dots_fast, MIN_BARS

def nbase(m, win=120): return int(min(20, max(5, np.floor(win / m + 0.5))))

def build(S, m, k, wmode, c, wmin, hmult, floor, N=None, hmin=0):
    N = N or nbase(m)
    B = S.med.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    R = S.rng.shift(1).rolling(N, min_periods=MIN_BARS).mean()
    ok = B.notna() & (B > 0)
    raw = c * np.sqrt(R) if wmode == 'sqrt' else R / c
    w = np.maximum(wmin, np.floor(raw + 0.5)).where(ok)
    h = np.maximum(hmin, np.floor(hmult * w + 0.5))
    thr = np.maximum(k * B, floor).where(ok)
    return thr, w, h

def density(sym, m, **kw):
    F, S = load(sym, m); thr, w, h = build(S, m, **kw); ok = thr.notna()
    Dt = dots_fast(F, thr, w, h)
    per = Dt.groupby('t').size().reindex(S.index[ok], fill_value=0); ses = ses_of(per.index)
    red = (Dt.col == 'S').sum() / max(len(Dt), 1)
    return per.mean(), {s: per.values[ses == s].mean() for s in SES}, red, Dt

if __name__ == '__main__':
    rows = []
    combos = [dict(k=k, wmode='sqrt', c=c, wmin=3, hmult=1.5, floor=fl) for k in (2.8, 3.0, 3.2, 3.5) for c in (0.8, 1.0, 1.2) for fl in (9,)]
    combos += [dict(k=k, wmode='lin', c=D, wmin=4, hmult=1.5, floor=9) for k in (2.8, 3.2, 3.5) for D in (6, 10, 14)]
    for kw in combos:
        rr = dict(kw)
        for sym in ('GC', 'NQ'):
            for m in TFS:
                a, bs, red, _ = density(sym, m, **kw)
                rr[f'{sym}{m}'] = round(a, 2)
                if m in (1, 15): rr[f'{sym}{m}_A/Au/My'] = '/'.join(f'{bs[s]:.2f}' for s in SES)
        v = np.array([rr[f'{s}{m}'] for s in ('GC', 'NQ') for m in TFS]); rr['max/min'] = round(v.max() / v.min(), 2)
        rows.append(rr); print(rr, flush=True)
    pd.DataFrame(rows).to_csv('out_dot_grid.csv', index=False)
