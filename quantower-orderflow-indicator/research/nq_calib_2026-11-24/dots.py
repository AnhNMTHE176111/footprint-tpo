"""Luật chấm Bid/Ask (giống CellBigLogic.Evaluate): xét riêng từng bên, v >= k x B_med, v >= sàn, lớn hơn hẳn mọi tick khác trong ±w, che xanh cách đỏ <= h tick."""
import sys, pandas as pd, numpy as np
def neigh_max(F, col, w):
    idx = pd.Series(F[col].values, index=pd.MultiIndex.from_arrays([F.t.values, F.tk.values]))
    mx = np.zeros(len(F))
    for o in list(range(-w, 0)) + list(range(1, w + 1)):
        j = pd.MultiIndex.from_arrays([F.t.values, F.tk.values + o])
        mx = np.maximum(mx, idx.reindex(j).fillna(0).values)
    return mx
_cache = {}
def dots(F, k, w, floor, h, key=None):
    out = []
    for col, c in (('ask', 'B'), ('bid', 'S')):
        ck = (key, col, w)
        if key is None or ck not in _cache: _cache[ck] = neigh_max(F, col, w) if w > 0 else np.zeros(len(F))
        nm = _cache[ck]; v = F[col].values
        m = (v >= np.maximum(k * F.B_med.values, floor)) & (v > nm) & F.B_med.notna().values
        H = F.loc[m, ['t', 'tk', col]].rename(columns={col: 'v'}); H['col'] = c; out.append(H)
    R = pd.concat(out, ignore_index=True)
    if h >= 0:
        red = R[R.col == 'S'][['t', 'tk']].rename(columns={'tk': 'rtk'})
        b = R[R.col == 'B'].reset_index().merge(red, on='t', how='left')
        hidden = b[(b.rtk - b.tk).abs() <= h]['index'].unique()
        R = R.drop(index=hidden)
    return R
