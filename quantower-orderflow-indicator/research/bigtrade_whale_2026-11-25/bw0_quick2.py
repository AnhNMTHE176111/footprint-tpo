"""Fable xem nhanh lần 2 (chưa gộp vòng): luật 'lớn thứ R*D trong D ngày nến có số liệu' — vòng theo phiên, có bắt top-1/top-3 mỗi ngày không, lớn nhất phiên có nổ không. python bw0_quick2.py"""
import pandas as pd, numpy as np
from collections import deque
D = r'C:\Users\anhla\AppData\Roaming\OrderFlowBubbles\bigtrade-log'
def load(name):
    d = pd.read_csv(D + '/' + name).drop_duplicates(['time_ticks', 'price'], keep='last')
    d['t'] = pd.to_datetime(d.time_iso.str[:19])
    ct = (d.t - pd.Timedelta(hours=6)).where(d.t >= '2026-11-01 07:00', d.t - pd.Timedelta(hours=5))
    d['day'] = (ct + pd.Timedelta(hours=7)).dt.date
    h = ct.dt.hour + ct.dt.minute / 60
    d['ses'] = np.select([(h >= 17) | (h < 2), (h >= 2) & (h < 8.5)], ['A', 'Au'], 'My')
    return d.sort_values(['t', 'price']).reset_index(drop=True)
def run(d, m, days, R, warm=1.0):
    H = np.zeros(4096, int); q = deque(); nb = round(days * 1380 / m); thr_col = np.full(len(d), -1)
    for t, g in d.groupby('t', sort=True):
        v = g.mot.values.astype(int)
        if len(q) >= round(warm * 1380 / m):
            K = max(1, int(np.floor(R * len(q) * m / 1380 + .5))); c = np.cumsum(H[::-1]); thr_col[g.index] = 4095 - int(np.searchsorted(c, K))
        q.append(v); np.add.at(H, np.minimum(v, 4095), 1)
        if len(q) > nb: np.add.at(H, np.minimum(q.popleft(), 4095), -1)
    return thr_col
for name, m in (('_GC_XCEC_Time_1Minute.csv', 1), ('_NQZ26_XCME_Time_1Minute.csv', 1), ('_NQZ26_XCME_Time_15Minute.csv', 15), ('_GCZ26_XCEC_Time_1Minute.csv', 1)):
    d = load(name)
    for days, R in ((5, 5), (5, 10), (5, 15), (3, 10), (10, 10)):
        d['thr'] = run(d, m, days, R); e = d[d.thr >= 0]; r = e[e.mot > e.thr]
        nd = e.t.nunique() * m / 1380
        top = e.sort_values('mot', ascending=False).groupby('day').head(3)
        t1 = e.sort_values('mot', ascending=False).groupby('day').head(1)
        sm = e.sort_values('mot', ascending=False).groupby(['day', 'ses']).head(1)
        per = r.groupby('day').size().reindex(e.day.unique(), fill_value=0)
        print(f"{name[:20]:20s} M{m:<2d} D={days:<2d} R={R:<2d} vong/ngay {len(r)/nd:5.1f} (ngay it/nhieu nhat {per.min()}/{per.max()}) "
              f"theo phien A/Au/My {dict(r.ses.value_counts())}  nguong {e.thr.quantile(.1):.0f}/{e.thr.median():.0f}/{e.thr.quantile(.9):.0f} "
              f"top1 {(t1.mot > t1.thr).mean():.2f} top3 {(top.mot > top.thr).mean():.2f} max-phien {(sm.mot > sm.thr).mean():.2f} "
              f"max-phien theo phien {sm.assign(hit=sm.mot > sm.thr).groupby('ses').hit.mean().round(2).to_dict()}")
