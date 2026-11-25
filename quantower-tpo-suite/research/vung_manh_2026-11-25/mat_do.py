#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mat_do.py — mật độ vùng ĐƯỢC VẼ (sau lọc hiển thị) ở mỗi nến M30, trên toàn bộ dữ liệu."""
import numpy as np
from collections import Counter
from vm import *
import vung_manh as V

D = Data()
eng = V.Engine(D)
cnt, gold, ins, wid, above, below = [], [], [], [], [], []
for j in range(D.n - 1):
    if not np.isfinite(D.U[j + 1]) or D.seg_of[j] != D.seg_of[j + 1]: continue
    sh = V.display(D, eng.zones(j), j, float(D.m30['c'][j]))
    cnt.append(len(sh)); gold.append(sum(z['gold'] for z in sh)); ins.append(sum(z['inside'] for z in sh))
    above.append(sum(1 for z in sh if z['side'] < 0 and not z['inside'])); below.append(sum(1 for z in sh if z['side'] > 0 and not z['inside']))
    wid += [(z['hi'] - z['lo']) / z['u'] for z in sh]
cnt = np.array(cnt); gold = np.array(gold)
print('nến xét:', len(cnt))
print('số vùng được vẽ: TB %.2f · phân bố %s' % (cnt.mean(), {k: round(100 * v / len(cnt), 1) for k, v in sorted(Counter(cnt.tolist()).items())}))
print('%% thời gian có >= 1 vùng: %.0f%% · TB kháng cự (trên giá) %.2f · hỗ trợ (dưới giá) %.2f · giá đang trong vùng %.1f%% thời gian'
      % (100 * (cnt >= 1).mean(), np.mean(above), np.mean(below), 100 * (np.array(ins) >= 1).mean()))
print('%% thời gian có vùng VÀNG: %.1f%%' % (100 * (gold >= 1).mean()))
print('bề rộng vùng (×U) pct 10/50/90:', np.percentile(wid, [10, 50, 90]).round(2).tolist())
