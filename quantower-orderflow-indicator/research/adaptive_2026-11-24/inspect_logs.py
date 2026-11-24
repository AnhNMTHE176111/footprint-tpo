"""Kiểm nhật ký lệnh đơn: trùng lặp, khoảng phủ theo ngày, phân phối mot."""
import os, glob, pandas as pd, numpy as np
D = os.path.join(os.environ['APPDATA'], 'OrderFlowBubbles', 'bigtrade-log')
for p in sorted(glob.glob(D + '/*.csv')):
    d = pd.read_csv(p); d['t'] = pd.to_datetime(d.time_iso, utc=True)
    dup = d.duplicated(['time_ticks', 'price']).sum()
    nb = d.t.nunique()
    print('\n==', os.path.basename(p), len(d), 'dòng', nb, 'nến', 'trùng (nến,giá):', dup, '| thứ tự thời gian tăng:', d.t.is_monotonic_increasing)
    print('  ', d.t.min(), '->', d.t.max(), '| mot: 0 =', (d.mot <= 0).sum(), 'p50', d.mot.median(), 'p99', d.mot.quantile(.99), 'max', d.mot.max(), '| >=10:', (d.mot >= 10).sum(), round((d.mot >= 10).sum() / nb, 3), '/nến')
    print('   mot > buy+sell:', (d.mot > d.buy + d.sell).sum(), '| buy+sell==0:', ((d.buy + d.sell) == 0).sum())
    day = d.groupby(d.t.dt.date).agg(nen=('t', 'nunique'), dong=('t', 'size'), big=('mot', lambda x: (x >= 10).sum()), h0=('t', lambda x: x.min().strftime('%H:%M')), h1=('t', lambda x: x.max().strftime('%H:%M')))
    print(day.to_string())
