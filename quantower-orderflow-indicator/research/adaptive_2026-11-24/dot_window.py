"""Câu B: mức nền 20 nến bị trễ qua phiên ở khung lớn. Thử cửa sổ nền ngắn hơn (N nến) và nền pha với chính nến đang xét.
Chạy: python dot_window.py"""
import numpy as np, pandas as pd
from dot_measure import load, measure, TFS
from dot_rule import params_for, MIN_BARS
pd.set_option('display.width', 250)
CUR = {'GC': dict(k=2.8, D=0, wmin=4, hfix=6), 'NQ': dict(k=3.5, D=14, wmin=8, hfix=12)}
rows = []
for sym in ('GC', 'NQ'):
    for m in (5, 15, 30, 60):
        for N in (20, 10, 7, 5):
            r, _ = measure(sym, m, dict(CUR[sym], N=N)); r['nen_nen'] = N; r['gio_nen'] = round(N * m / 60, 1); rows.append(r)
print(pd.DataFrame(rows).drop(columns=['do', 'xanh']).to_string(index=False))
