#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parity_cases.py — xuất BỘ DỮ LIỆU ĐỐI CHIẾU C# = Python cho PLAN-VUNG-MANH.md.

Ghi vào fixture/:
  m30_bars.csv        idx,time_utc,open,high,low,close,volume        (nến M30 GCZ26, 2026-09-20 → 2026-11-06)
  m30_levels.csv.gz   idx,price,volume                               (khối lượng từng mức giá của mỗi nến M30)
  expected.json       params; days/weeks (ranh giới phiên, tuần, U từng phiên); pivots (mọi điểm va đập);
                      cases: với mỗi nến j từ 2026-10-18: U, các mức hợp lưu, MỌI cụm đủ số lần va đập, các vùng được vẽ
Kết quả kỳ vọng được tính CHỈ từ hai file fixture (không dùng dữ liệu ngoài) ⇒ C# đọc đúng hai file này phải ra y hệt.
Đồng thời kiểm: tính trên toàn bộ dữ liệu 2 năm cho cùng kết quả ở các nến đó (lịch sử trong fixture là đủ).
"""
import gzip, json, os, sys
import numpy as np
import pandas as pd
from vm import *
import vung_manh as V

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, 'fixture')
T0, T1 = np.datetime64('2026-09-20T00:00'), np.datetime64('2026-11-07T00:00')
E0 = np.datetime64('2026-10-18T00:00')        # từ đây mới ghi kết quả kỳ vọng


def zone_json(z):
    return dict(lo=round(float(z['lo']), 1), hi=round(float(z['hi']), 1), n=int(z['n']), pmin=round(float(z['pmin']), 1), pmax=round(float(z['pmax']), 1),
                names=z['names'], ngroup=int(z['ngroup']), hvn=bool(z['hvn']), gold=bool(z['gold']),
                ngroup_khong_gop=len(set(z['names'])), gold_khong_gop=bool(len(set(z['names'])) >= V.P['GOLD_MIN'] and z['hvn']))


def main():
    os.makedirs(FX, exist_ok=True)
    full = Data()
    t = full.m30['t']
    a, b = int(np.searchsorted(t, T0)), int(np.searchsorted(t, T1)) - 1
    m = full.m30
    bars = pd.DataFrame({'idx': np.arange(b - a + 1), 'time_utc': pd.to_datetime(t[a:b + 1]).strftime('%Y-%m-%d %H:%M:%S'),
                         'open': m['o'][a:b + 1], 'high': m['h'][a:b + 1], 'low': m['l'][a:b + 1], 'close': m['c'][a:b + 1], 'volume': m['v'][a:b + 1]})
    bars.to_csv(os.path.join(FX, 'm30_bars.csv'), index=False, lineterminator='\n')
    s, e = full.lv_ptr[a], full.lv_ptr[b + 1]
    with gzip.open(os.path.join(FX, 'm30_levels.csv.gz'), 'wt', newline='\n') as f:
        f.write('idx,price,volume\n')
        for i, tk, v in zip(full.lv_i[s:e] - a, full.lv_tick[s:e], full.lv_vol[s:e]):
            f.write('%d,%.1f,%d\n' % (i, tk / 10.0, int(round(v))))
    # ---- nạp lại CHỈ từ fixture
    bb = pd.read_csv(os.path.join(FX, 'm30_bars.csv'))
    lv = pd.read_csv(os.path.join(FX, 'm30_levels.csv.gz'))
    d = dict(m1=None, m30=dict(t=pd.to_datetime(bb['time_utc']).values.astype('datetime64[ns]'), o=bb['open'].values, h=bb['high'].values,
                               l=bb['low'].values, c=bb['close'].values, v=bb['volume'].values.astype(float)),
             lv=(lv['idx'].values.astype(np.int32), np.round(lv['price'].values * 10).astype(np.int32), lv['volume'].values.astype(np.float32)))
    D = Data(d=d)
    eng, engF = V.Engine(D), V.Engine(full)
    exp, mism, n_gold, n_in = [], 0, 0, 0
    for j in range(D.n - 1):
        if D.m30['t'][j] < E0: continue
        zs = eng.zones(j)
        zf = engF.zones(j + a)
        if [zone_json(z) for z in zs] != [zone_json(z) for z in zf]: mism += 1
        now = float(D.m30['c'][j])
        shown = V.display(D, zs, j, now)
        dday = int(D.day_of[j + 1])
        n_gold += any(z['gold'] for z in shown); n_in += any(z['inside'] for z in shown)
        exp.append(dict(j=j, time_utc=str(pd.Timestamp(D.m30['t'][j])), now=now, U=round(float(D.U[j + 1]), 6),
                        levels=[dict(name=L['name'], lo=round(float(L['lo']), 4), hi=round(float(L['hi']), 4),
                                     **({'peak': round(float(L['peak']), 1), 'ratio': round(float(L['ratio']), 4), 'dshape': bool(L['dshape']), 'src': int(L['src']),
                                         'ok': bool(V.hvn_ok(D, L, j, D.U[j + 1]))} if 'peak' in L else {})) for L in eng.levels(dday)],
                        clusters=[zone_json(z) for z in sorted(zs, key=lambda z: z['lo'])],
                        shown=[dict(lo=round(float(z['lo']), 1), hi=round(float(z['hi']), 1), side=int(z['side']), color=z['color'], label=z['label']) for z in shown]))
    with open(os.path.join(FX, 'expected.json'), 'w', encoding='utf-8') as f:
        pv = eng.pv
        piv = [dict(i=int(q['idx']), time_utc=str(pd.Timestamp(D.m30['t'][q['idx']])), price=round(float(q['price']), 1), kind=int(q['kind']), conf=int(q['conf'])) for q in pv[np.argsort(pv['idx'], kind='stable')]]
        days = [dict(d=k, start=int(a_), end=int(b_), U=(None if not np.isfinite(D.unit_day[k]) else round(float(D.unit_day[k]), 6))) for k, (a_, b_) in enumerate(D.days)]
        weeks = [dict(w=k, start=int(a_), end=int(b_)) for k, (a_, b_) in enumerate(D.weeks)]
        json.dump(dict(params=V.P, tick=TICK, row=ROW, days=days, weeks=weeks, pivots=piv, cases=exp), f, ensure_ascii=False, separators=(',', ':'))
    print('nến fixture', D.n, '| ca kỳ vọng', len(exp), '| lệch so với tính trên toàn bộ dữ liệu:', mism, '| ca có vùng vàng được vẽ', n_gold, '| ca giá trong vùng', n_in)
    print('kích thước:', {f: os.path.getsize(os.path.join(FX, f)) for f in os.listdir(FX)})
    # ---- vài ca in ra để chép vào PLAN
    pv = eng.pv
    print('điểm va đập trong fixture:', len(pv))
    want = sys.argv[1:] or []
    for e in exp:
        if e['time_utc'][:16] in want:
            print('\n===', e['time_utc'], 'giá', e['now'], 'U', round(e['U'], 3))
            for L in e['levels']: print('   mức', L)
            for c in e['clusters']: print('   cụm', c)
            for s_ in e['shown']: print('   VẼ', s_)
    return exp


if __name__ == '__main__':
    main()
