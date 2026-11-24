"""Câu B: khoảng che chấm xanh gần chấm đỏ (h) trong công thức chung. h = 1,5 w che quá nhiều chấm xanh ở khung lớn.
So tỉ lệ chấm đỏ và mật độ với h = round(hmult x w) và h = max(6, round(hmult x w)). Chạy: python dot_hide.py"""
import numpy as np, pandas as pd
from dot_measure import load, TFS
from dot_grid import build, nbase
from dot_rule import dots_fast
pd.set_option('display.width', 250)
rows = []
for hm, hmin in ((1.5, 0), (1.0, 0), (0.75, 0), (0.5, 6), (0.5, 0), (0.0, 6)):
    r = dict(che=f'max({hmin}, {hm} x w)')
    for sym in ('GC', 'NQ'):
        for m in TFS:
            F, S = load(sym, m); thr, w, h = build(S, m, k=2.8, wmode='lin', c=6, wmin=4, hmult=hm, floor=9)
            h = np.maximum(h, hmin); ok = thr.notna(); D = dots_fast(F, thr, w, h)
            r[f'{sym}{m}'] = f'{len(D) / ok.sum():.2f} ({(D.col == "S").mean() * 100:.0f}%)'
    rows.append(r); print(r, flush=True)
print(pd.DataFrame(rows).to_string(index=False))
