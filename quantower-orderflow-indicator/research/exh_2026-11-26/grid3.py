import pandas as pd, numpy as np, itertools
from grid1 import f1
D = {'GC': pd.read_pickle('X_GC.pkl'), 'NQ': pd.read_pickle('X_NQ.pkl')}
DEN = ['Bmean', 'vol', 'v_mean', 'v_max', 'Bvol', 'Bvmax', 's_max', 's_tot']
def search(X, nums=('ms3', 'cs3'), wopts=(('wick_r', 1), ('wick_r', 2), ('wick_r', 3))):
    y = X.y.values.astype(bool); res = []
    for num in nums:
        R = {d: (X[num] / X[d]).values for d in DEN}
        Q = {d: np.unique(np.quantile(R[d][y], [.85, .9, .93, .96, .98, 1.0])) for d in DEN}
        for d1, d2 in itertools.combinations(DEN, 2):
            for a in Q[d1]:
                h1 = R[d1] <= a
                for b in Q[d2]:
                    h2 = h1 & (R[d2] <= b)
                    for wc, w in wopts:
                        res.append((f1(y, h2 & (X[wc].values >= w)), num, d1, round(float(a), 4), d2, round(float(b), 4), wc, w))
    res.sort(key=lambda z: -z[0][0]); return res
def apply(X, r):
    _, num, d1, a, d2, b, wc, w = r
    return f1(X.y.values.astype(bool), ((X[num] / X[d1] <= a) & (X[num] / X[d2] <= b) & (X[wc] >= w)).values)
if __name__ == '__main__':
    for fit, test in (('GC', 'NQ'), ('NQ', 'GC')):
        res = search(D[fit]); seen = set(); print('fit', fit)
        for r in res:
            k = (r[1], r[2], r[4])
            if k in seen: continue
            seen.add(k); t = apply(D[test], r)
            print('  fit %.3f tp %d fp %d fn %d | test %.3f tp %d fp %d fn %d |' % (r[0] + t), r[1:])
            if len(seen) >= 10: break
