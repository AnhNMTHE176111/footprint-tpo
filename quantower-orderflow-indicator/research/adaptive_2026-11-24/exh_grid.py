"""Kiệt sức: quét luật mới. Tiêu chí: giữ đủ 11/11 dấu CORVEN (26 nến M5 GC 18/11) trước, rồi mới giảm số dấu và làm phẳng theo khung.
Họ luật:
  A (hiện tại)  : râu >= 3, S6 <= c x volume TB mỗi ô của 20 nến trước
  B (nền đuôi)  : râu >= 3, S6 <= c x trung vị (hoặc TB) của S6 trên N nến trước (cả đỉnh lẫn đáy)
  C (nền đuôi + yếu hơn bên đối diện ...) xem mã
Chạy: python exh_grid.py"""
import numpy as np, pandas as pd
from exh_common import corven_gt, tail_base
from common_window import nbase
pd.set_option('display.width', 280)
G = corven_gt(full=True)
DS = {(s, m): pd.read_pickle(f'X_{s}_m{m}.pkl') for s in ('GC', 'NQ') for m in (1, 5, 15, 30, 60)}
def evalrule(name, fn):
    """fn(X, m) -> mảng bool."""
    h = fn(G, 5) & G['gt'].values; y = G['y'].values & G['gt'].values
    r = dict(luat=name, CORVEN_trung=int((h & y).sum()), thua=int((h & ~y).sum()), sot=int((y & ~h).sum()))
    for (s, m), X in DS.items():
        hh = fn(X, m); r[f'{s}{m}'] = round(np.nansum(hh) / X.t.nunique(), 2)
    return r
rows = []
rows.append(evalrule('A hiện tại: S6 <= 1,1 x TB mỗi ô (20 nến)', lambda X, m: ((X.wick >= 3) & (X.S6 <= 1.1 * X.Bm20)).values))
for how in ('median', 'mean'):
    for Nmode in ('20', 'nbase'):
        base = {}
        def fn(X, m, c, how=how, Nmode=Nmode):
            key = (id(X), how, Nmode)
            if key not in base: base[key] = tail_base(X, 6, 20 if Nmode == '20' else nbase(m), how)
            return ((X.wick >= 3) & (X.S6 <= c * base[key])).values
        for c in (0.6, 0.7, 0.8, 0.9, 1.0):
            rows.append(evalrule(f'B: S6 <= {c} x {"trung vị" if how == "median" else "TB"} S6 của N nến trước (N={Nmode})', lambda X, m, c=c: fn(X, m, c)))
            print(rows[-1], flush=True)
R = pd.DataFrame(rows); R.to_csv('out_exh_grid.csv', index=False); print(R.to_string(index=False))
