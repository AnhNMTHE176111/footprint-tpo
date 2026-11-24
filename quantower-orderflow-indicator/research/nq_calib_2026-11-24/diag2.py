import numpy as np, pandas as pd, sys
from corven_nq_compare import corven_nq, corven_gc
sym = sys.argv[1]
if sym == 'NQ': C, cov, _ = corven_nq()
else: C, cov = corven_gc()
F = pd.read_pickle(f'F_{sym}_m1.pkl'); F = F[F.t.isin(cov)]
g = {t: d.set_index('tk') for t, d in F.groupby('t')}
rng = np.random.default_rng(0)
def ranks(shift):
    out = []
    for r in C.itertuples():
        d = g.get(r.t)
        if d is None: continue
        v = d.bid if r.color == 'do' else (d.ask if r.color == 'xanh' else np.maximum(d.bid, d.ask))
        tk = r.tk + shift
        val = v.get(tk, 0)
        out.append((v > val).sum() / len(v))   # tỉ lệ ô lớn hơn ô tại chấm (0 = ô lớn nhất nến)
    return np.mean(out), np.mean(np.array(out) <= 0.1)
for s in range(-8, 9): print(sym, 'dịch', s, 'tick: hạng TB %.2f, %% nằm top10%% = %.2f' % ranks(s))
