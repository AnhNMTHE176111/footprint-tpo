#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hvn_cum2_fixture.py — dữ liệu đối chiếu C# = Python cho HVN dạng cụm v2 (PLAN-VUNG-MANH.md mục 13).
  python hvn_cum2_fixture.py        (cần bộ đệm: python prep1.py gc ; python prep1.py nq)

Ghi vào fixture/ (KHÔNG đụng file v1: hvn_cum_cases.json, expected_cum.json, nq_expected.json, các file nến/khối lượng):
  hvn_cum2_cases.json   ca mức HÀM (một profile → hộp). Có NQZ26 phiên 2026-11-20 và tuần 15→20/11 (ca người dùng báo sót).
  expected_cum2.json    ca mức CẢ BỘ MÁY trên fixture GCZ26 (m30_bars.csv + m30_levels.csv.gz), 689 ca; thêm `hvn_boxes` (hộp được vẽ).
  nq_expected2.json     NQZ26 giá thật (nq_m30_bars.csv + nq_m30_levels.csv.gz), bộ chặn chỗ nối TẮT (đúng như indicator chạy trên NQZ26);
                        các nến đóng giờ chẵn ngày 2026-11-24 + nến cuối; có `hvn_boxes`.
"""
import json, os, sys, tempfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, 'fixture')
E0 = np.datetime64('2026-10-18T00:00')
CDIR = os.environ.get('VM_CACHE_DIR', tempfile.gettempdir())


def func_cases():
    import hvn_cum as H1, hvn_cum2 as H2
    want = {'nq': [('2026-11-20', 'd'), ('2026-11-20', 'w'), ('2026-11-23', 'd'), ('2026-11-18', 'd'), ('2026-11-10', 'd'), ('2026-11-13', 'd'), ('2026-11-17', 'd'),
                   ('2026-11-11', 'd'), ('2026-10-08', 'd'), ('2026-10-16', 'w'), ('2026-11-13', 'w')],
            'gc': [('2026-10-29', 'd'), ('2026-11-05', 'd'), ('2026-11-03', 'd'), ('2026-10-28', 'd'), ('2026-11-02', 'd'), ('2026-10-30', 'w'), ('2026-08-21', 'w'), ('2026-08-14', 'w')]}
    out = []
    hp = H2.HP2
    for sym, lst in want.items():
        D, vm = H1.load(sym)
        tick = H1.TICK_REAL[sym]; dec = 2 if sym == 'nq' else 1
        t = pd.to_datetime(D.m30['t'])
        for date, kind in lst:
            k = H1.find_day(D, date)
            a, b = D.days[k] if kind == 'd' else D.weeks[int(D.week_of[D.days[k][0]])]
            tk, v = D.ticks_over(a, b)
            up_ticks = H1.up_of(D, a, b) / 0.1
            y = hp['Y_W'] if kind == 'w' else hp['Y']
            cl, ex = H2.clusters(tk, v, up_ticks, b - a + 1, hp, y)
            r = lambda x: round(int(x) * tick, dec)
            out.append(dict(
                ten='%sZ26 %s %s' % (sym.upper(), 'phiên' if kind == 'd' else 'tuần', date), tick=tick,
                tu=str(t[a]), den=str(t[b]), so_nen_m30=int(b - a + 1), up=round(up_ticks * tick, 6), mass_min=y,
                h=int(ex['h']), dn=int(max(1, np.floor(hp['DOM'] * up_ticks + 0.5))), max_boxes=int(ex['maxc']), tong_khoi_luong=float(v.sum()),
                levels=[[r(a_), int(round(b_))] for a_, b_ in zip(tk, v)],
                clusters=[dict(lo=r(c['lo']), hi=r(c['hi']), peak=r(c['peak']), core_lo=r(c['clo']), core_hi=r(c['chi']), mass=round(c['mass'], 6),
                               bars=round(c['bars'], 4), con=round(c['con'], 4), lon=c['lon'], noi=c['noi']) for c in cl]))
            o = out[-1]
            print('| %s | %.3f | %d | %d | %d | %s |' % (o['ten'], o['up'], o['h'], o['dn'], o['max_boxes'],
                  ' ; '.join('%s – %s · %s · %.3f · %.1f nến · ×%.2f' % (c['lo'], c['hi'], c['peak'], c['mass'], c['bars'], c['con']) for c in o['clusters']) or 'không có'))
    with open(os.path.join(FX, 'hvn_cum2_cases.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(ghi_chu='PLAN-VUNG-MANH.md mục 13. levels = [giá, khối lượng] từng bước giá của cả profile. con = mật độ hộp / mật độ xung quanh.',
                       params={k: hp[k] for k in ('SM', 'X', 'WT', 'XMIN', 'VD', 'DOM', 'CK', 'B', 'Y', 'Y_W', 'WMIN', 'MAXC', 'MAXC_STEP', 'MAXC_CAP', 'FLOOR')}, cases=out),
                  f, ensure_ascii=False, separators=(',', ':'))


def box_json(c, sc=1.0, dec=1):
    return dict(name=c['name'], lo=round(c['lo'] * sc, dec), hi=round(c['hi'] * sc, dec), peak=round(c['peak'] * sc, dec), mass=round(float(c['mass']), 6), label=c['label'])


def engine_gc(want):
    import importlib, vm
    os.environ.pop('VM_CACHE', None)
    importlib.reload(vm)
    from vm import Data, TICK, ROW
    import vung_manh as V
    importlib.reload(V)
    import hvn_cum2 as H2
    V.P['HVN_MODE'] = 'cum2'
    from parity_cases import zone_json
    bb = pd.read_csv(os.path.join(FX, 'm30_bars.csv'))
    lv = pd.read_csv(os.path.join(FX, 'm30_levels.csv.gz'))
    d = dict(m1=None, m30=dict(t=pd.to_datetime(bb['time_utc']).values.astype('datetime64[ns]'), o=bb['open'].values, h=bb['high'].values,
                               l=bb['low'].values, c=bb['close'].values, v=bb['volume'].values.astype(float)),
             lv=(lv['idx'].values.astype(np.int32), np.round(lv['price'].values * 10).astype(np.int32), lv['volume'].values.astype(np.float32)))
    D = Data(d=d)
    eng = V.Engine(D)
    exp, n_gold, n_hvn, nbox = [], 0, 0, []
    for j in range(D.n - 1):
        if D.m30['t'][j] < E0: continue
        zs = eng.zones(j)
        now = float(D.m30['c'][j])
        shown = V.display(D, zs, j, now)
        dday = int(D.day_of[j + 1])
        boxes = V.hvn_boxes(D, eng.levels(dday), j, now)
        n_gold += any(z['gold'] for z in shown); n_hvn += any(z['hvn'] for z in shown); nbox.append(len(boxes))
        exp.append(dict(j=j, time_utc=str(pd.Timestamp(D.m30['t'][j])), now=now, U=round(float(D.U[j + 1]), 6),
                        levels=[dict(name=L['name'], lo=round(float(L['lo']), 4), hi=round(float(L['hi']), 4),
                                     **({'peak': round(float(L['peak']), 1), 'mass': round(float(L['ratio']), 6), 'src': int(L['src']), 'end': int(L['end']),
                                         'ok': bool(V.hvn_ok(D, L, j, D.U[j + 1]))} if 'peak' in L else {})) for L in eng.levels(dday)],
                        clusters=[zone_json(z) for z in sorted(zs, key=lambda z: z['lo'])],
                        shown=[dict(lo=round(float(z['lo']), 1), hi=round(float(z['hi']), 1), side=int(z['side']), color=z['color'], label=z['label']) for z in shown],
                        hvn_boxes=[box_json(c) for c in boxes]))
    pv = eng.pv
    piv = [dict(i=int(q['idx']), price=round(float(q['price']), 1), kind=int(q['kind']), conf=int(q['conf'])) for q in pv[np.argsort(pv['idx'], kind='stable')]]
    days = [dict(d=k, start=int(a_), end=int(b_), U=(None if not np.isfinite(D.unit_day[k]) else round(float(D.unit_day[k]), 6))) for k, (a_, b_) in enumerate(D.days)]
    with open(os.path.join(FX, 'expected_cum2.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(params=dict(V.P, HVN2=H2.HP2), tick=TICK, row=ROW, days=days, weeks=[dict(w=k, start=int(a_), end=int(b_)) for k, (a_, b_) in enumerate(D.weeks)],
                       pivots=piv, cases=exp), f, ensure_ascii=False, separators=(',', ':'))
    print('\nexpected_cum2.json: %d ca · ca có vùng vàng được vẽ %d · ca có vùng dính HVN được vẽ %d · điểm va đập %d · hộp HVN được vẽ TB %.2f (nhiều nhất %d)'
          % (len(exp), n_gold, n_hvn, len(pv), np.mean(nbox), max(nbox)))
    for e in exp:
        if e['time_utc'][:16] in want:
            print('\n=== j', e['j'], e['time_utc'], 'giá', e['now'], 'U', round(e['U'], 6))
            for L in e['levels']:
                if 'peak' in L: print('   HVN', L['name'], L['lo'], L['hi'], round(L['mass'], 3), 'ok' if L['ok'] else 'chưa rời xa')
            for s_ in e['shown']: print('   VẼ', s_['lo'], s_['hi'], s_['color'], s_['label'])
            for s_ in e['hvn_boxes']: print('   HỘP', s_['lo'], s_['hi'], s_['label'], round(s_['mass'], 3))


def engine_nq():
    import importlib
    os.environ['VM_CACHE'] = os.path.join(CDIR, 'vm1_nq.pkl')
    import vm
    importlib.reload(vm)
    vm.SPLICE_JUMP = 1e12
    import vung_manh as V
    importlib.reload(V)
    V.P['HVN_MODE'] = 'cum2'
    SC, TK = 2.5, 0.25
    D = vm.Data(cache=os.environ['VM_CACHE'])
    t = D.m30['t']
    s0 = int(np.searchsorted(t, np.datetime64('2026-10-12T00:00')))
    chk = pd.read_csv(os.path.join(FX, 'nq_m30_bars.csv'))
    assert len(chk) == D.n - s0 and abs(chk['close'].values[-1] - D.m30['c'][-1] * SC) < 1e-6, 'nq_m30_bars.csv không khớp bộ đệm — chạy lại nq_fixture.py'
    eng = V.Engine(D)
    cases = []
    for j in range(s0, D.n - 1):
        ts = pd.Timestamp(t[j])
        if not ((str(ts)[:10] == '2026-11-24' and ts.minute == 0) or j == D.n - 2): continue
        zs = eng.zones(j); now = float(D.m30['c'][j])
        shown = V.display(D, zs, j, now)
        dday = int(D.day_of[j + 1]); lv = eng.levels(dday)
        cases.append(dict(j=j - s0, time_utc=str(ts), now=round(now * SC, 2), U=float(D.U[j + 1]) * SC,
                          hvn=[dict(name=L['name'], lo=round(L['lo'] * SC, 2), hi=round(L['hi'] * SC, 2), peak=round(L['peak'] * SC, 2),
                                    mass=round(float(L['ratio']), 6), src=int(L['src']), ok=bool(V.hvn_ok(D, L, j, D.U[j + 1]))) for L in lv if 'peak' in L],
                          shown=[dict(lo=round(float(z['lo']) * SC, 2), hi=round(float(z['hi']) * SC, 2), side=int(z['side']), color=z['color'], label=z['label']) for z in shown],
                          hvn_boxes=[box_json(c, SC, 2) for c in V.hvn_boxes(D, lv, j, now)]))
    with open(os.path.join(FX, 'nq_expected2.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(ghi_chu='NQZ26 giá thật; Python chạy trên giá chia 2,5 rồi nhân lại. Bộ chặn chỗ nối TẮT (splice_jump = 0). HVN v2 (PLAN mục 13).',
                       tick=TK, splice_jump=0.0, cases=cases), f, ensure_ascii=False, indent=0)
    print('\nnq_expected2.json: %d ca' % len(cases))
    for c in cases[-2:]:
        print(c['time_utc'], 'giá', c['now'], 'U', round(c['U'], 3))
        for h in c['hvn']: print('   HVN', h['name'], h['lo'], h['hi'], round(h['mass'], 3), 'ok' if h['ok'] else 'chưa rời xa')
        for s_ in c['shown']: print('   VẼ', s_['lo'], s_['hi'], s_['color'], s_['label'])
        for s_ in c['hvn_boxes']: print('   HỘP', s_['lo'], s_['hi'], s_['label'], round(s_['mass'], 3))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    func_cases()
    engine_gc(['2026-10-30 02:00', '2026-10-21 13:00', '2026-10-19 05:30', '2026-11-04 14:00', '2026-10-27 19:00'])
    engine_nq()
