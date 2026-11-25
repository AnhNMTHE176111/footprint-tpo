"""Xem nhanh nhật ký lệnh đơn (Fable, 2026-11-25). python bw0_profile.py
In: số ngày giao dịch có nhật ký, độ phủ, phân vị mot, số ô có mot >= 10/20/30/50/100 mỗi ngày, theo phiên."""
import pandas as pd, numpy as np, glob, os, sys
D = r'C:\Users\anhla\AppData\Roaming\OrderFlowBubbles\bigtrade-log'
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
def load(p):
    d = pd.read_csv(p)
    n0 = len(d)
    d = d.drop_duplicates(['time_ticks', 'price'], keep='last')
    d['t'] = pd.to_datetime(d.time_iso.str[:19])
    ct = d.t - pd.Timedelta(hours=6)            # Chicago mùa đông (CST); trước 1/11 là CDT (-5)
    ct = ct.where(d.t >= '2026-11-01 07:00', d.t - pd.Timedelta(hours=5))
    d['ct'] = ct
    d['day'] = (ct + pd.Timedelta(hours=7)).dt.date   # ngày giao dịch: bắt đầu 17:00 Chicago
    h = ct.dt.hour + ct.dt.minute / 60
    d['ses'] = np.select([(h >= 17) | (h < 2), (h >= 2) & (h < 8.5)], ['A', 'Au'], 'My')
    return d, n0
for p in sorted(glob.glob(D + r'\*.csv')):
    d, n0 = load(p)
    name = os.path.basename(p)
    print('=' * 110); print(name, 'dong', n0, 'sau bo trung', len(d), 'tu', d.t.min(), 'den', d.t.max())
    g = d.groupby('day')
    tab = pd.DataFrame({'nen': g.time_ticks.nunique(), 'o': g.size(), 'max': g.mot.max(),
                        'p99': g.mot.quantile(.99), 'p999': g.mot.quantile(.999),
                        **{f'>={k}': g.mot.apply(lambda s, k=k: (s >= k).sum()) for k in (10, 20, 30, 50, 100)}})
    print(tab.to_string())
    q = [.5, .9, .99, .995, .999, .9995, .9999, 1]
    print('phan vi toan bo', dict(zip(q, d.mot.quantile(q).round(1))))
    for s in ('A', 'Au', 'My'):
        x = d[d.ses == s]
        if len(x): print(' phien', s, 'o', len(x), dict(zip(q, x.mot.quantile(q).round(1))),
                         {k: int((x.mot >= k).sum()) for k in (10, 20, 30, 50, 100)})
    top = d.nlargest(15, 'mot')[['t', 'price', 'mot', 'buy', 'sell', 'ses']]
    print(top.to_string(index=False))
