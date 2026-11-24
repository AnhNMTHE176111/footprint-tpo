"""Vòng 2, mục 6.2 (cuối): so THAM KHẢO với chart CORVEN — chỉ báo số, không chỉnh gì theo nó.
Dùng lại ../nq_calib_2026-11-24/corven_nq_compare.py (corven_gc, corven_nq, match: cùng nến, cùng màu, cách <= 3 tick) như ../dot_floor_2026-11-24/floor_corven.py.
Ra: out_r2_corven.csv.  Chạy: python sa2_corven.py"""
import os, sys, numpy as np, pandas as pd
import sa2_lib as L
from sa_common import load_dot, NQDIR
sys.path.insert(0, NQDIR)
from corven_nq_compare import corven_nq, corven_gc, match  # noqa: E402

here = os.getcwd(); os.chdir(NQDIR); Cn, cov_n, _ = corven_nq(); Cg, cov_g = corven_gc(); os.chdir(here)
rows = []
CF = {c['name']: c for c in L.dot_configs()}
for sym, C, cov in (('GC', Cg, pd.DatetimeIndex(cov_g)), ('NQ', Cn, pd.DatetimeIndex(cov_n))):
    ds = load_dot(sym, 1)
    inb = np.isin(ds.t.values, cov.values)
    for nm in ('goc', 'p1', 'dc_dang_chay_khong_sot', 'dc_dang_chay_it_nhieu'):
        r = L.eval_dot(ds, CF[nm])
        k = r.dot & inb[ds.sbar]
        X = pd.DataFrame(dict(t=ds.t.values[ds.sbar[k]], tk=ds.stk[k], col=np.where(ds.sside[k] == 0, 'S', 'B')))
        rec, prec, f1 = match(C, X, 3)
        rows.append(dict(ma=sym, khung=1, cau_hinh=nm, so_nen_mau=int(inb.sum()), cham_CORVEN=len(C), cham_CORVEN_nen=len(C) / max(inb.sum(), 1),
                         cham_minh=len(X), cham_minh_nen=len(X) / max(inb.sum(), 1), recall=rec, precision=prec, F1=f1,
                         ghi_chu='NQ: chart CORVEN gộp hàng 8 tick, chỉ tham khảo' if sym == 'NQ' else ''))
        print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv('out_r2_corven.csv', index=False, float_format='%.4g')
