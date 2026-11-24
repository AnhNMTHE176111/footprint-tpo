import numpy as np, pandas as pd
from corven_nq_compare import corven_nq, corven_gc
Cn, cov, good = corven_nq()
F = pd.read_pickle('F_NQ_m1.pkl'); F = F[F.t.isin(cov)]
g = {t: d.set_index('tk') for t, d in F.groupby('t')}
# với mỗi chấm CORVEN: tick có volume bên (Bid cho đỏ, Ask cho xanh, max cho tím) lớn nhất trong ±6 tick -> độ lệch
off = []; rel = []
for r in Cn.itertuples():
    d = g.get(r.t)
    if d is None: continue
    w = d.loc[(d.index >= r.tk - 6) & (d.index <= r.tk + 6)]
    if w.empty: continue
    v = w.bid if r.color == 'do' else (w.ask if r.color == 'xanh' else np.maximum(w.bid, w.ask))
    off.append(int(v.idxmax() - r.tk)); rel.append(v.max() / d.B_med.iloc[0])
print('lệch tick (tick có bên lớn nhất ±6 - chấm CORVEN):'); print(pd.Series(off).value_counts().sort_index().to_string())
print('bên lớn nhất / B_med: phân vị', np.percentile(rel, [10, 25, 50, 75, 90]).round(2))
