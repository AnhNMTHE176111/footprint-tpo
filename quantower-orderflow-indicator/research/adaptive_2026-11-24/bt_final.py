"""Câu A: bảng trước/sau của Big Trade theo mã x khung x phiên, luật chốt:
N = nbase(phút) nến có số liệu liền trước; K = round(mật độ x N); ngưỡng = max(sàn, giá trị lớn thứ K); gộp vòng cách <= max(2, round(R/8)) tick; tối đa 3 vòng/nến.
Chạy: python bt_final.py"""
import numpy as np, pandas as pd
from bt_common import *
from bt_rule import simulate
from bt_measure import TFS
from bt_grid import row
from common_window import nbase
pd.set_option('display.width', 250)
rows = []
for key in ('NQ', 'GC', 'GClive'):
    d = load_m1(key)
    for m in TFS:
        c = to_tf(d, m)
        if key == 'GClive':
            if m > 15: continue
            if m > 1: n1 = d.groupby(d.t.dt.floor(f'{m}min')).t.nunique(); c = c[c.t.isin(n1[n1 == m].index)]
        b = bars_of(c); N = nbase(m)
        rows.append(dict(ma=key, N=N, **row('cố định 10 (hiện tại)', c[c.mot >= 10], pd.Series(10.0, index=b.t.values), b, m)))
        for name, kw in (('thích nghi 1,0 · sàn 5 · gộp · tối đa 3 (CHỐT)', dict(density=1.0, floor=5, cap=3, div=8, gmin=2)),
                         ('thích nghi 1,0 · sàn 5 · không gộp/giới hạn', dict(density=1.0, floor=5, cap=0, div=0, gmin=0)),
                         ('thích nghi 0,75 · sàn 5 · gộp · tối đa 3', dict(density=0.75, floor=5, cap=3, div=8, gmin=2)),
                         ('thích nghi 1,0 · sàn 10 · gộp · tối đa 3', dict(density=1.0, floor=10, cap=3, div=8, gmin=2))):
            h, thr = simulate(c, b, N=N, **kw); rows.append(dict(ma=key, N=N, **row(name, h, thr, b, m)))
R = pd.DataFrame(rows); R.to_csv('out_bt_final.csv', index=False); print(R.to_string(index=False))
