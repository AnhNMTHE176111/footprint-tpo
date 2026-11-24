"""Giả thuyết: chart NQ của CORVEN gộp nhiều tick thành một hàng (ticks per row). Gộp footprint NQ theo R tick rồi xem chấm CORVEN có rơi vào hàng lớn nhất không."""
import numpy as np, pandas as pd, sys
from corven_nq_compare import corven_nq, corven_gc
sym = sys.argv[1]
if sym == 'NQ': C, cov, _ = corven_nq()
else: C, cov = corven_gc()
F0 = pd.read_pickle(f'F_{sym}_m1.pkl'); F0 = F0[F0.t.isin(cov)]
for R in ([1, 2, 4, 5, 8, 10, 12, 16, 20] if sym == 'NQ' else [1, 2, 3, 5]):
    F = F0.copy(); F['row'] = np.floor_divide(F.tk, R)
    G = F.groupby(['t', 'row'])[['bid', 'ask']].sum().reset_index()
    g = {t: d.set_index('row') for t, d in G.groupby('t')}
    best = None
    for sh in np.arange(-R, R + 1, max(1, R // 4)):
        out = []
        for r in C.itertuples():
            d = g.get(r.t)
            if d is None: continue
            v = d.bid if r.color == 'do' else (d.ask if r.color == 'xanh' else np.maximum(d.bid, d.ask))
            val = v.get((r.tk + sh) // R, 0)
            out.append((v > val).sum() / len(v))
        out = np.array(out); sc = (np.mean(out <= 0.1), np.mean(out == 0), out.mean())
        if best is None or sc[0] > best[1][0]: best = (sh, sc)
    print(sym, f'R={R:>2} tick/hàng: dịch {best[0]:>3} -> top10% {best[1][0]:.2f}, là hàng lớn nhất nến {best[1][1]:.2f}, hạng TB {best[1][2]:.2f}, số hàng TB/nến {G.groupby("t").size().mean():.1f}')
