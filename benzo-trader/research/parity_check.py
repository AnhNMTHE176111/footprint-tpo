"""PARITY: tin hieu C# (BenzoDetectors) <-> Python (setup_*.py, o chinh) tren file 90d GCZ26.

Chay:  python parity_check.py [--no-run] [--from 2026-07-29]
  * Chay C# bang tools/ReplayCsv (dotnet) -> report/_replay_cs.csv  (bo qua neu --no-run va file da co).
  * Chay Python o 'o chinh' cua tung setup, mo phong (1 lenh mo/setup) bang kernel.simulate.
  * So (thoi gian mo nen vao, chieu) + entry/SL/TP + ket qua. Ghi report/PARITY.md.
O chinh: A = V3 het han 30 nen (n_hoi 3, than CF 0,5, TP 3R) | B = BASE theta 0,5 N 3 TP 3R |
         C = xuyen 2 tick, rong >= 6, TP co dinh 2R | D = V3 (delta, bo vung Z, loc sideway) 5 gia / hoi <= 70%, TP 2R.
Chi so sanh tu phien 2026-07-29 tro di: 4 phien dau file 90d la 'thin' (du lieu mong), Python loai (bad) con C# khong biet.
"""
import os, sys, subprocess
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kernel as K
import setup_a_pha_hoi as SA
import setup_b_hap_thu as SB
import setup_c_fade_canh as SC
import setup_d_trap as SD

ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = os.path.join(ROOT, 'data-export', 'data-footprint', 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
CS_CSV = os.path.join(HERE, 'report', '_replay_cs.csv')
BT = os.path.dirname(HERE)
FROM = '2026-07-29'
if '--from' in sys.argv:
    FROM = sys.argv[sys.argv.index('--from') + 1]


def run_cs():
    exe = os.path.join(BT, 'tools', 'ReplayCsv', 'bin', 'Release', 'net10.0', 'ReplayCsv.dll')
    subprocess.check_call(['dotnet', 'build', '-c', 'Release', os.path.join(BT, 'tools', 'ReplayCsv'), '-v', 'q', '-nologo'])
    subprocess.check_call(['dotnet', exe, BASE, 'ALL', CS_CSV])


def py_trades():
    out = {}
    D = SA.Data(BASE)
    df = D.df
    ent = SA.detect(df, D.zc, D.m5, 3, 0.5, zobj=D, expire=30)
    out['A'] = K.simulate(df, ent)
    df2 = df
    P = SB.prepare(df, D.prof)
    out['B'] = K.simulate(df, SB.detect(P, 0.5, 3))
    PC = SC.prepare(BASE)
    _, tc = SC.run(PC, pen_ticks=2, min_width=6.0, tp_mode='fixed2')
    out['C'] = tc
    PD = SD.Prep(BASE + '_bars.csv', BASE + '.csv')
    _, td = SD.run(PD, min_move=5.0, max_retr=0.7, method='delta', use_zone=False, sideway=True)
    out['D'] = td
    return df, out


def main():
    if '--no-run' not in sys.argv or not os.path.exists(CS_CSV):
        run_cs()
    cs = pd.read_csv(CS_CSV, parse_dates=['time_utc', 'exit_utc'])
    df, py = py_trades()
    sess = pd.Series(df['session_id'].to_numpy(), index=df['t_utc'])
    L = ['# PARITY C# <-> Python (file 90d GCZ26, tu phien %s)' % FROM, '',
         'Moi setup chay doc lap (1 lenh mo/setup). Khop = cung (gio mo nen vao, chieu) VA entry/SL/TP giong nhau (sai so 1e-6).', '',
         '| setup | Python | C# | khop hoan toan | khop thoi gian+chieu nhung khac gia | chi Python | chi C# | khop ket qua (TP/SL) |',
         '|---|---|---|---|---|---|---|---|']
    detail = []
    for s in 'ABCD':
        p = py[s]
        p = p[p['session_id'] >= FROM] if len(p) else p
        c = cs[cs['setup'] == s].copy()
        c['sid'] = [sess.get(t, '') for t in c['time_utc']]
        c = c[c['sid'] >= FROM]
        pk = {(pd.Timestamp(r.t_utc), int(r.side)): r for r in p.itertuples()}
        ck = {(r.time_utc, int(r.side)): r for r in c.itertuples()}
        both = sorted(set(pk) & set(ck))
        exact = [k for k in both if abs(pk[k].entry - ck[k].entry) < 1e-6 and abs(pk[k].sl - ck[k].sl) < 1e-6 and abs(pk[k].tp - ck[k].tp) < 1e-6]
        priceDiff = [k for k in both if k not in exact]
        onlyP = sorted(set(pk) - set(ck))
        onlyC = sorted(set(ck) - set(pk))
        same_out = sum(1 for k in exact if pk[k].outcome == ck[k].outcome)
        L.append('| %s | %d | %d | %d | %d | %d | %d | %d / %d |' % (s, len(pk), len(ck), len(exact), len(priceDiff), len(onlyP), len(onlyC), same_out, len(exact)))
        for lab, ks, src in (('chi Python', onlyP, pk), ('chi C#', onlyC, ck), ('khac gia', priceDiff, None)):
            for k in ks:
                if src is None:
                    detail.append('- %s khac gia %s side %d: Py e=%.1f sl=%.1f tp=%.1f | C# e=%.1f sl=%.1f tp=%.1f' % (
                        s, k[0], k[1], pk[k].entry, pk[k].sl, pk[k].tp, ck[k].entry, ck[k].sl, ck[k].tp))
                else:
                    r = src[k]
                    detail.append('- %s %s %s side %d entry %.1f sl %.1f tp %.1f' % (s, lab, k[0], k[1], r.entry, r.sl, r.tp))
        print(s, 'Py', len(pk), 'C#', len(ck), 'exact', len(exact), 'priceDiff', len(priceDiff), 'onlyPy', len(onlyP), 'onlyC#', len(onlyC), 'outcome', same_out)
    L += ['', '## Chi tiet lech', ''] + (detail or ['(khong lech)'])
    with open(os.path.join(HERE, 'report', 'PARITY.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('ghi report/PARITY.md')


if __name__ == '__main__':
    main()
