"""Fable xem nhanh (chưa gộp vòng sát nhau): luật hiện tại (1% của 240 phút) so với 'lớn thứ K*D trong D ngày số liệu'. python bw0_quick.py"""
import pandas as pd, numpy as np, sys
from collections import deque
D = r'C:\Users\anhla\AppData\Roaming\OrderFlowBubbles\bigtrade-log'
def load(name):
    d = pd.read_csv(D + '/' + name).drop_duplicates(['time_ticks', 'price'], keep='last')
    d['t'] = pd.to_datetime(d.time_iso.str[:19]); return d.sort_values(['t', 'price'])
def run(d, m, rule):
    bars = [(t, g.mot.values.astype(int)) for t, g in d.groupby('t')]
    H = np.zeros(4096, int); q = deque(); n = 0; out = []
    kind, a, b = rule
    nb = max(5, round((240 if kind == 'pct' else a * 1380) / m))
    for i, (t, v) in enumerate(bars):
        thr = None
        if kind == 'pct' and n >= 500:
            K = max(1, int(np.floor(n / 100 + .5))); c = np.cumsum(H[::-1]); thr = 4095 - int(np.searchsorted(c, K))
        if kind == 'rank' and len(q) >= round(1380 / m):      # cần ít nhất 1 ngày số liệu
            K = max(1, int(np.floor(b * len(q) * m / 1380 + .5))); c = np.cumsum(H[::-1]); thr = 4095 - int(np.searchsorted(c, K))
        if thr is not None:
            for x in v[v > thr]: out.append((t, int(x), thr))
        q.append(v); np.add.at(H, np.minimum(v, 4095), 1); n += len(v)
        if len(q) > nb:
            o = q.popleft(); np.add.at(H, np.minimum(o, 4095), -1); n -= len(o)
    o = pd.DataFrame(out, columns=['t', 'mot', 'thr'])
    ndays = len(bars) * m / 1380
    return o, ndays
for name, m in (('_GC_XCEC_Time_1Minute.csv', 1), ('_GC_XCEC_Time_5Minute.csv', 5), ('_NQZ26_XCME_Time_1Minute.csv', 1), ('_NQZ26_XCME_Time_15Minute.csv', 15)):
    d = load(name)
    for rule in (('pct', 0, 0), ('rank', 5, 5), ('rank', 5, 10), ('rank', 5, 20), ('rank', 1, 10), ('rank', 10, 10)):
        o, nd = run(d, m, rule)
        if not len(o): print(name, rule, 'khong vong'); continue
        print(f"{name[:22]:22s} M{m:<2d} {str(rule):18s} vong/ngay {len(o)/nd:7.1f}  nguong p10/p50/p90 {o.thr.quantile(.1):.0f}/{o.thr.quantile(.5):.0f}/{o.thr.quantile(.9):.0f}"
              f"  co vong p10/p50 {o.mot.quantile(.1):.0f}/{o.mot.quantile(.5):.0f}  nho nhat {o.mot.min()}")
