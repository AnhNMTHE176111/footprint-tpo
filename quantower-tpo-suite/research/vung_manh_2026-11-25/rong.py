#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rong.py — chọn ĐỘ RỘNG vùng: với mỗi nửa bề rộng h (×U) quanh tâm vùng, bao nhiêu % điểm đảo chiều rơi vào trong,
so với vùng dời; kèm tỉ lệ khớp lệnh chờ ở mép gần và kết quả 1:2. Thêm: hình dạng profile ngày (chữ D chiếm bao nhiêu)."""
import sys
import numpy as np
import pandas as pd
from an import turn_offset, trade
from final_an import load, BUF
from vm import Data
import vung_manh as V

tag = sys.argv[1] if len(sys.argv) > 1 else 'goc'
res, df = load(tag)
A, F, C = res['A'], res['F'], res['C']
t = ((df['typ'] == 'that') & (df['ngroup'] >= 1)).values
d = (df['typ'] == 'doi').values
off = df['off'].values
print('| nửa bề rộng h (×U) | bề rộng cả vùng ≈ giá khi U = 13,4 | vùng thật: % điểm đảo trong ±h | vùng dời: % | thật: % khớp lệnh ở mép gần | thật: thắng 1:2 % / R | dời: thắng 1:2 % / R |')
print('|---|---|---|---|---|---|---|')
for h in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50):
    f, r, rr = trade(A, F, C, h, BUF, 2.0)
    def wr(m):
        mm = m & f
        dec = mm & (r != 0)
        return '%.1f / %+.3f' % (100 * (r[dec] == 1).mean(), rr[mm].mean())
    print('| %.2f | %.1f | %.1f | %.1f | %.0f | %s | %s |' % (h, 2 * h * 13.4, 100 * (np.abs(off[t]) <= h).mean(), 100 * (np.abs(off[d]) <= h).mean(),
                                                       100 * f[t].mean(), wr(t), wr(d)))
# trong số các lần giá ĐÃ đảo chiều quanh vùng (|off| <= 0,75 U): cần h bao nhiêu để phủ 50/70/80%?
for nm, m in (('vùng thật', t), ('vùng dời', d)):
    x = np.abs(off[m]); x = x[~np.isnan(x) & (x <= 0.75)]
    print(nm, ': trong các lần đảo chiều cách tâm <= 0,75 U, h phủ 50/70/80%% = %s (n=%d)' % (np.percentile(x, [50, 70, 80]).round(2).tolist(), len(x)))
# điểm đảo so với MÉP vùng thật (đơn vị U): dương = đảo trước khi chạm mép gần, âm quá -2hw = thủng mép xa
x = (off[t] - df['hw'].values[t]); x = x[~np.isnan(x)]
print('vùng thật: điểm đảo so với mép gần (×U) pct 10/25/50/75/90:', np.percentile(x, [10, 25, 50, 75, 90]).round(2).tolist())

D = Data()
pp, vf = [], []
for a, b in D.days:
    if b - a + 1 < 20: continue
    st = V.profile_stats(D, a, b)
    if st: pp.append(st['poc_pos']); vf.append(st['va_frac'])
pp, vf = np.array(pp), np.array(vf)
print('profile ngày: vị trí POC trong biên độ pct 10/50/90 =', np.percentile(pp, [10, 50, 90]).round(2).tolist(),
      '| (VAH−VAL)/biên độ pct 10/50/90 =', np.percentile(vf, [10, 50, 90]).round(2).tolist())
print('chữ D (POC trong 30–70%% biên độ VÀ vùng giá trị <= 60%% biên độ): %.0f%% số phiên' % (100 * ((pp >= 0.3) & (pp <= 0.7) & (vf <= 0.6)).mean()))
