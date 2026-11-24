"""Chấm: đường recall / độ nhiễu so với CORVEN (tiêu chí "không bỏ sót trước, rồi mới giảm nhiễu").
Mẫu CORVEN: GC M1 580 nến (885 chấm), NQ M1 534 nến (1.205 chấm; chart CORVEN gộp hàng 8 tick nên khớp vị trí có trần thấp), GC M5 26 nến (16 cụm chấm).
Khớp M1: cùng nến, cùng màu (tím = cả hai), cách <= 3 tick. Khớp M5: cụm CORVEN có chấm cùng nến, cùng màu, cách tâm cụm <= 5 tick.
Chạy: python dot_recall.py"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); NQDIR = os.path.join(HERE, '..', 'nq_calib_2026-11-24')
sys.path.insert(0, NQDIR)
from corven_nq_compare import corven_nq, corven_gc, match
from dot_measure import load
from dot_grid import build
from dot_rule import dots_fast, params_for
pd.set_option('display.width', 280)
os.chdir(NQDIR); Cn, cov_n, _ = corven_nq(); Cg, cov_g = corven_gc(); os.chdir(HERE)
cov_n = pd.DatetimeIndex(cov_n); cov_g = pd.DatetimeIndex(cov_g)
# M5 GC 18/11
F0 = pd.read_pickle('../corven_m5_2026-11-18/F_m5.pkl')
F5 = pd.DataFrame(dict(t=pd.to_datetime(F0.datetime), tk=np.round(F0.price / 0.1).astype(np.int64), bid=F0.bid, ask=F0.ask, vol=F0.vol)); F5 = F5[F5.vol > 0]
S5 = F5.groupby('t').agg(med=('vol', 'median'), hi=('tk', 'max'), lo=('tk', 'min')); S5['rng'] = S5.hi - S5.lo
gt = pd.read_csv('../corven_m5_2026-11-18/gt_corven_m5.csv'); gt = gt[gt.type == 'dot'].copy(); gt['t'] = pd.to_datetime(gt.bar_time); gt['tk'] = np.round(gt.price_centre / 0.1).astype(int)
def m5(kw):
    thr, w, h = (params_for(S5, 2.8, 0, 4, hfix=6)[:3] if kw is None else build(S5, 5, **kw))
    D = dots_fast(F5, thr, w, h); D = D[(D.t >= '2026-11-18 12:15') & (D.t <= '2026-11-18 14:20')]
    hit = sum(((D.t == r.t) & (D.col == ('S' if r.colour == 'red' else 'B')) & ((D.tk - r.tk).abs() <= 5)).any() for r in gt.itertuples())
    return len(D), hit
def m1(sym, C, cov, kw):
    F, S = load(sym, 1)
    thr, w, h = ((params_for(S, 2.8, 0, 4, hfix=6) if sym == 'GC' else params_for(S, 3.5, 14, 8, hfix=12))[:3] if kw is None else build(S, 1, **kw))
    D = dots_fast(F[F.t.isin(cov)], thr, w, h); rec, prec, f1 = match(C, D, 3)
    return len(D) / len(cov), rec, prec
U = dict(k=2.8, wmode='lin', c=6, wmin=4, hmult=0.75, hmin=6, floor=9)
NOHIDE = dict(hmult=0, hmin=-1)
C = [('HIỆN TẠI', None), ('chung 2,8 · sàn 9 (che max(6; 0,75w))', U), ('chung 2,8 · sàn 9 · che 2 tick', dict(U, hmult=0, hmin=2))]
for k in (2.8, 2.4, 2.0):
    for fl in (9, 5):
        C.append((f'chung {k} · sàn {fl} · KHÔNG che', dict(U, k=k, floor=fl, **NOHIDE)))
C += [('chung 2,4 · sàn 5 · w tối thiểu 3 · không che', dict(U, k=2.4, floor=5, wmin=3, **NOHIDE)), ('chung 2,0 · sàn 5 · w tối thiểu 2 (R/10) · không che', dict(U, k=2.0, floor=5, wmin=2, c=10, **NOHIDE))]
rows = []
for name, kw in C:
    g = m1('GC', Cg, cov_g, kw); n = m1('NQ', Cn, cov_n, kw); a = m5(kw)
    rows.append(dict(luat=name, GC_M1_cham_nen=round(g[0], 2), GC_M1_recall=round(g[1], 2), GC_M1_precision=round(g[2], 2), NQ_M1_cham_nen=round(n[0], 2), NQ_M1_recall=round(n[1], 2), NQ_M1_precision=round(n[2], 2),
                     GC_M5_cham=a[0], GC_M5_cum_trung=f'{a[1]}/16'))
    print(rows[-1], flush=True)
print(f'CORVEN: GC M1 {len(Cg) / len(cov_g):.2f} chấm/nến, NQ M1 {len(Cn) / len(cov_n):.2f} chấm/nến, GC M5 16 cụm (~33 chấm) / 26 nến')
R = pd.DataFrame(rows); R.to_csv('out_dot_recall2.csv', index=False); print(R.to_string(index=False))
