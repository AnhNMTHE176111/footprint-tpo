"""Chạy cấu hình đã chốt (FROZEN.md) trên GC liên tục 2 năm, chỉ phần TRƯỚC 2026-08-11 (không trùng 90d).
Loại tín hiệu LVN có cửa sổ profile vắt qua bước nhảy giá giả (đổi hợp đồng / gap)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, '.'); sys.stdout.reconfigure(encoding='utf-8')
from core import Data, stats, to_df
import r2

d = Data(base='fp_GC_XCEC_Time_20240801-20260819_748d9h', cache_name='cache_2y.npz')
jump = np.abs(d.o[1:] - d.c[:-1]) > np.maximum(15, 4 * np.nan_to_num(d.atr1[:-1], nan=1.0))
jidx = np.flatnonzero(jump) + 1
print('bước nhảy:', len(jidx))
CUT = pd.Timestamp('2026-08-11')


def report(name, tr, window_min=None):
    df = to_df(tr, d)
    if window_min:
        bad = [np.any((jidx > i - window_min) & (jidx <= i)) for i in df.i.values]
        df = df[~np.array(bad)]
    df = df[df.date < CUT]
    df['half'] = np.where(df.date < pd.Timestamp('2025-08-01'), 'H1 08/24-07/25', 'H2 08/25-08/26')
    print(name, 'ALL', stats(df))
    for h, p in df.groupby('half'):
        print('   ', h, stats(p))
    df.to_csv(f'holdout2y_{name}.csv', index=False)


report('LVN', r2.lvn(d, hours=72, smooth=5, SLm=0.7, tf=5, min_rr=1.0), window_min=72 * 60)
report('FAKE', r2.fake(d, tf=5, va='dev', wick=0.6, SLbuf=0.1, tgt='poc'))
