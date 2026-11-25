#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum_fixture.py — sinh dữ liệu đối chiếu C# = Python cho "HVN dạng cụm" (PLAN-VUNG-MANH.md mục 10).

  python hvn_cum_fixture.py            ghi 2 file vào fixture/, KHÔNG đụng m30_bars.csv / m30_levels.csv.gz / expected.json cũ
  python hvn_cum_fixture.py "2026-10-30 02:00" ...   in thêm các ca theo giờ nến j (để chép vào PLAN)

  fixture/hvn_cum_cases.json   ca mức HÀM: mỗi ca = một profile (giá, khối lượng từng bước giá) + up + tick + thông số
                               → h, danh sách cụm kỳ vọng. Có NQZ26 phiên 2026-11-23 (ca người dùng vẽ tay).
  fixture/expected_cum.json    ca mức CẢ BỘ MÁY: cùng cấu trúc expected.json nhưng HVN = dạng cụm (689 ca trên fixture GCZ26).
                               Tính CHỈ từ m30_bars.csv + m30_levels.csv.gz.
"""
import json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, 'fixture')
E0 = np.datetime64('2026-10-18T00:00')


def func_cases():
    import hvn_cum as H
    want = {'nq': [('2026-11-23', 'd'), ('2026-11-18', 'd'), ('2026-11-10', 'd'), ('2026-11-13', 'd'), ('2026-11-17', 'd'), ('2026-11-20', 'w')],
            'gc': [('2026-10-29', 'd'), ('2026-11-05', 'd'), ('2026-11-03', 'd'), ('2026-10-28', 'd'), ('2026-10-30', 'w')]}
    out = []
    for sym, lst in want.items():
        D, vm = H.load(sym)
        tick = H.TICK_REAL[sym]
        t = pd.to_datetime(D.m30['t'])
        for date, kind in lst:
            k = H.find_day(D, date)
            a, b = D.days[k] if kind == 'd' else D.weeks[int(D.week_of[D.days[k][0]])]
            tk, v = D.ticks_over(a, b)
            up_ticks = H.up_of(D, a, b) / 0.1
            hp = dict(H.HP, Y=H.HP['Y_W'] if kind == 'w' else H.HP['Y'])
            cl, ex = H.clusters(tk, v, up_ticks, hp)
            dec = 2 if sym == 'nq' else 1
            out.append(dict(
                ten='%sZ26 %s %s' % (sym.upper(), 'phiên' if kind == 'd' else 'tuần', date), tick=tick,
                tu=str(t[a]), den=str(t[b]), so_nen_m30=int(b - a + 1),
                up=round(up_ticks * tick, 6), SM=hp['SM'], X=hp['X'], PK2=hp['PK2'], Y=hp['Y'], WMIN=hp['WMIN'], MAXC=hp['MAXC'],
                h=int(ex['h']), tong_khoi_luong=float(v.sum()),
                levels=[[round(int(a_) * tick, dec), int(round(b_))] for a_, b_ in zip(tk, v)],
                clusters=[dict(lo=round(c['lo'] * tick, dec), hi=round(c['hi'] * tick, dec), peak=round(c['peak'] * tick, dec),
                               mass=round(c['mass'], 6), rel=round(c['rel'], 6)) for c in cl]))
            print('%-28s up %8.3f h %3d → %s' % (out[-1]['ten'], out[-1]['up'], out[-1]['h'],
                                                 [(c['lo'], c['hi'], c['peak'], round(c['mass'], 3)) for c in out[-1]['clusters']] or 'KHÔNG có cụm'))
    with open(os.path.join(FX, 'hvn_cum_cases.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(ghi_chu='Xem PLAN-VUNG-MANH.md mục 10.3. levels = [giá, khối lượng] từng bước giá của cả profile.', cases=out), f, ensure_ascii=False, separators=(',', ':'))


def engine_cases(want):
    import importlib, vm
    importlib.reload(vm)
    from vm import Data, TICK, ROW
    import vung_manh as V
    importlib.reload(V)
    from parity_cases import zone_json
    bb = pd.read_csv(os.path.join(FX, 'm30_bars.csv'))
    lv = pd.read_csv(os.path.join(FX, 'm30_levels.csv.gz'))
    d = dict(m1=None, m30=dict(t=pd.to_datetime(bb['time_utc']).values.astype('datetime64[ns]'), o=bb['open'].values, h=bb['high'].values,
                               l=bb['low'].values, c=bb['close'].values, v=bb['volume'].values.astype(float)),
             lv=(lv['idx'].values.astype(np.int32), np.round(lv['price'].values * 10).astype(np.int32), lv['volume'].values.astype(np.float32)))
    D = Data(d=d)
    assert V.P['HVN_MODE'] == 'cum'
    eng = V.Engine(D)
    exp, n_gold, n_hvn = [], 0, 0
    for j in range(D.n - 1):
        if D.m30['t'][j] < E0: continue
        zs = eng.zones(j)
        now = float(D.m30['c'][j])
        shown = V.display(D, zs, j, now)
        dday = int(D.day_of[j + 1])
        n_gold += any(z['gold'] for z in shown); n_hvn += any(z['hvn'] for z in shown)
        exp.append(dict(j=j, time_utc=str(pd.Timestamp(D.m30['t'][j])), now=now, U=round(float(D.U[j + 1]), 6),
                        levels=[dict(name=L['name'], lo=round(float(L['lo']), 4), hi=round(float(L['hi']), 4),
                                     **({'peak': round(float(L['peak']), 1), 'mass': round(float(L['ratio']), 6), 'src': int(L['src']), 'end': int(L['end']),
                                         'ok': bool(V.hvn_ok(D, L, j, D.U[j + 1]))} if 'peak' in L else {})) for L in eng.levels(dday)],
                        clusters=[zone_json(z) for z in sorted(zs, key=lambda z: z['lo'])],
                        shown=[dict(lo=round(float(z['lo']), 1), hi=round(float(z['hi']), 1), side=int(z['side']), color=z['color'], label=z['label']) for z in shown]))
    pv = eng.pv
    piv = [dict(i=int(q['idx']), price=round(float(q['price']), 1), kind=int(q['kind']), conf=int(q['conf'])) for q in pv[np.argsort(pv['idx'], kind='stable')]]
    days = [dict(d=k, start=int(a_), end=int(b_), U=(None if not np.isfinite(D.unit_day[k]) else round(float(D.unit_day[k]), 6))) for k, (a_, b_) in enumerate(D.days)]
    with open(os.path.join(FX, 'expected_cum.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(params=V.P, tick=TICK, row=ROW, days=days, weeks=[dict(w=k, start=int(a_), end=int(b_)) for k, (a_, b_) in enumerate(D.weeks)],
                       pivots=piv, cases=exp), f, ensure_ascii=False, separators=(',', ':'))
    print('expected_cum.json: %d ca · ca có vùng vàng được vẽ %d · ca có vùng dính HVN được vẽ %d · điểm va đập %d' % (len(exp), n_gold, n_hvn, len(pv)))
    for e in exp:
        if e['time_utc'][:16] in want:
            print('\n=== j', e['j'], e['time_utc'], 'giá', e['now'], 'U', round(e['U'], 6))
            for L in e['levels']:
                if 'peak' in L: print('   HVN', L)
            print('   số cụm', len(e['clusters']))
            for s_ in e['shown']: print('   VẼ', s_)


def main():
    func_cases()
    os.environ.pop('VM_CACHE', None)
    engine_cases([a for a in sys.argv[1:] if a[:2] == '20'] or
                 ['2026-10-30 02:00', '2026-10-21 13:00', '2026-10-19 05:30', '2026-11-04 14:00', '2026-10-27 19:00'])


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
