"""PARITY: tin hieu C# (BenzoDetectors) <-> Python (setup_*.py, o chinh) tren file 90d GCZ26.

Chay:  python parity_check.py [--no-run] [--from 2026-07-29]
       python parity_check.py --c-layers [--no-run]   -> parity RIENG cho setup C va cac lop moi (C0 / C4 / C6, TP chinh va TP 2R co dinh),
                                                        ghi report/PARITY-C-LAYERS.md
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


# ---------------------------------------------------------------------------------------------------------
# --c-layers: setup C + cac lop moi (PLAN-C-v2 cong D / vung day P-b / CHoCH, PLAN-C-v3 hanh lang S/R)
# C0 = C goc · C4 = L2 (D + P/b) U CHoCH · C6 = C4 + hanh lang S/R. TP chinh = canh doi dien/POC (>=2R); fixed2 = 2R co dinh.
# Co: g cong D · t vung day P/b · h CHoCH · s hanh lang S/R · e TP ve canh/POC.  "C" tro tran = C0 cu (fixed2, khong lop moi).
C_CONFIGS = [  # (nhan, cau hinh C#, o Python, tp_mode)
    ('C0 TP chinh', 'C:e', 'C0', 'poc'), ('C4 TP chinh', 'C:gthe', 'C4', 'poc'), ('C6 TP chinh', 'C:gthse', 'C6', 'poc'),
    ('C0 fixed2', 'C', 'C0', 'fixed2'), ('C4 fixed2', 'C:gth', 'C4', 'fixed2'), ('C6 fixed2', 'C:gths', 'C6', 'fixed2'),
]
C_EXPECT_PY = {'C0 TP chinh': 103, 'C4 TP chinh': 191, 'C6 TP chinh': 555}   # so lenh Python da bao (RESULTS-C-V6/V7), phien sach


def run_cs_c(out):
    subprocess.check_call(['dotnet', 'build', '-c', 'Release', os.path.join(BT, 'tools', 'ReplayCsv'), '-v', 'q', '-nologo'])
    exe = os.path.join(BT, 'tools', 'ReplayCsv', 'bin', 'Release', 'net10.0', 'ReplayCsv.dll')
    subprocess.check_call(['dotnet', exe, BASE, ','.join(c[1] for c in C_CONFIGS), out])


def main_c_layers():
    import setup_c_v7 as S7
    import setup_c_v6 as S6
    out = os.path.join(HERE, 'report', '_replay_cs_c.csv')
    if '--no-run' not in sys.argv or not os.path.exists(out):
        run_cs_c(out)
    cs = pd.read_csv(out, parse_dates=['time_utc', 'exit_utc'])
    D = S7.Data7()
    df = D.df
    sm = df['sm'].to_numpy()
    cache = {}
    L = ['# PARITY C# <-> Python — setup C va cac lop moi (file 90d GCZ26, tu phien %s)' % FROM, '',
         'Python: setup_c_v7.run_all_v7 (C0/C4/C6), mo phong 1 lenh mo bang kernel.simulate. Cot "Python (tat ca)" = so lenh dong khong loc gi (so da bao trong RESULTS).',
         '"Python (luat mo ao)" = bo cac entry trong 19:20-20:30 TRUOC khi mo phong (engine C# khong phat tin hieu o do, nen cung khong chiem cho lenh mo). Khop = cung (gio mo nen vao, chieu) VA entry/SL/TP giong nhau (1e-6).', '',
         '| cau hinh | Python (tat ca) | Python (luat mo ao) | C# | khop hoan toan | khop gio+chieu nhung khac gia | chi Python | chi C# | khop ket qua |',
         '|---|---|---|---|---|---|---|---|---|']
    detail = []
    for label, cfg, cell, tp in C_CONFIGS:
        if tp not in cache:
            cache[tp] = S7.run_all_v7(D, tp)
        R = cache[tp]
        ents = R[cell][0]
        allt = R[cell][1]
        n_all = int(allt['outcome'].isin(['TP', 'SL', 'TIME']).sum()) if len(allt) else 0
        kept = [e for e in ents if not (860 <= sm[e['idx']] < 930)]
        p = S6.sim(D, kept)
        p = p[[str(s) >= FROM for s in p['session_id']]] if len(p) else p
        c = cs[cs['setup'] == cfg.upper()].copy()
        tmap = dict(zip(df['t_utc'], df['session_id']))
        c['sid'] = [tmap.get(t, '') for t in c['time_utc']]
        c = c[c['sid'] >= FROM]
        pk = {(pd.Timestamp(r.t_utc), int(r.side)): r for r in p.itertuples()}
        ck = {(r.time_utc, int(r.side)): r for r in c.itertuples()}
        both = sorted(set(pk) & set(ck))
        exact = [k for k in both if abs(pk[k].entry - ck[k].entry) < 1e-6 and abs(pk[k].sl - ck[k].sl) < 1e-6 and abs(pk[k].tp - ck[k].tp) < 1e-6]
        pd_ = [k for k in both if k not in exact]
        onlyP, onlyC = sorted(set(pk) - set(ck)), sorted(set(ck) - set(pk))
        same = sum(1 for k in exact if pk[k].outcome == ck[k].outcome)
        L.append('| %s (`%s`) | %d%s | %d | %d | %d | %d | %d | %d | %d / %d |' % (
            label, cfg, n_all, (' (da bao %d)' % C_EXPECT_PY[label]) if label in C_EXPECT_PY else '', len(pk), len(ck), len(exact), len(pd_), len(onlyP), len(onlyC), same, len(exact)))
        print(label, 'Py(tat ca)', n_all, 'Py(vo)', len(pk), 'C#', len(ck), 'exact', len(exact), 'priceDiff', len(pd_), 'onlyPy', len(onlyP), 'onlyC#', len(onlyC), 'outcome', same)
        for lab, ks, src in (('chi Python', onlyP, pk), ('chi C#', onlyC, ck), ('khac gia', pd_, None)):
            for k in ks:
                if src is None:
                    detail.append('- %s khac gia %s side %d: Py e=%.1f sl=%.1f tp=%.1f | C# e=%.1f sl=%.1f tp=%.1f' % (
                        label, k[0], k[1], pk[k].entry, pk[k].sl, pk[k].tp, ck[k].entry, ck[k].sl, ck[k].tp))
                else:
                    r = src[k]
                    detail.append('- %s %s %s side %d entry %.1f sl %.1f tp %.1f zone %s' % (label, lab, k[0], k[1], r.entry, r.sl, r.tp, getattr(r, 'zone', '')))
    L += ['', '## Chi tiet lech', ''] + (detail or ['(khong lech)'])
    with open(os.path.join(HERE, 'report', 'PARITY-C-LAYERS.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')
    print('ghi report/PARITY-C-LAYERS.md')


def main():
    if '--c-layers' in sys.argv:
        return main_c_layers()
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
        n_all = len(p)
        smv = dict(zip(df['t_utc'], df['sm']))
        p = p[[not (860 <= smv[t] < 930) for t in p['t_utc']]] if len(p) else p   # luat mo ao: C# engine khong phat trong 19:20-20:30
        print(s, 'Python bi loai boi luat mo ao:', n_all - len(p))
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
