"""Kiểm: khung lớn dựng từ nhật ký M1 có khớp nhật ký khung thật không (NQ M15, GC M5)."""
import os, numpy as np, pandas as pd
from bt_common import *
def real(f, tick):
    d = pd.read_csv(os.path.join(LOG, f)); d['t'] = pd.to_datetime(d.time_iso, utc=True).dt.tz_localize(None)
    d['tk'] = np.round(d.price / tick).astype(np.int64); return d[['t', 'tk', 'mot', 'buy', 'sell']]
for key, f, m in (('NQ', '_NQZ26_XCME_Time_15Minute.csv', 15), ('GC', '_GC_XCEC_Time_5Minute.csv', 5)):
    R = real(f, TICK[key]); B = to_tf(load_m1(key), m)
    R = R[(R.t >= B.t.min()) & (R.t <= B.t.max())]
    j = R.merge(B, on=['t', 'tk'], how='outer', suffixes=('_that', '_dung'), indicator=True)
    both = j[j._merge == 'both']
    print(f'{key} M{m}: ô khung thật {len(R)}, ô dựng từ M1 {len(B)}, chung {len(both)}, chỉ thật {(j._merge=="left_only").sum()}, chỉ dựng {(j._merge=="right_only").sum()}')
    print(f'   lệnh đơn giống hệt: {(both.mot_that == both.mot_dung).mean():.4f}; thật > dựng: {(both.mot_that > both.mot_dung).sum()}, thật < dựng: {(both.mot_that < both.mot_dung).sum()}')
    print(f'   buy+sell giống: {((both.buy_that + both.sell_that) == (both.buy_dung + both.sell_dung)).mean():.4f}')
    for T in (10, 20): print(f'   ô >= {T}: thật {(R.mot >= T).sum()}  dựng {(B.mot >= T).sum()}')
