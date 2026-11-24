"""Câu A: cửa sổ lịch sử theo khung cho Big Trade: N = min(20, max(5, round(120 / phút nến))) so với N = 20 cố định.
Chạy: python bt_window.py"""
import numpy as np, pandas as pd
from bt_common import *
from bt_rule import simulate
from bt_measure import TFS
from bt_grid import row
pd.set_option('display.width', 250)
def nbase(m, win=120): return int(min(20, max(5, np.floor(win / m + 0.5))))
for key in ('NQ', 'GC'):
    d = load_m1(key); rows = []
    for m in (15, 30, 60):
        c = to_tf(d, m); b = bars_of(c)
        for N in sorted({20, 10, nbase(m), 5}, reverse=True):
            for dens in (0.75, 1.0):
                h, thr = simulate(c, b, N=N, density=dens, floor=5, cap=3, div=8, gmin=2)
                rows.append(row(f'N={N} (K={max(1, int(np.floor(dens * N + .5)))}) d{dens}', h, thr, b, m))
    print(f'\n#### {key}'); print(pd.DataFrame(rows).to_string(index=False))
