#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nq_fixture.py — fixture NQZ26 (giá THẬT, bước giá 0,25) cho test C#: render PNG ca NQ 23/11–24/11 có hộp HVN + vùng mạnh,
và vài ca đối chiếu C# = Python trên NQ (bộ chặn chỗ nối BẬT như Python: 20 × 10 × 0,25 = 50 điểm).

Cần bộ đệm vm1_nq.pkl (python prep1.py nq). Ghi:
  fixture/nq_m30_bars.csv      idx,time_utc,open,high,low,close,volume   (từ 2026-10-12)
  fixture/nq_m30_levels.csv.gz idx,price,volume
  fixture/nq_expected.json     các ca j trong ngày 2026-11-24 (giờ UTC chẵn): U, mức HVN, vùng được vẽ (giá thật)
"""
import gzip, json, os, sys, tempfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, 'fixture')
SC, TK = 2.5, 0.25
T_FROM = np.datetime64('2026-10-12T00:00')


def main():
    os.environ['VM_CACHE'] = os.path.join(os.environ.get('VM_CACHE_DIR', tempfile.gettempdir()), 'vm1_nq.pkl')
    import vm, vung_manh as V
    D = vm.Data(cache=os.environ['VM_CACHE'])
    t = D.m30['t']
    s0 = int(np.searchsorted(t, T_FROM))
    n = D.n
    rows = []
    for i in range(s0, n):
        rows.append('%d,%s,%.2f,%.2f,%.2f,%.2f,%.1f' % (i - s0, str(pd.Timestamp(t[i]))[:19], D.m30['o'][i] * SC, D.m30['h'][i] * SC,
                                                       D.m30['l'][i] * SC, D.m30['c'][i] * SC, D.m30['v'][i]))
    with open(os.path.join(FX, 'nq_m30_bars.csv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('idx,time_utc,open,high,low,close,volume\n' + '\n'.join(rows) + '\n')
    with gzip.open(os.path.join(FX, 'nq_m30_levels.csv.gz'), 'wt', encoding='utf-8', newline='\n') as f:
        f.write('idx,price,volume\n')
        for i in range(s0, n):
            a, b = D.lv_ptr[i], D.lv_ptr[i + 1]
            for k, v in zip(D.lv_tick[a:b], D.lv_vol[a:b]):
                f.write('%d,%.2f,%d\n' % (i - s0, int(k) * TK, int(round(float(v)))))
    eng = V.Engine(D)
    cases = []
    for j in range(s0, n - 1):
        ts = pd.Timestamp(t[j])
        if str(ts)[:10] != '2026-11-24' or ts.minute != 0: continue
        zs = eng.zones(j)
        now = float(D.m30['c'][j])
        shown = V.display(D, zs, j, now)
        dday = int(D.day_of[j + 1])
        cases.append(dict(j=j - s0, time_utc=str(ts), now=round(now * SC, 2), U=float(D.U[j + 1]) * SC,
                          hvn=[dict(name=L['name'], lo=round(L['lo'] * SC, 2), hi=round(L['hi'] * SC, 2), peak=round(L['peak'] * SC, 2),
                                    mass=round(float(L['ratio']), 6), src=int(L['src']), ok=bool(V.hvn_ok(D, L, j, D.U[j + 1])))
                               for L in eng.levels(dday) if 'peak' in L],
                          shown=[dict(lo=round(float(z['lo']) * SC, 2), hi=round(float(z['hi']) * SC, 2), side=int(z['side']), color=z['color'],
                                      label=z['label']) for z in shown]))
    with open(os.path.join(FX, 'nq_expected.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(ghi_chu='NQZ26 giá thật; Python chạy trên giá chia 2,5 rồi nhân lại. Bộ chặn chỗ nối BẬT (50 điểm).',
                       tick=TK, splice_jump=50.0, cases=cases), f, ensure_ascii=False, indent=0)
    print('nến M30', n - s0, 'từ', str(pd.Timestamp(t[s0])), '→', str(pd.Timestamp(t[n - 1])), '· ca', len(cases))
    for c in cases[:3]:
        print(c['time_utc'], c['now'], round(c['U'], 3), [(h['name'], h['lo'], h['hi'], h['ok']) for h in c['hvn']][:4], [(s['lo'], s['hi'], s['label']) for s in c['shown']])


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
