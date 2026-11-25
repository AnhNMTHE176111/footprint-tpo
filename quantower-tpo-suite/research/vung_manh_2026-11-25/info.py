# -*- coding: utf-8 -*-
"""info.py — tổng quan dữ liệu: số phiên/tuần/chỗ nối, đơn vị biến động U, sai khác VWAP, mật độ điểm va đập."""
from vm import *
import pandas as pd

D = Data()
print('M30', D.n, 'phiên', len(D.days), 'tuần', len(D.weeks), 'chỗ nối', len(D.splices))
t = pd.to_datetime(D.m30['t'])
print('từ', t[0], 'đến', t[-1])
for s in D.splices:
    print('  nối', t[s], round(D.m30['o'][s] - D.m30['c'][s - 1], 1))
nb = np.array([b - a + 1 for a, b in D.days])
print('nến/phiên pct 1/5/25/50/95', np.percentile(nb, [1, 5, 25, 50, 95]), 'phiên <20 nến:', (nb < 20).sum())
u = D.unit_day
yrs = t[[a for a, b in D.days]].year
for y in (2024, 2025, 2026):
    px = np.median(D.m30['c'][[a for (a, b), yy in zip(D.days, yrs) if yy == y]])
    print(y, 'U trung vị', np.nanmedian(u[yrs == y]).round(2), 'p10/p90', np.nanpercentile(u[yrs == y], [10, 90]).round(2), 'giá', px)
vol = np.array([D.m30['v'][a:b + 1].sum() for a, b in D.days])
print('vol/phiên pct 1/5/25/50', np.percentile(vol, [1, 5, 25, 50]))
d = []
for a, b in D.days[-80:]:
    m1, s1 = D.vwap_sigma(a, b); m2, s2 = D.vwap_typical(a, b); d.append((m1 - m2, s1 - s2, s1))
d = np.array(d)
print('VWAP chính xác − điển hình M30: |lệch| trung vị/p90', np.median(abs(d[:, 0])).round(2), np.percentile(abs(d[:, 0]), 90).round(2),
      '| sigma lệch trung vị', np.median(d[:, 1]).round(2), '| sigma trung vị', np.median(d[:, 2]).round(2))
for (r, k) in ((0.75, 2), (1.0, 2), (1.5, 2), (1.0, 3)):
    pv = pivots(D, k=k, r=r)
    print('va đập r', r, 'k', k, len(pv), 'mỗi phiên', round(len(pv) / len(D.days), 2), 'trễ xác nhận TB (nến)', (pv['conf'] - pv['idx']).mean().round(2))
