import numpy as np, pandas as pd
from corven_nq_compare import corven_nq
R = 8
C, cov, _ = corven_nq()
F = pd.read_pickle('F_NQ_m1.pkl')
for sh in range(R):
    Fr = F.copy(); Fr['row'] = np.floor_divide(Fr.tk + sh, R)
    Fr = Fr[Fr.t.isin(cov)].groupby(['t', 'row'])[['bid', 'ask']].sum().reset_index()
    g = {t: d.set_index('row') for t, d in Fr.groupby('t')}
    top = []; 
    for r in C.itertuples():
        d = g.get(r.t)
        if d is None: continue
        row = (r.tk + 6 + sh) // R  # thử pha
        row = np.floor_divide(r.tk + sh, R)
        v = d.bid if r.color == 'do' else (d.ask if r.color == 'xanh' else np.maximum(d.bid, d.ask))
        top.append(v.get(row, 0) >= v.max())
    print('pha', sh, 'chấm rơi đúng hàng lớn nhất (cùng bên) của nến: %.2f' % np.mean(top))
