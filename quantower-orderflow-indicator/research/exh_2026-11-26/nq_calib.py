"""Hiệu chỉnh khung hình NQ của buổi Meet (jpg 1600x900 phóng 1,2 lần như bộ GC): khe nến -> phút, y -> giá. Ghi nq_calib.json."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '..')
from bubble_common import candles, slots, fit
from PIL import Image
FR = '../../../corven-meet/2026-11-07/frames/'
B = pd.read_csv('../../../data-export/data-footprint/fp_NQZ26_XCME_Time_20260826-20261124_90d_bars.csv', parse_dates=['datetime'])
B = B[(B.datetime >= '2026-11-05') & (B.datetime < '2026-11-07 12:00')].reset_index(drop=True)
res = {}
for n in sys.argv[1:]:
    im = Image.open(FR + n + '.jpg').convert('RGB').resize((1920, 1080), Image.LANCZOS)
    out = []
    for x1 in (1180, 1270, 1360):
        for y1 in (700, 750):
            try:
                c = candles(im, 60, x1, 275, y1, minlen=6); x0, s, d = slots(c); best, kmin = fit(d, B, 275, y1)
            except Exception as e: print(n, 'ERR', e); continue
            out.append((best[0][0], x1, y1, x0, s, len(d), best[0][1], kmin, best[0][2], best[0][3], best[1][0]))
    out.sort(); o = out[0]
    t0 = B.datetime.iloc[0] + pd.Timedelta(minutes=int(o[6]))
    print(n, 'cost %.2f next %.2f x1=%d y1=%d x0=%.1f s=%.2f nslots=%d n0=%d kmin=%d first=%s a=%.1f bb=%.4f' % (o[0], o[10], o[1], o[2], o[3], o[4], o[5], o[6], o[7], t0, o[8], o[9]))
    res[n] = dict(cost=o[0], x1=o[1], y1=o[2], x0=o[3], s=o[4], n0=int(o[6]), kmin=int(o[7]), a=o[8], bb=o[9], t_first=str(B.datetime.iloc[0]))
json.dump(res, open('nq_calib.json', 'w'), indent=1)
