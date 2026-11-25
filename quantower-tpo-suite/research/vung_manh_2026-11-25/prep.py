#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prep.py — nạp dữ liệu footprint M1 (nguồn chuẩn) và dựng bộ đệm cho nghiên cứu "vùng mạnh".

Chuỗi hợp nhất:
  A = fp_GC_XCEC_Time_20240801-20260819 (mã liên tục, có chỗ nối hợp đồng)
  B = fp_GCZ26 20260723-20261021 + 20260811-20261109 (một hợp đồng)
  Dùng A tới hết 2026-08-10, từ 2026-08-11 dùng B (A sau chỗ nối 07-29 cũng là GCZ26
  nên hai đoạn cùng thang giá).

Xuất pickle (mặc định trong thư mục tạm, KHÔNG nằm trong repo):
  m1  : dict các mảng numpy (t[ns], o, h, l, c, v)
  m30 : dict các mảng (t, o, h, l, c, v) — nến M30 neo :00/:30 UTC, y như Quantower
  lv  : (m30_idx[int32], tick[int32] = giá*10, vol[float32]) — khối lượng từng mức giá mỗi nến M30

Chạy:  python prep.py            (đặt VM_CACHE để đổi chỗ lưu)
"""
import os, pickle, sys, tempfile
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
FP = os.path.join(ROOT, 'data-export', 'data-footprint')
CACHE = os.environ.get('VM_CACHE', os.path.join(tempfile.gettempdir(), 'vung_manh_cache.pkl'))

SRC = [
    ('A', 'fp_GC_XCEC_Time_20240801-20260819_748d9h', None, '2026-08-11 00:00:00'),
    ('B1', 'fp_GCZ26_XCEC_Time_20260723-20261021_90d', '2026-08-11 00:00:00', '2026-10-21 00:00:00'),
    ('B2', 'fp_GCZ26_XCEC_Time_20260811-20261109_90d', '2026-10-21 00:00:00', None),
]


def load_one(stem, t_from, t_to):
    bars = pd.read_csv(os.path.join(FP, stem + '_bars.csv'),
                       usecols=['bar_idx', 'datetime', 'open', 'high', 'low', 'close', 'volume'],
                       parse_dates=['datetime'])
    bars = bars.sort_values('datetime').drop_duplicates('datetime', keep='last')
    keep = np.ones(len(bars), bool)
    if t_from: keep &= (bars['datetime'] >= pd.Timestamp(t_from)).values
    if t_to: keep &= (bars['datetime'] < pd.Timestamp(t_to)).values
    bars = bars[keep].reset_index(drop=True)
    idx2t = pd.Series(bars['datetime'].values, index=bars['bar_idx'].values)
    parts = []
    for ch in pd.read_csv(os.path.join(FP, stem + '.csv'), usecols=['bar_idx', 'price', 'volume'],
                          chunksize=3_000_000):
        t = idx2t.reindex(ch['bar_idx'].values).values
        ok = ~pd.isna(t)
        if not ok.any(): continue
        t30 = pd.DatetimeIndex(t[ok]).floor('30min')
        g = pd.DataFrame({'t30': t30, 'tick': np.round(ch['price'].values[ok] * 10).astype(np.int32),
                          'vol': ch['volume'].values[ok].astype(np.float64)})
        parts.append(g.groupby(['t30', 'tick'], sort=False)['vol'].sum().reset_index())
        print('  ', stem[-24:], len(parts), flush=True)
    lv = pd.concat(parts).groupby(['t30', 'tick'], sort=True)['vol'].sum().reset_index()
    return bars, lv


def main():
    B, L = [], []
    for name, stem, a, b in SRC:
        print('nạp', name, stem, flush=True)
        bars, lv = load_one(stem, a, b)
        B.append(bars); L.append(lv)
    bars = pd.concat(B).sort_values('datetime').reset_index(drop=True)
    lv = pd.concat(L).groupby(['t30', 'tick'], sort=True)['vol'].sum().reset_index()
    bars['t30'] = bars['datetime'].dt.floor('30min')
    g = bars.groupby('t30', sort=True)
    m30 = pd.DataFrame({'o': g['open'].first(), 'h': g['high'].max(), 'l': g['low'].min(),
                        'c': g['close'].last(), 'v': g['volume'].sum()}).reset_index()
    pos = pd.Series(np.arange(len(m30)), index=m30['t30'].values)
    out = dict(
        m1=dict(t=bars['datetime'].values.astype('datetime64[ns]'), o=bars['open'].values, h=bars['high'].values,
                l=bars['low'].values, c=bars['close'].values, v=bars['volume'].values.astype(float),
                i30=pos.reindex(bars['t30'].values).values.astype(np.int32)),
        m30=dict(t=m30['t30'].values.astype('datetime64[ns]'), o=m30['o'].values, h=m30['h'].values,
                 l=m30['l'].values, c=m30['c'].values, v=m30['v'].values.astype(float)),
        lv=(pos.reindex(lv['t30'].values).values.astype(np.int32), lv['tick'].values.astype(np.int32),
            lv['vol'].values.astype(np.float32)),
    )
    with open(CACHE, 'wb') as f:
        pickle.dump(out, f, protocol=4)
    print('xong:', CACHE, 'M1', len(bars), 'M30', len(m30), 'mức giá', len(lv))


if __name__ == '__main__':
    main()
