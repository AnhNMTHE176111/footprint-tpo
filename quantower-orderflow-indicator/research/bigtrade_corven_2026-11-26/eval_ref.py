"""Cham ref_rule.py (luat de xuat) tren 3 mau M1 + mau GC M5 18/11; ghi out_compare_marks.csv."""
import sys
import pandas as pd, numpy as np
from variants import *
import importlib.util
_sp = importlib.util.spec_from_file_location('bt_ref_rule', HERE + '/ref_rule.py'); RR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RR)
KK = float(sys.argv[1]) if len(sys.argv) > 1 else RR.K
rows = []; summ = []
for smp, sym in SAMPLES.items():
    bars, tick = D.load(sym, pd.Timestamp('2026-11-04'), pd.Timestamp('2026-11-07 12:00'), 1); G_, off = RR.GRID[sym]
    res = RR.run(RR.to_tuples(bars), G_, off, k=KK)
    p = pd.DataFrame([(b['t'], m[0], m[3], m[4], m[2], m[5]) for b, ms in zip(bars, res) for m in ms], columns=['t', 'k', 'ratio', 'size', 'side', 'two'])
    h, e, m, s = score(p[['t', 'k']], smp); nvis = int(V[V['sample'] == smp].t_utc.nunique())
    summ.append((smp, nvis, int((G[G['sample'] == smp].q >= 1.5).sum()), h + e + s, h, e, m, s))
    vis = set(V[V['sample'] == smp].t_utc); g = G[G['sample'] == smp]
    for r in p[p.t.isin(vis)].itertuples():
        x = g[g.t_utc == r.t]; dd = (x.pos - (r.k + 0.5)).abs() if len(x) else pd.Series([], dtype=float); j = dd.idxmin() if len(dd) and dd.min() <= 1.0 else None
        rows.append(dict(sample=smp, t_utc=r.t, row=r.k, ratio=round(r.ratio, 2), size_ref=round(r.size, 2), side=r.side, two_sided=int(r.two), gt_q=round(x.q[j], 2) if j is not None else '', gt_color=x.color[j] if j is not None else ''))
O = pd.DataFrame(rows); O.to_csv(HERE + '/out_compare_marks.csv', index=False)
print('mau | nen cham duoc | CORVEN co lon (q>=1.5) | de xuat | trung | thua | sot | (trung bong q 1.25-1.5, khong tinh thua)')
for s in summ: print(' | '.join(map(str, s)))
m = O[O.gt_q != ''].copy(); m['gt_q'] = m.gt_q.astype(float)
print('co: spearman(size_ref, q GT) = %.2f tren %d cap; trung vi |size_ref - q| = %.2f' % (m.size_ref.corr(m.gt_q, method='spearman'), len(m), (m.size_ref - m.gt_q).abs().median()))
nv = m[m.gt_color != 'V']
print('mau: CORVEN tim %d/%d vong trung; two_sided doan dung tim/khong tim %.2f; trong %d vong KHONG tim: phia trung mau %.2f' % ((m.gt_color == 'V').sum(), len(m), ((m.two_sided == 1) == (m.gt_color == 'V')).mean(), len(nv), (nv.side == nv.gt_color.map({'B': 'B', 'R': 'S'})).mean()))
# GC M5 18/11
Gm = pd.read_csv(HERE + '/../corven_m5_2026-11-18/gt_corven_m5.csv'); Gm = Gm[Gm.type == 'big']
bars, tick = D.load('GC18', pd.Timestamp('2026-11-08'), pd.Timestamp('2026-11-18 14:21'), 1); res = RR.run(RR.to_tuples(bars), 2, 1, k=KK)
samp = set(pd.Timestamp('2026-11-18 12:15') + pd.Timedelta(minutes=5 * k) for k in range(26))
for tol in (1.0, 1.5):
    hit = extra = 0
    for b, ms in zip(bars, res):
        if b['t'] not in samp: continue
        gp = [(g.price_centre / tick + 0.5 - 1) / 2 for g in Gm[Gm.bar_time == b['t'].strftime('%Y-%m-%d %H:%M')].itertuples()]; used = set()
        for m_ in ms:
            j = [i for i, x in enumerate(gp) if i not in used and abs(x - (m_[0] + 0.5)) <= tol]
            if j: used.add(j[0]); hit += 1
            else: extra += 1
    print('GC M5 18/11 (26 nen, 25 vong mo CORVEN), sai so <= %.1f hang: de xuat %d | trung %d | thua %d | sot %d' % (tol, hit + extra, hit, extra, 25 - hit))
