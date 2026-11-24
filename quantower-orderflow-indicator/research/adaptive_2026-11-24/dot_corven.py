"""Câu B: các công thức chấm so với chart CORVEN (M1): GC 580 nến (đo cũ), NQ 534 nến ngày 06/11 (corven_nq_raw.csv).
Khớp = cùng nến, cùng màu (tím khớp cả hai), cách <= 3 tick. Dùng lại corven_nq_compare.py (corven_nq, corven_gc, match).
Chạy: python dot_corven.py"""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); NQDIR = os.path.join(HERE, '..', 'nq_calib_2026-11-24')
sys.path.insert(0, HERE); sys.path.insert(0, NQDIR); os.chdir(NQDIR)
from corven_nq_compare import corven_nq, corven_gc, match
os.chdir(HERE)
import dot_measure
from dot_measure import load, TFS
from dot_grid import build
from dot_rule import dots_fast, params_for
pd.set_option('display.width', 250)

CANDS = [
    ('CÔNG THỨC CHUNG CHỐT: 2,8 · w=max(4,R/6) · che max(6; 0,75w) · sàn 9', dict(k=2.8, wmode='lin', c=6, wmin=4, hmult=0.75, hmin=6, floor=9)),
    ('như chốt, bội số 3,2', dict(k=3.2, wmode='lin', c=6, wmin=4, hmult=0.75, hmin=6, floor=9)),
    ('HIỆN TẠI (GC 2,8/±4/che 6; NQ 3,5/±max(8,R/14)/che 12)', None),
    ('chung: 2,8 · w=max(4,R/6) · che 1,5w', dict(k=2.8, wmode='lin', c=6, wmin=4, hmult=1.5, floor=9)),
    ('chung: 3,0 · w=max(4,R/6) · che 1,5w', dict(k=3.0, wmode='lin', c=6, wmin=4, hmult=1.5, floor=9)),
    ('chung: 2,8 · w=max(4,R/5) · che 1,5w', dict(k=2.8, wmode='lin', c=5, wmin=4, hmult=1.5, floor=9)),
    ('chung: 2,8 · w=max(4,R/4) · che 1,5w', dict(k=2.8, wmode='lin', c=4, wmin=4, hmult=1.5, floor=9)),
    ('chung: 2,8 · w=max(4,R/6) · che 1,5w · sàn 5', dict(k=2.8, wmode='lin', c=6, wmin=4, hmult=1.5, floor=5)),
    ('chung: 2,4 · w=max(4,R/4) · che 1,5w · sàn 5', dict(k=2.4, wmode='lin', c=4, wmin=4, hmult=1.5, floor=5)),
    ('chung: 2,0 · w=max(4,R/4) · che 1,5w · sàn 5', dict(k=2.0, wmode='lin', c=4, wmin=4, hmult=1.5, floor=5)),
]

def run(sym, m, kw):
    F, S = load(sym, m)
    if kw is None:
        thr, w, h, _, _ = params_for(S, 2.8, 0, 4, hfix=6) if sym == 'GC' else params_for(S, 3.5, 14, 8, hfix=12)
    else:
        thr, w, h = build(S, m, **kw)
    return F, S, thr, w, h

if __name__ == '__main__':
    os.chdir(NQDIR); Cn, cov_n, _ = corven_nq(); Cg, cov_g = corven_gc(); os.chdir(HERE)
    rows = []
    for name, kw in CANDS:
        r = dict(luat=name)
        for sym, C, cov in (('GC', Cg, cov_g), ('NQ', Cn, cov_n)):
            F, S, thr, w, h = run(sym, 1, kw)
            cov = pd.DatetimeIndex(cov)
            Dt = dots_fast(F[F.t.isin(cov)], thr, w, h)
            rec, prec, f1 = match(C, Dt, 3)
            r[f'{sym}_cham_nen'] = round(len(Dt) / len(cov), 2); r[f'{sym}_ti_le_CORVEN'] = round(len(Dt) / len(C), 2)
            r[f'{sym}_recall'] = round(rec, 2); r[f'{sym}_precision'] = round(prec, 2); r[f'{sym}_F1'] = round(f1, 3)
            r[f'{sym}_w'] = int(np.median(w.reindex(cov).dropna()))
        rows.append(r); print(r, flush=True)
    print(f'CORVEN: GC {len(Cg) / len(cov_g):.2f} chấm/nến ({len(cov_g)} nến), NQ {len(Cn) / len(cov_n):.2f} chấm/nến ({len(cov_n)} nến)')
    print(pd.DataFrame(rows).to_string(index=False))
